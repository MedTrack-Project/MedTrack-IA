"""Smoke test opcional: não executa inferência nem baixa arquivos."""

import os
from pathlib import Path

import pytest

from medtrack_ai.model_registry.manifest import load_manifest, verify_checksum

pytestmark = pytest.mark.model


def test_modelo_local_corresponde_ao_manifesto() -> None:
    if os.getenv("MEDTRACK_RUN_MODEL_SMOKE") != "1":
        pytest.skip("Defina MEDTRACK_RUN_MODEL_SMOKE=1 para validar o artefato local.")

    manifest = load_manifest(Path("config/models/medtrack-yolo-v1.0.0.json"))

    assert manifest.local_path.is_file(), (
        "Modelo ausente. Execute `uv run --group dev python scripts/fetch_model.py`."
    )
    assert verify_checksum(manifest.local_path, manifest.sha256)
