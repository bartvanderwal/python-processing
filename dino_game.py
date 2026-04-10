from processing import run, size, frame_rate, title, background, fill, rect, line
from processing import image, text_size, text, load_image, no_fill, stroke, stroke_weight, no_stroke
from processing import width, height, key, key_code, random
import pygame

# Dino game assets
DINO_IMG = load_image("dino-image/dino-transparant.png")
DINO_OOPS_IMG = load_image("dino-image/dino-oops-transparant.png")
DINO_DUCK_IMG = load_image("dino-image/dino-duck-transparant.png")
BIRD_IMG = load_image("dino-image/bird-transparant.png")
SNAKE_IMG = load_image("dino-image/snake-transparant.png")
CACTUS_IMGS = [
    load_image("dino-image/cactus-transparant.png"),
    load_image("dino-image/3cacti-transparant.png")
]

# Dino properties
DINO_X = 100
DINO_Y = 400
DINO_W = 60
DINO_H = 60
DUCK_H = 30
GRAVITY = 1.2
JUMP_VELOCITY = -18
GROUND_Y = 460

# Collision hitbox tuning (smaller than visual sprite for fair gameplay)
DINO_HITBOX_INSET_LEFT = 12
DINO_HITBOX_INSET_RIGHT = 12
DINO_HITBOX_INSET_TOP = 8
DINO_HITBOX_INSET_BOTTOM = 8
DINO_HITBOX_Y_OFFSET = 3

DINO_DUCK_HITBOX_INSET_LEFT = 8
DINO_DUCK_HITBOX_INSET_RIGHT = 8
DINO_DUCK_HITBOX_INSET_TOP = 6
DINO_DUCK_HITBOX_INSET_BOTTOM = 4
DINO_DUCK_HITBOX_Y_OFFSET = 2

OBSTACLE_CONFIG = {
    "cactus_single": {
        "img": CACTUS_IMGS[0],
        "w": 50,
        "h": 60,
        "y": 400,
        "hitbox_insets": (7, 7, 6, 4),  # left, right, top, bottom
    },
    "cactus_multi": {
        "img": CACTUS_IMGS[1],
        "w": 58,
        "h": 58,
        "y": 402,
        "hitbox_insets": (8, 8, 7, 4),
    },
    "snake": {
        "img": SNAKE_IMG,
        "w": 54,
        "h": 30,
        "y": 430,
        "hitbox_insets": (6, 6, 6, 3),
    },
    "bird": {
        "img": BIRD_IMG,
        "w": 56,
        "h": 34,
        "y": 390,
        "hitbox_insets": (8, 8, 6, 6),
    },
}

# Game state
obstacle_x = 800
obstacle_type = "cactus_single"

dino_y = DINO_Y
velocity_y = 0
on_ground = True
game_over = False
game_started = False
score = 0
JUMP_SOUND = None
CRASH_SOUND = None
isDebugMode = False
is_ducking = False
game_paused = False


def reset_game(show_splash=False):
    global dino_y, velocity_y, on_ground, score, game_over, game_started, is_ducking, game_paused
    dino_y = DINO_Y
    velocity_y = 0
    on_ground = True
    score = 0
    game_over = False
    game_started = not show_splash
    is_ducking = False
    game_paused = False
    spawn_obstacle("cactus_single")


def setup():
    global JUMP_SOUND, CRASH_SOUND
    size(800, 500)
    frame_rate(60)
    title("Dino Game")
    reset_game(show_splash=True)

    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
    except Exception:
        return

    try:
        JUMP_SOUND = pygame.mixer.Sound("dino-audio/jump.wav")
    except Exception:
        JUMP_SOUND = None

    try:
        CRASH_SOUND = pygame.mixer.Sound("dino-audio/crash.wav")
    except Exception:
        CRASH_SOUND = None


def get_dino_hitbox():
    dino_draw_y = get_dino_draw_y()
    if is_ducking and on_ground and not game_over:
        dino_h = DUCK_H
        inset_left = DINO_DUCK_HITBOX_INSET_LEFT
        inset_right = DINO_DUCK_HITBOX_INSET_RIGHT
        inset_top = DINO_DUCK_HITBOX_INSET_TOP
        inset_bottom = DINO_DUCK_HITBOX_INSET_BOTTOM
        y_offset = DINO_DUCK_HITBOX_Y_OFFSET
    else:
        dino_h = DINO_H
        inset_left = DINO_HITBOX_INSET_LEFT
        inset_right = DINO_HITBOX_INSET_RIGHT
        inset_top = DINO_HITBOX_INSET_TOP
        inset_bottom = DINO_HITBOX_INSET_BOTTOM
        y_offset = DINO_HITBOX_Y_OFFSET

    return (
        DINO_X + inset_left,
        dino_draw_y + inset_top + y_offset,
        DINO_W - inset_left - inset_right,
        dino_h - inset_top - inset_bottom,
    )


def choose_obstacle_type():
    roll = int(random(0, 100))
    if roll < 35:
        return "cactus_single"
    if roll < 60:
        return "cactus_multi"
    if roll < 82:
        return "snake"
    return "bird"


def spawn_obstacle(force_type=None):
    global obstacle_x, obstacle_type
    obstacle_type = force_type or choose_obstacle_type()
    obstacle_x = width + random(100, 300)


def get_obstacle_hitbox():
    cfg = OBSTACLE_CONFIG[obstacle_type]
    inset_left, inset_right, inset_top, inset_bottom = cfg["hitbox_insets"]
    return (
        obstacle_x + inset_left,
        cfg["y"] + inset_top,
        cfg["w"] - inset_left - inset_right,
        cfg["h"] - inset_top - inset_bottom,
    )


def rects_overlap(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax + aw > bx and ax < bx + bw and ay + ah > by and ay < by + bh


def get_dino_draw_y():
    if is_ducking and on_ground and not game_over:
        return dino_y + (DINO_H - DUCK_H)
    return dino_y


def draw():
    global dino_y, velocity_y, on_ground, obstacle_x, score, game_over, game_started, is_ducking
    background(245)
    fill(200)
    rect(0, GROUND_Y, width, 40)  # ground
    stroke(120)
    stroke_weight(2)
    line(0, GROUND_Y, width, GROUND_Y)
    no_stroke()

    # Draw dino
    draw_dino()

    if not game_started:
        fill(0)
        text_size(44)
        text("Dino Game", width // 2 - 105, height // 2 - 55)
        text_size(22)
        text("Start: SPACE of A", width // 2 - 95, height // 2 - 10)
        text("Spring: pijl omhoog", width // 2 - 110, height // 2 + 20)
        text("Duik: pijl omlaag", width // 2 - 100, height // 2 + 50)
        return

    # Draw obstacle
    obstacle_cfg = OBSTACLE_CONFIG[obstacle_type]
    image(obstacle_cfg["img"], obstacle_x, obstacle_cfg["y"], obstacle_cfg["w"], obstacle_cfg["h"])

    if game_paused:
        fill(40)
        text_size(34)
        text("Pauze", width // 2 - 55, height // 2 - 8)
        text_size(18)
        text("Druk op P om verder te gaan", width // 2 - 118, height // 2 + 22)
        return

    if not game_over:
        # Dino jump physics
        if not on_ground:
            velocity_y += GRAVITY
            dino_y += velocity_y
            if dino_y >= DINO_Y:
                dino_y = DINO_Y
                velocity_y = 0
                on_ground = True

        obstacle_x -= 6
        if obstacle_x < -obstacle_cfg["w"]:
            spawn_obstacle()
            score += 1

        # Collision detection
        dino_hitbox = get_dino_hitbox()
        obstacle_hitbox = get_obstacle_hitbox()
        if rects_overlap(dino_hitbox, obstacle_hitbox):
            game_over = True
            is_ducking = False
            if CRASH_SOUND is not None:
                CRASH_SOUND.play()

    if isDebugMode:
        no_fill()
        stroke(255, 0, 0)
        stroke_weight(2)
        rect(*get_obstacle_hitbox())
        no_stroke()

    if game_over:
        fill(255, 0, 0)
        text_size(40)
        text("Game Over!", width // 2 - 120, height // 2)
        fill(0)
        text_size(24)
        text(f"Score: {score}", 20, 40)
        text("Druk op SPACE voor startscherm", width // 2 - 170, height // 2 + 40)
        return

    # Score
    fill(0)
    text_size(24)
    text(f"Score: {score}", 20, 40)

def key_pressed():
    global velocity_y, on_ground, game_started, isDebugMode, is_ducking, game_paused
    if key in ("d", "D"):
        isDebugMode = not isDebugMode
        return

    if key in ("p", "P") and game_started and not game_over:
        game_paused = not game_paused
        return

    if game_over and key == " ":
        reset_game(show_splash=True)
        return

    if not game_started and key in (" ", "a", "A"):
        reset_game(show_splash=False)
        return

    if game_paused:
        return

    if game_started and not game_over and key_code == pygame.K_DOWN and on_ground:
        is_ducking = True
        return

    if game_started and not game_over and key_code == pygame.K_UP and on_ground:
        if is_ducking:
            return
        velocity_y = JUMP_VELOCITY
        on_ground = False
        if JUMP_SOUND is not None:
            JUMP_SOUND.play()


def key_released(released_key):
    global is_ducking
    if released_key == pygame.K_DOWN:
        is_ducking = False


def draw_dino():
    dino_h = DUCK_H if (is_ducking and on_ground and not game_over) else DINO_H
    dino_y_draw = get_dino_draw_y()
    if game_over:
        dino_sprite = DINO_OOPS_IMG
    elif is_ducking and on_ground:
        dino_sprite = DINO_DUCK_IMG
    else:
        dino_sprite = DINO_IMG
    image(dino_sprite, DINO_X, dino_y_draw, DINO_W, dino_h)
    if isDebugMode:
        no_fill()
        stroke(255, 0, 0)
        stroke_weight(2)
        rect(*get_dino_hitbox())
        no_stroke()

run()
