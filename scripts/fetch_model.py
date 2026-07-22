"""Baixa um modelo versionado e só o publica localmente após validar SHA-256."""

from __future__ import annotations

import argparse
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

from medtrack_ai.model_registry.manifest import load_manifest, verify_checksum


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("config/models/medtrack-yolo-v1.0.0.json"),
        help="Caminho para o manifesto JSON do modelo.",
    )
    parser.add_argument(
        "--destination",
        type=Path,
        help="Sobrescreve o caminho local definido no manifesto.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Substitui um arquivo local existente que não passe na verificação.",
    )
    return parser.parse_args()


def fetch(manifest_path: Path, destination: Path | None, force: bool) -> Path:
    """Baixa para arquivo temporário, verifica e move atomicamente para o destino."""
    manifest = load_manifest(manifest_path)
    target = destination or manifest.local_path

    if target.exists():
        if verify_checksum(target, manifest.sha256):
            print(f"Modelo já verificado: {target}")
            return target
        if not force:
            raise RuntimeError(
                f"O arquivo existente em {target} não corresponde ao manifesto. "
                "Use --force somente após investigar sua origem."
            )

    target.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = target.with_suffix(f"{target.suffix}.part")
    try:
        with urllib.request.urlopen(str(manifest.download_url), timeout=60) as response:
            with temporary_path.open("wb") as output:
                shutil.copyfileobj(response, output)
        if not verify_checksum(temporary_path, manifest.sha256):
            raise RuntimeError("Checksum inválido: o download não será usado.")
        temporary_path.replace(target)
    except urllib.error.URLError as error:
        raise RuntimeError(f"Não foi possível baixar o modelo: {error.reason}") from error
    finally:
        temporary_path.unlink(missing_ok=True)

    print(f"Modelo baixado e verificado: {target}")
    return target


def main() -> int:
    args = parse_args()
    try:
        fetch(args.manifest, args.destination, args.force)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
