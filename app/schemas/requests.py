from pydantic import BaseModel, Field
from typing import Optional


class RelayRequest(BaseModel):
    subject: str = Field(default="General", description="Subject area, e.g. Math, Physics")
    question: str = Field(default="", description="The student's typed question or prompt")
    system_instruction: str = Field(
        default="You are PrepAlly, an expert AI tutor. Explain clearly and step-by-step.",
        description="System instruction / persona for the AI",
    )
    image_b64: Optional[str] = Field(default=None, description="Base64-encoded image (JPEG/PNG)")
    video_b64: Optional[str] = Field(default=None, description="Base64-encoded video (MP4/MOV)")
    audio_b64: Optional[str] = Field(default=None, description="Base64-encoded audio (M4A/MP3/WAV)")
