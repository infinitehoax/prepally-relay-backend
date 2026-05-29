import pytest
import base64
from app.providers.gemini_client import gemini_provider
from app.providers.openrouter_client import openrouter_text_provider, openrouter_vision_provider
from app.providers.groq_client import groq_text_provider, groq_vision_provider
from app.providers.mistral_client import mistral_text_provider
from app.schemas.requests import RelayRequest
from tests.test_data import RED_SQUARE_B64

TINY_IMAGE_B64 = RED_SQUARE_B64

@pytest.mark.asyncio
async def test_gemini_text():
    req = RelayRequest(question="Hello, what is 2+2?")
    answer = await gemini_provider.solve(req)
    assert isinstance(answer, str)
    assert "4" in answer

@pytest.mark.asyncio
async def test_gemini_vision():
    req = RelayRequest(question="What is in this image?", image_b64=TINY_IMAGE_B64)
    answer = await gemini_provider.solve(req)
    assert isinstance(answer, str)
    assert len(answer) > 0

@pytest.mark.asyncio
async def test_openrouter_vision_multi_image():
    # Simulate multiple frames as list
    req = RelayRequest(question="What is in these images?", image_b64=[TINY_IMAGE_B64, TINY_IMAGE_B64])
    answer = await openrouter_vision_provider.solve(req)
    assert isinstance(answer, str)
    assert len(answer) > 0

@pytest.mark.asyncio
async def test_openrouter_text():
    req = RelayRequest(question="Hello, what is 2+2?")
    answer = await openrouter_text_provider.solve(req)
    assert isinstance(answer, str)
    assert "4" in answer

@pytest.mark.asyncio
async def test_openrouter_vision():
    req = RelayRequest(question="What is in this image?", image_b64=TINY_IMAGE_B64)
    answer = await openrouter_vision_provider.solve(req)
    assert isinstance(answer, str)
    assert len(answer) > 0

@pytest.mark.asyncio
async def test_groq_text():
    req = RelayRequest(question="Hello, what is 2+2?")
    answer = await groq_text_provider.solve(req)
    assert isinstance(answer, str)
    assert "4" in answer

@pytest.mark.asyncio
async def test_groq_vision():
    req = RelayRequest(question="What is in this image?", image_b64=TINY_IMAGE_B64)
    answer = await groq_vision_provider.solve(req)
    assert isinstance(answer, str)
    assert len(answer) > 0

@pytest.mark.asyncio
async def test_mistral_text():
    req = RelayRequest(question="Hello, what is 2+2?")
    answer = await mistral_text_provider.solve(req)
    assert isinstance(answer, str)
    assert "4" in answer
