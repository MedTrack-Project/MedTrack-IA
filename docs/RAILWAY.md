# Deploy de staging na Railway

Este repositório está preparado para ser implantado como um serviço Railway a
partir da branch `main`. A Railway detecta o `Dockerfile` na raiz e usa
`railway.toml` para aguardar a prontidão real em `/readyz`.

## Preparação da conta e do projeto

1. Entre na Railway usando sua conta GitHub e crie o projeto `medtrack`.
2. Crie o ambiente `staging` e conecte o repositório `MedTrack-Project/MedTrack-IA`
   à branch `main`.
3. Crie um serviço a partir do repositório. Não defina Start Command: o `CMD` do
   Dockerfile usa automaticamente a porta `PORT` injetada pela Railway.
4. Em **Volumes**, adicione um volume de ao menos 0,5 GB no caminho `/data`.
5. Em **Networking**, gere um domínio público Railway. Registre a URL no canal
   interno do projeto; o app Android deve recebê-la por configuração de build,
   nunca como literal no código-fonte.

## Variáveis do ambiente `staging`

Use o Raw Editor da aba **Variables** e cole os valores abaixo. Não copie um
`.env` com segredos para o Git.

```dotenv
MEDTRACK_ENV=staging
MEDTRACK_LOG_LEVEL=INFO
MEDTRACK_MODEL_URI=/data/models/medtrack-yolo/v1.0.0/best.pt
MEDTRACK_MODEL_VERSION=v1.0.0
MEDTRACK_MODEL_MANIFEST=config/models/medtrack-yolo-v1.0.0.json
MEDTRACK_FETCH_MODEL_ON_START=true
MEDTRACK_DEVICE=cpu
MEDTRACK_MAX_IMAGE_DIMENSION=1024
MEDTRACK_YOLO_CONFIDENCE=0.5
EASYOCR_MODULE_PATH=/data/easyocr
MEDTRACK_CORS_ORIGINS=
RAILWAY_HEALTHCHECK_TIMEOUT_SEC=300
RAILWAY_DEPLOYMENT_DRAINING_SECONDS=30
```

O entrypoint prepara as permissões do volume, baixa o peso apenas se ele ainda
não passar no checksum e inicia a API como usuário sem privilégios. O volume
também preserva os modelos auxiliares baixados pelo EasyOCR entre reinícios.

## Verificação após deploy

Substitua `URL` pelo domínio público gerado:

```powershell
Invoke-WebRequest https://URL/healthz
Invoke-WebRequest https://URL/readyz
```

`/healthz` confirma o processo; `/readyz` só retorna `200` quando o modelo foi
carregado. A Railway usa `/readyz` durante o deploy e aguarda até 300 segundos.

## Logs, operação e rollback

- Logs são JSON no stdout e incluem `request_id`, rota, status, duração e versão
  do modelo; não registram a imagem nem o texto extraído.
- Para correlacionar uma ocorrência do mobile, envie o valor de `X-Request-ID`
  junto ao relato.
- Antes de promover uma mudança, confira o workflow `Quality` e o endpoint
  `/readyz` em staging.
- Para rollback, em **Deployments** escolha o deployment estável anterior e use
  **Redeploy**. O volume contém o mesmo modelo versionado; para reverter modelo,
  altere explicitamente `MEDTRACK_MODEL_*` para outro manifesto/versão e faça
  novo deploy.

## Limitações intencionais

O ambiente Trial/Free tem créditos e políticas de restart limitadas. Ele é
adequado para staging acadêmico, não para alegações de disponibilidade clínica.
O serviço não deve decidir administração de medicamentos sem conferência humana.
