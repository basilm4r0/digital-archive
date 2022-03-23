from concurrent.futures import ThreadPoolExecutor
import json
from PyPDF2 import PdfFileWriter, PdfFileReader
import os
import sys
import ocrmypdf
import io
import requests
from typing import List
import pdfplumber
from typing import Tuple
import tempfile
import re


def split_pdf(raw_file: bytes) -> List[bytes]:
    outputs = []
    reader = PdfFileReader(io.BytesIO(raw_file))
    for i, p in enumerate(reader.pages):
        output = PdfFileWriter()
        output.addPage(p)
        f_out = io.BytesIO()
        output.write(f_out)
        f_out.seek(0)
        outputs.append(f_out.read())
    return outputs


def join_pdfs(raw_files: List[bytes]) -> bytes:
    output = PdfFileWriter()
    for raw_file in raw_files:
        reader = PdfFileReader(io.BytesIO(raw_file))
        for p in reader.pages:
            output.addPage(p)
    f_out = io.BytesIO()
    output.write(f_out)
    f_out.seek(0)
    return f_out.read()

def ocr_pdf(raw_file: bytes, language=("ara",)) -> Tuple[bytes, str]:
    f = io.BytesIO(raw_file)
    f_out = io.BytesIO()
    txt_out = io.StringIO()
    with tempfile.NamedTemporaryFile('r') as tmp_txt_f:
        ocrmypdf.ocr(f, f_out, language=language, sidecar=tmp_txt_f.name, use_threads=False, progress_bar=False)
        txt = tmp_txt_f.read()
    f_out.seek(0)
    txt_out.seek(0)
    return f_out.read(), txt


def clean_ocr_text(_in: str) -> str:
    return re.sub(r'\n[ \n]*', '\n', _in).strip()


def download_file(url) -> bytes:
    r = requests.get(url)
    r.raise_for_status()
    return r.content


def split_text_per_page(raw_file: bytes) -> List[str]:
    # reader = PdfFileReader(io.BytesIO(raw_file))
    # pageObj = reader.getNumPages()
    # page_texts = []
    # for page_count in range(pageObj):
    #     page = reader.getPage(page_count)
    #     page_texts.append(page.extractText())
    # return page_texts

    page_texts = []
    with pdfplumber.open(io.BytesIO(raw_file)) as pdf:
        for p in pdf.pages:
            page_texts.append(p.extract_text())

    return page_texts


from omeka import OmekaSGateway
from tqdm import tqdm


class OCRProcessor:
    def __init__(self, api: OmekaSGateway) -> None:
        self.api = api

        self.BIBO_CONTENT_ID = api.get_property_id("bibo:content")
        self.BIBO_DOCUMENT_PART_ID = api.get_resource_class_id('bibo:DocumentPart')
        self.IS_PART_OF_ID = api.get_property_id("dcterms:isPartOf")
        self.DCTERMS_TITLE_ID = api.get_property_id("dcterms:title")
        self.DCTERMS_LANGUAGE_ID = api.get_property_id("dcterms:language")

        with open('languages.json', 'r') as f:
            self.language_codes = json.load(f)

    def _find_code(self, v: str):
        for language_name, language_code in self.language_codes.items():
            if v.lower().startswith(language_name):
                return language_code
        return None

    def process_item(self, item_id: int):
        item_data = self.api.get_item_by_id(item_id)
        item_title = item_data['o:title']

        media_ids = [m['o:id'] for m in item_data['o:media']]
        if len(media_ids) != 1:  # We expect only a single file, otherwise we do not process the file
            print(f"Item {item_id} has not exactly 1 (but {len(media_ids)}) media file, not processing")
            return False
        media_id = media_ids[0]
        
        media_data = self.api.get_media_by_id(media_id)
        if media_data['o:media_type'] != 'application/pdf':  # We only process PDFs
            return False

        print(f"Processing item {item_id} named {item_title}")
        
        if "dcterms:language" in item_data:
            language_values = [d['@value'] for d in item_data["dcterms:language"]]
            print(language_values)

            # Parse language_values
            languages = []
            for v in language_values:
                code = self._find_code(v)
                if code is not None:
                    languages.append(code)
                else:
                    print(f"Unrecognised language {v}")
            languages = tuple(languages)
        else:
            # Default case
            # Note: has to be ISO 639-2 codes
            languages = ("ara", "eng")

        print(f"Using languages {languages}")

        media_raw_file = download_file(media_data['o:original_url'])

        pages_raw = split_pdf(media_raw_file)

        # Process and add each page
        complete_ocr_text = []
        processed_ocr_pages = []

        def _process_page(p):
            ocr_page, ocr_text = ocr_pdf(p, language=languages)
            ocr_text = clean_ocr_text(ocr_text)
            return ocr_page, ocr_text
        
        with ThreadPoolExecutor(3) as e:
            for i, (ocr_page, ocr_text) in tqdm(enumerate(e.map(_process_page, pages_raw)), total=len(pages_raw), desc="Processing pages"):
                page_number = i + 1
                # ocr_page, ocr_text = ocr_pdf(p, language=languages)
                # ocr_text = clean_ocr_text(ocr_text)
                complete_ocr_text.append(f"-----Page {page_number}-----\n{ocr_text}")
                processed_ocr_pages.append(ocr_page)
                page_title = f"{item_title}, p. {page_number}"
                page_item = self.api.add_item({
                    #"o:resource_template": {"o:id": PROCESSED_PAGE_RESOURCE_ID},
                    "o:resource_class": {"o:id": self.BIBO_DOCUMENT_PART_ID},
                    "dcterms:title": [{
                        "property_id": self.DCTERMS_TITLE_ID,
                        "type" : "literal",
                        "@value" : page_title
                    }],
                    
                    "bibo:content": [{
                        "property_id": self.BIBO_CONTENT_ID,
                        "type" : "literal",
                        "@value" : ocr_text
                    }],
                    
                    "dcterms:isPartOf": [{
                        "property_id": self.IS_PART_OF_ID,
                        "type" : 'resource:item',
                        'value_resource_id': item_id,
                        'value_resource_name': 'items',
                    }]
                })
                self.api.add_media(
                    item_id=page_item['o:id'],
                    filename=f"{page_title}.pdf",
                    file_data=ocr_page,
                    mimetype='application/pdf')
        
        # Save complete OCR text
        # complete_ocr_text = "\n".join(complete_ocr_text)
        # self.api.add_media(
        #     item_id=item_id,
        #     filename=f"OCR_output.txt",
        #     file_data=complete_ocr_text.encode("utf8"),
        #     mimetype='plain/text')

        # Hide original file
        self.api.update_media(media_id, {'o:is_public': False})

        # Save OCRized PDF
        complete_pdf = join_pdfs(processed_ocr_pages)
        self.api.add_media(
            item_id=item_id,
            filename=f"{item_title}.pdf",
            file_data=complete_pdf,
            mimetype='application/pdf')

        return True
