# ADR 004: Dev/Prod Runtime Parity For Loading And Asset Behavior

## Status

Accepted (2026-05-03).

## Context

The repository now targets both native Python/Pygame and web delivery through pygbag.

The project already values dev/prod parity in practice: local development should expose the same runtime behavior as the production web build wherever possible.

Cold boot time has become a concern, especially in the browser. The current game eagerly loads many images and sounds at import time or during early setup. Lazy loading is a plausible optimization, but it risks introducing environment-specific behavior if it is implemented only in the web template, bundling layer, or other build-specific code.

We want startup optimizations to remain testable locally and to preserve a single gameplay/runtime contract across desktop and web.

## Options

### Option A: Use web-only loading behavior

Implement lazy loading or staged loading only in the web build, template, or JavaScript glue.

### Option B: Keep fully eager loading everywhere

Avoid runtime loading changes and accept higher startup cost.

### Option C: Use shared Python-level loading behavior with runtime parity

Implement lazy loading, preloading, and asset caching in Python game code so desktop and web use the same loading semantics.

## Decision

Use Option C.

Runtime loading behavior must be defined in Python game code, not primarily in web-only template or packaging logic.

Working rules:

1. Asset path resolution and load timing should use the same Python code paths in desktop and web builds.
2. Web build tooling may package, mirror, or rewrite static delivery details, but must not introduce different gameplay or asset-loading semantics.
3. Lazy loading should happen via explicit Python helpers and caches.
4. Heavy assets should be loaded at deliberate transition points such as pre-boss scenes, shops, intros, or credits transitions rather than randomly during active gameplay.
5. New loading behavior should be locally testable without requiring a production web deployment.

## Consequences

### Positive

- Reduces the chance of prod-only or web-only loading bugs.
- Keeps local testing representative for load behavior.
- Preserves a single runtime contract for gameplay code.
- Makes gradual lazy loading possible without coupling game logic to build scripts.

### Negative

- Some aggressive web-only optimizations will be intentionally avoided.
- The game may need explicit preload or transition states for heavy assets.
- Startup improvements may require more deliberate asset lifecycle management in Python code.

## Sources

- [docs/sgb.md](../sgb.md)
- [AGENTS.md](../../../AGENTS.md)
- [scripts/web/build_web.sh](../../../scripts/web/build_web.sh)
- [dino_game.py](../../../dino_game.py)
- The Twelve-Factor App. (2017). *Dev/prod parity*. https://12factor.net/dev-prod-parity