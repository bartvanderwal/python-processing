from processing import run
from processing import *

x = 0


def setup():
    size(800, 500)
    text_size(40)
    background(128)
    text("hello world", 10, 10)

def draw():
    rect(100, 100, 100, 200)

run()
