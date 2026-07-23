# CI/CD

Os workflows em `.github/workflows/` separam validação, segurança, artefato de
modelo e publicação de imagem. Nenhum workflow faz deploy automático nesta
etapa: publicar uma imagem é diferente de promovê-la para um ambiente.

## Fluxos

| Workflow | Disparo | Responsabilidade |
| --- | --- | --- |
| `Quality` | Pull request e push em `main` | Lockfile, lint, tipos, testes e build do contêiner sem publicar. |
| `CodeQL` | Pull request, `main` e semanal | Análise estática de segurança Python. |
| `Model Artifact Smoke` | Manual | Baixa o peso definido no manifesto e verifica o checksum. |
| `Release API Image` | Tag `api-v*` | Valida o código e publica imagem imutável no GHCR. |

## Versionamento

Existem dois tipos de tag, deliberadamente distintos:

- `v1.0.0`: versão de **modelo** em GitHub Releases, indicada por manifesto.
- `api-v1.0.0`: versão de **aplicação/API**, que publica a imagem de contêiner.

Essa separação impede que treinar ou publicar um novo peso altere a API em
produção automaticamente.

## Publicar uma imagem

Após aprovar uma versão de código, crie e envie uma tag de API:

```powershell
git tag api-v1.0.0
git push origin api-v1.0.0
```

O workflow publica tags como `ghcr.io/medtrack-project/medtrack-ai:api-v1.0.0`
e também uma tag baseada no SHA do commit. Deploys futuros devem usar o digest
da imagem produzido pelo workflow, não uma tag mutável.

## Configuração no GitHub

Em **Settings → Actions → General**, permita workflows e mantenha a permissão
padrão do `GITHUB_TOKEN` como somente leitura. O workflow de release declara
explicitamente o mínimo adicional para publicar no GHCR (`packages: write`).
Para repositório privado, habilite CodeQL/Code Scanning conforme o plano GitHub
da organização.
