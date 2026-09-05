from __future__ import annotations

from typing import Sequence

from app.core.config import get_settings


class EmbeddingService:
    def __init__(self):
        self.settings = get_settings()

    def get_embedding(self, text: str) -> list[float]:
        if not self.settings.openai_api_key:
            return self._mock_embedding(text)
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("OpenAI SDK is not installed.") from exc

        client = OpenAI(api_key=self.settings.openai_api_key)
        response = client.embeddings.create(
            model=self.settings.openai_embedding_model,
            input=text,
        )
        return list(response.data[0].embedding)

    def _mock_embedding(self, text: str) -> list[float]:
        import hashlib

        digest = hashlib.sha256(text.encode("utf-8")).digest()
        vector = [((byte + 1) / 256.0) for byte in digest[: self.settings.embedding_dimension]]
        if len(vector) < self.settings.embedding_dimension:
            vector.extend([0.0] * (self.settings.embedding_dimension - len(vector)))
        return vector[: self.settings.embedding_dimension]
