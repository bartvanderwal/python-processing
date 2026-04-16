from processing import *

x = 0


def setup():
    size(800, 500)
    frame_rate(60)
    title("My First Sketch")


def draw():
    global x
    background(245)
    fill(80, 170, 255)
    no_stroke()
    circle(x, 250, 40)
    x = (x + 2) % width


run()