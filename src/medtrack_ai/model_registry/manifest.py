"""Leitura e validação do manifesto de um artefato de modelo."""

import hashlib
import re
from pathlib import Path

from pydantic import AnyHttpUrl, BaseModel, Field, field_validator

SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")


class TrainingMetadata(BaseModel):
    """Metadados de rastreabilidade preenchidos ao promover um modelo."""

    code_revision: str
    dataset_version: str
    metrics: str


class ModelManifest(BaseModel):
    """Descrição imutável de um peso publicado em uma release."""

    schema_version: int = Field(ge=1)
    artifact_version: str
    filename: str
    download_url: AnyHttpUrl
    sha256: str
    local_path: Path
    training: TrainingMetadata
    classes: list[str]

    @field_validator("sha256")
    @classmethod
    def validate_sha256(cls, value: str) -> str:
        normalized = value.removeprefix("sha256:").lower()
        if not SHA256_PATTERN.fullmatch(normalized):
            raise ValueError("sha256 deve conter exatamente 64 caracteres hexadecimais.")
        return normalized

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, value: str) -> str:
        if Path(value).name != value:
            raise ValueError("filename deve conter somente o nome do arquivo.")
        return value


def load_manifest(path: Path) -> ModelManifest:
    """Carrega e valida um manifesto JSON versionado no repositório."""
    return ModelManifest.model_validate_json(path.read_text(encoding="utf-8"))


def sha256_file(path: Path, block_size: int = 1024 * 1024) -> str:
    """Calcula o checksum em blocos, sem manter o arquivo inteiro em memória."""
    digest = hashlib.sha256()
    with path.open("rb") as artifact:
        for block in iter(lambda: artifact.read(block_size), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_checksum(path: Path, expected_sha256: str) -> bool:
    """Informa se o artefato local corresponde ao checksum do manifesto."""
    return sha256_file(path) == expected_sha256.removeprefix("sha256:").lower()
