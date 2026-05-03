# ADR 005: Semantic Versioning For The Game Application

## Status

Accepted (2026-05-03).

## Context

The project needs a clear application version that can be shown in the start menu and used to confirm which build is currently running.

That matters especially for deploy verification: when a feature or bugfix is tested locally and then deployed, we want to know whether production is actually serving the expected build version before spending time testing behavior on the live site.

The version number is therefore a build and deployment identity signal, not proof that a specific feature works correctly. Behavioral validation still requires testing the relevant gameplay logic.

The repository already has dependency version management in [requirements.txt](../../../requirements.txt), but dependency locking is not the same thing as application versioning.

We want a simple versioning approach that works for local desktop runs and web builds without requiring Python package publication.

## Options

### Option A: No explicit application version

Rely on Git commit hashes, branch names, or manual knowledge.

### Option B: Store application version in dependency or packaging metadata only

Use only `requirements.txt` or introduce packaging metadata solely to carry the game version.

### Option C: Use SemVer as explicit application metadata in the game codebase

Store a single application version in the repository and expose it in the runtime UI.

### Option D: Use WendtVer as a repository-specific alternative

Use a custom, repository-specific version naming scheme as a local alternative to SemVer.

In this ADR, `WendtVer` is used as an internal repository term. There is no canonical external specification for it.

## Decision

Use Option C.

The game uses Semantic Versioning (SemVer) as its standard application versioning scheme.

Option D (`WendtVer`) is noted as an explicit non-adopted alternative. It remains useful as a label for what we do not want: an ad hoc, repository-specific versioning scheme that weakens external clarity and interoperability.

Working rules:

1. The game version is application metadata, not dependency metadata.
2. `requirements.txt` remains dedicated to dependency locking and must not be used as the canonical application version source.
3. Introducing `pyproject.toml` is optional and not required for SemVer adoption in this repository.
4. A single Python-visible version value should exist so desktop and web builds present the same version string.
5. The version should be visible in the start menu and may also be reused in titles, logs, or diagnostics.
6. The version is used to confirm which build reached production, not to replace direct testing of feature behavior.

## Consequences

### Positive

- Makes it easier to confirm whether a deployment reached production with the expected build.
- Reduces wasted production testing when the wrong build is still live or a pipeline step failed.
- Keeps application versioning separate from dependency management.
- Works without converting the project into a packaged PyPI-style application.
- Preserves parity between local and web builds.

### Negative

- Version bumps become an explicit maintenance step.
- Additional discipline is needed to decide when changes are major, minor, or patch releases.

## Sources

- Semantic Versioning. (2024). *Semantic Versioning 2.0.0*. https://semver.org/
