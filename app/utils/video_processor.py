"""
Video Preprocessor — extracts 4 evenly-spaced keyframes from a video.
Used when Gemini Video fails and we need to pass images to OpenRouter/Groq.
Requires: ffmpeg installed and on PATH.
"""

import base64
import glob
import os
import subprocess
import tempfile

from app.core.logger import logger


def extract_frames_as_b64(base64_video: str, num_frames: int = 4) -> list[str]:
    """
    Decodes a base64 video string, extracts `num_frames` evenly-spaced
    JPEG frames using ffmpeg, and returns them as a list of base64 strings.
    """
    video_bytes = base64.b64decode(base64_video)
    logger.debug(f"VideoProcessor: extracting {num_frames} frames from {len(video_bytes)} bytes")

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "input.mp4")
        frame_pattern = os.path.join(tmpdir, "frame_%04d.jpg")

        with open(input_path, "wb") as f:
            f.write(video_bytes)

        # Use fps filter: extract 1 frame every (duration/num_frames) seconds
        # We drive this with a select filter that picks num_frames uniformly
        command = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vf", f"select='not(mod(n,floor(t*25/{num_frames})))',scale=1280:-2",
            "-vsync", "vfr",
            "-frames:v", str(num_frames),
            "-q:v", "3",          # JPEG quality (1=best, 31=worst)
            frame_pattern,
        ]
        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

        if result.returncode != 0:
            # Fallback: simpler fps-based extraction
            logger.warning("VideoProcessor: primary extraction failed, falling back to fps=1")
            command_fallback = [
                "ffmpeg", "-y",
                "-i", input_path,
                "-vf", "fps=1",
                "-frames:v", str(num_frames),
                "-q:v", "3",
                frame_pattern,
            ]
            subprocess.run(command_fallback, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        frames_b64: list[str] = []
        for path in sorted(glob.glob(os.path.join(tmpdir, "frame_*.jpg")))[:num_frames]:
            with open(path, "rb") as f:
                frames_b64.append(base64.b64encode(f.read()).decode())

        if not frames_b64:
            raise RuntimeError("VideoProcessor: no frames were extracted from the video.")

        logger.debug(f"VideoProcessor: extracted {len(frames_b64)} frame(s)")
        return frames_b64
