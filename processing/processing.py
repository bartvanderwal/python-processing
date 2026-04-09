import atexit
import inspect
import os
import random as _random_module
import sys
import threading
import time
import pygame
from .core.constants import LEFT, RIGHT, CENTER, TOP, BOTTOM, BASELINE, OPEN, CHORD, PIE, PI, TWO_PI
from .core.public_globals import PUBLIC_GLOBAL_NAMES
from .core.dispatch import invoke_handler
from .core.input_async import AsyncInputManager
from .core.runtime import run_app
from .core.window import resolve_icon_path as _resolve_icon_path_core
from .core.window import apply_window_icon as _apply_window_icon_core
from .core.window import init_window as _init_window_core
from .core.fonts import ensure_font as _ensure_font_core
from .core.sketch import set_public_global as _set_public_global_core
from .core.sketch import sync_public_globals_to_sketch as _sync_public_globals_to_sketch_core
from .core.sketch import make_sketch_from_caller as _make_sketch_from_caller_core
from .core.guards import require_screen as _require_screen_core
from .api import drawing as _drawing_api
from .api import style as _style_api
from .api import system as _system_api
from .api import utils as _utils_api


_width = 400
_height = 400
_fps = 60
_title = "Sketch"
_window_icon = "icon.png"
_fullscreen_enabled = False
_run_called = False
_auto_run_profile_armed = False
_auto_run_target_code = None
_auto_run_prev_trace = None

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
_text_align_x = LEFT
_text_align_y = TOP
_sketch_globals = None
_millis_start = None

# async console input state (explicit API: request_input + callbacks)
_input_manager = AsyncInputManager()
_draw_call_depth = 0
_run_thread = None

# Public Processing-like globals
width = _width
height = _height
display_width = _width
display_height = _height
pixel_width = _width
pixel_height = _height
frame_count = 0
focused = False
mouse_x = 0
mouse_y = 0
pmouse_x = 0
pmouse_y = 0
is_mouse_pressed = False
mouse_button = None
key = None
key_code = None
is_key_pressed = False


# --------------------
# Processing-like API
# --------------------

def _state():
    return globals()

def size(w, h):
    """Set the sketch window size in pixels."""
    _system_api.size(_state(), pygame, _set_public_global, w, h)
    if _screen is None:
        _init_window()
    _arm_auto_static_run()

def full_screen():
    """Switch the sketch window to fullscreen mode."""
    _system_api.full_screen(_state(), pygame, _set_public_global)

def frame_rate(fps):
    """Set the target frame rate for interactive mode."""
    _system_api.frame_rate(_state(), fps)

def title(t):
    """Set the window title."""
    _system_api.title(_state(), pygame, t)

def window_icon(path="icon.png"):
    """
    Set the window icon. By default this looks for processing/icon.png.
    """
    _system_api.window_icon(_state(), _apply_window_icon, path)

def background(*args):
    """Clear the screen with a grayscale or RGB color."""
    _drawing_api.background(_state(), _require_screen, *args)

def rect(x, y, w, h):
    """Draw a rectangle."""
    _drawing_api.rect(_state(), _require_screen, x, y, w, h)

def circle(x, y, d):
    """Draw a circle using center and diameter."""
    _drawing_api.circle(_state(), _require_screen, x, y, d)

# additional primitives

def point(x, y):
    """Draw a single point."""
    _drawing_api.point(_state(), _require_screen, x, y)

def line(x1, y1, x2, y2):
    """Draw a line segment between two points."""
    _drawing_api.line(_state(), _require_screen, _apply_coords, x1, y1, x2, y2)

def triangle(x1, y1, x2, y2, x3, y3):
    """Draw a triangle from three vertices."""
    _drawing_api.triangle(_state(), _require_screen, _apply_coords, x1, y1, x2, y2, x3, y3)

def quad(x1, y1, x2, y2, x3, y3, x4, y4):
    """Draw a quadrilateral from four vertices."""
    _drawing_api.quad(_state(), _require_screen, _apply_coords, x1, y1, x2, y2, x3, y3, x4, y4)

def ellipse(x, y, w, h):
    """Draw an ellipse centered at x,y."""
    _drawing_api.ellipse(_state(), _require_screen, x, y, w, h)

# style functions

def fill(r, g=None, b=None):
    """Set the fill color."""
    _style_api.fill(_state(), r, g, b)

def no_fill():
    """Disable fill for subsequent shapes."""
    _style_api.no_fill(_state())

def stroke(r, g=None, b=None):
    """Set the stroke color."""
    _style_api.stroke(_state(), r, g, b)

def no_stroke():
    """Disable stroke for subsequent shapes."""
    _style_api.no_stroke(_state())

def stroke_weight(w):
    """Set the stroke thickness."""
    _style_api.stroke_weight(_state(), w)

# helpers for colors and text

def color(r, g=None, b=None, a=None):
    """Create a color tuple."""
    return _style_api.color(r, g, b, a)

def text_size(sz):
    """Set the text size."""
    _style_api.text_size(_state(), sz)

def text(txt, x, y):
    """Draw text at the given position."""
    _drawing_api.text(_state(), _require_screen, _ensure_font, txt, x, y)

def text_align(align_x, align_y=None):
    """Set horizontal and optional vertical text alignment."""
    _style_api.text_align(_state(), align_x, align_y)

def random(low=None, high=None):
    """Return a random float in the requested range."""
    return _utils_api.random_value(low, high, _random_module)

def millis():
    """Return elapsed milliseconds since window initialization."""
    return _utils_api.millis_value(_state(), pygame, time)

def nf(value, left=0, right=0):
    """Format a number with zero-padded digits."""
    return _utils_api.nf_format(value, left, right)

def load_image(path):
    """Load and return an image surface from disk."""
    return _drawing_api.load_image(_state(), _resolve_icon_path, path)

def image(img, x, y, w=None, h=None):
    """Draw an image, optionally scaled to width and height."""
    _drawing_api.image(_state(), _require_screen, _apply_coords, _resolve_icon_path, img, x, y, w, h)

def request_input(prompt="> "):
    """
    Start an asynchronous console input request.
    Returns True when a new request is started, False when one is already pending.
    """
    return _system_api.request_input(_input_manager, prompt)

def input_pending():
    """Return whether an async input request is currently pending."""
    return _system_api.input_pending(_input_manager)

def arc(x, y, w, h, start, stop, mode=OPEN):
    """Draw an arc on an ellipse defined by center and size."""
    _drawing_api.arc(_state(), _require_screen, _apply_coords, x, y, w, h, start, stop, mode)

def bezier(x1, y1, x2, y2, x3, y3, x4, y4, segments=20):
    """Draw a cubic bezier curve."""
    _drawing_api.bezier(_state(), _require_screen, _apply_coords, x1, y1, x2, y2, x3, y3, x4, y4, segments)


# --------------------
# Helpers
# --------------------

def _ensure_font():
    _ensure_font_core(_state(), pygame)

def _apply_coords(vals):
    return tuple(int(v) for v in vals)

def _require_screen(func_name: str):
    if _screen is None:
        _init_window()
    _arm_auto_static_run()

def _set_public_global(name, value):
    _set_public_global_core(_state(), name, value)

def _sync_public_globals_to_sketch():
    _sync_public_globals_to_sketch_core(_state(), PUBLIC_GLOBAL_NAMES)

def _resolve_icon_path(path):
    return _resolve_icon_path_core(os.path.dirname(__file__), path)

def _apply_window_icon():
    _apply_window_icon_core(_state(), pygame, os.path.dirname(__file__))

def _make_sketch_from_caller():
    # Stack depth increased after extraction into core helper.
    return _make_sketch_from_caller_core(_state(), stack_index=3)

def _init_window():
    _init_window_core(_state(), pygame, _set_public_global, _apply_window_icon)

def _shutdown():
    pygame.quit()


def _arm_auto_static_run():
    global _auto_run_profile_armed, _auto_run_target_code, _auto_run_prev_trace

    if _run_called or _auto_run_profile_armed:
        return

    frame = inspect.currentframe()
    target_frame = None
    while frame is not None:
        if frame.f_globals.get("__name__") == "__main__":
            _auto_run_target_code = frame.f_code
            target_frame = frame
            break
        frame = frame.f_back

    if _auto_run_target_code is None:
        return

    _auto_run_prev_trace = sys.gettrace()

    def _auto_run_trace(frame, event, arg):
        if _auto_run_prev_trace is not None:
            _auto_run_prev_trace(frame, event, arg)

        if (
            _auto_run_profile_armed
            and not _run_called
            and event == "return"
            and frame.f_code is _auto_run_target_code
        ):
            _disarm_auto_static_profile()
            _maybe_auto_run()

        return _auto_run_trace

    _auto_run_profile_armed = True
    if target_frame is not None:
        target_frame.f_trace = _auto_run_trace
    sys.settrace(_auto_run_trace)


def _disarm_auto_static_profile():
    global _auto_run_profile_armed, _auto_run_target_code, _auto_run_prev_trace

    if _auto_run_profile_armed:
        sys.settrace(_auto_run_prev_trace)

    _auto_run_profile_armed = False
    _auto_run_target_code = None
    _auto_run_prev_trace = None


# --------------------
# Modes
# --------------------

def run():
    """Start the sketch loop in auto mode (interactive if draw() exists, else static)."""
    global _run_called
    _run_called = True
    _disarm_auto_static_profile()
    sketch = _make_sketch_from_caller()
    _sync_public_globals_to_sketch()

    global _run_thread, _draw_call_depth
    _run_thread = threading.current_thread()
    _draw_call_depth = 0

    def _get_public_global(name):
        return globals()[name]

    def _begin_draw():
        global _draw_call_depth
        _draw_call_depth += 1

    def _end_draw():
        global _draw_call_depth
        _draw_call_depth -= 1

    run_app(
        None,
        sketch,
        pygame=pygame,
        init_window=_init_window,
        patch_input_guard=lambda: _input_manager.patch_input_guard(lambda: _draw_call_depth, lambda: _run_thread),
        restore_input_guard=_input_manager.restore_input_guard,
        dispatch_input_events=lambda s: _input_manager.dispatch_events(s, invoke_handler),
        invoke_handler=invoke_handler,
        set_public_global=_set_public_global,
        get_public_global=_get_public_global,
        begin_draw=_begin_draw,
        end_draw=_end_draw,
        call_draw=lambda s: s.draw(),
        tick=lambda hz: _clock.tick(hz),
        fps_getter=lambda: _fps,
        shutdown=_shutdown,
    )


def _maybe_auto_run():
    global _screen
    if _screen is None or _run_called:
        return

    _disarm_auto_static_profile()

    # Keep static auto-run responsive in IDEs (e.g. Thonny) by yielding each frame.
    clock = pygame.time.Clock()
    pygame.display.flip()
    running = True
    while running:
        event = pygame.event.wait(33)
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        # Drain remaining queued events so window controls stay responsive.
        for queued in pygame.event.get():
            if queued.type == pygame.QUIT:
                running = False
            elif queued.type == pygame.KEYDOWN and queued.key == pygame.K_ESCAPE:
                running = False

        clock.tick(30)

    pygame.quit()
    _screen = None

atexit.register(_maybe_auto_run)