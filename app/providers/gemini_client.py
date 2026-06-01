"""
Gemini Provider — Primary Engine (Position 1 in ALL fallback chains).
SDK: google-genai  (pip install google-genai)
Uses the NEW google.genai client — NOT the legacy google.generativeai package.
"""

import base64
from google import genai
from google.genai import types

from app.core.config import settings
from app.core.logger import logger
from app.providers.base import BaseProvider
from app.schemas.requests import RelayRequest

# Initialised once at import time; reused across requests
_client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Use gemini-2.5-flash which showed availability in diagnostics
MODEL = "gemini-2.5-flash"


class GeminiProvider(BaseProvider):
    @property
    def name(self) -> str:
        return "gemini"

    async def solve(self, request: RelayRequest) -> str:
        parts: list[types.Part] = []

        # ── Attach media (only one type per request) ─────────────────────────
        if request.video_b64:
            logger.debug("Gemini: attaching video bytes (inline)")
            video_bytes = base64.b64decode(request.video_b64)
            parts.append(types.Part.from_bytes(data=video_bytes, mime_type="video/mp4"))

        elif request.audio_b64:
            logger.debug("Gemini: attaching audio bytes (inline)")
            audio_bytes = base64.b64decode(request.audio_b64)
            parts.append(types.Part.from_bytes(data=audio_bytes, mime_type="audio/mp4"))

        elif request.image_b64:
            logger.debug("Gemini: attaching image bytes (inline)")
            image_bytes = base64.b64decode(request.image_b64)
            parts.append(types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))

        # ── Text question ─────────────────────────────────────────────────────
        if request.question:
            parts.append(types.Part.from_text(text=request.question))

        if not parts:
            raise ValueError("GeminiProvider: RelayRequest has no content (no media, no question).")

        config = types.GenerateContentConfig(
            system_instruction=request.system_instruction,
            temperature=0.4,
        )

        # Switched to aio (async) client to prevent blocking
        response = await _client.aio.models.generate_content(
            model=MODEL,
            contents=parts,
            config=config,
        )

        text = response.text
        if not text:
            raise ValueError("Gemini returned an empty response.")
        return text


# Module-level singleton for use in chain lists
gemini_provider = GeminiProvider()
