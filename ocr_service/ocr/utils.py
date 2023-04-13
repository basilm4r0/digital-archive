from PyPDF2 import PdfFileWriter, PdfFileReader
import ocrmypdf
import io
import requests
from typing import List
import pdfplumber
from typing import Tuple, Union, Dict
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
        ocrmypdf.ocr(f, f_out, language=language, sidecar=tmp_txt_f.name, force_ocr=True,  use_threads=True, progress_bar=False) #, redo_ocr=True)
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
