"""
Audio Preprocessor — converts any audio format to 16kHz mono FLAC for Groq Whisper.
Requires: ffmpeg installed and on PATH.
"""

import base64
import subprocess
import tempfile
import os

from app.core.logger import logger


def downsample_to_16khz_flac(base64_audio: str) -> bytes:
    """
    Decodes a base64 audio string (M4A, MP3, WAV, OGG, etc.),
    uses ffmpeg to convert to 16kHz mono FLAC, and returns raw bytes.
    """
    audio_bytes = base64.b64decode(base64_audio)
    logger.debug(f"AudioProcessor: converting {len(audio_bytes)} bytes to 16kHz FLAC")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".input_audio") as tmp_in:
        tmp_in.write(audio_bytes)
        tmp_in_path = tmp_in.name

    tmp_out_path = tmp_in_path + ".flac"

    try:
        command = [
            "ffmpeg", "-y",
            "-i", tmp_in_path,
            "-ar", "16000",      # sample rate → 16 kHz
            "-ac", "1",          # mono
            "-map", "0:a",       # audio stream only
            "-c:a", "flac",
            tmp_out_path,
        ]
        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

        if result.returncode != 0:
            err = result.stderr.decode(errors="replace")
            raise RuntimeError(f"ffmpeg audio conversion failed: {err}")

        with open(tmp_out_path, "rb") as f:
            flac_bytes = f.read()

        logger.debug(f"AudioProcessor: produced {len(flac_bytes)} bytes of FLAC")
        return flac_bytes

    finally:
        for p in (tmp_in_path, tmp_out_path):
            if os.path.exists(p):
                os.unlink(p)
