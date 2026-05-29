"""
POST /api/v1/audio/tts

Text-to-Speech endpoint stub.
Primary: Gemini TTS (when available in the API).
Fallback: Hyperbolic TTS → Edge-TTS (open-source).

Note: Extend this once a TTS provider is confirmed in your stack.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from app.api.dependencies import verify_relay_key

router = APIRouter()


class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "en-US-Neural2-F"
    speed: Optional[float] = 1.0


class TTSResponse(BaseModel):
    success: bool
    audio_b64: Optional[str] = None   # base64-encoded MP3
    provider_used: str
    error_msg: Optional[str] = None


@router.post("/tts", response_model=TTSResponse, summary="Convert text to speech")
async def text_to_speech(
    payload: TTSRequest,
    _: str = Depends(verify_relay_key),
) -> TTSResponse:
    """
    Placeholder — wire up your TTS provider here.
    Currently returns a clear 'not implemented' so the app can handle it gracefully.
    """
    return TTSResponse(
        success=False,
        audio_b64=None,
        provider_used="NONE",
        error_msg="TTS is not yet configured on this relay. Implement in app/api/v1/endpoints/tts.py.",
    )
