import cv2
import easyocr
from utils.text_processor import sanitizar_texto

reader = easyocr.Reader(['en', 'pt'], gpu=True)


def process_crops_with_easyocr(img, x1, y1, x2, y2, label_name):
    """
    Recorta a região de interesse, executa a leitura óptica
    e delega a limpeza para o módulo utilitário de texto.
    """
    roi = img[y1:y2, x1:x2]
    if roi.size == 0:
        return ""

    resultado = reader.readtext(roi, detail=0, paragraph=False)
    if not resultado:
        return ""

    texto_bruto = " ".join(resultado).strip()

    # Executa a limpeza chamando o módulo separado
    return sanitizar_texto(texto_bruto, label_name)