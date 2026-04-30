import os
import sys
import traceback


def _log_window_exception(context, exc, *, once_key=None):
    if not hasattr(_log_window_exception, "_seen_keys"):
        _log_window_exception._seen_keys = set()
    if once_key is not None:
        if once_key in _log_window_exception._seen_keys:
            return
        _log_window_exception._seen_keys.add(once_key)
    print(f"[window] {context}: {exc.__class__.__name__}: {exc}", file=sys.stderr)
    traceback.print_exception(type(exc), exc, exc.__traceback__)


def _require_pygame_submodule(pygame, name):
    module = getattr(pygame, name, None)
    if module is not None:
        return module
    module = sys.modules.get("pygame" + "." + name)
    if module is not None:
        setattr(pygame, name, module)
        return module
    raise AttributeError(f"pygame has no attribute {name!r}")


def resolve_icon_path(base_dir, path):
    if os.path.isabs(path):
        return path

    if os.path.exists(path):
        return path

    pkg_path = os.path.join(base_dir, path)
    if os.path.exists(pkg_path):
        return pkg_path

    return path


def apply_window_icon(state, pygame, base_dir):
    resolved = resolve_icon_path(base_dir, state["_window_icon"])
    try:
        image = _require_pygame_submodule(pygame, "image")
        display = _require_pygame_submodule(pygame, "display")
        icon_surface = image.load(resolved)
        display.set_icon(icon_surface)
    except Exception as exc:
        _log_window_exception(
            f"Failed to apply window icon '{resolved}'",
            exc,
            once_key=f"window_icon:{resolved}",
        )
        # Keep startup robust if icon path is invalid or image can't be loaded.


def init_window(state, pygame, set_public_global, apply_window_icon_func):
    if state.get("_screen") is not None:
        return
    pygame.init()
    print("and hello from python-processing. https://github.com/AIM-HBO-ICT-Voorlichting/python-processing")
    pygame.font.init()
    info = pygame.display.Info()
    set_public_global("display_width", int(info.current_w))
    set_public_global("display_height", int(info.current_h))

    flags = 0
    if state["_fullscreen_enabled"]:
        state["_width"], state["_height"] = int(info.current_w), int(info.current_h)
        flags = pygame.FULLSCREEN

    state["_screen"] = pygame.display.set_mode((state["_width"], state["_height"]), flags)
    state["_millis_start"] = pygame.time.get_ticks()
    apply_window_icon_func()
    pygame.display.set_caption(state["_title"])
    state["_clock"] = pygame.time.Clock()

    # Set default background to light gray (Processing default)
    state["_screen"].fill((200, 200, 200))

    set_public_global("width", state["_width"])
    set_public_global("height", state["_height"])
    set_public_global("pixel_width", state["_width"])
    set_public_global("pixel_height", state["_height"])
    set_public_global("focused", True)
