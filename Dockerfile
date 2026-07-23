# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:0.11.30 AS uv

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        ca-certificates \
        libgl1 \
        libglib2.0-0 \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app \
    && useradd --system --gid app --home-dir /home/app --create-home app

WORKDIR /app

COPY --from=uv /uv /uvx /bin/

# Resolve dependências antes do código para aproveitar o cache de camadas.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --group inference --no-install-project

COPY --chown=app:app src ./src
COPY --chown=app:app config ./config
RUN uv sync --frozen --no-dev --group inference

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=45s --retries=3 \
    CMD python -c "from urllib.request import urlopen; urlopen('http://127.0.0.1:8000/healthz', timeout=3)"

CMD ["uvicorn", "medtrack_ai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
