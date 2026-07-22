from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações validadas, carregadas de variáveis MEDTRACK_* e de .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="MEDTRACK_",
        extra="ignore",
    )

    environment: str = Field(default="local", validation_alias="MEDTRACK_ENV")
    log_level: str = "INFO"
    model_uri: str = "models/medtrack-yolo/v1.0.0/best.pt"
    model_version: str = "v1.0.0"
    device: str = "cpu"
    max_image_dimension: int = Field(default=1024, ge=1)
    yolo_confidence: float = Field(default=0.5, ge=0, le=1)
    cors_origins: str = ""

    @property
    def model_path(self) -> Path:
        """Expõe caminhos locais como Path; URIs remotas serão tratadas depois."""
        return Path(self.model_uri)


@lru_cache
def get_settings() -> Settings:
    """Retorna uma única instância por processo."""
    return Settings()
