#!/usr/bin/env python3
"""Scan modes/ and families/ and emit index.json on stdout.

Schema is documented in docs/REGISTRY_FORMAT.md. This script is the
canonical reference implementation — the GitHub Action runs it on
every push to main and commits the resulting index.json back to the
repo.

Run locally: `python scripts/build_index.py > index.json`
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import sys
from pathlib import Path

try:
    import tomllib as toml  # Python 3.11+
except ModuleNotFoundError:
    import tomli as toml  # type: ignore

REPO = "Dominga/llm-workbench-registry"
BRANCH = "main"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}"

ROOT = Path(__file__).resolve().parent.parent


def _read_toml(path: Path) -> dict:
    with path.open("rb") as f:
        return toml.load(f)


def _sha256_concat(paths: list[Path]) -> str:
    h = hashlib.sha256()
    for p in paths:
        h.update(p.read_bytes())
    return h.hexdigest()


def _mode_artifact(dir_: Path) -> dict:
    mode_id = dir_.name
    meta = _read_toml(dir_ / f"{mode_id}.toml")
    files: list[Path] = [dir_ / f"{mode_id}.toml"]
    # Pick up every system.md variant in the directory (default + family-
    # specific). Sorted so the on-disk order is reproducible.
    for f in sorted(dir_.glob("*.system.md")):
        files.append(f)
    sha = _sha256_concat(files)
    preview = ""
    default_md = dir_ / f"{mode_id}.system.md"
    if default_md.exists():
        preview = default_md.read_text(encoding="utf-8")[:500]
    return {
        "type": "mode",
        "id": mode_id,
        "version": str(meta.get("version", "0.0.0")),
        "sha256": sha,
        "files": [
            {
                "path": f.name,
                "url": f"{RAW_BASE}/modes/{mode_id}/{f.name}",
            }
            for f in files
        ],
        "description": meta.get("desc") or meta.get("description") or "",
        "tags": list(meta.get("tags") or []),
        "recommended_for": list(meta.get("recommended_for") or []),
        "author": meta.get("author", ""),
        "preview": preview,
    }


def _family_artifact(dir_: Path) -> dict:
    fam_id = dir_.name
    meta = _read_toml(dir_ / f"{fam_id}.toml")
    files = [dir_ / f"{fam_id}.toml"]
    sha = _sha256_concat(files)
    return {
        "type": "family",
        "id": fam_id,
        "version": str(meta.get("version", "0.0.0")),
        "sha256": sha,
        "files": [
            {
                "path": f.name,
                "url": f"{RAW_BASE}/families/{fam_id}/{f.name}",
            }
            for f in files
        ],
        "description": meta.get("description", ""),
        "tags": list(meta.get("tags") or []),
        "author": meta.get("author", ""),
    }


def main() -> int:
    artifacts: list[dict] = []
    modes_dir = ROOT / "modes"
    if modes_dir.is_dir():
        for d in sorted(p for p in modes_dir.iterdir() if p.is_dir()):
            try:
                artifacts.append(_mode_artifact(d))
            except FileNotFoundError as e:
                print(f"skip mode {d.name}: {e}", file=sys.stderr)
    fams_dir = ROOT / "families"
    if fams_dir.is_dir():
        for d in sorted(p for p in fams_dir.iterdir() if p.is_dir()):
            try:
                artifacts.append(_family_artifact(d))
            except FileNotFoundError as e:
                print(f"skip family {d.name}: {e}", file=sys.stderr)

    out = {
        "schema_version": 1,
        "updated_at": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "artifacts": artifacts,
    }
    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
