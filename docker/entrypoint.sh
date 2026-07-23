#!/bin/sh
set -eu

artifact_directory="$(dirname "${MEDTRACK_MODEL_URI}")"
easyocr_directory="${EASYOCR_MODULE_PATH:-/home/app/.EasyOCR}"

# Volumes Railway são montados no início do container. Preparamos permissões
# como root e reexecutamos o entrypoint com o usuário sem privilégios.
if [ "$(id -u)" = "0" ]; then
    mkdir -p "${artifact_directory}" "${easyocr_directory}"
    chown -R app:app "${artifact_directory}" "${easyocr_directory}"
    exec gosu app "$0" "$@"
fi

if [ "${MEDTRACK_FETCH_MODEL_ON_START:-false}" = "true" ]; then
    python scripts/fetch_model.py --manifest "${MEDTRACK_MODEL_MANIFEST}"
fi

exec "$@"
