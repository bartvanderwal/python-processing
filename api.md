# API Reference

This document describes the public API exposed by `from processing import *`.

Notes:

- This project uses `snake_case` function and variable names.
- The API is inspired by Processing, with Python naming conventions.

## Structure

### `size(w, h)`
Set the sketch window size in pixels. The window is created immediately when called — even outside `setup()`, at the top level of your sketch. This allows drawing commands to follow directly without needing `setup()`. The new surface is initialized with the default background color (light gray, `(200, 200, 200)`).

### `full_screen()`

Switch the sketch window to fullscreen mode. Must be called before `run()`.

### `frame_rate(fps)`

Set the target frame rate for interactive mode.

### `run()`
Start the sketch loop.

Mode is auto-detected:
- interactive when `draw()` is defined
- static otherwise

Usage notes:
- Interactive mode: `run()` is required to start the frame loop and input callbacks.
- Static mode: `run()` is optional. Top-level drawing (outside `setup()`/`draw()`) works without it.

## Environment

### `title(t)`

Set the window title.

### `window_icon(path="icon.png")`

Set the window icon from an image file.

## Shape

### `background(gray)`

Fill the whole screen with a grayscale color.

### `background(r, g, b)`

Fill the whole screen with an RGB color.

Note: The window starts with a default light gray background `(200, 200, 200)`, matching Processing's default. Call `background()` in `draw()` to clear the canvas each frame; without it, drawing accumulates across frames.

### `rect(x, y, w, h)`

Draw a rectangle.

### `circle(x, y, d)`

Draw a circle using center `(x, y)` and diameter `d`.

### `ellipse(x, y, w, h)`

Draw an ellipse centered at `(x, y)`.

### `line(x1, y1, x2, y2)`

Draw a line segment.

### `point(x, y)`

Draw a single point.

### `triangle(x1, y1, x2, y2, x3, y3)`

Draw a triangle.

### `quad(x1, y1, x2, y2, x3, y3, x4, y4)`

Draw a quadrilateral.

### `arc(x, y, w, h, start, stop, mode=OPEN)`
Draw an arc over an ellipse defined by center and size.

Modes:
- `OPEN`: open curve (default)
- `CHORD`: closes endpoints with a straight line
- `PIE`: closes endpoints to center

### `bezier(x1, y1, x2, y2, x3, y3, x4, y4, segments=20)`

Draw a cubic Bezier curve.

## Color and Style

### `fill(r)`

Set grayscale fill color.

### `fill(r, g, b)`

Set RGB fill color.

### `no_fill()`

Disable fill.

### `stroke(r)`

Set grayscale stroke color.

### `stroke(r, g, b)`

Set RGB stroke color.

### `no_stroke()`

Disable stroke.

### `stroke_weight(w)`

Set stroke thickness.

### `color(r)`

Return grayscale color tuple `(r, r, r)`.

### `color(r, g, b)`

Return RGB color tuple.

### `color(r, g, b, a)`

Return RGBA color tuple.

## Typography

### `text_size(sz)`

Set text size.

### `text_align(align_x, align_y=None)`

Set text alignment.

Horizontal values:

- `LEFT`, `CENTER`, `RIGHT`

Vertical values:

- `TOP`, `CENTER`, `BOTTOM`, `BASELINE`

### `text(txt, x, y)`

Draw text at a position.

## Image

### `load_image(path)`

Load and return a `pygame.Surface` from disk.

### `image(img, x, y, w=None, h=None)`

Draw an image.

Arguments:

- `img`: a `pygame.Surface` or an image path string.
- `x, y`: target position.
- `w, h` (optional): scale image to width and height.

## Time and Math

### `millis()`

Return elapsed milliseconds since window initialization.

### `random(low=None, high=None)`

Return a random float.

Forms:

- `random()` -> `0.0 <= value < 1.0`
- `random(high)` -> `0.0 <= value < high`
- `random(low, high)` -> `low <= value < high` (uniform float)

### `nf(value, left=0, right=0)`

Format a number with zero-padded integer digits and fixed decimal digits.

Example:

- `nf(7.25, 4, 2)` -> `"0007.25"`

## Input

### `request_input(prompt="> ")`

Start asynchronous console input. Returns `True` if started, `False` if a request is already pending.

### `input_pending()`

Return `True` if an async console input request is pending.

## Public Constants

Alignment constants:

- `LEFT`
- `RIGHT`
- `CENTER`
- `TOP`
- `BOTTOM`
- `BASELINE`

Arc constants:
- `OPEN`
- `CHORD`
- `PIE`

Math constants:
- `PI`
- `TWO_PI`

Use these with `text_align(...)`.

## Public Global Variables

These variables are updated by the runtime loop:

### Window and display

- `width`
- `height`
- `display_width`
- `display_height`
- `pixel_width`
- `pixel_height`

### Runtime state

- `frame_count`
- `focused`

### Mouse state

- `mouse_x`
- `mouse_y`
- `pmouse_x`
- `pmouse_y`
- `is_mouse_pressed`
- `mouse_button`

### Keyboard state

- `key`
- `key_code`
- `is_key_pressed`

## User Callback Handlers (Optional)

Define any of these in your sketch file when needed:

- `setup()`
- `draw()`
- `key_pressed(key)`
- `key_released(key)`
- `key_typed(char)`
- `mouse_pressed(x, y, button)`
- `mouse_released(x, y, button)`
- `mouse_clicked(x, y, button)`
- `mouse_moved(x, y, dx, dy)`
- `mouse_dragged(x, y, dx, dy)`
- `mouse_wheel(dx, dy)`
- `input_received(text)`
- `input_error(err)`

## Minimal Example

```python
from processing import *

x = 0


def setup():
    size(800, 500)
    frame_rate(60)


def draw():
    global x
    background(245)
    fill(80, 170, 255)
    no_stroke()
    circle(x, 250, 40)
    x += 2


run()
```
