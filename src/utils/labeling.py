import cv2
from ultralytics import YOLO
import os

CLASSES = ["nome", "agente_ativo", "dosagem", "validade", "quantidade"]
current_class = 0
bboxes = []
drawing = False
ix, iy = -1, -1
mouse_x, mouse_y = 0, 0
img_view = None

model = YOLO('../../models/base/yolov8n.pt')


def detect_crop(img_path):
    img = cv2.imread(img_path)

    if img is None:
        print("Erro: Imagem nao encontrada")
        return None

    h_orig, w_orig, _ = img.shape
    results = model.predict(img, conf=0.2)
    biggest = 0
    better_box = None

    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            area = (y2 - y1) * (x2 - x1)
            if area > biggest:
                biggest = area
                better_box = (x1, y1, x2, y2)

    if better_box:
        x1, y1, x2, y2 = better_box

        largura_box = x2 - x1
        altura_box = y2 - y1

        padding_w = int(largura_box)
        padding_h = int(altura_box * 0.2)

        nx1 = max(0, x1 - padding_w)
        ny1 = max(0, y1 - padding_h)
        nx2 = min(w_orig, x2 + padding_w)
        ny2 = min(h_orig, y2 + padding_h)

        crop_img = img[ny1:ny2, nx1:nx2]
        cv2.imwrite('croped_medicine.jpg', crop_img)
        print("Sucesso! Recorte salvo como 'croped_medicine.jpg'")

        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 3)
        cv2.rectangle(img, (nx1, ny1), (nx2, ny2), (0, 255, 0), 3)
        cv2.imwrite('debug_deteccao.jpg', img)
        return crop_img

    print("Erro: Nenhum Objeto detectado pelo YOLO")
    return None


def draw_bbox(event, x, y, flags, param):
    global ix, iy, drawing, bboxes, current_class, img_view, mouse_x, mouse_y

    mouse_x, mouse_y = x, y

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        x_min, x_max = min(ix, x), max(ix, x)
        y_min, y_max = min(iy, y), max(iy, y)

        if (x_max - x_min) > 5 and (y_max - y_min) > 5:
            h, w = img_view.shape[:2]
            cx = (x_min + x_max) / 2.0 / w
            cy = (y_min + y_max) / 2.0 / h
            bw = (x_max - x_min) / w
            bh = (y_max - y_min) / h
            bboxes.append((current_class, cx, cy, bw, bh))

            cv2.rectangle(img_view, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
            cv2.putText(img_view, CLASSES[current_class], (x_min, y_min - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)


def save_labels(img_name, bboxes, output_lbl_dir):
    label_path = os.path.join(output_lbl_dir, os.path.splitext(img_name)[0] + ".txt")

    try:
        with open(label_path, "w") as f:
            for box in bboxes:
                f.write(f"{box[0]} {box[1]:.6f} {box[2]:.6f} {box[3]:.6f} {box[4]:.6f}\n")
        print(f"✅ Salvo: {label_path}")
    except Exception as e:
        print(f"❌ Erro ao salvar label: {e}")


# Pastas de entrada — todas as medicações disponíveis no projeto
input_dirs = [
    'data/remedios'
]

output_dir = '../../dataset/images/train'
output_lbl_dir = '../../dataset/labels/train'
os.makedirs(output_dir, exist_ok=True)
os.makedirs(output_lbl_dir, exist_ok=True)

for input_dir in input_dirs:
    if not os.path.exists(input_dir):
        print(f"⚠️ Pasta não encontrada, pulando: {input_dir}")
        continue

    print(f"\n📂 Processando: {input_dir}")

    for img_name in os.listdir(input_dir):
        if not img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        path = os.path.join(input_dir, img_name)
        crop = detect_crop(path)

        if crop is None:
            continue

        img_view = crop.copy()
        bboxes = []

        cv2.namedWindow("Labeling", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("Labeling", draw_bbox)

        while True:
            temp_canvas = img_view.copy()
            h, w = temp_canvas.shape[:2]

            # Linhas de guia
            cv2.line(temp_canvas, (0, mouse_y), (w, mouse_y), (255, 255, 255), 1)
            cv2.line(temp_canvas, (mouse_x, 0), (mouse_x, h), (255, 255, 255), 1)

            # Retângulo fantasma enquanto arrasta
            if drawing:
                cv2.rectangle(temp_canvas, (ix, iy), (mouse_x, mouse_y), (0, 255, 255), 1)

            # Legenda
            status = f"[{current_class}] {CLASSES[current_class]} | 1-6: Classe | s: Salvar | n: Sem classe | c: Limpar | q: Sair"
            cv2.putText(temp_canvas, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 0, 0), 2)

            cv2.imshow("Labeling", temp_canvas)

            key = cv2.waitKey(1) & 0xFF

            if key == ord('s'):
                save_labels(img_name, bboxes, output_lbl_dir)
                cv2.imwrite(os.path.join(output_dir, img_name), crop)
                break
            elif key == ord('n'):
                save_labels(img_name, [], output_lbl_dir)
                cv2.imwrite(os.path.join(output_dir, img_name), crop)
                print(f"Imagem {img_name} marcada como fundo (sem classes)")
                break
            elif key == ord('c'):
                img_view = crop.copy()
                bboxes = []
            elif ord('1') <= key <= ord('5'):
                current_class = int(chr(key)) - 1
            elif key == ord('q'):
                cv2.destroyAllWindows()
                exit()

        cv2.destroyAllWindows()

print("\n✅ Labeling concluído!")