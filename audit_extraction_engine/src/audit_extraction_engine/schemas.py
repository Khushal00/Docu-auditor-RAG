from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class DocumentPage:
    page_number: int
    text: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DocumentChunk:
    chunk_id: str
    document_id: str
    source_file: str
    page_number: int
    chunk_index: int
    text: str

    def to_dict(self) -> dict:
        return asdict(self)
