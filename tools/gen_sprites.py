"""
Generates:
  public/assets/characters/player.png       4 dirs x 4 frames, 48x48 (walk cycle)
  public/assets/characters/player_idle.png  4 dirs x 2 frames, 48x48 (idle breathing)
  public/assets/npc/guide.png               4 dirs x 5 frames, 48x48
      col 0: idle-a   col 1: idle-b (raised)   col 2: blink
      col 3: walk-a   col 4: walk-b
Still procedurally generated pixel art, tuned for crisper outlines and
richer shading so it reads clearly at gameplay scale.
"""
from PIL import Image, ImageDraw

FRAME = 48


def rect(d, x0, y0, x1, y1, fill):
    d.rectangle((x0, y0, x1, y1), fill=fill)


def shadow(d, cx, y, w=10):
    d.ellipse((cx - w, y + 40, cx + w, y + 45), fill=(0, 0, 0, 70))


# ---------------------------------------------------------------- PLAYER ----
def make_player():
    COLS, ROWS = 4, 4
    sheet = Image.new("RGBA", (FRAME * COLS, FRAME * ROWS), (0, 0, 0, 0))
    d = ImageDraw.Draw(sheet)

    SKIN = (240, 198, 160, 255)
    SKIN_SHADE = (214, 170, 132, 255)
    HAIR = (110, 56, 36, 255)
    HAIR_HI = (150, 82, 52, 255)
    SHIRT = (235, 240, 245, 255)
    SHIRT_SHADE = (205, 212, 220, 255)
    BELT = (94, 68, 44, 255)
    PANTS = (52, 82, 140, 255)
    PANTS_SHADE = (38, 62, 108, 255)
    SHOE = (60, 44, 36, 255)
    SHOE_HI = (86, 64, 50, 255)
    EYE = (35, 28, 26, 255)
    OUTLINE = (30, 24, 22, 200)

    def frame(ox, oy, direction, phase):
        bob = 1 if phase in (1, 3) else 0
        stride = 3 if phase == 1 else (-3 if phase == 3 else 0)
        y = oy + bob
        cx = ox + FRAME // 2
        shadow(d, cx, y)

        leg_l_x = cx - 7 + (stride if direction in ("left", "right") else 0)
        leg_r_x = cx + 1 - (stride if direction in ("left", "right") else 0)
        rect(d, leg_l_x, y + 33, leg_l_x + 6, y + 40, PANTS)
        rect(d, leg_r_x, y + 33, leg_r_x + 6, y + 40, PANTS_SHADE)
        rect(d, leg_l_x, y + 40, leg_l_x + 6, y + 43, SHOE)
        rect(d, leg_r_x, y + 40, leg_r_x + 6, y + 43, SHOE)
        d.line((leg_l_x, y + 40, leg_l_x + 6, y + 40), fill=SHOE_HI, width=1)
        d.line((leg_r_x, y + 40, leg_r_x + 6, y + 40), fill=SHOE_HI, width=1)

        rect(d, cx - 9, y + 19, cx + 9, y + 34, SHIRT)
        rect(d, cx + 2, y + 19, cx + 9, y + 34, SHIRT_SHADE)
        rect(d, cx - 9, y + 30, cx + 9, y + 32, BELT)  # belt line for detail

        arm_swing = 3 if phase == 1 else (-3 if phase == 3 else 0)
        rect(d, cx - 13, y + 21 + max(arm_swing, 0), cx - 9, y + 30 + max(arm_swing, 0), SKIN_SHADE)
        rect(d, cx + 9, y + 21 - min(arm_swing, 0), cx + 13, y + 30 - min(arm_swing, 0), SKIN)

        rect(d, cx - 3, y + 13, cx + 3, y + 17, SKIN_SHADE)
        rect(d, cx - 10, y + 2, cx + 10, y + 18, SKIN)
        rect(d, cx + 3, y + 2, cx + 10, y + 18, SKIN_SHADE)

        if direction == "up":
            rect(d, cx - 11, y, cx + 11, y + 8, HAIR)
        else:
            rect(d, cx - 11, y, cx + 11, y + 7, HAIR)
            rect(d, cx - 11, y, cx - 5, y + 12, HAIR_HI)

        if direction == "down":
            d.ellipse((cx - 6, y + 9, cx - 3, y + 12), fill=EYE)
            d.ellipse((cx + 3, y + 9, cx + 6, y + 12), fill=EYE)
            rect(d, cx - 3, y + 14, cx + 3, y + 15, (200, 120, 110, 255))
        elif direction == "left":
            d.ellipse((cx - 8, y + 9, cx - 5, y + 12), fill=EYE)
        elif direction == "right":
            d.ellipse((cx + 5, y + 9, cx + 8, y + 12), fill=EYE)

        # crisp ground contact outline for a cleaner silhouette
        d.line((leg_l_x - 1, y + 43, leg_r_x + 7, y + 44), fill=OUTLINE, width=1)

    directions = ["down", "left", "right", "up"]
    for r, dir_ in enumerate(directions):
        for c in range(COLS):
            frame(c * FRAME, r * FRAME, dir_, c % 4)
    sheet.save("/home/claude/portfolio-town/public/assets/characters/player.png")

    # idle breathing sheet: 2 frames per direction, frame1 = tiny chest raise
    idle = Image.new("RGBA", (FRAME * 2, FRAME * ROWS), (0, 0, 0, 0))
    di = ImageDraw.Draw(idle)

    def idle_frame(ox, oy, direction, raised):
        y = oy - (1 if raised else 0)
        cx = ox + FRAME // 2
        shadow(di, cx, oy)
        rect(di, cx - 7, y + 33, cx - 1, y + 40, PANTS)
        rect(di, cx + 1, y + 33, cx + 7, y + 40, PANTS_SHADE)
        rect(di, cx - 7, y + 40, cx - 1, y + 43, SHOE)
        rect(di, cx + 1, y + 40, cx + 7, y + 43, SHOE)
        rect(di, cx - 9, y + 19, cx + 9, y + 34, SHIRT)
        rect(di, cx + 2, y + 19, cx + 9, y + 34, SHIRT_SHADE)
        rect(di, cx - 9, y + 30, cx + 9, y + 32, BELT)
        rect(di, cx - 13, y + 21, cx - 9, y + 30, SKIN_SHADE)
        rect(di, cx + 9, y + 21, cx + 13, y + 30, SKIN)
        rect(di, cx - 3, y + 13, cx + 3, y + 17, SKIN_SHADE)
        rect(di, cx - 10, y + 2, cx + 10, y + 18, SKIN)
        rect(di, cx + 3, y + 2, cx + 10, y + 18, SKIN_SHADE)
        if direction == "up":
            rect(di, cx - 11, y, cx + 11, y + 8, HAIR)
        else:
            rect(di, cx - 11, y, cx + 11, y + 7, HAIR)
            rect(di, cx - 11, y, cx - 5, y + 12, HAIR_HI)
        if direction == "down":
            di.ellipse((cx - 6, y + 9, cx - 3, y + 12), fill=EYE)
            di.ellipse((cx + 3, y + 9, cx + 6, y + 12), fill=EYE)

    for r, dir_ in enumerate(directions):
        idle_frame(0, r * FRAME, dir_, False)
        idle_frame(FRAME, r * FRAME, dir_, True)
    idle.save("/home/claude/portfolio-town/public/assets/characters/player_idle.png")


# -------------------------------------------------------------- NPC GUIDE ---
def make_guide():
    COLS, ROWS = 5, 4  # idle-a, idle-b, blink, walk-a, walk-b  x  4 dirs
    sheet = Image.new("RGBA", (FRAME * COLS, FRAME * ROWS), (0, 0, 0, 0))
    d = ImageDraw.Draw(sheet)

    ROBE = (118, 104, 168, 255)
    ROBE_SHADE = (92, 80, 136, 255)
    ROBE_HI = (146, 132, 196, 255)
    TRIM = (222, 190, 96, 255)
    SKIN = (232, 192, 156, 255)
    BEARD = (238, 238, 238, 255)
    STAFF = (124, 88, 50, 255)
    STAFF_TOP = (150, 210, 226, 255)

    def base(cx, y, direction, raised, stride=0):
        yy = y - (1 if raised else 0)
        shadow(d, cx, y, w=11)

        # robe (long, triangular taper) with a subtle walk-sway via stride
        d.polygon([(cx - 11 + stride, yy + 44), (cx - 8, yy + 20), (cx + 8, yy + 20), (cx + 11 - stride, yy + 44)],
                   fill=ROBE)
        d.polygon([(cx + 1, yy + 20), (cx + 8, yy + 20), (cx + 11 - stride, yy + 44), (cx + 2, yy + 44)],
                   fill=ROBE_SHADE)
        d.polygon([(cx - 8, yy + 20), (cx - 5, yy + 20), (cx - 3, yy + 44), (cx - 10 + stride, yy + 44)],
                   fill=ROBE_HI)
        d.line((cx - 9, yy + 30, cx + 9, yy + 30), fill=TRIM, width=2)
        d.line((cx - 9, yy + 38, cx + 9, yy + 38), fill=TRIM, width=1)

        # staff (opposite side from facing detail), topped with a small glowing orb
        staff_x = cx - 15 if direction != "left" else cx + 15
        d.rectangle((staff_x, yy + 10, staff_x + 2, yy + 44), fill=STAFF)
        d.ellipse((staff_x - 3, yy + 4, staff_x + 5, yy + 12), fill=STAFF_TOP)
        d.ellipse((staff_x - 1, yy + 6, staff_x + 1, yy + 8), fill=(255, 255, 255, 200))

        # head + long grey beard
        rect(d, cx - 3, yy + 13, cx + 3, yy + 17, SKIN)
        d.ellipse((cx - 9, yy + 2, cx + 9, yy + 18), fill=SKIN)
        d.polygon([(cx - 8, yy + 13), (cx + 8, yy + 13), (cx + 5, yy + 24), (cx - 5, yy + 24)], fill=BEARD)
        rect(d, cx - 9, yy, cx + 9, yy + 6, (230, 230, 230, 255))  # hair/hood band
        d.line((cx - 9, yy + 6, cx + 9, yy + 6), fill=TRIM, width=1)
        return yy

    def eyes(cx, yy, direction, closed):
        if direction == "down":
            if closed:
                d.line((cx - 6, yy + 9.5, cx - 3, yy + 9.5), fill=(40, 34, 30, 255), width=1)
                d.line((cx + 2, yy + 9.5, cx + 5, yy + 9.5), fill=(40, 34, 30, 255), width=1)
            else:
                d.ellipse((cx - 5, yy + 8, cx - 2, yy + 11), fill=(40, 34, 30, 255))
                d.ellipse((cx + 2, yy + 8, cx + 5, yy + 11), fill=(40, 34, 30, 255))

    directions = ["down", "left", "right", "up"]
    for r, dir_ in enumerate(directions):
        oy = r * FRAME
        # col 0: idle-a
        cx = 0 * FRAME + FRAME // 2
        yy = base(cx, oy, dir_, False)
        eyes(cx, yy, dir_, False)
        # col 1: idle-b (raised breathing)
        cx = 1 * FRAME + FRAME // 2
        yy = base(cx, oy, dir_, True)
        eyes(cx, yy, dir_, False)
        # col 2: blink
        cx = 2 * FRAME + FRAME // 2
        yy = base(cx, oy, dir_, False)
        eyes(cx, yy, dir_, True)
        # col 3: walk-a (slight sway one way)
        cx = 3 * FRAME + FRAME // 2
        yy = base(cx, oy, dir_, False, stride=2)
        eyes(cx, yy, dir_, False)
        # col 4: walk-b (slight sway other way)
        cx = 4 * FRAME + FRAME // 2
        yy = base(cx, oy, dir_, True, stride=-2)
        eyes(cx, yy, dir_, False)

    sheet.save("/home/claude/portfolio-town/public/assets/npc/guide.png")


make_player()
make_guide()
print("characters written")
