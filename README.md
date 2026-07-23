# MedTrack AI

Serviço de inferência de visão computacional do ecossistema acadêmico MedTrack.
Ele expõe uma API HTTP com FastAPI e organiza o ciclo de vida do modelo de
detecção e extração de texto, além das ferramentas de treinamento associadas.

O projeto é um protótipo acadêmico. Suas previsões não substituem a conferência
humana ou a orientação de profissionais de saúde.

## Componentes

| Área | Responsabilidade |
| --- | --- |
| `src/medtrack_ai/api` | Aplicação FastAPI, contrato HTTP, health checks e observabilidade. |
| `src/medtrack_ai/inference` | Carregamento e execução do modelo de inferência. |
| `src/medtrack_ai/model_registry` | Leitura e validação do manifesto do artefato de modelo. |
| `src/training` | Ferramentas de treinamento e aumento de dados. |
| `config/training` | Configuração versionada do dataset e das classes de treinamento. |
| `tests` | Testes unitários, de integração e smoke tests opcionais do modelo. |

Dados de treinamento, pesos e resultados de execução não são versionados. O
artefato de inferência é recuperado de um GitHub Release e validado por checksum.

## Início rápido

O caminho recomendado para desenvolvimento da API é Docker Compose. São
necessários Docker Desktop, Python 3.11 e `uv` para recuperar o modelo local.

```powershell
Copy-Item .env.example .env
uv run --group dev python scripts/fetch_model.py
docker compose up --build
```

Após a inicialização:

```powershell
Invoke-WebRequest http://localhost:8000/healthz
Invoke-WebRequest http://localhost:8000/readyz
```

Para encerrar o ambiente:

```powershell
docker compose down
```

Consulte o [guia de contêiner](docs/CONTAINER.md) para os pré-requisitos,
execução sem Compose e detalhes do modelo local.

## Desenvolvimento e qualidade

```powershell
uv sync --group dev
uv run --group dev pytest
uv run --group dev ruff check src tests scripts
uv run --group dev pyright src/medtrack_ai tests scripts
```

A estratégia de testes e os comandos opcionais estão em
[docs/TESTING.md](docs/TESTING.md). Pull requests são validados pelos workflows
descritos em [docs/CI_CD.md](docs/CI_CD.md).

## Documentação

| Tema | Documento |
| --- | --- |
| Contrato HTTP | [docs/contracts/api-v1.md](docs/contracts/api-v1.md) |
| Artefato e versão do modelo | [docs/models/README.md](docs/models/README.md) |
| Contêiner local | [docs/CONTAINER.md](docs/CONTAINER.md) |
| CI/CD e versionamento | [docs/CI_CD.md](docs/CI_CD.md) |
| Deploy de staging | [docs/RAILWAY.md](docs/RAILWAY.md) |
| Decisões arquiteturais | [docs/adr/README.md](docs/adr/README.md) |
| Governança | [docs/GOVERNANCE.md](docs/GOVERNANCE.md) |

## Contribuição e segurança

O repositório é restrito aos integrantes do projeto MedTrack. As regras de
contribuição, revisão e responsáveis estão em [CONTRIBUTING.md](CONTRIBUTING.md).
Relatos de vulnerabilidade devem seguir [SECURITY.md](SECURITY.md), e não ser
publicados em issues.

## Licença

O código está licenciado sob a [MIT License](LICENSE).
