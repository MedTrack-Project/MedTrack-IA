import os
import cv2
import torch
import uvicorn
import numpy as np
from fastapi import FastAPI, UploadFile, File
from ultralytics import YOLO
import easyocr

if torch.cuda.is_available():
    torch.cuda.set_device(0)
    device = 'cuda'
else:
    device = 'cpu'

print(f"--- ATENÇÃO: YOLOv8 configurado em: {torch.cuda.get_device_name(0) if device == 'cuda' else 'CPU'} ---")

reader = easyocr.Reader(['en', 'pt'], gpu=True)


base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.normpath(
    os.path.join(base_dir, "..", "training", "runs", "detect", "runs", "detect", "medtrack_yolo_train", "weights",
                 "best.pt")
)



if not os.path.exists(model_path):
    print(f"❌ ERRO: Peso do modelo não encontrado em: {model_path}")
    exit()

model = YOLO(model_path).to(device)

app = FastAPI(title="MedTrack AI - OCR API Otimizada")


@app.post("/detect")
async def extract_medicine_info(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return {"status": "error", "message": "Não foi possível decodificar a imagem."}

    max_dim = 1024
    h, w = img.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))

    results = model.predict(img, conf=0.5, device=device)


    is_generico = False
    for item in results:

        classes_detectadas = item.boxes.cls.tolist()
        for cls_idx in classes_detectadas:
            if model.names[int(cls_idx)] == "generico":
                is_generico = True
                break
        if is_generico:
            break

    data_extracted = {
        "status": "success",
        "is_generico": is_generico,
        "data": {},
        "count": 0
    }

    for item in results:
        for box in item.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            label_name = model.names[int(box.cls[0])]

            if label_name == "generico":
                continue

            if label_name == "nome" and is_generico:
                data_extracted["data"][label_name] = "Medicamento Genérico"
                data_extracted["count"] += 1
                continue

            roi = img[y1:y2, x1:x2]
            if roi.size > 0:
                result_ocr = reader.readtext(roi, detail=0, paragraph=False)
                text = " ".join(result_ocr).strip()

                if text:
                    data_extracted["data"][label_name] = text
                    data_extracted["count"] += 1

    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    print(data_extracted)
    return data_extracted


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)