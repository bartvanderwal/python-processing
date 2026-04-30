from processing import run, size, full_screen, frame_rate, title, background, fill, rect, line, arc
from processing import ellipse, triangle
from processing import image, text_size, text, load_image, no_fill, stroke, stroke_weight, no_stroke, millis
from processing import width, height, key, key_code, random
from processing import PI, TWO_PI

from processing_extension import (
    K_DOWN,
    K_ESCAPE,
    K_LEFT,
    K_RIGHT,
    K_UP,
    K_c,
    display as pg_display,
    font as pg_font,
    get_init as pygame_get_init,
    image as pg_image,
    key as pg_key,
    mixer,
    pygame,
    transform,
)
import shared
import math
import os
import platform as py_platform
import sys
import traceback

# Dino game assets
DINO_IMG = load_image("assets/dino-transparant.png")
DINO_OOPS_IMG = load_image("assets/dino-oops-transparant.png")
DINO_DUCK_IMG = load_image("assets/dino-duck-transparant.png")
DINO_FALL_IMG = transform.rotate(DINO_OOPS_IMG, -90)
COWBOY_IMG = load_image("assets/cowboy-transparant.png")
COWBOY_RUN_IMG = load_image("assets/cowboy-run-transparant.png")
COWBOY_FALL_IMG = load_image("assets/pc/cowboy-fall-transparant.png")
COWBOY_DUCK_IMG = load_image("assets/pc/cowboy-duck-transparant.png")
ROADRUNNER_IMG = load_image("assets/roadrunner-transparant.png")
ROADRUNNER_OOPS_IMG = load_image("assets/roadrunner-oops-transparant.png")
ROADRUNNER_DUCK_IMG = load_image("assets/roadrunner-duck-transparant.png")
ROADRUNNER_FALL_IMG = transform.rotate(ROADRUNNER_OOPS_IMG, -90)
AIRPLANE_IMG = load_image("assets/plane-still.png")
PLANE_SPRITE_SHEET = load_image("assets/plane-sprite.png") if os.path.exists("assets/plane-sprite.png") else None
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


def load_optional_image(path_candidates):
    for candidate in path_candidates:
        if not os.path.exists(candidate):
            continue
        try:
            return load_image(candidate)
        except Exception as exc:
            log_soft_exception(
                f"Failed to load optional image '{candidate}'",
                exc,
                once_key=f"load_optional_image:{candidate}",
            )
            continue
    return None


CROWN_BADGE_IMG = load_optional_image((
    "assets/kroontje.png",
    "assets/crown.png",
    "assets/crown-transparant.png",
    "assets/kroon.png",
    "assets/pc/crown.png",
))
ZEPPELIN_IMG = load_optional_image((
    "assets/zeppelin.png",
    "assets/npc/zeppelin.png",
))
BADGER_SHOP_IMG = load_optional_image((
    "assets/obstacles/badger-shop-crop.png",
    "assets/obstacles/badger-shop.png",
    "assets/badger-shop.png",
    "assets/badger_shop.png",
    "assets/npc/badger-shop.png",
    "assets/npc/badger_shop.png",
))
SHOP_ITEM_ICONS = {
    "extra_life": load_optional_image((
        "assets/shop-heart.png",
        "assets/heart.png",
        "assets/shop/heart.png",
    )),
    "shield": load_optional_image((
        "assets/shop-shield.png",
        "assets/shield.png",
        "assets/shop/shield.png",
    )),
    "coin_boost": load_optional_image((
        "assets/shop-coin-boost.png",
        "assets/coin-boost.png",
        "assets/shop/coin-boost.png",
    )),
    "jump_shoes": load_optional_image((
        "assets/shop-jump-shoes.png",
        "assets/jump-shoes.png",
        "assets/shop/jump-shoes.png",
    )),
}
CACTUS_BOSS_IMG = load_optional_image((
    "assets/npc/cactus-endboss/cactus_omgedraaid.png",
    "assets/npc/cactus-endboss/cactus.png",
))
CACTUS_BOSS_TRUNK_IMG = load_optional_image((
    "assets/npc/cactus-endboss/cactus_stam_omgedraaid.png",
    "assets/npc/cactus-endboss/cactus_stam.png",
))
CACTUS_BOSS_ARMS_IMG = load_optional_image((
    "assets/npc/cactus-endboss/generated/cactus_arms_overlay.png",
))
CACTUS_BOSS_TRUNK_FLIPPED_IMG = transform.flip(CACTUS_BOSS_TRUNK_IMG, True, False) if CACTUS_BOSS_TRUNK_IMG is not None else None
CACTUS_BOSS_ARMS_FLIPPED_IMG = transform.flip(CACTUS_BOSS_ARMS_IMG, True, False) if CACTUS_BOSS_ARMS_IMG is not None else None


def extract_plane_sprite_rows(sheet, cols=3, rows=3):
    if sheet is None:
        return {}
    sw, sh = sheet.get_width(), sheet.get_height()
    row_frames = {}
    for row in range(rows):
        frames = []
        y0 = int((row * sh) / rows)
        y1 = int(((row + 1) * sh) / rows)
        for col in range(cols):
            x0 = int((col * sw) / cols)
            x1 = int(((col + 1) * sw) / cols)
            tile_w = max(1, x1 - x0)
            tile_h = max(1, y1 - y0)
            tile = sheet.subsurface((x0, y0, tile_w, tile_h)).copy()
            bounds = tile.get_bounding_rect(min_alpha=8)
            if bounds.width <= 0 or bounds.height <= 0:
                continue
            # Crop out transparent margins so scaling does not include huge empty area.
            trimmed = tile.subsurface(bounds).copy()
            frames.append(trimmed)
        if frames:
            row_frames[row] = frames
    return row_frames


PLANE_SPRITE_ROWS = extract_plane_sprite_rows(PLANE_SPRITE_SHEET, cols=3, rows=3)
# Current sheet layout (top->bottom): cowboy, roadrunner, dino.
PLANE_SPRITE_ROW_BY_CHARACTER = {
    "cowboy": 0,
    "roadrunner": 1,
    "dino": 2,
}


def get_plane_frames_for_character(character_key):
    if not PLANE_SPRITE_ROWS:
        return []
    preferred_row = PLANE_SPRITE_ROW_BY_CHARACTER.get(character_key, 0)
    if preferred_row in PLANE_SPRITE_ROWS:
        return PLANE_SPRITE_ROWS[preferred_row]
    first_row = sorted(PLANE_SPRITE_ROWS.keys())[0]
    return PLANE_SPRITE_ROWS[first_row]


# Richtingsvarianten (naar rechts kijken) voor specifieke enemies/bosses.
BIRD_RIGHT_IMG = transform.flip(BIRD_IMG, True, False)
GIANT_DINO_RIGHT_IMG = transform.flip(DINO_IMG, True, False)
GIANT_COWBOY_RIGHT_IMG = transform.flip(COWBOY_IMG, True, False)
GIANT_COWBOY_DUCK_RIGHT_IMG = transform.flip(COWBOY_DUCK_IMG, True, False)

# Dino properties
BASE_GAME_WIDTH = 800
BASE_GAME_HEIGHT = 500
DINO_X = 100
DINO_Y = 400
DINO_W = 60
DINO_H = 60
DUCK_H = 30
GRAVITY = 1.2
JUMP_VELOCITY = -18
HIGH_JUMP_VELOCITY = -22
POWERUP_HIGH_JUMP_VELOCITY = -26
STACKED_POWER_HIGH_JUMP_VELOCITY = POWERUP_HIGH_JUMP_VELOCITY + (HIGH_JUMP_VELOCITY - JUMP_VELOCITY)
HIGH_JUMP_POWERUP_MAX_CHARGES = 3
HIGH_JUMP_WINDOW_MS = 500
FAST_FALL_EXTRA_GRAVITY = 2.0
BASE_SCROLL_SPEED = 6.0
LEVEL_SPEED_FACTOR = 1.1
LEVEL_BLINK_DURATION_MS = 1200
LEVEL_BLINK_INTERVAL_MS = 120
MAX_LEVEL = 10
HIGH_JUMP_WARNING_DURATION_MS = 1800
HIGH_JUMP_POWERUP_NOTICE_MS = 1400
WEAPON_POWERUP_NOTICE_MS = 1600
WATER_WARNING_DURATION_MS = 1800
AIRPLANE_WARNING_DURATION_MS = 1800
MISSED_PLANE_NOTICE_MS = 1600
JUMP_BLOCK_WET_GROUND_MS = 7000
JUMP_BLOCK_FLOWER_GROW_MS = 1700
JUMP_BLOCK_DROPLET_COUNT = 14
JUMP_BLOCK_FLOWER_COUNT = 18
LEVEL_NAME_NOTICE_MS = 2200
WIND_SWIRL_EFFECT_MS = 1800
WIND_SWIRL_SLOW_GRAVITY = 0.18
WIND_SWIRL_MAX_FALL_SPEED = 1.6
FLIGHT_PIPE_GAP_H = 150
FLIGHT_PIPE_WIDTH = 72
FLIGHT_PIPE_SPAWN_BASE_MS = 1500
FLIGHT_PLANE_SPEED = 5.0
FLIGHT_PIPE_POINTS = 2
ZEPPELIN_CITY_APPROACH_DURATION_MS = 2400
AIRPLANE_PICKUP_W = 104
AIRPLANE_PICKUP_H = 40
PLAYER_SHOOT_COOLDOWN_MS = 180
CACTUS_SHOT_VERTICAL_BOOST = 1.45
CACTUS_SHOT_UPWARD_OFFSET_PX = 12
GIANT_COWBOY_CROUCH_CHANCE = 0.38
GIANT_COWBOY_CROUCH_MS = 520
GIANT_COWBOY_SHOT_STAND_OFFSET = 64
GIANT_COWBOY_SHOT_CROUCH_OFFSET = 34
BOSS_INTRO_DURATION_MS = 1700
BOSS_PLAYER_SPEED = 5.5
BOSS_LEVEL_ORDER = (4, 7, 10)
PIPE_ENTRY_DURATION_MS = 820
PIPE_ENTRY_CROUCH_HOLD_MS = 240
PIPE_ENTRY_CENTER_TOLERANCE_PX = 18
PIPE_ENTRY_SINK_EXTRA_PX = 20
CACTUS_ROTATION_INTERVAL_MS = 5000
CACTUS_MINIBOSS_TRUNK_HITS_REQUIRED = 3
CACTUS_ARM_SIDE_BY_INDEX = ("left", "right", "left", "right", "left")
BIRD_NEST_ENTRY_RECT = (654, 146, 106, 58)
BIRD_TREE_BRANCH_RECTS = (
    (356, 386, 128, 14),
    (494, 310, 124, 14),
    (626, 232, 112, 14),
)
BIRD_BOSS_BRANCH_RECTS = (
    (78, 396, 164, 14),
    (256, 332, 136, 14),
    (438, 274, 150, 14),
    (596, 360, 126, 14),
)
FINAL_BOSS_JUMP_GRAVITY = 0.78
FINAL_BOSS_JUMP_VELOCITY_MIN = -13.8
FINAL_BOSS_JUMP_VELOCITY_MAX = -10.6
FINAL_BOSS_JUMP_GAP_MIN_MS = 760
FINAL_BOSS_JUMP_GAP_MAX_MS = 1480
FINAL_BOSS_DUCK_GAP_MIN_MS = 980
FINAL_BOSS_DUCK_GAP_MAX_MS = 1920
FINAL_BOSS_DUCK_MIN_MS = 360
FINAL_BOSS_DUCK_MAX_MS = 740
MINI_BOSS_DEFEAT_DURATION_MS = 3200
MINI_BOSS_BLAST_INTERVAL_MS = 70
MINI_BOSS_DEFEAT_BURST_COUNT = 5
FINAL_BOSS_DEFEAT_DURATION_MS = 4200
FINAL_BOSS_BLAST_INTERVAL_MS = 70
FINAL_BOSS_BLAST_LIFE_MS = 920
BOSS_HIT_EXPLOSION_SIZE = 68
FINAL_BOSS_DEFEAT_EXPLOSION_SIZE = 128
FINAL_BOSS_DEFEAT_BURST_COUNT = 7
MAX_ACTIVE_EXPLOSIONS = 72
CACTUS_BRANCH_EXPLOSION_SIZE = 54
CACTUS_BRANCH_EXPLOSION_LIFE_MS = 360
BIRD_MINIBOSS_HITS_REQUIRED = 15
ZEPPELIN_MINIBOSS_HITS_REQUIRED = 18
FLIGHT_PLANE_MAX_HP = 3
FLIGHT_PLANE_SMOKE_INTERVAL_MS = {
    2: 4000,
    1: 2000,
}
CACTUS_MINIBOSS_HITS_REQUIRED = 15
COYOTE_TNT_THROW_SPEED = 6.8
COYOTE_TNT_THROW_GRAVITY = 0.34
COYOTE_TNT_BLAST_MS = 260
COYOTE_BIG_BOMB_CHANCE_PCT = 34
COYOTE_BIG_BOMB_THROW_SPEED = 5.1
COYOTE_BIG_BOMB_FUSE_MS = 1250
COYOTE_BIG_BOMB_BLAST_MS = 420
COYOTE_BIG_BOMB_RETURN_SPEED = 9.4
COYOTE_BIG_BOMB_RETURN_VY = -8.6
COYOTE_BIG_BOMB_RETURN_GRAVITY = 0.28
COYOTE_BIG_BOMB_BOSS_DAMAGE = 5
COYOTE_BIG_BOMB_RETURNS_REQUIRED = 5
FINAL_BOSS_DEFAULT_HITS_REQUIRED = 35
COYOTE_HITS_REQUIRED = COYOTE_BIG_BOMB_RETURNS_REQUIRED * COYOTE_BIG_BOMB_BOSS_DAMAGE
BOSS_REWARD_POINTS = {
    4: BIRD_MINIBOSS_HITS_REQUIRED,
    6: ZEPPELIN_MINIBOSS_HITS_REQUIRED,
    7: CACTUS_MINIBOSS_HITS_REQUIRED,
    10: FINAL_BOSS_DEFAULT_HITS_REQUIRED,
}
COYOTE_PIT_WIDTH = 86
COYOTE_PIT_LIFE_MS = 6500
COYOTE_MAX_PITS = 3
JACKET_BONUS_HP = 3
PLAYER_DAMAGE_COOLDOWN_MS = 750
MAX_PROJECTILES_PER_SIDE = 10
MAX_COIN_POUCH = 100
COIN_SCORE_VALUE = 1
COIN_SPAWN_CHANCE_PCT = 46
COIN_ARC_SPAWN_CHANCE_PCT = 24
BONUS_COIN_LINE_CHANCE_PCT = 28
BONUS_COIN_ARC_CHANCE_PCT = 22
MULTI_OBSTACLE_PACK_CHANCE_PCT = 34
MULTI_JUMP_NOTICE_MS = 1800
SHOP_SHIELD_MS = 5000
SHOP_COIN_BOOST_MS = 60000
SHOP_JUMP_SHOES_MS = 30000
SHOP_JUMP_SHOES_FACTOR = 1.18
SHOP_BOSS_WEAPON_COST = 24
SHOP_NOTICE_MS = 1800
PRE_BOSS_SCENE_NOTICE_MS = 2200
COYOTE_CAVE_FLASH_MS = 180
SHOP_ITEMS = (
    {
        "key": "extra_life",
        "label": "Extra Life",
        "cost": 20,
        "desc": "Absorb one fatal hit.",
    },
    {
        "key": "shield",
        "label": "Shield (5s)",
        "cost": 16,
        "desc": "Temporary protection.",
    },
    {
        "key": "coin_boost",
        "label": "Coin x2 (60s)",
        "cost": 22,
        "desc": "All collected coins are doubled.",
    },
    {
        "key": "jump_shoes",
        "label": "Jump Shoes (30s)",
        "cost": 18,
        "desc": "Higher jumps for a short time.",
    },
)
MENU_MUSIC_PATH = "assets/audio/loading-atmosphere.wav"
GAME_MUSIC_PATH = "assets/audio/pixel-leap.wav"
VICTORY_MUSIC_CANDIDATES = (
    "assets/audio/victory-music.wav",
    "assets/audio/victory.wav",
    "assets/audio/victory.mp3",
    "assets/audio/victory.m4a",
)
CREDITS_MUSIC_CANDIDATES = (
    "assets/audio/finish-game-music-victory.mp3",
    "assets/audio/finish-game-music-victory.wav",
    "assets/audio/finish-game-music-victory.m4a",
    "assets/audio/victory-music.wav",
    "assets/audio/victory.wav",
    "assets/audio/victory.mp3",
    "assets/audio/victory.m4a",
)
MUSIC_VOLUME = 0.35
INTRO_SPEECH_CANDIDATES = (
    "assets/audio/welcome-to-the-dino-game.mp3",
    "assets/audio/intro-speech.mp3",
    "assets/audio/intro-speech.m4a",
    "assets/audio/intro-speech.wav",
)
CREDITS_DURATION_MS = 60000
CREDITS_TOP_MARGIN = 30
CREDITS_BOTTOM_MARGIN = 110
CREDITS_SCROLL_SPEED_FACTOR = 0.82
CREDITS_FINISH_PAD_PX = 120
ZEPPELIN_ART_ATTRIBUTION = "Zeppelin artwork reference/source: FreeSVG.org 'Zeppelin' by j4p4n (Public Domain / CC0) https://freesvg.org/zeppelin"
SCREENSHOT_NOTICE_MS = 2200
GROUND_Y = 460
CACTUS_GUIDE_LINE_Y = 443
IS_WEB = sys.platform == "emscripten"
TOUCH_CONTROLS_ENABLED = IS_WEB
TOUCH_BTN_SIZE = 78
TOUCH_BTN_GAP = 12
TOUCH_ACTION_BTN_W = 132
TOUCH_ACTION_BTN_H = 78

_logged_soft_exception_keys = set()


def log_soft_exception(context, exc, *, once_key=None):
    if once_key is not None:
        if once_key in _logged_soft_exception_keys:
            return
        _logged_soft_exception_keys.add(once_key)
    print(f"[dino_game] {context}: {exc.__class__.__name__}: {exc}", file=sys.stderr)
    traceback.print_exception(type(exc), exc, exc.__traceback__)


def load_sound_or_none(path):
    try:
        return mixer.Sound(path)
    except Exception as exc:
        log_soft_exception(
            f"Failed to load sound '{path}'",
            exc,
            once_key=f"load_sound:{path}",
        )
        return None


def detect_touch_controls_enabled():
    if not IS_WEB:
        return False
    try:
        browser_window = getattr(py_platform, "window", None)
        navigator = getattr(browser_window, "navigator", None)
        max_touch_points = int(getattr(navigator, "maxTouchPoints", 0) or 0)
        if max_touch_points > 0:
            return True

        media_query = browser_window.matchMedia("(pointer: coarse)") if browser_window is not None else None
        if media_query is not None and bool(getattr(media_query, "matches", False)):
            return True

        user_agent = str(getattr(navigator, "userAgent", "")).lower()
        if any(token in user_agent for token in ("android", "iphone", "ipad", "mobile")):
            return True
    except Exception as exc:
        log_soft_exception(
            "detect_touch_controls_enabled failed",
            exc,
            once_key="detect_touch_controls_enabled",
        )
    return False


# Progression per level: first chapter = 6 cleared obstacles, then +3 obstacles each chapter.
LEVEL_OBSTACLE_REQUIREMENTS = [6, 9, 12, 15, 18, 21, 24, 27, 30, 33]
LEVEL_OBSTACLE_TOTAL_THRESHOLDS = []
_level_total = 0
for _obstacles_needed in LEVEL_OBSTACLE_REQUIREMENTS:
    _level_total += _obstacles_needed
    LEVEL_OBSTACLE_TOTAL_THRESHOLDS.append(_level_total)
LEVEL_START_OBSTACLE_COUNTS = [0] + LEVEL_OBSTACLE_TOTAL_THRESHOLDS[:-1]
FINAL_LEVEL_TOTAL_OBSTACLES = LEVEL_OBSTACLE_TOTAL_THRESHOLDS[-1]

# Score remains separate from level progression so coins and high-value obstacles can still award points.
LEVEL_SCORE_REFERENCE_TOTALS = list(LEVEL_OBSTACLE_TOTAL_THRESHOLDS)
LEVEL_START_SCORES = [0] + LEVEL_SCORE_REFERENCE_TOTALS[:-1]
FINAL_LEVEL_TOTAL_SCORE = LEVEL_SCORE_REFERENCE_TOTALS[-1]

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

USE_SCRIPTED_OBSTACLE_PATTERNS = True
LEVEL_SCRIPTED_OBSTACLE_PATTERNS = {
    1: [
        "cactus_low", "cactus_low", "bird_low", "cactus_high",
        "cactus_low", "bird_low", "cactus_high", "cactus_low",
    ],
    2: [
        "cactus_low", "snake", "bird_low", "cactus_high",
        "snake", "cactus_low", "bird_low", "cactus_high",
    ],
    3: [
        "jump_block", "cactus_tower", "snake", "cactus_low",
        "jump_block", "bird_low", "cactus_tower", "snake",
    ],
    4: [
        "cactus_low", "bird_low", "snake", "cactus_high",
        "cactus_low", "bird_low", "snake", "cactus_high",
    ],
    5: [
        "pipe_pair", "cactus_low", "pipe_pair", "snake",
        "pipe_pair", "bird_low", "pipe_pair", "cactus_high",
    ],
    6: [
        "pipe_pair", "snake", "pipe_pair", "cactus_high",
        "pipe_pair", "bird_low", "pipe_pair", "cactus_low",
    ],
    7: [
        "cactus_tower", "snake", "bird_low", "cactus_high",
        "cactus_low", "snake", "bird_low", "cactus_tower",
    ],
    8: [
        "cactus_low", "snake", "cactus_high", "bird_low",
        "cactus_low", "cactus_tower", "snake", "bird_low",
        "cactus_high", "cactus_low",
    ],
    9: [
        "cactus_low", "snake", "cactus_high", "bird_low",
        "cactus_low", "snake", "cactus_tower", "bird_low",
        "cactus_low", "snake", "cactus_high", "cactus_low",
    ],
    10: [
        "cactus_high", "snake", "bird_low", "cactus_tower",
        "cactus_low", "snake", "bird_low", "cactus_high",
    ],
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
    "jump_block": {
        "img": None,
        "w": 42,
        "h": 42,
        "y": 282,
        "hitbox_insets": (2, 2, 2, 2),
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
        "w": AIRPLANE_PICKUP_W,
        "h": AIRPLANE_PICKUP_H,
        "y": 378,
        "hitbox_insets": (8, 8, 6, 4),
        "points": 0,
    },
    "pipe_pair": {
        "img": None,
        "w": FLIGHT_PIPE_WIDTH,
        "h": GROUND_Y,
        "y": 0,
        "hitbox_insets": (0, 0, 0, 0),
        "points": 3,
    },
}

INFO_TEXT = [
    "i -> instructions screen",
    "w -> play/stop welcome speech (in instructions)",
    "m -> music on/off",
    "s -> sound effects on/off",
    "f -> fullscreen on/off",
    "q -> in game: menu, in menu: quit prompt",
    "d -> debug mode (show hitbox)",
    "l -> level up (debug mode)",
    "L -> level down (debug mode)",
    "v -> start credits (debug mode)",
    "p -> pause",
    "space/a -> start or shoot (boss)",
    "k -> save screenshot",
    "arrow keys -> move / jump / duck",
]

CHARACTER_ORDER = ["dino", "cowboy", "roadrunner"]
CHARACTER_CONFIG = {
    "dino": {
        "label": "Dino",
        "stand": DINO_IMG,
        "duck": DINO_DUCK_IMG,
        "pipe_crouch_path": "assets/dino-crouch-pipe-transparant.png",
        "oops": DINO_OOPS_IMG,
        "theme": {
            "bg": (245, 245, 245),
            "ground_fill": (200, 200, 200),
            "ground_line": (120, 120, 120),
            "text": (30, 30, 30),
            "accent": (70, 70, 70),
            "menu_title": (70, 70, 70),
            "menu_prompt": (52, 52, 52),
            "menu_meta": (84, 84, 84),
        },
    },
    "cowboy": {
        "label": "Cowboy",
        "stand": COWBOY_IMG,
        "run": COWBOY_RUN_IMG,
        "duck": COWBOY_DUCK_IMG,
        "pipe_crouch_path": "assets/pc/cowboy-crouch-pipe-transparant.png",
        "oops": COWBOY_FALL_IMG,
        "theme": {
            "bg": (245, 220, 170),
            "ground_fill": (220, 175, 120),
            "ground_line": (150, 98, 50),
            "text": (60, 35, 20),
            "accent": (178, 84, 28),
            "menu_title": (150, 86, 38),
            "menu_prompt": (78, 47, 26),
            "menu_meta": (112, 72, 42),
        },
    },
    "roadrunner": {
        "label": "Roadrunner",
        "stand": ROADRUNNER_IMG,
        "duck": ROADRUNNER_DUCK_IMG,
        "pipe_crouch_path": "assets/roadrunner-crouch-pipe-transparant.png",
        "oops": ROADRUNNER_OOPS_IMG,
        "theme": {
            "bg": (154, 214, 242),
            "ground_fill": (214, 200, 150),
            "ground_line": (121, 104, 76),
            "text": (16, 58, 88),
            "accent": (0, 112, 163),
            "menu_title": (0, 112, 163),
            "menu_prompt": (16, 58, 88),
            "menu_meta": (34, 86, 122),
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
game_completed = False
game_started = False
score = 0
high_score = 0
coin_count = 0
shop_active = False
shop_selected_index = 0
shop_notice_text = ""
shop_notice_until_ms = 0
shop_extra_life_count = 0
shop_shield_count = 0
shop_coin_boost_count = 0
shop_jump_shoes_count = 0
shield_until_ms = 0
coin_boost_until_ms = 0
jump_shoes_until_ms = 0
pre_boss_scene_level = 0
pending_boss_shop_level = 0
boss_shop_seen = {
    level: False for level in BOSS_LEVEL_ORDER
}
coyote_cave_flash_until_ms = 0
pipe_entry_active = False
pipe_entry_level = 0
pipe_entry_started_ms = 0
pipe_entry_start_x = float(DINO_X)
pipe_entry_start_feet_y = float(DINO_Y + DINO_H)
pipe_entry_sound_next_ms = 0
player_x = float(DINO_X)
JUMP_SOUND = None
HIGH_JUMP_SOUND = None
DINO_ROAR_SOUND = None
PIPE_ENTRY_SOUND = None
CRASH_SOUND = None
HISS_SOUND = None
SPLASH_SOUND = None
FIRE_PLAYER_SOUND = None
FIRE_ENEMY_SOUND = None
BOSS_EXPLOSION_SOUND = None
COIN_SOUND = None
MINI_BOSS_VICTORY_SOUND = None
INTRO_SPEECH_SOUND = None
INTRO_SPEECH_CHANNEL = None
pending_high_jump_landing_roar = False
isDebugMode = False
debug_coin_pressed = False
debug_coin_repeat_until_ms = 0
is_ducking = False
game_paused = False
selected_character_idx = 0
active_character_key = "dino"
checkpoint_level_by_character = {
    character_key: 1 for character_key in CHARACTER_ORDER
}
character_completed = {
    character_key: False for character_key in CHARACTER_ORDER
}
pipe_crouch_sprite_cache = {}
duck_jump_expires_ms = 0
is_fast_falling = False
current_level = 1
scroll_speed = BASE_SCROLL_SPEED
obstacles_cleared = 0
next_level_obstacle_goal = LEVEL_OBSTACLE_TOTAL_THRESHOLDS[0]
level_blink_until_ms = 0
high_jump_warning_until_ms = 0
high_jump_powerup_warning_until_ms = 0
weapon_powerup_warning_until_ms = 0
water_warning_until_ms = 0
airplane_warning_until_ms = 0
missed_plane_notice_until_ms = 0
multi_jump_notice_until_ms = 0
wet_ground_until_ms = 0
wet_ground_started_ms = 0
pending_airplane_spawn = False
queued_obstacle_after_powerup = None
queued_spawn_sequence = []
queued_coin_spawn_ys = []
bonus_coins = []
extra_obstacles = []
scripted_obstacle_level = 1
scripted_obstacle_index = 0
jump_block_droplets = []
ground_flowers = []
high_jump_powerup_charges = 0

ARROW_KEY_NAMES = {
    "arrowleft": K_LEFT,
    "arrowright": K_RIGHT,
    "arrowup": K_UP,
    "arrowdown": K_DOWN,
}
pending_weapon_powerup_level = 0
weapon_powerup_ready = False
weapon_powerup_level = 0
coin_spawn_y = 360
flight_mode = False
flight_plane_x = 0.0
flight_plane_y = 0.0
flight_mode_entry_level = 1
flight_mode_exit_level = 2
flight_pipe_spawn_due_ms = 0
flight_pipes = []
flight_plane_hp = FLIGHT_PLANE_MAX_HP
flight_plane_smoke_next_ms = 0
flight_plane_smoke_puffs = []
ground_pipe_gap_top = 220
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
    6: False,
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
explosion_effects = []
final_boss_snapshot = None
final_boss_defeat_until_ms = 0
final_boss_next_blast_ms = 0
credits_active = False
credits_finished = False
credits_started_ms = 0
credits_items = []
credits_content_height = 0
credits_scroll_speed_px_per_ms = 0.0
credits_total_duration_ms = CREDITS_DURATION_MS
credits_starfield = []
credits_font_cache = {}
pending_credits_after_victory = False
mini_boss_defeat_sequences = []
post_boss_transition = None
is_fullscreen = False
touch_active_button = None
touch_ignore_next_click = False
web_audio_unlocked = not IS_WEB


def reset_game(show_splash=False):
    global dino_y, velocity_y, on_ground, score, game_over, game_completed, game_started
    global shop_active, shop_selected_index, shop_notice_text, shop_notice_until_ms
    global shield_until_ms, coin_boost_until_ms, jump_shoes_until_ms
    global pre_boss_scene_level, pending_boss_shop_level, boss_shop_seen
    global coyote_cave_flash_until_ms
    global pipe_entry_active, pipe_entry_level, pipe_entry_started_ms
    global pipe_entry_start_x, pipe_entry_start_feet_y, pipe_entry_sound_next_ms
    global player_x
    global is_ducking, game_paused, bird_duck_scored, duck_jump_expires_ms, is_fast_falling
    global debug_coin_pressed, debug_coin_repeat_until_ms
    global current_level, scroll_speed, obstacles_cleared, next_level_obstacle_goal, level_blink_until_ms
    global high_jump_warning_until_ms, high_jump_powerup_warning_until_ms
    global weapon_powerup_warning_until_ms, water_warning_until_ms
    global airplane_warning_until_ms, missed_plane_notice_until_ms
    global multi_jump_notice_until_ms
    global wet_ground_until_ms, wet_ground_started_ms
    global pending_airplane_spawn, queued_obstacle_after_powerup
    global queued_spawn_sequence, queued_coin_spawn_ys, bonus_coins
    global extra_obstacles
    global scripted_obstacle_level, scripted_obstacle_index
    global jump_block_droplets, ground_flowers
    global high_jump_powerup_charges
    global pending_weapon_powerup_level, weapon_powerup_ready, weapon_powerup_level
    global coin_spawn_y
    global flight_mode, flight_plane_x, flight_plane_y, flight_mode_entry_level, flight_mode_exit_level
    global flight_pipe_spawn_due_ms, flight_pipes, ground_pipe_gap_top
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
    global explosion_effects, final_boss_snapshot, final_boss_defeat_until_ms, final_boss_next_blast_ms
    global credits_active, credits_finished, credits_started_ms
    global credits_items, credits_content_height, credits_scroll_speed_px_per_ms
    global credits_total_duration_ms, credits_starfield
    global pending_credits_after_victory
    global mini_boss_defeat_sequences
    global post_boss_transition
    global pipe_crouch_sprite_cache
    global touch_active_button, touch_ignore_next_click
    global pending_high_jump_landing_roar
    stop_intro_speech()
    dino_y = DINO_Y
    velocity_y = 0
    on_ground = True
    player_x = float(DINO_X)
    score = 0
    game_over = False
    game_completed = False
    game_started = not show_splash
    if show_splash:
        shop_active = False
    shop_selected_index = 0
    shop_notice_text = ""
    shop_notice_until_ms = 0
    pre_boss_scene_level = 0
    pending_boss_shop_level = 0
    boss_shop_seen = {
        level: False for level in BOSS_LEVEL_ORDER
    }
    coyote_cave_flash_until_ms = 0
    pipe_entry_active = False
    pipe_entry_level = 0
    pipe_entry_started_ms = 0
    pipe_entry_start_x = float(DINO_X)
    pipe_entry_start_feet_y = float(DINO_Y + DINO_H)
    pipe_entry_sound_next_ms = 0
    debug_coin_pressed = False
    debug_coin_repeat_until_ms = 0
    pending_high_jump_landing_roar = False
    is_ducking = False
    game_paused = False
    bird_duck_scored = False
    duck_jump_expires_ms = 0
    is_fast_falling = False
    current_level = 1
    scroll_speed = BASE_SCROLL_SPEED
    obstacles_cleared = 0
    next_level_obstacle_goal = LEVEL_OBSTACLE_TOTAL_THRESHOLDS[0]
    level_blink_until_ms = 0
    high_jump_warning_until_ms = 0
    high_jump_powerup_warning_until_ms = 0
    weapon_powerup_warning_until_ms = 0
    water_warning_until_ms = 0
    airplane_warning_until_ms = 0
    missed_plane_notice_until_ms = 0
    multi_jump_notice_until_ms = 0
    wet_ground_until_ms = 0
    wet_ground_started_ms = 0
    pending_airplane_spawn = False
    queued_obstacle_after_powerup = None
    queued_spawn_sequence = []
    queued_coin_spawn_ys = []
    bonus_coins = []
    extra_obstacles = []
    scripted_obstacle_level = 1
    scripted_obstacle_index = 0
    jump_block_droplets = []
    ground_flowers = []
    high_jump_powerup_charges = 0
    pending_weapon_powerup_level = 0
    weapon_powerup_ready = False
    weapon_powerup_level = 0
    coin_spawn_y = 360
    flight_mode = False
    flight_plane_x = 0.0
    flight_plane_y = 0.0
    flight_mode_entry_level = 1
    flight_mode_exit_level = 2
    flight_pipe_spawn_due_ms = 0
    flight_pipes = []
    ground_pipe_gap_top = 220
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
        6: False,
        7: False,
        10: False,
    }
    player_max_hp = 1
    player_hp = 1
    player_damage_cooldown_until_ms = 0
    shield_until_ms = 0
    coin_boost_until_ms = 0
    jump_shoes_until_ms = 0
    screenshot_notice_until_ms = 0
    screenshot_notice_text = ""
    quit_confirm_active = False
    level_name_announcement_until_ms = 0
    level_name_announcement_text = ""
    wind_swirl_effect_until_ms = 0
    explosion_effects = []
    final_boss_snapshot = None
    final_boss_defeat_until_ms = 0
    final_boss_next_blast_ms = 0
    credits_active = False
    credits_finished = False
    credits_started_ms = 0
    credits_items = []
    credits_content_height = 0
    credits_scroll_speed_px_per_ms = 0.0
    credits_total_duration_ms = CREDITS_DURATION_MS
    credits_starfield = []
    pending_credits_after_victory = False
    mini_boss_defeat_sequences = []
    post_boss_transition = None
    pipe_crouch_sprite_cache = {}
    touch_active_button = None
    touch_ignore_next_click = False
    spawn_obstacle("cactus_low")


def show_level_name_announcement(level=None):
    global level_name_announcement_until_ms, level_name_announcement_text
    shown_level = current_level if level is None else level
    level_name = LEVEL_NAMES.get(shown_level)
    if level_name is None:
        return
    level_name_announcement_text = f"LEVEL {shown_level}\n{level_name.upper()}"
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
        play_pending_high_jump_landing_roar()


def update_background_music(force=False):
    global current_music_mode
    if IS_WEB and not web_audio_unlocked:
        return
    if not mixer.get_init():
        return

    if not shared.music_enabled:
        if current_music_mode is not None:
            try:
                mixer.music.stop()
            except Exception as exc:
                log_soft_exception(
                    "Failed to stop background music while disabling music",
                    exc,
                    once_key="music_stop_disable",
                )
            current_music_mode = None
        return

    if credits_active:
        target_mode = "credits"
    elif game_completed:
        target_mode = "victory"
    elif game_over:
        target_mode = None
    elif not game_started or shared.show_info:
        target_mode = "menu"
    else:
        target_mode = "game"
    if target_mode is None:
        if current_music_mode is not None:
            try:
                mixer.music.stop()
            except Exception as exc:
                log_soft_exception(
                    "Failed to stop background music while clearing target mode",
                    exc,
                    once_key="music_stop_clear",
                )
            current_music_mode = None
        return

    if not force and target_mode == current_music_mode:
        return

    if target_mode == "menu":
        target_path = MENU_MUSIC_PATH
    elif target_mode == "credits":
        target_path = next((p for p in CREDITS_MUSIC_CANDIDATES if os.path.exists(p)), GAME_MUSIC_PATH)
    elif target_mode == "victory":
        target_path = next((p for p in VICTORY_MUSIC_CANDIDATES if os.path.exists(p)), GAME_MUSIC_PATH)
    else:
        target_path = GAME_MUSIC_PATH
    try:
        mixer.music.load(target_path)
        mixer.music.set_volume(MUSIC_VOLUME)
        mixer.music.play(-1)
        current_music_mode = target_mode
    except Exception as exc:
        log_soft_exception(
            f"Failed to start background music '{target_path}' for mode '{target_mode}'",
            exc,
            once_key=f"music_load:{target_mode}:{target_path}",
        )
        # Keep the game running even when a track cannot be loaded.
        current_music_mode = None


def unlock_web_audio_if_needed():
    global web_audio_unlocked
    if not IS_WEB:
        return
    if web_audio_unlocked:
        return
    web_audio_unlocked = True
    # Start or resume background music only after user interaction in the browser.
    update_background_music(force=True)


def get_credits_font(size, mono=False, bold=False):
    key = (int(size), bool(mono), bool(bold))
    cached = credits_font_cache.get(key)
    if cached is not None:
        return cached
    family = "Courier New" if mono else "Arial Black"
    font = pg_font.SysFont(family, int(size), bold=bool(bold))
    credits_font_cache[key] = font
    return font


def collect_files_with_extensions(root_path, extensions):
    found = []
    if not os.path.isdir(root_path):
        return found
    valid_ext = tuple(ext.lower() for ext in extensions)
    for base, _, files in os.walk(root_path):
        for file_name in sorted(files):
            lower_name = file_name.lower()
            if not lower_name.endswith(valid_ext):
                continue
            full_path = os.path.join(base, file_name)
            rel_path = os.path.relpath(full_path, "assets")
            found.append((full_path, rel_path, file_name))
    found.sort(key=lambda item: item[1].lower())
    return found


def build_credits_items():
    items = []

    def add_text(text_value, size, color, mono=False, bold=False, spacing=44):
        items.append({
            "kind": "text",
            "text": str(text_value),
            "font_size": int(size),
            "color": color,
            "mono": bool(mono),
            "bold": bool(bold),
            "height": int(spacing),
        })

    def add_spacer(height_value):
        items.append({
            "kind": "spacer",
            "height": int(height_value),
        })

    add_text("CONGRATULATIONS!", 58, (255, 70, 70), bold=True, spacing=80)
    add_text("LEVEL 10 CLEARED", 34, (255, 210, 74), bold=True, spacing=56)
    add_spacer(12)
    add_text("Special thanks to The Boyz J&J for testing and feedback.", 27, (247, 232, 132), spacing=46)
    add_text("Han de Pan for the visuals and good vibes.", 27, (247, 232, 132), spacing=44)
    add_text("HAN for the laptop and deep dives into Software Engineering", 27, (247, 232, 132), spacing=42)
    add_text("and for the fun Processing game engine, now also in Python.", 27, (247, 232, 132), spacing=50)
    add_spacer(20)
    add_text("Credits", 40, (255, 220, 86), bold=True, spacing=62)
    add_text("Thanks to Codex GPT-5.3", 28, (255, 238, 152), spacing=44)
    add_text("https://toolkit.artlist.io/ for the epic over-the-top finale music...", 23, (255, 238, 152), spacing=48)
    add_text("Zeppelin source: FreeSVG.org / 'Zeppelin' by j4p4n (Public Domain)", 22, (255, 238, 152), spacing=36)
    add_text("https://freesvg.org/zeppelin", 20, (188, 224, 255), mono=True, spacing=34)
    try:
        macbook_raw = pg_image.load("assets/macbook.png").convert_alpha()
        max_w = 250
        max_h = 150
        scale = min(max_w / max(1, macbook_raw.get_width()), max_h / max(1, macbook_raw.get_height()))
        target_w = max(24, int(macbook_raw.get_width() * scale))
        target_h = max(24, int(macbook_raw.get_height() * scale))
        macbook_scaled = transform.smoothscale(macbook_raw, (target_w, target_h))
        items.append({
            "kind": "image",
            "surface": macbook_scaled,
            "caption": "HAN laptop :)",
            "subcaption": "assets/macbook.png",
            "height": target_h + 74,
        })
    except Exception as exc:
        log_soft_exception(
            "Failed to add credits image 'assets/macbook.png'",
            exc,
            once_key="credits_macbook",
        )
    add_spacer(18)

    add_text("Enemies & Visual Assets", 36, (255, 220, 86), bold=True, spacing=58)
    image_sources = []
    image_sources.extend(collect_files_with_extensions("assets/obstacles", (".png",)))
    image_sources.extend(collect_files_with_extensions("assets/pc", (".png",)))
    image_sources.extend(collect_files_with_extensions("assets/npc", (".png",)))

    for full_path, rel_path, file_name in image_sources:
        try:
            raw = pg_image.load(full_path).convert_alpha()
        except Exception as exc:
            log_soft_exception(
                f"Failed to load credits image '{full_path}'",
                exc,
                once_key=f"credits_image:{full_path}",
            )
            continue
        max_w = 250
        max_h = 150
        scale = min(max_w / max(1, raw.get_width()), max_h / max(1, raw.get_height()))
        target_w = max(24, int(raw.get_width() * scale))
        target_h = max(24, int(raw.get_height() * scale))
        scaled = transform.smoothscale(raw, (target_w, target_h))
        items.append({
            "kind": "image",
            "surface": scaled,
            "caption": file_name,
            "subcaption": rel_path,
            "height": target_h + 74,
        })

    add_spacer(20)
    add_text("Tunes", 36, (255, 220, 86), bold=True, spacing=58)
    audio_sources = collect_files_with_extensions(
        "assets/audio",
        (".wav", ".mp3", ".m4a", ".ogg", ".flac"),
    )
    for _, rel_path, file_name in audio_sources:
        add_text(file_name, 21, (226, 226, 208), mono=True, spacing=34)
        add_text(f"assets/{rel_path}", 16, (160, 160, 150), mono=True, spacing=28)

    add_spacer(36)
    add_text("May your jumps be high and your hitboxes fair.", 24, (255, 233, 154), spacing=42)
    add_text("THE END", 46, (255, 86, 86), bold=True, spacing=72)

    return items


def start_credits_mode():
    global credits_active, credits_finished, credits_started_ms
    global credits_items, credits_content_height, credits_scroll_speed_px_per_ms
    global credits_total_duration_ms, credits_starfield, pending_credits_after_victory
    credits_items = build_credits_items()
    credits_content_height = sum(item.get("height", 0) for item in credits_items)
    travel_px = (height + CREDITS_BOTTOM_MARGIN) + (credits_content_height + CREDITS_TOP_MARGIN)
    base_speed = travel_px / max(1, CREDITS_DURATION_MS)
    credits_scroll_speed_px_per_ms = max(0.0001, base_speed * CREDITS_SCROLL_SPEED_FACTOR)
    credits_total_duration_ms = int(travel_px / max(0.0001, credits_scroll_speed_px_per_ms))
    credits_started_ms = millis()
    credits_active = True
    credits_finished = False
    pending_credits_after_victory = False
    shared.show_info = False
    stop_intro_speech()
    credits_starfield = [
        (
            random(0, width),
            random(0, height),
            random(1, 3),
            random(0, 1000),
        )
        for _ in range(90)
    ]
    update_background_music(force=True)


def draw_credits_starfield(now_ms):
    for sx, sy, sz, phase in credits_starfield:
        twinkle = 90 + int(90 * (0.5 + 0.5 * math.sin((now_ms + phase) / 420.0)))
        fill(twinkle, twinkle, twinkle)
        rect(int(sx), int(sy), int(sz), int(sz))


def draw_credits_screen():
    global credits_finished
    now = millis()
    background(0, 0, 8)
    draw_credits_starfield(now)

    if not credits_items:
        fill(255, 220, 80)
        text_size(26)
        text("No credits content found.", width // 2 - 138, height // 2)
        return

    elapsed = max(0, now - credits_started_ms)
    elapsed_for_scroll = min(elapsed, credits_total_duration_ms)
    if elapsed >= credits_total_duration_ms:
        credits_finished = True

    start_y = height + CREDITS_BOTTOM_MARGIN
    scroll_offset = start_y - (elapsed_for_scroll * credits_scroll_speed_px_per_ms)

    surface = pg_display.get_surface()
    if surface is None:
        return

    cursor_y = scroll_offset
    center_x = width // 2
    for item in credits_items:
        block_h = item.get("height", 0)
        draw_y = cursor_y
        cursor_y += block_h

        if draw_y + block_h < -120 or draw_y > height + 120:
            continue

        if item["kind"] == "spacer":
            continue

        if item["kind"] == "text":
            font = get_credits_font(
                item.get("font_size", 24),
                mono=item.get("mono", False),
                bold=item.get("bold", False),
            )
            color = item.get("color", (255, 230, 100))
            rendered = font.render(item["text"], True, color)
            perspective_t = max(0.0, min(1.0, (draw_y + block_h) / max(1.0, float(height))))
            scale = 0.42 + (0.58 * perspective_t)
            target_w = max(1, int(rendered.get_width() * scale))
            target_h = max(1, int(rendered.get_height() * scale))
            sprite = transform.smoothscale(rendered, (target_w, target_h))
            surface.blit(sprite, (int(center_x - (target_w / 2)), int(draw_y)))
            continue

        if item["kind"] == "image":
            base = item["surface"]
            perspective_t = max(0.0, min(1.0, (draw_y + block_h) / max(1.0, float(height))))
            scale = 0.48 + (0.52 * perspective_t)
            img_w = max(18, int(base.get_width() * scale))
            img_h = max(18, int(base.get_height() * scale))
            sprite = transform.smoothscale(base, (img_w, img_h))
            img_x = int(center_x - (img_w / 2))
            surface.blit(sprite, (img_x, int(draw_y)))

            caption_font = get_credits_font(18, mono=True, bold=True)
            caption = caption_font.render(item.get("caption", ""), True, (255, 231, 138))
            cx = int(center_x - (caption.get_width() / 2))
            cy = int(draw_y + img_h + 6)
            surface.blit(caption, (cx, cy))

            sub_font = get_credits_font(14, mono=True, bold=False)
            subcaption = sub_font.render(item.get("subcaption", ""), True, (170, 170, 160))
            sx = int(center_x - (subcaption.get_width() / 2))
            sy = cy + 18
            surface.blit(subcaption, (sx, sy))

    if cursor_y < -CREDITS_FINISH_PAD_PX:
        credits_finished = True

    fill(255, 220, 84)
    text_size(20)
    if credits_finished:
        text("Credits complete. Press Q for menu", width // 2 - 166, height - 28)
    else:
        text("Press Q to skip credits", width // 2 - 111, height - 28)


def capture_screenshot():
    global screenshot_notice_until_ms, screenshot_notice_text
    surface = pg_display.get_surface()
    if surface is None:
        screenshot_notice_text = "Screenshot failed (no active surface)"
        screenshot_notice_until_ms = millis() + SCREENSHOT_NOTICE_MS
        return None
    os.makedirs("assets/screenshots", exist_ok=True)
    stamp = int(millis())
    filename = f"level-{current_level:02d}-score-{int(score):03d}-{stamp}.png"
    path = os.path.join("assets", "screenshots", filename)
    try:
        pg_image.save(surface, path)
    except Exception as exc:
        log_soft_exception(
            f"Failed to save screenshot '{path}'",
            exc,
            once_key=f"screenshot:{path}",
        )
        screenshot_notice_text = "Screenshot failed (save error)"
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
    except Exception as exc:
        log_soft_exception(
            "Failed to play sound effect",
            exc,
            once_key="play_sfx",
        )


def make_pipe_entry_sound():
    try:
        init_info = mixer.get_init()
    except Exception as exc:
        log_soft_exception(
            "Failed to query mixer init state for pipe entry sound",
            exc,
            once_key="pipe_sound_get_init",
        )
        init_info = None
    if not init_info:
        return None

    sample_rate, _, channels = init_info
    sample_rate = int(sample_rate or 44100)
    channels = max(1, int(channels or 1))
    total_samples = int(sample_rate * 0.52)
    chirps = (
        (0.02, 0.12, 540.0, 330.0),
        (0.19, 0.29, 470.0, 280.0),
        (0.36, 0.47, 390.0, 220.0),
    )
    sound_buffer = bytearray()

    for sample_idx in range(total_samples):
        t = sample_idx / sample_rate
        value = 0.0
        for start_t, end_t, start_freq, end_freq in chirps:
            if start_t <= t <= end_t:
                p = (t - start_t) / max(0.001, end_t - start_t)
                freq = start_freq + ((end_freq - start_freq) * p)
                envelope = math.sin(math.pi * p)
                value += math.sin((2.0 * math.pi * freq * t) + (p * p * 8.0)) * envelope
        sample = int(max(-1.0, min(1.0, value * 0.35)) * 32767)
        for _ in range(channels):
            sound_buffer.extend(sample.to_bytes(2, byteorder="little", signed=True))

    try:
        return mixer.Sound(buffer=bytes(sound_buffer))
    except Exception as exc:
        log_soft_exception(
            "Failed to create synthesized pipe entry sound",
            exc,
            once_key="pipe_sound_create",
        )
        return None


def make_high_jump_sound():
    try:
        init_info = mixer.get_init()
    except Exception as exc:
        log_soft_exception(
            "Failed to query mixer init state for high jump sound",
            exc,
            once_key="high_jump_sound_get_init",
        )
        init_info = None
    if not init_info:
        return None

    sample_rate, _, channels = init_info
    sample_rate = int(sample_rate or 44100)
    channels = max(1, int(channels or 1))
    total_samples = int(sample_rate * 0.27)
    start_freq = 420.0
    end_freq = 930.0
    sound_buffer = bytearray()

    for sample_idx in range(total_samples):
        progress = sample_idx / max(1, total_samples - 1)
        t = sample_idx / sample_rate
        freq = start_freq + ((end_freq - start_freq) * (progress * progress))
        envelope = math.sin(math.pi * min(1.0, progress ** 0.72))
        chirp = math.sin(2.0 * math.pi * freq * t)
        shimmer = math.sin(2.0 * math.pi * (freq * 1.9) * t + (progress * 2.4)) * 0.22
        sample = int(max(-1.0, min(1.0, (chirp + shimmer) * envelope * 0.38)) * 32767)
        for _ in range(channels):
            sound_buffer.extend(sample.to_bytes(2, byteorder="little", signed=True))

    try:
        return mixer.Sound(buffer=bytes(sound_buffer))
    except Exception as exc:
        log_soft_exception(
            "Failed to create synthesized high jump sound",
            exc,
            once_key="high_jump_sound_create",
        )
        return None


def stop_intro_speech():
    global INTRO_SPEECH_CHANNEL
    try:
        if INTRO_SPEECH_CHANNEL is not None:
            INTRO_SPEECH_CHANNEL.stop()
    except Exception as exc:
        log_soft_exception(
            "Failed to stop intro speech",
            exc,
            once_key="stop_intro_speech",
        )
    INTRO_SPEECH_CHANNEL = None


def play_intro_speech(force_restart=True):
    global INTRO_SPEECH_CHANNEL
    if INTRO_SPEECH_SOUND is None or not shared.sound_enabled:
        return
    try:
        if INTRO_SPEECH_CHANNEL is not None and INTRO_SPEECH_CHANNEL.get_busy():
            if not force_restart:
                return
            INTRO_SPEECH_CHANNEL.stop()
        INTRO_SPEECH_CHANNEL = INTRO_SPEECH_SOUND.play()
    except Exception as exc:
        log_soft_exception(
            "Failed to play intro speech",
            exc,
            once_key="play_intro_speech",
        )
        INTRO_SPEECH_CHANNEL = None


def is_intro_speech_playing():
    try:
        return INTRO_SPEECH_CHANNEL is not None and INTRO_SPEECH_CHANNEL.get_busy()
    except Exception as exc:
        log_soft_exception(
            "Failed to query intro speech state",
            exc,
            once_key="intro_speech_busy",
        )
        return False


def toggle_intro_speech_playback():
    if is_intro_speech_playing():
        stop_intro_speech()
        return False
    play_intro_speech(force_restart=True)
    return True


def get_jump_sound(is_high_jump=False):
    if is_high_jump:
        if HIGH_JUMP_SOUND is not None:
            return HIGH_JUMP_SOUND
    return JUMP_SOUND


def play_pending_high_jump_landing_roar():
    global pending_high_jump_landing_roar
    if not pending_high_jump_landing_roar:
        return
    pending_high_jump_landing_roar = False
    if DINO_ROAR_SOUND is not None:
        play_sfx(DINO_ROAR_SOUND)


def setup():
    global JUMP_SOUND, HIGH_JUMP_SOUND, DINO_ROAR_SOUND, PIPE_ENTRY_SOUND, CRASH_SOUND, HISS_SOUND
    global SPLASH_SOUND, FIRE_PLAYER_SOUND, FIRE_ENEMY_SOUND
    global BOSS_EXPLOSION_SOUND, COIN_SOUND, MINI_BOSS_VICTORY_SOUND, INTRO_SPEECH_SOUND
    global TOUCH_CONTROLS_ENABLED
    size(BASE_GAME_WIDTH, BASE_GAME_HEIGHT)
    frame_rate(60)
    title("Dino Game")
    TOUCH_CONTROLS_ENABLED = detect_touch_controls_enabled()
    reset_game(show_splash=True)

    try:
        if not mixer.get_init():
            mixer.init()
    except Exception as exc:
        log_soft_exception(
            "Failed to initialize mixer in setup()",
            exc,
            once_key="setup_mixer_init",
        )
        return

    JUMP_SOUND = load_sound_or_none("assets/audio/jump.wav")
    HIGH_JUMP_SOUND = make_high_jump_sound()
    DINO_ROAR_SOUND = load_sound_or_none("assets/audio/roaarr.wav")

    PIPE_ENTRY_SOUND = make_pipe_entry_sound()

    CRASH_SOUND = load_sound_or_none("assets/audio/crash.wav")
    HISS_SOUND = load_sound_or_none("assets/audio/hiss.wav")
    SPLASH_SOUND = load_sound_or_none("assets/audio/splash.wav")
    FIRE_PLAYER_SOUND = load_sound_or_none("assets/audio/fire-player.wav")
    FIRE_ENEMY_SOUND = load_sound_or_none("assets/audio/fire-enemy.wav")
    BOSS_EXPLOSION_SOUND = load_sound_or_none("assets/audio/boss-explosion.wav")
    COIN_SOUND = load_sound_or_none("assets/audio/ping.wav")
    MINI_BOSS_VICTORY_SOUND = load_sound_or_none("assets/audio/victory.wav")
    if MINI_BOSS_VICTORY_SOUND is None:
        MINI_BOSS_VICTORY_SOUND = COIN_SOUND

    INTRO_SPEECH_SOUND = None
    for speech_path in INTRO_SPEECH_CANDIDATES:
        if not os.path.exists(speech_path):
            continue
        try:
            INTRO_SPEECH_SOUND = mixer.Sound(speech_path)
            break
        except Exception as exc:
            log_soft_exception(
                f"Failed to load intro speech '{speech_path}'",
                exc,
                once_key=f"intro_speech:{speech_path}",
            )
            INTRO_SPEECH_SOUND = None

    update_background_music(force=True)


def get_player_x():
    return player_x


def get_dino_hitbox_for_state(player_draw_x, dino_base_y, ducking=False):
    if ducking:
        dino_h = DUCK_H
        inset_left = DINO_DUCK_HITBOX_INSET_LEFT
        inset_right = DINO_DUCK_HITBOX_INSET_RIGHT
        inset_top = DINO_DUCK_HITBOX_INSET_TOP
        inset_bottom = DINO_DUCK_HITBOX_INSET_BOTTOM
        y_offset = DINO_DUCK_HITBOX_Y_OFFSET
        dino_draw_y = dino_base_y + (DINO_H - DUCK_H)
    else:
        dino_h = DINO_H
        inset_left = DINO_HITBOX_INSET_LEFT
        inset_right = DINO_HITBOX_INSET_RIGHT
        inset_top = DINO_HITBOX_INSET_TOP
        inset_bottom = DINO_HITBOX_INSET_BOTTOM
        y_offset = DINO_HITBOX_Y_OFFSET
        dino_draw_y = dino_base_y

    return (
        player_draw_x + inset_left,
        dino_draw_y + inset_top + y_offset,
        DINO_W - inset_left - inset_right,
        dino_h - inset_top - inset_bottom,
    )


def get_dino_hitbox():
    player_draw_x = get_player_x()
    ducking = bool(is_ducking and on_ground and not game_over)
    return get_dino_hitbox_for_state(player_draw_x, dino_y, ducking)


def choose_obstacle_type():
    global queued_obstacle_after_powerup, queued_spawn_sequence
    if pending_weapon_powerup_level > 0 and not weapon_powerup_ready:
        return "weapon_powerup"

    if pending_airplane_spawn and current_level in (5, 6):
        return "airplane_pickup"

    if queued_spawn_sequence:
        return queued_spawn_sequence.pop(0)

    if queued_obstacle_after_powerup is not None:
        queued_type = queued_obstacle_after_powerup
        queued_obstacle_after_powerup = None
        return queued_type

    if USE_SCRIPTED_OBSTACLE_PATTERNS:
        chosen = get_next_scripted_obstacle_type()
    else:
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

        elif current_level < 4:
            roll = int(random(0, 100))
            if roll < 16:
                chosen = "cactus_low"
            elif roll < 30:
                chosen = "cactus_high"
            elif roll < 52:
                chosen = "jump_block"
            elif roll < 66:
                chosen = "cactus_tower"
            elif roll < 92:
                chosen = "snake"
            else:
                chosen = "bird_low"

        else:
            roll = int(random(0, 100))
            if current_level in (5, 6):
                # Pipe chapters: pipes are normal obstacles, airplane is optional pickup.
                if roll < 44:
                    chosen = "pipe_pair"
                elif roll < 64:
                    chosen = "cactus_low"
                elif roll < 76:
                    chosen = "cactus_high"
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
    if (not USE_SCRIPTED_OBSTACLE_PATTERNS) and chosen in ("cactus_low", "cactus_high", "cactus_tower", "snake", "bird_low"):
        if int(random(0, 100)) < COIN_SPAWN_CHANCE_PCT:
            if int(random(0, 100)) < COIN_ARC_SPAWN_CHANCE_PCT:
                queued_coin_spawn_ys.extend(get_coin_arc_spawn_ys(chosen))
                queued_spawn_sequence = ["coin", "coin", "coin", "coin", chosen]
            else:
                queued_coin_spawn_ys.append(get_random_coin_spawn_y())
                queued_spawn_sequence = [chosen]
            return "coin"

    return chosen


def get_random_coin_spawn_y():
    coin_ys = [320, 350, 382]
    return coin_ys[int(random(0, len(coin_ys)))]


def get_active_coin_arc_lift():
    lift = 0
    if high_jump_powerup_charges > 0:
        lift += 142
    if is_jump_shoes_active():
        lift += 56
    return lift


def get_coin_arc_spawn_ys(obstacle_kind):
    obstacle_cfg = OBSTACLE_CONFIG.get(obstacle_kind, OBSTACLE_CONFIG["cactus_low"])
    obstacle_top = int(obstacle_cfg["y"])
    lift = get_active_coin_arc_lift()
    side_y = max(134, obstacle_top - 18 - lift)
    inner_y = max(112, obstacle_top - 52 - lift)
    apex_y = max(92, obstacle_top - 86 - lift)
    return [side_y, inner_y, apex_y, inner_y, side_y]


def build_ground_flowers():
    flowers = []
    for _ in range(JUMP_BLOCK_FLOWER_COUNT):
        flowers.append({
            "x": float(random(18, width - 24)),
            "stem_h": float(random(12, 24)),
            "petal_r": float(random(4, 7)),
            "stem": (
                int(random(42, 64)),
                int(random(148, 182)),
                int(random(58, 88)),
            ),
            "petal": (
                int(random(214, 255)),
                int(random(92, 214)),
                int(random(120, 255)),
            ),
            "center": (
                int(random(222, 255)),
                int(random(196, 238)),
                int(random(62, 108)),
            ),
        })
    return flowers


def trigger_jump_block_rain(obstacle_draw_x, obstacle_draw_y, obstacle_draw_w):
    global wet_ground_until_ms, wet_ground_started_ms
    global jump_block_droplets, ground_flowers
    now = millis()
    wet_ground_started_ms = now
    wet_ground_until_ms = now + JUMP_BLOCK_WET_GROUND_MS
    ground_flowers = build_ground_flowers()
    jump_block_droplets = []
    for _ in range(JUMP_BLOCK_DROPLET_COUNT):
        jump_block_droplets.append({
            "x": float(obstacle_draw_x + random(4, obstacle_draw_w - 4)),
            "y": float(obstacle_draw_y + 8),
            "vy": float(random(2.6, 5.4)),
            "size": int(random(3, 6)),
        })


def is_ground_wet_active():
    return millis() < wet_ground_until_ms


def maybe_spawn_bonus_coin_pattern(base_type, base_x):
    if base_type not in ("cactus_low", "cactus_high", "cactus_tower", "snake"):
        return

    obstacle_cfg = OBSTACLE_CONFIG[base_type]
    obstacle_w = obstacle_cfg["w"]
    obstacle_y = obstacle_cfg["y"]
    obstacle_h = obstacle_cfg["h"]
    obstacle_center_x = base_x + (obstacle_w / 2)
    coin_size = OBSTACLE_CONFIG["coin"]["w"]
    lift = get_active_coin_arc_lift()

    if int(random(0, 100)) < BONUS_COIN_ARC_CHANCE_PCT:
        arc_points = [
            (-56, -48 - lift),
            (-24, -84 - lift),
            (8, -118 - lift),
            (40, -84 - lift),
            (72, -48 - lift),
        ]
        for dx, dy in arc_points:
            bonus_coins.append({
                "x": float(obstacle_center_x + dx),
                "y": float(obstacle_y + dy),
                "w": coin_size,
                "h": coin_size,
            })
        return

    if int(random(0, 100)) < BONUS_COIN_LINE_CHANCE_PCT:
        line_y = float(max(122, obstacle_y - obstacle_h - 16 - int(lift * 0.85)))
        start_x = obstacle_center_x - 54
        for idx in range(4):
            bonus_coins.append({
                "x": float(start_x + idx * 34),
                "y": line_y,
                "w": coin_size,
                "h": coin_size,
            })


def maybe_spawn_extra_obstacle_pack(base_type, base_x):
    global multi_jump_notice_until_ms
    if USE_SCRIPTED_OBSTACLE_PATTERNS:
        return
    if current_level < 8:
        return
    if base_type not in ("cactus_low", "cactus_high", "cactus_tower"):
        return
    if int(random(0, 100)) >= MULTI_OBSTACLE_PACK_CHANCE_PCT:
        return

    pack_types = ["cactus_low", "cactus_low"]
    if current_level >= 9 and int(random(0, 100)) < 45:
        pack_types.append("cactus_low")

    current_x = base_x
    for idx, obstacle_kind in enumerate(pack_types):
        gap = random(44, 68) if idx == 0 else random(52, 82)
        prev_cfg = OBSTACLE_CONFIG[base_type if idx == 0 else pack_types[idx - 1]]
        current_x += prev_cfg["w"] + gap
        extra_obstacles.append({
            "type": obstacle_kind,
            "x": float(current_x),
            "bird_duck_scored": False,
            "snake_hiss_played": False,
        })

    multi_jump_notice_until_ms = millis() + MULTI_JUMP_NOTICE_MS


def get_extra_obstacle_draw_rect(obstacle):
    cfg = OBSTACLE_CONFIG[obstacle["type"]]
    return obstacle["x"], cfg["y"], cfg["w"], cfg["h"]


def get_extra_obstacle_hitbox(obstacle):
    cfg = OBSTACLE_CONFIG[obstacle["type"]]
    draw_x, draw_y, draw_w, draw_h = get_extra_obstacle_draw_rect(obstacle)
    inset_left, inset_right, inset_top, inset_bottom = cfg["hitbox_insets"]
    return (
        draw_x + inset_left,
        draw_y + inset_top,
        draw_w - inset_left - inset_right,
        draw_h - inset_top - inset_bottom,
    )


def spawn_obstacle(force_type=None):
    global obstacle_x, obstacle_type, bird_duck_scored
    global high_jump_warning_until_ms
    global weapon_powerup_warning_until_ms, water_warning_until_ms
    global airplane_warning_until_ms, pending_airplane_spawn
    global coin_spawn_y
    global ground_pipe_gap_top
    global snake_hiss_played_for_current
    obstacle_type = force_type or choose_obstacle_type()
    obstacle_x = width + random(100, 300)
    bird_duck_scored = False
    snake_hiss_played_for_current = False
    if obstacle_type == "airplane_pickup":
        pending_airplane_spawn = False
        airplane_warning_until_ms = millis() + AIRPLANE_WARNING_DURATION_MS
    if obstacle_type == "pipe_pair":
        # Ground pipe pair: gap tuned for normal jump/duck traversal.
        ground_pipe_gap_top = int(random(168, 262))
    if obstacle_type == "weapon_powerup":
        weapon_powerup_warning_until_ms = millis() + WEAPON_POWERUP_NOTICE_MS
    if obstacle_type == "coin":
        if queued_coin_spawn_ys:
            coin_spawn_y = queued_coin_spawn_ys.pop(0)
        else:
            coin_spawn_y = get_random_coin_spawn_y()
    if obstacle_type == "water_lily":
        water_warning_until_ms = millis() + WATER_WARNING_DURATION_MS
    if obstacle_type == "cactus_tower":
        high_jump_warning_until_ms = millis() + HIGH_JUMP_WARNING_DURATION_MS
    maybe_spawn_extra_obstacle_pack(obstacle_type, obstacle_x)
    maybe_spawn_bonus_coin_pattern(obstacle_type, obstacle_x)


def get_flight_plane_rect():
    return (flight_plane_x, flight_plane_y, AIRPLANE_PICKUP_W, AIRPLANE_PICKUP_H)


def get_flight_plane_bounds(has_boss=False):
    plane_w = AIRPLANE_PICKUP_W
    plane_h = AIRPLANE_PICKUP_H
    min_x = 20.0
    max_x = float(width - plane_w - 20) if has_boss else float((width // 2) - plane_w - 10)
    min_y = 50.0
    max_y = float(GROUND_Y - plane_h - 4)
    return (min_x, max_x, min_y, max_y)


def get_zeppelin_intro_progress(boss, now=None):
    if boss.get("type") != "zeppelin_miniboss" or boss.get("phase") != "approach":
        return 1.0
    if now is None:
        now = millis()
    duration_ms = max(1, int(boss.get("approach_duration_ms", ZEPPELIN_CITY_APPROACH_DURATION_MS)))
    elapsed = max(0, now - int(boss.get("phase_started_ms", now)))
    return max(0.0, min(1.0, elapsed / float(duration_ms)))


def update_zeppelin_boss_phase(boss, now):
    if boss.get("type") != "zeppelin_miniboss" or boss.get("phase") != "approach":
        return False

    progress = get_zeppelin_intro_progress(boss, now)
    eased = 1.0 - ((1.0 - progress) ** 3)
    boss["x"] = boss["approach_from_x"] + ((boss["approach_to_x"] - boss["approach_from_x"]) * eased)
    boss["y"] = boss["approach_from_y"] + ((boss["approach_to_y"] - boss["approach_from_y"]) * eased)

    if progress < 1.0:
        return False

    boss["phase"] = "fight"
    boss["phase_started_ms"] = now
    boss["x"] = boss["approach_to_x"]
    boss["y"] = boss["approach_to_y"]
    boss["vx"] = boss.get("fight_vx", -1.9)
    boss["vy"] = boss.get("fight_vy", 0.9)
    return True


def spawn_flight_pipe():
    gap_top = int(random(90, GROUND_Y - FLIGHT_PIPE_GAP_H - 50))
    flight_pipes.append({
        "x": width + 20,
        "gap_top": gap_top,
        "passed": False,
    })


def start_flight_mode():
    global flight_mode, flight_plane_x, flight_plane_y, flight_mode_entry_level, flight_mode_exit_level
    global flight_pipe_spawn_due_ms, flight_pipes
    global flight_plane_hp, flight_plane_smoke_next_ms, flight_plane_smoke_puffs
    global fly_left_pressed, fly_right_pressed, fly_up_pressed, fly_down_pressed
    flight_mode = True
    flight_plane_x = 120.0
    flight_plane_y = float(GROUND_Y - 90)
    flight_mode_entry_level = current_level
    flight_mode_exit_level = 7
    flight_pipe_spawn_due_ms = millis() + 400
    flight_pipes = []
    flight_plane_hp = FLIGHT_PLANE_MAX_HP
    flight_plane_smoke_next_ms = 0
    flight_plane_smoke_puffs = []
    fly_left_pressed = False
    fly_right_pressed = False
    fly_up_pressed = False
    fly_down_pressed = False


def end_flight_mode():
    global flight_mode, flight_pipes, flight_pipe_spawn_due_ms
    global flight_plane_hp, flight_plane_smoke_next_ms, flight_plane_smoke_puffs
    global fly_left_pressed, fly_right_pressed, fly_up_pressed, fly_down_pressed
    global dino_y, velocity_y, on_ground, is_ducking, is_fast_falling, player_x
    flight_mode = False
    flight_pipes = []
    flight_pipe_spawn_due_ms = 0
    flight_plane_hp = FLIGHT_PLANE_MAX_HP
    flight_plane_smoke_next_ms = 0
    flight_plane_smoke_puffs = []
    fly_left_pressed = False
    fly_right_pressed = False
    fly_up_pressed = False
    fly_down_pressed = False
    player_x = float(flight_plane_x)
    dino_y = float(flight_plane_y)
    velocity_y = 0
    on_ground = False
    is_ducking = False
    is_fast_falling = False
    spawn_obstacle()


def begin_post_boss_fall_in(fall_x=None, fall_y=None):
    global player_x, dino_y, velocity_y, on_ground, is_ducking, is_fast_falling
    global boss_left_pressed, boss_right_pressed

    resolved_x = player_x if fall_x is None else fall_x
    resolved_y = dino_y if fall_y is None else fall_y
    player_x = float(resolved_x)
    dino_y = float(resolved_y)
    velocity_y = 0
    on_ground = not (dino_y < DINO_Y)
    is_ducking = False
    is_fast_falling = False
    boss_left_pressed = False
    boss_right_pressed = False
    spawn_obstacle()


def start_post_boss_transition(boss_snapshot):
    global post_boss_transition
    transition_player_x = player_x
    transition_player_y = dino_y
    if boss_snapshot.get("level") == 6 and flight_mode:
        transition_player_x = flight_plane_x
        transition_player_y = flight_plane_y
    post_boss_transition = {
        "level": int(boss_snapshot.get("level", 0)),
        "type": boss_snapshot.get("type"),
        "snapshot": dict(boss_snapshot),
        "player_x": float(transition_player_x),
        "player_y": float(transition_player_y),
    }


def resolve_post_boss_transition_if_ready():
    global post_boss_transition
    if post_boss_transition is None:
        return False
    if mini_boss_defeat_sequences or explosion_effects:
        return False

    transition_level = int(post_boss_transition.get("level", 0))
    transition_player_x = float(post_boss_transition.get("player_x", player_x))
    transition_player_y = float(post_boss_transition.get("player_y", dino_y))
    post_boss_transition = None
    if transition_level == 6:
        end_flight_mode()
    else:
        begin_post_boss_fall_in(transition_player_x, transition_player_y)
    return True


def draw_post_boss_transition(theme):
    transition = post_boss_transition
    if transition is None:
        return False

    snapshot = transition.get("snapshot")
    transition_type = transition.get("type")
    if transition_type == "bird_miniboss":
        draw_bird_boss_arena(theme)
    elif transition_type == "cactus_miniboss":
        draw_cactus_boss_arena(theme)
    elif transition_type == "zeppelin_miniboss":
        draw_zeppelin_boss_arena(theme)
    else:
        background(*theme["bg"])

    if snapshot is not None:
        draw_boss_entity(snapshot)
    draw_main_character()
    draw_explosion_effects()
    draw_hud(theme, force_visible=True)
    draw_touch_controls_overlay()
    draw_debug_overlay()
    return True


def crash_flight_mode():
    apply_player_hit(CRASH_SOUND)
    end_flight_mode()


def spawn_flight_plane_smoke_puff():
    puff_x = flight_plane_x + 14
    puff_y = flight_plane_y + (AIRPLANE_PICKUP_H * 0.58)
    flight_plane_smoke_puffs.append({
        "x": float(puff_x),
        "y": float(puff_y),
        "size": float(random(16, 24)),
        "vx": float(random(-0.8, -0.2)),
        "vy": float(random(-0.5, -0.15)),
        "life_ms": int(random(900, 1300)),
        "spawned_ms": millis(),
    })
    overflow = len(flight_plane_smoke_puffs) - 18
    if overflow > 0:
        del flight_plane_smoke_puffs[0:overflow]


def register_flight_plane_damage_from_zeppelin():
    global flight_plane_hp, flight_plane_smoke_next_ms, player_damage_cooldown_until_ms
    now = millis()
    if now < player_damage_cooldown_until_ms:
        return False

    flight_plane_hp = max(0, flight_plane_hp - 1)
    player_damage_cooldown_until_ms = now + PLAYER_DAMAGE_COOLDOWN_MS
    spawn_flight_plane_smoke_puff()
    play_sfx(CRASH_SOUND)

    if flight_plane_hp <= 0:
        crash_flight_mode()
        return True

    smoke_interval = FLIGHT_PLANE_SMOKE_INTERVAL_MS.get(flight_plane_hp, 0)
    flight_plane_smoke_next_ms = now + smoke_interval if smoke_interval > 0 else 0
    return False


def update_and_draw_flight_plane_smoke():
    global flight_plane_smoke_next_ms
    if flight_plane_hp < FLIGHT_PLANE_MAX_HP and flight_plane_hp > 0:
        now = millis()
        if flight_plane_smoke_next_ms > 0 and now >= flight_plane_smoke_next_ms:
            spawn_flight_plane_smoke_puff()
            smoke_interval = FLIGHT_PLANE_SMOKE_INTERVAL_MS.get(flight_plane_hp, 0)
            flight_plane_smoke_next_ms = now + smoke_interval if smoke_interval > 0 else 0

    if not flight_plane_smoke_puffs:
        return

    now = millis()
    alive_puffs = []
    for puff in flight_plane_smoke_puffs:
        age = now - puff["spawned_ms"]
        if age >= puff["life_ms"]:
            continue
        progress = max(0.0, min(1.0, age / max(1, puff["life_ms"])))
        puff["x"] += puff["vx"]
        puff["y"] += puff["vy"]
        puff_size = puff["size"] * (1.0 + (progress * 0.7))
        shade = int(142 + (46 * (1.0 - progress)))
        fill(shade, shade, shade)
        ellipse(int(puff["x"]), int(puff["y"]), int(puff_size), int(puff_size * 0.82))
        alive_puffs.append(puff)
    flight_plane_smoke_puffs[:] = alive_puffs


def get_ground_pipe_rects(draw_x=None):
    pipe_x = obstacle_x if draw_x is None else draw_x
    gap_top = int(ground_pipe_gap_top)
    top_rect = (pipe_x, 0, FLIGHT_PIPE_WIDTH, gap_top)
    bottom_y = gap_top + FLIGHT_PIPE_GAP_H
    bottom_rect = (
        pipe_x,
        bottom_y,
        FLIGHT_PIPE_WIDTH,
        max(0, GROUND_Y - bottom_y),
    )
    return top_rect, bottom_rect


def draw_pipe_column(x, y, w, h):
    if h <= 0 or w <= 0:
        return
    x = int(x)
    y = int(y)
    w = int(w)
    h = int(h)
    lip_h = min(14, max(8, int(h * 0.2)))
    inner_w = max(10, w - 16)

    fill(74, 160, 90)
    rect(x, y, w, h)

    fill(42, 124, 60)
    rect(x + 8, y + lip_h + 4, inner_w, max(4, h - (lip_h + 8)))

    fill(92, 194, 110)
    rect(x - 4, y, w + 8, lip_h)
    fill(56, 138, 72)
    rect(x + 4, y + 2, max(8, w - 8), max(4, lip_h - 4))


def draw_ground_pipe_pair(draw_x=None):
    top_rect, bottom_rect = get_ground_pipe_rects(draw_x=draw_x)
    tx, ty, tw, th = top_rect
    bx, by, bw, bh = bottom_rect
    draw_pipe_column(tx, ty, tw, th)
    draw_pipe_column(bx, by, bw, bh)


def platform_supports_player(platform_rect):
    platform_x, platform_y, platform_w, _ = platform_rect
    current_hitbox = get_dino_hitbox()
    current_bottom = current_hitbox[1] + current_hitbox[3]
    return (
        current_hitbox[0] + current_hitbox[2] > platform_x + 6
        and current_hitbox[0] < platform_x + platform_w - 6
        and abs(current_bottom - platform_y) <= 8
    )


def apply_one_way_platform_collision(platform_rect, prev_player_x, prev_dino_y, prev_ducking, drop_if_unsupported=True):
    global dino_y, velocity_y, on_ground, is_fast_falling
    platform_x, platform_y, platform_w, _ = platform_rect
    platform_left = platform_x
    platform_right = platform_x + platform_w

    # If we were standing on an elevated platform and moved past its edge, start falling.
    if drop_if_unsupported and on_ground and dino_y < DINO_Y:
        if not platform_supports_player(platform_rect):
            on_ground = False

    prev_hitbox = get_dino_hitbox_for_state(prev_player_x, prev_dino_y, prev_ducking)
    current_hitbox = get_dino_hitbox()
    prev_bottom = prev_hitbox[1] + prev_hitbox[3]
    curr_bottom = current_hitbox[1] + current_hitbox[3]

    landing_overlap_x = (
        current_hitbox[0] + current_hitbox[2] > platform_left + 6
        and current_hitbox[0] < platform_right - 6
    )
    landing_from_above = (
        velocity_y >= 0
        and prev_bottom <= platform_y + 6
        and curr_bottom >= platform_y
        and landing_overlap_x
    )
    if not landing_from_above:
        return False

    dino_y = platform_y - DINO_H
    velocity_y = 0
    on_ground = True
    is_fast_falling = False
    play_pending_high_jump_landing_roar()
    return True


def apply_ground_pipe_platform_collision(prev_dino_y, prev_ducking):
    _, pipe_bottom = get_ground_pipe_rects()
    # Platformer rule: only the top surface of the lower pipe is solid.
    return apply_one_way_platform_collision(pipe_bottom, get_player_x(), prev_dino_y, prev_ducking)


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
    elif obstacle_type == "pipe_pair":
        draw_y = 0
        draw_w = FLIGHT_PIPE_WIDTH
        draw_h = GROUND_Y

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


def get_pipe_crouch_sprite(character_key):
    if character_key not in pipe_crouch_sprite_cache:
        pipe_crouch_path = CHARACTER_CONFIG[character_key]["pipe_crouch_path"]
        if os.path.exists(pipe_crouch_path):
            pipe_crouch_sprite_cache[character_key] = load_image(pipe_crouch_path)
        else:
            pipe_crouch_sprite_cache[character_key] = CHARACTER_CONFIG[character_key].get(
                "duck",
                CHARACTER_CONFIG[character_key]["stand"],
            )
    return pipe_crouch_sprite_cache[character_key]


def get_level_start_score(level):
    idx = max(1, min(MAX_LEVEL, int(level))) - 1
    return int(LEVEL_START_SCORES[idx])


def get_level_start_obstacle_count(level):
    idx = max(1, min(MAX_LEVEL, int(level))) - 1
    return int(LEVEL_START_OBSTACLE_COUNTS[idx])


def get_level_total_obstacle_count(level):
    idx = max(1, min(MAX_LEVEL, int(level))) - 1
    return int(LEVEL_OBSTACLE_TOTAL_THRESHOLDS[idx])


def get_level_total_score(level):
    idx = max(1, min(MAX_LEVEL, int(level))) - 1
    return int(LEVEL_SCORE_REFERENCE_TOTALS[idx])


def get_level_for_obstacle_count(current_obstacle_count):
    obstacle_value = max(0, int(current_obstacle_count))
    for idx, total_threshold in enumerate(LEVEL_OBSTACLE_TOTAL_THRESHOLDS, start=1):
        if obstacle_value < total_threshold:
            return idx
    return MAX_LEVEL


def reset_scripted_obstacle_sequence(level=None):
    global scripted_obstacle_level, scripted_obstacle_index
    target_level = current_level if level is None else level
    scripted_obstacle_level = max(1, min(MAX_LEVEL, int(target_level)))
    scripted_obstacle_index = 0


def get_next_scripted_obstacle_type():
    global scripted_obstacle_index
    if scripted_obstacle_level != current_level:
        reset_scripted_obstacle_sequence(current_level)

    pattern = LEVEL_SCRIPTED_OBSTACLE_PATTERNS.get(current_level)
    if not pattern:
        return "cactus_low"

    chosen = pattern[scripted_obstacle_index % len(pattern)]
    scripted_obstacle_index += 1
    return chosen


def save_character_checkpoint(level=None, character_key=None):
    checkpoint_character_key = character_key or active_character_key
    checkpoint_level = current_level if level is None else level
    checkpoint_level_by_character[checkpoint_character_key] = max(
        1,
        min(MAX_LEVEL, int(checkpoint_level)),
    )


def restore_character_checkpoint(character_key):
    global current_level, score, scroll_speed, obstacles_cleared, next_level_obstacle_goal
    global scripted_obstacle_level, scripted_obstacle_index
    checkpoint_level = checkpoint_level_by_character.get(character_key, 1)
    current_level = checkpoint_level
    score = get_level_start_score(checkpoint_level)
    obstacles_cleared = get_level_start_obstacle_count(checkpoint_level)
    scroll_speed = BASE_SCROLL_SPEED * (LEVEL_SPEED_FACTOR ** (current_level - 1))
    next_level_obstacle_goal = get_level_total_obstacle_count(current_level)
    scripted_obstacle_level = current_level
    scripted_obstacle_index = 0


def start_game_from_selection():
    global active_character_key, pending_airplane_spawn
    active_character_key = get_selected_character_key()
    reset_game(show_splash=False)
    restore_character_checkpoint(active_character_key)
    activate_shop_powerups_for_run()
    pending_airplane_spawn = (current_level in (5, 6))


def get_theme():
    return CHARACTER_CONFIG[get_current_character_key()]["theme"]


def get_boss_shop_target_level():
    if pending_boss_shop_level > 0:
        return pending_boss_shop_level
    if pre_boss_scene_level > 0:
        return pre_boss_scene_level
    return 0


def get_boss_weapon_shop_item():
    weapon_label = get_player_weapon_profile()["label"]
    target_level = get_boss_shop_target_level()
    level_hint = f" for boss L{target_level}" if target_level > 0 else ""
    return {
        "key": "weapon_powerup",
        "label": weapon_label,
        "cost": SHOP_BOSS_WEAPON_COST,
        "desc": f"Unlock {weapon_label.lower()}{level_hint}.",
    }


def get_active_shop_items():
    items = list(SHOP_ITEMS)
    target_level = get_boss_shop_target_level()
    if target_level > 0 and not (weapon_powerup_ready and weapon_powerup_level == target_level):
        items.append(get_boss_weapon_shop_item())
    return items


def set_shop_notice(message, duration_ms=SHOP_NOTICE_MS):
    global shop_notice_text, shop_notice_until_ms
    shop_notice_text = str(message)
    shop_notice_until_ms = millis() + max(200, int(duration_ms))


def is_shield_active():
    return millis() < shield_until_ms


def is_coin_boost_active():
    return millis() < coin_boost_until_ms


def is_jump_shoes_active():
    return millis() < jump_shoes_until_ms


def activate_shop_powerups_for_run():
    global shop_shield_count, shop_coin_boost_count, shop_jump_shoes_count
    global shield_until_ms, coin_boost_until_ms, jump_shoes_until_ms
    now = millis()
    if shop_shield_count > 0:
        shop_shield_count -= 1
        shield_until_ms = max(shield_until_ms, now + SHOP_SHIELD_MS)
    if shop_coin_boost_count > 0:
        shop_coin_boost_count -= 1
        coin_boost_until_ms = max(coin_boost_until_ms, now + SHOP_COIN_BOOST_MS)
    if shop_jump_shoes_count > 0:
        shop_jump_shoes_count -= 1
        jump_shoes_until_ms = max(jump_shoes_until_ms, now + SHOP_JUMP_SHOES_MS)


def close_shop():
    global shop_active, pending_boss_shop_level
    was_boss_prep_shop = game_started and pending_boss_shop_level > 0
    shop_active = False
    if was_boss_prep_shop:
        activate_shop_powerups_for_run()
        set_shop_notice(f"Boss prep done for L{pending_boss_shop_level}.", duration_ms=1400)
        pending_boss_shop_level = 0


def is_pre_boss_scene_active():
    return game_started and pre_boss_scene_level > 0 and boss_state is None


def get_pre_boss_shop_rect():
    shop_w = 276
    shop_h = 158
    return (64, GROUND_Y - shop_h, shop_w, shop_h)


def get_pre_boss_entrance_rect(level=None):
    target_level = pre_boss_scene_level if level is None else level
    if target_level == 4:
        return BIRD_NEST_ENTRY_RECT
    if target_level >= 10:
        return (width - 168, GROUND_Y - 132, FLIGHT_PIPE_WIDTH, 132)
    return (width - 168, GROUND_Y - 96, FLIGHT_PIPE_WIDTH, 96)


def pre_boss_scene_uses_pipe_entry(level=None):
    target_level = pre_boss_scene_level if level is None else level
    return target_level == 7 or target_level >= 10


def get_shop_overlay_layout():
    stall_x = 86
    stall_y = 136
    stall_w = 628
    stall_h = 246
    layout = []
    active_items = get_active_shop_items()
    if BADGER_SHOP_IMG is not None and len(active_items) <= 4:
        icon_positions = (
            (stall_x + 84, stall_y + 136, 72, 60),
            (stall_x + 206, stall_y + 132, 72, 64),
            (stall_x + 326, stall_y + 134, 72, 60),
            (stall_x + 464, stall_y + 132, 88, 62),
        )
    elif BADGER_SHOP_IMG is not None:
        icon_positions = (
            (stall_x + 44, stall_y + 134, 64, 58),
            (stall_x + 158, stall_y + 130, 64, 62),
            (stall_x + 274, stall_y + 132, 64, 60),
            (stall_x + 390, stall_y + 130, 64, 62),
            (stall_x + 506, stall_y + 132, 76, 60),
        )
    else:
        icon_positions = []
        spacing = 112 if len(active_items) > 4 else 126
        start_x = stall_x + (30 if len(active_items) > 4 else 118)
        base_y = stall_y + 78
        for idx in range(len(active_items)):
            icon_positions.append((start_x + idx * spacing, base_y - (20 if idx % 2 else 0), 76, 76))
    for item, (icon_x, icon_y, icon_w, icon_h) in zip(active_items, icon_positions):
        layout.append((item, icon_x, icon_y, icon_w, icon_h))
    return stall_x, stall_y, stall_w, stall_h, layout


def draw_shop_item_highlight(x, y, w, h, theme, selected=False):
    base_color = theme["ground_line"]
    glow_color = (255, 220, 104) if selected else theme["accent"]
    draw_rounded_rect_outline(x, y, w, h, 14, base_color, 2)
    if selected:
        pulse = (math.sin(millis() / 190.0) + 1.0) * 0.5
        pad = 3 + int(pulse * 5)
        draw_rounded_rect_outline(
            x - pad,
            y - pad,
            w + pad * 2,
            h + pad * 2,
            16,
            glow_color,
            2 + int(pulse * 2),
        )


def draw_shop_item_icon(item_key, x, y, size, theme):
    icon_img = SHOP_ITEM_ICONS.get(item_key)
    if icon_img is not None:
        image(icon_img, x, y, size, size)
        return

    px = int(x)
    py = int(y)
    if item_key == "extra_life":
        fill(214, 36, 58)
        rect(px + 14, py + 12, 16, 16)
        rect(px + 30, py + 12, 16, 16)
        rect(px + 10, py + 24, 40, 14)
        rect(px + 16, py + 38, 28, 12)
        rect(px + 22, py + 50, 16, 10)
        return
    if item_key == "shield":
        fill(64, 122, 210)
        rect(px + 20, py + 14, 32, 34)
        arc(px + 36, py + 14, 32, 24, PI, TWO_PI)
        fill(232, 240, 255)
        rect(px + 28, py + 22, 16, 22)
        return
    if item_key == "coin_boost":
        fill(240, 194, 48)
        rect(px + 16, py + 20, 18, 28)
        rect(px + 34, py + 16, 18, 28)
        fill(204, 146, 24)
        rect(px + 18, py + 24, 14, 20)
        rect(px + 36, py + 20, 14, 20)
        fill(*theme["text"])
        text_size(16)
        text("x2", px + 22, py + 64)
        return
    if item_key == "weapon_powerup":
        profile = get_player_weapon_profile()
        if profile["kind"] == "tnt":
            fill(210, 35, 30)
            rect(px + 14, py + 24, 34, 22)
            fill(255, 220, 100)
            rect(px + 44, py + 18, 4, 8)
            return
        if profile["kind"] == "fire":
            fill(235, 85, 20)
            rect(px + 12, py + 28, 38, 12)
            fill(250, 200, 70)
            rect(px + 22, py + 24, 16, 8)
            return
        fill(22, 22, 22)
        rect(px + 12, py + 30, 40, 8)
        rect(px + 28, py + 36, 8, 16)
        return
    fill(72, 166, 238)
    rect(px + 12, py + 36, 22, 16)
    rect(px + 36, py + 42, 24, 12)
    fill(34, 92, 164)
    rect(px + 10, py + 50, 28, 8)
    rect(px + 36, py + 52, 28, 8)


def draw_shop_icon_button(item, x, y, w, h, theme, selected=False):
    pulse = (math.sin(millis() / 190.0) + 1.0) * 0.5 if selected else 0.0
    glow_color = (255, 220, 104) if selected else theme["ground_line"]
    outer_pad = 2 + int(pulse * 4) if selected else 2
    fill(255, 250, 238)
    rect(x, y, w, h)
    draw_rounded_rect_outline(x, y, w, h, 12, theme["ground_line"], 2)
    draw_rounded_rect_outline(
        x - outer_pad,
        y - outer_pad,
        w + outer_pad * 2,
        h + outer_pad * 2,
        14,
        glow_color,
        2 + int(pulse * 2) if selected else 1,
    )
    draw_shop_item_icon(item["key"], x + 8, y + 6, w - 16, theme)
    fill(*theme["text"])
    text_size(15)
    text(item["label"], x - 10, y + h + 19)
    text_size(14)
    text(f"{item['cost']}c", x + 8, y + h + 35)
    text(f"x{get_shop_item_count(item['key'])}", x + 46, y + h + 35)


def draw_badger_shop_fallback(x, y, w, h, theme):
    fill(135, 84, 48)
    rect(x + 16, y + 82, w - 32, h - 92)
    fill(198, 58, 48)
    rect(x + 8, y + 26, w - 16, 30)
    fill(246, 220, 172)
    for idx in range(6):
        rect(x + 14 + idx * 42, y + 58, 30, 18)
    draw_shop_seller_with_tie(x + 26, y + 24)
    fill(92, 58, 28)
    rect(x + 22, y + h - 30, w - 44, 16)
    fill(*theme["text"])
    text_size(16)
    text("BADGER SHOP", x + 78, y + 20)


def draw_pre_boss_shop_world(theme):
    shop_x, shop_y, shop_w, shop_h = get_pre_boss_shop_rect()
    if BADGER_SHOP_IMG is not None:
        image(BADGER_SHOP_IMG, shop_x, shop_y, shop_w, shop_h)
    else:
        draw_badger_shop_fallback(shop_x, shop_y, shop_w, shop_h, theme)


def draw_cactus_fortress_backdrop(theme):
    fill(182, 143, 98)
    ellipse(156, GROUND_Y - 18, 258, 92)
    ellipse(380, GROUND_Y - 10, 344, 108)
    ellipse(650, GROUND_Y - 16, 286, 96)

    fill(144, 98, 66)
    rect(94, 184, 118, 138)
    rect(108, 162, 78, 28)
    rect(522, 204, 142, 118)
    rect(548, 176, 86, 32)

    fill(199, 164, 120)
    rect(112, 194, 74, 12)
    rect(544, 214, 94, 12)

    if CACTUS_BOSS_IMG is not None:
        image(CACTUS_BOSS_IMG, 224, GROUND_Y - 176, 104, 176)
        image(CACTUS_BOSS_IMG, 470, GROUND_Y - 142, 80, 142)
    else:
        image(CACTUS_IMGS[0], 234, GROUND_Y - 130, 72, 130)
        image(CACTUS_IMGS[0], 482, GROUND_Y - 102, 56, 102)

    if CACTUS_BOSS_TRUNK_IMG is not None:
        image(CACTUS_BOSS_TRUNK_IMG, 618, GROUND_Y - 126, 64, 126)
    else:
        image(CACTUS_IMGS[0], 624, GROUND_Y - 104, 52, 104)

    fill(128, 92, 60)
    rect(0, GROUND_Y - 10, width, 18)


def draw_bird_tree_entry(theme):
    fill(72, 148, 74)
    ellipse(586, 118, 168, 86)
    ellipse(674, 104, 154, 90)
    ellipse(726, 154, 118, 76)
    fill(58, 126, 64)
    ellipse(468, 166, 156, 76)
    ellipse(540, 138, 136, 72)

    fill(106, 68, 38)
    rect(692, 186, 34, GROUND_Y - 186)
    fill(138, 88, 46)
    rect(700, 190, 12, GROUND_Y - 194)

    for idx, (branch_x, branch_y, branch_w, branch_h) in enumerate(BIRD_TREE_BRANCH_RECTS):
        fill(116, 72, 38)
        rect(branch_x, branch_y, branch_w, branch_h)
        fill(154, 96, 48)
        rect(branch_x + 4, branch_y + 2, max(12, branch_w - 12), max(4, branch_h - 6))
        fill(70, 138, 66)
        leaf_x = branch_x + branch_w - 18 if idx % 2 == 0 else branch_x + 18
        ellipse(leaf_x, branch_y - 8, 48, 24)

    nest_x, nest_y, nest_w, nest_h = get_pre_boss_entrance_rect(4)
    fill(112, 72, 42)
    ellipse(nest_x + (nest_w // 2), nest_y + 30, nest_w, nest_h)
    fill(84, 52, 28)
    ellipse(nest_x + (nest_w // 2), nest_y + 24, nest_w - 24, nest_h - 18)
    fill(188, 220, 232)
    ellipse(nest_x + 42, nest_y + 24, 18, 24)
    ellipse(nest_x + 62, nest_y + 22, 18, 24)
    fill(102, 70, 44)
    rect(nest_x + 10, nest_y + 34, nest_w - 20, 10)


def draw_pre_boss_entrance(level, theme):
    entry_x, entry_y, entry_w, entry_h = get_pre_boss_entrance_rect(level)
    if level == 4:
        draw_bird_tree_entry(theme)
        return

    if level >= 10:
        draw_pipe_column(entry_x, entry_y, entry_w, entry_h)
        fill(48, 48, 48)
        rect(entry_x + 16, entry_y + 18, max(16, entry_w - 32), 12)
        fill(34, 34, 34)
        rect(entry_x + 20, entry_y + 22, max(10, entry_w - 40), 6)
        return

    if level == 7:
        fill(124, 90, 60)
        rect(entry_x - 18, entry_y + 56, entry_w + 36, 16)
        fill(164, 120, 76)
        rect(entry_x - 10, entry_y + 60, entry_w + 20, 8)
    draw_pipe_column(entry_x, entry_y, entry_w, entry_h)
    fill(44, 92, 48)
    rect(entry_x + 14, entry_y + 16, max(16, entry_w - 28), 10)


def player_on_platform_top(platform_rect, tolerance=10):
    hitbox = get_dino_hitbox()
    feet_y = hitbox[1] + hitbox[3]
    platform_x, platform_y, platform_w, _ = platform_rect
    overlap_x = hitbox[0] + hitbox[2] > platform_x + 6 and hitbox[0] < platform_x + platform_w - 6
    return overlap_x and abs(feet_y - platform_y) <= tolerance


def player_centered_on_pipe(pipe_rect):
    hitbox = get_dino_hitbox()
    hitbox_center_x = hitbox[0] + (hitbox[2] / 2.0)
    pipe_x, _, pipe_w, _ = pipe_rect
    pipe_center_x = pipe_x + (pipe_w / 2.0)
    return abs(hitbox_center_x - pipe_center_x) <= PIPE_ENTRY_CENTER_TOLERANCE_PX


def start_pipe_entry_sequence(level, pipe_rect):
    global pipe_entry_active, pipe_entry_level, pipe_entry_started_ms
    global pipe_entry_start_x, pipe_entry_start_feet_y, pipe_entry_sound_next_ms
    global player_x, dino_y, velocity_y, on_ground, is_ducking, is_fast_falling
    pipe_x, pipe_y, pipe_w, _ = pipe_rect
    pipe_entry_active = True
    pipe_entry_level = level
    pipe_entry_started_ms = millis()
    pipe_entry_start_x = float(player_x)
    pipe_entry_start_feet_y = float(get_dino_hitbox()[1] + get_dino_hitbox()[3])
    pipe_entry_sound_next_ms = pipe_entry_started_ms
    player_x = float((pipe_x + (pipe_w / 2.0)) - (DINO_W / 2.0))
    dino_y = float(pipe_y - DINO_H)
    velocity_y = 0
    on_ground = True
    is_ducking = True
    is_fast_falling = False
    play_sfx(PIPE_ENTRY_SOUND if PIPE_ENTRY_SOUND is not None else HISS_SOUND)


def update_pipe_entry_sequence():
    global pipe_entry_active, pipe_entry_sound_next_ms
    if not pipe_entry_active:
        return
    now = millis()
    if now >= pipe_entry_sound_next_ms and PIPE_ENTRY_SOUND is None:
        play_sfx(HISS_SOUND)
        pipe_entry_sound_next_ms = now + 190
    if now - pipe_entry_started_ms >= PIPE_ENTRY_DURATION_MS:
        level = pipe_entry_level
        pipe_entry_active = False
        start_pending_boss_encounter(level)


def get_pipe_entry_pose():
    if not pipe_entry_active:
        return None
    pipe_rect = get_pre_boss_entrance_rect(pipe_entry_level)
    pipe_x, pipe_y, pipe_w, pipe_h = pipe_rect
    elapsed = millis() - pipe_entry_started_ms
    target_x = (pipe_x + (pipe_w / 2.0)) - (DINO_W / 2.0)
    center_progress = max(0.0, min(1.0, elapsed / max(1, PIPE_ENTRY_CROUCH_HOLD_MS)))
    center_eased = center_progress * center_progress * (3.0 - (2.0 * center_progress))
    draw_x = pipe_entry_start_x + ((target_x - pipe_entry_start_x) * center_eased)

    sink_elapsed = max(0, elapsed - PIPE_ENTRY_CROUCH_HOLD_MS)
    sink_duration = max(1, PIPE_ENTRY_DURATION_MS - PIPE_ENTRY_CROUCH_HOLD_MS)
    sink_progress = max(0.0, min(1.0, sink_elapsed / sink_duration))
    sink_eased = sink_progress * sink_progress * (3.0 - (2.0 * sink_progress))
    target_feet_y = pipe_y + pipe_h + PIPE_ENTRY_SINK_EXTRA_PX
    feet_y = pipe_entry_start_feet_y + ((target_feet_y - pipe_entry_start_feet_y) * sink_eased)
    return int(draw_x), int(feet_y - DUCK_H), DINO_W, DUCK_H


def draw_pre_boss_scene(theme):
    level = pre_boss_scene_level
    if level <= 0:
        return

    if level == 7:
        background(242, 210, 164)
        fill(198, 156, 108)
        rect(0, GROUND_Y, width, 40)
        draw_cactus_fortress_backdrop(theme)
    else:
        muted_bg = tuple(max(28, int(channel * 0.82)) for channel in theme["bg"])
        muted_ground = tuple(max(36, int(channel * 0.8)) for channel in theme["ground_fill"])
        background(*muted_bg)
        draw_parallax_clouds(theme)
        fill(*muted_ground)
        rect(0, GROUND_Y, width, 40)

    stroke(*theme["ground_line"])
    stroke_weight(2)
    line(0, GROUND_Y, width, GROUND_Y)
    no_stroke()
    draw_pre_boss_shop_world(theme)
    draw_pre_boss_entrance(level, theme)

    fill(*theme["text"])
    text_size(24)
    if level == 4:
        text("Boss approach: climb the tree to the nest.", 132, 44)
    elif level == 7:
        text("Boss approach: jump on the pipe, then duck.", 120, 44)
    else:
        text("Boss approach: visit the shop, then enter the green pipe.", 102, 44)
    text_size(18)
    text(f"Level {level}: {LEVEL_NAMES.get(level, 'Boss Stage')}", 210, 74)


def apply_pre_boss_scene_collisions(prev_player_x, prev_dino_y, prev_ducking):
    global player_x, on_ground
    if pre_boss_scene_level == 4:
        platforms = tuple(BIRD_TREE_BRANCH_RECTS) + (get_pre_boss_entrance_rect(4),)
        landed = False
        for platform_rect in platforms:
            if apply_one_way_platform_collision(
                platform_rect,
                prev_player_x,
                prev_dino_y,
                prev_ducking,
                drop_if_unsupported=False,
            ):
                landed = True
                break
        if (not landed) and on_ground and dino_y < DINO_Y:
            if not any(platform_supports_player(platform_rect) for platform_rect in platforms):
                on_ground = False
        return

    if not pre_boss_scene_uses_pipe_entry():
        return

    pipe_rect = get_pre_boss_entrance_rect(pre_boss_scene_level)
    # Solid side walls for the pipe in the hub scene.
    current_hitbox = get_dino_hitbox()
    prev_hitbox = get_dino_hitbox_for_state(prev_player_x, prev_dino_y, prev_ducking)
    if rects_overlap(current_hitbox, pipe_rect):
        pipe_x, _, pipe_w, _ = pipe_rect
        pipe_left = pipe_x
        pipe_right = pipe_x + pipe_w
        moved_right_into_pipe = prev_hitbox[0] + prev_hitbox[2] <= pipe_left and current_hitbox[0] + current_hitbox[2] > pipe_left
        moved_left_into_pipe = prev_hitbox[0] >= pipe_right and current_hitbox[0] < pipe_right
        if moved_right_into_pipe:
            player_x = min(player_x, float(pipe_left - DINO_W - 1))
        elif moved_left_into_pipe:
            player_x = max(player_x, float(pipe_right + 1))

    # Pipe top is a one-way platform: jump onto it, pass through from below/sides.
    apply_one_way_platform_collision(pipe_rect, prev_player_x, prev_dino_y, prev_ducking)


def start_pending_boss_encounter(level):
    global boss_state, boss_intro_until_ms, player_shot_cooldown_until_ms
    global pre_boss_scene_level, pending_boss_shop_level, shop_active
    global pipe_entry_active, pipe_entry_level
    global player_x, boss_left_pressed, boss_right_pressed
    pre_boss_scene_level = 0
    pending_boss_shop_level = 0
    shop_active = False
    pipe_entry_active = False
    pipe_entry_level = 0
    player_x = float(DINO_X)
    boss_left_pressed = False
    boss_right_pressed = False
    boss_state = spawn_boss_for_level(level)
    boss_intro_until_ms = millis() + BOSS_INTRO_DURATION_MS
    reset_projectile_pool(player_projectiles)
    player_shot_cooldown_until_ms = 0


def maybe_start_bird_nest_encounter():
    if pre_boss_scene_level != 4 or pipe_entry_active or game_over:
        return False
    nest_rect = get_pre_boss_entrance_rect(4)
    if rects_overlap(get_dino_hitbox(), nest_rect) or player_on_platform_top(nest_rect, tolerance=14):
        start_pending_boss_encounter(4)
        return True
    return False


def try_interact_pre_boss_scene():
    global shop_active, shop_selected_index, pending_boss_shop_level
    if not is_pre_boss_scene_active() or game_over or pipe_entry_active:
        return False

    player_hitbox = get_dino_hitbox()
    if rects_overlap(player_hitbox, get_pre_boss_shop_rect()):
        pending_boss_shop_level = pre_boss_scene_level
        shop_active = True
        shop_selected_index = 0
        set_shop_notice("Buy gear from the badger stall, then press Back.", duration_ms=PRE_BOSS_SCENE_NOTICE_MS)
        return True

    entrance_rect = get_pre_boss_entrance_rect(pre_boss_scene_level)
    if pre_boss_scene_uses_pipe_entry():
        ducking_on_pipe = (
            is_ducking
            and on_ground
            and player_on_platform_top(entrance_rect)
            and player_centered_on_pipe(entrance_rect)
        )
        if not ducking_on_pipe:
            return False
        start_pipe_entry_sequence(pre_boss_scene_level, entrance_rect)
        return True

    if rects_overlap(player_hitbox, entrance_rect):
        start_pending_boss_encounter(pre_boss_scene_level)
        return True

    return False


def get_shop_item_count(item_key):
    if item_key == "extra_life":
        return shop_extra_life_count
    if item_key == "shield":
        return shop_shield_count
    if item_key == "coin_boost":
        return shop_coin_boost_count
    if item_key == "jump_shoes":
        return shop_jump_shoes_count
    if item_key == "weapon_powerup":
        target_level = get_boss_shop_target_level()
        return 1 if target_level > 0 and weapon_powerup_ready and weapon_powerup_level == target_level else 0
    return 0


def get_shop_selection_count():
    return len(get_active_shop_items()) + 1


def move_shop_selection(key_code):
    global shop_selected_index

    back_idx = len(get_active_shop_items())
    if shop_selected_index < 0 or shop_selected_index > back_idx:
        shop_selected_index = 0

    if shop_selected_index == back_idx:
        if key_code == K_UP:
            shop_selected_index = 0
        return

    if key_code == K_LEFT:
        shop_selected_index = max(0, shop_selected_index - 1)
    elif key_code == K_RIGHT:
        shop_selected_index = min(back_idx - 1, shop_selected_index + 1)
    elif key_code == K_DOWN:
        shop_selected_index = back_idx


def activate_shop_selection():
    active_items = get_active_shop_items()
    back_idx = len(active_items)
    if shop_selected_index == back_idx:
        close_shop()
        return True
    if 0 <= shop_selected_index < len(active_items):
        return buy_shop_item(active_items[shop_selected_index]["key"])
    return False


def add_shop_item(item_key, amount=1):
    global shop_extra_life_count, shop_shield_count, shop_coin_boost_count, shop_jump_shoes_count
    delta = max(0, int(amount))
    if delta <= 0:
        return
    if item_key == "extra_life":
        shop_extra_life_count += delta
    elif item_key == "shield":
        shop_shield_count += delta
    elif item_key == "coin_boost":
        shop_coin_boost_count += delta
    elif item_key == "jump_shoes":
        shop_jump_shoes_count += delta


def buy_shop_item(item_key):
    global coin_count, weapon_powerup_ready, weapon_powerup_level, pending_weapon_powerup_level
    item = next((it for it in get_active_shop_items() if it["key"] == item_key), None)
    if item is None:
        return False
    if item_key == "weapon_powerup":
        target_level = get_boss_shop_target_level()
        if target_level <= 0:
            set_shop_notice("Boss weapon only appears in boss prep shop.")
            return False
        if weapon_powerup_ready and weapon_powerup_level == target_level:
            set_shop_notice(f"{item['label']} already ready.")
            return False
    cost = int(item["cost"])
    if coin_count < cost:
        set_shop_notice("Not enough coins in pouch.")
        return False
    coin_count -= cost
    if item_key == "weapon_powerup":
        weapon_powerup_ready = True
        weapon_powerup_level = get_boss_shop_target_level()
        pending_weapon_powerup_level = 0
    else:
        add_shop_item(item_key, 1)
    set_shop_notice(f"Purchased: {item['label']}")
    return True


def apply_player_hit(hit_sound=None):
    global game_over, player_damage_cooldown_until_ms, shop_extra_life_count
    now = millis()
    if now < player_damage_cooldown_until_ms:
        return

    if is_shield_active():
        player_damage_cooldown_until_ms = now + PLAYER_DAMAGE_COOLDOWN_MS
        play_sfx(hit_sound if hit_sound is not None else CRASH_SOUND)
        return

    if shop_extra_life_count > 0:
        shop_extra_life_count -= 1
        player_damage_cooldown_until_ms = now + PLAYER_DAMAGE_COOLDOWN_MS
        set_shop_notice("Extra life used!", duration_ms=1200)
        play_sfx(hit_sound if hit_sound is not None else CRASH_SOUND)
        return

    game_over = True
    play_sfx(hit_sound if hit_sound is not None else CRASH_SOUND)


def update_level_from_progress():
    global current_level, scroll_speed, next_level_obstacle_goal, level_blink_until_ms, pending_airplane_spawn
    global scripted_obstacle_level, scripted_obstacle_index
    new_level = get_level_for_obstacle_count(obstacles_cleared)
    if new_level > current_level:
        current_level = new_level
        scripted_obstacle_level = current_level
        scripted_obstacle_index = 0
        scroll_speed = BASE_SCROLL_SPEED * (LEVEL_SPEED_FACTOR ** (current_level - 1))
        next_level_obstacle_goal = get_level_total_obstacle_count(current_level)
        level_blink_until_ms = millis() + LEVEL_BLINK_DURATION_MS
        show_level_name_announcement(current_level)
        save_character_checkpoint(current_level)
        if current_level in (5, 6) and not flight_mode:
            pending_airplane_spawn = True
        elif current_level > 6:
            pending_airplane_spawn = False


def register_cleared_obstacle(amount=1):
    global obstacles_cleared
    obstacles_cleared += max(0, int(amount))
    update_level_from_progress()


def debug_step_level(level_delta):
    global current_level, score, scroll_speed, obstacles_cleared, next_level_obstacle_goal, level_blink_until_ms, pending_airplane_spawn
    global scripted_obstacle_level, scripted_obstacle_index
    old_level = current_level
    target_level = max(1, min(MAX_LEVEL, current_level + level_delta))
    if target_level == old_level:
        return

    # In debug mode, score and cleared-obstacle count snap to the selected level start.
    score = get_level_start_score(target_level)
    obstacles_cleared = get_level_start_obstacle_count(target_level)
    current_level = target_level
    scripted_obstacle_level = current_level
    scripted_obstacle_index = 0
    scroll_speed = BASE_SCROLL_SPEED * (LEVEL_SPEED_FACTOR ** (current_level - 1))
    next_level_obstacle_goal = get_level_total_obstacle_count(current_level)
    level_blink_until_ms = millis() + LEVEL_BLINK_DURATION_MS
    show_level_name_announcement(current_level)
    save_character_checkpoint(current_level)

    if current_level in (5, 6) and not flight_mode:
        pending_airplane_spawn = True
    else:
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


def get_rect_center(rect):
    rx, ry, rw, rh = rect
    return (rx + (rw / 2), ry + (rh / 2))


def get_linear_aim_velocity(origin_x, origin_y, target_x, target_y, speed, min_vy=None, max_vy=None):
    dx = target_x - origin_x
    if abs(dx) < 1.0:
        dx = -1.0 if speed < 0 else 1.0
    direction = -1.0 if dx < 0 else 1.0
    vx = abs(speed) * direction
    travel_time = abs(dx) / max(0.1, abs(vx))
    vy = (target_y - origin_y) / max(0.1, travel_time)
    if min_vy is not None:
        vy = max(min_vy, vy)
    if max_vy is not None:
        vy = min(max_vy, vy)
    return vx, vy


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

    if kind in ("enemy_big_tnt", "enemy_big_tnt_ground", "returned_big_tnt"):
        if kind == "enemy_big_tnt":
            glow_w = w + 28
            glow_x = x - ((glow_w - w) // 2)
            glow_y = GROUND_Y - 10
            fill(255, 214, 84)
            rect(glow_x, glow_y, glow_w, 4)
            fill(246, 164, 34)
            rect(glow_x + 10, glow_y + 4, max(12, glow_w - 20), 3)
        fill(182, 24, 24)
        rect(x, y, w, h)
        fill(120, 10, 10)
        rect(x + 2, y + 2, max(4, w - 4), max(4, h - 4))
        fill(255, 228, 110)
        fuse_x = x + w - 4 if kind != "returned_big_tnt" else x + 2
        rect(fuse_x, y - 4, 3, 5)
        return

    if kind in ("tnt_blast", "big_tnt_blast"):
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

    if kind == "bird_egg":
        fill(248, 248, 232)
        ellipse(x + (w // 2), y + (h // 2), w, h)
        fill(216, 226, 214)
        ellipse(x + (w // 2) - 4, y + (h // 2) + 2, max(4, w // 3), max(4, h // 3))
        return

    # gun / wind
    fill(*projectile["color"])
    rect(x, y, w, h)


def spawn_explosion_effect(center_x, center_y, size, life_ms=FINAL_BOSS_BLAST_LIFE_MS, alpha=225, hazardous=False):
    if not EXPLOSION_FRAMES:
        return
    frame_count = len(EXPLOSION_FRAMES)
    explosion_effects.append({
        "x": float(center_x),
        "y": float(center_y),
        "size": max(16.0, float(size)),
        "spawned_ms": millis(),
        "life_ms": max(120, int(life_ms)),
        "alpha": max(40, min(255, int(alpha))),
        "frame_offset": int(random(0, frame_count)),
        "hazardous": bool(hazardous),
        "hit_player": False,
    })
    overflow = len(explosion_effects) - MAX_ACTIVE_EXPLOSIONS
    if overflow > 0:
        del explosion_effects[0:overflow]


def spawn_final_boss_explosion_burst(boss_snapshot, count=FINAL_BOSS_DEFEAT_BURST_COUNT):
    if boss_snapshot is None:
        return
    min_x = boss_snapshot["x"] - 28
    max_x = boss_snapshot["x"] + boss_snapshot["w"] + 28
    min_y = boss_snapshot["y"] - 20
    max_y = boss_snapshot["y"] + boss_snapshot["h"] + 24
    for _ in range(max(1, int(count))):
        px = random(min_x, max_x)
        py = random(min_y, max_y)
        size_scale = random(0.72, 1.24)
        size = FINAL_BOSS_DEFEAT_EXPLOSION_SIZE * size_scale
        life_ms = FINAL_BOSS_BLAST_LIFE_MS + int(random(-110, 180))
        spawn_explosion_effect(px, py, size, life_ms=life_ms, alpha=235)


def draw_explosion_effects():
    if not explosion_effects:
        return
    surface = pg_display.get_surface()
    if surface is None or not EXPLOSION_FRAMES:
        return
    frame_count = len(EXPLOSION_FRAMES)
    now = millis()
    alive_effects = []
    for effect in explosion_effects:
        age = now - effect["spawned_ms"]
        life_ms = max(1, effect["life_ms"])
        if age >= life_ms:
            continue

        progress = max(0.0, min(0.999, age / life_ms))
        frame_step = int(progress * frame_count)
        frame_idx = (effect["frame_offset"] + frame_step) % frame_count
        frame = EXPLOSION_FRAMES[frame_idx]
        if frame is None:
            continue

        size_now = int(max(16, effect["size"] * (0.86 + (0.30 * progress))))
        sprite = transform.smoothscale(frame, (size_now, size_now)).copy()
        alpha_now = int(effect["alpha"] * (1.0 - progress))
        sprite.set_alpha(max(0, min(255, alpha_now)))
        draw_x = int(effect["x"] - (size_now / 2))
        draw_y = int(effect["y"] - (size_now / 2))
        surface.blit(sprite, (draw_x, draw_y))
        alive_effects.append(effect)

    explosion_effects[:] = alive_effects


def update_hazardous_explosions():
    if not explosion_effects or game_over:
        return

    player_hitbox = get_dino_hitbox()
    now = millis()
    for effect in explosion_effects:
        if not effect.get("hazardous") or effect.get("hit_player"):
            continue
        age = now - effect["spawned_ms"]
        life_ms = max(1, effect["life_ms"])
        if age >= life_ms:
            continue

        progress = max(0.0, min(0.999, age / life_ms))
        size_now = max(16.0, effect["size"] * (0.86 + (0.30 * progress)))
        blast_rect = (
            effect["x"] - (size_now * 0.34),
            effect["y"] - (size_now * 0.34),
            size_now * 0.68,
            size_now * 0.68,
        )
        if rects_overlap(player_hitbox, blast_rect):
            effect["hit_player"] = True
            apply_player_hit(CRASH_SOUND)
            if game_over:
                return


def update_mini_boss_defeat_sequences():
    if not mini_boss_defeat_sequences:
        return
    now = millis()
    active_sequences = []
    for sequence in mini_boss_defeat_sequences:
        snapshot = sequence.get("snapshot")
        next_blast_ms = sequence.get("next_blast_ms", 0)
        until_ms = sequence.get("until_ms", 0)

        while snapshot is not None and now >= next_blast_ms and now <= until_ms:
            burst_count = int(random(3, 7))
            spawn_final_boss_explosion_burst(snapshot, count=burst_count)
            next_blast_ms += MINI_BOSS_BLAST_INTERVAL_MS

        sequence["next_blast_ms"] = next_blast_ms
        if now <= until_ms:
            active_sequences.append(sequence)
    mini_boss_defeat_sequences[:] = active_sequences


def fire_player_weapon():
    global player_shot_cooldown_until_ms
    if boss_state is None or game_over or game_paused or shared.show_info:
        return
    if boss_state.get("form") == "ReuzenCoyote":
        return
    is_zeppelin_flight_boss = boss_state.get("type") == "zeppelin_miniboss" and flight_mode
    if is_zeppelin_flight_boss and boss_state.get("phase") != "fight":
        return
    if (not weapon_powerup_ready) and (not is_zeppelin_flight_boss):
        return
    now = millis()
    if now < player_shot_cooldown_until_ms:
        return
    projectile = acquire_projectile_slot(player_projectiles)
    if projectile is None:
        return
    profile = get_player_weapon_profile()
    if is_zeppelin_flight_boss:
        profile = {
            "w": 18,
            "h": 8,
            "speed": 8.6,
            "kind": "plane_shot",
            "color": (255, 214, 78),
            "label": "Plane slingshot",
        }
        plane_x, plane_y, plane_w, plane_h = get_flight_plane_rect()
        projectile_x = plane_x + plane_w - 8
        projectile_y = plane_y + (plane_h * 0.46) - (profile["h"] / 2)
    else:
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
        boss_hitbox = get_boss_hitbox(boss_state)
        target_x = boss_hitbox[0] + (boss_hitbox[2] * 0.5)
        target_y = boss_hitbox[1] + (boss_hitbox[3] * 0.5)
        min_vy = -3.2
        max_vy = 3.2

        if boss_state["type"] == "cactus_miniboss":
            branch_rects = get_cactus_branch_rects(boss_state)
            living_branches = [
                branch_rects[idx]
                for idx, hp in enumerate(boss_state["branch_hp"])
                if hp > 0
            ]
            if living_branches:
                projectile_center_y = projectile_y + (profile["h"] / 2)
                target_branch = min(
                    living_branches,
                    key=lambda rect: abs((rect[1] + (rect[3] * 0.5)) - projectile_center_y),
                )
                target_x = target_branch[0] + (target_branch[2] * 0.5)
                target_y = target_branch[1] + (target_branch[3] * 0.5)
            min_vy = -2.6
            max_vy = 2.6

        _, projectile["vy"] = get_linear_aim_velocity(
            projectile_x + (profile["w"] / 2),
            projectile_y + (profile["h"] / 2),
            target_x,
            target_y,
            profile["speed"],
            min_vy=min_vy,
            max_vy=max_vy,
        )
    play_sfx(FIRE_PLAYER_SOUND)
    player_shot_cooldown_until_ms = now + PLAYER_SHOOT_COOLDOWN_MS


def try_throw_back_coyote_bomb():
    if boss_state is None or boss_state.get("form") != "ReuzenCoyote":
        return False

    player_hitbox = get_dino_hitbox()
    reach_rect = (
        player_hitbox[0] - 10,
        player_hitbox[1] - 10,
        player_hitbox[2] + 42,
        player_hitbox[3] + 20,
    )
    for projectile in iter_active_projectiles(boss_state["enemy_projectiles"]):
        if projectile.get("kind") != "enemy_big_tnt_ground":
            continue
        projectile_rect = get_projectile_rect(projectile)
        if not rects_overlap(reach_rect, projectile_rect):
            continue
        boss_hitbox = get_boss_hitbox(boss_state)
        target_x = boss_hitbox[0] + (boss_hitbox[2] * 0.5)
        target_y = boss_hitbox[1] + (boss_hitbox[3] * 0.5) - 34
        throw_x = get_player_x() + DINO_W - 6
        throw_y = GROUND_Y - projectile["h"] - 10
        throw_vx, throw_vy = get_linear_aim_velocity(
            throw_x + (projectile["w"] / 2),
            throw_y + (projectile["h"] / 2),
            target_x,
            target_y,
            COYOTE_BIG_BOMB_RETURN_SPEED,
            min_vy=-10.0,
            max_vy=-2.2,
        )
        projectile.update({
            "kind": "returned_big_tnt",
            "enemy": False,
            "vx": throw_vx,
            "vy": min(COYOTE_BIG_BOMB_RETURN_VY, throw_vy - 1.0),
            "x": throw_x,
            "y": throw_y,
        })
        play_sfx(FIRE_PLAYER_SOUND)
        return True
    return False


def get_boss_hitbox(boss):
    def hitbox_from_sprite(surface, draw_x, draw_y, draw_w, draw_h, pad_x=0, pad_y=0):
        if surface is None:
            return (draw_x, draw_y, draw_w, draw_h)
        bounds = surface.get_bounding_rect(min_alpha=8)
        if bounds.width <= 0 or bounds.height <= 0:
            return (draw_x, draw_y, draw_w, draw_h)

        sx = draw_x + (draw_w * (bounds.x / max(1.0, float(surface.get_width()))))
        sy = draw_y + (draw_h * (bounds.y / max(1.0, float(surface.get_height()))))
        sw = draw_w * (bounds.width / max(1.0, float(surface.get_width())))
        sh = draw_h * (bounds.height / max(1.0, float(surface.get_height())))
        return (
            sx + pad_x,
            sy + pad_y,
            max(8.0, sw - (pad_x * 2)),
            max(8.0, sh - (pad_y * 2)),
        )

    if boss["type"] == "bird_miniboss":
        return hitbox_from_sprite(BIRD_RIGHT_IMG, boss["x"], boss["y"], boss["w"], boss["h"], pad_x=14, pad_y=10)

    if boss["type"] == "cactus_miniboss":
        return (boss["x"] + 16, boss["y"] + 16, boss["w"] - 34, boss["h"] - 26)

    if boss["type"] == "zeppelin_miniboss":
        return (boss["x"] + 24, boss["y"] + 20, boss["w"] - 64, boss["h"] - 42)

    if boss.get("form") == "ReuzenDino":
        draw_y = boss["y"]
        draw_h = boss["h"]
        if boss.get("is_crouching", False) and not boss.get("jumping", False):
            draw_h = int(boss["h"] * 0.72)
            draw_y = boss["y"] + (boss["h"] - draw_h)
        return hitbox_from_sprite(GIANT_DINO_RIGHT_IMG, boss["x"], draw_y, boss["w"], draw_h, pad_x=12, pad_y=11)

    if boss.get("form") == "ReuzenCowboy":
        if boss.get("is_crouching", False):
            crouch_h = int(boss["h"] * 0.62)
            crouch_y = boss["y"] + (boss["h"] - crouch_h)
            return hitbox_from_sprite(
                GIANT_COWBOY_DUCK_RIGHT_IMG,
                boss["x"],
                crouch_y,
                boss["w"],
                crouch_h,
                pad_x=11,
                pad_y=9,
            )
        return hitbox_from_sprite(GIANT_COWBOY_RIGHT_IMG, boss["x"], boss["y"], boss["w"], boss["h"], pad_x=12, pad_y=11)

    # ReuzenCoyote (shape-based render): keep manual tuned hitbox.
    draw_y = boss["y"]
    draw_h = boss["h"]
    if boss.get("is_crouching", False) and not boss.get("jumping", False):
        draw_h = int(boss["h"] * 0.74)
        draw_y = boss["y"] + (boss["h"] - draw_h)
    return (boss["x"] + 26, draw_y + 48, boss["w"] - 72, draw_h - 112)


def get_cactus_branch_rects(boss):
    branch_rects = []
    base_y = boss["y"] + 22
    for idx in range(5):
        branch_y = base_y + idx * 38
        branch_side = get_cactus_arm_side(idx)
        branch_x = boss["x"] - 62 if branch_side == "left" else boss["x"] + boss["w"] - 2
        branch_rects.append((branch_x, branch_y, 54, 18))
    return branch_rects


def cactus_boss_showing_right_side(boss):
    interval_ms = max(1000, int(boss.get("rotation_interval_ms", CACTUS_ROTATION_INTERVAL_MS)))
    started_ms = int(boss.get("rotation_started_ms", 0))
    phase = ((millis() - started_ms) // interval_ms) % 2
    return bool(phase)


def get_cactus_visible_side(boss):
    return "right" if cactus_boss_showing_right_side(boss) else "left"


def get_cactus_arm_side(idx):
    return CACTUS_ARM_SIDE_BY_INDEX[idx]


def get_cactus_visible_arm_indices(boss):
    visible_side = get_cactus_visible_side(boss)
    return [idx for idx, hp in enumerate(boss["branch_hp"]) if hp > 0 and get_cactus_arm_side(idx) == visible_side]


def get_cactus_boss_platform_rects():
    return (
        (96, GROUND_Y - 66, 132, 16),
        (318, GROUND_Y - 114, 146, 16),
        (560, GROUND_Y - 74, 132, 16),
    )


def cactus_all_arms_destroyed(boss):
    return all(hp <= 0 for hp in boss["branch_hp"])


def get_cactus_arm_segment_cache(surface):
    if surface is None:
        return []
    cache = getattr(get_cactus_arm_segment_cache, "cache", None)
    if cache is None:
        cache = {}
        setattr(get_cactus_arm_segment_cache, "cache", cache)
    cache_key = id(surface)
    if cache_key in cache:
        return cache[cache_key]

    segments = []
    surface_w = max(1, surface.get_width())
    surface_h = max(1, surface.get_height())
    band_h = surface_h / 5.0
    for idx in range(5):
        band_top = int(round(idx * band_h))
        band_bottom = surface_h if idx == 4 else int(round((idx + 1) * band_h))
        band_rect = (0, band_top, surface_w, max(1, band_bottom - band_top))
        band_surface = surface.subsurface(band_rect).copy()
        bounds = band_surface.get_bounding_rect(min_alpha=8)
        if bounds.width <= 0 or bounds.height <= 0:
            segments.append(None)
            continue
        segment_surface = band_surface.subsurface(bounds).copy()
        segments.append({
            "surface": segment_surface,
            "offset_x": bounds.x / float(surface_w),
            "offset_y": (band_top + bounds.y) / float(surface_h),
            "width_ratio": bounds.width / float(surface_w),
            "height_ratio": bounds.height / float(surface_h),
        })
    cache[cache_key] = segments
    return segments


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
            "name": "Mini Boss L4: Giant Bird",
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
            "hits_required": BIRD_MINIBOSS_HITS_REQUIRED,
            "meter_steps": 20,
            "enemy_projectiles": create_projectile_pool(),
            "attack_interval_ms": 1120,
            "last_attack_ms": now,
        }

    if level == 6:
        return {
            "type": "zeppelin_miniboss",
            "level": 6,
            "name": "Mini Boss L6: Zeppelin",
            "x": -260.0,
            "y": 120.0,
            "w": 220,
            "h": 108,
            "vx": 0.0,
            "vy": 0.0,
            "min_x": 56.0,
            "max_x": float(width - 256),
            "min_y": 68.0,
            "max_y": 164.0,
            "phase": "approach",
            "phase_started_ms": now,
            "approach_duration_ms": ZEPPELIN_CITY_APPROACH_DURATION_MS,
            "approach_from_x": -260.0,
            "approach_to_x": float(width - 268),
            "approach_from_y": 132.0,
            "approach_to_y": 92.0,
            "fight_vx": -1.9,
            "fight_vy": 0.9,
            "hits_taken": 0,
            "hits_required": ZEPPELIN_MINIBOSS_HITS_REQUIRED,
            "meter_steps": ZEPPELIN_MINIBOSS_HITS_REQUIRED,
            "enemy_projectiles": create_projectile_pool(),
            "attack_interval_ms": 980,
            "last_attack_ms": now,
        }

    if level == 7:
        return {
            "type": "cactus_miniboss",
            "level": 7,
            "name": "Mini Boss L7: Giant Cactus",
            "x": float(width - 190),
            "y": 176.0,
            "w": 124,
            "h": 242,
            "ground_y": 176.0,
            "vy": 1.2,
            "min_y": 150.0,
            "max_y": 210.0,
            "branch_hp": [3, 3, 3, 3, 3],
            "trunk_hp": CACTUS_MINIBOSS_TRUNK_HITS_REQUIRED,
            "hits_taken": 0,
            "hits_required": CACTUS_MINIBOSS_HITS_REQUIRED + CACTUS_MINIBOSS_TRUNK_HITS_REQUIRED,
            "meter_steps": CACTUS_MINIBOSS_HITS_REQUIRED + CACTUS_MINIBOSS_TRUNK_HITS_REQUIRED,
            "enemy_projectiles": create_projectile_pool(),
            "attack_interval_ms": 860,
            "last_attack_ms": now,
            "rotation_interval_ms": CACTUS_ROTATION_INTERVAL_MS,
            "rotation_started_ms": now,
        }

    profile = get_player_weapon_profile()
    form_name = "ReuzenDino"
    form_display_name = "Giant Dino"
    if active_character_key == "cowboy":
        form_name = "ReuzenCowboy"
        form_display_name = "Giant Cowboy"
    elif active_character_key == "roadrunner":
        form_name = "ReuzenCoyote"
        form_display_name = "Giant Coyote"
    spawn_y = 162.0
    min_y = 120.0
    max_y = 220.0
    if form_name == "ReuzenCowboy":
        # Keep giant cowboy closer to the ground so straight shots can hit ground-level player.
        spawn_y = 214.0
        min_y = 188.0
        max_y = 252.0

    return {
        "type": "final_boss",
        "level": 10,
        "name": f"Final Boss L10: {form_display_name}",
        "form": form_name,
        "x": float(width - 220),
        "y": spawn_y,
        "w": 190,
        "h": 230,
        "vy": 1.35,
        "min_y": min_y,
        "max_y": max_y,
        "hits_taken": 0,
        "hits_required": COYOTE_HITS_REQUIRED if form_name == "ReuzenCoyote" else FINAL_BOSS_DEFAULT_HITS_REQUIRED,
        "meter_steps": COYOTE_HITS_REQUIRED if form_name == "ReuzenCoyote" else FINAL_BOSS_DEFAULT_HITS_REQUIRED,
        "enemy_projectiles": create_projectile_pool(),
        "attack_interval_ms": 760,
        "phase": "laugh",
        "pit_traps": [],
        "vx": 1.5 if form_name == "ReuzenCoyote" else 0.0,
        "min_x": float(width - 320),
        "max_x": float(width - 68),
        "last_attack_ms": now,
        "enemy_weapon_kind": profile["kind"],
        "is_crouching": False,
        "crouch_until_ms": 0,
        "ground_y": spawn_y,
        "jumping": False,
        "jump_vy": 0.0,
        "next_jump_ms": now + int(random(FINAL_BOSS_JUMP_GAP_MIN_MS, FINAL_BOSS_JUMP_GAP_MAX_MS)),
        "next_duck_ms": now + int(random(FINAL_BOSS_DUCK_GAP_MIN_MS, FINAL_BOSS_DUCK_GAP_MAX_MS)),
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


def draw_branch_platform(branch_rect):
    branch_x, branch_y, branch_w, branch_h = branch_rect
    fill(104, 64, 34)
    rect(branch_x, branch_y, branch_w, branch_h)
    fill(150, 94, 48)
    rect(branch_x + 4, branch_y + 2, max(12, branch_w - 12), max(4, branch_h - 6))
    fill(78, 142, 66)
    ellipse(branch_x + 24, branch_y - 8, 52, 24)
    ellipse(branch_x + branch_w - 26, branch_y - 10, 58, 26)


def draw_bird_boss_arena(theme):
    background(118, 184, 132)
    draw_parallax_clouds(theme)
    fill(86, 154, 96)
    ellipse(90, 120, 220, 98)
    ellipse(244, 82, 270, 116)
    ellipse(530, 102, 260, 108)
    ellipse(708, 142, 210, 98)
    fill(62, 128, 76)
    ellipse(180, 198, 210, 86)
    ellipse(438, 174, 250, 92)
    ellipse(646, 216, 230, 90)

    fill(92, 58, 34)
    rect(704, 98, 42, GROUND_Y - 98)
    fill(132, 84, 44)
    rect(716, 104, 12, GROUND_Y - 110)
    fill(82, 52, 30)
    rect(28, 160, 32, GROUND_Y - 160)

    for branch_rect in BIRD_BOSS_BRANCH_RECTS:
        draw_branch_platform(branch_rect)

    nest_x = 522
    nest_y = 94
    nest_w = 198
    nest_h = 82
    fill(118, 76, 42)
    ellipse(nest_x + (nest_w // 2), nest_y + 52, nest_w, nest_h)
    fill(86, 54, 30)
    ellipse(nest_x + (nest_w // 2), nest_y + 44, nest_w - 34, nest_h - 24)
    fill(248, 248, 232)
    ellipse(nest_x + 74, nest_y + 42, 28, 38)
    ellipse(nest_x + 104, nest_y + 36, 30, 42)
    ellipse(nest_x + 132, nest_y + 44, 26, 36)
    fill(108, 70, 40)
    rect(nest_x + 22, nest_y + 62, nest_w - 44, 12)

    fill(102, 76, 48)
    rect(0, GROUND_Y, width, 40)
    stroke(84, 58, 34)
    stroke_weight(2)
    line(0, GROUND_Y, width, GROUND_Y)
    no_stroke()


def draw_cactus_boss_arena(theme):
    cave_light_phase = millis() / 230.0
    background(106, 106, 114)
    fill(82, 82, 90)
    rect(0, 0, width, 36)
    rect(0, 88, width, 46)
    fill(70, 70, 78)
    rect(0, GROUND_Y, width, 40)
    fill(94, 94, 102)
    rect(34, 112, 38, 250)
    rect(width - 84, 100, 44, 272)
    fill(134, 134, 142)
    triangle(28, 0, 54, 48, 78, 0)
    triangle(144, 0, 170, 54, 198, 0)
    triangle(292, 0, 314, 40, 340, 0)
    triangle(490, 0, 518, 58, 546, 0)
    triangle(646, 0, 672, 42, 700, 0)
    fill(126, 126, 134)
    ellipse(124, GROUND_Y - 8, 208, 62)
    ellipse(392, GROUND_Y - 12, 320, 78)
    ellipse(676, GROUND_Y - 6, 236, 64)
    fill(88, 88, 96)
    ellipse(118, 184, 102, 54)
    ellipse(236, 146, 126, 60)
    ellipse(574, 164, 136, 70)
    ellipse(706, 206, 94, 52)

    cave_lights = (
        (122, 92, 0.0, 1.0),
        (278, 132, 1.7, 0.7),
        (524, 104, 3.1, 0.9),
        (676, 156, 4.4, 0.65),
    )
    for light_x, light_y, phase_offset, wobble in cave_lights:
        flicker = 0.5 + (0.5 * math.sin(cave_light_phase + phase_offset))
        jitter = math.sin((cave_light_phase * 2.2) + (phase_offset * 1.9)) * wobble
        glow = 26 + int(flicker * 38)
        core = 178 + int(flicker * 54)

        fill(94 + glow, 86 + glow, 58 + (glow // 2))
        ellipse(light_x + jitter, light_y + 8, 54 + glow, 34 + (glow // 2))
        fill(66, 66, 74)
        rect(light_x - 3, light_y - 22, 6, 18)
        fill(core, 150 + int(flicker * 36), 88 + int(flicker * 24))
        ellipse(light_x + jitter, light_y, 16, 16)
        fill(232, 208, 128)
        ellipse(light_x + jitter, light_y, 7 + int(flicker * 3), 7 + int(flicker * 3))

    platform_rects = get_cactus_boss_platform_rects()
    for platform_x, platform_y, platform_w, platform_h in platform_rects:
        fill(118, 114, 120)
        rect(platform_x - 10, platform_y + 4, platform_w + 20, platform_h + 12)
        fill(156, 152, 158)
        rect(platform_x, platform_y, platform_w, platform_h)
        fill(178, 174, 180)
        rect(platform_x + 10, platform_y + 2, platform_w - 20, 5)
        fill(92, 92, 100)
        rect(platform_x + 8, platform_y + platform_h, platform_w - 16, 5)

        fill(132, 128, 136)
        ellipse(platform_x + 18, platform_y + 4, 18, 10)
        ellipse(platform_x + platform_w - 22, platform_y + 5, 20, 10)

    stroke(154, 154, 162)
    stroke_weight(2)
    line(0, GROUND_Y, width, GROUND_Y)
    no_stroke()


def draw_parallax_clouds(theme):
    now = millis()
    layer_specs = (
        {
            "speed": 0.018,
            "color": (244, 248, 252),
            "clouds": ((90, 76, 76), (302, 124, 68), (564, 92, 84)),
        },
        {
            "speed": 0.034,
            "color": (232, 240, 246),
            "clouds": ((164, 104, 58), (448, 136, 72), (738, 88, 62)),
        },
        {
            "speed": 0.072,
            "color": (222, 232, 240),
            "clouds": ((118, 154, 42), (356, 172, 48), (640, 148, 44), (812, 166, 40)),
        },
    )

    for spec in layer_specs:
        fill(*spec["color"])
        speed = spec["speed"]
        for base_x, base_y, cloud_w in spec["clouds"]:
            travel = (now * speed) % (width + cloud_w + 120)
            cloud_x = base_x - travel
            while cloud_x < -cloud_w - 80:
                cloud_x += width + cloud_w + 140
            ellipse(cloud_x, base_y, cloud_w, 30)
            ellipse(cloud_x + 24, base_y - 10, cloud_w - 18, 26)
            ellipse(cloud_x - 22, base_y - 2, cloud_w - 26, 24)


def draw_zeppelin_city_backdrop(theme, arena_mode=False, reveal_ratio=1.0):
    reveal_ratio = max(0.0, min(1.0, reveal_ratio))
    city_shift_x = (1.0 - reveal_ratio) * (width * 0.72)
    sky_top = (126, 184, 222) if arena_mode else (144, 198, 232)
    sky_mid = (176, 212, 236) if arena_mode else (192, 224, 242)
    sky_low = (222, 232, 214) if arena_mode else (230, 238, 220)
    background(*sky_top)
    fill(*sky_mid)
    rect(0, 112, width, 132)
    fill(*sky_low)
    rect(0, 244, width, GROUND_Y - 244)
    draw_parallax_clouds(theme)

    if reveal_ratio < 1.0:
        haze_w = int((1.0 - reveal_ratio) * (width * 0.36))
        if haze_w > 0:
            fill(232, 238, 226)
            rect(0, 0, haze_w, GROUND_Y)

    def sx(value):
        return value + city_shift_x

    fill(94, 102, 122)
    rect(sx(22), 212, 68, GROUND_Y - 212)
    rect(sx(106), 188, 84, GROUND_Y - 188)
    rect(sx(206), 226, 54, GROUND_Y - 226)
    rect(sx(282), 170, 112, GROUND_Y - 170)
    rect(sx(418), 202, 74, GROUND_Y - 202)
    rect(sx(514), 156, 96, GROUND_Y - 156)
    rect(sx(632), 214, 62, GROUND_Y - 214)
    rect(sx(710), 184, 82, GROUND_Y - 184)

    fill(72, 78, 98)
    rect(sx(128), 152, 18, 36)
    rect(sx(320), 122, 22, 48)
    rect(sx(548), 118, 22, 38)
    rect(sx(756), 148, 16, 36)

    fill(244, 220, 126)
    for window_x, window_y in (
        (36, 238), (56, 238), (116, 214), (138, 214), (160, 214),
        (302, 196), (324, 196), (346, 196), (368, 196),
        (432, 222), (454, 222), (528, 182), (550, 182), (572, 182),
        (720, 206), (742, 206), (764, 206),
    ):
        rect(sx(window_x), window_y, 8, 12)

    fill(116, 84, 58)
    rect(0, GROUND_Y, width, 40)
    fill(92, 68, 44)
    rect(0, GROUND_Y - 12, width, 12)

    tower_x = sx(width - 178)
    fill(78, 72, 84)
    rect(tower_x, 126, 24, GROUND_Y - 126)
    rect(tower_x - 18, 172, 60, 18)
    rect(tower_x - 10, 224, 44, 14)
    fill(164, 62, 54)
    rect(tower_x + 4, 108, 16, 18)

    if arena_mode:
        search_phase = millis() / 520.0
        for beam_x, phase_offset in ((104, 0.0), (376, 1.8), (622, 3.5)):
            beam_top_x = sx(beam_x) + math.sin(search_phase + phase_offset) * 40.0
            fill(238, 232, 188)
            triangle(sx(beam_x) - 8, GROUND_Y, sx(beam_x) + 8, GROUND_Y, beam_top_x, 86)


def draw_zeppelin_boss_arena(theme):
    draw_zeppelin_city_backdrop(theme, arena_mode=True)
    stroke(86, 74, 60)
    stroke_weight(2)
    line(0, GROUND_Y, width, GROUND_Y)
    no_stroke()


def draw_cactus_back_stems(boss, visible_right_side):
    rear_direction = -1 if visible_right_side else 1
    base_x = boss["x"] + (boss["w"] * 0.5)
    base_y = boss["y"] + 34
    for idx in range(3):
        stem_len = 48 + idx * 14
        stem_h = 16 + idx * 2
        stem_y = base_y + idx * 54
        body_x = base_x if rear_direction > 0 else base_x - stem_len
        fill(94, 144, 88)
        rect(body_x, stem_y, stem_len, stem_h)
        ellipse(body_x + (stem_len if rear_direction > 0 else 0), stem_y + (stem_h / 2), stem_h + 10, stem_h + 6)
        fill(132, 184, 122)
        inner_w = max(12, stem_len - 12)
        inner_x = body_x + 4 if rear_direction > 0 else body_x + stem_len - inner_w - 4
        rect(inner_x, stem_y + 3, inner_w, max(6, stem_h - 6))


def draw_cactus_branch_segment(boss, branch_rect, branch_hp):
    idx = boss.get("active_branch_index", 0)
    _, by, bw, bh = branch_rect
    grow_right = get_cactus_arm_side(idx) == "right"
    hp_ratio = max(0.2, min(1.0, branch_hp / 3.0))
    arm_w = int(max(16, bw * hp_ratio))
    arm_h = int(max(10, bh - 2))
    trunk_anchor_x = boss["x"] + boss["w"] - 8 if grow_right else boss["x"] + 8
    arm_x = trunk_anchor_x if grow_right else trunk_anchor_x - arm_w
    arm_y = int(by + 1)

    fill(84, 144, 74)
    rect(arm_x, arm_y, arm_w, arm_h)
    fill(132, 184, 118)
    inner_w = max(6, arm_w - 10)
    inner_x = arm_x + 4 if grow_right else arm_x + arm_w - inner_w - 4
    rect(inner_x, arm_y + 3, inner_w, max(4, arm_h - 6))
    tip_x = arm_x + arm_w if grow_right else arm_x
    ellipse(tip_x, arm_y + (arm_h / 2), arm_h + 12, arm_h + 8)
    fill(98, 152, 86)
    ellipse(trunk_anchor_x, arm_y + (arm_h / 2), arm_h + 8, arm_h + 6)
    draw_cactus_spines(arm_x + 2, arm_y + 1, max(6, arm_w - 4), arm_h - 2, step_x=12, step_y=8)


def draw_cactus_arm_sprite_segment(boss, idx, hp_ratio, pose_surface, draw_x, draw_y, draw_w, draw_h):
    segments = get_cactus_arm_segment_cache(pose_surface)
    if idx >= len(segments) or segments[idx] is None:
        return False

    segment = segments[idx]
    segment_surface = segment["surface"]
    segment_w = max(6, int(segment_surface.get_width() * hp_ratio))
    if segment_w <= 0:
        return False

    grow_right = get_cactus_arm_side(idx) == "right"
    source_x = 0 if grow_right else max(0, segment_surface.get_width() - segment_w)
    cropped_surface = segment_surface.subsurface((source_x, 0, segment_w, segment_surface.get_height())).copy()

    dest_w = max(8, int(draw_w * segment["width_ratio"] * hp_ratio))
    dest_h = max(8, int(draw_h * segment["height_ratio"]))
    anchor_x = draw_x + int(draw_w * segment["offset_x"])
    dest_x = anchor_x if grow_right else anchor_x + int(draw_w * segment["width_ratio"]) - dest_w
    dest_y = draw_y + int(draw_h * segment["offset_y"])
    image(cropped_surface, dest_x, dest_y, dest_w, dest_h)
    return True


def apply_bird_boss_branch_collisions(prev_player_x, prev_dino_y, prev_ducking):
    global on_ground
    landed = False
    for platform_rect in BIRD_BOSS_BRANCH_RECTS:
        if apply_one_way_platform_collision(
            platform_rect,
            prev_player_x,
            prev_dino_y,
            prev_ducking,
            drop_if_unsupported=False,
        ):
            landed = True
            break
    if (not landed) and on_ground and dino_y < DINO_Y:
        if not any(platform_supports_player(platform_rect) for platform_rect in BIRD_BOSS_BRANCH_RECTS):
            on_ground = False


def maybe_start_boss_encounter():
    global pending_weapon_powerup_level, pre_boss_scene_level
    global boss_left_pressed, boss_right_pressed, player_x
    global dino_y, velocity_y, on_ground, is_ducking, is_fast_falling
    if boss_state is not None or pre_boss_scene_level > 0 or game_over or game_completed or not game_started or game_paused or flight_mode or shop_active:
        return

    # Skip older boss tiers once the player is already in a higher tier.
    # This keeps boss order aligned with the current level (e.g. level 7 starts with cactus).
    for level in BOSS_LEVEL_ORDER:
        if current_level > level:
            boss_completed[level] = True

    for level in BOSS_LEVEL_ORDER:
        if current_level >= level and not boss_completed[level]:
            requires_weapon = level != 10
            has_weapon_for_level = (not requires_weapon) or (weapon_powerup_ready and weapon_powerup_level == level)
            if requires_weapon and not has_weapon_for_level:
                pending_weapon_powerup_level = level
                return
            pending_weapon_powerup_level = 0
            if not boss_shop_seen.get(level, False):
                boss_shop_seen[level] = True
                pre_boss_scene_level = level
                player_x = 48.0
                boss_left_pressed = False
                boss_right_pressed = False
                dino_y = DINO_Y
                velocity_y = 0
                on_ground = True
                is_ducking = False
                is_fast_falling = False
                set_shop_notice(f"Badger shop before boss L{level}. Walk right and press DOWN.", duration_ms=PRE_BOSS_SCENE_NOTICE_MS)
                return
            start_pending_boss_encounter(level)
            break


def draw_boss_entity(boss):
    x = int(boss["x"])
    y = int(boss["y"])
    w = int(boss["w"])
    h = int(boss["h"])
    crouching = boss.get("is_crouching", False) and not boss.get("jumping", False)

    if boss["type"] == "bird_miniboss":
        image(BIRD_RIGHT_IMG, x, y, w, h)
        return

    if boss["type"] == "cactus_miniboss":
        trunk_x = x + 22
        trunk_y = y + 16
        trunk_w = w - 30
        trunk_h = h - 18
        show_right_side = cactus_boss_showing_right_side(boss)
        visible_side = get_cactus_visible_side(boss)
        pose_arms_img = CACTUS_BOSS_ARMS_IMG if show_right_side else CACTUS_BOSS_ARMS_FLIPPED_IMG
        pose_shift_x = 12 if show_right_side else -12
        pose_shift_y = -2 if show_right_side else 2
        sprite_draw_x = trunk_x - 26 + pose_shift_x
        sprite_draw_y = trunk_y - 10 + pose_shift_y
        sprite_draw_w = trunk_w + 22 if show_right_side else trunk_w + 32
        sprite_draw_h = trunk_h + 12

        fill(52, 52, 58)
        ellipse(x + (w // 2) + (8 if show_right_side else -8), y + h - 6, w - 24, 24)

        if CACTUS_BOSS_TRUNK_IMG is not None:
            trunk_img = CACTUS_BOSS_TRUNK_IMG if show_right_side else CACTUS_BOSS_TRUNK_FLIPPED_IMG
            image(trunk_img, sprite_draw_x, sprite_draw_y, sprite_draw_w, sprite_draw_h)
        else:
            fill(38, 126, 48)
            rect(trunk_x - 6 + pose_shift_x, trunk_y + 8 + pose_shift_y, trunk_w + 8, trunk_h - 10)
            arc(trunk_x + (trunk_w // 2) - 1 + pose_shift_x, trunk_y + 8 + pose_shift_y, trunk_w + 8, 28, PI, TWO_PI)

            fill(58, 168, 70)
            rect(trunk_x + 2 + pose_shift_x, trunk_y + 14 + pose_shift_y, trunk_w - 8, trunk_h - 22)
            arc(trunk_x + (trunk_w // 2) - 2 + pose_shift_x, trunk_y + 14 + pose_shift_y, trunk_w - 8, 22, PI, TWO_PI)
            fill(71, 186, 84)
            rect(trunk_x + 12 + pose_shift_x, trunk_y + 28 + pose_shift_y, trunk_w - 32, trunk_h - 52)
            arc(trunk_x + (trunk_w // 2) - 4 + pose_shift_x, trunk_y + 28 + pose_shift_y, trunk_w - 32, 18, PI, TWO_PI)

            stroke(48, 145, 58)
            stroke_weight(2)
            line(trunk_x + 18 + pose_shift_x, trunk_y + 18 + pose_shift_y, trunk_x + 18 + pose_shift_x, trunk_y + trunk_h - 16 + pose_shift_y)
            line(trunk_x + trunk_w // 2 + pose_shift_x, trunk_y + 16 + pose_shift_y, trunk_x + trunk_w // 2 + pose_shift_x, trunk_y + trunk_h - 14 + pose_shift_y)
            line(trunk_x + trunk_w - 22 + pose_shift_x, trunk_y + 18 + pose_shift_y, trunk_x + trunk_w - 22 + pose_shift_x, trunk_y + trunk_h - 16 + pose_shift_y)
            no_stroke()
            draw_cactus_spines(trunk_x + 4 + pose_shift_x, trunk_y + 18 + pose_shift_y, trunk_w - 12, trunk_h - 24, step_x=16, step_y=20)

        branch_rects = get_cactus_branch_rects(boss)
        for idx, branch_hp in enumerate(boss["branch_hp"]):
            _, by, _, bh = branch_rects[idx]
            if get_cactus_arm_side(idx) != visible_side:
                continue
            if branch_hp <= 0:
                stump_x = boss["x"] + boss["w"] - 10 if show_right_side else boss["x"] + 2
                fill(84, 136, 72)
                rect(int(stump_x), int(by + 3), 10, int(max(8, bh - 5)))
                ellipse(int(stump_x + (8 if show_right_side else 0)), int(by + (bh / 2)), 12, 10)
                continue
            hp_ratio = max(0.2, min(1.0, branch_hp / 3.0))
            used_sprite_segment = False
            if pose_arms_img is not None:
                used_sprite_segment = draw_cactus_arm_sprite_segment(
                    boss,
                    idx,
                    hp_ratio,
                    pose_arms_img,
                    sprite_draw_x,
                    sprite_draw_y,
                    sprite_draw_w,
                    sprite_draw_h,
                )
            if not used_sprite_segment:
                continue
        return

    if boss["type"] == "zeppelin_miniboss":
        if ZEPPELIN_IMG is not None:
            image(ZEPPELIN_IMG, x - 8, y + 2, w + 32, h + 14)
        else:
            # Reference attribution for the zeppelin look used here:
            # FreeSVG.org "Zeppelin" by j4p4n (Public Domain / CC0) https://freesvg.org/zeppelin
            hull_x = x + 10
            hull_y = y + 14
            hull_w = w - 26
            hull_h = h - 38
            fill(198, 64, 54)
            ellipse(hull_x + (hull_w * 0.5), hull_y + (hull_h * 0.44), hull_w, hull_h * 0.7)
            fill(240, 226, 194)
            ellipse(hull_x + (hull_w * 0.56), hull_y + (hull_h * 0.42), hull_w * 0.52, hull_h * 0.42)
            fill(130, 36, 28)
            rect(x + 30, y + h - 42, w - 92, 10)
            fill(84, 64, 42)
            rect(x + 54, y + h - 30, w - 144, 18)
            fill(62, 62, 70)
            rect(x + 92, y + h - 16, 16, 8)
            rect(x + w - 118, y + h - 16, 16, 8)
            fill(250, 214, 82)
            rect(x + 82, y + h - 24, 8, 6)
            rect(x + 104, y + h - 24, 8, 6)
            rect(x + 126, y + h - 24, 8, 6)
            fill(142, 42, 34)
            triangle(x + w - 34, y + 38, x + w + 8, y + 52, x + w - 34, y + 66)
            fill(220, 184, 94)
            rect(x + w - 18, y + 46, 18, 10)
        return

    # Final boss
    if boss["form"] == "ReuzenDino":
        if crouching:
            crouch_h = int(h * 0.72)
            crouch_y = y + (h - crouch_h)
            image(GIANT_DINO_RIGHT_IMG, x, crouch_y, w, crouch_h)
        else:
            image(GIANT_DINO_RIGHT_IMG, x, y, w, h)
        return
    if boss["form"] == "ReuzenCowboy":
        if crouching:
            crouch_h = int(h * 0.62)
            crouch_y = y + (h - crouch_h)
            image(GIANT_COWBOY_DUCK_RIGHT_IMG, x, crouch_y, w, crouch_h)
        else:
            image(GIANT_COWBOY_RIGHT_IMG, x, y, w, h)
        return

    # ReuzenCoyote without dedicated sprite: stylized silhouette with mood phases.
    if crouching:
        crouch_h = int(h * 0.74)
        y = y + (h - crouch_h)
        h = crouch_h
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
    global boss_state, score, weapon_powerup_ready, weapon_powerup_level, game_completed
    global boss_left_pressed, boss_right_pressed
    global final_boss_snapshot, final_boss_defeat_until_ms, final_boss_next_blast_ms
    global pending_credits_after_victory
    if boss["hits_taken"] < boss["hits_required"]:
        return
    if boss["type"] in ("bird_miniboss", "cactus_miniboss"):
        play_sfx(MINI_BOSS_VICTORY_SOUND)
    boss_completed[boss["level"]] = True
    boss_state = None
    weapon_powerup_ready = False
    weapon_powerup_level = 0
    boss_left_pressed = False
    boss_right_pressed = False
    reset_projectile_pool(player_projectiles)
    boss_snapshot = dict(boss)
    boss_snapshot["enemy_projectiles"] = []
    boss_snapshot["pit_traps"] = []
    now = millis()
    burst_count = MINI_BOSS_DEFEAT_BURST_COUNT if boss["level"] < 10 else (FINAL_BOSS_DEFEAT_BURST_COUNT + 3)
    spawn_final_boss_explosion_burst(boss_snapshot, count=burst_count)
    play_sfx(BOSS_EXPLOSION_SOUND)
    score += BOSS_REWARD_POINTS.get(boss["level"], 0)
    if boss["level"] < 10:
        mini_boss_defeat_sequences.append({
            "snapshot": boss_snapshot,
            "until_ms": now + MINI_BOSS_DEFEAT_DURATION_MS,
            "next_blast_ms": now + MINI_BOSS_BLAST_INTERVAL_MS,
        })
        start_post_boss_transition(boss_snapshot)
    if boss["level"] == 6:
        return
    if boss["level"] >= 10:
        final_boss_snapshot = boss_snapshot
        final_boss_defeat_until_ms = now + FINAL_BOSS_DEFEAT_DURATION_MS
        final_boss_next_blast_ms = now
        character_completed[active_character_key] = True
        game_completed = True
        pending_credits_after_victory = True
        return
    if boss["level"] >= 10:
        return


def update_enemy_projectiles(boss):
    global coyote_cave_flash_until_ms
    if flight_mode and boss.get("type") == "zeppelin_miniboss":
        player_hitbox = get_flight_plane_rect()
    else:
        player_hitbox = get_dino_hitbox()
    for projectile in iter_active_projectiles(boss["enemy_projectiles"]):
        if projectile["kind"] == "returned_big_tnt":
            projectile["x"] += projectile["vx"]
            projectile["y"] += projectile.get("vy", 0.0)
            projectile["vy"] = min(3.4, projectile.get("vy", 0.0) + COYOTE_BIG_BOMB_RETURN_GRAVITY)
            projectile_rect = get_projectile_rect(projectile)
            boss_hitbox = get_boss_hitbox(boss)
            bomb_hitbox = (
                projectile_rect[0] - 6,
                projectile_rect[1] - 6,
                projectile_rect[2] + 12,
                projectile_rect[3] + 12,
            )
            if rects_overlap(bomb_hitbox, boss_hitbox):
                boss["hits_taken"] += COYOTE_BIG_BOMB_BOSS_DAMAGE
                projectile["active"] = False
                coyote_cave_flash_until_ms = millis() + COYOTE_CAVE_FLASH_MS
                spawn_explosion_effect(
                    projectile_rect[0] + (projectile_rect[2] / 2),
                    projectile_rect[1] + (projectile_rect[3] / 2),
                    84,
                    life_ms=380,
                    alpha=235,
                )
                play_sfx(BOSS_EXPLOSION_SOUND)
                continue
            if projectile["x"] > width + 40 or projectile["y"] > height + 40:
                projectile["active"] = False
            continue

        if projectile["kind"] == "enemy_tnt":
            projectile["x"] += projectile["vx"]
            projectile["y"] += projectile.get("vy", 0.0)
            projectile["vy"] = projectile.get("vy", 0.0) + COYOTE_TNT_THROW_GRAVITY
            projectile_rect = get_projectile_rect(projectile)
            if rects_overlap(projectile_rect, player_hitbox):
                projectile["active"] = False
                apply_player_hit(CRASH_SOUND)
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

        if projectile["kind"] == "enemy_big_tnt":
            projectile["x"] += projectile["vx"]
            projectile["y"] += projectile.get("vy", 0.0)
            projectile["vy"] = projectile.get("vy", 0.0) + COYOTE_TNT_THROW_GRAVITY
            projectile_rect = get_projectile_rect(projectile)
            if rects_overlap(projectile_rect, player_hitbox):
                projectile["active"] = False
                apply_player_hit(CRASH_SOUND)
                return
            if projectile["y"] + projectile["h"] >= GROUND_Y:
                projectile.update({
                    "kind": "enemy_big_tnt_ground",
                    "x": projectile["x"],
                    "y": GROUND_Y - projectile["h"],
                    "vx": 0.0,
                    "vy": 0.0,
                    "explode_at": millis() + COYOTE_BIG_BOMB_FUSE_MS,
                })
                continue
            if projectile["x"] + projectile["w"] < -40:
                projectile["active"] = False
            continue

        if projectile["kind"] == "enemy_big_tnt_ground":
            if millis() >= projectile.get("explode_at", 0):
                coyote_cave_flash_until_ms = millis() + COYOTE_CAVE_FLASH_MS
                projectile.update({
                    "kind": "big_tnt_blast",
                    "x": projectile["x"] - 22,
                    "y": GROUND_Y - 42,
                    "w": 72,
                    "h": 42,
                    "vx": 0.0,
                    "blast_until": millis() + COYOTE_BIG_BOMB_BLAST_MS,
                })
                continue
            continue

        if projectile["kind"] in ("tnt_blast", "big_tnt_blast"):
            if rects_overlap(get_projectile_rect(projectile), player_hitbox):
                apply_player_hit(CRASH_SOUND)
                return
            if millis() >= projectile.get("blast_until", 0):
                projectile["active"] = False
            continue

        projectile["x"] += projectile["vx"]
        projectile["y"] += projectile.get("vy", 0.0)
        projectile_rect = get_projectile_rect(projectile)
        if rects_overlap(projectile_rect, player_hitbox):
            projectile["active"] = False
            if flight_mode and boss.get("type") == "zeppelin_miniboss" and projectile.get("kind") == "zeppelin_bomb":
                register_flight_plane_damage_from_zeppelin()
            else:
                apply_player_hit(CRASH_SOUND)
            return
        if projectile["x"] + projectile["w"] < -40:
            projectile["active"] = False
            continue
        if projectile["y"] + projectile["h"] < -50 or projectile["y"] > height + 50:
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
            visible_arm_indices = get_cactus_visible_arm_indices(boss)
            for idx in visible_arm_indices:
                branch_rect = branch_rects[idx]
                if boss["branch_hp"][idx] <= 0:
                    continue
                if rects_overlap(projectile_rect, branch_rect):
                    boss["branch_hp"][idx] -= 1
                    boss["hits_taken"] += 1
                    if boss["branch_hp"][idx] == 0:
                        branch_center_x = branch_rect[0] + (branch_rect[2] / 2)
                        branch_center_y = branch_rect[1] + (branch_rect[3] / 2)
                        spawn_explosion_effect(
                            branch_center_x,
                            branch_center_y,
                            CACTUS_BRANCH_EXPLOSION_SIZE,
                            life_ms=CACTUS_BRANCH_EXPLOSION_LIFE_MS,
                            alpha=235,
                            hazardous=True,
                        )
                        play_sfx(BOSS_EXPLOSION_SOUND)
                    hit = True
                    break
            if (not hit) and cactus_all_arms_destroyed(boss) and rects_overlap(projectile_rect, boss_hitbox):
                boss["trunk_hp"] = max(0, boss.get("trunk_hp", 0) - 1)
                boss["hits_taken"] += 1
                spawn_explosion_effect(
                    projectile_rect[0] + (projectile_rect[2] / 2),
                    projectile_rect[1] + (projectile_rect[3] / 2),
                    BOSS_HIT_EXPLOSION_SIZE * 0.9,
                    life_ms=430,
                    alpha=220,
                )
                play_sfx(BOSS_EXPLOSION_SOUND)
                hit = True
        elif rects_overlap(projectile_rect, boss_hitbox):
            boss["hits_taken"] += 1
            hit = True

        if hit:
            if boss["type"] in ("final_boss", "zeppelin_miniboss"):
                impact_x = projectile_rect[0] + (projectile_rect[2] / 2)
                impact_y = projectile_rect[1] + (projectile_rect[3] / 2)
                spawn_explosion_effect(
                    impact_x,
                    impact_y,
                    BOSS_HIT_EXPLOSION_SIZE * random(0.78, 1.12),
                    life_ms=430,
                    alpha=220,
                )
            projectile["active"] = False
            continue
        if projectile["x"] > width + 40:
            projectile["active"] = False


def spawn_boss_attack_if_needed(boss):
    now = millis()
    if now - boss["last_attack_ms"] < boss["attack_interval_ms"]:
        return
    boss["last_attack_ms"] = now
    target_rect = get_flight_plane_rect() if (flight_mode and boss.get("type") == "zeppelin_miniboss") else get_dino_hitbox()
    player_center_x, player_center_y = get_rect_center(target_rect)

    projectile = acquire_projectile_slot(boss["enemy_projectiles"])
    if projectile is None:
        return

    if boss["type"] == "bird_miniboss":
        proj_w = 24
        proj_h = 32
        origin_x = boss["x"] + (boss["w"] * 0.24)
        origin_y = boss["y"] + (boss["h"] * 0.72)
        vx, vy = get_linear_aim_velocity(
            origin_x + (proj_w / 2),
            origin_y + (proj_h / 2),
            player_center_x,
            player_center_y,
            8.2,
            min_vy=-2.8,
            max_vy=5.2,
        )
        projectile.update({
            "x": origin_x,
            "y": origin_y,
            "w": proj_w,
            "h": proj_h,
            "vx": vx,
            "vy": vy,
            "kind": "bird_egg",
            "color": (248, 248, 232),
            "enemy": True,
        })
        play_sfx(FIRE_ENEMY_SOUND)
        return

    if boss["type"] == "zeppelin_miniboss":
        proj_w = 18
        proj_h = 18
        origin_x = boss["x"] + 42
        origin_y = boss["y"] + boss["h"] - 26
        vx, vy = get_linear_aim_velocity(
            origin_x + (proj_w / 2),
            origin_y + (proj_h / 2),
            player_center_x,
            player_center_y,
            4.9,
            min_vy=-1.4,
            max_vy=3.4,
        )
        projectile.update({
            "x": origin_x,
            "y": origin_y,
            "w": proj_w,
            "h": proj_h,
            "vx": vx,
            "vy": vy,
            "kind": "zeppelin_bomb",
            "color": (214, 74, 58),
            "enemy": True,
        })
        play_sfx(FIRE_ENEMY_SOUND)
        return
        return

    if boss["type"] == "cactus_miniboss":
        branch_rects = get_cactus_branch_rects(boss)
        living_idxs = get_cactus_visible_arm_indices(boss)
        if not living_idxs:
            projectile["active"] = False
            return
        pick = living_idxs[int(random(0, len(living_idxs)))]
        bx, by, bw, bh = branch_rects[pick]
        hp_ratio = max(0.2, min(1.0, boss["branch_hp"][pick] / 3.0))
        arm_w = int(max(10, bw * hp_ratio))
        grow_right = get_cactus_arm_side(pick) == "right"
        arm_x = int(bx if grow_right else bx + (bw - arm_w))
        proj_w = 22
        proj_h = 8
        origin_x = arm_x + arm_w + 2 if grow_right else arm_x - proj_w - 2
        origin_y = by + (bh // 2) - 4
        vx, vy = get_linear_aim_velocity(
            origin_x + (proj_w / 2),
            origin_y + (proj_h / 2),
            player_center_x,
            player_center_y,
            9.6,
            min_vy=-6.0,
            max_vy=6.0,
        )
        projectile.update({
            "x": origin_x,
            "y": origin_y,
            "w": proj_w,
            "h": proj_h,
            "vx": vx,
            "vy": vy,
            "kind": "stem",
            "color": (40, 130, 40),
            "enemy": True,
        })
        play_sfx(FIRE_ENEMY_SOUND)
        return

    if boss.get("form") == "ReuzenCoyote":
        throw_big_bomb = int(random(0, 100)) < COYOTE_BIG_BOMB_CHANCE_PCT
        proj_w = 24 if throw_big_bomb else 14
        proj_h = 24 if throw_big_bomb else 28
        origin_x = boss["x"] - 6
        origin_y = boss["y"] + (108 if throw_big_bomb else 112)
        bomb_speed = COYOTE_BIG_BOMB_THROW_SPEED if throw_big_bomb else COYOTE_TNT_THROW_SPEED
        travel_px = max(28.0, origin_x - player_center_x)
        travel_time = travel_px / max(0.1, bomb_speed)
        raw_vy = (
            (player_center_y - origin_y)
            - (0.5 * COYOTE_TNT_THROW_GRAVITY * (travel_time ** 2))
        ) / max(0.1, travel_time)
        throw_vy = max(-12.0, min(-3.6, raw_vy))
        projectile.update({
            "x": origin_x,
            "y": origin_y,
            "w": proj_w,
            "h": proj_h,
            "vx": -bomb_speed,
            "vy": throw_vy,
            "kind": "enemy_big_tnt" if throw_big_bomb else "enemy_tnt",
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

    if boss.get("form") == "ReuzenCowboy":
        crouch_shot = random(0, 1) < GIANT_COWBOY_CROUCH_CHANCE
        boss["is_crouching"] = crouch_shot
        if crouch_shot:
            boss["crouch_until_ms"] = now + GIANT_COWBOY_CROUCH_MS
            muzzle_y = boss["y"] + boss["h"] - GIANT_COWBOY_SHOT_CROUCH_OFFSET
        else:
            boss["crouch_until_ms"] = 0
            muzzle_y = boss["y"] + boss["h"] - GIANT_COWBOY_SHOT_STAND_OFFSET

        origin_x = boss["x"] - 14
        origin_y = muzzle_y - (h // 2)
        vx, vy = get_linear_aim_velocity(
            origin_x + (w / 2),
            origin_y + (h / 2),
            player_center_x,
            player_center_y,
            speed,
            min_vy=-2.2,
            max_vy=2.2,
        )
        projectile.update({
            "x": origin_x,
            "y": origin_y,
            "w": w,
            "h": h,
            "vx": vx,
            "vy": vy,
            "kind": enemy_kind,
            "color": color,
            "enemy": True,
        })
        play_sfx(FIRE_ENEMY_SOUND)
        return

    origin_x = boss["x"] - 14
    origin_y = boss["y"] + (boss["h"] // 2) + int(random(-18, 18))
    vx, vy = get_linear_aim_velocity(
        origin_x + (w / 2),
        origin_y + (h / 2),
        player_center_x,
        player_center_y,
        speed,
        min_vy=-4.2,
        max_vy=4.2,
    )
    projectile.update({
        "x": origin_x,
        "y": origin_y,
        "w": w,
        "h": h,
        "vx": vx,
        "vy": vy,
        "kind": enemy_kind,
        "color": color,
        "enemy": True,
    })
    play_sfx(FIRE_ENEMY_SOUND)


def update_final_boss_movement(boss, now):
    if boss.get("form") == "ReuzenCoyote":
        boss["x"] += boss.get("vx", 0.0)
        if boss["x"] <= boss["min_x"] or boss["x"] >= boss["max_x"]:
            boss["vx"] *= -1
        update_coyote_phase_state(boss)
        update_coyote_pits(boss)

    if boss.get("jumping", False):
        boss["jump_vy"] = boss.get("jump_vy", 0.0) + FINAL_BOSS_JUMP_GRAVITY
        boss["y"] += boss["jump_vy"]
        if boss["y"] >= boss.get("ground_y", boss["y"]):
            boss["y"] = boss.get("ground_y", boss["y"])
            boss["jumping"] = False
            boss["jump_vy"] = 0.0
            boss["next_jump_ms"] = now + int(random(FINAL_BOSS_JUMP_GAP_MIN_MS, FINAL_BOSS_JUMP_GAP_MAX_MS))
    elif now >= boss.get("next_jump_ms", 0) and not boss.get("is_crouching", False):
        boss["jumping"] = True
        boss["jump_vy"] = float(random(FINAL_BOSS_JUMP_VELOCITY_MIN, FINAL_BOSS_JUMP_VELOCITY_MAX))
        boss["next_jump_ms"] = now + int(random(FINAL_BOSS_JUMP_GAP_MIN_MS, FINAL_BOSS_JUMP_GAP_MAX_MS))

    if boss.get("is_crouching", False):
        if now >= boss.get("crouch_until_ms", 0):
            boss["is_crouching"] = False
            boss["next_duck_ms"] = now + int(random(FINAL_BOSS_DUCK_GAP_MIN_MS, FINAL_BOSS_DUCK_GAP_MAX_MS))
    elif (not boss.get("jumping", False)) and now >= boss.get("next_duck_ms", 0):
        boss["is_crouching"] = True
        boss["crouch_until_ms"] = now + int(random(FINAL_BOSS_DUCK_MIN_MS, FINAL_BOSS_DUCK_MAX_MS))
        boss["next_duck_ms"] = now + int(random(FINAL_BOSS_DUCK_GAP_MIN_MS, FINAL_BOSS_DUCK_GAP_MAX_MS))


def update_and_draw_boss_mode(theme, update_world=True):
    global on_ground, player_x
    boss = boss_state
    if boss is None:
        return

    if update_world:
        now = millis()
        prev_player_x = player_x
        prev_dino_y = dino_y
        prev_ducking = bool(is_ducking and on_ground and not game_over)

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
            apply_bird_boss_branch_collisions(prev_player_x, prev_dino_y, prev_ducking)
            boss["x"] += boss["vx"]
            boss["y"] += boss["vy"]
            if boss["x"] <= boss["min_x"] or boss["x"] >= boss["max_x"]:
                boss["vx"] *= -1
            if boss["y"] <= boss["min_y"] or boss["y"] >= boss["max_y"]:
                boss["vy"] *= -1
        elif boss["type"] == "cactus_miniboss":
            boss["y"] = boss.get("ground_y", boss["y"])
            platforms = get_cactus_boss_platform_rects()
            landed = False
            for platform_rect in platforms:
                if apply_one_way_platform_collision(
                    platform_rect,
                    prev_player_x,
                    prev_dino_y,
                    prev_ducking,
                    drop_if_unsupported=False,
                ):
                    landed = True
                    break
            if (not landed) and on_ground and dino_y < DINO_Y:
                if not any(platform_supports_player(platform_rect) for platform_rect in platforms):
                    on_ground = False
        else:
            update_final_boss_movement(boss, now)

        spawn_boss_attack_if_needed(boss)
        update_enemy_projectiles(boss)
        if game_over:
            return

        update_player_projectiles_against_boss(boss)
        update_hazardous_explosions()
        if game_over:
            return
        finish_boss_if_defeated(boss)
        if boss_state is None:
            return

        if rects_overlap(get_dino_hitbox(), get_boss_hitbox(boss)):
            apply_player_hit(CRASH_SOUND)
            return

    if boss["type"] == "bird_miniboss":
        draw_bird_boss_arena(theme)
    elif boss["type"] == "cactus_miniboss":
        draw_cactus_boss_arena(theme)
    elif boss.get("form") == "ReuzenCoyote":
        flash_ratio = max(0.0, (coyote_cave_flash_until_ms - millis()) / max(1, COYOTE_CAVE_FLASH_MS))
        cave_base = 72 + int(76 * flash_ratio)
        ground_base = 56 + int(84 * flash_ratio)
        background(cave_base, cave_base, cave_base + 6)
        fill(ground_base, ground_base, ground_base + 8)
        rect(0, GROUND_Y, width, 40)
        fill(44 + int(54 * flash_ratio), 44 + int(54 * flash_ratio), 48 + int(58 * flash_ratio))
        rect(0, 82, width, 56)
        rect(0, 0, width, 34)
        fill(92 + int(70 * flash_ratio), 92 + int(70 * flash_ratio), 96 + int(70 * flash_ratio))
        rect(58, 110, 42, 248)
        rect(width - 104, 96, 48, 268)
        stroke(108 + int(80 * flash_ratio), 108 + int(80 * flash_ratio), 112 + int(80 * flash_ratio))
        stroke_weight(2)
        line(0, GROUND_Y, width, GROUND_Y)
        no_stroke()

    draw_coyote_pits(boss, theme)
    draw_boss_entity(boss)
    draw_boss_meter(boss, theme)

    for projectile in iter_active_projectiles(boss["enemy_projectiles"]):
        draw_projectile(projectile)
    for projectile in iter_active_projectiles(player_projectiles):
        draw_projectile(projectile)
    draw_explosion_effects()

    fill(*theme["text"])
    text_size(16)
    if boss.get("form") == "ReuzenCoyote":
        text(f"TIP: throw back {COYOTE_BIG_BOMB_RETURNS_REQUIRED} big bombs with SPACE", 20, 66)
    else:
        weapon_label = get_player_weapon_profile()["label"]
        text(f"Weapon: {weapon_label} (SPACE)", 20, 66)

    if millis() < boss_intro_until_ms:
        if boss["type"] in ("bird_miniboss", "cactus_miniboss"):
            fill(200, 40, 40)
            text_size(34)
            text("Mini boss coming...", width // 2 - 168, 34)
        elif boss.get("form") == "ReuzenCoyote":
            fill(200, 40, 40)
            text_size(30)
            text(f"Throw back {COYOTE_BIG_BOMB_RETURNS_REQUIRED} big bombs!", width // 2 - 166, 34)
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
    font = pg_font.SysFont("Arial Black", key, bold=True)
    announcement_font_cache[key] = font
    return font


def wrap_announcement_lines(raw_lines, font, max_width):
    wrapped = []
    for raw_line in raw_lines:
        raw_text = str(raw_line).strip()
        if not raw_text:
            wrapped.append("")
            continue
        words = raw_text.split()
        if len(words) <= 1:
            wrapped.append(raw_text)
            continue
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if font.render(candidate, True, (255, 255, 255)).get_width() <= max_width:
                current = candidate
            else:
                wrapped.append(current)
                current = word
        wrapped.append(current)
    return wrapped


def draw_transparent_blink_text(message, y, base_size=96, base_color=(255, 74, 56)):
    surface = pg_display.get_surface()
    if surface is None:
        return
    raw_lines = str(message).split("\n")
    lines = raw_lines
    max_len = max((len(line) for line in lines), default=0)
    if max_len > 58:
        base_size = 56
    elif max_len > 42:
        base_size = 66
    elif max_len > 28:
        base_size = 80

    min_size = 46
    max_width = max(240, width - 56)
    font = get_announcement_font(base_size)
    lines = wrap_announcement_lines(raw_lines, font, max_width)
    while base_size > min_size:
        widest = max((font.render(line, True, (255, 255, 255)).get_width() for line in lines), default=0)
        if widest <= max_width and len(lines) <= 5:
            break
        base_size = max(min_size, base_size - 4)
        font = get_announcement_font(base_size)
        lines = wrap_announcement_lines(raw_lines, font, max_width)

    blink_on = int(millis() / 180) % 2 == 0
    alpha_main = 235 if blink_on else 110
    alpha_outline = 200 if blink_on else 95
    line_height = int(base_size * 1.02)
    oy = int(y)
    for text_line in lines:
        outline = font.render(text_line, True, (255, 255, 255))
        outline.set_alpha(alpha_outline)
        main = font.render(text_line, True, base_color)
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
    if millis() < level_name_announcement_until_ms and level_name_announcement_text:
        message = level_name_announcement_text
        y = 12
    elif millis() < high_jump_warning_until_ms:
        message = "HIGH JUMP!"
    elif millis() < high_jump_powerup_warning_until_ms:
        message = "HIGH JUMP\nPOWERUP!"
    elif millis() < weapon_powerup_warning_until_ms:
        message = "WEAPON POWERUP!"
    elif millis() < water_warning_until_ms:
        message = "WATER!\nSPRING OP LELIEBLADEN"
        color = (66, 176, 242)
        y = 26
    elif millis() < airplane_warning_until_ms:
        message = "JUMP ON\nTHE AIRPLANE!"
        color = (255, 212, 78)
    elif millis() < missed_plane_notice_until_ms:
        message = "YOU MISSED\nTHE PLANE"
        color = (255, 212, 78)
    elif millis() < multi_jump_notice_until_ms:
        message = "USE ↓ TO LAND QUICKER\nFOR A MULTI JUMP"

    if message is None:
        return
    draw_transparent_blink_text(message, y, base_size=100, base_color=color)


def draw_hud(theme, force_visible=False):
    blink_active = is_level_blink_active() and not force_visible
    visible = True if force_visible else (not blink_active or should_show_blink_phase())

    if visible:
        level_idx = max(0, min(MAX_LEVEL - 1, current_level - 1))
        level_goal = LEVEL_OBSTACLE_REQUIREMENTS[level_idx]
        level_start_obstacles = get_level_start_obstacle_count(current_level)
        level_progress = max(0, obstacles_cleared - level_start_obstacles)
        level_progress = min(level_goal, level_progress)
        fill(*theme["text"])
        text_size(24)
        text(f"Score: {score}", 20, 40)
        text_size(18)
        text(f"Coins: {coin_count}/{MAX_COIN_POUCH}", 20, 66)
        status_y = 88
        if is_shield_active():
            shield_left = max(0.0, (shield_until_ms - millis()) / 1000.0)
            draw_shop_item_icon("shield", 18, status_y - 14, 18, theme)
            text(f"Shield: {shield_left:.1f}s", 42, status_y)
            status_y += 20
        if is_coin_boost_active():
            coin_left = max(0.0, (coin_boost_until_ms - millis()) / 1000.0)
            draw_shop_item_icon("coin_boost", 18, status_y - 14, 18, theme)
            text(f"Coin x2: {coin_left:.0f}s", 42, status_y)
            status_y += 20
        if is_jump_shoes_active():
            shoes_left = max(0.0, (jump_shoes_until_ms - millis()) / 1000.0)
            draw_shop_item_icon("jump_shoes", 18, status_y - 14, 18, theme)
            text(f"Jump shoes: {shoes_left:.0f}s", 42, status_y)
            status_y += 20
        if shop_extra_life_count > 0:
            draw_shop_item_icon("extra_life", 18, status_y - 14, 18, theme)
            text(f"Extra lives: {shop_extra_life_count}", 42, status_y)
        text_size(24)
        text(f"Level: {current_level}", width - 150, 40)
        text_size(16)
        text(f"Obstacles: {level_progress}/{level_goal}", width - 190, 66)

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

        draw_pipe_column(x, 0, FLIGHT_PIPE_WIDTH, top_h)
        draw_pipe_column(x, bottom_y, FLIGHT_PIPE_WIDTH, bottom_h)


def update_and_draw_flight_mode(theme, update_world=True):
    global flight_plane_x, flight_plane_y, flight_pipe_spawn_due_ms, score
    global boss_state, boss_intro_until_ms
    global flight_pipes

    now = millis()
    boss = boss_state if boss_state is not None and boss_state.get("type") == "zeppelin_miniboss" else None
    if update_world:
        # During the zeppelin section the plane can roam the whole arena.
        if fly_left_pressed:
            flight_plane_x -= FLIGHT_PLANE_SPEED
        if fly_right_pressed:
            flight_plane_x += FLIGHT_PLANE_SPEED
        if fly_up_pressed:
            flight_plane_y -= FLIGHT_PLANE_SPEED
        if fly_down_pressed:
            flight_plane_y += FLIGHT_PLANE_SPEED

        min_plane_x, max_plane_x, min_plane_y, max_plane_y = get_flight_plane_bounds(has_boss=(boss is not None))
        flight_plane_x = max(min_plane_x, min(max_plane_x, flight_plane_x))
        flight_plane_y = max(min_plane_y, min(max_plane_y, flight_plane_y))

        if boss is None and now >= flight_pipe_spawn_due_ms:
            spawn_flight_pipe()
            spawn_delay = max(700, int(FLIGHT_PIPE_SPAWN_BASE_MS / max(0.8, scroll_speed / BASE_SCROLL_SPEED)))
            flight_pipe_spawn_due_ms = now + spawn_delay

        for pipe in flight_pipes:
            pipe["x"] -= scroll_speed
            if not pipe["passed"] and pipe["x"] + FLIGHT_PIPE_WIDTH < flight_plane_x:
                pipe["passed"] = True
                score += FLIGHT_PIPE_POINTS
                register_cleared_obstacle()

        if boss is None and current_level >= flight_mode_exit_level:
            if not boss_completed.get(6, False):
                boss_state = spawn_boss_for_level(6)
                boss_intro_until_ms = 0
                boss = boss_state
                flight_pipes = []
            else:
                end_flight_mode()
                return

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
                crash_flight_mode()
                break

        if boss is not None:
            phase_completed = update_zeppelin_boss_phase(boss, now)
            if phase_completed:
                boss_intro_until_ms = now + BOSS_INTRO_DURATION_MS

            if boss.get("phase") == "fight":
                boss["x"] += boss.get("vx", 0.0)
                boss["y"] += boss.get("vy", 0.0)
                if boss["x"] <= boss["min_x"] or boss["x"] >= boss["max_x"]:
                    boss["vx"] *= -1
                if boss["y"] <= boss["min_y"] or boss["y"] >= boss["max_y"]:
                    boss["vy"] *= -1
                spawn_boss_attack_if_needed(boss)
                update_enemy_projectiles(boss)
                if game_over:
                    return
                update_player_projectiles_against_boss(boss)
                finish_boss_if_defeated(boss)
                if not flight_mode:
                    return
                if rects_overlap(get_flight_plane_rect(), get_boss_hitbox(boss)):
                    crash_flight_mode()
                    return

    if boss is not None:
        intro_progress = get_zeppelin_intro_progress(boss, now)
        draw_zeppelin_city_backdrop(theme, arena_mode=(boss.get("phase") == "fight"), reveal_ratio=intro_progress)
        stroke(86, 74, 60)
        stroke_weight(2)
        line(0, GROUND_Y, width, GROUND_Y)
        no_stroke()
    else:
        draw_flight_pipes()

    update_and_draw_flight_plane_smoke()

    if boss is not None:
        draw_boss_entity(boss)
        if boss.get("phase") == "fight":
            draw_boss_meter(boss, theme)
            for projectile in iter_active_projectiles(boss["enemy_projectiles"]):
                draw_projectile(projectile)
            for projectile in iter_active_projectiles(player_projectiles):
                draw_projectile(projectile)
            draw_explosion_effects()
        fill(*theme["text"])
        text_size(16)
        if boss.get("phase") == "fight":
            text("Weapon: Plane slingshot (SPACE)", 20, 66)
            text(f"Plane HP: {flight_plane_hp}/{FLIGHT_PLANE_MAX_HP}", 20, 88)
        else:
            text("Fly into the city. The zeppelin is moving in...", 20, 66)

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

    if boss is not None and boss.get("phase") != "fight":
        fill(255, 212, 78)
        text_size(28)
        text("Entering the city...", width // 2 - 118, 34)
        text_size(20)
        text("The zeppelin flies in from the left", width // 2 - 140, 62)
    elif boss is not None and millis() < boss_intro_until_ms:
        fill(200, 40, 40)
        text_size(32)
        text("Mini boss: Zeppelin!", width // 2 - 142, 34)
    elif millis() < airplane_warning_until_ms and not game_over:
        fill(*theme["accent"])
        text_size(20)
        text("Flight mode: dodge the pipes and get ready for the city!", width // 2 - 220, 28)


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


def draw_jump_block_obstacle(draw_x, draw_y, draw_w, draw_h):
    px = int(draw_x)
    py = int(draw_y)
    pw = int(draw_w)
    ph = int(draw_h)
    fill(225, 182, 72)
    rect(px, py, pw, ph)
    fill(186, 138, 42)
    rect(px + 3, py + 3, max(4, pw - 6), max(4, ph - 6))
    fill(244, 222, 144)
    rect(px + 9, py + 9, max(4, pw - 18), max(4, ph - 18))
    fill(126, 84, 22)
    rect(px + (pw // 2) - 2, py + 10, 4, ph - 20)
    rect(px + 10, py + (ph // 2) - 2, pw - 20, 4)


def update_and_draw_jump_block_garden(theme):
    if not is_ground_wet_active() and not jump_block_droplets:
        return

    if is_ground_wet_active():
        fill(96, 152, 182)
        rect(0, GROUND_Y + 2, width, 38)
        fill(74, 128, 158)
        rect(0, GROUND_Y + 24, width, 10)

        growth_progress = min(
            1.0,
            max(0.0, (millis() - wet_ground_started_ms) / max(1, JUMP_BLOCK_FLOWER_GROW_MS)),
        )
        for flower in ground_flowers:
            stem_h = flower["stem_h"] * growth_progress
            bloom_r = flower["petal_r"] * growth_progress
            stem_x = int(flower["x"])
            stem_top_y = int(GROUND_Y - stem_h)
            fill(*flower["stem"])
            rect(stem_x, stem_top_y, 3, max(6, int(stem_h)))
            if bloom_r >= 2.0:
                bloom_x = stem_x + 1
                bloom_y = stem_top_y
                fill(*flower["petal"])
                rect(int(bloom_x - bloom_r), int(bloom_y - 2), int(bloom_r * 2), 4)
                rect(int(bloom_x - 2), int(bloom_y - bloom_r), 4, int(bloom_r * 2))
                fill(*flower["center"])
                rect(int(bloom_x - 1), int(bloom_y - 1), 3, 3)

    alive_droplets = []
    for droplet in jump_block_droplets:
        if not game_paused and not game_over:
            droplet["y"] += droplet["vy"]
        if droplet["y"] >= GROUND_Y + 6:
            continue
        fill(92, 176, 226)
        rect(int(droplet["x"]), int(droplet["y"]), droplet["size"], droplet["size"] + 2)
        alive_droplets.append(droplet)
    jump_block_droplets[:] = alive_droplets


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
    btn_x = 36
    _, _, card_y, _, _ = get_character_select_layout()[0]
    total_stack_h = btn_h * 3 + 12 * 2
    btn_y = card_y - total_stack_h - 34
    return btn_x, btn_y, btn_w, btn_h


def get_explain_button_rect():
    btn_x, btn_y, btn_w, btn_h = get_start_button_rect()
    return btn_x, btn_y + btn_h + 12, btn_w, btn_h


def get_shop_button_rect():
    btn_x, btn_y, btn_w, btn_h = get_explain_button_rect()
    return btn_x, btn_y + btn_h + 12, btn_w, btn_h


def get_info_screen_action_layout():
    panel_x = width - 280
    panel_y = 210
    button_w = 232
    button_h = 40
    gap = 12
    return [
        {"key": "debug", "label": "Debug mode", "x": panel_x, "y": panel_y, "w": button_w, "h": button_h},
        {"key": "music", "label": "Music", "x": panel_x, "y": panel_y + (button_h + gap), "w": button_w, "h": button_h},
        {"key": "sfx", "label": "SFX", "x": panel_x, "y": panel_y + ((button_h + gap) * 2), "w": button_w, "h": button_h},
        {"key": "speech", "label": "Welcome speech", "x": panel_x, "y": panel_y + ((button_h + gap) * 3), "w": button_w, "h": button_h},
        {"key": "back", "label": "Back", "x": panel_x, "y": panel_y + ((button_h + gap) * 4), "w": button_w, "h": button_h},
    ]


def get_info_screen_action_state(action_key):
    if action_key == "debug":
        return isDebugMode
    if action_key == "music":
        return shared.music_enabled
    if action_key == "sfx":
        return shared.sound_enabled
    if action_key == "speech":
        return is_intro_speech_playing()
    return None


def draw_info_screen_actions(theme):
    fill(*theme["accent"])
    text_size(18)
    text("Touch options", width - 278, 186)

    for action in get_info_screen_action_layout():
        x = int(action["x"])
        y = int(action["y"])
        w = int(action["w"])
        h = int(action["h"])
        state = get_info_screen_action_state(action["key"])

        fill(255, 255, 255)
        no_stroke()
        rect(x, y, w, h)
        draw_rounded_rect_outline(x, y, w, h, 10, theme["accent"], 2)

        fill(*theme["text"])
        text_size(18)
        text(action["label"], x + 14, y + 25)

        if state is None:
            continue

        pill_w = 64
        pill_h = 24
        pill_x = x + w - pill_w - 12
        pill_y = y + ((h - pill_h) // 2)
        if state:
            fill(96, 180, 110)
        else:
            fill(186, 194, 206)
        rect(pill_x, pill_y, pill_w, pill_h)
        fill(255 if state else 42, 255 if state else 50, 255 if state else 64)
        text_size(14)
        text("ON" if state else "OFF", pill_x + 17, pill_y + 16)


def handle_info_screen_click(x, y):
    global isDebugMode, debug_coin_pressed

    for action in get_info_screen_action_layout():
        if not point_in_rect(x, y, action["x"], action["y"], action["w"], action["h"]):
            continue

        action_key = action["key"]
        if action_key == "back":
            shared.show_info = False
            stop_intro_speech()
            update_background_music(force=True)
            return True

        if action_key == "debug":
            isDebugMode = not isDebugMode
            if not isDebugMode:
                debug_coin_pressed = False
            return True

        if action_key == "music":
            shared.music_enabled = not shared.music_enabled
            update_background_music(force=True)
            return True

        if action_key == "sfx":
            shared.sound_enabled = not shared.sound_enabled
            if not shared.sound_enabled:
                stop_intro_speech()
            return True

        if action_key == "speech":
            if not shared.sound_enabled:
                shared.sound_enabled = True
            toggle_intro_speech_playback()
            return True

    return False


def draw_start_button(theme):
    btn_x, btn_y, btn_w, btn_h = get_start_button_rect()
    fill(255, 255, 255)
    no_stroke()
    rect(btn_x, btn_y, btn_w, btn_h)
    draw_rounded_rect_outline(btn_x, btn_y, btn_w, btn_h, 12, theme["accent"], 3)
    fill(*theme["accent"])
    text_size(24)
    text("Start", btn_x + 40, btn_y + 30)


def draw_explain_button(theme):
    btn_x, btn_y, btn_w, btn_h = get_explain_button_rect()
    fill(255, 255, 255)
    no_stroke()
    rect(btn_x, btn_y, btn_w, btn_h)
    draw_rounded_rect_outline(btn_x, btn_y, btn_w, btn_h, 12, theme["accent"], 3)

    fill(*theme["accent"])
    rect(btn_x + 10, btn_y + 10, 24, 24)
    fill(255, 255, 255)
    text_size(22)
    text("i", btn_x + 19, btn_y + 28)

    fill(*theme["accent"])
    text_size(22)
    text("Explain", btn_x + 44, btn_y + 29)


def draw_shop_button(theme):
    btn_x, btn_y, btn_w, btn_h = get_shop_button_rect()
    fill(255, 255, 255)
    no_stroke()
    rect(btn_x, btn_y, btn_w, btn_h)
    draw_rounded_rect_outline(btn_x, btn_y, btn_w, btn_h, 12, theme["accent"], 3)
    fill(*theme["accent"])
    text_size(22)
    text("Shop", btn_x + 48, btn_y + 29)


def get_shop_item_layout():
    card_w = 280
    card_h = 108
    gap_x = 24
    gap_y = 18
    start_x = 92
    start_y = 138
    layout = []
    for idx, item in enumerate(SHOP_ITEMS):
        row = idx // 2
        col = idx % 2
        card_x = start_x + col * (card_w + gap_x)
        card_y = start_y + row * (card_h + gap_y)
        layout.append((item, card_x, card_y, card_w, card_h))
    return layout


def get_shop_buy_button_rect(card_x, card_y, card_w, card_h):
    btn_w = 86
    btn_h = 30
    btn_x = card_x + card_w - btn_w - 12
    btn_y = card_y + card_h - btn_h - 10
    return btn_x, btn_y, btn_w, btn_h


def get_shop_back_button_rect():
    btn_w = 126
    btn_h = 38
    btn_x = width - btn_w - 34
    btn_y = height - btn_h - 22
    return btn_x, btn_y, btn_w, btn_h


def draw_shop_seller_with_tie(sx=26, sy=168):
    fill(255, 225, 186)
    rect(sx + 24, sy, 62, 52)
    fill(32, 32, 38)
    rect(sx + 20, sy + 50, 72, 96)
    fill(212, 40, 40)
    rect(sx + 50, sy + 60, 12, 34)
    fill(170, 24, 24)
    rect(sx + 47, sy + 88, 18, 20)
    fill(20, 20, 20)
    rect(sx + 36, sy + 14, 10, 8)
    rect(sx + 65, sy + 14, 10, 8)
    fill(245, 245, 245)
    rect(sx + 42, sy + 34, 24, 4)


def draw_shop_screen(theme):
    global shop_selected_index
    stall_x, stall_y, stall_w, stall_h, item_layout = get_shop_overlay_layout()
    active_items = get_active_shop_items()
    back_selection_idx = len(active_items)
    if shop_selected_index < 0 or shop_selected_index > back_selection_idx:
        shop_selected_index = 0
    fill(*theme["text"])
    text_size(40)
    title_text = "Powerup Shop"
    subtitle_text = "Use arrows to choose, SPACE to buy."
    if game_started and pending_boss_shop_level > 0:
        title_text = f"Badger Shop L{pending_boss_shop_level}"
        subtitle_text = "Boss prep: arrows + SPACE, then Back."
    text(title_text, 214, 64)
    text_size(20)
    text(subtitle_text, 214, 92)
    text(f"Coin pouch: {coin_count}/{MAX_COIN_POUCH}", 214, 118)

    fill(250, 248, 240)
    rect(stall_x - 18, stall_y - 18, stall_w + 36, stall_h + 36)
    draw_rounded_rect_outline(stall_x - 18, stall_y - 18, stall_w + 36, stall_h + 36, 18, theme["ground_line"], 2)
    if BADGER_SHOP_IMG is not None:
        image(BADGER_SHOP_IMG, stall_x, stall_y, stall_w, stall_h)
    else:
        draw_badger_shop_fallback(stall_x, stall_y, stall_w, stall_h, theme)

    for idx, (item, icon_x, icon_y, icon_w, icon_h) in enumerate(item_layout):
        if BADGER_SHOP_IMG is not None:
            draw_shop_item_highlight(
                icon_x,
                icon_y,
                icon_w,
                icon_h,
                theme,
                selected=(shop_selected_index == idx),
            )
        else:
            draw_shop_icon_button(
                item,
                icon_x,
                icon_y,
                icon_w,
                icon_h,
                theme,
                selected=(shop_selected_index == idx),
            )

    fill(*theme["text"])
    text_size(14)
    text("Choose an item on the counter with arrows, then press SPACE.", stall_x + 72, stall_y + stall_h + 26)

    if 0 <= shop_selected_index < len(active_items):
        selected_item = active_items[shop_selected_index]
        owned_count = get_shop_item_count(selected_item["key"])
        text_size(18)
        text(
            f"{selected_item['label']}  {selected_item['cost']}c  owned x{owned_count}",
            stall_x + 28,
            stall_y + stall_h + 52,
        )
        text_size(15)
        text(selected_item["desc"], stall_x + 28, stall_y + stall_h + 74)

    back_x, back_y, back_w, back_h = get_shop_back_button_rect()
    fill(255, 255, 255)
    rect(back_x, back_y, back_w, back_h)
    draw_rounded_rect_outline(back_x, back_y, back_w, back_h, 10, theme["accent"], 3)
    if shop_selected_index == back_selection_idx:
        back_pulse = (math.sin(millis() / 190.0) + 1.0) * 0.5
        pad = 3 + int(back_pulse * 4)
        draw_rounded_rect_outline(
            back_x - pad,
            back_y - pad,
            back_w + pad * 2,
            back_h + pad * 2,
            12,
            (255, 220, 104),
            2 + int(back_pulse * 2),
        )
    fill(*theme["accent"])
    text_size(20)
    text("Back", back_x + 36, back_y + 26)

    if millis() < shop_notice_until_ms and shop_notice_text:
        fill(*theme["accent"])
        text_size(18)
        text(shop_notice_text, 168, height - 26)


def draw_crown_badge_on_card(x, card_y, card_w, card_h):
    crown_w = 40
    crown_h = 28
    crown_x = int(x + (card_w / 2) - (crown_w / 2))
    crown_y = int(card_y - (crown_h / 2) - 8)

    if CROWN_BADGE_IMG is not None:
        image(CROWN_BADGE_IMG, crown_x, crown_y, crown_w, crown_h)
        return

    # Fallback: simple pixel-style crown.
    fill(252, 214, 52)
    rect(crown_x + 2, crown_y + 13, crown_w - 4, crown_h - 14)
    fill(236, 182, 36)
    rect(crown_x + 2, crown_y + 13, 8, 7)
    rect(crown_x + crown_w - 10, crown_y + 13, 8, 7)
    fill(252, 214, 52)
    rect(crown_x + 3, crown_y + 7, 8, 6)
    rect(crown_x + 16, crown_y + 2, 8, 11)
    rect(crown_x + 29, crown_y + 7, 8, 6)


def crown_menu_card_decorator(draw_fn):
    def wrapped(idx, x, card_y, card_w, card_h, character_key, character, theme):
        draw_fn(idx, x, card_y, card_w, card_h, character_key, character, theme)
        if character_completed.get(character_key, False):
            draw_crown_badge_on_card(x, card_y, card_w, card_h)
    return wrapped


@crown_menu_card_decorator
def draw_menu_character_card(idx, x, card_y, card_w, card_h, character_key, character, theme):
    fill(255, 255, 255)
    no_stroke()
    rect(x, card_y, card_w, card_h)
    draw_rounded_rect_outline(x, card_y, card_w, card_h, 14, theme["ground_line"], 2)

    preview = character["stand"]
    image(preview, x + 28, card_y + 16, 114, 96)

    fill(*theme["text"])
    text_size(20)
    text(character["label"], x + 46, card_y + 140)


def draw_character_select(theme):
    text_size(22)
    fill(*theme.get("menu_meta", theme["text"]))
    _, _, card_y, _, _ = get_character_select_layout()[0]
    text("Choose character: left/right arrows", width // 2 - 185, card_y - 22)

    pulse = (math.sin(millis() / 180.0) + 1.0) * 0.5
    pulse_pad = int(5 + pulse * 6)
    pulse_weight = int(2 + pulse * 2)

    for idx, x, card_y, card_w, card_h in get_character_select_layout():
        character_key = CHARACTER_ORDER[idx]
        character = CHARACTER_CONFIG[character_key]
        draw_menu_character_card(idx, x, card_y, card_w, card_h, character_key, character, theme)

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
    draw_explain_button(theme)
    draw_shop_button(theme)


def update_and_draw_bonus_coins():
    global score, coin_count
    if not bonus_coins:
        return

    dino_hitbox = get_dino_hitbox()
    remaining = []
    for coin in bonus_coins:
        if not game_paused and not game_over:
            coin["x"] -= scroll_speed

        if coin["x"] + coin["w"] < -8:
            continue

        draw_coin_pickup(coin["x"], coin["y"], coin["w"], coin["h"])
        coin_rect = (coin["x"], coin["y"], coin["w"], coin["h"])
        if (not game_paused and not game_over) and rects_overlap(dino_hitbox, coin_rect):
            gained_coins = COIN_SCORE_VALUE * (2 if is_coin_boost_active() else 1)
            coin_count = min(MAX_COIN_POUCH, coin_count + gained_coins)
            score += gained_coins
            play_sfx(COIN_SOUND)
            continue

        remaining.append(coin)

    bonus_coins[:] = remaining


def update_and_draw_extra_obstacles(theme):
    global score, is_ducking

    if not extra_obstacles:
        return

    dino_hitbox = get_dino_hitbox()
    remaining = []
    for obstacle in extra_obstacles:
        if not game_paused and not game_over:
            obstacle["x"] -= scroll_speed
        obstacle_type_local = obstacle["type"]
        obstacle_cfg = OBSTACLE_CONFIG[obstacle_type_local]
        draw_x, draw_y, draw_w, draw_h = get_extra_obstacle_draw_rect(obstacle)
        image(obstacle_cfg["img"], draw_x, draw_y, draw_w, draw_h)

        if not game_paused and not game_over and draw_x < -draw_w:
            score += obstacle_cfg["points"]
            register_cleared_obstacle()
            continue

        obstacle_hitbox = get_extra_obstacle_hitbox(obstacle)
        if not game_paused and not game_over and rects_overlap(dino_hitbox, obstacle_hitbox):
            is_ducking = False
            apply_player_hit(CRASH_SOUND)
            if game_over:
                remaining.append(obstacle)
                break

        remaining.append(obstacle)

    extra_obstacles[:] = remaining


def draw():
    global dino_y, velocity_y, on_ground, obstacle_x, score, high_score, coin_count
    global is_ducking, bird_duck_scored, is_fast_falling, snake_hiss_played_for_current
    global debug_coin_repeat_until_ms
    global high_jump_powerup_charges, high_jump_powerup_warning_until_ms
    global weapon_powerup_warning_until_ms
    global missed_plane_notice_until_ms
    global pending_weapon_powerup_level, weapon_powerup_ready, weapon_powerup_level
    global weapon_powerup_ready, weapon_powerup_level, pending_weapon_powerup_level
    global final_boss_snapshot, final_boss_next_blast_ms
    global player_x
    theme = get_theme()
    update_background_music()
    if score > high_score:
        high_score = int(score)

    keys_pressed = pg_key.get_pressed() if pygame_get_init() else None
    coin_key_held = bool(keys_pressed and keys_pressed[K_c])

    if (
        (debug_coin_pressed or coin_key_held)
        and isDebugMode
        and not credits_active
        and not game_over
        and millis() >= debug_coin_repeat_until_ms
    ):
        coin_count = min(MAX_COIN_POUCH, coin_count + 1)
        debug_coin_repeat_until_ms = millis() + 90

    if credits_active:
        draw_credits_screen()
        return

    background(*theme["bg"])
    draw_parallax_clouds(theme)
    fill(*theme["ground_fill"])
    rect(0, CACTUS_GUIDE_LINE_Y, width, height - CACTUS_GUIDE_LINE_Y)  # ground
    stroke(*theme["ground_line"])
    stroke_weight(1)
    line(0, CACTUS_GUIDE_LINE_Y, width, CACTUS_GUIDE_LINE_Y)
    stroke_weight(2)
    line(0, GROUND_Y, width, GROUND_Y)
    no_stroke()
    update_and_draw_jump_block_garden(theme)
    update_mini_boss_defeat_sequences()

    if shared.show_info:
        shared.draw_info_screen(INFO_TEXT)
        fill(20)
        text_size(20)
        speed_mult = scroll_speed / BASE_SCROLL_SPEED
        text(f"Current level: {current_level}", 500, 120)
        text(f"Speed: {speed_mult:.2f}x", 500, 148)
        text_size(16)
        text("L: level +1, Shift+L: level -1", 500, 176)
        draw_info_screen_actions(theme)
        if millis() < screenshot_notice_until_ms:
            fill(30, 110, 30)
            text_size(14)
            text(screenshot_notice_text, 30, height - 24)
        return

    if not game_started:
        draw_main_character()
        if shop_active:
            draw_shop_screen(theme)
            draw_debug_overlay()
            return
        menu_meta_y = 112
        menu_title_y = 196
        menu_prompt_y = 236
        fill(*theme.get("menu_meta", theme["text"]))
        text_size(22)
        text(f"Coin pouch: {coin_count}/{MAX_COIN_POUCH}", width // 2 - 122, menu_meta_y)
        text(f"Highscore: {high_score}", width // 2 - 92, menu_meta_y + 30)
        fill(*theme.get("menu_title", theme["accent"]))
        text_size(44)
        text("Dino Game", width // 2 - 105, menu_title_y)
        fill(*theme.get("menu_prompt", theme["text"]))
        text_size(21)
        text("Start: SPACE/A or click Start", width // 2 - 165, menu_prompt_y)
        text("Jump: up arrow", width // 2 - 88, menu_prompt_y + 28)
        text("Duck: down arrow (air = fast fall)", width // 2 - 190, menu_prompt_y + 56)
        text("High jump: duck then jump within 0.5s", width // 2 - 220, menu_prompt_y + 84)
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
        draw_touch_controls_overlay()
        draw_debug_overlay()
        return

    if game_completed:
        now = millis()
        draw_main_character()
        if final_boss_snapshot is not None:
            draw_boss_entity(final_boss_snapshot)
            if now <= final_boss_defeat_until_ms and now >= final_boss_next_blast_ms:
                burst_count = int(random(4, 8))
                spawn_final_boss_explosion_burst(final_boss_snapshot, count=burst_count)
                final_boss_next_blast_ms = now + FINAL_BOSS_BLAST_INTERVAL_MS
            if now > final_boss_defeat_until_ms:
                final_boss_snapshot = None
        draw_explosion_effects()
        if pending_credits_after_victory and final_boss_snapshot is None and not explosion_effects:
            start_credits_mode()
            return
        draw_transparent_blink_text("Congratulations!", 18, base_size=92, base_color=(224, 44, 44))
        fill(30, 150, 60)
        text_size(44)
        text("You Win!", width // 2 - 98, height // 2 - 12)
        fill(*theme["text"])
        text_size(22)
        text("Final boss defeated. Press Q for start screen", width // 2 - 208, height // 2 + 26)
        draw_hud(theme, force_visible=True)
        draw_touch_controls_overlay()
        draw_debug_overlay()
        return

    if post_boss_transition is not None:
        if resolve_post_boss_transition_if_ready():
            draw_main_character()
            draw_hud(theme)
            draw_touch_controls_overlay()
            draw_debug_overlay()
            return
        draw_post_boss_transition(theme)
        return

    if flight_mode:
        update_and_draw_flight_mode(theme, update_world=(not game_paused and not game_over))
        if not flight_mode:
            draw_main_character()
            draw_hud(theme)
            draw_touch_controls_overlay()
            draw_debug_overlay()
            return
        draw_main_character()
        if game_paused and not game_over:
            fill(40)
            text_size(34)
            text("Paused", width // 2 - 65, height // 2 - 8)
            text_size(18)
            text("Press P to continue", width // 2 - 96, height // 2 + 22)
            draw_hud(theme)
            draw_touch_controls_overlay()
            draw_debug_overlay()
            return
        if game_over:
            fill(255, 0, 0)
            text_size(40)
            text("Game Over!", width // 2 - 120, height // 2)
            draw_hud(theme, force_visible=True)
            fill(*theme["text"])
            text_size(22)
            text(f"Speed: x{round(scroll_speed / BASE_SCROLL_SPEED, 2)}", width - 195, 72)
            text("Press SPACE for start screen", width // 2 - 165, height // 2 + 40)
            draw_touch_controls_overlay()
            draw_debug_overlay()
            return
        draw_hud(theme)
        draw_touch_controls_overlay()
        draw_debug_overlay()
        return

    if shop_active:
        draw_main_character()
        draw_shop_screen(theme)
        draw_hud(theme, force_visible=True)
        draw_touch_controls_overlay()
        draw_debug_overlay()
        return

    if pre_boss_scene_level > 0:
        prev_player_x = player_x
        prev_dino_y = dino_y
        prev_ducking = bool(is_ducking and on_ground and not game_over)
        if not game_paused:
            if pipe_entry_active:
                update_pipe_entry_sequence()
                if not pipe_entry_active:
                    return
            else:
                move_dir = int(boss_right_pressed) - int(boss_left_pressed)
                if move_dir != 0:
                    min_player_x = 24.0
                    max_player_x = float(width - DINO_W - 24)
                    player_x = max(min_player_x, min(max_player_x, player_x + (move_dir * BOSS_PLAYER_SPEED)))
                update_player_vertical_motion()
                apply_pre_boss_scene_collisions(prev_player_x, prev_dino_y, prev_ducking)
                if maybe_start_bird_nest_encounter():
                    return
        draw_pre_boss_scene(theme)
        if pipe_entry_active:
            draw_main_character()
            draw_pre_boss_entrance(pre_boss_scene_level, theme)
        else:
            draw_main_character()
        if game_paused:
            fill(40)
            text_size(34)
            text("Paused", width // 2 - 65, height // 2 - 8)
            text_size(18)
            text("Press P to continue", width // 2 - 96, height // 2 + 22)
        draw_hud(theme, force_visible=True)
        draw_touch_controls_overlay()
        draw_debug_overlay()
        return

    maybe_start_boss_encounter()
    if boss_state is not None:
        update_and_draw_boss_mode(theme, update_world=(not game_paused and not game_over))
        draw_main_character()
        if game_paused and not game_over:
            fill(40)
            text_size(34)
            text("Paused", width // 2 - 65, height // 2 - 8)
            text_size(18)
            text("Press P to continue", width // 2 - 96, height // 2 + 22)
            draw_hud(theme)
            draw_touch_controls_overlay()
            draw_debug_overlay()
            return
        if game_over:
            fill(255, 0, 0)
            text_size(40)
            text("Game Over!", width // 2 - 120, height // 2)
            draw_hud(theme, force_visible=True)
            fill(*theme["text"])
            text_size(22)
            text(f"Speed: x{round(scroll_speed / BASE_SCROLL_SPEED, 2)}", width - 195, 72)
            text("Press SPACE for start screen", width // 2 - 165, height // 2 + 40)
            draw_touch_controls_overlay()
            draw_debug_overlay()
            return
        draw_hud(theme)
        draw_touch_controls_overlay()
        draw_debug_overlay()
        return

    # Draw obstacle
    obstacle_cfg = OBSTACLE_CONFIG[obstacle_type]
    obstacle_draw_x, obstacle_draw_y, obstacle_draw_w, obstacle_draw_h = get_obstacle_draw_rect()
    if obstacle_type == "high_jump_powerup":
        draw_high_jump_powerup(obstacle_draw_x, obstacle_draw_y, obstacle_draw_w, obstacle_draw_h, theme)
    elif obstacle_type == "weapon_powerup":
        draw_weapon_powerup(obstacle_draw_x, obstacle_draw_y, obstacle_draw_w, obstacle_draw_h)
    elif obstacle_type == "jump_block":
        draw_jump_block_obstacle(obstacle_draw_x, obstacle_draw_y, obstacle_draw_w, obstacle_draw_h)
    elif obstacle_type == "coin":
        draw_coin_pickup(obstacle_draw_x, obstacle_draw_y, obstacle_draw_w, obstacle_draw_h)
    elif obstacle_type == "water_lily":
        draw_water_lily_obstacle(obstacle_draw_x, obstacle_draw_y, obstacle_draw_w, obstacle_draw_h)
    elif obstacle_type == "pipe_pair":
        draw_ground_pipe_pair(obstacle_draw_x)
    else:
        image(obstacle_cfg["img"], obstacle_draw_x, obstacle_draw_y, obstacle_draw_w, obstacle_draw_h)
    update_and_draw_bonus_coins()
    update_and_draw_extra_obstacles(theme)
    draw_main_character()

    if game_paused:
        fill(40)
        text_size(34)
        text("Paused", width // 2 - 65, height // 2 - 8)
        text_size(18)
        text("Press P to continue", width // 2 - 96, height // 2 + 22)
        draw_hud(theme)
        draw_touch_controls_overlay()
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
        text(f"Collect weapon powerup for boss L{pending_weapon_powerup_level}", 20, 110)

    if not game_over:
        prev_dino_y = dino_y
        prev_ducking = bool(is_ducking and on_ground and not game_over)
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
                play_pending_high_jump_landing_roar()

        obstacle_x -= scroll_speed
        if obstacle_type == "pipe_pair":
            apply_ground_pipe_platform_collision(prev_dino_y, prev_ducking)

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
            if obstacle_type == "airplane_pickup":
                missed_plane_notice_until_ms = millis() + MISSED_PLANE_NOTICE_MS
            gained_points = obstacle_cfg["points"]
            if obstacle_cfg.get("requires_duck_score", False) and not bird_duck_scored:
                gained_points = 0
            score += gained_points
            register_cleared_obstacle()
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
                draw_touch_controls_overlay()
                return

        if obstacle_type == "jump_block":
            dino_hitbox = get_dino_hitbox()
            block_hitbox = get_obstacle_hitbox()
            block_bottom = block_hitbox[1] + block_hitbox[3]
            overlap_x = (
                dino_hitbox[0] < block_hitbox[0] + block_hitbox[2] and
                dino_hitbox[0] + dino_hitbox[2] > block_hitbox[0]
            )
            head_hits_block = (
                overlap_x and
                velocity_y < 0 and
                dino_hitbox[1] <= block_bottom <= dino_hitbox[1] + 18
            )
            if head_hits_block:
                velocity_y = 1.8
                trigger_jump_block_rain(
                    obstacle_draw_x,
                    obstacle_draw_y,
                    obstacle_draw_w,
                )
                register_cleared_obstacle()
                spawn_obstacle()
                draw_main_character()
                draw_hud(theme)
                draw_touch_controls_overlay()
                return

        # Collision detection
        dino_hitbox = get_dino_hitbox()
        obstacle_hitbox = get_obstacle_hitbox()
        if obstacle_type == "high_jump_powerup" and rects_overlap(dino_hitbox, obstacle_hitbox):
            high_jump_powerup_charges = HIGH_JUMP_POWERUP_MAX_CHARGES
            high_jump_powerup_warning_until_ms = millis() + HIGH_JUMP_POWERUP_NOTICE_MS
            register_cleared_obstacle()
            spawn_obstacle()
        elif obstacle_type == "weapon_powerup" and rects_overlap(dino_hitbox, obstacle_hitbox):
            weapon_powerup_ready = True
            weapon_powerup_level = pending_weapon_powerup_level if pending_weapon_powerup_level > 0 else current_level
            pending_weapon_powerup_level = 0
            weapon_powerup_warning_until_ms = millis() + WEAPON_POWERUP_NOTICE_MS
            register_cleared_obstacle()
            spawn_obstacle()
        elif obstacle_type == "coin" and rects_overlap(dino_hitbox, obstacle_hitbox):
            gained_coins = COIN_SCORE_VALUE * (2 if is_coin_boost_active() else 1)
            coin_count = min(MAX_COIN_POUCH, coin_count + gained_coins)
            score += gained_coins
            play_sfx(COIN_SOUND)
            register_cleared_obstacle()
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
                is_ducking = False
                apply_player_hit(SPLASH_SOUND)
        elif obstacle_type == "jump_block":
            pass
        elif rects_overlap(dino_hitbox, obstacle_hitbox):
            is_ducking = False
            apply_player_hit(CRASH_SOUND)

    if isDebugMode:
        no_fill()
        stroke(255, 0, 0)
        stroke_weight(2)
        if obstacle_type == "pipe_pair":
            top_pipe, bottom_pipe = get_ground_pipe_rects()
            rect(*top_pipe)
            rect(*bottom_pipe)
        else:
            rect(*get_obstacle_hitbox())
        no_stroke()

    draw_explosion_effects()

    if game_over:
        fill(255, 0, 0)
        text_size(40)
        text("Game Over!", width // 2 - 120, height // 2)
        draw_hud(theme, force_visible=True)
        fill(*theme["text"])
        text_size(22)
        text(f"Speed: x{round(scroll_speed / BASE_SCROLL_SPEED, 2)}", width - 195, 72)
        text("Press SPACE for start screen", width // 2 - 165, height // 2 + 40)
        draw_touch_controls_overlay()
        draw_debug_overlay()
        if millis() < screenshot_notice_until_ms:
            fill(30, 110, 30)
            text_size(14)
            text(screenshot_notice_text, 20, height - 20)
        return

    draw_hud(theme)
    draw_touch_controls_overlay()
    draw_debug_overlay()
    if millis() < screenshot_notice_until_ms:
        fill(30, 110, 30)
        text_size(14)
        text(screenshot_notice_text, 20, height - 20)


def perform_jump_if_possible():
    global velocity_y, on_ground, is_ducking, is_fast_falling
    global duck_jump_expires_ms, high_jump_powerup_charges
    global pending_high_jump_landing_roar
    if not (game_started and not game_over and on_ground):
        return False
    # Buk-spring binnen half seconde geeft high jump.
    now = millis()
    used_duck_window = now <= duck_jump_expires_ms
    used_jump_powerup = high_jump_powerup_charges > 0
    jump_shoes_active = is_jump_shoes_active()
    jump_velocity = JUMP_VELOCITY
    if used_jump_powerup:
        jump_velocity = STACKED_POWER_HIGH_JUMP_VELOCITY if used_duck_window else POWERUP_HIGH_JUMP_VELOCITY
        high_jump_powerup_charges = max(0, high_jump_powerup_charges - 1)
    elif used_duck_window:
        jump_velocity = HIGH_JUMP_VELOCITY
    if jump_shoes_active:
        jump_velocity *= SHOP_JUMP_SHOES_FACTOR
    is_high_jump = used_duck_window or used_jump_powerup or jump_shoes_active
    is_ducking = False
    velocity_y = jump_velocity
    on_ground = False
    is_fast_falling = False
    duck_jump_expires_ms = 0
    pending_high_jump_landing_roar = active_character_key == "dino" and is_high_jump
    play_sfx(get_jump_sound(is_high_jump=is_high_jump))
    return True


def should_show_touch_controls():
    if not TOUCH_CONTROLS_ENABLED:
        return False
    if not game_started and not game_over:
        return False
    if credits_active or shared.show_info or shop_active:
        return False
    return True


def get_touch_control_names():
    names = ["up", "down"]
    if game_over:
        names.append("action")
    if flight_mode or (game_started and (boss_state is not None or pre_boss_scene_level > 0)):
        names = ["left", "right", "up", "down", "action"]
    return names


def get_touch_controls_layout():
    names = set(get_touch_control_names())
    side = max(44, min(TOUCH_BTN_SIZE, int(min(width, height) * 0.10)))
    gap = max(7, min(TOUCH_BTN_GAP, int(side * 0.16)))
    pad = max(8, int(side * 0.14))
    buttons = {}

    if "left" in names or "right" in names:
        left_x = pad
        right_x = left_x + side + gap
        down_y = height - side - pad
        up_y = down_y - side - gap
        buttons["left"] = (left_x, down_y, side, side)
        buttons["right"] = (right_x, down_y, side, side)
        buttons["up"] = (right_x, up_y, side, side)
        buttons["down"] = (left_x, up_y, side, side)
    else:
        controls_x = width - side - pad
        down_y = height - side - pad
        up_y = down_y - side - gap
        buttons["up"] = (controls_x, up_y, side, side)
        buttons["down"] = (controls_x, down_y, side, side)

    if "action" in names:
        action_w = max(96, min(TOUCH_ACTION_BTN_W, int(side * 1.55)))
        action_h = side
        action_x = width - action_w - pad
        action_y = height - action_h - pad
        if "left" not in names and "right" not in names:
            action_x = pad
        buttons["action"] = (action_x, action_y, action_w, action_h)

    return buttons


def draw_touch_controls_overlay():
    if not should_show_touch_controls():
        return
    buttons = get_touch_controls_layout()
    labels = {
        "left": "<",
        "right": ">",
        "up": "^",
        "down": "v",
        "action": "SPACE",
    }
    for name, (bx, by, bw, bh) in buttons.items():
        is_pressed = (touch_active_button == name)
        if is_pressed:
            fill(244, 208, 88)
        else:
            fill(206, 214, 226)
        rect(int(bx), int(by), int(bw), int(bh))
        fill(22, 28, 42)
        text_size(18 if name != "action" else 20)
        tx = int(bx + (bw * 0.32))
        ty = int(by + (bh * 0.62))
        if name == "action":
            tx = int(bx + 18)
        text(labels[name], tx, ty)


def press_touch_control(name):
    global touch_active_button
    global selected_character_idx
    global fly_left_pressed, fly_right_pressed, fly_up_pressed, fly_down_pressed
    global boss_left_pressed, boss_right_pressed
    global is_ducking, duck_jump_expires_ms, is_fast_falling

    touch_active_button = name

    if pipe_entry_active:
        return True

    if name == "left":
        if not game_started:
            selected_character_idx = (selected_character_idx - 1) % len(CHARACTER_ORDER)
            return True
        if game_started and not game_over and (boss_state is not None or pre_boss_scene_level > 0):
            boss_left_pressed = True
        if game_started and flight_mode and not game_over:
            fly_left_pressed = True
        return True

    if name == "right":
        if not game_started:
            selected_character_idx = (selected_character_idx + 1) % len(CHARACTER_ORDER)
            return True
        if game_started and not game_over and (boss_state is not None or pre_boss_scene_level > 0):
            boss_right_pressed = True
        if game_started and flight_mode and not game_over:
            fly_right_pressed = True
        return True

    if name == "up":
        if game_started and flight_mode and not game_over:
            fly_up_pressed = True
            return True
        if game_started and not game_over and not game_paused:
            perform_jump_if_possible()
        return True

    if name == "down":
        if game_started and flight_mode and not game_over:
            fly_down_pressed = True
            return True
        if game_started and not game_over and not game_paused:
            if on_ground:
                is_ducking = True
                duck_jump_expires_ms = millis() + HIGH_JUMP_WINDOW_MS
            else:
                is_fast_falling = True
        if game_started and pre_boss_scene_level > 0 and not game_over:
            try_interact_pre_boss_scene()
        return True

    if name == "action":
        if shop_active:
            return True
        if game_over:
            save_character_checkpoint()
            if active_character_key in CHARACTER_ORDER:
                selected_character_idx = CHARACTER_ORDER.index(active_character_key)
            reset_game(show_splash=True)
            return True
        if not game_started:
            start_game_from_selection()
            return True
        if game_paused or game_completed or game_over:
            return True
        if boss_state is not None:
            if boss_state.get("form") == "ReuzenCoyote":
                try_throw_back_coyote_bomb()
            else:
                fire_player_weapon()
        return True

    return False


def release_touch_control(name):
    global touch_active_button
    global fly_left_pressed, fly_right_pressed, fly_up_pressed, fly_down_pressed
    global boss_left_pressed, boss_right_pressed
    global is_ducking, duck_jump_expires_ms, is_fast_falling
    if name == "left":
        fly_left_pressed = False
        boss_left_pressed = False
    elif name == "right":
        fly_right_pressed = False
        boss_right_pressed = False
    elif name == "up":
        fly_up_pressed = False
    elif name == "down":
        fly_down_pressed = False
        if on_ground:
            duck_jump_expires_ms = millis() + HIGH_JUMP_WINDOW_MS
        is_ducking = False
        is_fast_falling = False
    touch_active_button = None


def try_press_touch_control(x, y, button):
    if button != 1 or not should_show_touch_controls():
        return False
    for name, (bx, by, bw, bh) in get_touch_controls_layout().items():
        if point_in_rect(x, y, bx, by, bw, bh):
            return press_touch_control(name)
    return False


def normalize_key_code(current_key, current_key_code):
    if isinstance(current_key, str):
        return ARROW_KEY_NAMES.get(current_key.lower(), current_key_code)
    return current_key_code


def key_pressed():
    global isDebugMode, is_ducking
    global game_paused, selected_character_idx
    global duck_jump_expires_ms, is_fast_falling, game_completed
    global fly_left_pressed, fly_right_pressed, fly_up_pressed
    global fly_down_pressed
    global boss_left_pressed, boss_right_pressed
    global quit_confirm_active, is_fullscreen, coin_count
    global debug_coin_pressed, debug_coin_repeat_until_ms
    unlock_web_audio_if_needed()
    pressed_key = key.lower() if isinstance(key, str) else key
    effective_key_code = normalize_key_code(key, key_code)
    if credits_active and pressed_key == "i":
        return
    shared.handle_common_keys(
        pressed_key,
        effective_key_code,
        info_text=INFO_TEXT,
        music_toggle_callback=lambda _enabled: update_background_music(force=True),
        allow_quit=False,
    )
    if pressed_key == "i":
        stop_intro_speech()
        update_background_music(force=True)
        return
    if pressed_key == "s":
        if not shared.sound_enabled:
            stop_intro_speech()
        return
    if pressed_key == "m":
        return
    if pressed_key == "f":
        if is_fullscreen:
            size(BASE_GAME_WIDTH, BASE_GAME_HEIGHT)
            is_fullscreen = False
        else:
            full_screen()
            is_fullscreen = True
        return

    if shop_active:
        if pressed_key == "b" or effective_key_code == K_ESCAPE:
            close_shop()
            return
        if effective_key_code in (K_LEFT, K_RIGHT, K_UP, K_DOWN):
            move_shop_selection(effective_key_code)
            return
        if pressed_key in (" ", "a", "A") or effective_key_code in (10, 13):
            activate_shop_selection()
            return
        return

    if quit_confirm_active:
        if pressed_key == "y":
            exit()
        if pressed_key in ("n", "q") or effective_key_code == K_ESCAPE:
            quit_confirm_active = False
        return

    if pressed_key == "q" or effective_key_code == K_ESCAPE:
        if game_started:
            save_character_checkpoint()
            if active_character_key in CHARACTER_ORDER:
                selected_character_idx = CHARACTER_ORDER.index(active_character_key)
            reset_game(show_splash=True)
        else:
            quit_confirm_active = True
        return

    if not game_started and pressed_key == "w":
        toggle_intro_speech_playback()
        return

    if shared.show_info:
        if pressed_key == "w":
            toggle_intro_speech_playback()
            return
        if pressed_key == "l":
            if key == "L":
                debug_step_level(-1)
            else:
                debug_step_level(1)
        return

    if key in ("d", "D"):
        isDebugMode = not isDebugMode
        if not isDebugMode:
            debug_coin_pressed = False
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

    if isDebugMode and pressed_key == "v":
        game_completed = True
        start_credits_mode()
        return

    if isDebugMode and pressed_key == "c":
        debug_coin_pressed = True
        coin_count = min(MAX_COIN_POUCH, coin_count + 1)
        debug_coin_repeat_until_ms = millis() + 160
        set_shop_notice("Debug: +1 coin", duration_ms=900)
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

    if game_completed and key == " ":
        # Avoid accidental skip when player is still hammering shoot during boss defeat.
        return

    if not game_started and effective_key_code == K_LEFT:
        selected_character_idx = (selected_character_idx - 1) % len(CHARACTER_ORDER)
        return

    if not game_started and effective_key_code == K_RIGHT:
        selected_character_idx = (selected_character_idx + 1) % len(CHARACTER_ORDER)
        return

    if not game_started and key in (" ", "a", "A"):
        if shop_active:
            return
        start_game_from_selection()
        return

    if game_paused:
        return

    if pipe_entry_active:
        return

    if game_started and (boss_state is not None or pre_boss_scene_level > 0) and not game_over:
        if effective_key_code == K_LEFT:
            boss_left_pressed = True
            return
        if effective_key_code == K_RIGHT:
            boss_right_pressed = True
            return

    if game_started and pre_boss_scene_level > 0 and not game_over and effective_key_code == K_DOWN:
        if on_ground:
            is_ducking = True
            duck_jump_expires_ms = millis() + HIGH_JUMP_WINDOW_MS
        else:
            is_fast_falling = True
        try_interact_pre_boss_scene()
        return

    if game_started and not game_over and key == " " and boss_state is not None:
        if boss_state.get("form") == "ReuzenCoyote":
            try_throw_back_coyote_bomb()
            return
        fire_player_weapon()
        return

    if game_started and not game_over and key == " " and flight_mode and boss_state is not None and boss_state.get("type") == "zeppelin_miniboss":
        fire_player_weapon()
        return

    if game_started and flight_mode and not game_over:
        if effective_key_code == K_LEFT:
            fly_left_pressed = True
            return
        if effective_key_code == K_RIGHT:
            fly_right_pressed = True
            return
        if effective_key_code == K_UP:
            fly_up_pressed = True
            return
        if effective_key_code == K_DOWN:
            fly_down_pressed = True
            return
        return

    if game_started and not game_over and effective_key_code == K_DOWN:
        if on_ground:
            is_ducking = True
            duck_jump_expires_ms = millis() + HIGH_JUMP_WINDOW_MS
        else:
            is_fast_falling = True
        return

    if game_started and not game_over and effective_key_code == K_UP:
        perform_jump_if_possible()


def key_released(released_key):
    global is_ducking, duck_jump_expires_ms, is_fast_falling
    global debug_coin_pressed
    global fly_left_pressed, fly_right_pressed, fly_up_pressed, fly_down_pressed
    global boss_left_pressed, boss_right_pressed
    effective_released_key = normalize_key_code(released_key, released_key)
    if flight_mode:
        if effective_released_key == K_LEFT:
            fly_left_pressed = False
        elif effective_released_key == K_RIGHT:
            fly_right_pressed = False
        elif effective_released_key == K_UP:
            fly_up_pressed = False
        elif effective_released_key == K_DOWN:
            fly_down_pressed = False
        return

    if effective_released_key == K_LEFT:
        boss_left_pressed = False
    elif effective_released_key == K_RIGHT:
        boss_right_pressed = False
    elif effective_released_key == K_c:
        debug_coin_pressed = False

    if effective_released_key == K_DOWN:
        if on_ground:
            duck_jump_expires_ms = millis() + HIGH_JUMP_WINDOW_MS
        is_ducking = False
        is_fast_falling = False


def mouse_pressed(x, y, button):
    global touch_ignore_next_click
    if button == 1:
        unlock_web_audio_if_needed()
    if try_press_touch_control(x, y, button):
        touch_ignore_next_click = True


def mouse_released(x, y, button):
    if button != 1:
        return
    if touch_active_button is None:
        return
    release_touch_control(touch_active_button)


def mouse_clicked(x, y, button):
    global selected_character_idx, shop_active, shop_selected_index, quit_confirm_active
    global touch_ignore_next_click
    if touch_ignore_next_click:
        touch_ignore_next_click = False
        return
    if button != 1:
        return
    if shared.show_info:
        handle_info_screen_click(x, y)
        return

    if shop_active:
        _, _, _, _, item_layout = get_shop_overlay_layout()
        for item, icon_x, icon_y, icon_w, icon_h in item_layout:
            if point_in_rect(x, y, icon_x, icon_y, icon_w, icon_h):
                buy_shop_item(item["key"])
                return
        back_x, back_y, back_w, back_h = get_shop_back_button_rect()
        if point_in_rect(x, y, back_x, back_y, back_w, back_h):
            close_shop()
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
        return

    explain_x, explain_y, explain_w, explain_h = get_explain_button_rect()
    if point_in_rect(x, y, explain_x, explain_y, explain_w, explain_h):
        shared.show_info = True
        stop_intro_speech()
        update_background_music(force=True)
        return

    shop_x, shop_y, shop_w, shop_h = get_shop_button_rect()
    if point_in_rect(x, y, shop_x, shop_y, shop_w, shop_h):
        shop_active = True
        shop_selected_index = 0
        quit_confirm_active = False


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
    surface = pg_display.get_surface()
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
    glow = transform.smoothscale(frame, (glow_size, glow_size)).copy()
    glow.set_alpha(alpha_by_charge.get(charge_level, 90))

    feet_x = int(pose["x"] + (pose["w"] // 2) - (glow_size // 2))
    feet_y = int(pose["y"] + pose["h"] - (glow_size // 3))
    surface.blit(glow, (feet_x, feet_y))


def weapon_overlay_decorator(draw_fn):
    def wrapped():
        pose = draw_fn()
        if pose is None:
            return None
        if pipe_entry_active:
            return pose
        if game_started and not game_over and high_jump_powerup_charges > 0:
            draw_high_jump_powerup_effect(pose)
        if game_started and not game_over and weapon_powerup_ready and (boss_state is None or boss_state.get("form") != "ReuzenCoyote"):
            draw_equipped_weapon_on_character(pose)
        return pose
    return wrapped


@weapon_overlay_decorator
def draw_main_character():
    if flight_mode:
        plane_x, plane_y, plane_w, plane_h = get_flight_plane_rect()
        plane_frames = get_plane_frames_for_character(get_current_character_key())
        if plane_frames:
            frame_idx = int(millis() / 120) % len(plane_frames)
            plane_frame = plane_frames[frame_idx]
            image(plane_frame, plane_x, plane_y, plane_w, plane_h)
        else:
            image(AIRPLANE_IMG, plane_x, plane_y, plane_w, plane_h)
        if isDebugMode:
            no_fill()
            stroke(255, 0, 0)
            stroke_weight(2)
            rect(plane_x, plane_y, plane_w, plane_h)
            no_stroke()
        return None

    if pipe_entry_active:
        pose = get_pipe_entry_pose()
        if pose is not None:
            draw_x, draw_y, draw_w, draw_h = pose
            pipe_crouch_sprite = get_pipe_crouch_sprite(get_current_character_key())
            image(pipe_crouch_sprite, draw_x, draw_y, draw_w, draw_h)
            if isDebugMode:
                no_fill()
                stroke(255, 0, 0)
                stroke_weight(2)
                pipe_rect = get_pre_boss_entrance_rect(pipe_entry_level)
                rect(*pipe_rect)
                no_stroke()
            return {
                "x": draw_x,
                "y": draw_y,
                "w": draw_w,
                "h": draw_h,
                "ducking": True,
            }

    dino_h = DUCK_H if (is_ducking and on_ground and not game_over) else DINO_H
    dino_y_draw = get_dino_draw_y()
    character = CHARACTER_CONFIG[get_current_character_key()]
    draw_x = int(get_player_x())
    draw_w = DINO_W
    draw_h = dino_h
    if game_over:
        dino_sprite = character["oops"]
        current_character_key = get_current_character_key()
        if current_character_key == "dino":
            dino_sprite = DINO_FALL_IMG
            draw_x -= 8
            draw_w = 84
            draw_h = 44
            dino_y_draw = GROUND_Y - draw_h
        elif current_character_key == "cowboy":
            # Cowboy falls backward and lies on the ground.
            draw_x -= 10
            draw_w = 88
            draw_h = 40
            dino_y_draw = GROUND_Y - draw_h
        elif current_character_key == "roadrunner":
            dino_sprite = ROADRUNNER_FALL_IMG
            draw_x -= 6
            draw_w = 86
            draw_h = 42
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


if __name__ == "__main__" or IS_WEB:
    try:
        run()
    except KeyboardInterrupt:
        try:
            pygame.quit()
        except Exception as exc:
            log_soft_exception(
                "Failed to quit pygame after KeyboardInterrupt",
                exc,
                once_key="pygame_quit_keyboard_interrupt",
            )
