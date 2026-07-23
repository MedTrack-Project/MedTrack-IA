# Contribuindo

Este é um repositório acadêmico privado do projeto MedTrack. Somente integrantes
autorizados da organização podem criar branches e pull requests.

## Fluxo de contribuição

1. Crie uma branch a partir de `main` para uma issue ou card específico.
2. Faça mudanças pequenas, testáveis e com escopo explícito.
3. Use Conventional Commits e referencie a issue no corpo do commit, por exemplo
   `Refs #123`.
4. Abra um pull request, descreva a motivação, os testes executados e impactos de
   configuração ou deploy.
5. Aguarde os checks obrigatórios e a aprovação de outro integrante antes do merge.

Não faça push direto em `main`, force push em branches protegidas, nem inclua
dados de treinamento, pesos de modelos, segredos ou arquivos `.env` no Git.

## Revisão

Os responsáveis técnicos atuais são:

| Integrante | Papel |
| --- | --- |
| [@YannLeao](https://github.com/YannLeao) | Maintainer e responsável final por releases e merge. |
| [@MClaraFerreira5](https://github.com/MClaraFerreira5) | Integrante e revisora. |
| [@EllenRocha1](https://github.com/EllenRocha1) | Integrante e revisora. |

Todo pull request requer pelo menos uma aprovação de um integrante diferente do
autor. Alterações em API, infraestrutura, segurança, modelo ou dados devem
explicar a compatibilidade e o plano de validação.

## Convenções

- Prefira `feat`, `fix`, `docs`, `test`, `build`, `ci` e `chore` como tipos de
  commit.
- Mantenha documentação operacional em `docs/` e decisões relevantes como ADRs
  em `docs/adr/`.
- Não altere o contrato HTTP sem atualizar `docs/contracts/api-v1.md` e alinhar
  a mudança com os consumidores do ecossistema MedTrack.
- Execute os checks indicados em [docs/TESTING.md](docs/TESTING.md) antes de
  solicitar revisão.

Consulte [docs/GOVERNANCE.md](docs/GOVERNANCE.md) para as regras de integração e
responsabilidades do projeto.
