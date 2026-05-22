from __future__ import annotations

import os

from openai import OpenAI

from .config import DEFAULT_OPENAI_CHAT_MODEL


def generate_answer(question: str, context_chunks: list[str]) -> str | None:
    if not os.environ.get("OPENAI_API_KEY"):
        return None

    client = OpenAI()
    model_name = os.environ.get("OPENAI_CHAT_MODEL", DEFAULT_OPENAI_CHAT_MODEL)
    context = "\n\n".join(
        f"Context chunk {index + 1}:\n{chunk}" for index, chunk in enumerate(context_chunks)
    )
    prompt = (
        "Answer the question using only the context below. "
        "If the answer is not present, say that it is not found in the document.\n\n"
        f"{context}\n\nQuestion: {question}"
    )
    response = client.responses.create(
        model=model_name,
        input=prompt,
    )
    return response.output_text.strip()
