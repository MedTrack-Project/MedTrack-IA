# Inventário técnico — linha de base

Data do levantamento: 22 de julho de 2026.

## Componentes existentes

| Componente | Localização atual | Observação |
| --- | --- | --- |
| API FastAPI | `src/api/api.py` | Expõe uma única rota e também carrega o modelo no momento da importação. |
| OCR | `src/api/ocr_extration.py` | Inicializa o EasyOCR no momento da importação e depende de GPU fixa. |
| Treinamento | `src/training/train.py` | Executa fine-tuning YOLO e grava resultados em `runs/detect`. |
| Utilitários | `src/utils/` | Sanitização de texto e ferramenta de rotulagem. |
| Dados | `dataset/` e fonte externa indicada no README | Dataset e pesos são locais e ignorados; apenas a configuração de treino é versionada. |
| Contêiner | `Dockerfile` | Instala `requirements.txt` e inicia `src.api.api:app`, mas não recebe o modelo. |
| Testes | `tests/test_api.py` | Mistura teste HTTP e modelo real; cria artefato local; alguns casos são ignorados quando não há imagem. |

## Contrato HTTP observado (baseline)

O contrato abaixo descreve o comportamento atual e deve ser preservado até que
uma nova versão de API seja acordada com o aplicativo Android.

| Item | Definição atual |
| --- | --- |
| Serviço | FastAPI, porta `8000` |
| Operação | `POST /detect` |
| Entrada | `multipart/form-data`, campo obrigatório `file`, conteúdo de imagem |
| Sucesso | `200 OK` com `status`, `is_generico`, `data` e `count` |
| Erro de tipo não-imagem | `400 Bad Request` com `detail` |
| Erro de validação multipart | `422 Unprocessable Entity` gerado pelo FastAPI |
| OpenAPI interativa | `GET /docs` |

Exemplo de resposta de sucesso:

```json
{
  "status": "success",
  "is_generico": false,
  "data": {
    "nome": "..."
  },
  "count": 1
}
```

## Riscos e débitos confirmados

1. O caminho do peso do YOLO contém diretórios de resultados de treinamento e
   está codificado no código da API.
2. A aplicação encerra o processo durante a importação se o peso não existir;
   isso dificulta testes e health checks.
3. O Dockerfile não contém nem recupera o peso exigido pela aplicação.
4. Dispositivo CUDA, limiar, tamanho de imagem e leitor OCR são configurados no
   código, e não por ambiente.
5. `requirements.txt` não possui lockfile; versões sem `==` não são
   reprodutíveis.
6. O `.gitignore` ignora todo arquivo `.txt`, inclusive arquivos que podem ser
   manifestos, documentação ou anotações de dados desejadas.

## Fora do escopo desta entrega

- Alterar a rota, a resposta ou as regras de extração.
- Melhorar treino, métricas ou qualidade OCR/YOLO.
- Escolher o registry definitivo de modelo ou a plataforma de deploy.
- Reescrever o Dockerfile ou publicar uma imagem.
