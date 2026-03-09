def require_screen(state, func_name):
    if state.get("_screen") is None:
        raise RuntimeError(
            f"{func_name}() called before the window exists. "
            f"Call run() after your drawing code (or draw inside setup()/draw())."
        )
