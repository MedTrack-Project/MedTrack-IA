"""Modelos de dados compartilhados entre API e inferência."""

from pydantic import BaseModel, ConfigDict, Field


class ExtractedMedicineData(BaseModel):
    """Campos que podem ser extraídos de uma embalagem."""

    model_config = ConfigDict(extra="forbid")

    nome: str | None = None
    agente_ativo: str | None = None
    dosagem: str | None = None
    validade: str | None = None
    quantidade: str | None = None


class DetectionResult(BaseModel):
    """Resultado independente de HTTP da inferência de uma imagem."""

    is_generico: bool
    data: ExtractedMedicineData = Field(default_factory=ExtractedMedicineData)

    @property
    def count(self) -> int:
        return len(self.data.model_dump(exclude_none=True))
