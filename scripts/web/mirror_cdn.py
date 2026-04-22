#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import urllib.request
from urllib.error import HTTPError
from pathlib import Path


def download_url(url: str, target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    print(f"[cdn-mirror] GET {url}")
    with urllib.request.urlopen(url) as response:
        data = response.read()
    target.write_bytes(data)
    print(f"[cdn-mirror] WROTE {target} ({len(data)} bytes)")
    return target


def download(base_url: str, rel_path: str, out_root: Path) -> Path:
    url = f"{base_url}{rel_path}"
    target = out_root / rel_path
    return download_url(url, target)


def try_download(base_url: str, rel_path: str, out_root: Path) -> bool:
    try:
        download(base_url, rel_path, out_root)
        return True
    except HTTPError as exc:
        print(f"[cdn-mirror] MISS {rel_path} ({exc})")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Mirror minimal pygbag CDN files locally.")
    parser.add_argument("--output", required=True, help="Local output folder (usually .web-build/output/cdn)")
    parser.add_argument("--cdn-base", default="https://pygame-web.github.io/cdn/", help="Upstream CDN root")
    parser.add_argument("--pygbag-version", default="0.9.3")
    parser.add_argument("--python-tag", default="cp312")
    parser.add_argument("--api-tag", default="wasm32_bi_emscripten")
    parser.add_argument("--modules", default="pygame", help="Comma-separated package modules to mirror from index")
    args = parser.parse_args()

    out_root = Path(args.output).resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    base = args.cdn_base if args.cdn_base.endswith("/") else f"{args.cdn_base}/"

    runtime_files = [
        f"{args.pygbag_version}/pythons.js",
        f"{args.pygbag_version}/empty.html",
        f"{args.pygbag_version}/empty.ogg",
        f"{args.pygbag_version}/cpythonrc.py",
        f"{args.pygbag_version}/cpython312/main.js",
        f"{args.pygbag_version}/cpython312/main.data",
        f"{args.pygbag_version}/cpython312/main.wasm",
    ]
    for rel in runtime_files:
        download(base, rel, out_root)

    browserfs_rel = f"{args.pygbag_version}/browserfs.min.js"
    if not try_download(base, browserfs_rel, out_root):
        fallback_url = "https://unpkg.com/browserfs@1.4.3/dist/browserfs.min.js"
        try:
            download_url(fallback_url, out_root / browserfs_rel)
        except HTTPError as exc:
            raise SystemExit(f"[cdn-mirror] Missing required BrowserFS asset ({exc})")

    index_rel = f"index-{args.pygbag_version}-{args.python_tag}.json"
    index_path = download(base, index_rel, out_root)
    index_data = json.loads(index_path.read_text(encoding="utf-8"))

    requested_modules = [m.strip() for m in args.modules.split(",") if m.strip()]
    for module in requested_modules:
        rel = index_data.get(module)
        if not rel:
            print(f"[cdn-mirror] SKIP missing module in index: {module}")
            continue
        rel = rel.replace("<abi>", args.python_tag).replace("<api>", args.api_tag)
        download(base, rel, out_root)

    print("[cdn-mirror] Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
