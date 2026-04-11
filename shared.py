"""
shared.py - Gedeelde functionaliteit voor input, info, quit, en geluid/muziek
"""
from processing import *

# --- Sound/Music State ---
sound_enabled = True
music_enabled = True

# --- Info scherm ---
show_info = False

# --- Key handling ---
def handle_common_keys(
    key,
    key_code,
    info_text=None,
    music_toggle_callback=None,
    sound_toggle_callback=None,
    quit_callback=None,
    allow_quit=True
):
    global show_info, sound_enabled, music_enabled
    if key == 'i':
        show_info = not show_info
    elif allow_quit and (key == 'q' or key_code == 27):  # 27 = ESC
        if quit_callback:
            quit_callback()
        else:
            exit()
    elif key == 'm':
        music_enabled = not music_enabled
        if music_toggle_callback:
            music_toggle_callback(music_enabled)
    elif key == 's':
        sound_enabled = not sound_enabled
        if sound_toggle_callback:
            sound_toggle_callback(sound_enabled)

# --- Info scherm tekenen ---
def draw_info_screen(info_text):
    background(245)
    fill(18)
    text_size(28)
    text("Controls Guide", 90, 90)
    text_size(18)
    y = 140
    for line in info_text:
        if "->" in line:
            key_txt, action_txt = [part.strip() for part in line.split("->", 1)]
            fill(30, 30, 30)
            text(key_txt, 110, y)
            fill(70, 70, 70)
            text("->", 210, y)
            fill(20, 20, 20)
            text(action_txt, 250, y)
        else:
            fill(20, 20, 20)
            text(line, 110, y)
        y += 32
    text_size(18)
    fill(30, 30, 30)
    text(f"Music: {'on' if music_enabled else 'off'}", 110, y + 24)
    text(f"SFX: {'on' if sound_enabled else 'off'}", 280, y + 24)
    text("Press i to return.", 110, y + 56)

# --- Speaker icoon tekenen ---
def draw_speaker_icon(x, y, enabled=True):
    # Simpel speaker icoon
    fill(60)
    rect(x, y+8, 8, 16)
    triangle(x+8, y+8, x+20, y, x+20, y+32)
    if not enabled:
        stroke(255,0,0)
        stroke_weight(4)
        line(x+4, y+4, x+24, y+28)
        no_stroke()

# --- Geluid afspelen ---
def play_sound(path):
    if sound_enabled:
        try:
            sound = load_sound(path)
            sound.play()
        except Exception:
            pass

# --- Muziek afspelen ---
def play_music(path):
    if music_enabled:
        try:
            music = load_sound(path)
            music.loop()
        except Exception:
            pass

def stop_music():
    # Vereist dat je een referentie naar het muziek-object bewaart in je sketch
    pass
