from omeka import OmekaSGateway
from tqdm import tqdm
import json
from concurrent.futures import ThreadPoolExecutor

from .utils import *


class OCRProcessor:
    def __init__(self, api: OmekaSGateway, document_status_property: str, error_message_property: str,
                 generated_page_class: str, processed_media_class: str) -> None:
        self.api = api

        self.BIBO_CONTENT_ID = api.get_property_id("bibo:content")
        self.GENERATED_PAGE_CLASS = generated_page_class
        self.GENERATED_PAGE_CLASS_ID = api.get_resource_class_id(generated_page_class)
        self.PROCESSED_MEDIA_CLASS = generated_page_class
        self.PROCESSED_MEDIA_CLASS_ID = api.get_resource_class_id(processed_media_class)
        self.IS_PART_OF_ID = api.get_property_id("dcterms:isPartOf")
        self.DCTERMS_TITLE_ID = api.get_property_id("dcterms:title")
        self.DCTERMS_CREATOR_ID = api.get_property_id("dcterms:creator")
        self.DCTERMS_LANGUAGE_ID = api.get_property_id("dcterms:language")
        self.DOCUMENT_STATUS_ID = api.get_property_id(document_status_property)
        self.DOCUMENT_STATUS_TERM = document_status_property
        self.ERROR_MSG_ID = api.get_property_id(error_message_property)
        self.ERROR_MSG_TERM = error_message_property

        #self.CREATOR_NAME = 'OCR Bot'

        with open('languages.json', 'r') as f:
            self.language_codes = json.load(f)

    def _find_code(self, v: str):
        for language_name, language_code in self.language_codes.items():
            if v.lower().startswith(language_name):
                return language_code
        return None

    def list_items_to_process(self):
        return self.api.list_items(property_filters=[{"property":self.DOCUMENT_STATUS_ID, "type": "eq", "text": "TO_BE_PROCESSED"}])

    def clean_item(self, item_id: Union[int, Dict]):
        if isinstance(item_id, (int, str)):
            item_data = self.api.get_item_by_id(int(item_id))
        else:
            item_data = item_id

        # Delete OCRized file is it exists
        for media_item in item_data.get('o:media', []):
            media_id = media_item['o:id']
            media_item = self.api.get_media_by_id(media_id)

            # Check that media is generated one
            class_data = media_item.get('o:resource_class')
            if class_data and (class_data.get("o:id", -1) == self.PROCESSED_MEDIA_CLASS_ID):
                self.api.delete_media_by_id(media_id)
            
        # Delete page items
        for page_item in self.api.list_items(
            resource_class_id=self.GENERATED_PAGE_CLASS_ID,
            property_filters=[
                {"property": self.IS_PART_OF_ID, "type": "res", "text": item_id},
            ]):
            self.api.delete_item_by_id(page_item["o:id"])

    def _flag_item_as_done(self, item_id: int):
        item_data = self.api.get_item_by_id(item_id)
        item_data.update({
            self.DOCUMENT_STATUS_TERM: [{
            "property_id": self.DOCUMENT_STATUS_ID,
            "type" : "literal",
            "@value" : "PROCESSED",
            "is_public": False
            }],
            self.ERROR_MSG_TERM: []
        })
        self.api.update_item(item_id, item_data)

    def _flag_item_as_failed(self, item_id: int, reason: str):
        item_data = self.api.get_item_by_id(item_id)
        item_data.update({
            self.DOCUMENT_STATUS_TERM: [{
            "property_id": self.DOCUMENT_STATUS_ID,
            "type" : "literal",
            "@value" : "FAILURE",
            "is_public": False
            }],
            self.ERROR_MSG_TERM: [{
            "property_id": self.ERROR_MSG_ID,
            "type" : "literal",
            "@value" : reason,
            "is_public": False
            }]
        })
        self.api.update_item(item_id, item_data)

    def _add_generated_page(self, item_data: dict, part_number: int, page_raw_file: bytes, ocr_text: str):
        item_title = item_data['o:title']
        item_id = item_data['o:id']
        page_title = f"{item_title}, part {part_number}"
        page_item = self.api.add_item({
            "o:resource_class": {"o:id": self.GENERATED_PAGE_CLASS_ID},
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

            # "dcterms:creator": [{
            #     "property_id": self.DCTERMS_CREATOR_ID,
            #     "type" : "literal",
            #     "@value" : self.CREATOR_NAME,
            #     "is_public": False
            # }],
            
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
            file_data=page_raw_file,
            mimetype='application/pdf'
        )

    def _parse_languages(self, item_data: dict) -> Tuple[str]:
        if "dcterms:language" in item_data:
            language_values = [d['@value'] for d in item_data["dcterms:language"]]

            # Parse language_values
            languages = []
            for v in language_values:
                code = self._find_code(v)
                if code is not None:
                    languages.append(code)
                else:
                    raise ValueError(f"Unrecognised language {v}")
            languages = tuple(languages)
        else:
            # Default case
            # Note: has to be ISO 639-2 codes
            languages = ("ara", "eng")
        return languages

    def process_item(self, item_id: int):
        try:
            item_data = self.api.get_item_by_id(item_id)
            item_title = item_data['o:title']

            media_ids = [m['o:id'] for m in item_data['o:media']]
            media_items = [self.api.get_media_by_id(m['o:id']) for m in item_data['o:media']]
            pdf_media_items = [media_data for media_data in media_items if media_data.get('o:media_type', '') == 'application/pdf']

            if len(pdf_media_items) != 1:  # We expect only a single file, otherwise we do not process the file
                raise ValueError(f"Item has not exactly 1 (but {len(media_ids)}) PDF file, not processing")

            media_data = pdf_media_items[0]
            media_id = media_data["o:id"]

            print(f"Processing item {item_id} named {item_title}")
            
            languages = self._parse_languages(item_data)
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
                    # ocr_page, ocr_text = ocr_pdf(p, language=languages)
                    # ocr_text = clean_ocr_text(ocr_text)
                    complete_ocr_text.append(f"-----Page {i+1}-----\n{ocr_text}")
                    processed_ocr_pages.append(ocr_page)
                    self._add_generated_page(item_data, i+1, ocr_page, ocr_text)

            # Hide original file
            self.api.update_media(media_id, {'o:is_public': False})

            # Save OCRized PDF
            complete_pdf = join_pdfs(processed_ocr_pages)
            self.api.add_media(
                item_id=item_id,
                filename=f"{item_title}.pdf",
                file_data=complete_pdf,
                mimetype='application/pdf',
                resource_class_id=self.PROCESSED_MEDIA_CLASS_ID)

            # Flag item as done
            self._flag_item_as_done(item_id)
            print(f"Successfully processed item with id={item_id}")

            return True
        except Exception as e:
            reason = str(e)
            self._flag_item_as_failed(item_id, reason)
            print(f"Failed processing item with id={item_id}: '{reason}'")
            return False
