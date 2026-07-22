"""Aplicação FastAPI e ciclo de vida dos recursos de inferência."""

from collections.abc import Callable
from contextlib import asynccontextmanager

import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from medtrack_ai.api.schemas import DecodeErrorResponse, DetectResponse, ReadinessResponse
from medtrack_ai.inference.service import InferenceService, ModelLoadError
from medtrack_ai.inference.yolo_ocr import YoloOcrInferenceService
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
