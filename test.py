from processing import *
import os
import tempfile

# State
local_frame_count = 0
local_mouse_x = 0
local_mouse_y = 0
last_key = ""
last_typed = ""
last_event = "none"
wheel_dx = 0
wheel_dy = 0
is_dragging = False
console_last = "none"
console_error = "none"
asked_count = 0
image_test_status = "not-run"
image_test_surface = None
image_scale_8bit_status = "not-run"
random_test_status = "not-run"
random_last_value = 0.0
millis_start_value = 0
millis_now_value = 0
millis_test_status = "not-run"
nf_test_value = ""
nf_test_status = "not-run"
text_align_status = "not-run"
fullscreen_test_status = "not-run"
size_test_status = "not-run"
default_bg_test_status = "not-run"

# Test full_screen() before run() initializes the window.
full_screen()

# Visual style state
fill_on = True
stroke_on = True
stroke_w = 2
current_fill = color(80, 170, 255)
current_stroke = color(20)


def _write_test_png(path):
    # Create a guaranteed-valid PNG through pygame itself.
    surface = pygame.Surface((1, 1))
    surface.fill((0, 0, 0))
    pygame.image.save(surface, path)


def setup():
    global image_test_status, image_test_surface
    global image_scale_8bit_status
    global random_test_status, random_last_value
    global millis_start_value, millis_test_status
    global nf_test_value, nf_test_status, text_align_status, fullscreen_test_status, size_test_status, default_bg_test_status
    frame_rate(60)
    title("processing.py API + Event Handler Test")
    text_size(18)

    # Test size() function resizing the window
    size(1000, 600)
    if width == 1000 and height == 600:
        size_test_status = "ok"
    else:
        size_test_status = "failed-got-" + str(width) + "x" + str(height)

    sample = pygame.display.get_surface().get_at((0, 0))[:3]
    if sample == (200, 200, 200):
        default_bg_test_status = "ok"
    else:
        default_bg_test_status = "failed-rgb-" + str(sample)

    if width == display_width and height == display_height:
        fullscreen_test_status = "ok"
    else:
        fullscreen_test_status = "failed-size-" + str(width) + "x" + str(height)

    # load_image()/image() test: create a tiny PNG, load it, and validate dimensions.
    tmp_path = os.path.join(tempfile.gettempdir(), "processing_load_image_test.png")
    _write_test_png(tmp_path)
    image_test_surface = load_image(tmp_path)
    if image_test_surface.get_size() == (1, 1):
        image_test_status = "ok"
    else:
        image_test_status = "failed-size-" + str(image_test_surface.get_size())

    try:
        indexed_surface = pygame.Surface((2, 2), depth=8)
        image(indexed_surface, 2, 2, 20, 20)
        image_scale_8bit_status = "ok"
    except (ValueError, TypeError, pygame.error) as exc:
        image_scale_8bit_status = "failed-" + exc.__class__.__name__

    random_last_value = random(10, 20)
    if 10 <= random_last_value < 20:
        random_test_status = "ok"
    else:
        random_test_status = "failed-range"

    millis_start_value = millis()
    millis_test_status = "ok"

    nf_test_value = nf(7.25, 4, 2)
    if nf_test_value == "0007.25":
        nf_test_status = "ok"
    else:
        nf_test_status = "failed-value-" + nf_test_value

    text_align(LEFT, TOP)
    text_align_status = "ok"


def draw():
    global local_frame_count, millis_now_value, millis_test_status
    local_frame_count += 1

    # Base background
    background(245)

    # Style setup using color(), fill(), stroke(), stroke_weight()
    if fill_on:
        fill(current_fill[0], current_fill[1], current_fill[2])
    else:
        no_fill()

    if stroke_on:
        stroke(current_stroke[0], current_stroke[1], current_stroke[2])
    else:
        no_stroke()

    stroke_weight(stroke_w)

    # Shapes: rect(), circle(), point(), line(), triangle(), quad(), ellipse(), arc(), bezier()
    rect(40, 80, 160, 100)
    circle(280, 130, 90)
    point(350, 80)
    line(360, 85, 520, 170)
    triangle(560, 80, 700, 170, 620, 40)
    quad(730, 70, 860, 70, 840, 170, 710, 150)
    ellipse(140, 280, 200, 120)
    arc(380, 280, 160, 120, 0.0, 3.14)
    bezier(520, 260, 600, 180, 720, 360, 820, 280)

    # Cursor marker
    fill(255, 80, 80)
    stroke(0)
    stroke_weight(1)
    circle(local_mouse_x, local_mouse_y, 14)

    # Text overlay (text_size() already called in setup)
    fill(15)
    no_stroke()
    text("API draw calls done each frame", 20, 20)
    text("frame: " + str(local_frame_count), 20, 45)
    text("mouse: (" + str(local_mouse_x) + ", " + str(local_mouse_y) + ")", 20, 70)
    text("last key: " + str(last_key), 20, 95)
    text("last typed: " + str(last_typed), 20, 120)
    text("last event: " + str(last_event), 20, 145)
    text("wheel: dx=" + str(wheel_dx) + " dy=" + str(wheel_dy), 20, 170)
    text("fill_on=" + str(fill_on) + " stroke_on=" + str(stroke_on), 20, 195)
    text("stroke_weight=" + str(stroke_w), 20, 220)

    fill(40)
    text("Controls:", 20, 260)
    text("F: toggle fill", 20, 285)
    text("S: toggle stroke", 20, 310)
    text("+ / -: stroke weight", 20, 335)

    # Global variable validation panel
    text("Globals validation:", 500, 20)
    text("width/height: " + str(width) + " / " + str(height), 500, 45)
    text("display_width/display_height: " + str(display_width) + " / " + str(display_height), 500, 70)
    text("pixel_width/pixel_height: " + str(pixel_width) + " / " + str(pixel_height), 500, 95)
    text("frame_count: " + str(frame_count), 500, 120)
    text("focused: " + str(focused), 500, 145)
    text("mouse_x/mouse_y: " + str(mouse_x) + " / " + str(mouse_y), 500, 170)
    text("pmouse_x/pmouse_y: " + str(pmouse_x) + " / " + str(pmouse_y), 500, 195)
    text("is_mouse_pressed: " + str(is_mouse_pressed), 500, 220)
    text("mouse_button: " + str(mouse_button), 500, 245)
    text("key: " + str(key), 500, 270)
    text("key_code: " + str(key_code), 500, 295)
    text("is_key_pressed: " + str(is_key_pressed), 500, 320)
    text("input_pending: " + str(input_pending()), 500, 345)
    text("input_last: " + str(console_last), 500, 370)
    text("input_error: " + str(console_error), 500, 395)
    text("input_requests_started: " + str(asked_count), 500, 420)

    text("Input test:", 20, 370)
    text("Press I to request async console input", 20, 395)
    text("Type in terminal and press Enter", 20, 420)
    text("Press ESC to close window (esc handler test)", 20, 545)

    text("Image test status: " + image_test_status, 20, 445)
    text("image() 8-bit scale: " + image_scale_8bit_status, 20, 570)
    if image_test_surface is not None:
        image(image_test_surface, 20, 460, 90, 90)
        no_fill()
        stroke(20)
        stroke_weight(1)
        rect(20, 460, 90, 90)

    millis_now_value = millis()
    if millis_now_value < millis_start_value:
        millis_test_status = "failed-monotonic"

    fill(20)
    no_stroke()
    text("random(10,20) status: " + random_test_status + " value=" + nf(random_last_value, 2, 3), 500, 445)
    text("millis() status: " + millis_test_status + " start=" + str(millis_start_value) + " now=" + str(millis_now_value), 500, 470)
    text("nf() status: " + nf_test_status + " value=" + nf_test_value, 500, 495)
    text("text_align() status: " + text_align_status, 500, 520)
    text("full_screen() status: " + fullscreen_test_status, 500, 545)
    text("size() status: " + size_test_status, 500, 570)
    text("default bg status: " + default_bg_test_status, 500, 595)

    # text_align() visual test: all labels should line up around the anchors.
    text_align(LEFT, TOP)
    text("LEFT", 20, 560)
    text_align(CENTER, TOP)
    text("CENTER", 450, 560)
    text_align(RIGHT, TOP)
    text("RIGHT", 880, 560)
    text_align(LEFT, TOP)


# Keyboard handlers

def key_pressed(key):
    global last_key, last_event, fill_on, stroke_on, stroke_w, asked_count
    last_key = key
    last_event = "key_pressed"

    # Pygame key constants: f=102, s=115, plus variants around 43/61/1073741911
    # minus variants around 45/95/1073741910. Keep tolerant for different keyboards.
    if key == 102:
        fill_on = not fill_on
    elif key == 115:
        stroke_on = not stroke_on
    elif key in (43, 61, 1073741911):
        stroke_w += 1
    elif key in (45, 95, 1073741910):
        stroke_w = max(1, stroke_w - 1)
    elif key == 105:
        if request_input("speed? "):
            asked_count += 1


def input_received(text_line):
    global console_last, last_event
    console_last = text_line
    last_event = "input_received"


def input_error(err):
    global console_error, last_event
    console_error = str(err)
    last_event = "input_error"


def key_released(key):
    global last_key, last_event
    last_key = key
    last_event = "key_released"


def key_typed(char):
    global last_typed, last_event
    last_typed = char
    last_event = "key_typed"


# Mouse handlers

def mouse_pressed(x, y, button):
    global local_mouse_x, local_mouse_y, last_event, is_dragging
    local_mouse_x, local_mouse_y = x, y
    last_event = "mouse_pressed(button=" + str(button) + ")"
    is_dragging = True


def mouse_released(x, y, button):
    global local_mouse_x, local_mouse_y, last_event, is_dragging
    local_mouse_x, local_mouse_y = x, y
    last_event = "mouse_released(button=" + str(button) + ")"
    is_dragging = False


def mouse_clicked(x, y, button):
    global local_mouse_x, local_mouse_y, last_event
    local_mouse_x, local_mouse_y = x, y
    last_event = "mouse_clicked(button=" + str(button) + ")"



def mouse_moved(x, y, dx, dy):
    global local_mouse_x, local_mouse_y, last_event
    local_mouse_x, local_mouse_y = x, y
    last_event = "mouse_moved(dx=" + str(dx) + ", dy=" + str(dy) + ")"



def mouse_dragged(x, y, dx, dy):
    global local_mouse_x, local_mouse_y, last_event, is_dragging
    local_mouse_x, local_mouse_y = x, y
    is_dragging = True
    last_event = "mouse_dragged(dx=" + str(dx) + ", dy=" + str(dy) + ")"



def mouse_wheel(dx, dy):
    global wheel_dx, wheel_dy, last_event
    wheel_dx = dx
    wheel_dy = dy
    last_event = "mouse_wheel"


run()
