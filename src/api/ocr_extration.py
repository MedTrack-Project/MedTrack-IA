import cv2
import easyocr


reader = easyocr.Reader(['en', 'pt'], gpu=False)

def verificar_generico_preprocess(img):

    resultado = reader.readtext(img, detail=0, paragraph=True)
    texto_completo = " ".join(resultado).lower()

    indicadores = ["medicamento genérico", "genérico", "similar"]
    return any(ind in texto_completo for ind in indicadores)

def process_crops_with_ocr(img, results, reader, model_names):

    extracted_data = {}

    for item in results:
        for box in item.boxes:

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            label_name = model_names[int(box.cls[0])]
            roi = img[y1:y2, x1:x2]

            if roi.size > 0:

                result_ocr = reader.readtext(roi, detail=0, paragraph=True)
                text = " ".join(result_ocr).strip()


                extracted_data[label_name] = text

    return extracted_data