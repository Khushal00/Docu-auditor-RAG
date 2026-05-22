from __future__ import annotations

from pathlib import Path

import fitz

from .schemas import DocumentPage


def extract_pdf_pages(file_path: Path) -> list[DocumentPage]:
    pages: list[DocumentPage] = []
    with fitz.open(file_path) as document:
        for index, page in enumerate(document, start=1):
            text = page.get_text("text")
            pages.append(DocumentPage(page_number=index, text=text.strip()))
    return pages
