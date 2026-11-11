from __future__ import annotations

from app.core.config import get_settings


class LLMService:
    def __init__(self):
        self.settings = get_settings()

    def generate_response(self, prompt: str) -> str:
        if not self.settings.openai_api_key:
            return (
                "I can’t access the configured AI provider in this environment, so I’m responding from the available context only. "
                "Please configure OPENAI_API_KEY to enable live model responses."
            )
        try:
            from openai import AzureOpenAI, OpenAI
        except ImportError as exc:
            raise RuntimeError("OpenAI SDK is not installed.") from exc

        if self.settings.azure_openai_endpoint:
            client = AzureOpenAI(
                api_key=self.settings.openai_api_key,
                api_version=self.settings.azure_openai_api_version,
                azure_endpoint=self.settings.azure_openai_endpoint,
            )
            model = (
                self.settings.azure_openai_chat_deployment
                or self.settings.openai_chat_model
            )
        else:
            client = OpenAI(api_key=self.settings.openai_api_key)
            model = self.settings.openai_chat_model

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or "No answer generated."
