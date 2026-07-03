"""
Generates an upgraded ground tileset (32x32 tiles, 8 cols x 5 rows = 40 tiles).
Richer grass texture (4 shades + speckle + tiny blades), cobblestone paths
(rounded stones with grout, not a flat fill), smoother corners, a proper stone
plaza floor, six flower colors, bush, rocks, mushrooms, fences, dirt, bridge
and water — everything a Stardew-style village needs to not look flat.

Tile index map (1-based gid, row-major, 8 cols):
 1 grass_a        2 grass_b        3 grass_c        4 grass_d(dark patch)
 5 grass_light    6 path           7 path_edge_n    8 path_edge_s
 9 path_edge_w   10 path_edge_e   11 path_corner_nw 12 path_corner_ne
13 path_corner_sw 14 path_corner_se 15 stone_floor   16 cobble_floor
17 flower_red    18 flower_purple 19 flower_yellow  20 flower_white
21 flower_blue   22 flower_orange 23 flower_pink    24 bush
25 fence_h       26 fence_post    27 dirt_plain     28 bridge_plank
29 water         30 water_edge_n  31 rock_small     32 rock_cluster
33 mushroom_red  34 mushroom_brown 35 grass_tuft    36 dirt_path_worn
37 stepping_stone 38 sand         39 blank          40 blank
"""
from PIL import Image, ImageDraw
import random

random.seed(42)

TILE = 32
COLS = 8
ROWS = 5
img = Image.new("RGBA", (TILE * COLS, TILE * ROWS), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# ---- palette --------------------------------------------------------------
GRASS = (86, 168, 60, 255)
GRASS_HI = (108, 190, 78, 255)
GRASS_HI2 = (124, 204, 92, 255)
GRASS_LO = (66, 138, 44, 255)
GRASS_LO2 = (52, 116, 36, 255)
GRASS_DARK_PATCH = (58, 124, 40, 255)
GRASS_LIGHT_PATCH = (128, 206, 92, 255)

PATH = (206, 172, 118, 255)
PATH_HI = (222, 188, 132, 255)
PATH_LO = (182, 148, 98, 255)
GROUT = (150, 118, 78, 255)

STONE = (176, 176, 180, 255)
STONE_HI = (196, 196, 200, 255)
STONE_LO = (150, 150, 154, 255)


def cell(idx):
    c = idx % COLS
    r = idx // COLS
    return c * TILE, r * TILE, c * TILE + TILE, r * TILE + TILE


def speckle(box, base, variants, count=26):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=base)
    for _ in range(count):
        px = random.randint(x0, x1 - 1)
        py = random.randint(y0, y1 - 1)
        draw.point((px, py), fill=random.choice(variants))


def grass_blades(box, n=6, dark=False):
    x0, y0, x1, y1 = box
    col = GRASS_LO2 if dark else GRASS_HI2
    for _ in range(n):
        px = random.randint(x0 + 2, x1 - 3)
        py = random.randint(y0 + 6, y1 - 3)
        draw.line((px, py, px, py - random.randint(2, 4)), fill=col, width=1)


def grass_fill(box, blades=5):
    speckle(box, GRASS, [GRASS_HI, GRASS_LO, GRASS_HI2], 24)
    grass_blades(box, blades)


def path_fill(box):
    speckle(box, PATH, [PATH_HI, PATH_LO], 18)


def cobble_fill(box):
    """Rounded cobblestones with grout lines — used for the plaza + main roads."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=GROUT)
    stone_w = 10
    row = 0
    y = y0
    while y < y1:
        offset = 0 if row % 2 == 0 else stone_w // 2
        x = x0 - offset
        while x < x1:
            shade = random.choice([STONE, STONE_HI, STONE_LO])
            draw.rounded_rectangle((x + 1, y + 1, x + stone_w - 2, y + 8), radius=3, fill=shade)
            x += stone_w
        y += 9
        row += 1


# 0-4: grass variants -------------------------------------------------------
grass_fill(cell(0), 5)
grass_fill(cell(1), 4)
speckle(cell(2), GRASS, [GRASS_HI2], 12)
grass_blades(cell(2), 8)

b = cell(3)  # dark patch
speckle(b, GRASS_DARK_PATCH, [GRASS_LO2, GRASS_LO], 22)
grass_blades(b, 4, dark=True)

b = cell(4)  # light patch (sunlit)
speckle(b, GRASS_LIGHT_PATCH, [GRASS_HI2, GRASS_HI], 20)
grass_blades(b, 6)

# 5: cobblestone road tile
cobble_fill(cell(5))

# 6-7: path straight edges (grass/cobble split)
b = cell(6)  # north edge: grass top, path bottom
grass_fill(b)
cobble_fill((b[0], b[1] + TILE // 2, b[2], b[3]))
b = cell(7)  # south edge: path top, grass bottom
cobble_fill((b[0], b[1], b[2], b[1] + TILE // 2))
grass_fill((b[0], b[1] + TILE // 2, b[2], b[3]))

# 8-9: west/east edges
b = cell(8)
grass_fill(b)
cobble_fill((b[0] + TILE // 2, b[1], b[2], b[3]))
b = cell(9)
cobble_fill((b[0], b[1], b[0] + TILE // 2, b[3]))
grass_fill((b[0] + TILE // 2, b[1], b[2], b[3]))


# 10-13: path corners (quarter-circle grass cut into cobble tile)
def corner(idx, grass_quadrant):
    b = cell(idx)
    x0, y0, x1, y1 = b
    cobble_fill(b)
    cx = x0 if "w" in grass_quadrant else x1
    cy = y0 if "n" in grass_quadrant else y1
    r = TILE
    mask = Image.new("L", (TILE, TILE), 0)
    md = ImageDraw.Draw(mask)
    bbox = (cx - r - x0, cy - r - y0, cx + r - x0, cy + r - y0)
    md.ellipse(bbox, fill=255)
    grass_tile = Image.new("RGBA", (TILE, TILE), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grass_tile)
    for _ in range(24):
        px = random.randint(0, TILE - 1)
        py = random.randint(0, TILE - 1)
        gd.point((px, py), fill=random.choice([GRASS, GRASS_HI, GRASS_LO]))
    gd.rectangle((0, 0, TILE, TILE), fill=GRASS)
    for _ in range(18):
        px = random.randint(0, TILE - 1)
        py = random.randint(0, TILE - 1)
        gd.point((px, py), fill=random.choice([GRASS_HI, GRASS_LO]))
    img.paste(grass_tile, (x0, y0), mask)


corner(10, "nw")
corner(11, "ne")
corner(12, "sw")
corner(13, "se")

# 14: stone plaza floor (large tile, seams)
b = cell(14)
speckle(b, STONE, [STONE_HI, STONE_LO], 20)
draw.line((b[0], b[1], b[2], b[1]), fill=STONE_LO)
draw.line((b[0], b[1], b[0], b[3]), fill=STONE_LO)
draw.line((b[0] + TILE // 2, b[1], b[0] + TILE // 2, b[3]), fill=STONE_LO, width=1)
draw.line((b[0], b[1] + TILE // 2, b[2], b[1] + TILE // 2), fill=STONE_LO, width=1)

# 15: cobble plaza floor
cobble_fill(cell(15))

# 16-22: flowers, 6 colors on grass base ------------------------------------
def flower_tile(idx, petal, center=(255, 240, 200, 255)):
    b = cell(idx)
    grass_fill(b, 3)
    for _ in range(7):
        px = random.randint(b[0] + 3, b[2] - 5)
        py = random.randint(b[1] + 3, b[3] - 5)
        draw.ellipse((px - 1, py, px + 1, py + 3), fill=(60, 120, 40, 255))  # stem
        draw.ellipse((px, py - 2, px + 4, py + 2), fill=petal)
        draw.point((px + 2, py), fill=center)


flower_tile(16, (224, 84, 84, 255))
flower_tile(17, (150, 96, 214, 255))
flower_tile(18, (232, 196, 64, 255))
flower_tile(19, (245, 245, 245, 255), center=(255, 214, 120, 255))
flower_tile(20, (92, 142, 226, 255))
flower_tile(21, (232, 142, 54, 255))

# 23: extra pink flower tile
flower_tile(22, (236, 132, 176, 255))

# 24: bush
b = cell(24)
grass_fill(b, 2)
cx, cy = (b[0] + b[2]) // 2, (b[1] + b[3]) // 2 + 3
draw.ellipse((cx - 13, cy - 11, cx + 13, cy + 11), fill=(42, 104, 42, 255))
draw.ellipse((cx - 9, cy - 15, cx + 9, cy - 1), fill=(54, 126, 50, 255))
draw.ellipse((cx - 4, cy - 17, cx + 6, cy - 7), fill=(70, 146, 64, 255))
for _ in range(10):
    px = random.randint(cx - 10, cx + 10)
    py = random.randint(cy - 10, cy + 8)
    draw.point((px, py), fill=(78, 154, 70, 255))
draw.ellipse((cx - 3, cy + 6, cx + 3, cy + 10), fill=(0, 0, 0, 40))

# 25: fence horizontal rail
b = cell(25)
x0, y0, x1, y1 = b
draw.rectangle((x0 + 3, y0 + 5, x0 + 7, y1 - 1), fill=(118, 82, 46, 255))
draw.rectangle((x1 - 7, y0 + 5, x1 - 3, y1 - 1), fill=(118, 82, 46, 255))
draw.rectangle((x0, y0 + 10, x1, y0 + 14), fill=(138, 98, 56, 255))
draw.rectangle((x0, y0 + 18, x1, y0 + 22), fill=(138, 98, 56, 255))
draw.line((x0, y0 + 10, x1, y0 + 10), fill=(158, 116, 68, 255))

# 26: fence post
b = cell(26)
draw.rectangle((b[0] + 12, b[1] + 4, b[0] + 20, b[3] - 1), fill=(120, 84, 48, 255))
draw.rectangle((b[0] + 12, b[1] + 4, b[0] + 20, b[1] + 8), fill=(148, 108, 62, 255))

# 27: dirt
speckle(cell(27), (176, 140, 92, 255), [(190, 154, 104, 255), (158, 124, 78, 255)], 24)

# 28: bridge plank
b = cell(28)
draw.rectangle(b, fill=(150, 108, 66, 255))
for gx in range(b[0], b[2], 6):
    draw.line((gx, b[1], gx, b[3]), fill=(126, 90, 54, 255), width=1)
draw.rectangle((b[0], b[1], b[2], b[1] + 2), fill=(170, 126, 80, 255))
draw.rectangle((b[0], b[3] - 2, b[2], b[3]), fill=(170, 126, 80, 255))

# 29: water
b = cell(29)
speckle(b, (72, 138, 198, 255), [(92, 158, 214, 255), (56, 118, 176, 255)], 20)
for _ in range(3):
    y = random.randint(b[1] + 4, b[3] - 4)
    draw.line((b[0] + 3, y, b[2] - 3, y), fill=(160, 208, 236, 150), width=1)

# 30: water edge (grass -> water)
b = cell(30)
grass_fill((b[0], b[1], b[2], b[1] + TILE // 3))
speckle((b[0], b[1] + TILE // 3, b[2], b[3]), (72, 138, 198, 255), [(92, 158, 214, 255)], 12)

# 31: small rock
b = cell(31)
grass_fill(b, 2)
cx, cy = (b[0] + b[2]) // 2, (b[1] + b[3]) // 2 + 4
draw.ellipse((cx - 6, cy + 2, cx + 6, cy + 6), fill=(0, 0, 0, 50))
draw.polygon([(cx - 7, cy + 3), (cx - 3, cy - 6), (cx + 4, cy - 5), (cx + 7, cy + 2), (cx, cy + 4)], fill=(140, 140, 146, 255))
draw.polygon([(cx - 3, cy - 6), (cx + 1, cy - 5), (cx - 1, cy), (cx - 4, cy + 1)], fill=(168, 168, 174, 255))

# 32: rock cluster
b = cell(32)
grass_fill(b, 2)
cx, cy = (b[0] + b[2]) // 2, (b[1] + b[3]) // 2 + 3
for dx, dy, r in [(-6, 2, 6), (5, 3, 5), (0, -2, 5)]:
    draw.ellipse((cx + dx - r, cy + dy + 3, cx + dx + r, cy + dy + 6), fill=(0, 0, 0, 40))
    draw.polygon([(cx + dx - r, cy + dy + 2), (cx + dx - 2, cy + dy - r), (cx + dx + r, cy + dy + 1), (cx + dx + 1, cy + dy + 3)],
                 fill=(146, 146, 152, 255))

# 33: red mushroom
b = cell(33)
grass_fill(b, 2)
cx, cy = (b[0] + b[2]) // 2, (b[1] + b[3]) // 2 + 5
draw.rectangle((cx - 2, cy - 2, cx + 2, cy + 5), fill=(238, 232, 214, 255))
draw.ellipse((cx - 7, cy - 10, cx + 7, cy - 1), fill=(214, 64, 64, 255))
for px, py in [(cx - 3, cy - 7), (cx + 2, cy - 8), (cx, cy - 4)]:
    draw.ellipse((px - 1, py - 1, px + 1, py + 1), fill=(255, 255, 255, 255))

# 34: brown mushroom cluster
b = cell(34)
grass_fill(b, 2)
cx, cy = (b[0] + b[2]) // 2, (b[1] + b[3]) // 2 + 5
for ox, s in [(-4, 5), (3, 6), (0, 4)]:
    draw.rectangle((cx + ox - 1, cy - 1, cx + ox + 1, cy + 4), fill=(224, 214, 192, 255))
    draw.ellipse((cx + ox - s, cy - s, cx + ox + s, cy + 1), fill=(150, 104, 66, 255))

# 35: grass tuft
b = cell(35)
grass_fill(b, 2)
cx, cy = (b[0] + b[2]) // 2, (b[1] + b[3]) // 2 + 6
for i in range(7):
    px = cx - 6 + i * 2
    h = random.randint(6, 11)
    col = random.choice([GRASS_HI2, GRASS_HI, (90, 172, 62, 255)])
    draw.line((px, cy, px + random.randint(-2, 2), cy - h), fill=col, width=1)

# 36: worn dirt path (foot-worn shortcut look)
b = cell(36)
speckle(b, (188, 156, 106, 255), [(202, 170, 118, 255), (168, 138, 92, 255)], 22)
for _ in range(6):
    px = random.randint(b[0], b[2] - 2)
    py = random.randint(b[1], b[3] - 2)
    draw.point((px, py), fill=(150, 120, 78, 255))

# 37: stepping stone (single, on grass)
b = cell(37)
grass_fill(b, 3)
cx, cy = (b[0] + b[2]) // 2, (b[1] + b[3]) // 2
draw.ellipse((cx - 9, cy - 6, cx + 9, cy + 8), fill=(0, 0, 0, 40))
draw.ellipse((cx - 10, cy - 8, cx + 10, cy + 6), fill=(178, 178, 182, 255))
draw.ellipse((cx - 8, cy - 7, cx + 4, cy + 2), fill=(196, 196, 200, 255))

# 38: sand (fountain surrounds / decorative)
speckle(cell(38), (224, 202, 154, 255), [(236, 214, 166, 255), (208, 186, 138, 255)], 20)

# 39: blank (kept empty)

img.save("/home/claude/portfolio-town/public/assets/tilesets/town_tileset.png")
print("tileset written", img.size)
