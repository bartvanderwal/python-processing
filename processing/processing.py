import os
import random as _random_module
import threading
import time
import pygame
from .core.constants import LEFT, RIGHT, CENTER, TOP, BOTTOM, BASELINE
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


_width = 800
_height = 500
_fps = 60
_title = "Sketch"
_window_icon = "icon.png"
_fullscreen_enabled = False

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
# Processing-achtige API
# --------------------

def _state():
    return globals()

def size(w, h):
    _system_api.size(_state(), _set_public_global, w, h)

def full_screen():
    _system_api.full_screen(_state(), pygame, _set_public_global)

def frame_rate(fps):
    _system_api.frame_rate(_state(), fps)

def title(t):
    _system_api.title(_state(), pygame, t)

def window_icon(path="icon.png"):
    """
    Stel het venster-icoon in. Standaard zoekt dit naar processing/icon.png.
    """
    _system_api.window_icon(_state(), _apply_window_icon, path)

def background(*args):
    _drawing_api.background(_state(), _require_screen, *args)

def rect(x, y, w, h):
    _drawing_api.rect(_state(), _require_screen, x, y, w, h)

def circle(x, y, d):
    _drawing_api.circle(_state(), _require_screen, x, y, d)

# additional primitives

def point(x, y):
    _drawing_api.point(_state(), _require_screen, x, y)

def line(x1, y1, x2, y2):
    _drawing_api.line(_state(), _require_screen, _apply_coords, x1, y1, x2, y2)

def triangle(x1, y1, x2, y2, x3, y3):
    _drawing_api.triangle(_state(), _require_screen, _apply_coords, x1, y1, x2, y2, x3, y3)

def quad(x1, y1, x2, y2, x3, y3, x4, y4):
    _drawing_api.quad(_state(), _require_screen, _apply_coords, x1, y1, x2, y2, x3, y3, x4, y4)

def ellipse(x, y, w, h):
    _drawing_api.ellipse(_state(), _require_screen, x, y, w, h)

# style functions

def fill(r, g=None, b=None):
    _style_api.fill(_state(), r, g, b)

def no_fill():
    _style_api.no_fill(_state())

def stroke(r, g=None, b=None):
    _style_api.stroke(_state(), r, g, b)

def no_stroke():
    _style_api.no_stroke(_state())

def stroke_weight(w):
    _style_api.stroke_weight(_state(), w)

# helpers for colors and text

def color(r, g=None, b=None, a=None):
    return _style_api.color(r, g, b, a)

def text_size(sz):
    _style_api.text_size(_state(), sz)

def text(txt, x, y):
    _drawing_api.text(_state(), _require_screen, _ensure_font, txt, x, y)

def text_align(align_x, align_y=None):
    _style_api.text_align(_state(), align_x, align_y)

def random(low=None, high=None):
    return _utils_api.random_value(low, high, _random_module)

def millis():
    return _utils_api.millis_value(_state(), pygame, time)

def nf(value, left=0, right=0):
    return _utils_api.nf_format(value, left, right)

def load_image(path):
    return _drawing_api.load_image(_state(), _resolve_icon_path, path)

def image(img, x, y, w=None, h=None):
    _drawing_api.image(_state(), _require_screen, _apply_coords, _resolve_icon_path, img, x, y, w, h)

def request_input(prompt="> "):
    """
    Start een asynchrone console input request.
    Returnt True als een nieuwe request gestart is, False als er al één pending is.
    """
    return _system_api.request_input(_input_manager, prompt)

def input_pending():
    return _system_api.input_pending(_input_manager)

def arc(x, y, w, h, start, stop):
    _drawing_api.arc(_state(), _require_screen, _apply_coords, x, y, w, h, start, stop)

def bezier(x1, y1, x2, y2, x3, y3, x4, y4, segments=20):
    _drawing_api.bezier(_state(), _require_screen, _apply_coords, x1, y1, x2, y2, x3, y3, x4, y4, segments)


# --------------------
# Helpers
# --------------------

def _ensure_font():
    _ensure_font_core(_state(), pygame)

def _apply_coords(vals):
    return tuple(int(v) for v in vals)

def _require_screen(func_name: str):
    _require_screen_core(_state(), func_name)

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
        mode,
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