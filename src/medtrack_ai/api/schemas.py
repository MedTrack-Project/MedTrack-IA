"""Schemas HTTP da versão atual da API."""

from pydantic import BaseModel, Field

from medtrack_ai.domain.models import ExtractedMedicineData


class DetectResponse(BaseModel):
    status: str = "success"
    is_generico: bool
    data: ExtractedMedicineData
    count: int = Field(ge=0)


class DecodeErrorResponse(BaseModel):
    status: str = "error"
    message: str


class ReadinessResponse(BaseModel):
    status: str
    model_version: str | None = None
    reason: str | None = None
