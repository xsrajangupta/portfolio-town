"""
Generates public/assets/buildings/building_parts.png + .json — modular,
near-greyscale, TINTABLE parts. Wall/roof/door/window *style* variants let
each building (built from the same shared sheet + a per-building tint color
from tools/gen_map.py) read as genuinely different architecture, read at
runtime by src/objects/Building.js.

Frames (variable size, packed left-to-right, read by name via JSON atlas):
  wall_brick, wall_wood, wall_stone, wall_panel
  roof_gable, roof_hip, roof_dome, roof_tower
  door, door_arch, window, window_round, window_arch
  sign, chimney, flag, trim, corner_post, base_border
"""
from PIL import Image, ImageDraw
import json
import random

tiles = []


def add(name, size, drawer):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    drawer(d, size, im)
    tiles.append((name, im))


def _shade_gradient(im, w, h, max_alpha):
    """Subtle left-to-right darkening overlay. Drawn on a separate transparent
    layer and alpha-composited on top, so it shades the wall instead of
    overwriting (and destroying) the base texture's opacity."""
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for x in range(w):
        od.line((x, 0, x, h), fill=(0, 0, 0, int(max_alpha * (x / w))))
    im.alpha_composite(overlay)


# ------------------------------------------------------------- WALLS -------
def wall_brick(d, size, im):
    w, h = size
    base, mortar, shade = (238, 238, 238, 255), (206, 206, 206, 255), (222, 222, 222, 255)
    d.rectangle((0, 0, w, h), fill=base)
    brick_h, brick_w, row, y = 12, 24, 0, 0
    while y < h:
        offset = 0 if row % 2 == 0 else brick_w // 2
        x = -offset
        while x < w:
            d.rectangle((x, y, x + brick_w - 2, y + brick_h - 2), fill=base if (row + x) % 3 else shade)
            x += brick_w
        d.line((0, y + brick_h - 1, w, y + brick_h - 1), fill=mortar, width=1)
        y += brick_h
        row += 1
    _shade_gradient(im, w, h, 20)


def wall_wood(d, size, im):
    w, h = size
    plank_w = 12
    cols = [(236, 226, 206, 255), (226, 214, 192, 255), (216, 204, 180, 255)]
    for i, x in enumerate(range(0, w, plank_w)):
        d.rectangle((x, 0, x + plank_w - 2, h), fill=cols[i % len(cols)])
        d.line((x, 0, x, h), fill=(190, 176, 150, 255))
    for y in range(6, h, 14):
        d.line((0, y, w, y), fill=(200, 186, 160, 255), width=1)
    _shade_gradient(im, w, h, 16)


def wall_stone(d, size, im):
    w, h = size
    d.rectangle((0, 0, w, h), fill=(232, 232, 230, 255))
    random.seed(hash((w, h, "stone")) & 0xffff)
    y, row = 0, 0
    while y < h:
        rh = 14
        offset = 0 if row % 2 == 0 else 8
        cx = -offset
        while cx < w:
            sw = 18
            shade = 220 - (hash((cx, y)) % 20)
            d.rounded_rectangle((cx, y, cx + sw - 2, y + rh - 2), radius=2, fill=(shade, shade, shade, 255))
            cx += sw
        y += rh
        row += 1
    _shade_gradient(im, w, h, 18)


def wall_panel(d, size, im):
    """Smooth rendered/stucco panel wall with recessed rectangle detailing —
    used for modern-feeling buildings (Projects, Contact)."""
    w, h = size
    d.rectangle((0, 0, w, h), fill=(236, 236, 236, 255))
    pad = 8
    panel_w = (w - pad * 3) // 2
    panel_h = h - pad * 2
    for i in range(2):
        x0 = pad + i * (panel_w + pad)
        d.rounded_rectangle((x0, pad, x0 + panel_w, pad + panel_h), radius=3, fill=(224, 224, 224, 255),
                             outline=(206, 206, 206, 255))
    _shade_gradient(im, w, h, 14)
    d.line((0, 0, w, 0), fill=(255, 255, 255, 90))


# ------------------------------------------------------------- ROOFS -------
def _clip_to_poly(d, im, size, poly, band_drawer):
    w, h = size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    band_drawer(ImageDraw.Draw(overlay))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    alpha = Image.composite(overlay, Image.new("RGBA", (w, h), (0, 0, 0, 0)), mask).split()[3]
    im.paste(overlay, (0, 0), alpha)


def roof_gable(d, size, im):
    w, h = size
    poly = [(0, h), (w / 2, 0), (w, h)]
    d.polygon(poly, fill=(236, 236, 236, 255))

    def bands(od):
        y, row = h, 0
        while y > 4:
            col = (206, 206, 206, 255) if row % 2 == 0 else (188, 188, 188, 255)
            od.rectangle((0, y - 2, w, y - 1), fill=col)
            y -= 7
            row += 1
    _clip_to_poly(d, im, size, poly, bands)
    d.line((w / 2 - 1, 2, w / 2 - 1, h), fill=(255, 255, 255, 90), width=2)


def roof_hip(d, size, im):
    w, h = size
    poly = [(6, h), (w * 0.28, h * 0.18), (w * 0.72, h * 0.18), (w - 6, h)]
    d.polygon(poly, fill=(232, 232, 232, 255))

    def bands(od):
        y, row = h, 0
        while y > h * 0.16:
            col = (202, 202, 202, 255) if row % 2 == 0 else (184, 184, 184, 255)
            od.rectangle((0, y - 2, w, y - 1), fill=col)
            y -= 6
            row += 1
    _clip_to_poly(d, im, size, poly, bands)
    d.line((w * 0.28, h * 0.18, w * 0.72, h * 0.18), fill=(255, 255, 255, 110), width=2)


def roof_dome(d, size, im):
    w, h = size
    d.pieslice((0, -h * 0.15, w, h * 1.85), 180, 360, fill=(234, 234, 234, 255))
    for i in range(3):
        yy = h * (0.25 + i * 0.22)
        d.arc((w * 0.08, -h * 0.15 + yy * 0.15, w * 0.92, h * 1.7), 200, 340, fill=(200, 200, 200, 255), width=2)
    d.ellipse((w / 2 - 3, 0, w / 2 + 3, 8), fill=(255, 214, 92, 255))  # small finial


def roof_tower(d, size, im):
    w, h = size
    poly = [(w * 0.32, h), (w / 2, 0), (w * 0.68, h)]
    d.polygon(poly, fill=(230, 230, 230, 255))

    def bands(od):
        y, row = h, 0
        while y > 4:
            col = (198, 198, 198, 255) if row % 2 == 0 else (180, 180, 180, 255)
            od.rectangle((0, y - 2, w, y - 1), fill=col)
            y -= 6
            row += 1
    _clip_to_poly(d, im, size, poly, bands)
    d.line((w / 2 - 1, 2, w / 2 - 1, h), fill=(255, 255, 255, 100), width=2)


# ------------------------------------------------------------ ACCENTS ------
def door(d, size, im):
    w, h = size
    frame, panel, panel_shade = (222, 222, 222, 255), (196, 196, 196, 255), (178, 178, 178, 255)
    d.rectangle((0, h * 0.28, w, h), fill=frame)
    d.pieslice((0, 0, w, h * 0.56), 180, 360, fill=frame)
    inset = 3
    d.rectangle((inset, h * 0.34, w - inset, h - inset), fill=panel)
    d.pieslice((inset, inset, w - inset, h * 0.5), 180, 360, fill=panel)
    d.line((w * 0.5, h * 0.32, w * 0.5, h - inset), fill=panel_shade, width=1)
    d.rectangle((inset + 2, h * 0.55, w - inset - 2, h * 0.6), outline=panel_shade)
    d.ellipse((w - 9, h * 0.58, w - 5, h * 0.58 + 4), fill=(255, 221, 140, 255))


def door_arch(d, size, im):
    """Tall arched double-panel door — used for grand / formal buildings."""
    w, h = size
    frame, panel, panel_shade = (224, 224, 224, 255), (198, 198, 198, 255), (176, 176, 176, 255)
    d.rectangle((0, h * 0.2, w, h), fill=frame)
    d.pieslice((0, -h * 0.05, w, h * 0.45), 180, 360, fill=frame)
    inset = 2
    d.rectangle((inset, h * 0.26, w - inset, h - inset), fill=panel)
    d.pieslice((inset, h * 0.01, w - inset, h * 0.4), 180, 360, fill=panel)
    d.line((w * 0.5, h * 0.02, w * 0.5, h - inset), fill=panel_shade, width=1)
    for fy in (0.4, 0.55, 0.7, 0.85):
        d.rectangle((inset + 2, h * fy, w - inset - 2, h * fy + 2), fill=panel_shade)
    d.ellipse((w - 8, h * 0.5, w - 4, h * 0.5 + 4), fill=(255, 221, 140, 255))


def window(d, size, im):
    w, h = size
    frame, sill = (232, 232, 232, 255), (210, 210, 210, 255)
    glass_top, glass_bot = (196, 226, 236, 255), (150, 196, 214, 255)
    d.rounded_rectangle((0, 0, w, h * 0.86), radius=2, fill=frame)
    for i in range(int(h * 0.7)):
        t = i / (h * 0.7)
        col = tuple(int(glass_top[c] + (glass_bot[c] - glass_top[c]) * t) for c in range(3)) + (255,)
        d.line((2, 2 + i, w - 2, 2 + i), fill=col)
    d.line((w / 2, 2, w / 2, h * 0.84), fill=frame, width=2)
    d.line((2, h * 0.44, w - 2, h * 0.44), fill=frame, width=2)
    d.rectangle((-1, h * 0.86, w + 1, h), fill=sill)
    d.line((4, 4, 8, h * 0.3), fill=(255, 255, 255, 140), width=1)


def window_round(d, size, im):
    """Circular porthole window — used for research/nautical-feel buildings."""
    w, h = size
    frame = (232, 232, 232, 255)
    glass_top, glass_bot = (196, 226, 236, 255), (140, 190, 210, 255)
    d.ellipse((0, 0, w, h), fill=frame)
    for i in range(h):
        t = i / h
        col = tuple(int(glass_top[c] + (glass_bot[c] - glass_top[c]) * t) for c in range(3)) + (255,)
        d.ellipse((2, 2, w - 2, h - 2), outline=None)
        d.line((3, i, w - 3, i), fill=col)
    d.ellipse((2, 2, w - 2, h - 2), outline=(210, 210, 210, 255), width=1)
    d.line((w * 0.3, h * 0.25, w * 0.5, h * 0.5), fill=(255, 255, 255, 160), width=1)


def window_arch(d, size, im):
    """Arched cathedral-style window — used for grand / research buildings."""
    w, h = size
    frame, sill = (232, 232, 232, 255), (210, 210, 210, 255)
    glass_top, glass_bot = (200, 228, 236, 255), (150, 196, 214, 255)
    d.pieslice((0, 0, w, h * 0.7), 180, 360, fill=frame)
    d.rectangle((0, h * 0.34, w, h * 0.86), fill=frame)
    for i in range(int(h * 0.55)):
        t = i / (h * 0.55)
        col = tuple(int(glass_top[c] + (glass_bot[c] - glass_top[c]) * t) for c in range(3)) + (255,)
        d.line((2, 2 + i, w - 2, 2 + i), fill=col)
    d.line((w / 2, 2, w / 2, h * 0.84), fill=frame, width=1)
    d.rectangle((-1, h * 0.86, w + 1, h), fill=sill)


def sign(d, size, im):
    w, h = size
    plank, grain = (232, 232, 232, 255), (214, 214, 214, 255)
    d.rounded_rectangle((0, 0, w, h), radius=5, fill=plank)
    for gy in range(4, h - 3, 5):
        d.line((5, gy, w - 5, gy), fill=grain, width=1)
    d.rounded_rectangle((2, 2, w - 2, h - 2), radius=4, outline=(200, 200, 200, 255))
    d.ellipse((6, 1, 10, 5), fill=(180, 180, 180, 255))
    d.ellipse((w - 10, 1, w - 6, 5), fill=(180, 180, 180, 255))


def chimney(d, size, im):
    w, h = size
    d.rectangle((0, 0, w, h), fill=(224, 224, 224, 255))
    for y in range(0, h, 6):
        d.line((0, y, w, y), fill=(200, 200, 200, 255))
    d.rectangle((-2, 0, w + 2, 4), fill=(200, 200, 200, 255))


def flag(d, size, im):
    w, h = size
    d.rectangle((0, 0, 2, h), fill=(210, 210, 210, 255))
    d.polygon([(2, 2), (w, h * 0.3), (2, h * 0.55)], fill=(235, 235, 235, 255))


def trim(d, size, im):
    """Thin decorative accent strip run along a wall edge (tinted to the
    building's secondary accent color at runtime, e.g. gold on purple)."""
    w, h = size
    d.rectangle((0, 0, w, h), fill=(240, 240, 240, 255))
    for x in range(0, w, 8):
        d.rectangle((x, 0, x + 4, h), fill=(220, 220, 220, 255))


def corner_post(d, size, im):
    w, h = size
    d.rectangle((0, 0, w, h), fill=(226, 226, 226, 255))
    for y in range(0, h, 10):
        d.rectangle((0, y, w, y + 5), fill=(210, 210, 210, 255))
    d.line((0, 0, 0, h), fill=(255, 255, 255, 120))


def base_border(d, size, im):
    """Low decorative stone footing that runs along the base of a wall."""
    w, h = size
    d.rectangle((0, 0, w, h), fill=(214, 214, 214, 255))
    x = 0
    while x < w:
        sw = 14
        d.rounded_rectangle((x + 1, 1, x + sw - 1, h - 1), radius=2, fill=(198, 198, 198, 255))
        x += sw
    d.line((0, 0, w, 0), fill=(240, 240, 240, 255))


add("wall_brick", (96, 96), wall_brick)
add("wall_wood", (96, 96), wall_wood)
add("wall_stone", (96, 96), wall_stone)
add("wall_panel", (96, 96), wall_panel)
add("roof_gable", (108, 60), roof_gable)
add("roof_hip", (108, 60), roof_hip)
add("roof_dome", (108, 60), roof_dome)
add("roof_tower", (108, 70), roof_tower)
add("door", (30, 42), door)
add("door_arch", (32, 46), door_arch)
add("window", (20, 20), window)
add("window_round", (18, 18), window_round)
add("window_arch", (20, 24), window_arch)
add("sign", (84, 26), sign)
add("chimney", (14, 26), chimney)
add("flag", (22, 26), flag)
add("trim", (96, 6), trim)
add("corner_post", (6, 90), corner_post)
add("base_border", (100, 10), base_border)

pad = 2
total_w = sum(im.width for _, im in tiles) + pad * (len(tiles) - 1)
max_h = max(im.height for _, im in tiles)
sheet = Image.new("RGBA", (total_w, max_h), (0, 0, 0, 0))
x = 0
frames = {}
for name, im in tiles:
    sheet.paste(im, (x, 0), im)
    frames[name] = {"x": x, "y": 0, "w": im.width, "h": im.height}
    x += im.width + pad

sheet.save("/home/claude/portfolio-town/public/assets/buildings/building_parts.png")
with open("/home/claude/portfolio-town/public/assets/buildings/building_parts.json", "w") as f:
    json.dump(frames, f, indent=2)

print("building parts written:", list(frames.keys()))
