from __future__ import annotations

import re
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import CHUNK_OVERLAP, CHUNK_SIZE
from .schemas import DocumentChunk, DocumentPage


def normalize_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def build_chunks(pages: list[DocumentPage], source_file: Path) -> list[DocumentChunk]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    document_id = source_file.stem.lower().replace(" ", "_")
    chunks: list[DocumentChunk] = []

    for page in pages:
        normalized_text = normalize_text(page.text)
        if not normalized_text:
            continue
        page_chunks = splitter.split_text(normalized_text)
        for index, chunk_text in enumerate(page_chunks):
            chunks.append(
                DocumentChunk(
                    chunk_id=f"{document_id}_p{page.page_number:02d}_c{index:03d}",
                    document_id=document_id,
                    source_file=source_file.name,
                    page_number=page.page_number,
                    chunk_index=index,
                    text=chunk_text,
                )
            )

    return chunks
