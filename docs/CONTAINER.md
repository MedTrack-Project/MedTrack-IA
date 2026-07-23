# Execução em contêiner

O contêiner executa a API em CPU por padrão. O peso do modelo não entra na
imagem: ele é montado em modo somente leitura, preservando a separação entre
código de serving e artefato de ML.

## Pré-requisito

Recupere e verifique o modelo uma vez na máquina hospedeira:

```powershell
uv run --group dev python scripts/fetch_model.py
```

Isso cria `models/medtrack-yolo/v1.0.0/best.pt`, que é ignorado pelo Git.

## Desenvolvimento local

```powershell
docker compose up --build
```

A API fica em `http://localhost:8000`. O healthcheck do Docker consulta
`/healthz`; a prontidão do modelo deve ser conferida em `GET /readyz`.

Para encerrar:

```powershell
docker compose down
```

## Build e execução sem Compose

```powershell
docker build --tag medtrack-ai:local .
docker run --rm --publish 8000:8000 --volume "${PWD}/models:/app/models:ro" medtrack-ai:local
```

No PowerShell, se a expansão de `${PWD}` não for aceita pelo Docker instalado,
use `$PWD.Path` para fornecer o caminho absoluto.

## Decisões importantes

- A imagem instala dependências a partir de `uv.lock`, com `--frozen`; um build
  falha se o lockfile não corresponder ao `pyproject.toml`.
- O processo é executado pelo usuário sem privilégios `app`.
- Modelo ausente não derruba o processo: `/readyz` retorna `503`, permitindo que
  a plataforma identifique indisponibilidade sem confundir com falha de processo.
- O Compose é CPU. Uma variante GPU só será criada após a escolha da plataforma
  de deploy e do runtime NVIDIA.
