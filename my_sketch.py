
from processing import *


x = 0
show_instructions = False

def setup():
    size(800, 500)
    frame_rate(60)
    title("My First Sketch")


def draw():

    global x, show_instructions
    background(245)
    if show_instructions:
        fill(0)
        text_size(28)
        text("Dit spel ondersteunt de volgende toetsen", 80, 120)
        text_size(22)
        text("i -> Instructies (dit scherm)", 120, 180)
        text("q -> Stoppen", 120, 220)
        text("esc (ape) -> Ook stoppen (standaard voor pygame)", 120, 260)
        text_size(18)
        text("Druk op i om terug te keren.", 120, 320)
        return

    fill(80, 170, 255)
    no_stroke()
    circle(x, 250, 40)
    x = (x + 2) % width


def key_pressed():
    global show_instructions
    if key == 'q' or key_code == 27:  # 27 = ESC
        exit()
    elif key == 'i':
        show_instructions = not show_instructions

run()