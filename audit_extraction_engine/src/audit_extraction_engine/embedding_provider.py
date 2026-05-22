from __future__ import annotations

import hashlib
import math
import os
import re
from dataclasses import dataclass

from openai import OpenAI

from .config import DEFAULT_OPENAI_EMBEDDING_MODEL, EMBEDDING_DIMENSION


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_+-]+", text.lower())


def _local_embed_text(text: str) -> list[float]:
    vector = [0.0] * EMBEDDING_DIMENSION
    for token in _tokenize(text):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:2], "big") % EMBEDDING_DIMENSION
        sign = 1.0 if digest[2] % 2 == 0 else -1.0
        vector[index] += sign

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


@dataclass
class EmbeddingProvider:
    provider_name: str
    model_name: str

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class LocalEmbeddingProvider(EmbeddingProvider):
    def __init__(self) -> None:
        super().__init__(provider_name="local", model_name="hash_embedding_v1")

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [_local_embed_text(text) for text in texts]


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str) -> None:
        super().__init__(provider_name="openai", model_name=model_name)
        self.client = OpenAI()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = self.client.embeddings.create(model=self.model_name, input=texts)
        return [item.embedding for item in response.data]


def get_embedding_provider() -> EmbeddingProvider:
    if os.environ.get("OPENAI_API_KEY"):
        model_name = os.environ.get(
            "OPENAI_EMBEDDING_MODEL",
            DEFAULT_OPENAI_EMBEDDING_MODEL,
        )
        return OpenAIEmbeddingProvider(model_name=model_name)
    return LocalEmbeddingProvider()
