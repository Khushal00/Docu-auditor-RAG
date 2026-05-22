from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .config import ARTIFACTS_DIR, DEFAULT_PDF_PATH
from .embedding_provider import get_embedding_provider
from .pdf_loader import extract_pdf_pages
from .schemas import DocumentPage
from .text_splitter import build_chunks
from .vector_store import index_chunks


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def run_ingestion(pdf_path: Path | None = None, reset: bool = True) -> dict:
    target_path = pdf_path or DEFAULT_PDF_PATH
    embedding_provider = get_embedding_provider()
    pages: list[DocumentPage] = extract_pdf_pages(target_path)
    chunks = build_chunks(pages, target_path)
    indexed_count = index_chunks(chunks, reset=reset)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    _write_json(ARTIFACTS_DIR / "raw_text.json", [page.to_dict() for page in pages])
    _write_json(ARTIFACTS_DIR / "chunks.json", [chunk.to_dict() for chunk in chunks])

    report = {
        "source_file": str(target_path),
        "page_count": len(pages),
        "chunk_count": len(chunks),
        "indexed_count": indexed_count,
        "embedding_provider": embedding_provider.provider_name,
        "embedding_model": embedding_provider.model_name,
        "ingested_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    _write_json(ARTIFACTS_DIR / "ingest_report.json", report)
    return report
