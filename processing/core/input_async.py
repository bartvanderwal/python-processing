import builtins
from collections import deque
import threading


class AsyncInputManager:
    def __init__(self):
        self._input_events = deque()
        self._events_lock = threading.Lock()
        self._input_lock = threading.Lock()
        self._input_pending = False
        self._input_patch_active = False
        self._original_input = builtins.input

    def request_input(self, prompt="> "):
        with self._input_lock:
            if self._input_pending:
                return False
            self._input_pending = True

        thread = threading.Thread(target=self._input_worker, args=(str(prompt),), daemon=True)
        thread.start()
        return True

    def input_pending(self):
        with self._input_lock:
            return self._input_pending

    def dispatch_events(self, sketch, invoke_handler):
        while True:
            with self._events_lock:
                if not self._input_events:
                    break
                kind, payload = self._input_events.popleft()

            if kind == "received":
                invoke_handler(sketch, "input_received", payload)
            elif kind == "error":
                invoke_handler(sketch, "input_error", payload)

    def patch_input_guard(self, draw_call_depth_getter, run_thread_getter):
        if self._input_patch_active:
            return

        def guarded_input(*args, **kwargs):
            if draw_call_depth_getter() > 0 and threading.current_thread() is run_thread_getter():
                raise RuntimeError(
                    "input() is not allowed inside draw() because it blocks rendering. "
                    "Use request_input(prompt) with input_received(text) instead."
                )
            return self._original_input(*args, **kwargs)

        builtins.input = guarded_input
        self._input_patch_active = True

    def restore_input_guard(self):
        if not self._input_patch_active:
            return
        builtins.input = self._original_input
        self._input_patch_active = False

    def _input_worker(self, prompt):
        try:
            text_line = input(prompt)
            with self._events_lock:
                self._input_events.append(("received", text_line))
        except EOFError as err:
            with self._events_lock:
                self._input_events.append(("error", err))
        except Exception as err:
            with self._events_lock:
                self._input_events.append(("error", err))
        finally:
            with self._input_lock:
                self._input_pending = False
