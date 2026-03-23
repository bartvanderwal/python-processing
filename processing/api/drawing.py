from ..core.constants import CENTER, RIGHT, BOTTOM, BASELINE


def background(state, require_screen, *args):
    require_screen("background")
    if len(args) == 1:
        g = int(args[0])
        col = (g, g, g)
    elif len(args) == 3:
        col = tuple(int(v) for v in args)
    else:
        raise TypeError("background() takes 1 or 3 arguments")
    state["_screen"].fill(col)


def rect(state, require_screen, x, y, w, h):
    require_screen("rect")
    x, y, w, h = map(int, (x, y, w, h))
    if state["_fill_enabled"]:
        pygame = state["pygame"]
        pygame.draw.rect(state["_screen"], state["_fill_color"], (x, y, w, h), 0)
    if state["_stroke_enabled"]:
        pygame = state["pygame"]
        pygame.draw.rect(state["_screen"], state["_stroke_color"], (x, y, w, h), int(state["_stroke_weight"]))


def circle(state, require_screen, x, y, d):
    require_screen("circle")
    pygame = state["pygame"]
    x, y, d = int(x), int(y), int(d)
    radius = d // 2
    if state["_fill_enabled"]:
        pygame.draw.circle(state["_screen"], state["_fill_color"], (x, y), radius, 0)
    if state["_stroke_enabled"]:
        pygame.draw.circle(state["_screen"], state["_stroke_color"], (x, y), radius, int(state["_stroke_weight"]))


def point(state, require_screen, x, y):
    require_screen("point")
    x, y = int(x), int(y)
    if state["_stroke_enabled"]:
        state["_screen"].set_at((x, y), state["_stroke_color"])


def line(state, require_screen, apply_coords, x1, y1, x2, y2):
    require_screen("line")
    pygame = state["pygame"]
    pts = apply_coords((x1, y1, x2, y2))
    if state["_stroke_enabled"]:
        pygame.draw.line(state["_screen"], state["_stroke_color"], pts[:2], pts[2:], int(state["_stroke_weight"]))


def triangle(state, require_screen, apply_coords, x1, y1, x2, y2, x3, y3):
    require_screen("triangle")
    pygame = state["pygame"]
    pts = apply_coords((x1, y1, x2, y2, x3, y3))
    tri = [pts[0:2], pts[2:4], pts[4:6]]
    if state["_fill_enabled"]:
        pygame.draw.polygon(state["_screen"], state["_fill_color"], tri)
    if state["_stroke_enabled"]:
        pygame.draw.polygon(state["_screen"], state["_stroke_color"], tri, int(state["_stroke_weight"]))


def quad(state, require_screen, apply_coords, x1, y1, x2, y2, x3, y3, x4, y4):
    require_screen("quad")
    pygame = state["pygame"]
    pts = apply_coords((x1, y1, x2, y2, x3, y3, x4, y4))
    pts_list = [pts[i : i + 2] for i in range(0, 8, 2)]
    if state["_fill_enabled"]:
        pygame.draw.polygon(state["_screen"], state["_fill_color"], pts_list)
    if state["_stroke_enabled"]:
        pygame.draw.polygon(state["_screen"], state["_stroke_color"], pts_list, int(state["_stroke_weight"]))


def ellipse(state, require_screen, x, y, w, h):
    require_screen("ellipse")
    pygame = state["pygame"]
    x, y, w, h = map(int, (x, y, w, h))
    box = (x - w // 2, y - h // 2, w, h)
    if state["_fill_enabled"]:
        pygame.draw.ellipse(state["_screen"], state["_fill_color"], box, 0)
    if state["_stroke_enabled"]:
        pygame.draw.ellipse(state["_screen"], state["_stroke_color"], box, int(state["_stroke_weight"]))


def text(state, require_screen, ensure_font, txt, x, y):
    require_screen("text")
    ensure_font()
    surf = state["_font"].render(str(txt), True, state["_fill_color"] if state["_fill_enabled"] else state["_stroke_color"])
    x = int(x)
    y = int(y)

    if state["_text_align_x"] == CENTER:
        x -= surf.get_width() // 2
    elif state["_text_align_x"] == RIGHT:
        x -= surf.get_width()

    if state["_text_align_y"] == CENTER:
        y -= surf.get_height() // 2
    elif state["_text_align_y"] == BOTTOM:
        y -= surf.get_height()
    elif state["_text_align_y"] == BASELINE:
        y -= state["_font"].get_ascent()

    state["_screen"].blit(surf, (x, y))


def load_image(state, resolve_icon_path, path):
    pygame = state["pygame"]
    resolved = resolve_icon_path(str(path))
    return pygame.image.load(resolved)


def image(state, require_screen, apply_coords, resolve_icon_path, img, x, y, w=None, h=None):
    pygame = state["pygame"]
    require_screen("image")

    if isinstance(img, str):
        img = load_image(state, resolve_icon_path, img)

    if not isinstance(img, pygame.Surface):
        raise TypeError("image() expects a pygame Surface or a path string")

    x, y = apply_coords((x, y))

    if w is None and h is None:
        state["_screen"].blit(img, (x, y))
        return

    if w is None or h is None:
        raise TypeError("image() requires both w and h when scaling")

    w, h = apply_coords((w, h))
    if w <= 0 or h <= 0:
        raise ValueError("image() width and height must be > 0")

    img_for_scale = img
    if img_for_scale.get_bitsize() not in (24, 32):
        img_for_scale = img_for_scale.convert_alpha()

    scaled = pygame.transform.smoothscale(img_for_scale, (w, h))
    state["_screen"].blit(scaled, (x, y))


def arc(state, require_screen, apply_coords, x, y, w, h, start, stop):
    pygame = state["pygame"]
    require_screen("arc")
    rect = pygame.Rect(apply_coords((x - w / 2, y - h / 2, w, h)))
    if state["_stroke_enabled"]:
        pygame.draw.arc(state["_screen"], state["_stroke_color"], rect, float(start), float(stop), int(state["_stroke_weight"]))


def bezier(state, require_screen, apply_coords, x1, y1, x2, y2, x3, y3, x4, y4, segments=20):
    pygame = state["pygame"]
    require_screen("bezier")
    pts = apply_coords((x1, y1, x2, y2, x3, y3, x4, y4))
    path = []
    for i in range(segments + 1):
        t = i / segments
        x = ((1 - t) ** 3 * pts[0] + 3 * (1 - t) ** 2 * t * pts[2] + 3 * (1 - t) * t ** 2 * pts[4] + t ** 3 * pts[6])
        y = ((1 - t) ** 3 * pts[1] + 3 * (1 - t) ** 2 * t * pts[3] + 3 * (1 - t) * t ** 2 * pts[5] + t ** 3 * pts[7])
        path.append((int(x), int(y)))
    if state["_stroke_enabled"] and len(path) > 1:
        pygame.draw.lines(state["_screen"], state["_stroke_color"], False, path, int(state["_stroke_weight"]))
