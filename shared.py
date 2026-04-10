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
def handle_common_keys(key, key_code, info_text=None, music_toggle_callback=None, quit_callback=None):
    global show_info, sound_enabled, music_enabled
    if key == 'i':
        show_info = not show_info
    elif key == 'q' or key_code == 27:  # 27 = ESC
        if quit_callback:
            quit_callback()
        else:
            exit()
    elif key == 's':
        music_enabled = not music_enabled
        if music_toggle_callback:
            music_toggle_callback(music_enabled)

# --- Info scherm tekenen ---
def draw_info_screen(info_text):
    background(245)
    fill(0)
    text_size(28)
    text("Dit spel ondersteunt de volgende toetsen", 80, 120)
    text_size(22)
    y = 180
    for line in info_text:
        text(line, 120, y)
        y += 40
    text_size(18)
    text("Druk op i om terug te keren.", 120, y+20)

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
