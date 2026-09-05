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
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("OpenAI SDK is not installed.") from exc

        client = OpenAI(api_key=self.settings.openai_api_key)
        response = client.chat.completions.create(
            model=self.settings.openai_chat_model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or "No answer generated."
