#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${VENV_DIR:-$ROOT_DIR/.venv}"
PYTHON_BIN="${PYTHON_BIN:-}"

choose_python_bin() {
  local candidate
  local minor
  local major
  local version

  if [ -n "$PYTHON_BIN" ]; then
    local forced_version
    local forced_major
    local forced_minor
    if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
      echo "[venv-setup] ERROR: PYTHON_BIN '$PYTHON_BIN' not found."
      exit 1
    fi
    forced_version="$("$PYTHON_BIN" - <<'PY'
import sys
print(f"{sys.version_info.major}.{sys.version_info.minor}")
PY
)"
    forced_major="${forced_version%%.*}"
    forced_minor="${forced_version##*.}"
    if [ "$forced_major" -eq 3 ] && [ "$forced_minor" -ge 14 ]; then
      echo "[venv-setup] ERROR: PYTHON_BIN '$PYTHON_BIN' is Python $forced_version." >&2
      echo "[venv-setup] Use Python 3.13/3.12 for reliable PNG support in pygame." >&2
      exit 1
    fi
    echo "$PYTHON_BIN"
    return 0
  fi

  for candidate in python3.13 python3.12 python3; do
    if ! command -v "$candidate" >/dev/null 2>&1; then
      continue
    fi
    version="$("$candidate" - <<'PY'
import sys
print(f"{sys.version_info.major}.{sys.version_info.minor}")
PY
)"
    major="${version%%.*}"
    minor="${version##*.}"
    if [ "$major" -eq 3 ] && [ "$minor" -lt 14 ]; then
      echo "$candidate"
      return 0
    fi
  done

  echo "[venv-setup] ERROR: No compatible Python found (<3.14)." >&2
  echo "[venv-setup] Install Python 3.13 and rerun." >&2
  exit 1
}

venv_needs_recreate() {
  local version
  local major
  local minor
  if [ ! -x "$VENV_DIR/bin/python" ]; then
    return 1
  fi
  version="$("$VENV_DIR/bin/python" - <<'PY'
import sys
print(f"{sys.version_info.major}.{sys.version_info.minor}")
PY
)"
  major="${version%%.*}"
  minor="${version##*.}"
  if [ "$major" -eq 3 ] && [ "$minor" -ge 14 ]; then
    return 0
  fi
  return 1
}

PYTHON_BIN="$(choose_python_bin)"

echo "[venv-setup] root: $ROOT_DIR"
echo "[venv-setup] python: $PYTHON_BIN"
echo "[venv-setup] venv: $VENV_DIR"

if venv_needs_recreate; then
  echo "[venv-setup] Existing venv uses Python >=3.14; recreating for pygame image support."
  "$PYTHON_BIN" -m venv --clear "$VENV_DIR"
elif [ ! -d "$VENV_DIR" ]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -r "$ROOT_DIR/requirements.txt"

"$VENV_DIR/bin/python" - <<PY
import pygame
from pathlib import Path

target = Path(r"$ROOT_DIR") / "assets" / "dino-transparant.png"
try:
    pygame.image.load(str(target))
except Exception as exc:
    raise SystemExit(
        f"[venv-setup] ERROR: PNG decode test failed for {target}: {exc}"
    )
print(f"[venv-setup] PNG decode test: OK ({target.name})")
PY

echo "[venv-setup] Done."
echo "[venv-setup] Run game with: scripts/run_dino.sh"
