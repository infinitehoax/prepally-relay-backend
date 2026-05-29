"""
OpenRouter Provider — Position 2 in Fallback Chains.
Models:
  - Text/Reasoning: nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free
  - Vision: nvidia/nemotron-nano-12b-v2-vl:free
SDK: httpx (async REST — OpenAI-compatible format)
"""

import httpx

from app.core.config import settings
from app.core.logger import logger
from app.providers.base import BaseProvider
from app.schemas.requests import RelayRequest

_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
_TEXT_MODEL = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
_VISION_MODEL = "nvidia/nemotron-nano-12b-v2-vl:free"


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
            "model": _TEXT_MODEL,
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


class OpenRouterVisionProvider(BaseProvider):
    """Uses Nemotron Nano 12B 2 VL (free) for image/vision tasks."""

    @property
    def name(self) -> str:
        return "openrouter-vision"

    async def solve(self, request: RelayRequest) -> str:
        if not request.image_b64:
            raise ValueError("OpenRouterVisionProvider requires image_b64.")

        # Support passing multiple images (e.g. video frames extracted by video_processor)
        image_b64_list: list[str] = (
            request.image_b64
            if isinstance(request.image_b64, list)
            else [request.image_b64]
        )

        content: list[dict] = []
        for b64 in image_b64_list:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                }
            )
        content.append({"type": "text", "text": request.question or "Solve what is shown in the image(s)."})

        payload = {
            "model": _VISION_MODEL,
            "messages": [
                {"role": "user", "content": content},
            ],
            "max_tokens": 2048,
            "temperature": 0.4,
        }

        logger.debug(f"OpenRouter: sending vision request with {len(image_b64_list)} image(s)")
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(_BASE_URL, headers=_headers(), json=payload)
            response.raise_for_status()
            data = response.json()

        return data["choices"][0]["message"]["content"]


openrouter_text_provider = OpenRouterTextProvider()
openrouter_vision_provider = OpenRouterVisionProvider()
