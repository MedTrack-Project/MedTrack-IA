import os

import cv2
import easyocr
import torch
import uvicorn
from fastapi import FastAPI, UploadFile, File
from ultralytics import YOLO
import numpy as np

from src.api.ocr_extration import verificar_generico_preprocess

if torch.cuda.is_available():
    torch.cuda.set_device(0)
    device = 'cuda'
else:
    device = 'cpu'

# Mude para isso:
reader = easyocr.Reader(['en', 'pt'], gpu=False)
print(f"--- ATENÇÃO: Rodando em {torch.cuda.get_device_name(0) if device == 'cuda' else 'CPU'} ---")
base_dir = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(base_dir, "..", "..", "models", "production", "best.pt")
model_path = os.path.normpath(model_path)
model = YOLO(model_path).to(device)


app = FastAPI(title="MedTrack AI - OCR API")


@app.post("/detect")
async def extract_medicine_info(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    is_generico = verificar_generico_preprocess(img)

    results = model.predict(img, conf=0.5, device=device)
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()

    data_extracted = {
        "status": "success",
        "data": {},
        "count": 0,
        "is_generico": is_generico
    }

    for item in results:
        for box in item.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            label_name = model.names[int(box.cls[0])]

            if label_name == "nome" and is_generico:
                data_extracted["data"][label_name] = "Medicamento Genérico"
                data_extracted["count"] += 1
                continue

            roi = img[y1:y2, x1:x2]
            if roi.size > 0:
                result_ocr = reader.readtext(roi, detail=0, paragraph=True)
                text = " ".join(result_ocr).strip()
                data_extracted["data"][label_name] = text
                data_extracted["count"] += 1
    print(data_extracted)
    return data_extracted

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)