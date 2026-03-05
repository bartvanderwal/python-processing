import inspect
import os
import queue
import threading
import pygame


_width = 800
_height = 500
_fps = 60
_title = "Sketch"
_window_icon = "icon.png"

_screen = None
_clock = None

# drawing state
_fill_enabled = True
_stroke_enabled = True
_fill_color = (255, 255, 255)
_stroke_color = (0, 0, 0)
_stroke_weight = 1
_text_size = 12
_font = None
_sketch_globals = None

# async console input state (explicit API: request_input + callbacks)
_input_events = queue.Queue()
_input_lock = threading.Lock()
_input_pending = False

# Public Processing-like globals
width = _width
height = _height
displayWidth = _width
displayHeight = _height
pixelWidth = _width
pixelHeight = _height
frameCount = 0
focused = False
mouseX = 0
mouseY = 0
pmouseX = 0
pmouseY = 0
mousePressed = False
mouseButton = None
key = None
keyCode = None
keyPressed = False


# --------------------
# Processing-achtige API
# --------------------

def size(w, h):
    global _width, _height
    _width, _height = int(w), int(h)
    _set_public_global("width", _width)
    _set_public_global("height", _height)
    _set_public_global("pixelWidth", _width)
    _set_public_global("pixelHeight", _height)

def frame_rate(fps):
    global _fps
    _fps = int(fps)

def title(t):
    global _title
    _title = str(t)

def window_icon(path="icon.png"):
    """
    Stel het venster-icoon in. Standaard zoekt dit naar processing/icon.png.
    """
    global _window_icon
    _window_icon = str(path)

    # If the window already exists, apply immediately as well.
    if _screen is not None:
        _apply_window_icon()

def background(*args):
    _require_screen("background")
    # grayscale or rgb overload
    if len(args) == 1:
        g = int(args[0])
        col = (g, g, g)
    elif len(args) == 3:
        col = tuple(int(v) for v in args)
    else:
        raise TypeError("background() takes 1 or 3 arguments")
    _screen.fill(col)

def rect(x, y, w, h):
    _require_screen("rect")
    x, y, w, h = map(int, (x, y, w, h))
    if _fill_enabled:
        pygame.draw.rect(_screen, _fill_color, (x, y, w, h), 0)
    if _stroke_enabled:
        pygame.draw.rect(_screen, _stroke_color, (x, y, w, h), int(_stroke_weight))

def circle(x, y, d):
    _require_screen("circle")
    x, y, d = int(x), int(y), int(d)
    radius = d // 2
    if _fill_enabled:
        pygame.draw.circle(_screen, _fill_color, (x, y), radius, 0)
    if _stroke_enabled:
        pygame.draw.circle(_screen, _stroke_color, (x, y), radius, int(_stroke_weight))

# additional primitives

def point(x, y):
    _require_screen("point")
    x, y = int(x), int(y)
    if _stroke_enabled:
        _screen.set_at((x, y), _stroke_color)

def line(x1, y1, x2, y2):
    _require_screen("line")
    pts = _apply_coords((x1, y1, x2, y2))
    if _stroke_enabled:
        pygame.draw.line(_screen, _stroke_color, pts[:2], pts[2:], int(_stroke_weight))

def triangle(x1, y1, x2, y2, x3, y3):
    _require_screen("triangle")
    pts = _apply_coords((x1, y1, x2, y2, x3, y3))
    if _fill_enabled:
        pygame.draw.polygon(_screen, _fill_color, [pts[0:2], pts[2:4], pts[4:6]])
    if _stroke_enabled:
        pygame.draw.polygon(_screen, _stroke_color, [pts[0:2], pts[2:4], pts[4:6]], int(_stroke_weight))

def quad(x1, y1, x2, y2, x3, y3, x4, y4):
    _require_screen("quad")
    pts = _apply_coords((x1, y1, x2, y2, x3, y3, x4, y4))
    pts_list = [pts[i:i+2] for i in range(0, 8, 2)]
    if _fill_enabled:
        pygame.draw.polygon(_screen, _fill_color, pts_list)
    if _stroke_enabled:
        pygame.draw.polygon(_screen, _stroke_color, pts_list, int(_stroke_weight))

def ellipse(x, y, w, h):
    _require_screen("ellipse")
    x, y, w, h = map(int, (x, y, w, h))
    rect = (x - w//2, y - h//2, w, h)
    if _fill_enabled:
        pygame.draw.ellipse(_screen, _fill_color, rect, 0)
    if _stroke_enabled:
        pygame.draw.ellipse(_screen, _stroke_color, rect, int(_stroke_weight))

# style functions

def fill(r, g=None, b=None):
    global _fill_enabled, _fill_color
    _fill_enabled = True
    if g is None:
        g = r
        _fill_color = (int(r), int(r), int(r))
    else:
        _fill_color = (int(r), int(g), int(b))

def noFill():
    global _fill_enabled
    _fill_enabled = False

def stroke(r, g=None, b=None):
    global _stroke_enabled, _stroke_color
    _stroke_enabled = True
    if g is None:
        g = r
        _stroke_color = (int(r), int(r), int(r))
    else:
        _stroke_color = (int(r), int(g), int(b))

def noStroke():
    global _stroke_enabled
    _stroke_enabled = False

def strokeWeight(w):
    global _stroke_weight
    _stroke_weight = int(w)

# helpers for colors and text

def color(r, g=None, b=None, a=None):
    if g is None:
        return (int(r), int(r), int(r))
    col = (int(r), int(g), int(b))
    if a is not None:
        col = (*col, int(a))
    return col

def textSize(sz):
    global _text_size, _font
    _text_size = int(sz)
    _font = None  # will recreate on next draw

def text(txt, x, y):
    _require_screen("text")
    _ensure_font()
    surf = _font.render(str(txt), True, _fill_color if _fill_enabled else _stroke_color)
    _screen.blit(surf, _apply_coords((x, y)))

def request_input(prompt="> "):
    """
    Start een asynchrone console input request.
    Returnt True als een nieuwe request gestart is, False als er al één pending is.
    """
    global _input_pending
    with _input_lock:
        if _input_pending:
            return False
        _input_pending = True

    thread = threading.Thread(target=_input_worker, args=(str(prompt),), daemon=True)
    thread.start()
    return True

def input_pending():
    with _input_lock:
        return _input_pending

def arc(x, y, w, h, start, stop):
    _require_screen("arc")
    rect = pygame.Rect(_apply_coords((x - w/2, y - h/2, w, h)))
    if _stroke_enabled:
        pygame.draw.arc(_screen, _stroke_color, rect, float(start), float(stop), int(_stroke_weight))

def bezier(x1, y1, x2, y2, x3, y3, x4, y4, segments=20):
    _require_screen("bezier")
    pts = _apply_coords((x1, y1, x2, y2, x3, y3, x4, y4))
    path = []
    for i in range(segments + 1):
        t = i / segments
        # cubic bezier formula
        x = ( (1-t)**3 * pts[0] + 3*(1-t)**2*t * pts[2] + 3*(1-t)*t**2 * pts[4] + t**3 * pts[6] )
        y = ( (1-t)**3 * pts[1] + 3*(1-t)**2*t * pts[3] + 3*(1-t)*t**2 * pts[5] + t**3 * pts[7] )
        path.append((int(x), int(y)))
    if _stroke_enabled and len(path) > 1:
        pygame.draw.lines(_screen, _stroke_color, False, path, int(_stroke_weight))


# --------------------
# Helpers
# --------------------

def _ensure_font():
    global _font
    if _font is None:
        _font = pygame.font.SysFont(None, _text_size)

def _apply_coords(vals):
    return tuple(int(v) for v in vals)

def _require_screen(func_name: str):
    if _screen is None:
        raise RuntimeError(
            f"{func_name}() called before the window exists. "
            f"Call run() after your drawing code (or draw inside setup()/draw())."
        )

def _set_public_global(name, value):
    globals()[name] = value
    if _sketch_globals is not None:
        _sketch_globals[name] = value

def _sync_public_globals_to_sketch():
    if _sketch_globals is None:
        return
    for name in (
        "width", "height", "displayWidth", "displayHeight", "pixelWidth", "pixelHeight",
        "frameCount", "focused", "mouseX", "mouseY", "pmouseX", "pmouseY",
        "mousePressed", "mouseButton", "key", "keyCode", "keyPressed"
    ):
        _sketch_globals[name] = globals()[name]

def _invoke_handler(sketch, name, *args):
    if not hasattr(sketch, name):
        return

    handler = getattr(sketch, name)
    sig = inspect.signature(handler)
    params = list(sig.parameters.values())
    has_varargs = any(p.kind == inspect.Parameter.VAR_POSITIONAL for p in params)

    if has_varargs:
        handler(*args)
        return

    positional = [
        p for p in params
        if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    ]

    if not positional:
        handler()
    else:
        handler(*args[:len(positional)])

def _input_worker(prompt):
    global _input_pending
    try:
        text_line = input(prompt)
        _input_events.put(("received", text_line))
    except EOFError as err:
        _input_events.put(("error", err))
    except Exception as err:
        _input_events.put(("error", err))
    finally:
        with _input_lock:
            _input_pending = False

def _dispatch_input_events(sketch):
    while True:
        try:
            kind, payload = _input_events.get_nowait()
        except queue.Empty:
            break

        if kind == "received":
            _invoke_handler(sketch, "input_received", payload)
        elif kind == "error":
            _invoke_handler(sketch, "input_error", payload)

def _resolve_icon_path(path):
    if os.path.isabs(path):
        return path

    # Try caller working directory first, then processing package directory.
    if os.path.exists(path):
        return path

    pkg_path = os.path.join(os.path.dirname(__file__), path)
    if os.path.exists(pkg_path):
        return pkg_path

    return path

def _apply_window_icon():
    resolved = _resolve_icon_path(_window_icon)
    try:
        icon_surface = pygame.image.load(resolved)
        pygame.display.set_icon(icon_surface)
    except Exception:
        # Keep startup robust if icon path is invalid or image can't be loaded.
        pass

def _make_sketch_from_caller():
    global _sketch_globals
    caller_globals = inspect.stack()[2].frame.f_globals
    _sketch_globals = caller_globals
    return type("Sketch", (object,), caller_globals)

def _init_window():
    global _screen, _clock
    pygame.init()
    pygame.font.init()
    info = pygame.display.Info()
    _set_public_global("displayWidth", int(info.current_w))
    _set_public_global("displayHeight", int(info.current_h))
    _screen = pygame.display.set_mode((_width, _height))
    _apply_window_icon()
    pygame.display.set_caption(_title)
    _clock = pygame.time.Clock()
    _set_public_global("width", _width)
    _set_public_global("height", _height)
    _set_public_global("pixelWidth", _width)
    _set_public_global("pixelHeight", _height)
    _set_public_global("focused", True)

def _shutdown():
    pygame.quit()


# --------------------
# Modes
# --------------------

def run(mode=None):
    """
    Processing-achtige runner met 2 modes:

    1) Static mode (default als er GEEN draw() is):
       - Je tekent direct (top-level) of in setup()
       - Geen animatieloop
       - Window blijft open tot sluiten

    2) Interactive mode (default als er draw() is):
       - Vereist: setup() én draw()
       - draw() wordt ~fps keer per seconde aangeroepen
             - Optionele handlers:
                 key_pressed(key), key_released(key), key_typed(char),
                 mouse_pressed(x, y, button), mouse_released(x, y, button),
                 mouse_clicked(x, y, button), mouse_moved(x, y, dx, dy),
                 mouse_dragged(x, y, dx, dy), mouse_wheel(dx, dy),
                 input_received(text), input_error(err)

    Je kunt mode forceren met mode="static" of mode="interactive".
    """
    sketch = _make_sketch_from_caller()
    _sync_public_globals_to_sketch()

    has_setup = hasattr(sketch, "setup")
    has_draw = hasattr(sketch, "draw")

    if mode is None:
        mode = "interactive" if has_draw else "static"
    else:
        mode = mode.lower().strip()

    if mode not in ("static", "interactive"):
        raise ValueError('mode must be None, "static", or "interactive"')

    _init_window()

    try:
        if mode == "interactive":
            # minimaal vereist
            if not has_setup or not has_draw:
                raise RuntimeError(
                    "Interactive mode requires both setup() and draw(). "
                    "Either define them, or remove draw() to use static mode."
                )

            # setup één keer
            sketch.setup()
            pygame.key.start_text_input()
            current_mouse_x, current_mouse_y = pygame.mouse.get_pos()
            _set_public_global("mouseX", int(current_mouse_x))
            _set_public_global("mouseY", int(current_mouse_y))
            _set_public_global("pmouseX", int(current_mouse_x))
            _set_public_global("pmouseY", int(current_mouse_y))

            # loop
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == getattr(pygame, "WINDOWFOCUSGAINED", -1):
                        _set_public_global("focused", True)
                    elif event.type == getattr(pygame, "WINDOWFOCUSLOST", -1):
                        _set_public_global("focused", False)
                    elif event.type == pygame.KEYDOWN:
                        key_value = event.unicode if getattr(event, "unicode", "") else event.key
                        _set_public_global("key", key_value)
                        _set_public_global("keyCode", event.key)
                        _set_public_global("keyPressed", True)
                        _invoke_handler(sketch, "key_pressed", event.key)
                    elif event.type == pygame.KEYUP:
                        key_value = event.unicode if getattr(event, "unicode", "") else event.key
                        _set_public_global("key", key_value)
                        _set_public_global("keyCode", event.key)
                        _set_public_global("keyPressed", False)
                        _invoke_handler(sketch, "key_released", event.key)
                    elif event.type == pygame.TEXTINPUT:
                        _set_public_global("key", event.text)
                        _invoke_handler(sketch, "key_typed", event.text)
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        _set_public_global("pmouseX", mouseX)
                        _set_public_global("pmouseY", mouseY)
                        _set_public_global("mouseX", event.pos[0])
                        _set_public_global("mouseY", event.pos[1])
                        _set_public_global("mousePressed", True)
                        _set_public_global("mouseButton", event.button)
                        _invoke_handler(sketch, "mouse_pressed", event.pos[0], event.pos[1], event.button)
                    elif event.type == pygame.MOUSEBUTTONUP:
                        _set_public_global("pmouseX", mouseX)
                        _set_public_global("pmouseY", mouseY)
                        _set_public_global("mouseX", event.pos[0])
                        _set_public_global("mouseY", event.pos[1])
                        _set_public_global("mousePressed", False)
                        _set_public_global("mouseButton", event.button)
                        _invoke_handler(sketch, "mouse_released", event.pos[0], event.pos[1], event.button)
                        _invoke_handler(sketch, "mouse_clicked", event.pos[0], event.pos[1], event.button)
                    elif event.type == pygame.MOUSEMOTION:
                        _set_public_global("pmouseX", mouseX)
                        _set_public_global("pmouseY", mouseY)
                        _set_public_global("mouseX", event.pos[0])
                        _set_public_global("mouseY", event.pos[1])
                        if any(event.buttons):
                            _set_public_global("mousePressed", True)
                            _invoke_handler(sketch, "mouse_dragged", event.pos[0], event.pos[1], event.rel[0], event.rel[1])
                        else:
                            _set_public_global("mousePressed", False)
                            _invoke_handler(sketch, "mouse_moved", event.pos[0], event.pos[1], event.rel[0], event.rel[1])
                    elif event.type == pygame.MOUSEWHEEL:
                        _invoke_handler(sketch, "mouse_wheel", event.x, event.y)

                _dispatch_input_events(sketch)
                _set_public_global("frameCount", frameCount + 1)
                sketch.draw()

                pygame.display.flip()
                _clock.tick(_fps)

        else:  # static
            # In static mode mag setup() bestaan, draw() wordt genegeerd
            if has_setup:
                sketch.setup()

            # 1 frame renderen
            pygame.display.flip()

            # window openhouden
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == getattr(pygame, "WINDOWFOCUSGAINED", -1):
                        _set_public_global("focused", True)
                    elif event.type == getattr(pygame, "WINDOWFOCUSLOST", -1):
                        _set_public_global("focused", False)

                _dispatch_input_events(sketch)
                _clock.tick(30)

    finally:
        if mode == "interactive":
            pygame.key.stop_text_input()
        _shutdown()