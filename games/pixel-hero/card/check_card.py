"""The Checker for the pixel hero card. Written FIRST (it fails until the art exists).

    python3 -I -B check_card.py [path/to/hero_card.png]
Rules (from the style guide and tasks/plan.md): size 64x96, transparent background, hard pixels only
(alpha 0 or 255), at most 24 colours, no stray single pixels, outline continuous around the figure,
left/right balance, nothing touching the frame edge. Exit code 1 if anything fails.
"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "hero_card.png")
W, H, MAX_COLOURS = 64, 96, 24
results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(("PASS  " if ok else "FAIL  ") + name + (f": {detail}" if detail else ""))


if not os.path.isfile(PATH):
    print(f"FAIL  hero card exists: {PATH} not found (RED: the art has not been made yet)")
    sys.exit(1)

im = Image.open(PATH).convert("RGBA")
px = im.load()
check("size is 64x96", im.size == (W, H), str(im.size))
opaque = {(x, y) for y in range(im.height) for x in range(im.width) if px[x, y][3] > 0}
check("figure is not empty", len(opaque) > 500, f"{len(opaque)} opaque pixels")
check("hard pixels only (alpha is 0 or 255)", all(px[x, y][3] in (0, 255) for y in range(im.height) for x in range(im.width)))
cols = {px[x, y][:3] for (x, y) in opaque}
check(f"at most {MAX_COLOURS} colours", len(cols) <= MAX_COLOURS, f"{len(cols)} colours")
check("nothing touches the frame edge", not any(x in (0, im.width - 1) or y in (0, im.height - 1) for x, y in opaque))

# stray pixels: a pixel whose colour differs from all 8 neighbours AND that is not on the outline colour
dark = min(cols, key=lambda c: sum(c)) if cols else (0, 0, 0)
strays = []
for (x, y) in opaque:
    me = px[x, y][:3]
    if me == dark:
        continue
    same = 0
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if (dx or dy) and (x + dx, y + dy) in opaque and px[x + dx, y + dy][:3] == me:
                same += 1
    if same == 0:
        strays.append((x, y))
check("no stray single pixels", len(strays) <= 6, f"{len(strays)} isolated pixels (allowed 6 for eye/face highlights)")

# outline: every opaque pixel that touches empty space (4-neighbour) must be the darkest colour
edge_bad = [(x, y) for (x, y) in opaque
            if any((x + dx, y + dy) not in opaque for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            and px[x, y][:3] != dark]
check("outline is continuous", len(edge_bad) <= 12, f"{len(edge_bad)} silhouette pixels are not outline colour (allowed 12)")

# balance: left and right halves have similar mass (a front-facing hero should not lean)
mid = im.width // 2
left = sum(1 for (x, y) in opaque if x < mid)
right = len(opaque) - left
check("left/right balance within 12%", abs(left - right) <= 0.12 * max(1, len(opaque)), f"left {left} / right {right}")

print(f"{sum(results)}/{len(results)} checks passed")
sys.exit(0 if all(results) else 1)
