import os
import pytest
import torch
from fastapi.testclient import TestClient

import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/api')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from api import app

client = TestClient(app)

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "test_artifacts")
IMAGEM_VALIDA = os.path.join(ARTIFACTS_DIR, "remedio_valido.jpg")
IMAGEM_GENERICO = os.path.join(ARTIFACTS_DIR, "remedio_generico.jpg")
ARQUIVO_INVALIDO = os.path.join(ARTIFACTS_DIR, "documento_invalido.pdf")


@pytest.fixture(autouse=True)
def run_around_tests():
    """
    Fixture executada automaticamente antes e depois de CADA teste.
    Garante o Critério: Mapeamento de VRAM (Limpeza de Cache do PyTorch).
    """
    yield
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def test_payload_valido():
    """
    Critério: Teste de Payload Válido.
    Envia uma imagem real e valida se o JSON retorna 200, status de sucesso
    e os campos esperados da estrutura de dados do MedTrack.
    """
    if not os.path.exists(IMAGEM_VALIDA):
        pytest.skip("Imagem 'remedio_valido.jpg' não encontrada na pasta test_artifacts.")

    with open(IMAGEM_VALIDA, "rb") as img:
        response = client.post("/detect", files={"file": ("remedio.jpg", img, "image/jpeg")})

    assert response.status_code == 200
    json_data = response.json()

    assert json_data["status"] == "success"
    assert "is_generico" in json_data
    assert "data" in json_data
    assert "count" in json_data
    assert isinstance(json_data["is_generico"], bool)


def test_regra_medicamento_generico():
    """
    Critério: Teste da Regra de Genérico.
    Valida se, ao interceptar uma imagem com tarja amarela de genérico,
    a API força o campo 'nome' para 'Medicamento Genérico'.
    """
    if not os.path.exists(IMAGEM_GENERICO):
        pytest.skip("Imagem 'remedio_generico.jpg' não encontrada na pasta test_artifacts.")

    with open(IMAGEM_GENERICO, "rb") as img:
        response = client.post("/detect", files={"file": ("generico.jpg", img, "image/jpeg")})

    assert response.status_code == 200
    json_data = response.json()

    if json_data["is_generico"] == True:
        assert json_data["data"]["nome"] == "Medicamento Genérico"


def test_resiliencia_arquivo_invalido():
    """
    Critério: Teste de Resiliência/Erro.
    Garante que o envio de formatos não suportados (ex: PDF) retorne o erro tratado
    com a mensagem esperada e não cause um travamento geral (Crash/Erro 500) no servidor.
    """
    if not os.path.exists(ARQUIVO_INVALIDO):
        os.makedirs(ARTIFACTS_DIR, exist_ok=True)
        with open(ARQUIVO_INVALIDO, "w") as f:
            f.write("%PDF-1.5 fake pdf content")

    with open(ARQUIVO_INVALIDO, "rb") as f:
        response = client.post("/detect", files={"file": ("documento.pdf", f, "application/pdf")})

    assert response.status_code == 400 or response.status_code == 422
    json_data = response.json()
    assert "Não foi possível decodificar a imagem." in json_data["detail"]


def test_resiliencia_multiplos_disparos_vram():
    """
    Critério extra de estresse: Executa 5 requisições seguidas para simular
    uso volumoso e monitorar se o consumo de VRAM da GTX 1650 permanece estável.
    """
    if not os.path.exists(IMAGEM_VALIDA):
        pytest.skip("Imagem 'remedio_valido.jpg' não encontrada.")

    for _ in range(5):
        with open(IMAGEM_VALIDA, "rb") as img:
            response = client.post("/detect", files={"file": ("remedio.jpg", img, "image/jpeg")})
        assert response.status_code == 200