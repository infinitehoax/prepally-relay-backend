"""
POST /api/v1/homework/solve

Accepts a multimodal RelayRequest and returns a RelayResponse.
Protected by X-Relay-Key header authentication.
"""

from fastapi import APIRouter, Depends

from app.api.dependencies import verify_relay_key
from app.schemas.requests import RelayRequest
from app.schemas.responses import RelayResponse
from app.services.orchestrator import route

router = APIRouter()


@router.post("/solve", response_model=RelayResponse, summary="Solve a homework question")
async def solve_homework(
    payload: RelayRequest,
    _: str = Depends(verify_relay_key),
) -> RelayResponse:
    """
    Accepts text, image, audio, or video payloads and routes through
    the Gemini-first fallback chain appropriate for the modality.
    """
    return await route(payload)
