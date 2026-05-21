import cv2
import easyocr
import re

reader = easyocr.Reader(['en', 'pt'], gpu=True)


def process_crops_with_easyocr(img, x1, y1, x2, y2):
    """
    Recebe o recorte gerado pelo YOLO e aplica o EasyOCR de forma cirúrgica.
    """
    roi = img[y1:y2, x1:x2]
    if roi.size == 0:
        return ""

    resultado = reader.readtext(roi, detail=0, paragraph=False)

    if not resultado:
        return ""

    texto_bruto = " ".join(resultado).replace("\n", " ").strip()
    texto_limpo = re.sub(r'\s+', ' ', texto_bruto)

    return texto_limpo