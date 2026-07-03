"""
Programmatically generates public/assets/maps/town.json (standard Tiled JSON).
Phaser only reads this — no tile is placed by hand in game code. Open it in
the real Tiled Map Editor later if you want to tweak visually; layer names and
object property schema are unchanged (with additive new layers for the
fountain + extra decor + tree variants).
"""
import json
import math
import random

random.seed(7)

TILE = 32
COLS = 56
ROWS = 44

# gids matching tools/gen_tileset.py order (8 cols x 5 rows, firstgid=1)
(GRASS_A, GRASS_B, GRASS_C, GRASS_DARK, GRASS_LIGHT, COBBLE, PATH_N, PATH_S,
 PATH_W, PATH_E, CORNER_NW, CORNER_NE, CORNER_SW, CORNER_SE, STONE_FLOOR,
 COBBLE_FLOOR, FLOWER_RED, FLOWER_PURPLE, FLOWER_YELLOW, FLOWER_WHITE,
 FLOWER_BLUE, FLOWER_ORANGE, FLOWER_PINK, BUSH, FENCE_H, FENCE_POST, DIRT,
 BRIDGE, WATER, WATER_EDGE, ROCK_SMALL, ROCK_CLUSTER, MUSHROOM_RED,
 MUSHROOM_BROWN, GRASS_TUFT, DIRT_WORN, STEPPING_STONE, SAND, BLANK1,
 BLANK2) = range(1, 41)

FLOWER_GIDS = [FLOWER_RED, FLOWER_PURPLE, FLOWER_YELLOW, FLOWER_WHITE, FLOWER_BLUE, FLOWER_ORANGE, FLOWER_PINK]


def idx(x, y):
    return y * COLS + x


def new_layer():
    return [0] * (COLS * ROWS)


def fill_rect(layer, x1, x2, y1, y2, gid):
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            if 0 <= x < COLS and 0 <= y < ROWS:
                layer[idx(x, y)] = gid


def set_tile(layer, x, y, gid):
    if 0 <= x < COLS and 0 <= y < ROWS:
        layer[idx(x, y)] = gid


def in_any_rect(x, y, rects, pad=1):
    for (x1, x2, y1, y2) in rects:
        if x1 - pad <= x <= x2 + pad and y1 - pad <= y <= y2 + pad:
            return True
    return False


# ---- Ground layer: richer grass mix with dark/light sunlight patches ------
ground = new_layer()
for y in range(ROWS):
    for x in range(COLS):
        r = random.random()
        if r < 0.60:
            gid = GRASS_A
        elif r < 0.80:
            gid = GRASS_B
        elif r < 0.90:
            gid = GRASS_C
        elif r < 0.95:
            gid = GRASS_DARK
        else:
            gid = GRASS_LIGHT
        ground[idx(x, y)] = gid

# ---- Plaza + fountain center ----------------------------------------------
PLAZA_CX, PLAZA_CY = 30, 21
PLAZA = (PLAZA_CX - 9, PLAZA_CX + 9, PLAZA_CY - 7, PLAZA_CY + 7)

paths = new_layer()
fill_rect(paths, *PLAZA, gid=COBBLE_FLOOR)
# ring of finer stone right around the fountain itself
fill_rect(paths, PLAZA_CX - 3, PLAZA_CX + 3, PLAZA_CY - 3, PLAZA_CY + 3, gid=STONE_FLOOR)

# ---- Spine: from spawn (south) up into the plaza ---------------------------
SPAWN_X, SPAWN_Y = PLAZA_CX, ROWS - 4
SPINE = (PLAZA_CX - 1, PLAZA_CX + 1, PLAZA[3], SPAWN_Y)
fill_rect(paths, *SPINE, gid=COBBLE)

# ---- Decorative pond + bridge (top-left corner, off the path network) ----
POND = (1, 6, 1, 3)
fill_rect(paths, *POND, gid=WATER)
BRIDGE_COL = 3
for y in range(POND[2], POND[3] + 1):
    set_tile(paths, BRIDGE_COL, y, BRIDGE)
fill_rect(paths, POND[0], POND[1], POND[2] - 1, POND[2] - 1, WATER_EDGE)

# ---- Buildings (object layer): 9, one per user-requested category --------
BUILDING_SIZE_PX = {"w": 260, "h": 210}


def tile_center_px(tx, ty):
    return tx * TILE, ty * TILE


buildings_def = [
    dict(key="projects", title="Projects", color="#17a2b8", accent="#2f3438", icon="folder",
         wallStyle="wall_panel", roofStyle="roof_hip", doorStyle="door_arch", windowStyle="window_round",
         windowCount=3, flag=True, tile=(30, 8), blurb="10 things I've built"),
    dict(key="education", title="Education", color="#1f4e9c", accent="#a9c6ff", icon="book",
         wallStyle="wall_brick", roofStyle="roof_gable", doorStyle="door", windowStyle="window_arch",
         windowCount=3, flag=False, tile=(40, 11), blurb="Degrees & coursework"),
    dict(key="skills", title="Skills", color="#d9822b", accent="#6b4423", icon="star",
         wallStyle="wall_wood", roofStyle="roof_dome", doorStyle="door", windowStyle="window",
         windowCount=2, flag=False, tile=(46, 19), blurb="Languages & tools"),
    dict(key="certifications", title="Certifications", color="#1f9d55", accent="#c9a227", icon="ribbon",
         wallStyle="wall_stone", roofStyle="roof_gable", doorStyle="door_arch", windowStyle="window",
         windowCount=3, flag=False, tile=(44, 28), blurb="Courses & credentials"),
    dict(key="contact", title="Contact", color="#e8edf2", accent="#2f6fb0", icon="mail",
         wallStyle="wall_panel", roofStyle="roof_hip", doorStyle="door", windowStyle="window",
         windowCount=2, flag=False, tile=(36, 33), blurb="Let's connect"),
    dict(key="about", title="About Me", color="#a83232", accent="#e0c9a6", icon="user",
         wallStyle="wall_brick", roofStyle="roof_hip", doorStyle="door", windowStyle="window",
         windowCount=2, flag=False, tile=(24, 33), blurb="Who I am"),
    dict(key="experience", title="Experience", color="#6a3fa0", accent="#d4af37", icon="clock",
         wallStyle="wall_brick", roofStyle="roof_tower", doorStyle="door_arch", windowStyle="window_arch",
         windowCount=2, flag=False, tile=(16, 28), blurb="Internships & journey"),
    dict(key="research", title="Research", color="#0f4c4c", accent="#7fd4c1", icon="flask",
         wallStyle="wall_stone", roofStyle="roof_dome", doorStyle="door", windowStyle="window_round",
         windowCount=3, flag=False, tile=(14, 19), blurb="Papers & findings"),
    dict(key="resume", title="Resume", color="#4a5568", accent="#c9d3de", icon="doc",
         wallStyle="wall_wood", roofStyle="roof_gable", doorStyle="door", windowStyle="window",
         windowCount=2, flag=False, tile=(20, 11), blurb="View & download my CV"),
]

building_objects = []
obj_id = 1
building_blocked_rects = []
for b in buildings_def:
    tx, ty = b["tile"]
    cx_px, cy_px = tile_center_px(tx, ty)
    w, h = BUILDING_SIZE_PX["w"], BUILDING_SIZE_PX["h"]
    ox, oy = cx_px - w / 2, cy_px - h / 2
    building_objects.append({
        "id": obj_id, "name": b["key"], "type": "building",
        "x": ox, "y": oy, "width": w, "height": h, "visible": True,
        "properties": [
            {"name": "title", "type": "string", "value": b["title"]},
            {"name": "color", "type": "string", "value": b["color"]},
            {"name": "accent", "type": "string", "value": b["accent"]},
            {"name": "icon", "type": "string", "value": b["icon"]},
            {"name": "blurb", "type": "string", "value": b["blurb"]},
            {"name": "wallStyle", "type": "string", "value": b["wallStyle"]},
            {"name": "roofStyle", "type": "string", "value": b["roofStyle"]},
            {"name": "doorStyle", "type": "string", "value": b["doorStyle"]},
            {"name": "windowStyle", "type": "string", "value": b["windowStyle"]},
            {"name": "windowCount", "type": "int", "value": b["windowCount"]},
            {"name": "flag", "type": "bool", "value": b["flag"]},
        ],
    })
    building_blocked_rects.append((tx - 5, tx + 5, ty - 4, ty + 5))
    obj_id += 1

# ---- Path spokes: simple L-shaped cobble corridor from plaza to each door -
def draw_spoke(px, py, width=2):
    x0, x1 = sorted([PLAZA_CX, px])
    fill_rect(paths, x0, x1, PLAZA_CY - width // 2, PLAZA_CY + width // 2, COBBLE)
    y0, y1 = sorted([PLAZA_CY, py + 3])
    fill_rect(paths, px - width // 2, px + width // 2, y0, y1, COBBLE)


for b in buildings_def:
    tx, ty = b["tile"]
    draw_spoke(tx, ty)

# ---- Spawn point -----------------------------------------------------------
spawn_objects = [{
    "id": obj_id, "name": "player_start", "type": "spawn",
    "x": SPAWN_X * TILE, "y": SPAWN_Y * TILE, "width": 0, "height": 0, "visible": True, "properties": [],
}]
obj_id += 1

# ---- Fountain: centerpiece of the plaza ------------------------------------
fountain_objects = [{
    "id": obj_id, "name": "fountain", "type": "fountain",
    "x": PLAZA_CX * TILE, "y": PLAZA_CY * TILE, "width": 0, "height": 0, "visible": True, "properties": [],
}]
obj_id += 1

# ---- NPC: Guide, stationed just south of the fountain (map center) --------
npc_objects = [{
    "id": obj_id, "name": "town_guide", "type": "npc",
    "x": PLAZA_CX * TILE - 10, "y": (PLAZA_CY + 4) * TILE, "width": 0, "height": 0, "visible": True,
    "properties": [
        {"name": "name", "type": "string", "value": "Guide"},
        {"name": "direction", "type": "string", "value": "down"},
        {
  "name": "dialogue",
  "type": "string",
  "value": (
    "\U0001F44B Welcome to Srajan Gupta's Interactive Portfolio!\n"
    "I'm your guide for this adventure.\n"
    "Explore each building to discover my projects, technical skills,\n"
    "education, achievements, resume, and contact information.\n"
    "If you're ready, let's begin the journey! \U0001F680"
  )
}
    ],
}]
obj_id += 1

# ---- Lamp posts around the plaza + spokes ----------------------------------
lamp_tiles = [
    (PLAZA_CX - 6, PLAZA_CY - 5), (PLAZA_CX + 6, PLAZA_CY - 5),
    (PLAZA_CX - 6, PLAZA_CY + 5), (PLAZA_CX + 6, PLAZA_CY + 5),
    (PLAZA_CX - 3, PLAZA_CY - 8), (PLAZA_CX + 3, PLAZA_CY - 8),
    (PLAZA_CX, SPAWN_Y - 3), (PLAZA_CX - 8, PLAZA_CY),
]
lamp_objects = []
for (tx, ty) in lamp_tiles:
    lamp_objects.append({
        "id": obj_id, "name": "lamp", "type": "lamp",
        "x": tx * TILE, "y": ty * TILE, "width": 0, "height": 0, "visible": True, "properties": [],
    })
    obj_id += 1

# ---- Benches, barrels, flower pots, mailboxes, logs, signboards -----------
def make_layer(name_prefix, points):
    objs = []
    global obj_id
    for (tx, ty) in points:
        objs.append({
            "id": obj_id, "name": name_prefix, "type": name_prefix,
            "x": tx * TILE, "y": ty * TILE, "width": 0, "height": 0, "visible": True, "properties": [],
        })
        obj_id += 1
    return objs


bench_objects = make_layer("bench", [
    (PLAZA_CX - 5, PLAZA_CY - 3), (PLAZA_CX + 5, PLAZA_CY - 3),
    (PLAZA_CX - 5, PLAZA_CY + 3), (PLAZA_CX + 5, PLAZA_CY + 3),
])
barrel_objects = make_layer("barrel", [
    (16 + 3, 28 + 4), (44 - 3, 28 + 4), (46 + 3, 19),
])
flowerpot_objects = make_layer("flowerpot", [
    (PLAZA_CX - 8, PLAZA_CY - 6), (PLAZA_CX + 8, PLAZA_CY - 6),
    (PLAZA_CX - 8, PLAZA_CY + 6), (PLAZA_CX + 8, PLAZA_CY + 6),
    (30 - 2, 8 + 4), (24 - 2, 33 + 4),
])
mailbox_objects = make_layer("mailbox", [
    (36 - 4, 33 + 4), (40 + 4, 11 + 4),
])
log_objects = make_layer("log", [
    (14 - 4, 19 + 4), (16 + 4, 28 - 4),
])
signboard_objects = make_layer("signboard", [
    (PLAZA_CX, SPAWN_Y - 2),
])

# ---- Fences (near pond, for a cozy enclosed feel) --------------------------
decoration = new_layer()
fence_runs = [(4, 8, 5), (36, 40, 5)]
for (x1, x2, y) in fence_runs:
    for x in range(x1, x2 + 1):
        decoration[idx(x, y)] = FENCE_H
decoration[idx(3, 5)] = FENCE_POST
decoration[idx(9, 5)] = FENCE_POST
decoration[idx(35, 5)] = FENCE_POST
decoration[idx(41, 5)] = FENCE_POST

# ---- Scatter flowers, bushes, rocks, mushrooms, grass tufts, worn dirt ----
blocked_for_decor = [PLAZA, SPINE, POND] + building_blocked_rects
scatter_gids_weighted = (
    [FLOWER_RED] * 3 + [FLOWER_PURPLE] * 3 + [FLOWER_YELLOW] * 3 + [FLOWER_WHITE] * 2 +
    [FLOWER_BLUE] * 3 + [FLOWER_ORANGE] * 2 + [FLOWER_PINK] * 3 +
    [BUSH] * 4 + [ROCK_SMALL] * 3 + [ROCK_CLUSTER] * 2 +
    [MUSHROOM_RED] * 2 + [MUSHROOM_BROWN] * 2 + [GRASS_TUFT] * 5 + [STEPPING_STONE] * 2
)

placed_decor = []
attempts = 0
while len(placed_decor) < 130 and attempts < 6000:
    attempts += 1
    tx = random.randint(1, COLS - 2)
    ty = random.randint(1, ROWS - 2)
    if in_any_rect(tx, ty, blocked_for_decor, pad=1):
        continue
    if any(abs(tx - px) < 2 and abs(ty - py) < 2 for (px, py) in placed_decor):
        continue
    decoration[idx(tx, ty)] = random.choice(scatter_gids_weighted)
    placed_decor.append((tx, ty))

# a few worn dirt "shortcut" patches off the main paths for realism
for _ in range(10):
    tx = random.randint(2, COLS - 3)
    ty = random.randint(2, ROWS - 3)
    if in_any_rect(tx, ty, blocked_for_decor, pad=0):
        continue
    decoration[idx(tx, ty)] = DIRT_WORN

# ---- Trees: five variants, avoiding plaza/spine/spokes/buildings/pond -----
tree_blocked = [PLAZA, SPINE, POND] + building_blocked_rects
VARIANTS = ["oak", "pine", "sakura", "bush", "sapling"]
VARIANT_WEIGHTS = [4, 3, 2, 2, 2]

tree_objects = []
attempts = 0
placed_trees = []
while len(tree_objects) < 46 and attempts < 5000:
    attempts += 1
    tx = random.randint(1, COLS - 2)
    ty = random.randint(1, ROWS - 2)
    if in_any_rect(tx, ty, tree_blocked, pad=1):
        continue
    px, py = tx * TILE + TILE / 2, ty * TILE + TILE / 2
    if any(abs(px - ox) < 42 and abs(py - oy) < 42 for (ox, oy) in placed_trees):
        continue
    variant = random.choices(VARIANTS, weights=VARIANT_WEIGHTS, k=1)[0]
    tree_objects.append({
        "id": obj_id, "name": "tree", "type": "tree",
        "x": px, "y": py, "width": 0, "height": 0, "visible": True,
        "properties": [
            {"name": "scale", "type": "float", "value": round(random.uniform(0.85, 1.3), 2)},
            {"name": "variant", "type": "string", "value": variant},
        ],
    })
    placed_trees.append((px, py))
    obj_id += 1

# ---- Assemble Tiled JSON ----
tiled_map = {
    "compressionlevel": -1, "width": COLS, "height": ROWS,
    "tilewidth": TILE, "tileheight": TILE, "infinite": False,
    "orientation": "orthogonal", "renderorder": "right-down", "type": "map",
    "tiledversion": "1.10.2", "version": "1.10",
    "nextlayerid": 17, "nextobjectid": obj_id,
    "tilesets": [{
        "firstgid": 1, "name": "town_tileset", "image": "../tilesets/town_tileset.png",
        "imagewidth": 256, "imageheight": 160, "tilewidth": TILE, "tileheight": TILE,
        "columns": 8, "tilecount": 40, "margin": 0, "spacing": 0,
    }],
    "layers": [
        {"id": 1, "name": "Ground", "type": "tilelayer", "width": COLS, "height": ROWS,
         "x": 0, "y": 0, "opacity": 1, "visible": True, "data": ground},
        {"id": 2, "name": "Paths", "type": "tilelayer", "width": COLS, "height": ROWS,
         "x": 0, "y": 0, "opacity": 1, "visible": True, "data": paths},
        {"id": 3, "name": "Decoration", "type": "tilelayer", "width": COLS, "height": ROWS,
         "x": 0, "y": 0, "opacity": 1, "visible": True, "data": decoration},
        {"id": 4, "name": "Buildings", "type": "objectgroup", "x": 0, "y": 0,
         "opacity": 1, "visible": True, "draworder": "topdown", "objects": building_objects},
        {"id": 5, "name": "Spawn", "type": "objectgroup", "x": 0, "y": 0,
         "opacity": 1, "visible": True, "draworder": "topdown", "objects": spawn_objects},
        {"id": 6, "name": "Trees", "type": "objectgroup", "x": 0, "y": 0,
         "opacity": 1, "visible": True, "draworder": "topdown", "objects": tree_objects},
        {"id": 7, "name": "NPCs", "type": "objectgroup", "x": 0, "y": 0,
         "opacity": 1, "visible": True, "draworder": "topdown", "objects": npc_objects},
        {"id": 8, "name": "Lamps", "type": "objectgroup", "x": 0, "y": 0,
         "opacity": 1, "visible": True, "draworder": "topdown", "objects": lamp_objects},
        {"id": 9, "name": "Fountain", "type": "objectgroup", "x": 0, "y": 0,
         "opacity": 1, "visible": True, "draworder": "topdown", "objects": fountain_objects},
        {"id": 10, "name": "Benches", "type": "objectgroup", "x": 0, "y": 0,
         "opacity": 1, "visible": True, "draworder": "topdown", "objects": bench_objects},
        {"id": 11, "name": "Barrels", "type": "objectgroup", "x": 0, "y": 0,
         "opacity": 1, "visible": True, "draworder": "topdown", "objects": barrel_objects},
        {"id": 12, "name": "FlowerPots", "type": "objectgroup", "x": 0, "y": 0,
         "opacity": 1, "visible": True, "draworder": "topdown", "objects": flowerpot_objects},
        {"id": 13, "name": "Mailboxes", "type": "objectgroup", "x": 0, "y": 0,
         "opacity": 1, "visible": True, "draworder": "topdown", "objects": mailbox_objects},
        {"id": 14, "name": "Logs", "type": "objectgroup", "x": 0, "y": 0,
         "opacity": 1, "visible": True, "draworder": "topdown", "objects": log_objects},
        {"id": 15, "name": "Signboards", "type": "objectgroup", "x": 0, "y": 0,
         "opacity": 1, "visible": True, "draworder": "topdown", "objects": signboard_objects},
    ],
}

with open("/home/claude/portfolio-town/public/assets/maps/town.json", "w") as f:
    json.dump(tiled_map, f)

print("map written:", COLS, "x", ROWS, "|", len(building_objects), "buildings |",
      len(tree_objects), "trees |", len(placed_decor), "decor |", len(lamp_objects), "lamps")
