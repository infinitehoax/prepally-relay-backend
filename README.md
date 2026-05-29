# PrepAlly Relay Server

A high-performance **FastAPI** middleware that routes multimodal AI requests through a Gemini-first fallback chain.

## Fallback Matrix

| Chain | Trigger | Priority |
|-------|---------|----------|
| A | Video uploaded | Gemini → Hyperbolic (frames) → Groq (frames) |
| B | Audio uploaded | Gemini → Groq Whisper STT → Chain D |
| C | Image uploaded | Gemini → Hyperbolic → Groq Vision |
| D | Text only | Gemini → OpenRouter → Groq Text → Mistral |

---

## Quick Start

### 1. Prerequisites

- Python 3.11+
- `ffmpeg` installed and on your PATH (`brew install ffmpeg` / `apt install ffmpeg`)

### 2. Install

```bash
cd prepally-relay-backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure

```bash
cp .env.example .env
# Edit .env and fill in all API keys + RELAY_API_KEY
```

### 4. Run

```bash
python run.py
# Server starts at http://localhost:8000
# Interactive docs: http://localhost:8000/docs
```

---

## Docker

```bash
cp .env.example .env   # fill in keys first
docker compose up --build
```

---

## API Reference

### Authentication

Every request must include the header:

```
X-Relay-Key: <your RELAY_API_KEY from .env>
```

### POST `/api/v1/homework/solve`

**Request body (JSON):**

```json
{
  "subject": "Mathematics",
  "question": "Solve: 2x + 5 = 13",
  "system_instruction": "You are PrepAlly, an expert AI tutor.",
  "image_b64": null,
  "video_b64": null,
  "audio_b64": null
}
```

Send **only one** of `image_b64`, `video_b64`, or `audio_b64` per request (base64-encoded).

**Response:**

```json
{
  "success": true,
  "answer": "x = 4 ...",
  "provider_used": "gemini",
  "error_msg": null
}
```

### GET `/health`

Returns `{ "status": "ok", "version": "1.0.0" }` — no auth required.

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `RELAY_API_KEY` | Shared secret sent by Android client in `X-Relay-Key` header |
| `GEMINI_API_KEY` | Google AI Studio key |
| `GROQ_API_KEY` | Groq Cloud key |
| `HYPERBOLIC_API_KEY` | Hyperbolic AI key |
| `OPENROUTER_API_KEY` | OpenRouter key |
| `MISTRAL_API_KEY` | Mistral AI key |

---

## Project Structure

```
prepally-relay-backend/
├── run.py                          # Entrypoint
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── app/
    ├── main.py                     # FastAPI app factory
    ├── core/
    │   ├── config.py               # Pydantic settings
    │   ├── logger.py               # Centralised logging
    │   └── exceptions.py           # Custom error types
    ├── api/
    │   ├── dependencies.py         # X-Relay-Key auth
    │   └── v1/endpoints/
    │       ├── homework.py         # POST /api/v1/homework/solve
    │       └── tts.py              # POST /api/v1/audio/tts (stub)
    ├── schemas/
    │   ├── requests.py             # RelayRequest
    │   └── responses.py            # RelayResponse
    ├── services/
    │   ├── orchestrator.py         # Modality detection + chain selection
    │   └── fallback_manager.py     # Chain-of-Responsibility loop
    ├── providers/
    │   ├── base.py                 # Abstract BaseProvider
    │   ├── gemini_client.py        # Primary (all modalities)
    │   ├── groq_client.py          # Fallback 1 (STT + vision + text)
    │   ├── hyperbolic_client.py    # Fallback 2 (vision/OCR)
    │   ├── openrouter_client.py    # Fallback 3 (reasoning/text)
    │   └── mistral_client.py       # Fallback 4 (text)
    └── utils/
        ├── audio_processor.py      # ffmpeg → 16kHz FLAC
        ├── video_processor.py      # ffmpeg → 4 keyframes
        └── media_parser.py         # base64 helpers
```
