"""
Mistral Provider — Position 4 (Final Text Safety Net).
Model: mistral-large-latest
SDK: mistralai  (pip install mistralai)
"""

import asyncio
from mistralai import Mistral

from app.core.config import settings
from app.core.logger import logger
from app.providers.base import BaseProvider
from app.schemas.requests import RelayRequest

_client = Mistral(api_key=settings.MISTRAL_API_KEY)
_MODEL = "mistral-large-latest"


class MistralTextProvider(BaseProvider):
    @property
    def name(self) -> str:
        return "mistral-text"

    async def solve(self, request: RelayRequest) -> str:
        if not request.question:
            raise ValueError("MistralTextProvider requires a question.")

        logger.debug("Mistral: sending text request")

        # The sync client is wrapped in asyncio.to_thread for non-blocking I/O
        response = await asyncio.to_thread(
            _client.chat.complete,
            model=_MODEL,
            messages=[
                {"role": "system", "content": request.system_instruction},
                {"role": "user", "content": request.question},
            ],
        )
        return response.choices[0].message.content


mistral_text_provider = MistralTextProvider()
