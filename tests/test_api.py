"""Testes de contrato da API sem dependência de pesos, GPU ou OCR real."""

import base64
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from medtrack_ai.api.main import create_app
from medtrack_ai.domain.models import DetectionResult, ExtractedMedicineData
from medtrack_ai.inference.service import ModelLoadError
from medtrack_ai.settings import Settings

JPEG_1X1 = base64.b64decode(
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////"
    "2wBDAf//////////////////////////////////////////////////////////////////////////////////////wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAf/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIQAxAAAAH/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oACAEBAAEFAqf/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oACAEDAQE/Aaf/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oACAECAQE/Aaf/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oACAEBAAY/Ap//xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oACAEBAAE/Iaf/2gAMAwEAAgADAAAAEP/EABQRAQAAAAAAAAAAAAAAAAAAABD/2gAIAQMBAT8QH//EABQRAQAAAAAAAAAAAAAAAAAAABD/2gAIAQIBAT8QH//EABQQAQAAAAAAAAAAAAAAAAAAABD/2gAIAQEAAT8QH//Z"
)


class FakeInferenceService:
    model_version = "model-v1.0.0"

    def detect(self, image: object) -> DetectionResult:
        return DetectionResult(
            is_generico=True,
            data=ExtractedMedicineData(nome="Medicamento Genérico", dosagem="500mg"),
        )


def fake_factory(_: Settings) -> FakeInferenceService:
    return FakeInferenceService()


def unavailable_factory(_: Settings) -> FakeInferenceService:
    raise ModelLoadError("Peso do modelo não encontrado.")


@pytest.fixture
def client() -> Iterator[TestClient]:
    app = create_app(settings=Settings(), inference_factory=fake_factory)
    with TestClient(app) as test_client:
        yield test_client


def test_detect_preserva_contrato_de_sucesso(client: TestClient) -> None:
    response = client.post("/detect", files={"file": ("medicamento.jpg", JPEG_1X1, "image/jpeg")})

    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "is_generico": True,
        "data": {"nome": "Medicamento Genérico", "dosagem": "500mg"},
        "count": 2,
    }


def test_detect_rejeita_tipo_de_arquivo_invalido(client: TestClient) -> None:
    response = client.post("/detect", files={"file": ("arquivo.pdf", b"%PDF", "application/pdf")})

    assert response.status_code == 400
    assert response.json()["detail"] == "Não foi possível decodificar a imagem."


def test_detect_preserva_erro_de_imagem_ilegivel(client: TestClient) -> None:
    response = client.post("/detect", files={"file": ("corrompida.jpg", b"invalido", "image/jpeg")})

    assert response.status_code == 200
    assert response.json() == {
        "status": "error",
        "message": "Não foi possível decodificar a imagem.",
    }


def test_health_e_readiness(client: TestClient) -> None:
    assert client.get("/healthz").json() == {"status": "ok"}
    assert client.get("/readyz").json() == {"status": "ready", "model_version": "model-v1.0.0"}


def test_readiness_indica_modelo_ausente() -> None:
    app = create_app(settings=Settings(), inference_factory=unavailable_factory)
    with TestClient(app) as client:
        response = client.get("/readyz")

    assert response.status_code == 503
    assert response.json() == {"status": "not_ready", "reason": "Peso do modelo não encontrado."}
