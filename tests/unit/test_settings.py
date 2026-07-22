import pytest
from pydantic import ValidationError

from medtrack_ai.settings import Settings

pytestmark = pytest.mark.unit


def test_settings_le_variaveis_de_ambiente(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MEDTRACK_ENV", "test")
    monkeypatch.setenv("MEDTRACK_MODEL_VERSION", "v9.9.9")
    monkeypatch.setenv("MEDTRACK_YOLO_CONFIDENCE", "0.75")

    settings = Settings()

    assert settings.environment == "test"
    assert settings.model_version == "v9.9.9"
    assert settings.yolo_confidence == 0.75


def test_settings_rejeita_limiar_invalido() -> None:
    with pytest.raises(ValidationError):
        Settings(yolo_confidence=1.1)
