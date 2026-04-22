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

## Snelle Start Met Virtual Environment

### macOS / Linux

```bash
scripts/setup_venv.sh
scripts/run_dino.sh
```

`scripts/setup_venv.sh` prefers Python 3.13/3.12 and avoids Python 3.14, because some 3.14 pygame builds only support BMP images.

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
