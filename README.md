# Python Processing Starter voor Dino Game

In deze GitHub fork van de repo van collega ICT docent Jorg Jansen heb ik een dino game gemaakt. Hieronder de originele inhoud van README.md, maar deze game start ik met

```console
python3 dino_game.py
```

Op Windows zou gewoon dit moeten werken:

```bash
python dino_game.py
```

Uitgaande dat [Python 3](https://www.python.org/downloads/windows/) is geinstalleerd en op/in command line/PATH staat.

## Projectdocumentatie

Voor ontwerpkeuzes, spelregels en structurele principes, zie [docs/sgb.md](docs/sgb.md).

## Snelle Start Met Virtual Environment

### macOS / Linux

```bash
scripts/setup_venv.sh
scripts/run_dino.sh
```

`scripts/setup_venv.sh` installs from hash-locked requirements and supports Python 3.12+.

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python dino_game.py
```

### Handmatig activeren (optioneel)

```bash
source .venv/bin/activate
python dino_game.py
```

### IDE gebruik

Je kunt ook een IDE zoals [Thonny](https://thonny.org/) gebruiken.

- Installeer daarin `pygame-ce` via de package manager, of gebruik de bestaande virtual environment van dit project.
- Zorg dat de map `processing` beschikbaar is naast je programma, of in de gebruikte `site-packages`.
- Voor deze repo is de veiligste route op macOS/Linux meestal gewoon `scripts/setup_venv.sh` en daarna draaien vanuit die omgeving.

### Flake8 handmatig draaien

Als VS Code alleen toastmeldingen geeft, kun je Flake8 handmatig in de terminal draaien voor een volledig overzicht:

```bash
source .venv/bin/activate
python -m flake8 dino_game.py
```

Voor de hele repository:

```bash
source .venv/bin/activate
python -m flake8 .
```

Als je melding krijgt als `No module named flake8`, installeer Flake8 dan eerst in de actieve virtual environment:

```bash
source .venv/bin/activate
python -m pip install flake8
```

## Original Intro and README

This project provides a small Processing-like API on top of Pygame, using Python-style naming.
It is designed for quick visual programming, classroom demos, and beginner-friendly sketch workflows.

## Project Goal

The goal is to let you write simple sketches with minimal setup:

- define `setup()` for one-time initialization
- define `draw()` for frame-by-frame rendering
- call `run()` to start the sketch loop

You can use functions like `size()`, `background()`, `circle()`, `text()`, `image()`, and input callbacks.

## Preparation

1. Have Python!
2. Create a virtual environment
3. Install dependencies from `requirements.txt`

Dependency installs are hash-locked and use a single index policy (see `scripts/security/README.md`).

## Create Your First Sketch

Create a file like `my_sketch.py`:

```python
from processing import *

x = 0


def setup():
    size(800, 500)
    frame_rate(60)
    title("My First Sketch")


def draw():
    global x
    background(245)
    fill(80, 170, 255)
    no_stroke()
    circle(x, 250, 40)
    x = (x + 2) % width


run()
```

Run it with:

```powershell
python my_sketch.py
```

## API Documentation

See `api.md` for the full English API reference, including:

- public constants
- public runtime variables
- public functions
- optional callback handlers

## Notes

- Function and variable names follow `snake_case`.
- ESC closes the sketch window.
- The runtime supports both static and interactive sketch modes.

## WebAssembly Build (pygbag)

You can package `dino_game.py` for the browser (WASM) and embed it in a blog post.
This uses a separate web build environment: `.venv-web`.
The build script allows non-OGG audio files, because this project currently contains `.wav/.mp3/.m4a`.

### 1) Setup once

```bash
scripts/web/setup_web.sh
```

Web dependencies are installed from `requirements-web.txt` (hash-locked).

### 2) Build web version

```bash
scripts/web/build_web.sh
```

Output is copied to:

```text
.web-build/output/
```

### 3) Run local preview

```bash
scripts/web/run_web.sh
```

Then open:

```text
http://127.0.0.1:9000
```

The build script mirrors the required pygbag runtime/package files into
`.web-build/output/cdn/` by default (`LOCAL_CDN=1`), so preview and deploy do
not depend on remote CDN CORS behavior.

### 4) Deploy to GitHub Pages

A workflow is included at:

```text
.github/workflows/deploy-pages.yml
```

It builds `dino_game.py` as a web app and publishes `.web-build/output/` to
GitHub Pages on pushes to `main` (and on manual dispatch).

### Blog embed idea

Host the generated `.web-build/output/` files on your site and embed with an iframe:

```html
<iframe
  src="https://bartvanderwal.nl/path-to-game/index.html"
  width="960"
  height="600"
  style="border:0;"
  loading="lazy"
  allowfullscreen
></iframe>
```

![alt text](assets/macbook.png)
