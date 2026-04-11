from processing import run, size, frame_rate, title, background, fill, rect, line, arc
from processing import image, text_size, text, load_image, no_fill, stroke, stroke_weight, no_stroke, millis
from processing import width, height, key, key_code, random
from processing import PI, TWO_PI
import pygame
import shared
import math
import os

# Dino game assets
DINO_IMG = load_image("assets/dino-transparant.png")
DINO_OOPS_IMG = load_image("assets/dino-oops-transparant.png")
DINO_DUCK_IMG = load_image("assets/dino-duck-transparant.png")
COWBOY_IMG = load_image("assets/cowboy-transparant.png")
COWBOY_RUN_IMG = load_image("assets/cowboy-run-transparant.png")
COWBOY_FALL_IMG = load_image("assets/pc/cowboy-fall-transparant.png")
COWBOY_DUCK_IMG = load_image("assets/pc/cowboy-duck-transparant.png")
ROADRUNNER_IMG = load_image("assets/roadrunner-transparant.png")
ROADRUNNER_OOPS_IMG = load_image("assets/roadrunner-oops-transparant.png")
ROADRUNNER_DUCK_IMG = load_image("assets/roadrunner-duck-transparant.png")
AIRPLANE_IMG = load_image("assets/airplane-transparant.png")
BIRD_IMG = load_image("assets/obstacles/bird-transparant.png")
SNAKE_IMG = load_image("assets/snake-transparant.png")
EXPLOSION_IMG = load_image("assets/explosion.png")
EXPLOSION_FRAMES = [
    load_image(f"assets/explosion-frame-{idx:02d}.png")
    for idx in range(12)
]
CACTUS_IMGS = [
    load_image("assets/obstacles/cactus-transparant.png"),
    load_image("assets/obstacles/3Cacti-transparant.png")
]

# Richtingsvarianten (naar rechts kijken) voor specifieke enemies/bosses.
BIRD_RIGHT_IMG = pygame.transform.flip(BIRD_IMG, True, False)
GIANT_DINO_RIGHT_IMG = pygame.transform.flip(DINO_IMG, True, False)

# Dino properties
DINO_X = 100
DINO_Y = 400
DINO_W = 60
DINO_H = 60
DUCK_H = 30
GRAVITY = 1.2
JUMP_VELOCITY = -18
HIGH_JUMP_VELOCITY = -22
POWERUP_HIGH_JUMP_VELOCITY = -26
HIGH_JUMP_POWERUP_MAX_CHARGES = 3
HIGH_JUMP_WINDOW_MS = 500
FAST_FALL_EXTRA_GRAVITY = 2.0
BASE_SCROLL_SPEED = 6.0
LEVEL_SCORE_STEP = 10
LEVEL_SPEED_FACTOR = 1.1
LEVEL_BLINK_DURATION_MS = 1200
LEVEL_BLINK_INTERVAL_MS = 120
MAX_LEVEL = 10
HIGH_JUMP_WARNING_DURATION_MS = 1800
HIGH_JUMP_POWERUP_NOTICE_MS = 1400
WEAPON_POWERUP_NOTICE_MS = 1600
WATER_WARNING_DURATION_MS = 1800
AIRPLANE_WARNING_DURATION_MS = 1800
LEVEL_NAME_NOTICE_MS = 2200
WIND_SWIRL_EFFECT_MS = 1800
WIND_SWIRL_SLOW_GRAVITY = 0.18
WIND_SWIRL_MAX_FALL_SPEED = 1.6
FLIGHT_PIPE_GAP_H = 150
FLIGHT_PIPE_WIDTH = 72
FLIGHT_PIPE_SPAWN_BASE_MS = 1500
FLIGHT_PLANE_SPEED = 5.0
FLIGHT_PIPE_POINTS = 2
PLAYER_SHOOT_COOLDOWN_MS = 180
CACTUS_SHOT_VERTICAL_BOOST = 1.45
CACTUS_SHOT_UPWARD_OFFSET_PX = 12
BOSS_INTRO_DURATION_MS = 1700
BOSS_PLAYER_SPEED = 5.5
BOSS_LEVEL_ORDER = (4, 7, 10)
BOSS_REWARD_POINTS = {
    4: 8,
    7: 12,
    10: 20,
}
FINAL_BOSS_DEFEAT_DURATION_MS = 2600
FINAL_BOSS_BLAST_INTERVAL_MS = 110
FINAL_BOSS_BLAST_LIFE_MS = 620
COYOTE_TNT_THROW_SPEED = 6.8
COYOTE_TNT_THROW_GRAVITY = 0.34
COYOTE_TNT_BLAST_MS = 260
COYOTE_PIT_WIDTH = 86
COYOTE_PIT_LIFE_MS = 6500
COYOTE_MAX_PITS = 3
JACKET_BONUS_HP = 3
PLAYER_DAMAGE_COOLDOWN_MS = 750
MAX_PROJECTILES_PER_SIDE = 10
COIN_SCORE_VALUE = 1
MENU_MUSIC_PATH = "assets/audio/loading-atmosphere.wav"
GAME_MUSIC_PATH = "assets/audio/pixel-leap.wav"
MUSIC_VOLUME = 0.35
SCREENSHOT_NOTICE_MS = 2200
GROUND_Y = 460

LEVEL_NAMES = {
    1: "Enter Cactus Land...",
    2: "Snake Sands",
    3: "High Jump Ridge",
    4: "Bird Boss Canyon",
    5: "Fly away",
    6: "Storm track",
    7: "Cactus Fortress",
    8: "Wild Flats",
    9: "Last Stretch",
    10: "Giant Town",
}

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
    "high_jump_powerup": {
        "img": None,
        "w": 28,
        "h": 28,
        "y": 408,
        "hitbox_insets": (3, 3, 3, 3),
        "points": 0,
    },
    "weapon_powerup": {
        "img": None,
        "w": 34,
        "h": 26,
        "y": 404,
        "hitbox_insets": (3, 3, 3, 3),
        "points": 0,
    },
    "coin": {
        "img": None,
        "w": 20,
        "h": 20,
        "y": 360,
        "hitbox_insets": (2, 2, 2, 2),
        "points": 0,
    },
    "water_lily": {
        "img": None,
        "w": 184,
        "h": 34,
        "y": 426,
        "hitbox_insets": (0, 0, 0, 0),
        "points": 3,
    },
    "wind_swirl": {
        "img": None,
        "w": 76,
        "h": 96,
        "y": 324,
        "hitbox_insets": (10, 10, 8, 8),
        "points": 3,
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
        "img": BIRD_RIGHT_IMG,
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
    "i -> instructiescherm",
    "m -> muziek aan/uit",
    "s -> sound effects aan/uit",
    "q -> in game: menu, in menu: quit prompt",
    "d -> debug modus (toon hitbox)",
    "l -> level omhoog (debug mode)",
    "L -> level omlaag (debug mode)",
    "p -> pauze",
    "space/a -> start of schieten (boss)",
    "k -> screenshot opslaan",
    "pijltjes -> bewegen / springen / duiken",
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
coin_count = 0
player_x = float(DINO_X)
JUMP_SOUND = None
ROADRUNNER_JUMP_SOUND = None
CRASH_SOUND = None
HISS_SOUND = None
SPLASH_SOUND = None
FIRE_PLAYER_SOUND = None
FIRE_ENEMY_SOUND = None
BOSS_EXPLOSION_SOUND = None
COIN_SOUND = None
isDebugMode = False
is_ducking = False
game_paused = False
selected_character_idx = 0
active_character_key = "dino"
checkpoint_level_by_character = {
    character_key: 1 for character_key in CHARACTER_ORDER
}
duck_jump_expires_ms = 0
is_fast_falling = False
current_level = 1
scroll_speed = BASE_SCROLL_SPEED
next_level_score = LEVEL_SCORE_STEP
level_blink_until_ms = 0
high_jump_warning_until_ms = 0
high_jump_powerup_warning_until_ms = 0
weapon_powerup_warning_until_ms = 0
water_warning_until_ms = 0
airplane_warning_until_ms = 0
pending_airplane_spawn = False
queued_obstacle_after_powerup = None
high_jump_powerup_charges = 0
pending_weapon_powerup_level = 0
weapon_powerup_ready = False
weapon_powerup_level = 0
coin_spawn_y = 360
flight_mode = False
flight_plane_x = 0.0
flight_plane_y = 0.0
flight_pipe_spawn_due_ms = 0
flight_pipes = []
fly_left_pressed = False
fly_right_pressed = False
fly_up_pressed = False
fly_down_pressed = False
boss_left_pressed = False
boss_right_pressed = False
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
player_max_hp = 1
player_hp = 1
player_damage_cooldown_until_ms = 0
screenshot_notice_until_ms = 0
screenshot_notice_text = ""
quit_confirm_active = False
announcement_font_cache = {}
level_name_announcement_until_ms = 0
level_name_announcement_text = ""
wind_swirl_effect_until_ms = 0


def reset_game(show_splash=False):
    global dino_y, velocity_y, on_ground, score, coin_count, game_over, game_started
    global player_x
    global is_ducking, game_paused, bird_duck_scored, duck_jump_expires_ms, is_fast_falling
    global current_level, scroll_speed, next_level_score, level_blink_until_ms
    global high_jump_warning_until_ms, high_jump_powerup_warning_until_ms
    global weapon_powerup_warning_until_ms, water_warning_until_ms
    global airplane_warning_until_ms, pending_airplane_spawn, queued_obstacle_after_powerup
    global high_jump_powerup_charges
    global pending_weapon_powerup_level, weapon_powerup_ready, weapon_powerup_level
    global coin_spawn_y
    global flight_mode, flight_plane_x, flight_plane_y, flight_pipe_spawn_due_ms, flight_pipes
    global fly_left_pressed, fly_right_pressed, fly_up_pressed, fly_down_pressed
    global boss_left_pressed, boss_right_pressed
    global snake_hiss_played_for_current
    global player_projectiles, player_shot_cooldown_until_ms
    global boss_state, boss_intro_until_ms, boss_completed
    global player_max_hp, player_hp, player_damage_cooldown_until_ms
    global screenshot_notice_until_ms, screenshot_notice_text
    global quit_confirm_active
    global level_name_announcement_until_ms, level_name_announcement_text
    global wind_swirl_effect_until_ms
    dino_y = DINO_Y
    velocity_y = 0
    on_ground = True
    player_x = float(DINO_X)
    score = 0
    coin_count = 0
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
    high_jump_powerup_warning_until_ms = 0
    weapon_powerup_warning_until_ms = 0
    water_warning_until_ms = 0
    airplane_warning_until_ms = 0
    pending_airplane_spawn = False
    queued_obstacle_after_powerup = None
    high_jump_powerup_charges = 0
    pending_weapon_powerup_level = 0
    weapon_powerup_ready = False
    weapon_powerup_level = 0
    coin_spawn_y = 360
    flight_mode = False
    flight_plane_x = 0.0
    flight_plane_y = 0.0
    flight_pipe_spawn_due_ms = 0
    flight_pipes = []
    fly_left_pressed = False
    fly_right_pressed = False
    fly_up_pressed = False
    fly_down_pressed = False
    boss_left_pressed = False
    boss_right_pressed = False
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
    player_max_hp = 1
    player_hp = 1
    player_damage_cooldown_until_ms = 0
    screenshot_notice_until_ms = 0
    screenshot_notice_text = ""
    quit_confirm_active = False
    level_name_announcement_until_ms = 0
    level_name_announcement_text = ""
    wind_swirl_effect_until_ms = 0
    spawn_obstacle("cactus_low")


def show_level_name_announcement(level=None):
    global level_name_announcement_until_ms, level_name_announcement_text
    shown_level = current_level if level is None else level
    level_name = LEVEL_NAMES.get(shown_level)
    if level_name is None:
        return
    level_name_announcement_text = f"WELCOME IN LEVEL {shown_level}:\n{level_name}"
    level_name_announcement_until_ms = millis() + LEVEL_NAME_NOTICE_MS


def is_wind_swirl_active():
    return millis() < wind_swirl_effect_until_ms


def update_player_vertical_motion():
    global dino_y, velocity_y, on_ground, is_fast_falling
    if on_ground:
        return

    gravity_now = GRAVITY + (FAST_FALL_EXTRA_GRAVITY if is_fast_falling else 0)
    if is_wind_swirl_active() and velocity_y >= 0:
        gravity_now = min(gravity_now, WIND_SWIRL_SLOW_GRAVITY)

    velocity_y += gravity_now
    if is_wind_swirl_active() and velocity_y > WIND_SWIRL_MAX_FALL_SPEED:
        velocity_y = WIND_SWIRL_MAX_FALL_SPEED

    dino_y += velocity_y
    if dino_y >= DINO_Y:
        dino_y = DINO_Y
        velocity_y = 0
        on_ground = True
        is_fast_falling = False


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


def capture_screenshot():
    global screenshot_notice_until_ms, screenshot_notice_text
    surface = pygame.display.get_surface()
    if surface is None:
        screenshot_notice_text = "Screenshot mislukt (geen actieve surface)"
        screenshot_notice_until_ms = millis() + SCREENSHOT_NOTICE_MS
        return None
    os.makedirs("assets/screenshots", exist_ok=True)
    stamp = int(millis())
    filename = f"level-{current_level:02d}-score-{int(score):03d}-{stamp}.png"
    path = os.path.join("assets", "screenshots", filename)
    try:
        pygame.image.save(surface, path)
    except Exception:
        screenshot_notice_text = "Screenshot mislukt (opslaan)"
        screenshot_notice_until_ms = millis() + SCREENSHOT_NOTICE_MS
        return None
    screenshot_notice_text = f"Screenshot: {path}"
    screenshot_notice_until_ms = millis() + SCREENSHOT_NOTICE_MS
    return path


def play_sfx(sound):
    if sound is None:
        return
    if not shared.sound_enabled:
        return
    try:
        sound.play()
    except Exception:
        pass


def get_jump_sound():
    if (
        get_current_character_key() == "roadrunner"
        and ROADRUNNER_JUMP_SOUND is not None
    ):
        return ROADRUNNER_JUMP_SOUND
    return JUMP_SOUND


def setup():
    global JUMP_SOUND, ROADRUNNER_JUMP_SOUND, CRASH_SOUND, HISS_SOUND
    global SPLASH_SOUND, FIRE_PLAYER_SOUND, FIRE_ENEMY_SOUND
    global BOSS_EXPLOSION_SOUND
    global COIN_SOUND
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
        ROADRUNNER_JUMP_SOUND = pygame.mixer.Sound("assets/audio/weeh.wav")
    except Exception:
        ROADRUNNER_JUMP_SOUND = None

    try:
        CRASH_SOUND = pygame.mixer.Sound("assets/audio/crash.wav")
    except Exception:
        CRASH_SOUND = None

    try:
        HISS_SOUND = pygame.mixer.Sound("assets/audio/hiss.wav")
    except Exception:
        HISS_SOUND = None

    try:
        SPLASH_SOUND = pygame.mixer.Sound("assets/audio/splash.wav")
    except Exception:
        SPLASH_SOUND = None

    try:
        FIRE_PLAYER_SOUND = pygame.mixer.Sound("assets/audio/fire-player.wav")
    except Exception:
        FIRE_PLAYER_SOUND = None

    try:
        FIRE_ENEMY_SOUND = pygame.mixer.Sound("assets/audio/fire-enemy.wav")
    except Exception:
        FIRE_ENEMY_SOUND = None

    try:
        BOSS_EXPLOSION_SOUND = pygame.mixer.Sound("assets/audio/boss-explosion.wav")
    except Exception:
        BOSS_EXPLOSION_SOUND = None

    try:
        COIN_SOUND = pygame.mixer.Sound("assets/audio/ping.wav")
    except Exception:
        COIN_SOUND = None

    update_background_music(force=True)


def get_player_x():
    return player_x


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

    player_draw_x = get_player_x()
    return (
        player_draw_x + inset_left,
        dino_draw_y + inset_top + y_offset,
        DINO_W - inset_left - inset_right,
        dino_h - inset_top - inset_bottom,
    )


def choose_obstacle_type():
    global queued_obstacle_after_powerup
    if pending_weapon_powerup_level > 0 and not weapon_powerup_ready:
        return "weapon_powerup"

    if pending_airplane_spawn:
        return "airplane_pickup"

    if queued_obstacle_after_powerup is not None:
        queued_type = queued_obstacle_after_powerup
        queued_obstacle_after_powerup = None
        return queued_type

    chosen = "cactus_low"

    # Level 1: nog geen slang.
    if current_level < 2:
        roll = int(random(0, 100))
        if roll < 52:
            chosen = "cactus_low"
        elif roll < 84:
            chosen = "cactus_high"
        else:
            chosen = "bird_low"

    # Level 2: slang komt erbij.
    elif current_level < 3:
        roll = int(random(0, 100))
        if roll < 36:
            chosen = "cactus_low"
        elif roll < 66:
            chosen = "cactus_high"
        elif roll < 84:
            chosen = "snake"
        else:
            chosen = "bird_low"

    else:
        roll = int(random(0, 100))
        if current_level == 6:
            # Vrij level-slot: water met leliebladen verschijnt hier als extra mechanic.
            if roll < 18:
                chosen = "water_lily"
            elif roll < 45:
                chosen = "cactus_low"
            elif roll < 62:
                chosen = "cactus_high"
            elif roll < 72:
                chosen = "cactus_tower"
            elif roll < 86:
                chosen = "snake"
            else:
                chosen = "bird_low"
        else:
            if roll < 35:
                chosen = "cactus_low"
            elif roll < 58:
                chosen = "cactus_high"
            elif roll < 68:
                chosen = "cactus_tower"
            elif roll < 82:
                chosen = "snake"
            else:
                chosen = "bird_low"

    # Laat vóór grotere cactussen eerst een High Jump powerup verschijnen.
    if chosen in ("cactus_high", "cactus_tower") and high_jump_powerup_charges <= 0:
        queued_obstacle_after_powerup = chosen
        return "high_jump_powerup"

    # Muntje kan vóór een normaal obstakel spawnen en gebruikt dezelfde collision flow.
    if chosen in ("cactus_low", "cactus_high", "cactus_tower", "snake", "bird_low"):
        if int(random(0, 100)) < 18:
            queued_obstacle_after_powerup = chosen
            return "coin"

    return chosen


def spawn_obstacle(force_type=None):
    global obstacle_x, obstacle_type, bird_duck_scored
    global high_jump_warning_until_ms, high_jump_powerup_warning_until_ms
    global weapon_powerup_warning_until_ms, water_warning_until_ms
    global airplane_warning_until_ms, pending_airplane_spawn
    global coin_spawn_y
    global snake_hiss_played_for_current
    obstacle_type = force_type or choose_obstacle_type()
    obstacle_x = width + random(100, 300)
    bird_duck_scored = False
    snake_hiss_played_for_current = False
    if obstacle_type == "airplane_pickup":
        pending_airplane_spawn = False
        airplane_warning_until_ms = millis() + AIRPLANE_WARNING_DURATION_MS
    if obstacle_type == "weapon_powerup":
        weapon_powerup_warning_until_ms = millis() + WEAPON_POWERUP_NOTICE_MS
    if obstacle_type == "coin":
        coin_ys = [332, 360, 392]
        coin_spawn_y = coin_ys[int(random(0, len(coin_ys)))]
    if obstacle_type == "water_lily":
        water_warning_until_ms = millis() + WATER_WARNING_DURATION_MS
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
    save_character_checkpoint(current_level)


def is_snake_extended():
    if obstacle_type != "snake":
        return False
    return obstacle_x < get_player_x() + 220


def get_obstacle_draw_rect():
    cfg = OBSTACLE_CONFIG[obstacle_type]
    draw_x = obstacle_x
    if obstacle_type == "coin":
        draw_y = coin_spawn_y
    else:
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


def save_character_checkpoint(level=None, character_key=None):
    checkpoint_character_key = character_key or active_character_key
    checkpoint_level = current_level if level is None else level
    checkpoint_level_by_character[checkpoint_character_key] = max(
        1,
        min(MAX_LEVEL, int(checkpoint_level)),
    )


def restore_character_checkpoint(character_key):
    global current_level, score, scroll_speed, next_level_score
    checkpoint_level = checkpoint_level_by_character.get(character_key, 1)
    current_level = checkpoint_level
    score = max(0, (checkpoint_level - 1) * LEVEL_SCORE_STEP)
    scroll_speed = BASE_SCROLL_SPEED * (LEVEL_SPEED_FACTOR ** (current_level - 1))
    next_level_score = current_level * LEVEL_SCORE_STEP


def start_game_from_selection():
    global active_character_key
    active_character_key = get_selected_character_key()
    reset_game(show_splash=False)
    restore_character_checkpoint(active_character_key)


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
        save_character_checkpoint(current_level)
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
    save_character_checkpoint(current_level)

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

    if kind == "tnt_blast":
        fill(238, 96, 42)
        rect(x, y, w, h)
        fill(255, 210, 90)
        rect(x + 6, y + 6, max(4, w - 12), max(4, h - 12))
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
    if not weapon_powerup_ready:
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
    projectile_x = get_player_x() + DINO_W - 4
    projectile.update({
        "x": projectile_x,
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
        target_x = boss_state["x"] + (boss_state["w"] * 0.5)
        target_y = boss_state["y"] + (boss_state["h"] * 0.5)
        vertical_boost = 1.0

        if boss_state["type"] == "cactus_miniboss":
            # Mik hoger op de bovenste nog levende tak zodat top-armen beter raakbaar zijn.
            branch_rects = get_cactus_branch_rects(boss_state)
            living_branches = [
                branch_rects[idx]
                for idx, hp in enumerate(boss_state["branch_hp"])
                if hp > 0
            ]
            if living_branches:
                top_branch = min(living_branches, key=lambda r: r[1])
                target_x = top_branch[0] + (top_branch[2] * 0.6)
                target_y = top_branch[1] + (top_branch[3] * 0.45)
            target_y -= CACTUS_SHOT_UPWARD_OFFSET_PX
            vertical_boost = CACTUS_SHOT_VERTICAL_BOOST

        travel_px = max(40.0, target_x - projectile_x)
        travel_time = travel_px / max(0.1, profile["speed"])
        base_vy = (target_y - projectile_y) / max(0.1, travel_time)
        projectile["vy"] = base_vy * vertical_boost
    play_sfx(FIRE_PLAYER_SOUND)
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


def draw_cactus_spines(area_x, area_y, area_w, area_h, step_x=14, step_y=16):
    stroke(220, 242, 196)
    stroke_weight(1)
    row = 0
    y_cursor = int(area_y + 6)
    while y_cursor < int(area_y + area_h - 5):
        x_cursor = int(area_x + 6 + (row % 2) * 4)
        while x_cursor < int(area_x + area_w - 8):
            line(x_cursor, y_cursor, x_cursor + 3, y_cursor - 2)
            line(x_cursor + 2, y_cursor + 1, x_cursor + 5, y_cursor + 3)
            x_cursor += step_x
        y_cursor += step_y
        row += 1
    no_stroke()


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
        "phase": "laugh",
        "pit_traps": [],
        "vx": 1.5 if form_name == "ReuzenCoyote" else 0.0,
        "min_x": float(width - 320),
        "max_x": float(width - 68),
        "last_attack_ms": now,
        "enemy_weapon_kind": profile["kind"],
    }


def get_coyote_phase(boss):
    hit_ratio = boss["hits_taken"] / max(1, boss["hits_required"])
    if hit_ratio < (1 / 3):
        return "laugh"
    if hit_ratio < (2 / 3):
        return "angry"
    return "nervous"


def update_coyote_phase_state(boss):
    if boss.get("form") != "ReuzenCoyote":
        return
    phase = get_coyote_phase(boss)
    boss["phase"] = phase
    if phase == "laugh":
        boss["attack_interval_ms"] = 860
        boss["vx"] = 1.3 if boss["vx"] >= 0 else -1.3
    elif phase == "angry":
        boss["attack_interval_ms"] = 710
        boss["vx"] = 1.9 if boss["vx"] >= 0 else -1.9
    else:
        boss["attack_interval_ms"] = 560
        boss["vx"] = 2.6 if boss["vx"] >= 0 else -2.6


def spawn_coyote_pit(boss, center_x):
    pit_left = max(24.0, min(width - COYOTE_PIT_WIDTH - 24.0, center_x - (COYOTE_PIT_WIDTH / 2)))
    pits = boss.setdefault("pit_traps", [])
    pits.append({
        "x": pit_left,
        "w": COYOTE_PIT_WIDTH,
        "expires_at": millis() + COYOTE_PIT_LIFE_MS,
    })
    if len(pits) > COYOTE_MAX_PITS:
        del pits[0:len(pits) - COYOTE_MAX_PITS]


def update_coyote_pits(boss):
    if boss.get("form") != "ReuzenCoyote":
        return
    pits = boss.setdefault("pit_traps", [])
    now = millis()
    pits[:] = [pit for pit in pits if pit["expires_at"] > now]


def player_over_coyote_pit(boss):
    if boss.get("form") != "ReuzenCoyote":
        return False
    player_hitbox = get_dino_hitbox()
    player_center_x = player_hitbox[0] + (player_hitbox[2] / 2)
    for pit in boss.get("pit_traps", []):
        if pit["x"] <= player_center_x <= pit["x"] + pit["w"]:
            return True
    return False


def draw_coyote_pits(boss, theme):
    if boss.get("form") != "ReuzenCoyote":
        return
    for pit in boss.get("pit_traps", []):
        pit_x = int(pit["x"])
        pit_w = int(pit["w"])
        fill(*theme["bg"])
        rect(pit_x, GROUND_Y - 2, pit_w, 42)
        fill(54, 34, 22)
        rect(pit_x + 4, GROUND_Y + 6, max(8, pit_w - 8), 20)
        stroke(*theme["ground_line"])
        stroke_weight(2)
        line(pit_x - 2, GROUND_Y, pit_x + 10, GROUND_Y)
        line(pit_x + pit_w - 10, GROUND_Y, pit_x + pit_w + 2, GROUND_Y)
        no_stroke()


def maybe_start_boss_encounter():
    global boss_state, boss_intro_until_ms, player_shot_cooldown_until_ms
    global pending_weapon_powerup_level
    if boss_state is not None or game_over or not game_started or game_paused or flight_mode:
        return

    # Skip older boss tiers once the player is already in a higher tier.
    # This keeps boss order aligned with the current level (e.g. level 7 starts with cactus).
    for level in BOSS_LEVEL_ORDER:
        if current_level > level:
            boss_completed[level] = True

    for level in BOSS_LEVEL_ORDER:
        if current_level >= level and not boss_completed[level]:
            has_weapon_for_level = weapon_powerup_ready and weapon_powerup_level == level
            if not has_weapon_for_level:
                pending_weapon_powerup_level = level
                return
            pending_weapon_powerup_level = 0
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
        image(BIRD_RIGHT_IMG, x, y, w, h)
        return

    if boss["type"] == "cactus_miniboss":
        trunk_x = x + 22
        trunk_y = y + 16
        trunk_w = w - 30
        trunk_h = h - 18

        # Outer contour
        fill(38, 126, 48)
        rect(trunk_x - 6, trunk_y + 8, trunk_w + 8, trunk_h - 10)
        arc(trunk_x + (trunk_w // 2) - 1, trunk_y + 8, trunk_w + 8, 28, PI, TWO_PI)

        # Inner body + highlight
        fill(58, 168, 70)
        rect(trunk_x + 2, trunk_y + 14, trunk_w - 8, trunk_h - 22)
        arc(trunk_x + (trunk_w // 2) - 2, trunk_y + 14, trunk_w - 8, 22, PI, TWO_PI)
        fill(71, 186, 84)
        rect(trunk_x + 12, trunk_y + 28, trunk_w - 32, trunk_h - 52)
        arc(trunk_x + (trunk_w // 2) - 4, trunk_y + 28, trunk_w - 32, 18, PI, TWO_PI)

        # Vertical ribs on the cactus body.
        stroke(48, 145, 58)
        stroke_weight(2)
        line(trunk_x + 18, trunk_y + 18, trunk_x + 18, trunk_y + trunk_h - 16)
        line(trunk_x + trunk_w // 2, trunk_y + 16, trunk_x + trunk_w // 2, trunk_y + trunk_h - 14)
        line(trunk_x + trunk_w - 22, trunk_y + 18, trunk_x + trunk_w - 22, trunk_y + trunk_h - 16)
        no_stroke()
        draw_cactus_spines(trunk_x + 4, trunk_y + 18, trunk_w - 12, trunk_h - 24, step_x=16, step_y=20)

        branch_rects = get_cactus_branch_rects(boss)
        for idx, branch_hp in enumerate(boss["branch_hp"]):
            bx, by, bw, bh = branch_rects[idx]
            if branch_hp <= 0:
                # Remaining stump when a branch is gone.
                fill(44, 133, 53)
                rect(int(trunk_x - 4), int(by + 2), 8, int(bh - 3))
                continue

            # Branch crumbles gradually: less HP = shorter arm.
            hp_ratio = max(0.2, min(1.0, branch_hp / 5.0))
            arm_w = int(max(10, bw * hp_ratio))
            arm_x = int(bx + (bw - arm_w))
            arm_y = int(by + 1)
            arm_h = int(max(8, bh - 2))

            fill(45, 140, 55)
            rect(arm_x, arm_y, arm_w, arm_h)
            fill(61, 172, 71)
            rect(arm_x + 2, arm_y + 2, max(3, arm_w - 4), max(3, arm_h - 4))
            # Rounded branch tip.
            arc(arm_x + 1, arm_y + (arm_h // 2), arm_h, arm_h, PI / 2, PI + PI / 2)
            draw_cactus_spines(arm_x + 2, arm_y + 1, max(6, arm_w - 4), arm_h - 2, step_x=10, step_y=8)
        return

    # Final boss
    if boss["form"] == "ReuzenDino":
        image(GIANT_DINO_RIGHT_IMG, x, y, w, h)
        return
    if boss["form"] == "ReuzenCowboy":
        image(COWBOY_IMG, x, y, w, h)
        return

    # ReuzenCoyote without dedicated sprite: stylized silhouette with mood phases.
    phase = boss.get("phase", "laugh")
    fill(124, 84, 51)
    rect(x + 24, y + 78, w - 54, h - 120)
    rect(x + 8, y + 92, 30, h - 112)
    rect(x + w - 50, y + 62, 42, 58)
    fill(94, 60, 34)
    rect(x + w - 44, y + 54, 12, 14)
    rect(x + w - 26, y + 54, 12, 14)
    fill(12, 12, 12)
    if phase == "laugh":
        rect(x + w - 36, y + 84, 4, 4)
        rect(x + w - 22, y + 84, 4, 4)
        fill(210, 188, 138)
        rect(x + w - 40, y + 98, 20, 4)
        fill(94, 60, 34)
        rect(x + w - 38, y + 96, 18, 2)
    elif phase == "angry":
        rect(x + w - 38, y + 85, 5, 5)
        rect(x + w - 24, y + 85, 5, 5)
        stroke(12, 12, 12)
        stroke_weight(2)
        line(x + w - 42, y + 82, x + w - 34, y + 79)
        line(x + w - 18, y + 79, x + w - 10, y + 82)
        no_stroke()
        fill(70, 18, 18)
        rect(x + w - 39, y + 101, 20, 5)
    else:
        rect(x + w - 40, y + 82, 6, 8)
        rect(x + w - 24, y + 82, 6, 8)
        fill(210, 188, 138)
        rect(x + w - 34, y + 100, 8, 8)
        fill(94, 60, 34)
        rect(x + w - 38, y + 98, 16, 2)


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
    global boss_state, score, weapon_powerup_ready, weapon_powerup_level
    global player_x, boss_left_pressed, boss_right_pressed
    if boss["hits_taken"] < boss["hits_required"]:
        return
    boss_completed[boss["level"]] = True
    boss_state = None
    weapon_powerup_ready = False
    weapon_powerup_level = 0
    player_x = float(DINO_X)
    boss_left_pressed = False
    boss_right_pressed = False
    reset_projectile_pool(player_projectiles)
    score += BOSS_REWARD_POINTS.get(boss["level"], 0)
    update_level_from_score()
    spawn_obstacle()


def update_enemy_projectiles(boss):
    global game_over
    player_hitbox = get_dino_hitbox()
    for projectile in iter_active_projectiles(boss["enemy_projectiles"]):
        if projectile["kind"] == "enemy_tnt":
            projectile["x"] += projectile["vx"]
            projectile["y"] += projectile.get("vy", 0.0)
            projectile["vy"] = projectile.get("vy", 0.0) + COYOTE_TNT_THROW_GRAVITY
            projectile_rect = get_projectile_rect(projectile)
            if rects_overlap(projectile_rect, player_hitbox):
                projectile["active"] = False
                game_over = True
                play_sfx(CRASH_SOUND)
                return
            if projectile["y"] + projectile["h"] >= GROUND_Y:
                spawn_coyote_pit(boss, projectile["x"] + (projectile["w"] / 2))
                projectile.update({
                    "kind": "tnt_blast",
                    "x": projectile["x"] - 16,
                    "y": GROUND_Y - 28,
                    "w": 44,
                    "h": 28,
                    "vx": 0.0,
                    "blast_until": millis() + COYOTE_TNT_BLAST_MS,
                })
                continue
            if projectile["x"] + projectile["w"] < -40:
                projectile["active"] = False
            continue

        if projectile["kind"] == "tnt_blast":
            if millis() >= projectile.get("blast_until", 0):
                projectile["active"] = False
            continue

        projectile["x"] += projectile["vx"]
        projectile_rect = get_projectile_rect(projectile)
        if rects_overlap(projectile_rect, player_hitbox):
            projectile["active"] = False
            game_over = True
            play_sfx(CRASH_SOUND)
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
        play_sfx(FIRE_ENEMY_SOUND)
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
        play_sfx(FIRE_ENEMY_SOUND)
        return

    if boss.get("form") == "ReuzenCoyote":
        projectile.update({
            "x": boss["x"] - 6,
            "y": boss["y"] + 112,
            "w": 14,
            "h": 28,
            "vx": -COYOTE_TNT_THROW_SPEED,
            "vy": float(random(-7.8, -5.8)),
            "kind": "enemy_tnt",
            "color": (210, 35, 30),
            "enemy": True,
        })
        play_sfx(FIRE_ENEMY_SOUND)
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
    play_sfx(FIRE_ENEMY_SOUND)


def update_and_draw_boss_mode(theme, update_world=True):
    global dino_y, velocity_y, on_ground, is_fast_falling, game_over, player_x
    boss = boss_state
    if boss is None:
        return

    if update_world:
        if boss.get("form") == "ReuzenCoyote":
            update_coyote_phase_state(boss)
            update_coyote_pits(boss)

        move_dir = int(boss_right_pressed) - int(boss_left_pressed)
        if move_dir != 0:
            min_player_x = 36.0
            max_player_x = max(
                min_player_x,
                get_boss_hitbox(boss)[0] - DINO_W - 18,
            )
            player_x = max(
                min_player_x,
                min(max_player_x, player_x + (move_dir * BOSS_PLAYER_SPEED)),
            )

        update_player_vertical_motion()

        if boss["type"] == "bird_miniboss":
            boss["x"] += boss["vx"]
            boss["y"] += boss["vy"]
            if boss["x"] <= boss["min_x"] or boss["x"] >= boss["max_x"]:
                boss["vx"] *= -1
            if boss["y"] <= boss["min_y"] or boss["y"] >= boss["max_y"]:
                boss["vy"] *= -1
        elif boss.get("form") == "ReuzenCoyote":
            boss["x"] += boss.get("vx", 0.0)
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

        if on_ground and player_over_coyote_pit(boss):
            game_over = True
            play_sfx(CRASH_SOUND)
            return

        if rects_overlap(get_dino_hitbox(), get_boss_hitbox(boss)):
            game_over = True
            play_sfx(CRASH_SOUND)
            return

    draw_coyote_pits(boss, theme)
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
        if boss["type"] in ("bird_miniboss", "cactus_miniboss"):
            fill(200, 40, 40)
            text_size(34)
            text("Mini boss coming...", width // 2 - 168, 34)
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


def get_announcement_font(size):
    key = int(size)
    font = announcement_font_cache.get(key)
    if font is not None:
        return font
    font = pygame.font.SysFont("Arial Black", key, bold=True)
    announcement_font_cache[key] = font
    return font


def draw_transparent_blink_text(message, y, base_size=96, base_color=(255, 74, 56)):
    surface = pygame.display.get_surface()
    if surface is None:
        return
    lines = str(message).split("\n")
    max_len = max((len(line) for line in lines), default=0)
    if max_len > 58:
        base_size = 56
    elif max_len > 42:
        base_size = 66
    elif max_len > 28:
        base_size = 80

    blink_on = int(millis() / 180) % 2 == 0
    alpha_main = 235 if blink_on else 110
    alpha_outline = 200 if blink_on else 95
    font = get_announcement_font(base_size)
    line_height = int(base_size * 1.02)
    oy = int(y)
    for line in lines:
        outline = font.render(line, True, (255, 255, 255))
        outline.set_alpha(alpha_outline)
        main = font.render(line, True, base_color)
        main.set_alpha(alpha_main)
        x = (width - main.get_width()) // 2
        for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, 2)):
            surface.blit(outline, (x + dx, oy + dy))
        surface.blit(main, (x, oy))
        oy += line_height


def draw_big_announcement_overlay(theme):
    if not game_started or game_over or game_paused:
        return

    message = None
    color = (255, 74, 56)
    y = 18
    if millis() < high_jump_warning_until_ms:
        message = "HIGH JUMP!"
    elif millis() < high_jump_powerup_warning_until_ms:
        message = "HIGH JUMP\nPOWERUP!"
    elif millis() < weapon_powerup_warning_until_ms:
        message = "WEAPON POWERUP!"
    elif millis() < water_warning_until_ms:
        message = "WATER! SPRING OP LELIEBLADEN"
        color = (66, 176, 242)
        y = 26
    elif millis() < airplane_warning_until_ms:
        message = "JUMP ON THE AIRPLANE!"
        color = (255, 212, 78)

    if message is None:
        return
    draw_transparent_blink_text(message, y, base_size=100, base_color=color)


def draw_hud(theme, force_visible=False):
    blink_active = is_level_blink_active() and not force_visible
    visible = True if force_visible else (not blink_active or should_show_blink_phase())

    if visible:
        fill(*theme["text"])
        text_size(24)
        text(f"Score: {score}", 20, 40)
        text_size(18)
        text(f"Coins: {coin_count}", 20, 66)
        text_size(24)
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
                play_sfx(CRASH_SOUND)
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


def draw_high_jump_powerup(x, y, w, h, theme):
    px = int(x)
    py = int(y)
    pw = int(w)
    ph = int(h)
    fill(255, 235, 96)
    rect(px, py, pw, ph)
    fill(236, 186, 34)
    rect(px + 3, py + 3, max(2, pw - 6), max(2, ph - 6))
    stroke(*theme["accent"])
    stroke_weight(3)
    arrow_x = px + pw // 2
    arrow_top = py + 6
    arrow_bottom = py + ph - 7
    line(arrow_x, arrow_bottom, arrow_x, arrow_top)
    line(arrow_x, arrow_top, arrow_x - 6, arrow_top + 7)
    line(arrow_x, arrow_top, arrow_x + 6, arrow_top + 7)
    no_stroke()


def draw_weapon_powerup(x, y, w, h):
    profile = get_player_weapon_profile()
    px = int(x)
    py = int(y)
    pw = int(w)
    ph = int(h)
    fill(248, 248, 248)
    rect(px, py, pw, ph)
    fill(220, 220, 220)
    rect(px + 2, py + 2, max(2, pw - 4), max(2, ph - 4))

    if profile["kind"] == "tnt":
        fill(210, 35, 30)
        rect(px + 8, py + 5, pw - 16, ph - 10)
        fill(255, 220, 100)
        rect(px + pw - 10, py + 2, 2, 4)
        return

    if profile["kind"] == "fire":
        fill(235, 85, 20)
        rect(px + 7, py + 7, pw - 14, ph - 12)
        fill(250, 200, 70)
        rect(px + 11, py + 10, pw - 22, ph - 18)
        return

    # Cowboy gun (black)
    fill(22, 22, 22)
    rect(px + 6, py + 9, pw - 12, 6)
    rect(px + 18, py + 14, 5, 7)


def draw_coin_pickup(x, y, w, h):
    px = int(x)
    py = int(y)
    pw = int(w)
    ph = int(h)
    fill(250, 214, 56)
    rect(px, py, pw, ph)
    fill(235, 180, 30)
    rect(px + 2, py + 2, max(2, pw - 4), max(2, ph - 4))
    fill(160, 110, 20)
    rect(px + (pw // 2) - 2, py + 4, 4, ph - 8)


def get_water_lily_pad_rects(draw_x, draw_y, draw_w, draw_h):
    pad_w = 42
    pad_h = 12
    pad_y = draw_y - 10
    return [
        (draw_x + 16, pad_y, pad_w, pad_h),
        (draw_x + (draw_w // 2) - (pad_w // 2), pad_y - 2, pad_w, pad_h),
        (draw_x + draw_w - pad_w - 16, pad_y, pad_w, pad_h),
    ]


def draw_water_lily_obstacle(draw_x, draw_y, draw_w, draw_h):
    fill(82, 164, 212)
    rect(int(draw_x), int(draw_y), int(draw_w), int(draw_h))
    fill(52, 112, 156)
    rect(int(draw_x), int(draw_y + draw_h - 6), int(draw_w), 6)
    for lx, ly, lw, lh in get_water_lily_pad_rects(draw_x, draw_y, draw_w, draw_h):
        fill(62, 150, 72)
        rect(int(lx), int(ly), int(lw), int(lh))
        fill(48, 128, 58)
        rect(int(lx + 3), int(ly + 2), int(max(2, lw - 6)), int(max(2, lh - 4)))


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
    global dino_y, velocity_y, on_ground, obstacle_x, score, coin_count, game_over, game_started
    global is_ducking, bird_duck_scored, is_fast_falling, snake_hiss_played_for_current
    global high_jump_powerup_charges, high_jump_powerup_warning_until_ms
    global weapon_powerup_warning_until_ms, water_warning_until_ms
    global weapon_powerup_ready, weapon_powerup_level, pending_weapon_powerup_level
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
        if millis() < screenshot_notice_until_ms:
            fill(30, 110, 30)
            text_size(14)
            text(screenshot_notice_text, 30, height - 24)
        return

    if not game_started:
        draw_main_character()
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
        if quit_confirm_active:
            fill(250, 250, 250)
            rect(width // 2 - 190, height // 2 + 132, 380, 84)
            stroke(*theme["accent"])
            stroke_weight(3)
            no_fill()
            rect(width // 2 - 190, height // 2 + 132, 380, 84)
            no_stroke()
            fill(*theme["text"])
            text_size(28)
            text("Wanna quit, really? y/n", width // 2 - 168, height // 2 + 186)
        draw_debug_overlay()
        return

    if flight_mode:
        update_and_draw_flight_mode(theme, update_world=(not game_paused and not game_over))
        draw_main_character()
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
        draw_main_character()
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
    if obstacle_type == "high_jump_powerup":
        draw_high_jump_powerup(obstacle_draw_x, obstacle_draw_y, obstacle_draw_w, obstacle_draw_h, theme)
    elif obstacle_type == "weapon_powerup":
        draw_weapon_powerup(obstacle_draw_x, obstacle_draw_y, obstacle_draw_w, obstacle_draw_h)
    elif obstacle_type == "coin":
        draw_coin_pickup(obstacle_draw_x, obstacle_draw_y, obstacle_draw_w, obstacle_draw_h)
    elif obstacle_type == "water_lily":
        draw_water_lily_obstacle(obstacle_draw_x, obstacle_draw_y, obstacle_draw_w, obstacle_draw_h)
    else:
        image(obstacle_cfg["img"], obstacle_draw_x, obstacle_draw_y, obstacle_draw_w, obstacle_draw_h)
    draw_main_character()

    if game_paused:
        fill(40)
        text_size(34)
        text("Pauze", width // 2 - 55, height // 2 - 8)
        text_size(18)
        text("Druk op P om verder te gaan", width // 2 - 118, height // 2 + 22)
        draw_hud(theme)
        draw_debug_overlay()
        return

    draw_big_announcement_overlay(theme)
    if high_jump_powerup_charges > 0 and game_started and not game_over:
        fill(*theme["accent"])
        text_size(16)
        text(f"High Jump x{high_jump_powerup_charges}", 20, 88)
    if weapon_powerup_ready and game_started and not game_over:
        fill(*theme["accent"])
        text_size(16)
        weapon_label = get_player_weapon_profile()["label"]
        if weapon_powerup_level > 0:
            text(f"{weapon_label} ready (L{weapon_powerup_level})", 20, 110)
        else:
            text(f"{weapon_label} ready", 20, 110)
    elif pending_weapon_powerup_level > 0 and game_started and not game_over:
        fill(*theme["accent"])
        text_size(16)
        text(f"Pak weapon powerup voor boss L{pending_weapon_powerup_level}", 20, 110)

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
            play_sfx(HISS_SOUND)

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
                draw_main_character()
                draw_hud(theme)
                return

        # Collision detection
        dino_hitbox = get_dino_hitbox()
        obstacle_hitbox = get_obstacle_hitbox()
        if obstacle_type == "high_jump_powerup" and rects_overlap(dino_hitbox, obstacle_hitbox):
            high_jump_powerup_charges = HIGH_JUMP_POWERUP_MAX_CHARGES
            high_jump_powerup_warning_until_ms = millis() + HIGH_JUMP_POWERUP_NOTICE_MS
            spawn_obstacle()
        elif obstacle_type == "weapon_powerup" and rects_overlap(dino_hitbox, obstacle_hitbox):
            weapon_powerup_ready = True
            weapon_powerup_level = pending_weapon_powerup_level if pending_weapon_powerup_level > 0 else current_level
            pending_weapon_powerup_level = 0
            weapon_powerup_warning_until_ms = millis() + WEAPON_POWERUP_NOTICE_MS
            spawn_obstacle()
        elif obstacle_type == "coin" and rects_overlap(dino_hitbox, obstacle_hitbox):
            coin_count += 1
            score += COIN_SCORE_VALUE
            play_sfx(COIN_SOUND)
            update_level_from_score()
            spawn_obstacle()
        elif obstacle_type == "water_lily":
            water_hitbox = obstacle_hitbox
            dino_feet_hitbox = (
                dino_hitbox[0],
                dino_hitbox[1] + dino_hitbox[3] - 8,
                dino_hitbox[2],
                8,
            )
            lily_pad_rects = get_water_lily_pad_rects(
                obstacle_draw_x, obstacle_draw_y, obstacle_draw_w, obstacle_draw_h
            )
            on_lily = any(rects_overlap(dino_feet_hitbox, lily_rect) for lily_rect in lily_pad_rects)
            if rects_overlap(dino_hitbox, water_hitbox) and not on_lily:
                game_over = True
                is_ducking = False
                play_sfx(SPLASH_SOUND)
        elif rects_overlap(dino_hitbox, obstacle_hitbox):
            game_over = True
            is_ducking = False
            play_sfx(CRASH_SOUND)

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
        if millis() < screenshot_notice_until_ms:
            fill(30, 110, 30)
            text_size(14)
            text(screenshot_notice_text, 20, height - 20)
        return

    draw_hud(theme)
    draw_debug_overlay()
    if millis() < screenshot_notice_until_ms:
        fill(30, 110, 30)
        text_size(14)
        text(screenshot_notice_text, 20, height - 20)

def key_pressed():
    global velocity_y, on_ground, game_started, isDebugMode, is_ducking
    global game_paused, selected_character_idx, active_character_key
    global duck_jump_expires_ms, is_fast_falling, high_jump_powerup_charges
    global fly_left_pressed, fly_right_pressed, fly_up_pressed, fly_down_pressed
    global boss_left_pressed, boss_right_pressed
    global quit_confirm_active
    pressed_key = key.lower() if isinstance(key, str) else key
    shared.handle_common_keys(
        pressed_key,
        key_code,
        info_text=INFO_TEXT,
        music_toggle_callback=lambda _enabled: update_background_music(force=True),
        allow_quit=False,
    )
    if pressed_key == "i":
        update_background_music(force=True)
    if pressed_key in ("i", "m", "s"):
        return

    if quit_confirm_active:
        if pressed_key == "y":
            exit()
        if pressed_key in ("n", "q") or key_code == pygame.K_ESCAPE:
            quit_confirm_active = False
        return

    if pressed_key == "q" or key_code == pygame.K_ESCAPE:
        if game_started:
            save_character_checkpoint()
            if active_character_key in CHARACTER_ORDER:
                selected_character_idx = CHARACTER_ORDER.index(active_character_key)
            reset_game(show_splash=True)
        else:
            quit_confirm_active = True
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

    if pressed_key == "k":
        capture_screenshot()
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
        save_character_checkpoint()
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

    if game_started and boss_state is not None and not game_over:
        if key_code == pygame.K_LEFT:
            boss_left_pressed = True
            return
        if key_code == pygame.K_RIGHT:
            boss_right_pressed = True
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
        jump_velocity = JUMP_VELOCITY
        if high_jump_powerup_charges > 0:
            jump_velocity = POWERUP_HIGH_JUMP_VELOCITY
            high_jump_powerup_charges = max(0, high_jump_powerup_charges - 1)
        elif now <= duck_jump_expires_ms:
            jump_velocity = HIGH_JUMP_VELOCITY
        is_ducking = False
        velocity_y = jump_velocity
        on_ground = False
        is_fast_falling = False
        duck_jump_expires_ms = 0
        play_sfx(get_jump_sound())


def key_released(released_key):
    global is_ducking, duck_jump_expires_ms, is_fast_falling
    global fly_left_pressed, fly_right_pressed, fly_up_pressed, fly_down_pressed
    global boss_left_pressed, boss_right_pressed
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

    if released_key == pygame.K_LEFT:
        boss_left_pressed = False
    elif released_key == pygame.K_RIGHT:
        boss_right_pressed = False

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


def draw_equipped_weapon_on_character(pose):
    profile = get_player_weapon_profile()
    hand_x = int(pose["x"] + pose["w"] - 8)
    hand_y = int(pose["y"] + pose["h"] * 0.48)
    if pose["ducking"]:
        hand_y += 2

    if profile["kind"] == "tnt":
        fill(210, 35, 30)
        rect(hand_x - 8, hand_y - 6, 12, 12)
        fill(255, 220, 100)
        rect(hand_x + 1, hand_y - 9, 2, 3)
        return

    if profile["kind"] == "fire":
        fill(235, 85, 20)
        rect(hand_x - 4, hand_y - 3, 14, 7)
        fill(250, 200, 70)
        rect(hand_x - 1, hand_y - 1, 8, 3)
        return

    # Cowboy gun overlay (black), dichtbij hand.
    fill(22, 22, 22)
    rect(hand_x - 4, hand_y - 3, 15, 4)
    rect(hand_x + 1, hand_y + 1, 4, 5)


def draw_high_jump_powerup_effect(pose):
    if high_jump_powerup_charges <= 0:
        return
    surface = pygame.display.get_surface()
    if surface is None or not EXPLOSION_FRAMES:
        return

    charge_level = max(0, min(HIGH_JUMP_POWERUP_MAX_CHARGES, high_jump_powerup_charges))
    if charge_level == 0:
        return

    # 3 -> fel/groot, 2 -> medium, 1 -> subtiel
    alpha_by_charge = {3: 210, 2: 145, 1: 85}
    size_by_charge = {3: 54, 2: 42, 1: 30}
    frame_idx = int(millis() / 85) % len(EXPLOSION_FRAMES)
    frame = EXPLOSION_FRAMES[frame_idx]
    if frame is None:
        return

    glow_size = size_by_charge.get(charge_level, 30)
    glow = pygame.transform.smoothscale(frame, (glow_size, glow_size)).copy()
    glow.set_alpha(alpha_by_charge.get(charge_level, 90))

    feet_x = int(pose["x"] + (pose["w"] // 2) - (glow_size // 2))
    feet_y = int(pose["y"] + pose["h"] - (glow_size // 3))
    surface.blit(glow, (feet_x, feet_y))


def weapon_overlay_decorator(draw_fn):
    def wrapped():
        pose = draw_fn()
        if pose is None:
            return None
        if game_started and not game_over and high_jump_powerup_charges > 0:
            draw_high_jump_powerup_effect(pose)
        if game_started and not game_over and weapon_powerup_ready:
            draw_equipped_weapon_on_character(pose)
        return pose
    return wrapped


@weapon_overlay_decorator
def draw_main_character():
    if flight_mode:
        plane_x, plane_y, plane_w, plane_h = get_flight_plane_rect()
        image(AIRPLANE_IMG, plane_x, plane_y, plane_w, plane_h)
        if isDebugMode:
            no_fill()
            stroke(255, 0, 0)
            stroke_weight(2)
            rect(plane_x, plane_y, plane_w, plane_h)
            no_stroke()
        return None

    dino_h = DUCK_H if (is_ducking and on_ground and not game_over) else DINO_H
    dino_y_draw = get_dino_draw_y()
    character = CHARACTER_CONFIG[get_current_character_key()]
    draw_x = int(get_player_x())
    draw_w = DINO_W
    draw_h = dino_h
    if game_over:
        dino_sprite = character["oops"]
        if get_current_character_key() == "cowboy":
            # Cowboy falls backward and lies on the ground.
            draw_x -= 10
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
    return {
        "x": draw_x,
        "y": dino_y_draw,
        "w": draw_w,
        "h": draw_h,
        "ducking": bool(is_ducking and on_ground and not game_over),
    }


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        try:
            pygame.quit()
        except Exception:
            pass
