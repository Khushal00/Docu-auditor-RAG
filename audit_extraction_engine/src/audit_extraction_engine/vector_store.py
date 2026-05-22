from __future__ import annotations

import re
from pathlib import Path

import chromadb

from .config import CHROMA_DIR, COLLECTION_NAME
from .embedding_provider import get_embedding_provider
from .schemas import DocumentChunk


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9_+-]+", text.lower()))


def _keyword_overlap_score(query: str, document: str) -> float:
    query_tokens = _tokenize(query)
    document_tokens = _tokenize(document)
    if not query_tokens or not document_tokens:
        return 0.0
    overlap = len(query_tokens & document_tokens)
    return overlap / len(query_tokens)


def get_collection(persist_directory: Path | None = None, reset: bool = False):
    storage_dir = persist_directory or CHROMA_DIR
    storage_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(storage_dir))

    if reset:
        existing = {collection.name for collection in client.list_collections()}
        if COLLECTION_NAME in existing:
            client.delete_collection(COLLECTION_NAME)

    return client.get_or_create_collection(name=COLLECTION_NAME)


def index_chunks(chunks: list[DocumentChunk], reset: bool = False) -> int:
    collection = get_collection(reset=reset)
    if not chunks:
        return 0
    embedding_provider = get_embedding_provider()
    embeddings = embedding_provider.embed_texts([chunk.text for chunk in chunks])

    collection.add(
        ids=[chunk.chunk_id for chunk in chunks],
        documents=[chunk.text for chunk in chunks],
        embeddings=embeddings,
        metadatas=[
            {
                "document_id": chunk.document_id,
                "source_file": chunk.source_file,
                "page_number": chunk.page_number,
                "chunk_index": chunk.chunk_index,
                "embedding_provider": embedding_provider.provider_name,
                "embedding_model": embedding_provider.model_name,
            }
            for chunk in chunks
        ],
    )
    return len(chunks)


def query_chunks(query: str, top_k: int = 3) -> dict:
    collection = get_collection()
    embedding_provider = get_embedding_provider()
    query_embedding = embedding_provider.embed_texts([query])[0]
    initial_k = max(top_k * 5, top_k)
    results = collection.query(query_embeddings=[query_embedding], n_results=initial_k)
    all_rows = collection.get(include=["documents", "metadatas"])

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    ids = results.get("ids", [[]])[0]

    combined_rows: dict[str, dict] = {}
    for index, document in enumerate(documents):
        distance = distances[index] if index < len(distances) else None
        similarity = 0.0 if distance is None else 1 / (1 + float(distance))
        keyword_score = _keyword_overlap_score(query, document)
        row_id = ids[index] if index < len(ids) else f"vector_{index}"
        combined_rows[row_id] = {
            "id": row_id,
            "document": document,
            "metadata": metadatas[index] if index < len(metadatas) else {},
            "distance": distance,
            "combined_score": (0.7 * keyword_score) + (0.3 * similarity),
        }

    for index, document in enumerate(all_rows.get("documents", [])):
        row_id = all_rows.get("ids", [])[index]
        keyword_score = _keyword_overlap_score(query, document)
        if keyword_score == 0:
            continue
        lexical_score = 0.8 * keyword_score
        existing = combined_rows.get(row_id)
        if existing is None or lexical_score > existing["combined_score"]:
            combined_rows[row_id] = {
                "id": row_id,
                "document": document,
                "metadata": all_rows.get("metadatas", [])[index],
                "distance": existing["distance"] if existing else None,
                "combined_score": lexical_score,
            }

    ranked_rows = sorted(
        combined_rows.values(),
        key=lambda row: row["combined_score"],
        reverse=True,
    )
    top_rows = ranked_rows[:top_k]
    return {
        "ids": [[row["id"] for row in top_rows]],
        "documents": [[row["document"] for row in top_rows]],
        "metadatas": [[row["metadata"] for row in top_rows]],
        "distances": [[row["distance"] for row in top_rows]],
    }
