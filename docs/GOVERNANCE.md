# Governança do repositório

## Escopo e acesso

O MedTrack AI é um projeto acadêmico mantido pela organização MedTrack Project.
O repositório é fechado a contribuições externas; mudanças são realizadas pelos
integrantes autorizados e integradas por pull request.

| Responsável | Atribuição |
| --- | --- |
| [@YannLeao](https://github.com/YannLeao) | Maintainer, aprovação final, releases e operação. |
| [@MClaraFerreira5](https://github.com/MClaraFerreira5) | Desenvolvimento e revisão. |
| [@EllenRocha1](https://github.com/EllenRocha1) | Desenvolvimento e revisão. |

## Integração em `main`

A branch `main` é protegida por rulesets. O fluxo obrigatório é branch de
trabalho, pull request, checks automatizados e revisão por outra pessoa.

Configuração esperada no GitHub:

- bloquear exclusão e force push;
- exigir pull request e resolução de conversas;
- exigir branches atualizadas e status checks aprovados;
- exigir ao menos uma aprovação;
- exigir revisão de CODEOWNERS, quando os três integrantes tiverem acesso de
  escrita confirmado.

`CODEOWNERS` define os três integrantes como responsáveis pelo repositório. O
arquivo apenas aponta responsáveis; a exigência efetiva de aprovação depende dos
dois últimos controles no ruleset do GitHub.

## Decisões e mudanças

Mudanças que afetem contratos, modelo, segurança, dados ou operação devem ter
issue/card associado, validação explícita e, quando envolverem uma decisão
duradoura, uma ADR em `docs/adr/`.

Os commits seguem Conventional Commits e mencionam a issue relacionada no corpo,
por exemplo `Refs #123`. As instruções práticas estão em
[CONTRIBUTING.md](../CONTRIBUTING.md).

## Segurança e dados

Vulnerabilidades seguem [SECURITY.md](../SECURITY.md). Dados de treinamento,
pesos de modelos, segredos e arquivos de ambiente não pertencem ao Git; suas
regras de armazenamento e recuperação são documentadas nos guias de modelo e
de operação.
