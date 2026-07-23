# ADR 0003 — GitHub Releases como registry temporário de modelos

- **Status:** aceito
- **Data:** 2026-07-22

## Contexto

Pesos de modelo são binários grandes e não devem entrar no histórico Git. O
projeto acadêmico já possui GitHub Releases e precisa de uma solução simples,
auditável e com baixo custo inicial.

## Decisão

Usar GitHub Releases temporariamente para publicar cada peso promovido. Cada
release terá uma tag imutável, por exemplo `v1.0.0`, o arquivo `best.pt`,
um manifesto versionado no repositório e seu SHA-256. A API usa somente um
arquivo local já verificado; o download será responsabilidade de um script da
Fase 3.

## Consequências

- A versão exata do modelo pode ser recuperada e relacionada ao código.
- Releases são suficientes no contexto acadêmico, mas não oferecem governança,
  controle de acesso e lifecycle de um registry de ML dedicado.
- Não será utilizado o conceito de “latest” como entrada de produção.
