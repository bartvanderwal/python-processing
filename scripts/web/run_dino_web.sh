#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

ENTRY_FILE="${ENTRY_FILE:-dino_game.py}"
INCLUDE_ASSETS="${INCLUDE_ASSETS:-1}"
LOCAL_CDN="${LOCAL_CDN:-1}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-9000}"

ENTRY_FILE="$ENTRY_FILE" \
INCLUDE_ASSETS="$INCLUDE_ASSETS" \
LOCAL_CDN="$LOCAL_CDN" \
"$ROOT_DIR/scripts/web/build_web.sh"

HOST="$HOST" PORT="$PORT" "$ROOT_DIR/scripts/web/run_web.sh"
