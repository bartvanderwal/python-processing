#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-9000}"
OUTPUT_DIR="$ROOT_DIR/.web-build/output"

if [ ! -f "$OUTPUT_DIR/index.html" ]; then
  echo "[web-run] No web build found. Building first..."
  "$ROOT_DIR/scripts/web/build_web.sh"
fi

echo "[web-run] Serving $OUTPUT_DIR on http://$HOST:$PORT"
python3 -m http.server "$PORT" --bind "$HOST" --directory "$OUTPUT_DIR"
