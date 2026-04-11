from processing import run, size, frame_rate, title, background, fill, rect, line, arc
from processing import image, text_size, text, load_image, no_fill, stroke, stroke_weight, no_stroke, millis
from processing import width, height, key, key_code, random
from processing import PI, TWO_PI
import pygame
import shared
import math

# Dino game assets
DINO_IMG = load_image("assets/dino-transparant.png")
DINO_OOPS_IMG = load_image("assets/dino-oops-transparant.png")
DINO_DUCK_IMG = load_image("assets/dino-duck-transparant.png")
COWBOY_IMG = load_image("assets/cowboy-transparant.png")
COWBOY_RUN_IMG = load_image("assets/cowboy-run-transparant.png")
COWBOY_FALL_IMG = load_image("assets/cowboy-fall-transparant.png")
COWBOY_DUCK_IMG = load_image("assets/cowboy-duck-transparant.png")
ROADRUNNER_IMG = load_image("assets/roadrunner-transparant.png")
ROADRUNNER_OOPS_IMG = load_image("assets/roadrunner-oops-transparant.png")
ROADRUNNER_DUCK_IMG = load_image("assets/roadrunner-duck-transparant.png")
AIRPLANE_IMG = load_image("assets/airplane-transparant.png")
BIRD_IMG = load_image("assets/bird-transparant.png")
SNAKE_IMG = load_image("assets/snake-transparant.png")
CACTUS_IMGS = [
    load_image("assets/cactus-transparant.png"),
    load_image("assets/3Cacti-transparant.png")
]

# Dino properties
DINO_X = 100
DINO_Y = 400
DINO_W = 60
DINO_H = 60
DUCK_H = 30
GRAVITY = 1.2
JUMP_VELOCITY = -18
HIGH_JUMP_VELOCITY = -22
HIGH_JUMP_WINDOW_MS = 500
FAST_FALL_EXTRA_GRAVITY = 2.0
BASE_SCROLL_SPEED = 6.0
LEVEL_SCORE_STEP = 10
LEVEL_SPEED_FACTOR = 1.1
LEVEL_BLINK_DURATION_MS = 1200
LEVEL_BLINK_INTERVAL_MS = 120
MAX_LEVEL = 10
HIGH_JUMP_WARNING_DURATION_MS = 1800
AIRPLANE_WARNING_DURATION_MS = 1800
FLIGHT_PIPE_GAP_H = 150
FLIGHT_PIPE_WIDTH = 72
FLIGHT_PIPE_SPAWN_BASE_MS = 1500
FLIGHT_PLANE_SPEED = 5.0
FLIGHT_PIPE_POINTS = 2
PLAYER_SHOOT_COOLDOWN_MS = 180
BOSS_INTRO_DURATION_MS = 1700
BOSS_LEVEL_ORDER = (4, 7, 10)
BOSS_REWARD_POINTS = {
    4: 8,
    7: 12,
    10: 20,
}
MAX_PROJECTILES_PER_SIDE = 10
MENU_MUSIC_PATH = "assets/audio/loading-atmosphere.wav"
GAME_MUSIC_PATH = "assets/audio/pixel-leap.m4a"
MUSIC_VOLUME = 0.35
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
    "cactus_low": {
        "img": CACTUS_IMGS[0],
        "w": 50,
        "h": 60,
        "y": 400,
        "hitbox_insets": (7, 7, 6, 4),  # left, right, top, bottom
        "points": 1,
    },
    "cactus_high": {
        "img": CACTUS_IMGS[0],
        "w": 56,
        "h": 88,
        "y": 372,
        "hitbox_insets": (8, 8, 8, 4),
        "points": 2,
    },
    "cactus_tower": {
        # 2x zo hoog als de lage cactus; doorgaans high jump nodig.
        "img": CACTUS_IMGS[0],
        "w": 72,
        "h": 120,
        "y": 340,
        "hitbox_insets": (10, 10, 8, 4),
        "points": 4,
    },
    "snake": {
        "img": SNAKE_IMG,
        "w": 54,
        "h": 30,
        "y": 430,
        "hitbox_insets": (6, 6, 6, 3),
        "extended_w": 108,
        "extended_hitbox_insets": (10, 10, 6, 3),
        "points": 5,
    },
    "bird_low": {
        "img": BIRD_IMG,
        "w": 56,
        "h": 34,
        "y": 390,
        "hitbox_insets": (8, 8, 6, 6),
        "points": 3,
        "requires_duck_score": True,
    },
    "airplane_pickup": {
        "img": AIRPLANE_IMG,
        "w": 120,
        "h": 44,
        "y": 378,
        "hitbox_insets": (8, 8, 6, 4),
        "points": 0,
    },
}

INFO_TEXT = [
    "SPACE of A: start / herstart",
    "Pijl omhoog: springen",
    "Pijl omlaag: duiken / sneller vallen in de lucht",
    "High jump: buk en spring binnen 0.5s",
    "Pijl links/rechts: character kiezen",
    "Punten: lage cactus +1, hoge cactus +2, torencactus +4",
    "Punten: bukken onder lage vogel +3, slang +5",
    "Vanaf level 5: spring op vliegtuig voor flight mode",
    "Flight mode: pijltjes bewegen, ontwijk pijpen",
    "Boss fights (lvl 4, 7, 10): SPACE = schieten",
    "Startscherm: klik character of klik Start",
    "P: pauze",
    "D: debug hitboxen",
    "L (debug): level +1, Shift+L: level -1",
    "I: dit infoscherm",
    "Q of ESC: afsluiten",
]

CHARACTER_ORDER = ["dino", "cowboy", "roadrunner"]
CHARACTER_CONFIG = {
    "dino": {
        "label": "Dino",
        "stand": DINO_IMG,
        "duck": DINO_DUCK_IMG,
        "oops": DINO_OOPS_IMG,
        "theme": {
            "bg": (245, 245, 245),
            "ground_fill": (200, 200, 200),
            "ground_line": (120, 120, 120),
            "text": (30, 30, 30),
            "accent": (70, 70, 70),
        },
    },
    "cowboy": {
        "label": "Cowboy",
        "stand": COWBOY_IMG,
        "run": COWBOY_RUN_IMG,
        "duck": COWBOY_DUCK_IMG,
        "oops": COWBOY_FALL_IMG,
        "theme": {
            "bg": (245, 220, 170),
            "ground_fill": (220, 175, 120),
            "ground_line": (150, 98, 50),
            "text": (60, 35, 20),
            "accent": (178, 84, 28),
        },
    },
    "roadrunner": {
        "label": "Roadrunner",
        "stand": ROADRUNNER_IMG,
        "duck": ROADRUNNER_DUCK_IMG,
        "oops": ROADRUNNER_OOPS_IMG,
        "theme": {
            "bg": (154, 214, 242),
            "ground_fill": (214, 200, 150),
            "ground_line": (121, 104, 76),
            "text": (16, 58, 88),
            "accent": (0, 112, 163),
        },
    },
}

# Game state
obstacle_x = 800
obstacle_type = "cactus_low"
bird_duck_scored = False

dino_y = DINO_Y
velocity_y = 0
on_ground = True
game_over = False
game_started = False
score = 0
JUMP_SOUND = None
CRASH_SOUND = None
HISS_SOUND = None
FIRE_PLAYER_SOUND = None
FIRE_ENEMY_SOUND = None
isDebugMode = False
is_ducking = False
game_paused = False
selected_character_idx = 0
active_character_key = "dino"
duck_jump_expires_ms = 0
is_fast_falling = False
current_level = 1
scroll_speed = BASE_SCROLL_SPEED
next_level_score = LEVEL_SCORE_STEP
level_blink_until_ms = 0
high_jump_warning_until_ms = 0
airplane_warning_until_ms = 0
pending_airplane_spawn = False
flight_mode = False
flight_plane_x = 0.0
flight_plane_y = 0.0
flight_pipe_spawn_due_ms = 0
flight_pipes = []
fly_left_pressed = False
fly_right_pressed = False
fly_up_pressed = False
fly_down_pressed = False
snake_hiss_played_for_current = False
player_projectiles = [{"active": False} for _ in range(MAX_PROJECTILES_PER_SIDE)]
player_shot_cooldown_until_ms = 0
boss_state = None
boss_intro_until_ms = 0
boss_completed = {
    4: False,
    7: False,
    10: False,
}
current_music_mode = None


def reset_game(show_splash=False):
    global dino_y, velocity_y, on_ground, score, game_over, game_started
    global is_ducking, game_paused, bird_duck_scored, duck_jump_expires_ms, is_fast_falling
    global current_level, scroll_speed, next_level_score, level_blink_until_ms
    global high_jump_warning_until_ms, airplane_warning_until_ms, pending_airplane_spawn
    global flight_mode, flight_plane_x, flight_plane_y, flight_pipe_spawn_due_ms, flight_pipes
    global fly_left_pressed, fly_right_pressed, fly_up_pressed, fly_down_pressed
    global snake_hiss_played_for_current
    global player_projectiles, player_shot_cooldown_until_ms
    global boss_state, boss_intro_until_ms, boss_completed
    dino_y = DINO_Y
    velocity_y = 0
    on_ground = True
    score = 0
    game_over = False
    game_started = not show_splash
    is_ducking = False
    game_paused = False
    bird_duck_scored = False
    duck_jump_expires_ms = 0
    is_fast_falling = False
    current_level = 1
    scroll_speed = BASE_SCROLL_SPEED
    next_level_score = LEVEL_SCORE_STEP
    level_blink_until_ms = 0
    high_jump_warning_until_ms = 0
    airplane_warning_until_ms = 0
    pending_airplane_spawn = False
    flight_mode = False
    flight_plane_x = 0.0
    flight_plane_y = 0.0
    flight_pipe_spawn_due_ms = 0
    flight_pipes = []
    fly_left_pressed = False
    fly_right_pressed = False
    fly_up_pressed = False
    fly_down_pressed = False
    snake_hiss_played_for_current = False
    player_projectiles = [{"active": False} for _ in range(MAX_PROJECTILES_PER_SIDE)]
    player_shot_cooldown_until_ms = 0
    boss_state = None
    boss_intro_until_ms = 0
    boss_completed = {
        4: False,
        7: False,
        10: False,
    }
    spawn_obstacle("cactus_low")


def update_background_music(force=False):
    global current_music_mode
    if not pygame.mixer.get_init():
        return

    if not shared.music_enabled:
        if current_music_mode is not None:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
            current_music_mode = None
        return

    target_mode = "menu" if (not game_started or shared.show_info) else "game"
    if not force and target_mode == current_music_mode:
        return

    target_path = MENU_MUSIC_PATH if target_mode == "menu" else GAME_MUSIC_PATH
    try:
        pygame.mixer.music.load(target_path)
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
        pygame.mixer.music.play(-1)
        current_music_mode = target_mode
    except Exception:
        # Keep the game running even when a track cannot be loaded.
        current_music_mode = None


def setup():
    global JUMP_SOUND, CRASH_SOUND, HISS_SOUND, FIRE_PLAYER_SOUND, FIRE_ENEMY_SOUND
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
        JUMP_SOUND = pygame.mixer.Sound("assets/audio/jump.wav")
    except Exception:
        JUMP_SOUND = None

    try:
        CRASH_SOUND = pygame.mixer.Sound("assets/audio/crash.wav")
    except Exception:
        CRASH_SOUND = None

    try:
        HISS_SOUND = pygame.mixer.Sound("assets/audio/hiss.wav")
    except Exception:
        HISS_SOUND = None

    try:
        FIRE_PLAYER_SOUND = pygame.mixer.Sound("assets/audio/fire-player.wav")
    except Exception:
        FIRE_PLAYER_SOUND = None

    try:
        FIRE_ENEMY_SOUND = pygame.mixer.Sound("assets/audio/fire-enemy.wav")
    except Exception:
        FIRE_ENEMY_SOUND = None

    update_background_music(force=True)


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
    if pending_airplane_spawn:
        return "airplane_pickup"

    # Level 1: nog geen slang.
    if current_level < 2:
        roll = int(random(0, 100))
        if roll < 52:
            return "cactus_low"
        if roll < 84:
            return "cactus_high"
        return "bird_low"

    # Level 2: slang komt erbij.
    if current_level < 3:
        roll = int(random(0, 100))
        if roll < 36:
            return "cactus_low"
        if roll < 66:
            return "cactus_high"
        if roll < 84:
            return "snake"
        return "bird_low"

    roll = int(random(0, 100))
    if roll < 35:
        return "cactus_low"
    if roll < 58:
        return "cactus_high"
    if roll < 68:
        return "cactus_tower"
    if roll < 82:
        return "snake"
    return "bird_low"


def spawn_obstacle(force_type=None):
    global obstacle_x, obstacle_type, bird_duck_scored
    global high_jump_warning_until_ms, airplane_warning_until_ms, pending_airplane_spawn
    global snake_hiss_played_for_current
    obstacle_type = force_type or choose_obstacle_type()
    obstacle_x = width + random(100, 300)
    bird_duck_scored = False
    snake_hiss_played_for_current = False
    if obstacle_type == "airplane_pickup":
        pending_airplane_spawn = False
        airplane_warning_until_ms = millis() + AIRPLANE_WARNING_DURATION_MS
    if obstacle_type == "cactus_tower":
        high_jump_warning_until_ms = millis() + HIGH_JUMP_WARNING_DURATION_MS


def get_flight_plane_rect():
    return (flight_plane_x, flight_plane_y, 88, 36)


def spawn_flight_pipe():
    gap_top = int(random(90, GROUND_Y - FLIGHT_PIPE_GAP_H - 50))
    flight_pipes.append({
        "x": width + 20,
        "gap_top": gap_top,
        "passed": False,
    })


def start_flight_mode():
    global flight_mode, flight_plane_x, flight_plane_y, flight_pipe_spawn_due_ms, flight_pipes
    global fly_left_pressed, fly_right_pressed, fly_up_pressed, fly_down_pressed
    global current_level, scroll_speed, next_level_score, level_blink_until_ms
    flight_mode = True
    flight_plane_x = 120.0
    flight_plane_y = float(GROUND_Y - 90)
    flight_pipe_spawn_due_ms = millis() + 400
    flight_pipes = []
    fly_left_pressed = False
    fly_right_pressed = False
    fly_up_pressed = False
    fly_down_pressed = False
    current_level = min(MAX_LEVEL, current_level + 1)
    scroll_speed = BASE_SCROLL_SPEED * (LEVEL_SPEED_FACTOR ** (current_level - 1))
    next_level_score = current_level * LEVEL_SCORE_STEP
    level_blink_until_ms = millis() + LEVEL_BLINK_DURATION_MS


def is_snake_extended():
    if obstacle_type != "snake":
        return False
    return obstacle_x < DINO_X + 220


def get_obstacle_draw_rect():
    cfg = OBSTACLE_CONFIG[obstacle_type]
    draw_x = obstacle_x
    draw_y = cfg["y"]
    draw_w = cfg["w"]
    draw_h = cfg["h"]

    if obstacle_type == "snake" and is_snake_extended():
        draw_w = cfg["extended_w"]
        # Uitklappen rondom midden, zodat de slang zichtbaar langer wordt dichtbij de speler.
        draw_x = obstacle_x - (draw_w - cfg["w"]) // 2

    return draw_x, draw_y, draw_w, draw_h


def get_obstacle_hitbox():
    cfg = OBSTACLE_CONFIG[obstacle_type]
    draw_x, draw_y, draw_w, draw_h = get_obstacle_draw_rect()
    if obstacle_type == "snake" and is_snake_extended():
        inset_left, inset_right, inset_top, inset_bottom = cfg["extended_hitbox_insets"]
    else:
        inset_left, inset_right, inset_top, inset_bottom = cfg["hitbox_insets"]

    return (
        draw_x + inset_left,
        draw_y + inset_top,
        draw_w - inset_left - inset_right,
        draw_h - inset_top - inset_bottom,
    )


def rects_overlap(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax + aw > bx and ax < bx + bw and ay + ah > by and ay < by + bh


def get_dino_draw_y():
    if is_ducking and on_ground and not game_over:
        return dino_y + (DINO_H - DUCK_H)
    return dino_y


def get_selected_character_key():
    return CHARACTER_ORDER[selected_character_idx]


def get_current_character_key():
    if game_started:
        return active_character_key
    return get_selected_character_key()


def start_game_from_selection():
    global active_character_key
    active_character_key = get_selected_character_key()
    reset_game(show_splash=False)


def get_theme():
    return CHARACTER_CONFIG[get_current_character_key()]["theme"]


def update_level_from_score():
    global current_level, scroll_speed, next_level_score, level_blink_until_ms, pending_airplane_spawn
    new_level = min(MAX_LEVEL, max(1, (score // LEVEL_SCORE_STEP) + 1))
    if new_level > current_level:
        current_level = new_level
        scroll_speed = BASE_SCROLL_SPEED * (LEVEL_SPEED_FACTOR ** (current_level - 1))
        next_level_score = current_level * LEVEL_SCORE_STEP
        level_blink_until_ms = millis() + LEVEL_BLINK_DURATION_MS
        if current_level >= 5 and not flight_mode:
            pending_airplane_spawn = True


def debug_step_level(level_delta):
    global current_level, score, scroll_speed, next_level_score, level_blink_until_ms, pending_airplane_spawn
    old_level = current_level
    target_level = max(1, min(MAX_LEVEL, current_level + level_delta))
    if target_level == old_level:
        return

    # In debug mode, level and score move together in fixed 10-point steps.
    score = max(0, score + (target_level - old_level) * LEVEL_SCORE_STEP)
    current_level = target_level
    scroll_speed = BASE_SCROLL_SPEED * (LEVEL_SPEED_FACTOR ** (current_level - 1))
    next_level_score = current_level * LEVEL_SCORE_STEP
    level_blink_until_ms = millis() + LEVEL_BLINK_DURATION_MS

    if old_level < 5 <= current_level and not flight_mode:
        pending_airplane_spawn = True
    if current_level < 5:
        pending_airplane_spawn = False


def get_player_weapon_profile():
    character_key = get_current_character_key()
    if character_key == "cowboy":
        return {"kind": "gun", "label": "Gun", "w": 16, "h": 4, "speed": 12.0, "color": (25, 25, 25)}
    if character_key == "roadrunner":
        return {"kind": "tnt", "label": "TNT", "w": 12, "h": 12, "speed": 9.0, "color": (210, 35, 30)}
    return {"kind": "fire", "label": "Fire", "w": 18, "h": 8, "speed": 10.0, "color": (240, 120, 25)}


def create_projectile_pool():
    return [{"active": False} for _ in range(MAX_PROJECTILES_PER_SIDE)]


def reset_projectile_pool(pool):
    for projectile in pool:
        projectile["active"] = False


def acquire_projectile_slot(pool):
    for projectile in pool:
        if not projectile.get("active", False):
            projectile.clear()
            projectile["active"] = True
            return projectile
    return None


def iter_active_projectiles(pool):
    for projectile in pool:
        if projectile.get("active", False):
            yield projectile


def get_projectile_rect(projectile):
    return (projectile["x"], projectile["y"], projectile["w"], projectile["h"])


def draw_projectile(projectile):
    x = int(projectile["x"])
    y = int(projectile["y"])
    w = int(projectile["w"])
    h = int(projectile["h"])
    kind = projectile["kind"]

    if kind == "fire":
        fill(235, 85, 20)
        rect(x, y, w, h)
        fill(250, 200, 70)
        rect(x + 3, y + 2, max(3, w - 7), max(2, h - 4))
        return

    if kind == "tnt":
        fill(205, 30, 30)
        rect(x, y, w, h)
        fill(255, 220, 90)
        rect(x + w - 2, y - 3, 2, 3)
        return

    if kind == "stem":
        fill(42, 130, 44)
        rect(x, y, w, h)
        fill(28, 98, 30)
        rect(x + 2, y + 2, max(2, w - 4), max(2, h - 4))
        return

    # gun / wind / fallback
    fill(*projectile["color"])
    rect(x, y, w, h)


def fire_player_weapon():
    global player_shot_cooldown_until_ms
    if boss_state is None or game_over or game_paused or shared.show_info:
        return
    now = millis()
    if now < player_shot_cooldown_until_ms:
        return
    projectile = acquire_projectile_slot(player_projectiles)
    if projectile is None:
        return
    profile = get_player_weapon_profile()
    dino_draw_y = get_dino_draw_y()
    dino_h = DUCK_H if (is_ducking and on_ground and not game_over) else DINO_H
    projectile_y = dino_draw_y + (dino_h // 2) - (profile["h"] // 2)
    projectile.update({
        "x": DINO_X + DINO_W - 4,
        "y": projectile_y,
        "w": profile["w"],
        "h": profile["h"],
        "vx": profile["speed"],
        "vy": 0.0,
        "kind": profile["kind"],
        "color": profile["color"],
        "enemy": False,
    })
    if boss_state is not None:
        target_y = boss_state["y"] + (boss_state["h"] * 0.5)
        travel_px = max(80.0, width - (DINO_X + DINO_W))
        projectile["vy"] = (target_y - projectile_y) / (travel_px / max(0.1, profile["speed"]))
    if FIRE_PLAYER_SOUND is not None:
        FIRE_PLAYER_SOUND.play()
    player_shot_cooldown_until_ms = now + PLAYER_SHOOT_COOLDOWN_MS


def get_boss_hitbox(boss):
    if boss["type"] == "cactus_miniboss":
        return (boss["x"] + 10, boss["y"] + 8, boss["w"] - 20, boss["h"] - 8)
    return (boss["x"] + 10, boss["y"] + 6, boss["w"] - 20, boss["h"] - 12)


def get_cactus_branch_rects(boss):
    branch_rects = []
    branch_x = boss["x"] - 46
    base_y = boss["y"] + 22
    for idx in range(5):
        branch_y = base_y + idx * 38
        branch_rects.append((branch_x, branch_y, 46, 14))
    return branch_rects


def spawn_boss_for_level(level):
    now = millis()
    if level == 4:
        return {
            "type": "bird_miniboss",
            "level": 4,
            "name": "Miniboss L4: Reuzenvogel",
            "x": float(width - 220),
            "y": 188.0,
            "w": 200,
            "h": 120,
            "vx": -2.2,
            "vy": 1.6,
            "min_x": float(width - 320),
            "max_x": float(width - 70),
            "min_y": 118.0,
            "max_y": 300.0,
            "hits_taken": 0,
            "hits_required": 15,
            "meter_steps": 20,
            "enemy_projectiles": create_projectile_pool(),
            "attack_interval_ms": 1120,
            "last_attack_ms": now,
        }

    if level == 7:
        return {
            "type": "cactus_miniboss",
            "level": 7,
            "name": "Miniboss L7: Reuzencactus",
            "x": float(width - 190),
            "y": 176.0,
            "w": 124,
            "h": 242,
            "vy": 1.2,
            "min_y": 150.0,
            "max_y": 210.0,
            "branch_hp": [5, 5, 5, 5, 5],
            "hits_taken": 0,
            "hits_required": 25,
            "meter_steps": 25,
            "enemy_projectiles": create_projectile_pool(),
            "attack_interval_ms": 860,
            "last_attack_ms": now,
        }

    profile = get_player_weapon_profile()
    form_name = "ReuzenDino"
    if active_character_key == "cowboy":
        form_name = "ReuzenCowboy"
    elif active_character_key == "roadrunner":
        form_name = "ReuzenCoyote"
    return {
        "type": "final_boss",
        "level": 10,
        "name": f"Eindbaas L10: {form_name}",
        "form": form_name,
        "x": float(width - 220),
        "y": 162.0,
        "w": 190,
        "h": 230,
        "vy": 1.35,
        "min_y": 120.0,
        "max_y": 220.0,
        "hits_taken": 0,
        "hits_required": 35,
        "meter_steps": 35,
        "enemy_projectiles": create_projectile_pool(),
        "attack_interval_ms": 760,
        "last_attack_ms": now,
        "enemy_weapon_kind": profile["kind"],
    }


def maybe_start_boss_encounter():
    global boss_state, boss_intro_until_ms, player_shot_cooldown_until_ms
    if boss_state is not None or game_over or not game_started or game_paused or flight_mode:
        return
    for level in BOSS_LEVEL_ORDER:
        if current_level >= level and not boss_completed[level]:
            boss_state = spawn_boss_for_level(level)
            boss_intro_until_ms = millis() + BOSS_INTRO_DURATION_MS
            reset_projectile_pool(player_projectiles)
            player_shot_cooldown_until_ms = 0
            break


def draw_boss_entity(boss):
    x = int(boss["x"])
    y = int(boss["y"])
    w = int(boss["w"])
    h = int(boss["h"])

    if boss["type"] == "bird_miniboss":
        image(BIRD_IMG, x, y, w, h)
        return

    if boss["type"] == "cactus_miniboss":
        fill(46, 145, 54)
        rect(x, y, w, h)
        fill(61, 172, 71)
        rect(x + 20, y + 10, w - 40, h - 24)
        branch_rects = get_cactus_branch_rects(boss)
        for idx, branch_hp in enumerate(boss["branch_hp"]):
            if branch_hp <= 0:
                continue
            bx, by, bw, bh = branch_rects[idx]
            fill(48, 138, 53)
            rect(int(bx), int(by), int(bw), int(bh))
        return

    # Final boss
    if boss["form"] == "ReuzenDino":
        image(DINO_IMG, x, y, w, h)
        return
    if boss["form"] == "ReuzenCowboy":
        image(COWBOY_IMG, x, y, w, h)
        return

    # ReuzenCoyote without dedicated sprite: stylized silhouette.
    fill(124, 84, 51)
    rect(x + 24, y + 78, w - 54, h - 120)
    rect(x + 8, y + 92, 30, h - 112)
    rect(x + w - 50, y + 62, 42, 58)
    fill(94, 60, 34)
    rect(x + w - 44, y + 54, 12, 14)
    rect(x + w - 26, y + 54, 12, 14)
    fill(12, 12, 12)
    rect(x + w - 34, y + 84, 6, 6)


def draw_boss_meter(boss, theme):
    bar_x = width // 2 - 190
    bar_y = 74
    bar_w = 380
    bar_h = 18
    fill(45, 45, 45)
    rect(bar_x, bar_y, bar_w, bar_h)

    steps = boss["meter_steps"]
    hits_required = boss["hits_required"]
    hits_taken = boss["hits_taken"]
    remaining_ratio = max(0.0, (hits_required - hits_taken) / max(1, hits_required))
    filled_steps = int(round(steps * remaining_ratio))
    step_w = (bar_w - 4) / max(1, steps)

    fill(214, 66, 66)
    for idx in range(filled_steps):
        px = int(bar_x + 2 + idx * step_w)
        rect(px, bar_y + 2, max(2, int(step_w - 1)), bar_h - 4)

    fill(*theme["text"])
    text_size(18)
    text(boss["name"], width // 2 - 186, 66)
    text_size(15)
    text(f"Hits: {hits_taken}/{hits_required}", width // 2 + 106, 66)


def finish_boss_if_defeated(boss):
    global boss_state, score
    if boss["hits_taken"] < boss["hits_required"]:
        return
    boss_completed[boss["level"]] = True
    boss_state = None
    reset_projectile_pool(player_projectiles)
    score += BOSS_REWARD_POINTS.get(boss["level"], 0)
    update_level_from_score()
    spawn_obstacle()


def update_enemy_projectiles(boss):
    global game_over
    player_hitbox = get_dino_hitbox()
    for projectile in iter_active_projectiles(boss["enemy_projectiles"]):
        projectile["x"] += projectile["vx"]
        projectile_rect = get_projectile_rect(projectile)
        if rects_overlap(projectile_rect, player_hitbox):
            projectile["active"] = False
            game_over = True
            if CRASH_SOUND is not None:
                CRASH_SOUND.play()
            return
        if projectile["x"] + projectile["w"] < -40:
            projectile["active"] = False


def update_player_projectiles_against_boss(boss):
    boss_hitbox = get_boss_hitbox(boss)
    branch_rects = get_cactus_branch_rects(boss) if boss["type"] == "cactus_miniboss" else []
    for projectile in iter_active_projectiles(player_projectiles):
        projectile["x"] += projectile["vx"]
        projectile["y"] += projectile.get("vy", 0.0)
        projectile_rect = get_projectile_rect(projectile)
        hit = False

        if boss["type"] == "cactus_miniboss":
            for idx, branch_rect in enumerate(branch_rects):
                if boss["branch_hp"][idx] <= 0:
                    continue
                if rects_overlap(projectile_rect, branch_rect):
                    boss["branch_hp"][idx] -= 1
                    boss["hits_taken"] += 1
                    hit = True
                    break
        elif rects_overlap(projectile_rect, boss_hitbox):
            boss["hits_taken"] += 1
            hit = True

        if hit:
            projectile["active"] = False
            continue
        if projectile["x"] > width + 40:
            projectile["active"] = False


def spawn_boss_attack_if_needed(boss):
    now = millis()
    if now - boss["last_attack_ms"] < boss["attack_interval_ms"]:
        return
    boss["last_attack_ms"] = now

    projectile = acquire_projectile_slot(boss["enemy_projectiles"])
    if projectile is None:
        return

    if boss["type"] == "bird_miniboss":
        projectile.update({
            "x": boss["x"] - 26,
            "y": DINO_Y + 14 + int(random(-5, 6)),
            "w": 30,
            "h": 14,
            "vx": -10.0,
            "kind": "wind",
            "color": (80, 80, 80),
            "enemy": True,
        })
        if FIRE_ENEMY_SOUND is not None:
            FIRE_ENEMY_SOUND.play()
        return

    if boss["type"] == "cactus_miniboss":
        branch_rects = get_cactus_branch_rects(boss)
        living_idxs = [idx for idx, hp in enumerate(boss["branch_hp"]) if hp > 0]
        if not living_idxs:
            projectile["active"] = False
            return
        pick = living_idxs[int(random(0, len(living_idxs)))]
        bx, by, bw, bh = branch_rects[pick]
        projectile.update({
            "x": bx - 10,
            "y": by + (bh // 2) - 4,
            "w": 22,
            "h": 8,
            "vx": -8.8,
            "kind": "stem",
            "color": (40, 130, 40),
            "enemy": True,
        })
        if FIRE_ENEMY_SOUND is not None:
            FIRE_ENEMY_SOUND.play()
        return

    # final boss shoots same style as player
    enemy_kind = boss["enemy_weapon_kind"]
    if enemy_kind == "tnt":
        w, h, speed, color = 12, 12, 9.0, (210, 35, 30)
    elif enemy_kind == "fire":
        w, h, speed, color = 18, 8, 10.0, (240, 120, 25)
    else:
        w, h, speed, color = 16, 4, 12.0, (25, 25, 25)
    projectile.update({
        "x": boss["x"] - 14,
        "y": boss["y"] + (boss["h"] // 2) + int(random(-26, 26)),
        "w": w,
        "h": h,
        "vx": -speed,
        "kind": enemy_kind,
        "color": color,
        "enemy": True,
    })
    if FIRE_ENEMY_SOUND is not None:
        FIRE_ENEMY_SOUND.play()


def update_and_draw_boss_mode(theme, update_world=True):
    global dino_y, velocity_y, on_ground, is_fast_falling, game_over
    boss = boss_state
    if boss is None:
        return

    if update_world:
        # Player jump physics stays active during boss fights.
        if not on_ground:
            gravity_now = GRAVITY + (FAST_FALL_EXTRA_GRAVITY if is_fast_falling else 0)
            velocity_y += gravity_now
            dino_y += velocity_y
            if dino_y >= DINO_Y:
                dino_y = DINO_Y
                velocity_y = 0
                on_ground = True
                is_fast_falling = False

        if boss["type"] == "bird_miniboss":
            boss["x"] += boss["vx"]
            boss["y"] += boss["vy"]
            if boss["x"] <= boss["min_x"] or boss["x"] >= boss["max_x"]:
                boss["vx"] *= -1
            if boss["y"] <= boss["min_y"] or boss["y"] >= boss["max_y"]:
                boss["vy"] *= -1
        else:
            boss["y"] += boss["vy"]
            if boss["y"] <= boss["min_y"] or boss["y"] >= boss["max_y"]:
                boss["vy"] *= -1

        spawn_boss_attack_if_needed(boss)
        update_enemy_projectiles(boss)
        if game_over:
            return

        update_player_projectiles_against_boss(boss)
        finish_boss_if_defeated(boss)
        if boss_state is None:
            return

        if rects_overlap(get_dino_hitbox(), get_boss_hitbox(boss)):
            game_over = True
            if CRASH_SOUND is not None:
                CRASH_SOUND.play()
            return

    draw_boss_entity(boss)
    draw_boss_meter(boss, theme)

    for projectile in iter_active_projectiles(boss["enemy_projectiles"]):
        draw_projectile(projectile)
    for projectile in iter_active_projectiles(player_projectiles):
        draw_projectile(projectile)

    weapon_label = get_player_weapon_profile()["label"]
    fill(*theme["text"])
    text_size(16)
    text(f"Wapen: {weapon_label} (SPACE)", 20, 66)

    if millis() < boss_intro_until_ms:
        fill(*theme["accent"])
        text_size(24)
        text(boss["name"], width // 2 - 150, 112)

    if isDebugMode:
        no_fill()
        stroke(255, 0, 0)
        stroke_weight(2)
        rect(*get_boss_hitbox(boss))
        for projectile in iter_active_projectiles(boss["enemy_projectiles"]):
            rect(*get_projectile_rect(projectile))
        for projectile in iter_active_projectiles(player_projectiles):
            rect(*get_projectile_rect(projectile))
        if boss["type"] == "cactus_miniboss":
            for idx, branch_rect in enumerate(get_cactus_branch_rects(boss)):
                if boss["branch_hp"][idx] > 0:
                    rect(*branch_rect)
        no_stroke()


def is_level_blink_active():
    return millis() < level_blink_until_ms


def should_show_blink_phase():
    return int(millis() / LEVEL_BLINK_INTERVAL_MS) % 2 == 0


def draw_hud(theme, force_visible=False):
    blink_active = is_level_blink_active() and not force_visible
    visible = True if force_visible else (not blink_active or should_show_blink_phase())

    if visible:
        fill(*theme["text"])
        text_size(24)
        text(f"Score: {score}", 20, 40)
        text(f"Level: {current_level}", width - 150, 40)

    # During blink, briefly show level-up cue in accent color.
    if is_level_blink_active() and should_show_blink_phase():
        fill(*theme["accent"])
        text_size(20)
        text(f"Level Up! x{LEVEL_SPEED_FACTOR}", width // 2 - 90, 40)


def draw_debug_overlay():
    if not isDebugMode:
        return
    fill(180, 20, 20)
    text_size(18)
    text("DEBUG MODE", width - 140, 24)
    text_size(14)
    speed_mult = scroll_speed / BASE_SCROLL_SPEED
    text(f"Speed: {speed_mult:.2f}x", width - 140, 44)
    text(f"Level: {current_level}", width - 140, 62)


def draw_flight_pipes():
    for pipe in flight_pipes:
        x = int(pipe["x"])
        top_h = int(pipe["gap_top"])
        bottom_y = top_h + FLIGHT_PIPE_GAP_H
        bottom_h = GROUND_Y - bottom_y

        fill(74, 160, 90)
        rect(x, 0, FLIGHT_PIPE_WIDTH, top_h)
        rect(x, bottom_y, FLIGHT_PIPE_WIDTH, bottom_h)


def update_and_draw_flight_mode(theme, update_world=True):
    global flight_plane_x, flight_plane_y, flight_pipe_spawn_due_ms, score, game_over

    now = millis()
    if update_world:
        # Movement in left half of the screen.
        if fly_left_pressed:
            flight_plane_x -= FLIGHT_PLANE_SPEED
        if fly_right_pressed:
            flight_plane_x += FLIGHT_PLANE_SPEED
        if fly_up_pressed:
            flight_plane_y -= FLIGHT_PLANE_SPEED
        if fly_down_pressed:
            flight_plane_y += FLIGHT_PLANE_SPEED

        plane_w = 88
        plane_h = 36
        flight_plane_x = max(20.0, min((width // 2) - plane_w - 10, flight_plane_x))
        flight_plane_y = max(50.0, min(GROUND_Y - plane_h - 4, flight_plane_y))

        if now >= flight_pipe_spawn_due_ms:
            spawn_flight_pipe()
            spawn_delay = max(700, int(FLIGHT_PIPE_SPAWN_BASE_MS / max(0.8, scroll_speed / BASE_SCROLL_SPEED)))
            flight_pipe_spawn_due_ms = now + spawn_delay

        for pipe in flight_pipes:
            pipe["x"] -= scroll_speed
            if not pipe["passed"] and pipe["x"] + FLIGHT_PIPE_WIDTH < flight_plane_x:
                pipe["passed"] = True
                score += FLIGHT_PIPE_POINTS
                update_level_from_score()

        flight_pipes[:] = [p for p in flight_pipes if p["x"] + FLIGHT_PIPE_WIDTH > -20]

        # Plane hitbox vs pipes.
        plane_rect = get_flight_plane_rect()
        for pipe in flight_pipes:
            top_rect = (pipe["x"], 0, FLIGHT_PIPE_WIDTH, pipe["gap_top"])
            bottom_rect = (
                pipe["x"],
                pipe["gap_top"] + FLIGHT_PIPE_GAP_H,
                FLIGHT_PIPE_WIDTH,
                GROUND_Y - (pipe["gap_top"] + FLIGHT_PIPE_GAP_H),
            )
            if rects_overlap(plane_rect, top_rect) or rects_overlap(plane_rect, bottom_rect):
                game_over = True
                if CRASH_SOUND is not None:
                    CRASH_SOUND.play()
                break

    draw_flight_pipes()

    if isDebugMode:
        plane_rect = get_flight_plane_rect()
        no_fill()
        stroke(255, 0, 0)
        stroke_weight(2)
        rect(*plane_rect)
        for pipe in flight_pipes:
            rect(pipe["x"], 0, FLIGHT_PIPE_WIDTH, pipe["gap_top"])
            rect(
                pipe["x"],
                pipe["gap_top"] + FLIGHT_PIPE_GAP_H,
                FLIGHT_PIPE_WIDTH,
                GROUND_Y - (pipe["gap_top"] + FLIGHT_PIPE_GAP_H),
            )
        no_stroke()

    if millis() < airplane_warning_until_ms and not game_over:
        fill(*theme["accent"])
        text_size(20)
        text("Flight mode: stay left and dodge the pipes!", width // 2 - 170, 28)


def draw_rounded_rect_outline(x, y, w, h, radius, col, weight=2):
    # Rounded rectangle via lines + quarter arcs (API has no native rounded rect).
    stroke(*col)
    stroke_weight(weight)
    no_fill()
    line(x + radius, y, x + w - radius, y)
    line(x + radius, y + h, x + w - radius, y + h)
    line(x, y + radius, x, y + h - radius)
    line(x + w, y + radius, x + w, y + h - radius)
    arc(x + radius, y + radius, radius * 2, radius * 2, PI, PI + PI / 2)
    arc(x + w - radius, y + radius, radius * 2, radius * 2, PI + PI / 2, TWO_PI)
    arc(x + w - radius, y + h - radius, radius * 2, radius * 2, 0, PI / 2)
    arc(x + radius, y + h - radius, radius * 2, radius * 2, PI / 2, PI)
    no_stroke()


def point_in_rect(px, py, x, y, w, h):
    return x <= px <= x + w and y <= py <= y + h


def get_character_select_layout():
    card_w = 170
    card_h = 165
    gap = 26
    start_x = (width - (card_w * 3 + gap * 2)) // 2
    card_y = height // 2 + 92
    cards = []
    for idx in range(len(CHARACTER_ORDER)):
        x = start_x + idx * (card_w + gap)
        cards.append((idx, x, card_y, card_w, card_h))
    return cards


def get_start_button_rect():
    btn_w = 150
    btn_h = 44
    btn_x = width - btn_w - 36
    btn_y = height // 2 - 10
    return btn_x, btn_y, btn_w, btn_h


def draw_start_button(theme):
    btn_x, btn_y, btn_w, btn_h = get_start_button_rect()
    fill(255, 255, 255)
    no_stroke()
    rect(btn_x, btn_y, btn_w, btn_h)
    draw_rounded_rect_outline(btn_x, btn_y, btn_w, btn_h, 12, theme["accent"], 3)
    fill(*theme["accent"])
    text_size(24)
    text("Start", btn_x + 40, btn_y + 30)


def draw_character_select(theme):
    text_size(22)
    fill(*theme["text"])
    text("Kies character: pijl links/rechts", width // 2 - 160, height // 2 + 72)

    pulse = (math.sin(millis() / 180.0) + 1.0) * 0.5
    pulse_pad = int(5 + pulse * 6)
    pulse_weight = int(2 + pulse * 2)

    for idx, x, card_y, card_w, card_h in get_character_select_layout():
        character_key = CHARACTER_ORDER[idx]
        character = CHARACTER_CONFIG[character_key]

        fill(255, 255, 255)
        no_stroke()
        rect(x, card_y, card_w, card_h)
        draw_rounded_rect_outline(x, card_y, card_w, card_h, 14, theme["ground_line"], 2)

        preview = character["stand"]
        image(preview, x + 28, card_y + 16, 114, 96)

        fill(*theme["text"])
        text_size(20)
        text(character["label"], x + 46, card_y + 140)

        if idx == selected_character_idx:
            draw_rounded_rect_outline(
                x - pulse_pad,
                card_y - pulse_pad,
                card_w + pulse_pad * 2,
                card_h + pulse_pad * 2,
                18,
                theme["accent"],
                pulse_weight,
            )

    draw_start_button(theme)


def draw():
    global dino_y, velocity_y, on_ground, obstacle_x, score, game_over, game_started
    global is_ducking, bird_duck_scored, is_fast_falling, snake_hiss_played_for_current
    theme = get_theme()
    update_background_music()
    background(*theme["bg"])
    fill(*theme["ground_fill"])
    rect(0, GROUND_Y, width, 40)  # ground
    stroke(*theme["ground_line"])
    stroke_weight(2)
    line(0, GROUND_Y, width, GROUND_Y)
    no_stroke()

    if shared.show_info:
        shared.draw_info_screen(INFO_TEXT)
        fill(20)
        text_size(20)
        speed_mult = scroll_speed / BASE_SCROLL_SPEED
        text(f"Current level: {current_level}", 500, 120)
        text(f"Speed: {speed_mult:.2f}x", 500, 148)
        text_size(16)
        text("L: level +1, Shift+L: level -1", 500, 176)
        return

    if not game_started:
        draw_dino()
        fill(*theme["text"])
        text_size(44)
        text("Dino Game", width // 2 - 105, height // 2 - 55)
        text_size(22)
        text("Start: SPACE/A of klik Start", width // 2 - 150, height // 2 - 10)
        text("Spring: pijl omhoog", width // 2 - 110, height // 2 + 20)
        text("Duik: pijl omlaag (lucht = fast fall)", width // 2 - 188, height // 2 + 50)
        text("High jump: buk en spring binnen 0.5s", width // 2 - 190, height // 2 + 80)
        text("Info: I", width // 2 - 45, height // 2 + 110)
        draw_character_select(theme)
        draw_debug_overlay()
        return

    if flight_mode:
        update_and_draw_flight_mode(theme, update_world=(not game_paused and not game_over))
        draw_dino()
        if game_paused and not game_over:
            fill(40)
            text_size(34)
            text("Pauze", width // 2 - 55, height // 2 - 8)
            text_size(18)
            text("Druk op P om verder te gaan", width // 2 - 118, height // 2 + 22)
            draw_hud(theme)
            draw_debug_overlay()
            return
        if game_over:
            fill(255, 0, 0)
            text_size(40)
            text("Game Over!", width // 2 - 120, height // 2)
            draw_hud(theme, force_visible=True)
            fill(*theme["text"])
            text_size(22)
            text(f"Snelheid: x{round(scroll_speed / BASE_SCROLL_SPEED, 2)}", width - 230, 72)
            text("Druk op SPACE voor startscherm", width // 2 - 170, height // 2 + 40)
            draw_debug_overlay()
            return
        draw_hud(theme)
        draw_debug_overlay()
        return

    maybe_start_boss_encounter()
    if boss_state is not None:
        update_and_draw_boss_mode(theme, update_world=(not game_paused and not game_over))
        draw_dino()
        if game_paused and not game_over:
            fill(40)
            text_size(34)
            text("Pauze", width // 2 - 55, height // 2 - 8)
            text_size(18)
            text("Druk op P om verder te gaan", width // 2 - 118, height // 2 + 22)
            draw_hud(theme)
            draw_debug_overlay()
            return
        if game_over:
            fill(255, 0, 0)
            text_size(40)
            text("Game Over!", width // 2 - 120, height // 2)
            draw_hud(theme, force_visible=True)
            fill(*theme["text"])
            text_size(22)
            text(f"Snelheid: x{round(scroll_speed / BASE_SCROLL_SPEED, 2)}", width - 230, 72)
            text("Druk op SPACE voor startscherm", width // 2 - 170, height // 2 + 40)
            draw_debug_overlay()
            return
        draw_hud(theme)
        draw_debug_overlay()
        return

    # Draw obstacle
    obstacle_cfg = OBSTACLE_CONFIG[obstacle_type]
    obstacle_draw_x, obstacle_draw_y, obstacle_draw_w, obstacle_draw_h = get_obstacle_draw_rect()
    image(obstacle_cfg["img"], obstacle_draw_x, obstacle_draw_y, obstacle_draw_w, obstacle_draw_h)
    draw_dino()

    if game_paused:
        fill(40)
        text_size(34)
        text("Pauze", width // 2 - 55, height // 2 - 8)
        text_size(18)
        text("Druk op P om verder te gaan", width // 2 - 118, height // 2 + 22)
        draw_hud(theme)
        draw_debug_overlay()
        return

    if millis() < high_jump_warning_until_ms and game_started and not game_over:
        fill(*theme["accent"])
        text_size(20)
        text("Prepare for high jump: duck first then quickly jump.", width // 2 - 235, 28)
    if millis() < airplane_warning_until_ms and game_started and not game_over:
        fill(*theme["accent"])
        text_size(20)
        text("Jump on the airplane to start flight mode!", width // 2 - 170, 56)

    if not game_over:
        # Dino jump physics
        if not on_ground:
            gravity_now = GRAVITY + (FAST_FALL_EXTRA_GRAVITY if is_fast_falling else 0)
            velocity_y += gravity_now
            dino_y += velocity_y
            if dino_y >= DINO_Y:
                dino_y = DINO_Y
                velocity_y = 0
                on_ground = True
                is_fast_falling = False

        obstacle_x -= scroll_speed

        if obstacle_type == "snake" and is_snake_extended() and not snake_hiss_played_for_current:
            snake_hiss_played_for_current = True
            if HISS_SOUND is not None:
                HISS_SOUND.play()

        if obstacle_type == "bird_low":
            dino_hitbox = get_dino_hitbox()
            obstacle_hitbox = get_obstacle_hitbox()
            if (
                is_ducking and on_ground and
                obstacle_hitbox[0] < dino_hitbox[0] + dino_hitbox[2] and
                obstacle_hitbox[0] + obstacle_hitbox[2] > dino_hitbox[0]
            ):
                bird_duck_scored = True

        obstacle_draw_x, _, obstacle_draw_w, _ = get_obstacle_draw_rect()
        if obstacle_draw_x < -obstacle_draw_w:
            gained_points = obstacle_cfg["points"]
            if obstacle_cfg.get("requires_duck_score", False) and not bird_duck_scored:
                gained_points = 0
            score += gained_points
            update_level_from_score()
            spawn_obstacle()

        if obstacle_type == "airplane_pickup":
            dino_hitbox = get_dino_hitbox()
            plane_hitbox = get_obstacle_hitbox()
            dino_bottom = dino_hitbox[1] + dino_hitbox[3]
            plane_top = plane_hitbox[1]
            overlap_x = (
                dino_hitbox[0] < plane_hitbox[0] + plane_hitbox[2] and
                dino_hitbox[0] + dino_hitbox[2] > plane_hitbox[0]
            )
            landing_on_top = overlap_x and velocity_y >= 0 and plane_top - 10 <= dino_bottom <= plane_top + 18
            if landing_on_top:
                is_ducking = False
                is_fast_falling = False
                velocity_y = 0
                on_ground = False
                start_flight_mode()
                draw_dino()
                draw_hud(theme)
                return

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
        draw_hud(theme, force_visible=True)
        fill(*theme["text"])
        text_size(22)
        text(f"Snelheid: x{round(scroll_speed / BASE_SCROLL_SPEED, 2)}", width - 230, 72)
        text("Druk op SPACE voor startscherm", width // 2 - 170, height // 2 + 40)
        draw_debug_overlay()
        return

    draw_hud(theme)
    draw_debug_overlay()

def key_pressed():
    global velocity_y, on_ground, game_started, isDebugMode, is_ducking
    global game_paused, selected_character_idx, active_character_key
    global duck_jump_expires_ms, is_fast_falling
    global fly_left_pressed, fly_right_pressed, fly_up_pressed, fly_down_pressed
    pressed_key = key.lower() if isinstance(key, str) else key
    shared.handle_common_keys(pressed_key, key_code, info_text=INFO_TEXT)
    if pressed_key in ("i", "s"):
        update_background_music(force=True)
    if pressed_key in ("i", "q", "s"):
        return

    if shared.show_info:
        if pressed_key == "l":
            if key == "L":
                debug_step_level(-1)
            else:
                debug_step_level(1)
        return

    if key in ("d", "D"):
        isDebugMode = not isDebugMode
        return

    if isDebugMode and game_started and not game_over and pressed_key == "l":
        if key == "L":
            debug_step_level(-1)
        else:
            debug_step_level(1)
        return

    if key in ("p", "P") and game_started and not game_over:
        game_paused = not game_paused
        return

    if game_over and key == " ":
        if active_character_key in CHARACTER_ORDER:
            selected_character_idx = CHARACTER_ORDER.index(active_character_key)
        reset_game(show_splash=True)
        return

    if not game_started and key_code == pygame.K_LEFT:
        selected_character_idx = (selected_character_idx - 1) % len(CHARACTER_ORDER)
        return

    if not game_started and key_code == pygame.K_RIGHT:
        selected_character_idx = (selected_character_idx + 1) % len(CHARACTER_ORDER)
        return

    if not game_started and key in (" ", "a", "A"):
        start_game_from_selection()
        return

    if game_paused:
        return

    if game_started and not game_over and key == " " and boss_state is not None:
        fire_player_weapon()
        return

    if game_started and flight_mode and not game_over:
        if key_code == pygame.K_LEFT:
            fly_left_pressed = True
            return
        if key_code == pygame.K_RIGHT:
            fly_right_pressed = True
            return
        if key_code == pygame.K_UP:
            fly_up_pressed = True
            return
        if key_code == pygame.K_DOWN:
            fly_down_pressed = True
            return
        return

    if game_started and not game_over and key_code == pygame.K_DOWN:
        if on_ground:
            is_ducking = True
            duck_jump_expires_ms = millis() + HIGH_JUMP_WINDOW_MS
        else:
            is_fast_falling = True
        return

    if game_started and not game_over and key_code == pygame.K_UP and on_ground:
        # Buk-spring binnen half seconde geeft high jump.
        now = millis()
        jump_velocity = HIGH_JUMP_VELOCITY if now <= duck_jump_expires_ms else JUMP_VELOCITY
        is_ducking = False
        velocity_y = jump_velocity
        on_ground = False
        is_fast_falling = False
        duck_jump_expires_ms = 0
        if JUMP_SOUND is not None:
            JUMP_SOUND.play()


def key_released(released_key):
    global is_ducking, duck_jump_expires_ms, is_fast_falling
    global fly_left_pressed, fly_right_pressed, fly_up_pressed, fly_down_pressed
    if flight_mode:
        if released_key == pygame.K_LEFT:
            fly_left_pressed = False
        elif released_key == pygame.K_RIGHT:
            fly_right_pressed = False
        elif released_key == pygame.K_UP:
            fly_up_pressed = False
        elif released_key == pygame.K_DOWN:
            fly_down_pressed = False
        return

    if released_key == pygame.K_DOWN:
        if on_ground:
            duck_jump_expires_ms = millis() + HIGH_JUMP_WINDOW_MS
        is_ducking = False
        is_fast_falling = False


def mouse_clicked(x, y, button):
    global selected_character_idx
    if button != 1:
        return
    if shared.show_info:
        return
    if game_started:
        return

    for idx, card_x, card_y, card_w, card_h in get_character_select_layout():
        if point_in_rect(x, y, card_x, card_y, card_w, card_h):
            selected_character_idx = idx
            return

    btn_x, btn_y, btn_w, btn_h = get_start_button_rect()
    if point_in_rect(x, y, btn_x, btn_y, btn_w, btn_h):
        start_game_from_selection()


def draw_dino():
    if flight_mode:
        plane_x, plane_y, plane_w, plane_h = get_flight_plane_rect()
        image(AIRPLANE_IMG, plane_x, plane_y, plane_w, plane_h)
        if isDebugMode:
            no_fill()
            stroke(255, 0, 0)
            stroke_weight(2)
            rect(plane_x, plane_y, plane_w, plane_h)
            no_stroke()
        return

    dino_h = DUCK_H if (is_ducking and on_ground and not game_over) else DINO_H
    dino_y_draw = get_dino_draw_y()
    character = CHARACTER_CONFIG[get_current_character_key()]
    draw_x = DINO_X
    draw_w = DINO_W
    draw_h = dino_h
    if game_over:
        dino_sprite = character["oops"]
        if get_current_character_key() == "cowboy":
            # Cowboy falls backward and lies on the ground.
            draw_x = DINO_X - 10
            draw_w = 88
            draw_h = 40
            dino_y_draw = GROUND_Y - draw_h
    elif is_ducking and on_ground:
        dino_sprite = character["duck"]
    elif (
        get_current_character_key() == "cowboy" and
        game_started and
        not game_paused and
        on_ground
    ):
        # Simple walk cycle for cowboy: alternate stand/run frames.
        run_phase = int(millis() / 150) % 2
        dino_sprite = character["run"] if run_phase else character["stand"]
    else:
        dino_sprite = character["stand"]
    image(dino_sprite, draw_x, dino_y_draw, draw_w, draw_h)
    if isDebugMode:
        no_fill()
        stroke(255, 0, 0)
        stroke_weight(2)
        rect(*get_dino_hitbox())
        no_stroke()

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        try:
            pygame.quit()
        except Exception:
            pass
