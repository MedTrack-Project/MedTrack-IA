# ADR 0002 — Layout `src/` e fronteiras entre inferência e treinamento

- **Status:** aceito
- **Data:** 2026-07-22

## Contexto

API, OCR, utilitários e treinamento existem em diretórios soltos. A API depende
diretamente da estrutura de saída do treinamento.

## Decisão

Adotar `src/medtrack_ai` como pacote Python principal. O repositório continuará
único nesta etapa, pois API e treinamento compartilham domínio, equipe e ciclo
acadêmico. Na Fase 2, ele será organizado nas fronteiras `api`, `inference`,
`training` e `domain` dentro desse pacote.

## Consequências

- Testes importarão o pacote instalado, reduzindo falsos positivos causados pela
  raiz do repositório no `PYTHONPATH`.
- A API não poderá depender de `runs/` como caminho de produção.
- Dois repositórios independentes são uma alternativa futura caso treinamento e
  serving passem a ter equipes, permissões ou cadências de release distintas.
