# ADR 0001 — Gerenciamento de dependências com uv

- **Status:** aceito
- **Data:** 2026-07-22

## Contexto

O projeto possuía apenas `requirements.txt`, com parte das versões sem fixação,
sem lockfile e sem separação entre runtime, treinamento e ferramentas de
desenvolvimento.

## Decisão

Usar `pyproject.toml` como fonte de verdade de metadados e dependências, e
**uv** para sincronizar o ambiente e gerar `uv.lock`. As dependências são
separadas nos grupos `inference`, `training` e `dev`. `requirements.txt` permanece
temporariamente para não interromper o Dockerfile legada; ele será removido ou
gerado automaticamente na fase de contêiner.

## Consequências

- Instalações e CI terão um conjunto resolvido de versões a partir de `uv.lock`.
- O time aprende uma ferramenta adicional, mas reduz comandos e tempo de
  instalação em relação à combinação de `venv` e `pip`.
- Poetry e pip-tools eram alternativas válidas. Não serão usadas em paralelo,
  pois múltiplas fontes de verdade causam divergência.
