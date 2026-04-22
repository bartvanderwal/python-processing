"""Compatibility shim for importing the local pygame extension."""

from processing.processing_extension import (
    K_DOWN,
    K_ESCAPE,
    K_LEFT,
    K_RIGHT,
    K_UP,
    K_c,
    display,
    font,
    get_init,
    image,
    key,
    mixer,
    pygame,
    quit,
    transform,
)

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
