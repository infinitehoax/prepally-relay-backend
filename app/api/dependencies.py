from fastapi import Header, HTTPException, status
from app.core.config import settings


async def verify_relay_key(x_relay_key: str = Header(..., alias="X-Relay-Key")) -> str:
    """
    Protect every endpoint behind a shared secret sent by the Android client.
    Header: X-Relay-Key: <RELAY_API_KEY value from .env>
    """
    if x_relay_key != settings.RELAY_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing relay API key.",
        )
    return x_relay_key
