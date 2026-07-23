"""Fronteira entre a API HTTP e as bibliotecas de visão computacional."""

from pathlib import Path
from typing import Protocol

import numpy as np

from medtrack_ai.domain.models import DetectionResult


class InferenceService(Protocol):
    """Contrato mínimo necessário para a API solicitar uma inferência."""

    model_version: str

    def detect(self, image: np.ndarray) -> DetectionResult:
        """Extrai dados de uma imagem BGR decodificada."""
        ...


class ModelLoadError(RuntimeError):
    """Indica que o serviço não conseguiu carregar um artefato de modelo."""


def require_local_model(model_uri: str) -> Path:
    """Valida o artefato local; URIs remotas serão materializadas pelo fetcher."""
    if "://" in model_uri:
        raise ModelLoadError(
            "MODEL_URI deve apontar para um arquivo local. "
            "Baixe o artefato versionado antes de iniciar o serviço."
        )

    model_path = Path(model_uri)
    if not model_path.is_file():
        raise ModelLoadError(f"Peso do modelo não encontrado em: {model_path}")
    return model_path
