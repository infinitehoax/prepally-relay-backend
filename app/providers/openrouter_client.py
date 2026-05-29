"""
OpenRouter Provider — Fallback 3 (Text / Reasoning).
Model: nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free
SDK: httpx (async REST — OpenAI-compatible format)
"""

import httpx

from app.core.config import settings
from app.core.logger import logger
from app.providers.base import BaseProvider
from app.schemas.requests import RelayRequest

_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
_MODEL = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://prepally.ai",
        "X-Title": "PrepAlly",
    }


class OpenRouterTextProvider(BaseProvider):
    @property
    def name(self) -> str:
        return "openrouter-text"

    async def solve(self, request: RelayRequest) -> str:
        if not request.question:
            raise ValueError("OpenRouterTextProvider requires a question.")

        payload = {
            "model": _MODEL,
            "messages": [
                {"role": "system", "content": request.system_instruction},
                {"role": "user", "content": request.question},
            ],
        }

        logger.debug("OpenRouter: sending text request")
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(_BASE_URL, headers=_headers(), json=payload)
            response.raise_for_status()
            data = response.json()

        return data["choices"][0]["message"]["content"]


openrouter_text_provider = OpenRouterTextProvider()
