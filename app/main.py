"""
PrepAlly Relay — FastAPI Application
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logger import logger
from app.api.v1.endpoints.homework import router as homework_router
from app.api.v1.endpoints.tts import router as tts_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    # Adjust origins for your production domain
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Global Exception Handler ──────────────────────────────────────────────
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "answer": None,
                "provider_used": "NONE",
                "error_msg": "An unexpected server error occurred.",
            },
        )

    # ── Routes ────────────────────────────────────────────────────────────────
    app.include_router(
        homework_router,
        prefix="/api/v1/homework",
        tags=["Homework"],
    )
    app.include_router(
        tts_router,
        prefix="/api/v1/audio",
        tags=["Audio / TTS"],
    )

    # ── Health check ──────────────────────────────────────────────────────────
    @app.get("/health", tags=["System"])
    async def health() -> dict:
        return {"status": "ok", "version": settings.APP_VERSION}

    logger.info(f"PrepAlly Relay v{settings.APP_VERSION} initialised.")
    return app


app = create_app()
