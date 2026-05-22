from __future__ import annotations

import json

from .config import ARTIFACTS_DIR
from .generator import generate_answer
from .vector_store import query_chunks


def ask_question(question: str, top_k: int = 3) -> dict:
    results = query_chunks(question, top_k=top_k)
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    retrieved_chunks = []
    for index, document in enumerate(documents):
        retrieved_chunks.append(
            {
                "rank": index + 1,
                "text": document,
                "metadata": metadatas[index] if index < len(metadatas) else {},
                "distance": distances[index] if index < len(distances) else None,
            }
        )

    answer = generate_answer(question, [chunk["text"] for chunk in retrieved_chunks])
    if answer is None:
        if retrieved_chunks:
            answer = (
                "LLM answer generation is disabled because OPENAI_API_KEY is not set. "
                "The most relevant retrieved chunk is:\n\n"
                f"{retrieved_chunks[0]['text'][:700]}"
            )
        else:
            answer = "No chunks were retrieved for this question."
    payload = {
        "question": question,
        "answer": answer,
        "retrieved_chunks": retrieved_chunks,
    }
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS_DIR / "last_query.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    return payload
