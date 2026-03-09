import inspect


def set_public_global(state, name, value):
    state[name] = value
    sketch_globals = state.get("_sketch_globals")
    if sketch_globals is not None:
        sketch_globals[name] = value


def sync_public_globals_to_sketch(state, public_global_names):
    sketch_globals = state.get("_sketch_globals")
    if sketch_globals is None:
        return

    for name in public_global_names:
        sketch_globals[name] = state[name]


def make_sketch_from_caller(state, stack_index=2):
    caller_globals = inspect.stack()[stack_index].frame.f_globals
    state["_sketch_globals"] = caller_globals
    return type("Sketch", (object,), caller_globals)
