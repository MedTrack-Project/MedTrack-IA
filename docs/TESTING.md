# Estratégia de testes

O projeto separa testes por custo e dependências. A CI de pull request executa
somente os níveis rápidos; testes que requerem artefato real são opt-in.

| Nível | Localização | Dependências | Quando executar |
| --- | --- | --- | --- |
| Unitário | `tests/unit/` | Nenhuma rede, peso ou GPU | Todo commit e pull request |
| Integração | `tests/test_api.py` | FastAPI e adaptador falso | Todo commit e pull request |
| Manifesto | `tests/test_model_manifest.py` | Arquivos pequenos | Todo commit e pull request |
| Smoke de artefato | `tests/model/` | Peso local já verificado | Antes de deploy ou promoção |
| Inferência real | futuro fixture de imagens aprovada | Peso + grupo `inference` | Pipeline manual dedicado |

## Comandos

```powershell
# Testes rápidos, integração e relatório de cobertura.
uv run --group dev pytest

# Apenas uma categoria.
uv run --group dev pytest -m unit
uv run --group dev pytest -m integration

# Verifica se o peso local confere com o manifesto; não baixa nada.
$env:MEDTRACK_RUN_MODEL_SMOKE = "1"
uv run --group dev pytest -m model
```

O marcador `model` é excluído do comando padrão. Isso é intencional: uma CI não
deve esconder falhas usando `skip` porque um arquivo grande ou uma GPU não está
disponível. O job que executá-lo deve baixar o artefato pelo manifesto antes de
rodar o teste.

## Cobertura

O pytest produz cobertura de `medtrack_ai` a cada execução. Não há meta mínima
ainda, pois a camada de YOLO/EasyOCR será coberta por testes de adaptador e
smoke de inferência em etapa posterior. Uma meta só será ativada após medir uma
linha de base estável, para evitar uma porcentagem artificial.
