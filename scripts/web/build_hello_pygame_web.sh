#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

ENTRY_FILE="hello_pygame_web.py" INCLUDE_ASSETS=0 "$ROOT_DIR/scripts/web/build_web.sh"
