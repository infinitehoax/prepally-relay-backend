"""
Media Parser — lightweight base64 helpers used across providers and processors.
"""

import base64


def decode_b64(b64_string: str) -> bytes:
    """Safely decode a base64 string, stripping data-URI prefix if present."""
    if "," in b64_string:
        b64_string = b64_string.split(",", 1)[1]
    return base64.b64decode(b64_string)


def encode_b64(raw_bytes: bytes) -> str:
    """Encode bytes to a plain base64 string."""
    return base64.b64encode(raw_bytes).decode()
