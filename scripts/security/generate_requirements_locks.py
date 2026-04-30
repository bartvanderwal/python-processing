#!/usr/bin/env python3
"""Generate hash-locked requirements files from PyPI metadata."""

from __future__ import annotations

import json
import ssl
import sys
import traceback
import urllib.request
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Requirement:
    name: str
    version: str


RUNTIME_REQUIREMENTS = [
    Requirement("pygame-ce", "2.5.7"),
]

WEB_REQUIREMENTS = [
    Requirement("pygame-ce", "2.5.7"),
    Requirement("pygbag", "0.9.3"),
    Requirement("certifi", "2026.2.25"),
]


def log_script_exception(context: str, exc: Exception, *, once_key: str | None = None) -> None:
    if not hasattr(log_script_exception, "_seen_keys"):
        log_script_exception._seen_keys = set()
    if once_key is not None:
        if once_key in log_script_exception._seen_keys:
            return
        log_script_exception._seen_keys.add(once_key)
    print(f"[generate_requirements_locks] {context}: {exc.__class__.__name__}: {exc}", file=sys.stderr)
    traceback.print_exception(type(exc), exc, exc.__traceback__)


def build_ssl_context() -> ssl.SSLContext:
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception as exc:
        log_script_exception(
            "Falling back to system CA bundle because certifi could not be loaded",
            exc,
            once_key="build_ssl_context_certifi",
        )
        return ssl.create_default_context()


def fetch_wheel_hashes(requirement: Requirement, context: ssl.SSLContext) -> list[str]:
    url = f"https://pypi.org/pypi/{requirement.name}/{requirement.version}/json"
    with urllib.request.urlopen(url, context=context) as response:
        payload = json.load(response)

    hashes = {
        file_obj["digests"]["sha256"]
        for file_obj in payload["urls"]
        if file_obj.get("packagetype") == "bdist_wheel"
    }
    if not hashes:
        raise RuntimeError(f"No wheel files found for {requirement.name}=={requirement.version}")
    return sorted(hashes)


def render_requirements(requirements: list[Requirement], *, generated_on: str) -> str:
    context = build_ssl_context()
    lines = [
        "# Locked dependencies for deterministic and secure installs.",
        f"# Generated from PyPI metadata on {generated_on}.",
        "# Enforced by setup scripts with --require-hashes and --only-binary=:all:.",
    ]

    for idx, requirement in enumerate(requirements):
        if idx:
            lines.append("")
        hashes = fetch_wheel_hashes(requirement, context)
        lines.append(f"{requirement.name}=={requirement.version} \\")
        for hash_idx, sha in enumerate(hashes):
            tail = " \\" if hash_idx < len(hashes) - 1 else ""
            lines.append(f"    --hash=sha256:{sha}{tail}")

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    generated_on = "2026-04-29"

    runtime_text = render_requirements(RUNTIME_REQUIREMENTS, generated_on=generated_on)
    web_text = render_requirements(WEB_REQUIREMENTS, generated_on=generated_on)

    (root / "requirements.txt").write_text(runtime_text, encoding="utf-8")
    (root / "requirements-web.txt").write_text(web_text, encoding="utf-8")

    print("Wrote requirements.txt and requirements-web.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
