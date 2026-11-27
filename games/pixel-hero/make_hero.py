"""Pixel superhero (top-down 3/4 view) drawn entirely in code. Free, no AI art.

    python3 -I games/pixel-hero/make_hero.py

Outputs (next to this file):
  hero_sheet.png     3 columns (idle, walk A, walk B) x 4 rows (down, up, left, right),
                     each frame 32x32, transparent background, hard pixel edges
  hero_preview.png   the sheet enlarged 8x with nearest-neighbour, on grey
  walk_preview.gif   all four directions walking, enlarged
Runs checks and exits 1 if any fail.
"""
import os
import sys

from PIL import Image

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
W = H = 32

# ---- palette: 14 colours + transparent ------------------------------------------------
P = {
    "OUT": (20, 16, 40, 255),        # outline
    "SUIT": (40, 90, 200, 255),
    "SUIT_D": (28, 60, 150, 255),
    "SUIT_L": (90, 150, 240, 255),
    "CAPE": (205, 40, 55, 255),
    "CAPE_D": (140, 24, 42, 255),
    "SKIN": (240, 190, 150, 255),
    "SKIN_D": (200, 140, 110, 255),
    "GOLD": (250, 200, 50, 255),
    "GOLD_D": (200, 140, 30, 255),
    "WHITE": (255, 255, 255, 255),
    "GLOW": (80, 240, 255, 255),
    "BELT": (60, 40, 30, 255),
    "SHADOW": (30, 30, 60, 255),     # soft ground shadow (opaque, no blur)
}


class Canvas:
    def __init__(self):
        self.im = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    def px(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            self.im.putpixel((x, y), P[c])

    def r(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.px(x, y, c)

    def outline(self):
        """Add a 1px outline around the whole silhouette (not the ground shadow)."""
        src = self.im.copy()
        for y in range(H):
            for x in range(W):
                if src.getpixel((x, y))[3] == 0:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < W and 0 <= ny < H:
                            n = src.getpixel((nx, ny))
                            if n[3] and n != P["SHADOW"]:
                                self.im.putpixel((x, y), P["OUT"])
                                break
        self.shadow()

    def shadow(self):
        """Ground shadow, painted last and only on empty pixels (rows 29-30)."""
        for x in range(9, 23):
            for y, lo, hi in ((29, 10, 21), (30, 12, 19)):
                if lo <= x <= hi and self.im.getpixel((x, y))[3] == 0:
                    self.px(x, y, "SHADOW")


def legs_boots(cv, phase, cx_left=12, cx_right=17, facing_dx=0):
    """phase: 0 idle, 1 left leg forward, 2 right leg forward."""
    up_l = 1 if phase == 2 else 0       # the trailing leg is lifted one pixel
    up_r = 1 if phase == 1 else 0
    for (x0, up) in ((cx_left, up_l), (cx_right, up_r)):
        cv.r(x0, 22, x0 + 2, 26 - up, "SUIT")
        cv.px(x0 + 2, 23, "SUIT_D")
        cv.r(x0 + 2, 22, x0 + 2, 26 - up, "SUIT_D")
        cv.r(x0 - 0, 27 - up, x0 + 2 + facing_dx, 28 - up, "GOLD")
        cv.r(x0 + 2, 28 - up, x0 + 2 + facing_dx, 28 - up, "GOLD_D")


def frame_down(phase):
    cv = Canvas()
    sw = {0: (0, 0), 1: (-1, 1), 2: (1, -1)}[phase]
    # cape peeking out behind the arms
    cv.r(8, 13, 9, 24, "CAPE_D")
    cv.r(22, 13, 23, 24, "CAPE_D")
    legs_boots(cv, phase)
    # torso
    cv.r(10, 13, 21, 21, "SUIT")
    cv.r(20, 13, 21, 21, "SUIT_D")
    cv.r(11, 13, 12, 14, "SUIT_L")
    cv.r(10, 12, 21, 12, "CAPE")                      # cape collar
    for (x, y) in ((16, 14), (15, 15), (16, 15), (17, 15), (16, 16)):
        cv.px(x, y, "GLOW")
    cv.px(16, 15, "WHITE")                             # chest emblem
    cv.r(10, 20, 21, 21, "GOLD")                       # belt
    cv.r(15, 20, 16, 21, "GOLD_D")
    # arms (swing opposite to the legs)
    cv.r(7, 13 + sw[0], 9, 19 + sw[0], "SUIT")
    cv.r(22, 13 + sw[1], 24, 19 + sw[1], "SUIT")
    cv.r(7, 20 + sw[0], 9, 21 + sw[0], "GOLD")
    cv.r(22, 20 + sw[1], 24, 21 + sw[1], "GOLD")
    cv.r(23, 13 + sw[1], 24, 19 + sw[1], "SUIT_D")
    # head: hood, gold mask band, eyes, mouth
    cv.r(11, 4, 20, 8, "SUIT")
    cv.r(12, 3, 19, 3, "SUIT")
    cv.px(13, 4, "SUIT_L")
    cv.px(14, 4, "SUIT_L")
    cv.r(11, 9, 11, 11, "SUIT")
    cv.r(20, 9, 20, 11, "SUIT")
    cv.r(12, 9, 19, 11, "SKIN")
    cv.r(12, 6, 19, 8, "GOLD")
    cv.r(12, 8, 19, 8, "GOLD_D")
    for x in (13, 14, 17, 18):
        cv.px(x, 7, "WHITE")
    cv.r(15, 10, 16, 10, "SKIN_D")
    cv.outline()
    return cv.im


def frame_up(phase):
    cv = Canvas()
    sw = {0: (0, 0), 1: (-1, 1), 2: (1, -1)}[phase]
    legs_boots(cv, phase)
    # arms behind the cape
    cv.r(7, 13 + sw[0], 9, 19 + sw[0], "SUIT")
    cv.r(22, 13 + sw[1], 24, 19 + sw[1], "SUIT")
    cv.r(7, 20 + sw[0], 9, 21 + sw[0], "GOLD")
    cv.r(22, 20 + sw[1], 24, 21 + sw[1], "GOLD")
    # big cape over the back, hem swings when walking
    hem = {0: 0, 1: 1, 2: -1}[phase]
    cv.r(9, 12, 22, 25, "CAPE")
    cv.r(15, 13, 16, 25, "CAPE_D")
    cv.r(9, 12, 10, 25, "CAPE_D")
    cv.r(21, 12, 22, 25, "CAPE_D")
    cv.r(9 + hem, 26, 22 + hem, 26, "CAPE_D")
    cv.r(11, 12, 20, 12, "GOLD_D")                    # cape clasp line
    # head from behind: plain hood, a little neck
    cv.r(11, 4, 20, 11, "SUIT")
    cv.r(12, 3, 19, 3, "SUIT")
    cv.r(19, 4, 20, 11, "SUIT_D")
    cv.px(13, 4, "SUIT_L")
    cv.px(14, 4, "SUIT_L")
    cv.r(14, 9, 17, 9, "SUIT_D")                     # hood seam
    cv.outline()
    return cv.im


def frame_right(phase):
    cv = Canvas()
    swing = {0: 0, 1: 2, 2: -2}[phase]               # arm / cape swing
    # cape trails behind (to the left), streams out when walking
    trail = {0: 0, 1: -1, 2: -2}[phase]
    cv.r(10 + trail, 13, 13, 21, "CAPE")                 # stays behind the torso
    cv.r(10 + trail, 13, 11 + trail, 21, "CAPE_D")
    cv.r(8 + trail, 22, 12 + trail, 25, "CAPE_D")
    # back leg, torso, front leg
    lx = {0: 0, 1: -2, 2: 2}[phase]
    rx = {0: 0, 1: 2, 2: -2}[phase]
    for x0, dx in ((13, lx), (16, rx)):
        cv.r(x0 + dx, 22, x0 + dx + 2, 26, "SUIT")
        cv.r(x0 + dx + 2, 22, x0 + dx + 2, 26, "SUIT_D")
        cv.r(x0 + dx, 27, x0 + dx + 3, 28, "GOLD")
        cv.r(x0 + dx, 28, x0 + dx + 3, 28, "GOLD_D")
    cv.r(13, 13, 18, 21, "SUIT")
    cv.r(13, 13, 14, 21, "SUIT_D")
    cv.r(17, 13, 18, 14, "SUIT_L")
    cv.r(13, 12, 18, 12, "CAPE")                      # collar
    cv.r(13, 20, 18, 21, "GOLD")
    cv.r(17, 20, 18, 21, "GOLD_D")
    cv.px(18, 16, "GLOW")                              # chest glow on the front edge
    cv.px(18, 15, "GLOW")
    # arm (swings)
    cv.r(15 + swing // 2, 13, 17 + swing // 2, 19, "SUIT")
    cv.r(15 + swing // 2, 20, 17 + swing // 2, 21, "GOLD")
    cv.r(15 + swing // 2, 13, 15 + swing // 2, 19, "SUIT_D")
    # head in profile: hood at the back, face + mask at the front
    cv.r(12, 4, 19, 8, "SUIT")
    cv.r(13, 3, 18, 3, "SUIT")
    cv.r(12, 9, 16, 11, "SUIT")
    cv.r(17, 9, 20, 11, "SKIN")
    cv.px(20, 9, "SKIN")
    cv.r(15, 6, 20, 8, "GOLD")
    cv.r(15, 8, 20, 8, "GOLD_D")
    cv.px(18, 7, "WHITE")
    cv.px(19, 7, "WHITE")
    cv.px(14, 4, "SUIT_L")
    cv.px(15, 4, "SUIT_L")
    cv.r(18, 10, 19, 10, "SKIN_D")
    cv.outline()
    return cv.im


def build():
    rows = {
        "down": [frame_down(p) for p in (0, 1, 2)],
        "up": [frame_up(p) for p in (0, 1, 2)],
        "right": [frame_right(p) for p in (0, 1, 2)],
    }
    rows["left"] = [f.transpose(Image.FLIP_LEFT_RIGHT) for f in rows["right"]]
    order = ["down", "up", "left", "right"]
    sheet = Image.new("RGBA", (W * 3, H * 4), (0, 0, 0, 0))
    for ry, name in enumerate(order):
        for cx, f in enumerate(rows[name]):
            sheet.paste(f, (cx * W, ry * H))
    return sheet, rows, order


def checks(sheet, rows, order):
    res = []

    def check(name, ok, detail=""):
        res.append(ok)
        print(("PASS " if ok else "FAIL ") + name + (f": {detail}" if detail else ""))

    px = sheet.load()
    cols = {px[x, y][:3] for y in range(sheet.height) for x in range(sheet.width) if px[x, y][3]}
    check("palette <= 16 colours", len(cols) <= 16, f"{len(cols)} colours")
    check("sheet size is 3x4 frames of 32x32", sheet.size == (96, 128), str(sheet.size))
    check("hard pixel edges (alpha is only 0 or 255)",
          all(px[x, y][3] in (0, 255) for y in range(sheet.height) for x in range(sheet.width)))
    check("4 directions x 3 frames", len(order) == 4 and all(len(rows[o]) == 3 for o in order))
    empty = [(o, i) for o in order for i, f in enumerate(rows[o]) if f.getbbox() is None]
    check("no empty frame", not empty, str(empty))
    edge = []
    for o in order:
        for i, f in enumerate(rows[o]):
            fp = f.load()
            for t in range(W):
                if fp[t, 0][3] or fp[t, H - 1][3] or fp[0, t][3] or fp[W - 1, t][3]:
                    edge.append((o, i))
                    break
    check("nothing touches the frame edge", not edge, str(edge))
    check("walk frames differ from idle",
          all(rows[o][1].tobytes() != rows[o][0].tobytes() and rows[o][2].tobytes() != rows[o][1].tobytes()
              for o in order))
    check("left is the mirror of right",
          all(rows["left"][i].tobytes() == rows["right"][i].transpose(Image.FLIP_LEFT_RIGHT).tobytes()
              for i in range(3)))
    print(f"{sum(res)}/{len(res)} checks passed")
    return all(res)


def previews(sheet, rows, order):
    s = 8
    big = sheet.resize((sheet.width * s, sheet.height * s), Image.NEAREST)
    bg = Image.new("RGBA", big.size, (176, 176, 184, 255))
    bg.alpha_composite(big)
    bg.convert("RGB").save(os.path.join(HERE, "hero_preview.png"))
    # walk gif: all four directions side by side, cycle idle-A-idle-B
    z = 6
    seq = [0, 1, 0, 2]
    frames = []
    for i in seq:
        strip = Image.new("RGBA", (W * 4 * z, H * z), (176, 176, 184, 255))
        for k, o in enumerate(order):
            f = rows[o][i].resize((W * z, H * z), Image.NEAREST)
            strip.alpha_composite(f, (k * W * z, 0))
        frames.append(strip.convert("P", palette=Image.ADAPTIVE))
    frames[0].save(os.path.join(HERE, "walk_preview.gif"), save_all=True,
                   append_images=frames[1:], duration=180, loop=0, disposal=2)


if __name__ == "__main__":
    sheet, rows, order = build()
    sheet.save(os.path.join(HERE, "hero_sheet.png"))
    ok = checks(sheet, rows, order)
    previews(sheet, rows, order)
    sys.exit(0 if ok else 1)
