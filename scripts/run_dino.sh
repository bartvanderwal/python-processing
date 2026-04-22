#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${VENV_DIR:-$ROOT_DIR/.venv}"

if [ ! -x "$VENV_DIR/bin/python" ]; then
  echo "[run-dino] Missing venv: $VENV_DIR"
  echo "[run-dino] Run: scripts/setup_venv.sh"
  exit 1
fi

exec "$VENV_DIR/bin/python" "$ROOT_DIR/dino_game.py" "$@"
