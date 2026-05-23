# MedTrack-IA

Modulo de inteligencia artificial do projeto MedTrack, usado para detectar campos em imagens de medicamentos e extrair informacoes por OCR para consumo pelo aplicativo mobile.

## Visao geral

O projeto combina:

- uma API FastAPI para inferencia;
- um modelo YOLOv8 para deteccao de campos na embalagem;
- EasyOCR para leitura dos textos detectados;
- scripts auxiliares para rotulagem, augmentation e treinamento.

## Estrutura do projeto

```text
MedTrack-IA/
|-- config/
|   `-- campos.yaml
|-- dataset/
|-- docs/
|-- src/
|   |-- api/
|   |-- training/
|   `-- utils/
|-- requirements.txt
`-- README.md
```

## Requisitos

- Python 3.10+ recomendado.
- Ambiente virtual Python.
- Dependencias listadas em `requirements.txt`.
- Modelo treinado `best.pt` disponivel localmente para executar a API.

> Observacao: o modelo treinado ainda nao esta versionado no repositorio. Consulte `docs/melhorias.md` e `docs/decisions.md` para as sugestoes de como disponibilizar esse artefato para os demais integrantes.

## Instalacao local

Crie e ative um ambiente virtual:

```bash
python -m venv .venv
```

No Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instale as dependencias:

```bash
pip install -r requirements.txt
```

## Execucao da API

O ponto de entrada atual da API esta em:

```text
src/api/api.py
```

Para executar:

```bash
python src/api/api.py
```

A rota principal e:

```text
POST /detect
```

Ela espera uma imagem enviada por upload e retorna os campos detectados em JSON.

## Treinamento

O treinamento atual esta em:

```text
src/training/train.py
```

Ele usa o arquivo:

```text
config/campos.yaml
```

Esse YAML define o caminho do dataset e a ordem das classes usadas pelo YOLO. A estrutura esperada do dataset segue o formato YOLO, com imagens e labels separados em treino e validacao.

## Documentacao

Arquivos importantes em `docs/`:

- `docs/architecture.md`: estrutura e fluxo atual do projeto.
- `docs/melhorias.md`: feedbacks e melhorias sugeridas.
- `docs/decisions.md`: decisoes tecnicas pendentes.

## Observacoes para contribuidores

- Nao versionar ambientes virtuais, arquivos de IDE, datasets grandes ou pesos de modelo.
- Antes de alterar classes do modelo, manter alinhados `config/campos.yaml`, scripts de rotulagem e logica da API.
- Melhorias estruturais devem ser feitas em pequenos passos para preservar o funcionamento atual.
