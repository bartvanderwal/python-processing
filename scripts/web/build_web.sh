#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_DIR="${VENV_DIR:-$ROOT_DIR/.venv-web}"
STAGE_DIR="$ROOT_DIR/.web-build/stage"
OUTPUT_DIR="$ROOT_DIR/.web-build/output"
ENTRY_FILE="${ENTRY_FILE:-dino_game.py}"
INCLUDE_ASSETS="${INCLUDE_ASSETS:-1}"
PYGBAG_CDN="${PYGBAG_CDN:-https://pygame-web.github.io/cdn/0.9.3/}"
PYGBAG_TEMPLATE="${PYGBAG_TEMPLATE:-$ROOT_DIR/scripts/web/default.tmpl}"
PYGBAG_ICON="${PYGBAG_ICON:-$ROOT_DIR/processing/icon.png}"
LOCAL_CDN="${LOCAL_CDN:-1}"
LOCAL_CDN_MODULES="${LOCAL_CDN_MODULES:-pygame}"

# Pygbag concatenates CDN + template filename directly, so CDN must end with '/'.
if [[ "$PYGBAG_CDN" != */ ]]; then
  PYGBAG_CDN="${PYGBAG_CDN}/"
fi

if [ ! -x "$VENV_DIR/bin/python" ]; then
  echo "[web-build] Missing venv: $VENV_DIR"
  echo "[web-build] Run: scripts/web/setup_web.sh"
  exit 1
fi

if [ ! -f "$ROOT_DIR/$ENTRY_FILE" ]; then
  echo "[web-build] Missing entry file: $ROOT_DIR/$ENTRY_FILE"
  exit 1
fi

echo "[web-build] Preparing stage folder..."
"$VENV_DIR/bin/python" - <<PY
import os
import shutil
from pathlib import Path

root = Path(r"$ROOT_DIR")
stage = Path(r"$STAGE_DIR")
entry = Path(r"$ENTRY_FILE")
include_assets = str(r"$INCLUDE_ASSETS").strip() not in ("0", "false", "False", "no", "NO")

if stage.exists():
    shutil.rmtree(stage)
stage.mkdir(parents=True, exist_ok=True)

# Entry point for pygbag should be main.py
shutil.copy2(root / entry, stage / "main.py")

for file_name in ("shared.py", "api.md", "dino.md", "README.md", "processing_extension.py"):
    src = root / file_name
    if src.exists():
        shutil.copy2(src, stage / file_name)

folders = ["processing"]
if include_assets:
    folders.append("assets")

for folder_name in folders:
    src = root / folder_name
    dst = stage / folder_name
    if src.exists():
        shutil.copytree(src, dst)

print(f"[web-build] Stage ready: {stage} (entry={entry}, include_assets={include_assets})")
PY

SSL_CERT_FILE="$($VENV_DIR/bin/python - <<'PY'
try:
    import certifi
    print(certifi.where())
except Exception:
    print("")
PY
)"
if [ -n "$SSL_CERT_FILE" ]; then
  export SSL_CERT_FILE
  echo "[web-build] SSL cert bundle: $SSL_CERT_FILE"
fi

echo "[web-build] Running pygbag build..."
PYGBAG_ARGS=(--build --disable-sound-format-error --cdn "$PYGBAG_CDN")

if [ -f "$PYGBAG_TEMPLATE" ]; then
  PYGBAG_ARGS+=(--template "$PYGBAG_TEMPLATE")
fi

if [ -f "$PYGBAG_ICON" ]; then
  PYGBAG_ARGS+=(--icon "$PYGBAG_ICON")
fi

"$VENV_DIR/bin/python" -m pygbag "${PYGBAG_ARGS[@]}" "$STAGE_DIR"

echo "[web-build] Collecting build output..."
"$VENV_DIR/bin/python" - <<PY
import shutil
import re
from pathlib import Path

stage = Path(r"$STAGE_DIR")
output = Path(r"$OUTPUT_DIR")
candidates = [
    stage / "build" / "web",
    stage / "build",
]

built = None
for candidate in candidates:
    if candidate.exists():
        built = candidate
        break

if built is None:
    raise SystemExit("[web-build] Could not find pygbag build output.")

if output.exists():
    shutil.rmtree(output)
output.parent.mkdir(parents=True, exist_ok=True)
shutil.copytree(built, output)

index_file = output / "index.html"
if index_file.exists():
    html = index_file.read_text(encoding="utf-8")
    # Some pygbag templates can emit a double slash before browserfs.min.js.
    html = re.sub(
        r"(https://pygame-web\\.github\\.io/cdn/[^\"']+)/+/browserfs\\.min\\.js",
        r"\\1/browserfs.min.js",
        html,
    )
    index_file.write_text(html, encoding="utf-8")

print(f"[web-build] Output copied to: {output}")
PY

if [ "$LOCAL_CDN" = "1" ]; then
  echo "[web-build] Mirroring pygbag CDN subset locally..."
  "$VENV_DIR/bin/python" "$ROOT_DIR/scripts/web/mirror_cdn.py" \
    --output "$OUTPUT_DIR/cdn" \
    --cdn-base "https://pygame-web.github.io/cdn/" \
    --pygbag-version "0.9.3" \
    --python-tag "cp312" \
    --api-tag "wasm32_bi_emscripten" \
    --modules "$LOCAL_CDN_MODULES"

  echo "[web-build] Rewriting index.html to local /cdn paths..."
  "$VENV_DIR/bin/python" - <<PY
from pathlib import Path
import re

index = Path(r"$OUTPUT_DIR") / "index.html"
if index.exists():
    html = index.read_text(encoding="utf-8")
    html = html.replace('src="https://pygame-web.github.io/cdn/0.9.3/pythons.js"', 'src="/cdn/0.9.3/pythons.js"')
    html = html.replace('src="https://pygame-web.github.io/cdn/0.9.3/browserfs.min.js"', 'src="/cdn/0.9.3/browserfs.min.js"')
    html = html.replace('src="https://pygame-web.github.io/cdn/0.9.3//browserfs.min.js"', 'src="/cdn/0.9.3/browserfs.min.js"')
    html = html.replace("https://pygame-web.github.io/cdn/0.9.3/empty.html", "/cdn/0.9.3/empty.html")
    html = html.replace('cdn : "https://pygame-web.github.io/cdn/0.9.3/",', 'cdn : "/cdn/0.9.3/",')
    html = re.sub(r'(<script[^>]*id="site"[^>]*?)\\s+async\\s+defer', r'\\1 defer', html, count=1)
    # Keep output lean: disable terminal addon that triggers extra CDN side-loads.
    html = html.replace('data-os="vtx,snd,gui"', 'data-os="snd,gui"')
    html = html.replace('xtermjs : "1"', 'xtermjs : "0"')
    index.write_text(html, encoding="utf-8")
PY
fi

echo "[web-build] Done."
echo "[web-build] Preview with: scripts/web/run_web.sh"
