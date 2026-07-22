# MedTrack IA — plano de modernização

Este repositório é o componente de inteligência artificial do ecossistema
MedTrack. Ele reúne dois produtos relacionados, mas com ciclos de vida
distintos:

- **serviço de inferência:** API HTTP que o aplicativo Android consome;
- **pipeline de treinamento:** código, configurações e dados necessários para
  produzir uma versão do modelo.

O objetivo deste plano é transformar o projeto em uma base reproduzível,
testável, implantável e segura para evoluir ao longo dos próximos semestres.
Ele não propõe alterar regras de negócio, rotas ou a qualidade do modelo nesta
etapa.

> Estado atual: a API depende de um caminho interno de `runs/.../best.pt`, que
> é uma saída de treinamento e não um artefato de produção. O contêiner não
> possui uma estratégia explícita para receber esse peso. Isso torna a execução
> e o deploy não reprodutíveis. O primeiro trabalho é desacoplar esses pontos.

## Decisões arquiteturais a validar

Estas são as direções recomendadas para a discussão inicial. Elas devem ser
registradas em ADRs (Architecture Decision Records) curtos antes da execução.

| Tema | Direção recomendada | Por quê |
| --- | --- | --- |
| Organização | Um repositório, dois módulos: `app` (inferência) e `training` (treinamento), ambos sob `src/` | Código importável, testes confiáveis e responsabilidades explícitas sem criar complexidade de vários repositórios. |
| Dependências | `pyproject.toml` (PEP 621) + lockfile, preferencialmente com **uv** | Substitui requisitos soltos por versões reprodutíveis e grupos separados para API, treino e desenvolvimento. `requirements.txt` pode ser exportado somente para compatibilidade de deploy. |
| Modelo | Pesos fora do Git; armazenamento de artefatos versionados | Git não é um registry de binários grandes. Cada modelo precisa de versão imutável, checksum, métricas e compatibilidade registrada. |
| Dataset | Dataset fora do Git, com manifesto e versionamento próprio | Preserva tamanho e privacidade do repositório, mantendo rastreabilidade da origem e da divisão treino/validação. |
| Configuração | Variáveis de ambiente tipadas + arquivos de exemplo sem segredos | Elimina caminhos e opções de hardware codificados no código. |
| Deploy | Contêiner OCI em serviço de contêineres | Vercel é inadequada para esta API: execução serverless, limites de tamanho/tempo e inicialização de PyTorch/YOLO/OCR prejudicam a inferência. Avaliar Cloud Run, Render, Railway ou Fly.io conforme custo e região. |

### Posição sobre `src/`

Sim. O layout `src/` é uma boa prática em Python: impede que os testes importem
acidentalmente arquivos da raiz e deixa explícito o que será distribuído. A
organização alvo é aproximadamente:

```text
src/medtrack_ai/
  api/                 # FastAPI: rotas, schemas e ciclo de vida
  inference/           # carregamento do modelo e orquestração YOLO/OCR
  training/            # execução de treino, avaliação e exportação
  domain/              # tipos e contratos independentes de framework
  settings.py          # configuração validada por ambiente
tests/
  unit/
  integration/
  contract/
scripts/               # download/verificação de modelo e tarefas locais
configs/               # configurações versionadas, sem dados/segredos
docs/adr/
```

Não se deve usar `runs/` como dependência da API. Essa pasta é efêmera e deve
ser gerada localmente ou na execução de treinamento.

## Plano de ação

### Fase 0 — diagnóstico e decisões

1. Inventariar os contratos atuais: endpoint, payload, resposta, códigos de
   erro, limite de upload e requisitos do aplicativo Android.
2. Definir ambientes `local`, `test`, `staging` e `production`, com responsáveis
   e variáveis necessárias em cada um.
3. Registrar ADRs para gerenciador de dependências, registry de modelos,
   plataforma de deploy, estratégia CPU/GPU e política de versão.
4. Definir critérios mensuráveis: tempo máximo de resposta, tamanho máximo de
   imagem, disponibilidade desejada e orçamento mensal.

**Aceite:** decisões documentadas e o contrato atual congelado em uma especificação
OpenAPI versionada.

### Fase 1 — fundação do projeto Python

1. Criar `pyproject.toml`, lockfile e grupos de dependência (`api`, `training`,
   `dev`). Fixar também as dependências transitivas pelo lockfile.
2. Migrar os imports para o pacote `medtrack_ai`; eliminar `sys.path.append`.
3. Adotar Ruff (lint e formatação), Pyright ou mypy (tipagem) e pre-commit.
4. Incluir `.python-version`, `.env.example`, `Makefile` ou `justfile` com
   comandos padronizados e instruções de bootstrap.
5. Corrigir `.gitignore` para não ignorar indiscriminadamente `*.txt`, pois
   isso pode esconder anotações, manifests ou documentação legítimos.

**Aceite:** uma instalação limpa cria o mesmo ambiente e `lint`, `format-check`
e testes rodam com um único conjunto de comandos documentados.

### Fase 2 — separação entre API e inferência

1. Mover a rota FastAPI para uma camada fina; ela só valida HTTP e chama um
   serviço de inferência por interface.
2. Encapsular YOLO e EasyOCR em adaptadores carregados no ciclo de vida da
   aplicação, não na importação do módulo.
3. Centralizar configurações: caminho/URI do modelo, limiar, tamanho de imagem,
   CPU/GPU, CORS, logs e limites devem vir de settings tipados.
4. Criar schemas Pydantic de entrada, saída e erro; gerar a OpenAPI como contrato
   para o mobile.
5. Adicionar `/healthz` (processo vivo) e `/readyz` (modelo carregado e apto a
   atender), sem expor informações sensíveis.

**Aceite:** a API inicia sem caminhos de treino codificados; os componentes de
inferência podem ser substituídos por doubles nos testes.

### Fase 3 — gestão de modelo e dados

1. Definir um formato de manifesto, por exemplo `model-manifest.json`, contendo
   versão, URI, SHA-256, data de treino, commit do código, versão do dataset,
   métricas e contrato de classes.
2. Publicar pesos imutáveis em um registry/armazenamento de artefatos. Para o
   estágio acadêmico, **GitHub Releases** é aceitável; para evolução, considerar
   bucket S3/R2/GCS ou DVC. Releases não substituem o manifesto.
3. Criar `scripts/fetch_model` que baixa uma **versão explícita**, verifica o
   SHA-256 e grava em diretório ignorado pelo Git. Nunca baixar “o mais recente”
   sem versão: isso destrói a reprodutibilidade.
4. Manter o modelo fora do repositório e fora da imagem-base. No deploy, usar
   imagem publicada com o peso versionado ou volume/object storage no startup;
   escolher comparando tamanho da imagem, cold start e segurança.
5. Tratar dataset e artefatos de experimento como recursos separados. Versionar
   apenas configuração, manifesto e metadados; documentar licença, origem,
   acesso e dados sensíveis.

**Aceite:** dado um manifesto, qualquer pessoa autorizada consegue recuperar
exatamente o peso e reproduzir uma inferência, sem arquivos manuais em `runs/`.

### Fase 4 — estratégia de testes

1. **Unitários:** validação HTTP, regras de composição da resposta, sanitização
   de texto e seleção/configuração de dispositivo — sem carregar IA real.
2. **Integração:** API com adaptadores falsos e casos de imagem inválida,
   payload grande, falha de modelo e resposta padronizada.
3. **Contrato:** validar OpenAPI e exemplos contra o cliente mobile; mudanças
   incompatíveis exigem nova versão da API.
4. **Smoke opcional de modelo:** em pipeline separado/manual, baixar um peso
   fixado e executar um pequeno conjunto de imagens permitido. Não fazer a CI
   comum depender de GPU, download pesado ou credenciais de produção.
5. Versionar fixtures pequenas e não sensíveis; não gerar arquivos durante os
   testes dentro de diretórios versionados.

**Aceite:** testes rápidos, determinísticos e executados em CI; o teste que
verifica o modelo real fica identificado e não mascara falhas como `skip`.

### Fase 5 — contêiner e execução local

1. Refazer o Dockerfile como multi-stage, com usuário não-root, `.dockerignore`,
   versões fixadas e imagem mínima.
2. Criar variantes explícitas: CPU como padrão de produção e GPU somente se a
   plataforma realmente oferecer GPU. Não detectar CUDA para decidir o contrato
   da aplicação.
3. Executar `uvicorn` com configuração por ambiente; incluir healthcheck e não
   incluir segredos no build.
4. Adicionar Docker Compose para desenvolvimento e teste de imagem, incluindo a
   forma documentada de fornecer o artefato do modelo.
5. Produzir SBOM e fazer varredura de vulnerabilidades da imagem.

**Aceite:** `docker build` e execução local funcionam a partir de clone limpo e
um manifesto de modelo; a imagem não contém dados de treino nem segredos.

### Fase 6 — CI/CD no GitHub Actions

1. Pull requests: checkout, instalação pelo lockfile, lint, tipos, testes
   unitários/integração, validação de OpenAPI e build do contêiner.
2. Segurança: Dependabot/Renovate, secret scanning, CodeQL/Bandit e scanner de
   imagem. Corrigir ou aceitar riscos conscientemente com registro.
3. Tags semânticas (`vMAJOR.MINOR.PATCH`) publicam imagem OCI imutável e release
   com changelog; usar digest da imagem no deploy.
4. O pipeline de treinamento deve ser separado do deploy da API. Ele publica
   apenas um novo artefato + manifesto após aprovação de métricas, nunca
   substitui silenciosamente o modelo em produção.
5. Configurar ambientes protegidos, secrets mínimos e aprovação para produção.

**Aceite:** nenhum merge ocorre sem verificações; uma tag gera artefatos
identificáveis e passíveis de rollback.

### Fase 7 — deploy e operação

1. Escolher a plataforma com um pequeno teste de viabilidade: build, cold start,
   memória, região, HTTPS, logs, custo e suporte a armazenamento de modelo.
2. Criar `staging` primeiro; integrar o Android a essa URL por configuração de
   build, nunca por URL fixa no código.
3. Configurar domínio/HTTPS, CORS restrito aos clientes necessários, limite de
   corpo, rate limit e autenticação conforme o contrato do ecossistema.
4. Registrar logs estruturados com ID de requisição e métricas de latência, erro,
   disponibilidade e versão do modelo; não registrar imagem enviada nem texto
   sensível sem política de retenção.
5. Documentar rollback: voltar o deployment ao digest de imagem anterior e/ou
   apontar para o manifesto anterior.

**Aceite:** URL HTTPS de staging atende `healthz`, `readyz` e o smoke test;
deploy e rollback estão descritos e foram testados.

### Fase 8 — governança e manutenção

1. Adicionar `CONTRIBUTING.md`, convenção de commits, template de PR, política
   de revisão e `CODEOWNERS` quando aplicável.
2. Incluir licença, aviso de uso assistivo, política de privacidade e processo
   para incidentes/vulnerabilidades (`SECURITY.md`).
3. Manter changelog, documentação de arquitetura e ADRs atualizados.
4. Revisar mensalmente dependências, custos, logs e tempo de resposta; revisar
   o modelo somente por processo controlado de avaliação e promoção.

**Aceite:** um novo integrante consegue configurar, testar e publicar em staging
seguindo documentação sem conhecimento implícito do computador de quem treinou.

## Ordem sugerida de execução

1. Fase 0, Fase 1 e inventário do contrato.
2. Fase 2 e testes com adaptadores falsos.
3. Fase 3 para tornar o modelo recuperável e rastreável.
4. Fases 5 e 6 para garantir entrega repetível.
5. Fase 7 para staging e integração Android.
6. Fase 8 continuamente.

## Primeira entrega prática

A próxima implementação deve se limitar a criar a fundação: `pyproject.toml`,
pacote `src/medtrack_ai`, configuração por ambiente, comandos de desenvolvimento
e pipeline de qualidade para pull requests. Antes de escolher plataforma ou
reescrever o Docker, decidiremos o local de armazenamento do modelo, a meta de
memória/latência e se a produção inicial será CPU.

## Princípios que guiam o projeto

- Cada deploy referencia uma versão exata do código, imagem e modelo.
- Treinar um modelo não publica automaticamente uma nova API.
- O ambiente de desenvolvimento não é fonte de verdade para artefatos.
- A API é compatível por contrato; o aplicativo não depende de detalhes do
  framework de IA.
- Segurança, observabilidade e rollback fazem parte da definição de pronto.
