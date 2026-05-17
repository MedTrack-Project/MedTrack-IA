from ultralytics import YOLO
import cv2

# Carrega o modelo base
model = YOLO('../../models/base/yolov8n.pt')

# 1. Carrega o SEU modelo treinado (ajuste o caminho se necessário)
model = YOLO(r'/runs/detect/train5/weights/best.pt')

# 2. Escolha uma imagem de teste (uma que o modelo nunca viu)
img_path = '20260330_115955.jpg'

# 3. Faz a detecção
results = model.predict(source=img_path, conf=0.5, save=True)

# ... (após o processamento do modelo)
for r in results:
    im_array = r.plot()

    # 1. Cria a janela como redimensionável
    cv2.namedWindow("Resultado", cv2.WINDOW_NORMAL)

    # 2. Define um tamanho fixo (ex: 800x600) para ela não ocupar a tela toda
    cv2.resizeWindow("Resultado", 800, 600)

    # 3. Mostra a imagem dentro dessa janela controlada
    cv2.imshow("Resultado", im_array)
    cv2.waitKey(0)
cv2.destroyAllWindows()