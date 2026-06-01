"""
Fallback Manager — the Chain of Responsibility engine.

Iterates through a list of BaseProvider instances in order.
On any exception it logs the failure, swallows the error, and tries the next provider.
If every provider fails, returns a structured failure dict.
"""

from app.core.logger import logger
from app.providers.base import BaseProvider
from app.schemas.requests import RelayRequest


async def execute_with_fallback(
    provider_chain: list[BaseProvider],
    request: RelayRequest,
) -> dict:
    """
    Args:
        provider_chain: Ordered list of provider instances to try.
        request:        The validated RelayRequest payload.

    Returns:
        dict with keys: success, answer, provider_used, error_msg
    """
    for provider in provider_chain:
        try:
            logger.info(f"[ROUTING] → {provider.name}")
            answer = await provider.solve(request)

            if not answer or not answer.strip():
                raise ValueError(f"{provider.name} returned an empty answer.")

            logger.info(f"[SUCCESS] ✓ {provider.name}")
            return {
                "success": True,
                "answer": answer.strip(),
                "provider_used": provider.name,
                "error_msg": None,
            }

        except Exception as exc:
            # Enhanced logging to capture exactly why it's falling back
            logger.error(f"[FAILURE] ✗ {provider.name} — {type(exc).__name__}: {str(exc)[:200]}")
            continue

    logger.critical("[FATAL] All providers in chain exhausted.")
    return {
        "success": False,
        "answer": None,
        "provider_used": "NONE",
        "error_msg": (
            "AI services are experiencing extremely high traffic. "
            "Please wait a moment and try again."
        ),
    }
