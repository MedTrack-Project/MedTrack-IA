"""Aplicação FastAPI e ciclo de vida dos recursos de inferência."""

from collections.abc import Callable
from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from medtrack_ai.api.schemas import DecodeErrorResponse, DetectResponse, ReadinessResponse
from medtrack_ai.inference.service import InferenceService, ModelLoadError
from medtrack_ai.inference.yolo_ocr import YoloOcrInferenceService
from medtrack_ai.observability import configure_logging
from medtrack_ai.settings import Settings, get_settings

InferenceFactory = Callable[[Settings], InferenceService]


def default_inference_factory(settings: Settings) -> InferenceService:
    """Constrói a implementação de produção somente durante o startup."""
    return YoloOcrInferenceService(
        model_uri=settings.model_uri,
        model_version=settings.model_version,
        device=settings.device,
        confidence=settings.yolo_confidence,
    )


def create_app(
    settings: Settings | None = None,
    inference_factory: InferenceFactory = default_inference_factory,
) -> FastAPI:
    """Cria uma aplicação testável, sem carregar IA durante a importação."""
    resolved_settings = settings or get_settings()
    logger = configure_logging(resolved_settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.inference = None
        app.state.readiness_reason = None
        try:
            app.state.inference = inference_factory(resolved_settings)
        except ModelLoadError as error:
            app.state.readiness_reason = str(error)
        yield
        app.state.inference = None

    app = FastAPI(
        title="MedTrack AI - OCR API Otimizada",
        version="1.0.0",
        lifespan=lifespan,
    )

    cors_origins = [
        origin.strip() for origin in resolved_settings.cors_origins.split(",") if origin.strip()
    ]
    if cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=False,
            allow_methods=["POST", "GET"],
            allow_headers=["Content-Type", "X-Request-ID"],
        )

    @app.middleware("http")
    async def log_request(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        started_at = perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "request.failed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "request_id": request_id,
                    "duration_ms": round((perf_counter() - started_at) * 1000, 2),
                },
            )
            raise

        duration_ms = round((perf_counter() - started_at) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "request.completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "request_id": request_id,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "model_version": getattr(request.app.state.inference, "model_version", None),
            },
        )
        return response

    @app.get("/healthz")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz", response_model=ReadinessResponse, response_model_exclude_none=True)
    async def ready(request: Request) -> ReadinessResponse | JSONResponse:
        inference = request.app.state.inference
        if inference is None:
            return JSONResponse(
                status_code=503,
                content=ReadinessResponse(
                    status="not_ready",
                    reason=request.app.state.readiness_reason or "Modelo ainda não foi carregado.",
                ).model_dump(exclude_none=True),
            )
        return ReadinessResponse(status="ready", model_version=inference.model_version)

    @app.post(
        "/detect",
        response_model=DetectResponse | DecodeErrorResponse,
        response_model_exclude_none=True,
    )
    async def detect(request: Request, file: UploadFile = File(...)):
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Não foi possível decodificar a imagem.")

        image = cv2.imdecode(np.frombuffer(await file.read(), np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            return DecodeErrorResponse(message="Não foi possível decodificar a imagem.")

        image = _resize_image(image, resolved_settings.max_image_dimension)
        inference: InferenceService | None = request.app.state.inference
        if inference is None:
            raise HTTPException(
                status_code=503,
                detail=(
                    request.app.state.readiness_reason
                    or "Modelo não está pronto para inferência."
                ),
            )

        result = inference.detect(image)
        return DetectResponse(
            is_generico=result.is_generico,
            data=result.data,
            count=result.count,
        )

    return app


def _resize_image(image: np.ndarray, max_dimension: int) -> np.ndarray:
    height, width = image.shape[:2]
    if max(height, width) <= max_dimension:
        return image
    scale = max_dimension / max(height, width)
    return cv2.resize(image, (int(width * scale), int(height * scale)))


app = create_app()
