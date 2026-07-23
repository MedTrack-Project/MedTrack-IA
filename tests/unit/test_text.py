import pytest

from medtrack_ai.inference.text import corrigir_letras_confusas, limpar_espacos, sanitizar_texto

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("  Sinvastatina\n  20 mg ", "Sinvastatina 20 mg"),
        ("", ""),
    ],
)
def test_limpar_espacos(raw: str, expected: str) -> None:
    assert limpar_espacos(raw) == expected


def test_corrigir_letras_confusas_apenas_em_texto_alfanumerico() -> None:
    assert corrigir_letras_confusas("A5TR0 500") == "ASTRO 500"


@pytest.mark.parametrize(
    ("label", "raw", "expected"),
    [
        ("nome", "a5tr0***", "Astro"),
        ("agente_ativo", "S1MVASTAT1NA", "simvastatina"),
        ("dosagem", "500 mg", "500mg"),
        ("quantidade", "30comprimidos", "30 comprimidos"),
    ],
)
def test_sanitizar_texto(label: str, raw: str, expected: str) -> None:
    assert sanitizar_texto(raw, label) == expected
