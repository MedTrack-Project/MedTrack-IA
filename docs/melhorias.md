# Melhorias e feedbacks iniciais

Este documento registra problemas observados no estado atual do modulo MedTrack-IA e sugere melhorias para uma proxima etapa de cleanup, refatoracao e documentacao.

## Objetivo dos feedbacks

O objetivo nao e reescrever o projeto imediatamente, mas organizar os pontos que dificultam:

- reproducao do treinamento por outros integrantes;
- execucao local da API;
- uso da rota pelo projeto mobile;
- manutencao do codigo;
- entendimento das decisoes de arquitetura.

## 1. Caminhos fixos misturados com codigo

### Situacao atual

Varios scripts possuem caminhos definidos diretamente no codigo:

- `src/api/api.py` monta um caminho especifico para `best.pt`;
- `src/api/main.py` usa caminhos locais para modelo e imagem de teste;
- `src/training/augmentation.py` define diretorios de entrada e saida no topo do arquivo;
- `src/utils/labeling.py` define diretorios de imagens originais e destino dentro do proprio script.

### Impacto

Isso torna o projeto dependente da maquina de quem desenvolveu ou da posicao exata em que o comando foi executado. Outros integrantes podem nao conseguir treinar, rotular ou subir a API sem editar codigo-fonte.

### Sugestao

Mover caminhos para configuracao:

- variaveis de ambiente em `.env`;
- arquivo YAML/TOML de configuracao;
- argumentos de linha de comando para scripts;
- constantes centralizadas em um modulo de configuracao.

Exemplo de variaveis possiveis:

```env
MEDTRACK_MODEL_PATH=models/best.pt
MEDTRACK_DATASET_PATH=dataset
MEDTRACK_YOLO_CONFIG=config/campos.yaml
MEDTRACK_OCR_GPU=false
```

## 2. Modelo treinado nao disponivel para os demais integrantes

### Situacao atual

A API depende de um arquivo `best.pt`, mas esse artefato nao esta presente no projeto. Como modelos sao arquivos grandes, faz sentido que nao sejam versionados diretamente no Git, mas a ausencia de uma estrategia documentada impede outros integrantes de executarem a rota.

### Impacto

Mesmo que a API esteja correta, ela nao sobe sem o modelo. Isso bloqueia integracao com o mobile e testes locais.

### Sugestao

Escolher e documentar uma estrategia:

- armazenar o modelo em Drive/OneDrive/S3/GitHub Release;
- informar a URL em `.env`;
- criar um script `download_model` para baixar o artefato;
- documentar manualmente onde baixar e onde colocar o arquivo;
- manter um modelo pequeno de exemplo apenas para desenvolvimento, se o tamanho permitir.

Decisao sugerida para discutir: nao versionar `best.pt` no Git, mas manter uma URL de download documentada e validada.

## 3. Treinamento dificil de reproduzir

### Situacao atual

O treinamento depende de:

- dataset local;
- estrutura exata esperada por `config/campos.yaml`;
- modelo base `yolov8n.pt`;
- parametros fixos no script;
- GPU opcional, mas com uso de `device=0` no treino.

### Impacto

Integrantes que nao possuem o dataset ou uma GPU configurada podem nao conseguir reproduzir o treino. Alem disso, os hiperparametros ficam escondidos no codigo, dificultando comparacao entre experimentos.

### Sugestao

Documentar:

- origem do dataset;
- estrutura esperada de pastas;
- como obter os dados;
- como rodar augmentation;
- como rodar treino;
- onde o melhor modelo sera salvo;
- quais parametros foram usados para gerar o modelo atual.

Em uma refatoracao futura, considerar argumentos de linha de comando:

```bash
python -m src.training.train --data config/campos.yaml --epochs 100 --device cpu
```

## 4. `requirements.txt` pode nao ser a melhor escolha isolada

### Situacao atual

O projeto usa `requirements.txt`, mas ha dependencias importadas diretamente que nao aparecem de forma explicita, como `torch`.

### Impacto

Ambientes podem quebrar durante execucao, principalmente em dependencias pesadas de IA, CUDA, PyTorch, EasyOCR e Ultralytics.

### Sugestao

Para um projeto de IA, avaliar uma das alternativas:

- manter `requirements.txt`, mas completo e separado por perfil;
- usar `pyproject.toml` com um gerenciador moderno;
- criar arquivos separados, como `requirements-api.txt`, `requirements-training.txt` e `requirements-dev.txt`;
- documentar versoes de Python, CUDA e PyTorch esperadas.

Uma abordagem simples para o curto prazo:

```text
requirements.txt
requirements-dev.txt
```

Uma abordagem mais organizada para evolucao:

```text
pyproject.toml
uv.lock ou poetry.lock
```

## 5. Dependencias faltantes ou ambiguas

### Situacao atual

O codigo importa `torch`, mas `torch` nao esta listado explicitamente em `requirements.txt`. Algumas dependencias tambem estao sem versao fixada, como `opencv-python-headless` e `python-dotenv`.

### Impacto

Instalacoes em maquinas diferentes podem resolver versoes diferentes e gerar erros dificeis de rastrear.

### Sugestao

Revisar dependencias reais:

- `torch`;
- `torchvision`, se necessario;
- `ultralytics`;
- `easyocr`;
- `opencv-python-headless`;
- `numpy`;
- `fastapi`;
- `uvicorn`;
- `python-multipart`;
- `python-dotenv`;
- `pydantic`.

Tambem vale validar se a API precisa de todas as dependencias de treinamento ou se pode ter um conjunto menor.

## 6. README ainda nao explica como executar

### Situacao atual

O `README.md` contem apenas o titulo do projeto.

### Impacto

Novos integrantes nao sabem:

- qual versao de Python usar;
- como criar ambiente virtual;
- como instalar dependencias;
- como obter o modelo treinado;
- como subir a API;
- como chamar a rota `/detect`;
- como treinar novamente;
- como organizar o dataset.

### Sugestao

Adicionar secoes minimas:

- Visao geral;
- Requisitos;
- Instalacao;
- Configuracao do `.env`;
- Como executar a API;
- Como testar a rota;
- Como treinar o modelo;
- Estrutura do dataset;
- Documentacao complementar em `docs/`.

## 7. `.gitignore` e arquivos de ambiente

### Situacao atual

O `.gitignore` ja possui entradas importantes, incluindo `.idea/`, `.vscode/`, `.env`, `venv/`, imagens, modelos e pastas de treino. Mesmo assim, ha arquivos de `.idea/` aparecendo como modificados no estado atual do Git, o que indica que eles provavelmente ja foram versionados antes ou estao sendo rastreados.

### Impacto

Arquivos de IDE e ambiente local podem gerar ruido em commits e conflitos entre integrantes.

### Sugestao

Em etapa futura:

- conferir quais arquivos estao rastreados pelo Git;
- remover do versionamento arquivos de IDE, sem apagar os arquivos locais;
- adicionar tambem `.venv/`, caso ainda nao esteja coberto pelo padrao atual;
- revisar regras muito amplas, como `*.txt`, pois labels YOLO sao `.txt` e pode haver arquivos texto que deveriam ser versionados.

## 8. Papel de `config/campos.yaml` pouco claro

### Situacao atual

`config/campos.yaml` define o dataset e as classes para o YOLO, mas isso nao esta explicado na documentacao principal.

### Impacto

Alterar a ordem ou os nomes das classes pode quebrar a interpretacao do modelo e da API. Por exemplo, a API depende de labels como `generico` e `nome`.

### Sugestao

Documentar que `config/campos.yaml`:

- e usado pelo treinamento YOLO;
- define onde estao as imagens e labels;
- define a ordem numerica das classes;
- precisa estar alinhado com `src/utils/labeling.py`;
- precisa estar alinhado com a logica da API.

## 9. Separacao entre scripts e biblioteca

### Situacao atual

Alguns arquivos executam trabalho diretamente ao serem chamados, com pouca separacao entre configuracao, funcoes reutilizaveis e ponto de entrada.

### Impacto

Fica mais dificil testar funcoes isoladas, reaproveitar codigo e evoluir o projeto sem quebrar scripts existentes.

### Sugestao

Organizar gradualmente:

```text
src/medtrack_ai/
|-- api/
|-- inference/
|-- ocr/
|-- training/
|-- data/
`-- config.py
scripts/
|-- train.py
|-- augment.py
`-- label.py
```

Essa mudanca deve ser feita aos poucos para evitar quebrar o fluxo atual.

## 10. Configuracao de GPU/CPU

### Situacao atual

A API escolhe CPU ou GPU, mas o OCR usa `gpu=True` fixo. O treino calcula uma variavel `device`, mas passa `device=0`.

### Impacto

Maquinas sem GPU ou com configuracao diferente podem falhar.

### Sugestao

Centralizar a decisao de dispositivo e permitir configuracao por ambiente:

```env
MEDTRACK_DEVICE=cpu
MEDTRACK_OCR_GPU=false
```

## Priorizacao sugerida

1. Documentar execucao local da API no README.
2. Definir como baixar ou disponibilizar o `best.pt`.
3. Documentar dataset e treinamento.
4. Revisar `.gitignore` e remover arquivos locais rastreados.
5. Completar dependencias.
6. Extrair caminhos fixos para `.env` ou configuracao.
7. Separar scripts executaveis de codigo reutilizavel.

## Resultado esperado apos as melhorias

Ao final do cleanup, qualquer integrante deveria conseguir:

- clonar o repositorio;
- criar o ambiente;
- baixar ou posicionar o modelo treinado;
- subir a API;
- enviar uma imagem para `/detect`;
- entender onde esta o dataset;
- reproduzir o treinamento quando tiver acesso aos dados;
- saber quais decisoes foram tomadas e por que.
