"""
Groq Provider — Position 3 in Fallback Chains.
  • Audio  → whisper-large-v3-turbo  (STT, then re-routes to text chain)
  • Vision → meta-llama/llama-4-scout-17b-16e-instruct
  • Text   → llama-3.3-70b-versatile
SDK: groq  (pip install groq)
"""

import base64
import tempfile
import os

from groq import AsyncGroq

from app.core.config import settings
from app.core.logger import logger
from app.providers.base import BaseProvider
from app.schemas.requests import RelayRequest

_client = AsyncGroq(api_key=settings.GROQ_API_KEY)

VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
TEXT_MODEL = "llama-3.3-70b-versatile"
STT_MODEL = "whisper-large-v3-turbo"


class GroqVisionProvider(BaseProvider):
    """Handles image inputs via Llama 4 Scout."""

    @property
    def name(self) -> str:
        return "groq-vision"

    async def solve(self, request: RelayRequest) -> str:
        if not request.image_b64:
            raise ValueError("GroqVisionProvider requires image_b64.")

        messages = [
            {"role": "system", "content": request.system_instruction},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": request.question or "Describe and solve this."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{request.image_b64}"},
                    },
                ],
            },
        ]

        response = await _client.chat.completions.create(
            model=VISION_MODEL,
            messages=messages,
            temperature=0.4,
            max_tokens=2048,
        )
        return response.choices[0].message.content


class GroqTextProvider(BaseProvider):
    """Handles plain-text questions."""

    @property
    def name(self) -> str:
        return "groq-text"

    async def solve(self, request: RelayRequest) -> str:
        if not request.question:
            raise ValueError("GroqTextProvider requires a question.")

        response = await _client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": request.system_instruction},
                {"role": "user", "content": request.question},
            ],
            temperature=0.4,
            max_tokens=2048,
        )
        return response.choices[0].message.content


async def transcribe_audio_bytes(flac_audio_bytes: bytes) -> str:
    """
    Transcribes pre-processed 16kHz FLAC bytes using Whisper.
    Called by the orchestrator after audio_processor runs ffmpeg.
    """
    logger.debug(f"Groq STT: transcribing {len(flac_audio_bytes)} bytes of FLAC audio")

    with tempfile.NamedTemporaryFile(suffix=".flac", delete=False) as tmp:
        tmp.write(flac_audio_bytes)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as f:
            transcription = await _client.audio.transcriptions.create(
                file=("audio.flac", f),
                model=STT_MODEL,
                response_format="text",
                language="en",
            )
        return transcription
    finally:
        os.unlink(tmp_path)


# Singletons
groq_vision_provider = GroqVisionProvider()
groq_text_provider = GroqTextProvider()
