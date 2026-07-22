# Contrato da API — MedTrack IA v1

**Status:** baseline do comportamento existente em 2026-07-22.

Este documento é a fonte de comunicação entre a API de IA e seus clientes. Ele
não cria uma versão nova; registra o contrato que qualquer refatoração das
Fases 1 e 2 deve preservar. A especificação OpenAPI gerada pelo FastAPI em
`/openapi.json` é a referência executável quando a aplicação está em execução.

## Operação `POST /detect`

Extrai informações de uma embalagem de medicamento a partir de uma imagem.

### Requisição

- **Content-Type:** `multipart/form-data`
- **Campo obrigatório:** `file`
- **Valor:** arquivo de imagem (`image/*`)

Exemplo com cURL:

```bash
curl --request POST http://localhost:8000/detect \
  --form "file=@medicamento.jpg;type=image/jpeg"
```

### Resposta de sucesso — `200 OK`

```json
{
  "status": "success",
  "is_generico": false,
  "data": {
    "nome": "Astro",
    "agente_ativo": "Sinvastatina",
    "dosagem": "500mg",
    "validade": "10/2026",
    "quantidade": "30 comprimidos"
  },
  "count": 5
}
```

| Campo | Tipo | Regra |
| --- | --- | --- |
| `status` | string | Atualmente sempre `success` nas respostas bem-sucedidas. |
| `is_generico` | boolean | Indica se a classe `generico` foi detectada. |
| `data` | objeto | Pode conter `nome`, `agente_ativo`, `dosagem`, `validade` e `quantidade`; campos não detectados podem estar ausentes. |
| `count` | inteiro | Quantidade de campos presentes em `data`. |

Quando `is_generico` é `true`, a regra atual força `data.nome` para
`"Medicamento Genérico"`; esse campo é incluído mesmo que não tenha sido
detectado pelo OCR.

### Erros conhecidos

| Situação | Código esperado | Corpo |
| --- | --- | --- |
| Tipo de arquivo não é imagem | `400 Bad Request` | Objeto com `detail`. |
| Campo `file` ausente ou multipart inválido | `422 Unprocessable Entity` | Erro de validação do FastAPI. |
| Imagem não pode ser decodificada | Atualmente retorna um objeto de erro no corpo; a padronização de código HTTP será feita na Fase 2. |

## Compatibilidade

Uma mudança de rota, campo obrigatório, tipo de campo ou significado de
`is_generico` é uma mudança incompatível. Ela deve ser discutida com o cliente
Android, registrada em ADR e publicada como uma nova versão da API, com período
de convivência quando necessário.

## Próxima evolução técnica

Na Fase 2, o contrato será representado por schemas Pydantic e terá testes de
contrato. A rota continuará com esta forma enquanto não houver decisão explícita
de versão.
