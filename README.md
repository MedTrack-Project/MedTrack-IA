# MedTrack AI 🧠💊
### Motor de Visão Computacional e OCR

O **MedTrack AI** é o motor de inteligência artificial do ecossistema MedTrack. O sistema utiliza um modelo híbrido que combina **YOLOv8** (detecção e localização dos campos na embalagem) e **EasyOCR** (extração textual inteligente), servindo dados estruturados em JSON para o aplicativo mobile em Kotlin via **FastAPI**.

---

## 📦 Estrutura do Repositório

```
MedTrack-IA/
├── src/
│   ├── api/
│   │   ├── api.py              # Servidor FastAPI com suporte a medicamentos genéricos
│   │   ├── ocr_extration.py    # Módulo de processamento de crops e chamadas ao EasyOCR
│   │   ├── labeling.py         # Ferramenta de anotação manual do dataset via OpenCV
│   │   └── augmentation.py     # Pipeline de Data Augmentation
│   └── training/
│       └── train.py            # Script de fine-tuning do YOLOv8
├── config/
│   └── campos.yaml             # Configuração das 6 classes do dataset
├── data/                       # Imagens brutas (não versionadas no Git)
├── dataset/                    # Dataset gerado pelo labeling (não versionado no Git)
├── requirements.txt
└── README.md
```

---

## 🎯 Classes Detectadas

| ID | Classe | Descrição |
|----|--------|-----------|
| 0 | `nome` | Nome comercial do medicamento |
| 1 | `agente_ativo` | Princípio ativo |
| 2 | `dosagem` | Concentração/dosagem |
| 3 | `validade` | Data de validade |
| 4 | `quantidade` | Quantidade de unidades |
| 5 | `generico` | Tarja/logo de medicamento genérico |

---

## 🛠️ Como Rodar Localmente

### 1. Pré-requisitos

- **Python 3.10 ou superior**
- Drivers NVIDIA + **CUDA Toolkit** (opcional, recomendado para GTX 1650+)

### 2. Clonar e instalar dependências

```bash
git clone https://github.com/MClaraFerreira5/MedTrack-IA.git
cd MedTrack-IA
pip install -r requirements.txt
```

### 3. Baixar os pesos do modelo (`best.pt`)

Os pesos do modelo treinado **não são versionados no Git** por boas práticas. Para obtê-los:

1. Acesse a aba **Releases** deste repositório
2. Baixe o arquivo `best.pt` da última versão estável
3. Coloque o arquivo no caminho:

```
src/training/runs/detect/medtrack_yolo_train/weights/best.pt
```

### 4. Iniciar o servidor

```bash
python src/api/api.py
```

A API estará disponível em:
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Endpoint principal:** `POST http://localhost:8000/detect`

---

## 📱 Integração com o App Mobile (Kotlin)

O celular físico ou emulador não enxerga `localhost` diretamente. Use as configurações abaixo no seu cliente Retrofit:

| Ambiente | URL Base |
|----------|----------|
| Emulador Android nativo | `http://10.0.2.2:8000` |
| Celular físico (Wi-Fi) | URL gerada pelo [Ngrok](https://ngrok.com) |

**Para usar o Ngrok:**
```bash
ngrok http 8000
# Use a URL gerada: https://xxxx.ngrok-free.app/detect
```

---

## 🔁 Pipeline de IA

```
[Imagem do App Mobile]
        │
        ▼ (resize para 640px)
[Imagem Otimizada]
        │
        ▼
┌─────────────────────────┐
│   YOLOv8 Nano (GPU)     │ ──► Detecta campos + tarja genérico
└─────────────────────────┘
        │
        ├──► [Tarja genérico detectada] ──► nome = "Medicamento Genérico"
        │
        └──► [Crops dos outros campos]
                    │
                    ▼
        ┌───────────────────────┐
        │   EasyOCR (GPU/CPU)   │ ──► Extrai texto de cada campo
        └───────────────────────┘
                    │
                    ▼
             JSON estruturado
```

**Exemplo de resposta:**
```json
{
  "status": "success",
  "data": {
    "nome": "Astro",
    "agente_ativo": "Sinvastatina",
    "dosagem": "500mg",
    "validade": "10/2026",
    "quantidade": "30 comprimidos",
    "is_generico": false
  }
}
```

---

## ⚠️ Aviso de Uso Responsável

O **MedTrack AI** é um protótipo assistivo desenvolvido para fins **acadêmicos**. O processamento visual e a extração de dados de embalagens são baseados em previsões probabilísticas.

Este sistema **NÃO substitui**, em nenhuma hipótese:
- A conferência visual humana da receita médica e da embalagem física
- A orientação de profissionais de saúde qualificados (médicos, farmacêuticos, enfermeiros)

Qualquer utilização em cenários reais deve contar com **dupla checagem humana** para garantir a segurança na administração de medicamentos.

---

## 📄 Licença

Projeto acadêmico — Engenharia da Computação · 2026
