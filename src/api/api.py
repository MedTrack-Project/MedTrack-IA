import os
import cv2
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import torch
import uvicorn
import numpy as np
from fastapi import FastAPI, UploadFile, File
from ultralytics import YOLO
from ocr_extration import process_crops_with_easyocr


if torch.cuda.is_available():
    torch.cuda.set_device(0)
    device = 'cuda'
else:
    device = 'cpu'

print(f"--- ATENÇÃO: YOLOv8 configurado em: {torch.cuda.get_device_name(0) if device == 'cuda' else 'CPU'} ---")

base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.normpath(
    os.path.join(base_dir, "..", "training", "runs", "detect", "runs", "detect", "medtrack_yolo_train2", "weights",
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
        if item.boxes is not None and len(item.boxes) > 0:
            classes_detectadas = item.boxes.cls.cpu().tolist()
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
        if item.boxes is None:
            continue

        for box in item.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
            label_name = model.names[int(box.cls[0].cpu().item())]

            if label_name == "generico":
                continue

            text = process_crops_with_easyocr(img, x1, y1, x2, y2, label_name)
            if text:
                data_extracted["data"][label_name] = text
                data_extracted["count"] += 1

    if is_generico and "nome" in data_extracted["data"]:
        data_extracted["data"]["nome"] = "Medicamento Genérico"
    elif is_generico and "nome" not in data_extracted["data"]:
        data_extracted["data"]["nome"] = "Medicamento Genérico"
        data_extracted["count"] += 1

    if torch.cuda.is_available():
        torch.cuda.synchronize()
        torch.cuda.empty_cache()

    print(data_extracted)
    return data_extracted


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)