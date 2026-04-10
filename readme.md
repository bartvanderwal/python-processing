# Python Processing Starter

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
2. Install Pygame using pip: `pip install pygame`
3. Copy the folder processing to your program's folder or to `/Lib/site-packages`

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
