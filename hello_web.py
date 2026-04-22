from processing import background, fill, frame_rate, run, size, text, text_size


def setup():
    size(640, 360)
    frame_rate(30)


def draw():
    background(32, 40, 58)
    fill(245, 248, 255)
    text_size(36)
    text("Hello WebAssembly", 40, 120)
    text_size(20)
    text("processing + pygbag test", 40, 165)


run()
