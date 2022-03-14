from PyPDF2 import PdfFileWriter, PdfFileReader
import os
import sys
import ocrmypdf
import io
import requests
from typing import List
import pdfplumber


def ocr_pdf(raw_file: bytes, language=("ara",)) -> bytes:
    f = io.BytesIO(raw_file)
    f_out = io.BytesIO()
    ocrmypdf.ocr(f, f_out, language=language)
    f_out.seek(0)
    return f_out.read()


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
