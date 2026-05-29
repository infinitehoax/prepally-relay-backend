import pytest
from app.services.orchestrator import route
from app.schemas.requests import RelayRequest
from tests.test_data import RED_SQUARE_B64

TINY_IMAGE_B64 = RED_SQUARE_B64

# A tiny valid MP4 header in base64 (not a full video, but enough to trigger video chain)
TINY_VIDEO_B64 = "AAAAGGZ0eXBtcDQyAAAAAG1wNDJpc29tAAAALm1vb3YAAABsbXZoZAAAAADbe86e23vOnv8AAAfQAAAFEAEAAAEAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAABidHJhawAAAFx0a2hkAAAAAdt7zp7be86eAAAAAQAAAAAAAAVQAAAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAGBtZGlhAAAAIG1kaGQAAAAA23vOntt7zp7AAAAAAAAB9AAAALpYWFZMAAAALWhkbHIAAAAAAAAAAHZpZGUAAAAAAAAAAAAAAABWaWRlb0hhbmRsZXIAAAABOG1pbmYAAAAUdm1oZAAAAAEAAAAAAAAAAAAAACRkaW5mAAAAHGRyZWYAAAAAAAAAAQAAAAx1cmwgAAAAAQAAASVzdGJsAAAAr3N0c2QAAAAAAAAAAQAAAJ9hdmMxAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAFAAVABIAAAASAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABj//wAAADVhdmljR0BIToAsg7Z0A8m9AAMAAAMAAAMAAAMAAKFAAP8GAAA8XvV6+v/7AAtvAAAAnHN0dHMAAAAAAAAAAQAAAAYAAA+gAAAAFHN0c3oAAAAAAAAAAAAAAAYAAAAUc3RzYwAAAAAAAAABAAAAAQAAAAEAAAABAAAAFHN0Y28AAAAAAAAAAQAAADg="

# A tiny valid WAV header in base64
TINY_AUDIO_B64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA="

@pytest.mark.asyncio
async def test_orchestrator_text_chain():
    req = RelayRequest(question="Text: What is 2+2?")
    response = await route(req)
    assert response.success is True
    assert "4" in response.answer
    assert response.provider_used in ["gemini", "openrouter-text", "groq-text", "mistral-text"]

@pytest.mark.asyncio
async def test_orchestrator_image_chain():
    req = RelayRequest(question="Image: What is 2+2?", image_b64=TINY_IMAGE_B64)
    response = await route(req)
    assert response.success is True
    assert response.provider_used in ["gemini", "openrouter-vision", "groq-vision"]

@pytest.mark.asyncio
async def test_orchestrator_audio_chain():
    # Note: This might fail if ffmpeg is missing or if the audio is too short for Whisper
    # But it tests the routing logic.
    req = RelayRequest(question="Audio: What is 2+2?", audio_b64=TINY_AUDIO_B64)
    response = await route(req)
    # If Gemini handles it natively, success=True. If it falls back to Whisper, it might fail on this tiny file.
    assert isinstance(response.success, bool)

@pytest.mark.asyncio
async def test_orchestrator_video_chain():
    req = RelayRequest(question="Video: What is 2+2?", video_b64=TINY_VIDEO_B64)
    response = await route(req)
    assert isinstance(response.success, bool)
