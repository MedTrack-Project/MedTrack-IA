from ultralytics import YOLO
import torch
import os

def train_model():
    device = '0' if torch.cuda.is_available() else 'cpu'
    print(f"🚀 Iniciando treinamento no dispositivo: {device}")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "..", "..", "config", "campos.yaml")
    config_path = os.path.normpath(config_path)

    model = YOLO('yolov8n.pt')

    results = model.train(
        data=config_path,
        epochs=100,
        imgsz=640,
        batch=4,
        workers=2,
        device=0,
        project='runs/detect',     # Onde salvar os logs
        name='medtrack_yolo_train',      # Nome da pasta do treino atual
        save=True,
        cache=False                       # Acelera o treino se tiver RAM disponível
    )

    print("✅ Treinamento concluído!")
    print(f"🏆 Melhor modelo salvo em: {results.save_dir}/weights/best.pt")

if __name__ == "__main__":
    train_model()