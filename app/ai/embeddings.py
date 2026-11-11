from __future__ import annotations

from app.core.config import get_settings


class EmbeddingService:
    def __init__(self):
        self.settings = get_settings()

    def get_embedding(self, text: str) -> list[float]:
        if not self.settings.openai_api_key:
            return self._mock_embedding(text)
        try:
            from openai import AzureOpenAI, OpenAI
        except ImportError as exc:
            raise RuntimeError("OpenAI SDK is not installed.") from exc

        if self.settings.azure_openai_endpoint:
            if "/api/projects/" in self.settings.azure_openai_endpoint:
                raise RuntimeError(
                    "Azure AI Foundry project endpoints do not support embeddings. "
                    "Set AZURE_OPENAI_ENDPOINT to the resource endpoint, for example "
                    "https://<resource-name>.openai.azure.com/."
                )
            endpoint = self.settings.azure_openai_endpoint.rstrip("/")
            deployment = (
                self.settings.azure_openai_embedding_deployment
                or "text-embedding-3-small"
            )
            client = AzureOpenAI(
                api_key=self.settings.openai_api_key,
                api_version=self.settings.azure_openai_api_version,
                azure_endpoint=endpoint,
            )
            model = deployment
        else:
            client = OpenAI(api_key=self.settings.openai_api_key)
            model = self.settings.openai_embedding_model

        response = client.embeddings.create(
            model=model,
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
