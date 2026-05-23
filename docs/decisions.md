# Decisoes tecnicas pendentes

Este arquivo registra decisoes que ainda precisam ser confirmadas pelo grupo. Ele pode evoluir para um ADR simples, mantendo data, contexto, decisao e consequencias.

## 1. Onde armazenar o modelo treinado

### Contexto

O arquivo `best.pt` e necessario para a API funcionar, mas nao esta presente no repositorio. Como pesos de modelo costumam ser grandes, versionar esse arquivo no Git pode nao ser adequado.

### Opcoes

- Google Drive ou OneDrive com link documentado.
- GitHub Release com o artefato anexado.
- Storage externo, como S3 ou equivalente.
- Modelo pequeno de desenvolvimento versionado, se o tamanho permitir.

### Decisao sugerida

Nao versionar pesos grandes no Git. Documentar uma URL oficial para download e padronizar o caminho local via `.env`.

### Consequencias

- Novos integrantes conseguem subir a API sem treinar novamente.
- O repositorio permanece leve.
- E preciso manter o link atualizado e garantir permissao de acesso.

## 2. Como compartilhar o dataset

### Contexto

O treinamento depende do dataset local no formato esperado pelo YOLO. O dataset pode ser grande e conter muitas imagens.

### Opcoes

- Link em Drive/OneDrive.
- Dataset versionado com Git LFS.
- Script de download.
- Documentacao manual de origem e estrutura.

### Decisao sugerida

Usar armazenamento externo para o dataset e documentar no README ou em `docs/dataset.md`:

- link de acesso;
- estrutura esperada;
- como atualizar os dados;
- como rodar augmentation;
- como rodar treino.

## 3. Gerenciamento de dependencias

### Contexto

O projeto usa `requirements.txt`, mas projetos de IA costumam depender de combinacoes sensiveis de Python, PyTorch, CUDA e bibliotecas de visao computacional.

### Opcoes

- Continuar com `requirements.txt`, mas completar e fixar versoes.
- Separar dependencias por perfil: API, treino e desenvolvimento.
- Migrar para `pyproject.toml` com lockfile.

### Decisao sugerida

Curto prazo: completar `requirements.txt` e documentar a versao de Python.

Medio prazo: avaliar `pyproject.toml` com lockfile para maior reproducibilidade.

## 4. Configuracao por `.env`

### Contexto

Hoje caminhos e escolhas de dispositivo estao espalhados no codigo.

### Decisao sugerida

Criar `.env.example` com variaveis como:

```env
MEDTRACK_MODEL_PATH=models/best.pt
MEDTRACK_DATASET_PATH=dataset
MEDTRACK_YOLO_CONFIG=config/campos.yaml
MEDTRACK_DEVICE=cpu
MEDTRACK_OCR_GPU=false
```

### Consequencias

- Menos edicao de codigo para rodar localmente.
- Mais clareza para o projeto mobile e outros integrantes.
- Necessidade de validar erros quando uma variavel obrigatoria estiver ausente.
