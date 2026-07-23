import os
import random

import cv2
import numpy as np

INPUT_IMG_DIR = "../../dataset/images/train"
INPUT_LBL_DIR = "../../dataset/labels/train"
OUTPUT_IMG_DIR = "../../dataset/images/train"
OUTPUT_LBL_DIR = "../../dataset/labels/train"

AUGMENTATIONS_PER_IMAGE = 5

os.makedirs(OUTPUT_IMG_DIR, exist_ok=True)
os.makedirs(OUTPUT_LBL_DIR, exist_ok=True)


def ajustar_brilho_contraste(img):
    alpha = random.uniform(0.6, 1.4)  # contraste
    beta = random.randint(-40, 40)  # brilho
    return cv2.convertScaleAbs(img, alpha=alpha, beta=beta)


def adicionar_ruido(img):
    ruido = np.random.normal(0, random.uniform(5, 20), img.shape).astype(np.float32)
    img_ruido = np.clip(img.astype(np.float32) + ruido, 0, 255).astype(np.uint8)
    return img_ruido


def blur_leve(img):
    kernel = random.choice([3, 5])
    return cv2.GaussianBlur(img, (kernel, kernel), 0)


def rotacao_leve(img, labels):
    h, w = img.shape[:2]
    angulo = random.uniform(-15, 15)
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angulo, 1.0)
    img_rot = cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REPLICATE)

    novas_labels = []
    for label in labels:
        cls, cx, cy, bw, bh = label

        # Converte para coordenadas absolutas
        x1 = (cx - bw / 2) * w
        y1 = (cy - bh / 2) * h
        x2 = (cx + bw / 2) * w
        y2 = (cy + bh / 2) * h

        # Rotaciona os 4 cantos
        pontos = np.array([[x1, y1], [x2, y1], [x2, y2], [x1, y2]], dtype=np.float32)
        pontos = np.hstack([pontos, np.ones((4, 1))])
        pontos_rot = (M @ pontos.T).T

        # Novo bounding box que envolve os cantos rotacionados
        nx1 = np.clip(pontos_rot[:, 0].min(), 0, w)
        ny1 = np.clip(pontos_rot[:, 1].min(), 0, h)
        nx2 = np.clip(pontos_rot[:, 0].max(), 0, w)
        ny2 = np.clip(pontos_rot[:, 1].max(), 0, h)

        ncx = ((nx1 + nx2) / 2) / w
        ncy = ((ny1 + ny2) / 2) / h
        nbw = (nx2 - nx1) / w
        nbh = (ny2 - ny1) / h

        novas_labels.append((cls, ncx, ncy, nbw, nbh))

    return img_rot, novas_labels


def flip_horizontal(img, labels):
    img_flip = cv2.flip(img, 1)
    novas_labels = []
    for label in labels:
        cls, cx, cy, bw, bh = label
        novas_labels.append((cls, 1.0 - cx, cy, bw, bh))  # inverte cx
    return img_flip, novas_labels


def simular_sombra(img):
    img_sombra = img.copy().astype(np.float32)
    h, w = img.shape[:2]

    x1, x2 = sorted(random.sample(range(w), 2))
    fator = random.uniform(0.4, 0.7)
    img_sombra[:, x1:x2] *= fator

    return np.clip(img_sombra, 0, 255).astype(np.uint8)


def carregar_labels(label_path):
    labels = []
    if not os.path.exists(label_path):
        return labels
    with open(label_path) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 5:
                labels.append(
                    (
                        int(parts[0]),
                        float(parts[1]),
                        float(parts[2]),
                        float(parts[3]),
                        float(parts[4]),
                    )
                )
    return labels


def salvar_labels(label_path, labels):
    with open(label_path, "w") as f:
        for label in labels:
            f.write(f"{label[0]} {label[1]:.6f} {label[2]:.6f} {label[3]:.6f} {label[4]:.6f}\n")


def aplicar_augmentation(img, labels):
    img = ajustar_brilho_contraste(img)

    if random.random() > 0.4:
        img = adicionar_ruido(img)

    if random.random() > 0.4:
        img = blur_leve(img)

    if random.random() > 0.5:
        img = simular_sombra(img)

    if random.random() > 0.5:
        img, labels = rotacao_leve(img, labels)

    if random.random() > 0.5:
        img, labels = flip_horizontal(img, labels)

    return img, labels


imagens = [
    f
    for f in os.listdir(INPUT_IMG_DIR)
    if f.lower().endswith((".jpg", ".jpeg", ".png")) and "_aug" not in f
]

print(f"\n🔍 {len(imagens)} imagens originais encontradas.")
print(f"📦 Gerando {AUGMENTATIONS_PER_IMAGE} versões por imagem...")
print(f"📊 Total esperado: {len(imagens) * AUGMENTATIONS_PER_IMAGE} novas imagens\n")

total_geradas = 0

for img_name in imagens:
    img_path = os.path.join(INPUT_IMG_DIR, img_name)
    label_path = os.path.join(INPUT_LBL_DIR, os.path.splitext(img_name)[0] + ".txt")

    img = cv2.imread(img_path)
    if img is None:
        print(f"⚠️ Não foi possível ler: {img_name}")
        continue

    labels = carregar_labels(label_path)

    nome_base = os.path.splitext(img_name)[0]
    ext = os.path.splitext(img_name)[1]

    for i in range(AUGMENTATIONS_PER_IMAGE):
        img_aug, labels_aug = aplicar_augmentation(img.copy(), labels.copy())

        novo_nome = f"{nome_base}_aug{i + 1}{ext}"
        novo_label = f"{nome_base}_aug{i + 1}.txt"

        cv2.imwrite(os.path.join(OUTPUT_IMG_DIR, novo_nome), img_aug)
        salvar_labels(os.path.join(OUTPUT_LBL_DIR, novo_label), labels_aug)
        total_geradas += 1

    print(f"✅ {img_name} → {AUGMENTATIONS_PER_IMAGE} versões geradas")

print(f"\n🎉 Concluído! {total_geradas} imagens aumentadas salvas em '{OUTPUT_IMG_DIR}'")
print("👉 Agora rode o treino normalmente com: model.train(data='campos.yaml', epochs=100)")
