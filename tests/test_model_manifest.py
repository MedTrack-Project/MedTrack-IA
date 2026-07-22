from pathlib import Path

import pytest

from medtrack_ai.model_registry.manifest import load_manifest, sha256_file, verify_checksum

pytestmark = pytest.mark.unit


def test_manifesto_atual_e_valido() -> None:
    manifest = load_manifest(Path("config/models/medtrack-yolo-v1.0.0.json"))

    assert manifest.artifact_version == "v1.0.0"
    assert manifest.filename == "best.pt"
    assert manifest.sha256 == "4a6a0d6b28fa8588f85c2f2b6ef739988a01ecfe66f8e44ce830492ccc59eaec"
    assert str(manifest.download_url).endswith("/releases/download/v1.0.0/best.pt")


def test_verificacao_de_checksum(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.bin"
    artifact.write_bytes(b"medtrack")

    expected = "761bd1b334b1be36b135fe3f95c7cc3ebf35e878936addb4ab027ba45be13b20"

    assert sha256_file(artifact) == expected
    assert verify_checksum(artifact, f"sha256:{expected}")
    assert not verify_checksum(artifact, "0" * 64)
