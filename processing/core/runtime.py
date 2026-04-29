import asyncio


def run_app(
    mode,
    sketch,
    *,
    pygame,
    init_window,
    patch_input_guard,
    restore_input_guard,
    dispatch_input_events,
    invoke_handler,
    set_public_global,
    get_public_global,
    begin_draw,
    end_draw,
    call_draw,
    tick,
    fps_getter,
    shutdown,
):
    has_setup = hasattr(sketch, "setup")
    has_draw = hasattr(sketch, "draw")

    if mode is None:
        mode = "interactive" if has_draw else "static"
    else:
        mode = mode.lower().strip()

    if mode not in ("static", "interactive"):
        raise ValueError('mode must be None, "static", or "interactive"')

    init_window()
    patch_input_guard()

    try:
        if mode == "interactive":
            if not has_setup or not has_draw:
                raise RuntimeError(
                    "Interactive mode requires both setup() and draw(). "
                    "Either define them, or remove draw() to use static mode."
                )

            sketch.setup()
            pygame.key.start_text_input()

            current_mouse_x, current_mouse_y = pygame.mouse.get_pos()
            set_public_global("mouse_x", int(current_mouse_x))
            set_public_global("mouse_y", int(current_mouse_y))
            set_public_global("pmouse_x", int(current_mouse_x))
            set_public_global("pmouse_y", int(current_mouse_y))

            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == getattr(pygame, "WINDOWFOCUSGAINED", -1):
                        set_public_global("focused", True)
                    elif event.type == getattr(pygame, "WINDOWFOCUSLOST", -1):
                        set_public_global("focused", False)
                    elif event.type == pygame.KEYDOWN:
                        key_value = event.unicode if getattr(event, "unicode", "") else event.key
                        set_public_global("key", key_value)
                        set_public_global("key_code", event.key)
                        set_public_global("is_key_pressed", True)
                        invoke_handler(sketch, "key_pressed", event.key)
                        if event.key == pygame.K_ESCAPE:
                            running = False
                    elif event.type == pygame.KEYUP:
                        key_value = event.unicode if getattr(event, "unicode", "") else event.key
                        set_public_global("key", key_value)
                        set_public_global("key_code", event.key)
                        set_public_global("is_key_pressed", False)
                        invoke_handler(sketch, "key_released", event.key)
                    elif event.type == pygame.TEXTINPUT:
                        set_public_global("key", event.text)
                        invoke_handler(sketch, "key_typed", event.text)
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        set_public_global("pmouse_x", get_public_global("mouse_x"))
                        set_public_global("pmouse_y", get_public_global("mouse_y"))
                        set_public_global("mouse_x", event.pos[0])
                        set_public_global("mouse_y", event.pos[1])
                        set_public_global("is_mouse_pressed", True)
                        set_public_global("mouse_button", event.button)
                        invoke_handler(sketch, "mouse_pressed", event.pos[0], event.pos[1], event.button)
                    elif event.type == pygame.MOUSEBUTTONUP:
                        set_public_global("pmouse_x", get_public_global("mouse_x"))
                        set_public_global("pmouse_y", get_public_global("mouse_y"))
                        set_public_global("mouse_x", event.pos[0])
                        set_public_global("mouse_y", event.pos[1])
                        set_public_global("is_mouse_pressed", False)
                        set_public_global("mouse_button", event.button)
                        invoke_handler(sketch, "mouse_released", event.pos[0], event.pos[1], event.button)
                        invoke_handler(sketch, "mouse_clicked", event.pos[0], event.pos[1], event.button)
                    elif event.type == pygame.MOUSEMOTION:
                        set_public_global("pmouse_x", get_public_global("mouse_x"))
                        set_public_global("pmouse_y", get_public_global("mouse_y"))
                        set_public_global("mouse_x", event.pos[0])
                        set_public_global("mouse_y", event.pos[1])
                        if any(event.buttons):
                            set_public_global("is_mouse_pressed", True)
                            invoke_handler(sketch, "mouse_dragged", event.pos[0], event.pos[1], event.rel[0], event.rel[1])
                        else:
                            set_public_global("is_mouse_pressed", False)
                            invoke_handler(sketch, "mouse_moved", event.pos[0], event.pos[1], event.rel[0], event.rel[1])
                    elif event.type == pygame.MOUSEWHEEL:
                        invoke_handler(sketch, "mouse_wheel", event.x, event.y)

                dispatch_input_events(sketch)
                set_public_global("frame_count", get_public_global("frame_count") + 1)

                begin_draw()
                try:
                    call_draw(sketch)
                finally:
                    end_draw()

                pygame.display.flip()
                tick(fps_getter())

        else:
            if has_setup:
                sketch.setup()

            pygame.display.flip()

            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.type == getattr(pygame, "WINDOWFOCUSGAINED", -1):
                        set_public_global("focused", True)
                    elif event.type == getattr(pygame, "WINDOWFOCUSLOST", -1):
                        set_public_global("focused", False)

                dispatch_input_events(sketch)
                tick(30)

    finally:
        restore_input_guard()
        if mode == "interactive":
            pygame.key.stop_text_input()
        shutdown()


async def run_app_async(
    mode,
    sketch,
    *,
    pygame,
    init_window,
    patch_input_guard,
    restore_input_guard,
    dispatch_input_events,
    invoke_handler,
    set_public_global,
    get_public_global,
    begin_draw,
    end_draw,
    call_draw,
    tick,
    fps_getter,
    shutdown,
):
    has_setup = hasattr(sketch, "setup")
    has_draw = hasattr(sketch, "draw")

    if mode is None:
        mode = "interactive" if has_draw else "static"
    else:
        mode = mode.lower().strip()

    if mode not in ("static", "interactive"):
        raise ValueError('mode must be None, "static", or "interactive"')

    init_window()
    patch_input_guard()

    try:
        if mode == "interactive":
            if not has_setup or not has_draw:
                raise RuntimeError(
                    "Interactive mode requires both setup() and draw(). "
                    "Either define them, or remove draw() to use static mode."
                )

            sketch.setup()
            pygame.key.start_text_input()

            current_mouse_x, current_mouse_y = pygame.mouse.get_pos()
            set_public_global("mouse_x", int(current_mouse_x))
            set_public_global("mouse_y", int(current_mouse_y))
            set_public_global("pmouse_x", int(current_mouse_x))
            set_public_global("pmouse_y", int(current_mouse_y))

            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == getattr(pygame, "WINDOWFOCUSGAINED", -1):
                        set_public_global("focused", True)
                    elif event.type == getattr(pygame, "WINDOWFOCUSLOST", -1):
                        set_public_global("focused", False)
                    elif event.type == pygame.KEYDOWN:
                        key_value = event.unicode if getattr(event, "unicode", "") else event.key
                        set_public_global("key", key_value)
                        set_public_global("key_code", event.key)
                        set_public_global("is_key_pressed", True)
                        invoke_handler(sketch, "key_pressed", event.key)
                        if event.key == pygame.K_ESCAPE:
                            running = False
                    elif event.type == pygame.KEYUP:
                        key_value = event.unicode if getattr(event, "unicode", "") else event.key
                        set_public_global("key", key_value)
                        set_public_global("key_code", event.key)
                        set_public_global("is_key_pressed", False)
                        invoke_handler(sketch, "key_released", event.key)
                    elif event.type == pygame.TEXTINPUT:
                        set_public_global("key", event.text)
                        invoke_handler(sketch, "key_typed", event.text)
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        set_public_global("pmouse_x", get_public_global("mouse_x"))
                        set_public_global("pmouse_y", get_public_global("mouse_y"))
                        set_public_global("mouse_x", event.pos[0])
                        set_public_global("mouse_y", event.pos[1])
                        set_public_global("is_mouse_pressed", True)
                        set_public_global("mouse_button", event.button)
                        invoke_handler(sketch, "mouse_pressed", event.pos[0], event.pos[1], event.button)
                    elif event.type == pygame.MOUSEBUTTONUP:
                        set_public_global("pmouse_x", get_public_global("mouse_x"))
                        set_public_global("pmouse_y", get_public_global("mouse_y"))
                        set_public_global("mouse_x", event.pos[0])
                        set_public_global("mouse_y", event.pos[1])
                        set_public_global("is_mouse_pressed", False)
                        set_public_global("mouse_button", event.button)
                        invoke_handler(sketch, "mouse_released", event.pos[0], event.pos[1], event.button)
                        invoke_handler(sketch, "mouse_clicked", event.pos[0], event.pos[1], event.button)
                    elif event.type == pygame.MOUSEMOTION:
                        set_public_global("pmouse_x", get_public_global("mouse_x"))
                        set_public_global("pmouse_y", get_public_global("mouse_y"))
                        set_public_global("mouse_x", event.pos[0])
                        set_public_global("mouse_y", event.pos[1])
                        if any(event.buttons):
                            set_public_global("is_mouse_pressed", True)
                            invoke_handler(sketch, "mouse_dragged", event.pos[0], event.pos[1], event.rel[0], event.rel[1])
                        else:
                            set_public_global("is_mouse_pressed", False)
                            invoke_handler(sketch, "mouse_moved", event.pos[0], event.pos[1], event.rel[0], event.rel[1])
                    elif event.type == pygame.MOUSEWHEEL:
                        invoke_handler(sketch, "mouse_wheel", event.x, event.y)

                dispatch_input_events(sketch)
                set_public_global("frame_count", get_public_global("frame_count") + 1)

                begin_draw()
                try:
                    call_draw(sketch)
                finally:
                    end_draw()

                pygame.display.flip()
                tick(fps_getter())
                await asyncio.sleep(0)

        else:
            if has_setup:
                sketch.setup()

            pygame.display.flip()

            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.type == getattr(pygame, "WINDOWFOCUSGAINED", -1):
                        set_public_global("focused", True)
                    elif event.type == getattr(pygame, "WINDOWFOCUSLOST", -1):
                        set_public_global("focused", False)

                dispatch_input_events(sketch)
                tick(30)
                await asyncio.sleep(0)

    finally:
        restore_input_guard()
        if mode == "interactive":
            pygame.key.stop_text_input()
        shutdown()
