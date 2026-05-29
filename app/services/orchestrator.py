"""
Orchestrator — inspects the RelayRequest payload, selects the correct
fallback chain, performs any necessary media preprocessing, and calls
the FallbackManager.

Chain A: Video uploaded
Chain B: Audio uploaded
Chain C: Image uploaded  (scanned homework)
Chain D: Text only
"""

import copy

from app.core.logger import logger
from app.providers.gemini_client import gemini_provider
from app.providers.groq_client import (
    groq_text_provider,
    groq_vision_provider,
    transcribe_audio_bytes,
)
from app.providers.hyperbolic_client import hyperbolic_vision_provider
from app.providers.mistral_client import mistral_text_provider
from app.providers.openrouter_client import openrouter_text_provider
from app.schemas.requests import RelayRequest
from app.schemas.responses import RelayResponse
from app.services.fallback_manager import execute_with_fallback


async def route(request: RelayRequest) -> RelayResponse:
    """
    Entry point called by the API endpoints.
    Returns a populated RelayResponse.
    """

    # ── Chain A: Video ────────────────────────────────────────────────────────
    if request.video_b64:
        logger.info("[ORCHESTRATOR] Modality: VIDEO → Chain A")
        return await _chain_video(request)

    # ── Chain B: Audio ────────────────────────────────────────────────────────
    if request.audio_b64:
        logger.info("[ORCHESTRATOR] Modality: AUDIO → Chain B")
        return await _chain_audio(request)

    # ── Chain C: Image ────────────────────────────────────────────────────────
    if request.image_b64:
        logger.info("[ORCHESTRATOR] Modality: IMAGE → Chain C")
        return await _chain_image(request)

    # ── Chain D: Text ─────────────────────────────────────────────────────────
    logger.info("[ORCHESTRATOR] Modality: TEXT → Chain D")
    return await _chain_text(request)


# ── Chain implementations ─────────────────────────────────────────────────────

async def _chain_video(request: RelayRequest) -> RelayResponse:
    """
    1. Gemini (native video)
    2. Extract 4 frames → Hyperbolic (Qwen2.5-VL)
    3. Extract 4 frames → Groq Vision (Llama 4 Scout)
    """
    from app.providers.base import BaseProvider
    from app.schemas.requests import RelayRequest as Req

    # Try Gemini first with the original video
    result = await execute_with_fallback([gemini_provider], request)
    if result["success"]:
        return RelayResponse(**result)

    # Gemini failed — extract frames and try vision fallbacks
    logger.info("[ORCHESTRATOR] Gemini failed on video — extracting keyframes for vision fallbacks")
    try:
        from app.utils.video_processor import extract_frames_as_b64
        frames = extract_frames_as_b64(request.video_b64)
    except Exception as exc:
        logger.error(f"[ORCHESTRATOR] Frame extraction failed: {exc}")
        return RelayResponse(
            success=False,
            answer=None,
            provider_used="NONE",
            error_msg="Video processing failed and no fallback was available.",
        )

    # Rebuild request with frames as a list stored in image_b64
    frame_request = request.model_copy(
        update={"video_b64": None, "image_b64": frames}  # type: ignore[arg-type]
    )

    result = await execute_with_fallback(
        [hyperbolic_vision_provider, groq_vision_provider],
        frame_request,
    )
    return RelayResponse(**result)


async def _chain_audio(request: RelayRequest) -> RelayResponse:
    """
    1. Gemini (native audio)
    2. ffmpeg → 16kHz FLAC → Groq Whisper STT → append transcript → Chain D (text)
    """
    result = await execute_with_fallback([gemini_provider], request)
    if result["success"]:
        return RelayResponse(**result)

    logger.info("[ORCHESTRATOR] Gemini failed on audio — converting to FLAC for Groq Whisper")
    try:
        from app.utils.audio_processor import downsample_to_16khz_flac
        flac_bytes = downsample_to_16khz_flac(request.audio_b64)
        transcript = await transcribe_audio_bytes(flac_bytes)
        logger.info(f"[ORCHESTRATOR] Whisper transcript: {transcript[:120]}…")
    except Exception as exc:
        logger.error(f"[ORCHESTRATOR] Audio preprocessing/STT failed: {exc}")
        return RelayResponse(
            success=False,
            answer=None,
            provider_used="NONE",
            error_msg="Audio processing failed and no fallback was available.",
        )

    # Merge transcript into the text question and run Chain D
    combined_question = (
        f"{request.question}\n\n[Transcribed audio]: {transcript}".strip()
        if request.question
        else f"[Transcribed audio]: {transcript}"
    )
    text_request = request.model_copy(
        update={"audio_b64": None, "question": combined_question}
    )
    return await _chain_text(text_request)


async def _chain_image(request: RelayRequest) -> RelayResponse:
    """
    1. Gemini
    2. Hyperbolic (Qwen2.5-VL — great at OCR/maths)
    3. Groq Vision (Llama 4 Scout)
    """
    result = await execute_with_fallback(
        [gemini_provider, hyperbolic_vision_provider, groq_vision_provider],
        request,
    )
    return RelayResponse(**result)


async def _chain_text(request: RelayRequest) -> RelayResponse:
    """
    1. Gemini
    2. OpenRouter Nemotron (reasoning)
    3. Groq Text (Llama 3.3 70B)
    4. Mistral Large
    """
    result = await execute_with_fallback(
        [gemini_provider, openrouter_text_provider, groq_text_provider, mistral_text_provider],
        request,
    )
    return RelayResponse(**result)
