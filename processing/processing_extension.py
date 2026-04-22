"""Small pygame wrapper for sketches that use the local processing API.

This module intentionally exposes only the subset currently used by dino_game.py.
"""

import pygame as _pygame
import sys


def _resolve_pygame_int(names, default):
    for name in names:
        value = getattr(_pygame, name, None)
        if isinstance(value, int):
            return value

    for namespace in ("locals", "constants"):
        module = getattr(_pygame, namespace, None)
        if module is None:
            continue
        for name in names:
            value = getattr(module, name, None)
            if isinstance(value, int):
                return value

    return default


def _resolve_pygame_module(module_name):
    module = getattr(_pygame, module_name, None)
    if module is not None:
        return module
    full_name = "pygame" + "." + str(module_name)
    module = sys.modules.get(full_name)
    if module is not None:
        setattr(_pygame, module_name, module)
        return module
    raise AttributeError(f"pygame has no attribute {module_name!r}")


K_ESCAPE_VALUE = _resolve_pygame_int(("K_ESCAPE", "K_ESC"), 27)
K_LEFT_VALUE = _resolve_pygame_int(("K_LEFT",), 1073741904)
K_RIGHT_VALUE = _resolve_pygame_int(("K_RIGHT",), 1073741903)
K_UP_VALUE = _resolve_pygame_int(("K_UP",), 1073741906)
K_DOWN_VALUE = _resolve_pygame_int(("K_DOWN",), 1073741905)
K_C_VALUE = _resolve_pygame_int(("K_c", "K_C"), ord("c"))


class _TransformProxy:
    @staticmethod
    def flip(surface, x_bool, y_bool):
        return _resolve_pygame_module("transform").flip(surface, x_bool, y_bool)

    @staticmethod
    def smoothscale(surface, size):
        return _resolve_pygame_module("transform").smoothscale(surface, size)


class _MusicProxy:
    @staticmethod
    def stop():
        return _resolve_pygame_module("mixer").music.stop()

    @staticmethod
    def load(path):
        return _resolve_pygame_module("mixer").music.load(path)

    @staticmethod
    def set_volume(volume):
        return _resolve_pygame_module("mixer").music.set_volume(volume)

    @staticmethod
    def play(loops=0):
        return _resolve_pygame_module("mixer").music.play(loops)


class _MixerProxy:
    music = _MusicProxy()

    @staticmethod
    def get_init():
        return _resolve_pygame_module("mixer").get_init()

    @staticmethod
    def init(*args, **kwargs):
        return _resolve_pygame_module("mixer").init(*args, **kwargs)

    @staticmethod
    def Sound(*args, **kwargs):
        return _resolve_pygame_module("mixer").Sound(*args, **kwargs)


class _FontProxy:
    @staticmethod
    def SysFont(name, size, bold=False, italic=False):
        return _resolve_pygame_module("font").SysFont(name, size, bold=bold, italic=italic)


class _ImageProxy:
    @staticmethod
    def load(path):
        return _resolve_pygame_module("image").load(path)

    @staticmethod
    def save(surface, path):
        return _resolve_pygame_module("image").save(surface, path)


class _DisplayProxy:
    @staticmethod
    def get_surface():
        return _resolve_pygame_module("display").get_surface()


class _KeyProxy:
    @staticmethod
    def get_pressed():
        return _resolve_pygame_module("key").get_pressed()


class _PygameProxy:
    transform = _TransformProxy()
    mixer = _MixerProxy()
    font = _FontProxy()
    image = _ImageProxy()
    display = _DisplayProxy()
    key = _KeyProxy()

    K_ESCAPE = K_ESCAPE_VALUE
    K_LEFT = K_LEFT_VALUE
    K_RIGHT = K_RIGHT_VALUE
    K_UP = K_UP_VALUE
    K_DOWN = K_DOWN_VALUE
    K_c = K_C_VALUE

    @staticmethod
    def get_init():
        return _pygame.get_init()

    @staticmethod
    def quit():
        return _pygame.quit()


_pg_proxy = _PygameProxy()
pygame = _pg_proxy

# Optional direct imports for scripts that do not want `pygame.<...>` access.
transform = _pg_proxy.transform
mixer = _pg_proxy.mixer
font = _pg_proxy.font
image = _pg_proxy.image
display = _pg_proxy.display
key = _pg_proxy.key
K_ESCAPE = _pg_proxy.K_ESCAPE
K_LEFT = _pg_proxy.K_LEFT
K_RIGHT = _pg_proxy.K_RIGHT
K_UP = _pg_proxy.K_UP
K_DOWN = _pg_proxy.K_DOWN
K_c = _pg_proxy.K_c
get_init = _pg_proxy.get_init
quit = _pg_proxy.quit

__all__ = [
    "pygame",
    "transform",
    "mixer",
    "font",
    "image",
    "display",
    "key",
    "K_ESCAPE",
    "K_LEFT",
    "K_RIGHT",
    "K_UP",
    "K_DOWN",
    "K_c",
    "get_init",
    "quit",
]
