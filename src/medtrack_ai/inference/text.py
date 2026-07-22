"""Pós-processamento determinístico do texto devolvido pelo OCR."""

import re


def limpar_espacos(texto: str) -> str:
    if not texto:
        return ""
    texto = texto.replace("\n", " ").strip()
    return re.sub(r"\s+", " ", texto)


def corrigir_letras_confusas(texto: str) -> str:
    substituicoes = {"0": "O", "1": "I", "3": "E", "4": "A", "5": "S", "8": "B"}
    palavras_corrigidas = []
    for palavra in texto.split():
        if re.search(r"[a-zA-Z]", palavra) and re.search(r"[013458]", palavra):
            for numero, letra in substituicoes.items():
                palavra = palavra.replace(numero, letra)
        palavras_corrigidas.append(palavra)
    return " ".join(palavras_corrigidas)


def sanitizar_texto(texto_bruto: str, label_name: str) -> str:
    """Aplica regras de limpeza compatíveis com a implementação anterior."""
    texto = limpar_espacos(texto_bruto)
    if not texto:
        return ""

    if label_name == "nome":
        texto = re.sub(r"[@€*_|\\/`~#$%&.+=§¬^-]", "", texto)
        texto = corrigir_letras_confusas(texto).title()
    elif label_name == "agente_ativo":
        texto = re.sub(r"[@€*_|\\/`~#$%&.=§¬^-]", "", texto)
        texto = corrigir_letras_confusas(texto).lower()
    elif label_name == "dosagem":
        texto = re.sub(r"[@€*_|`~#$&=§¬^-]", "", texto)
        texto = re.sub(r"(\d+)\s*(mg|g|ml|l|mcg|ui)\b", r"\1\2", texto, flags=re.IGNORECASE)
        for unidade in ["mg", "ml", "mcg", "ui"]:
            texto = re.sub(r"\b" + unidade + r"\b", unidade, texto, flags=re.IGNORECASE)
    elif label_name == "quantidade":
        texto = re.sub(r"[@€*_|`~#$%&=§¬^\[\]()-]", "", texto)
        texto = re.sub(r"^(\d+)([a-zA-Z])", r"\1 \2", texto)
    elif label_name == "validade":
        texto = re.sub(r"[@€*_|`~#$%&=§¬^-]", "", texto)

    return texto.strip(",.-/[]() ")
