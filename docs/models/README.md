# Artefatos de modelo

Os pesos não pertencem ao Git nem ao diretório `runs/` de treinamento. Cada
modelo promovido possui um manifesto JSON em `config/models/`, que fixa versão,
URL da release, checksum, classes e metadados de treinamento.

## Recuperar o modelo atual

Após instalar as dependências de runtime e inferência, execute na raiz do
repositório:

```powershell
uv run --group inference python scripts/fetch_model.py
```

O script baixa exatamente `v1.0.0/best.pt`, confere o SHA-256 e só então move o
arquivo para `models/medtrack-yolo/v1.0.0/best.pt`. Esse destino é ignorado pelo
Git. Uma execução repetida não baixa novamente se o checksum já for válido.

Para uma versão futura, crie outro manifesto; não altere a URL ou o checksum de
um artefato já publicado. O ambiente deve apontar para a nova versão com
`MEDTRACK_MODEL_URI` e `MEDTRACK_MODEL_VERSION`.

## Publicar uma versão futura

1. Treine e avalie o modelo fora do diretório de produção.
2. Publique uma GitHub Release com tag nova e imutável, anexando o peso.
3. Calcule e registre o SHA-256 do arquivo publicado.
4. Crie um novo manifesto com métricas, commit de código e versão do dataset.
5. Baixe o modelo com o novo manifesto e execute smoke test antes de promovê-lo.

Os campos `not-recorded` no primeiro manifesto descrevem uma limitação histórica
do peso atual; novos modelos não devem ser promovidos sem essas informações.
