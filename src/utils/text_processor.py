import re


def limpar_espacos(texto: str) -> str:
    """Elimina quebras de linha e espaços duplicados."""
    if not texto:
        return ""
    texto = texto.replace("\n", " ").strip()
    return re.sub(r'\s+', ' ', texto)


def corrigir_letras_confusas(texto: str) -> str:
    """Corrige números comuns que o OCR confunde com letras em campos alfabéticos."""
    substituicoes = {
        '0': 'O', '1': 'I', '3': 'E', '4': 'A', '5': 'S', '8': 'B'
    }
    lista_palavras = []
    for palavra in texto.split():
        if re.search(r'[a-zA-Z]', palavra) and re.search(r'[013458]', palavra):
            for num, letra in substituicoes.items():
                palavra = palavra.replace(num, letra)
        lista_palavras.append(palavra)
    return " ".join(lista_palavras)


def sanitizar_texto(texto_bruto: str, label_name: str) -> str:
    """
    Função principal de pós-processamento.
    Aplica regras de higienização baseadas no tipo de campo (label).
    """
    texto = limpar_espacos(texto_bruto)
    if not texto:
        return ""

    if label_name == "nome":
        texto = re.sub(r'[@€*_|\\/`~#\$%&.+=§¬^-]', '', texto)
        texto = corrigir_letras_confusas(texto)
        texto = texto.title()  # Ex: "Astros"

    elif label_name == "agente_ativo":
        texto = re.sub(r'[@€*_|\\/`~#\$%&.=§¬^-]', '', texto)
        texto = corrigir_letras_confusas(texto)
        texto = texto.lower()

    elif label_name == "dosagem":
        texto = re.sub(r'[@€*_|`~#\$&=§¬^-]', '', texto)
        texto = re.sub(r'(\d+)\s*(mg|g|ml|l|mcg|ui)\b', r'\1\2', texto, flags=re.IGNORECASE)
        for unidade in ["mg", "ml", "mcg", "ui"]:
            texto = re.sub(r'\b' + unidade + r'\b', unidade, texto, flags=re.IGNORECASE)

    elif label_name == "quantidade":
        texto = re.sub(r'[@€*_|`~#\$%&=§¬^\[\]()-]', '', texto)

        texto = re.sub(r'^(\d+)([a-zA-Z])', r'\1 \2', texto)

    elif label_name == "validade":
        texto = re.sub(r'[@€*_|`~#\$%&=§¬^-]', '', texto)

    return texto.strip(",.-/[]() ")