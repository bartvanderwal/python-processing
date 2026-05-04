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
PUBLIC_BASE_PATH="${PUBLIC_BASE_PATH:-}"

if git -C "$ROOT_DIR" rev-parse --verify HEAD >/dev/null 2>&1; then
  BUILD_ID="${WEB_BUILD_ID:-$(git -C "$ROOT_DIR" rev-parse --short=12 HEAD)}"
else
  BUILD_ID="${WEB_BUILD_ID:-$(date +%s)}"
fi

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

APP_VERSION="$(awk -F'"' '/^APP_VERSION = "/ { print $2; exit }' "$ROOT_DIR/$ENTRY_FILE")"
if [ -z "$APP_VERSION" ]; then
  APP_VERSION="0.0.0"
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

# Web build guard: pygbag exits with code 3 when MP3 assets are present.
# Keep source assets intact; remove MP3 only from temporary stage folder.
assets_dir = stage / "assets"
if assets_dir.exists():
    removed = 0
    for mp3_file in assets_dir.rglob("*.mp3"):
        mp3_file.unlink(missing_ok=True)
        removed += 1
    if removed:
        print(f"[web-build] Removed {removed} mp3 files from stage assets")

print(f"[web-build] Stage ready: {stage} (entry={entry}, include_assets={include_assets})")
PY

SSL_CERT_FILE="$($VENV_DIR/bin/python - <<'PY'
try:
    import certifi
    print(certifi.where())
except Exception as exc:
    import sys

    print(f"[web-build] Failed to resolve certifi CA bundle: {exc.__class__.__name__}: {exc}", file=sys.stderr)
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
import json
from pathlib import Path

stage = Path(r"$STAGE_DIR")
output = Path(r"$OUTPUT_DIR")
build_id = r"$BUILD_ID"
app_version = r"$APP_VERSION"
app_title = f"dino_game v{app_version}"
bundle_filename = f"dino_game-v{app_version}-{build_id}.tar.gz"
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

stage_archive = output / "stage.tar.gz"
if stage_archive.exists():
    renamed_archive = output / bundle_filename
    if renamed_archive.exists():
        renamed_archive.unlink()
    stage_archive.rename(renamed_archive)

version_file = output / "version.json"
version_file.write_text(
  json.dumps(
    {
      "build_id": build_id,
      "app_version": app_version,
      "title": app_title,
      "bundle_filename": bundle_filename,
    },
    indent=2,
  ) + "\n",
  encoding="utf-8",
)

index_file = output / "index.html"
if index_file.exists():
    html = index_file.read_text(encoding="utf-8")
    # Some pygbag templates can emit a double slash before browserfs.min.js.
    html = re.sub(
        r"(https://pygame-web\\.github\\.io/cdn/[^\"']+)/+/browserfs\\.min\\.js",
        r"\\1/browserfs.min.js",
        html,
    )
    html = html.replace('platform.fopen("stage.tar.gz", "rb")', f'platform.fopen("{bundle_filename}", "rb")')
    html = html.replace("<title>Dino Game</title>", f"<title>{app_title}</title>")
    if "#app_chrome_banner" not in html:
        html = html.replace(
            "</style>",
            """
        #app_chrome_banner {
            position: fixed;
            top: max(10px, env(safe-area-inset-top));
            left: 50%;
            transform: translateX(-50%);
            z-index: 30;
            padding: 8px 14px;
            border-radius: 999px;
            background: rgba(16, 24, 32, 0.78);
            color: #f4f1da;
            font: 600 13px/1.2 Menlo, Monaco, monospace;
            letter-spacing: 0.04em;
            pointer-events: none;
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.22);
        }
          #app_update_button {
            position: fixed;
            top: max(10px, env(safe-area-inset-top));
            right: 14px;
            z-index: 31;
            padding: 8px 12px;
            border: 0;
            border-radius: 999px;
            background: #e7f07a;
            color: #17212b;
            font: 700 12px/1.2 Menlo, Monaco, monospace;
            letter-spacing: 0.02em;
            cursor: pointer;
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.22);
          }
          #app_update_button[hidden] {
            display: none;
          }
        </style>""",
        )
        html = html.replace(
            "<body>",
            f"<body>\n    <div id=\"app_chrome_banner\">{app_title}</div>\n    <button id=\"app_update_button\" type=\"button\" hidden>Nieuwe versie ophalen</button>",
        )
    elif "id=\"app_update_button\"" not in html:
        html = html.replace(
            '<div id="app_chrome_banner">',
            '<button id="app_update_button" type="button" hidden>Nieuwe versie ophalen</button>\n    <div id="app_chrome_banner">',
            1,
        )
    if "__APP_BUILD_INFO__" not in html:
        html = html.replace(
            "</body>",
            f"""
        <script>
        window.__APP_BUILD_INFO__ = {{
          build_id: {build_id!r},
          app_version: {app_version!r},
          title: {app_title!r}
        }};

        (function() {{
          const currentBuild = window.__APP_BUILD_INFO__;
          const updateButton = document.getElementById("app_update_button");

          if (!updateButton) {{
            return;
          }}

          async function checkForNewBuild() {{
            try {{
              const response = await fetch("version.json?ts=" + Date.now(), {{ cache: "no-store" }});
              if (!response.ok) {{
                return;
              }}

              const remoteBuild = await response.json();
              if (!remoteBuild.build_id || remoteBuild.build_id === currentBuild.build_id) {{
                updateButton.hidden = true;
                return;
              }}

              updateButton.hidden = false;
              if (remoteBuild.app_version) {{
                updateButton.textContent = "Nieuwe versie ophalen (v" + remoteBuild.app_version + ")";
              }}

              updateButton.onclick = () => {{
                const url = new URL(window.location.href);
                url.searchParams.set("v", remoteBuild.build_id);
                window.location.replace(url.toString());
              }};
            }} catch (error) {{
              console.warn("build update check skipped:", error);
            }}
          }}

          window.addEventListener("load", () => {{
            checkForNewBuild();
            window.setInterval(checkForNewBuild, 60000);
          }});
        }})();
        </script>
      </body>""",
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
import json

index = Path(r"$OUTPUT_DIR") / "index.html"
# Use document-relative asset paths so the built site keeps working after
# GitHub Pages project-path changes such as repository renames.
cdn_prefix = "cdn/0.9.3"
build_id = r"$BUILD_ID"
app_version = r"$APP_VERSION"
app_title = f"dino_game v{app_version}"
bundle_filename = f"dino_game-v{app_version}-{build_id}.tar.gz"
if index.exists():
    html = index.read_text(encoding="utf-8")
    html = html.replace('src="https://pygame-web.github.io/cdn/0.9.3/pythons.js"', f'src="{cdn_prefix}/pythons.js?v={build_id}"')
    html = html.replace('src="https://pygame-web.github.io/cdn/0.9.3/browserfs.min.js"', f'src="{cdn_prefix}/browserfs.min.js?v={build_id}"')
    html = html.replace('src="https://pygame-web.github.io/cdn/0.9.3//browserfs.min.js"', f'src="{cdn_prefix}/browserfs.min.js?v={build_id}"')
    html = html.replace("https://pygame-web.github.io/cdn/0.9.3/empty.html", f"{cdn_prefix}/empty.html")
    html = html.replace('cdn : "https://pygame-web.github.io/cdn/0.9.3/",', f'cdn : "{cdn_prefix}/",')
    html = html.replace('CDN URL : https://pygame-web.github.io/cdn/0.9.3/', f'CDN URL : {cdn_prefix}/ (local mirror)')
    html = html.replace("<title>Dino Game</title>", f"<title>dino_game v{app_version}</title>")
    html = html.replace('sandbox="allow-scripts allow-pointer-lock"', 'sandbox="allow-scripts allow-pointer-lock allow-same-origin"')
    html = re.sub(r'(<script[^>]*id="site"[^>]*?)\\s+async\\s+defer', r'\\1 defer', html, count=1)
    # Keep output lean: disable terminal addon that triggers extra CDN side-loads.
    html = html.replace('data-os="vtx,snd,gui"', 'data-os="snd,gui"')
    html = html.replace('xtermjs : "1"', 'xtermjs : "0"')
    index.write_text(html, encoding="utf-8")
    (index.parent / "version.json").write_text(
      json.dumps(
        {
          "build_id": build_id,
          "app_version": app_version,
          "title": app_title,
          "bundle_filename": bundle_filename,
        },
        indent=2,
      ) + "\n",
      encoding="utf-8",
    )
PY
fi

echo "[web-build] Done."
echo "[web-build] Preview with: scripts/web/run_web.sh"
