"""
Hyperbolic Provider — Fallback 2 (Heavy-duty OCR / Vision).
Model: Qwen/Qwen2.5-VL-72B-Instruct
SDK: httpx (async REST — no dedicated SDK needed)
"""

import httpx

from app.core.config import settings
from app.core.logger import logger
from app.providers.base import BaseProvider
from app.schemas.requests import RelayRequest

_BASE_URL = "https://api.hyperbolic.xyz/v1/chat/completions"
_MODEL = "Qwen/Qwen2.5-VL-72B-Instruct"


def _headers() -> dict:
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.HYPERBOLIC_API_KEY}",
    }


class HyperbolicVisionProvider(BaseProvider):
    """Uses Qwen2.5-VL-72B for image/OCR tasks — excels at maths and handwriting."""

    @property
    def name(self) -> str:
        return "hyperbolic-vision"

    async def solve(self, request: RelayRequest) -> str:
        if not request.image_b64:
            raise ValueError("HyperbolicVisionProvider requires image_b64.")

        # Support passing multiple images (e.g. video frames extracted by video_processor)
        image_b64_list: list[str] = (
            request.image_b64
            if isinstance(request.image_b64, list)
            else [request.image_b64]
        )

        content: list[dict] = [
            {"type": "text", "text": request.question or "Solve what is shown in the image(s)."}
        ]
        for b64 in image_b64_list:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                }
            )

        payload = {
            "model": _MODEL,
            "messages": [
                {"role": "system", "content": request.system_instruction},
                {"role": "user", "content": content},
            ],
            "max_tokens": 2048,
            "temperature": 0.4,
        }

        logger.debug(f"Hyperbolic: sending request with {len(image_b64_list)} image(s)")
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(_BASE_URL, headers=_headers(), json=payload)
            response.raise_for_status()
            data = response.json()

        return data["choices"][0]["message"]["content"]


hyperbolic_vision_provider = HyperbolicVisionProvider()
