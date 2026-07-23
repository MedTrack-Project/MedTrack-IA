# ADR 0004 — Tags separadas para API e modelo

- **Status:** aceito
- **Data:** 2026-07-23

## Contexto

O repositório já contém a release de modelo `v1.0.0`. Tags de código também são
necessárias para publicar uma imagem de API no GHCR. Usar um único padrão faria
uma release de modelo disparar CI/CD de aplicação indevidamente.

## Decisão

Tags de modelo continuam no padrão `vMAJOR.MINOR.PATCH` e representam apenas um
artefato de ML. Tags de API usam `api-vMAJOR.MINOR.PATCH` e são as únicas que
disparam publicação de imagem de contêiner.

## Consequências

- Código, imagem e modelo têm ciclos de vida explícitos e independentes.
- O deploy deverá fixar digest de imagem e versão de modelo em vez de depender
  de uma tag genérica `latest`.
