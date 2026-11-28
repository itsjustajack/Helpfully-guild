"""Builds the pixel hero card on a 128x192 grid. Stage 2: flat silhouette (one flat colour per part).

    python3 -I -B build_card.py        -> hero_card.png (+ previews/t2_compare.png)
Landmarks (from measurements.md, scaled to a 176-px figure, 8-px margin): top y=8, chin 36, shoulders 43,
waist 91, shorts hem 107, knee 136, feet bottom 184. Everything here is my own drawing; the reference is
only used for proportions.
"""
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 128, 192
SKIN, HAIR, SHORTS = (246, 167, 95, 255), (36, 41, 64, 255), (41, 45, 71, 255)


def mirror(pts):
    return [(127 - x, y) for x, y in pts]


def silhouette():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    poly = lambda pts, c: d.polygon(pts, fill=c)
    both = lambda pts, c: (poly(pts, c), poly(mirror(pts), c))
    # legs and feet: ~14-16 px thick thighs, calves with a bulge, feet turned out
    both([(47, 100), (63, 100), (61, 136), (49, 136)], SKIN)                   # thigh
    both([(49, 136), (61, 136), (61, 148), (58, 172), (53, 172), (49, 150)], SKIN)   # knee and calf
    both([(52, 170), (59, 170), (60, 178), (62, 184), (42, 184), (45, 179), (51, 177)], SKIN)  # ankle and foot
    # torso: wide chest, V taper from the shoulders (y=43) to the waist (y=91)
    poly([(43, 43), (85, 43), (79, 91), (49, 91)], SKIN)
    poly([(57, 38), (71, 38), (86, 45), (42, 45)], SKIN)                       # trapezius slope into the neck
    d.ellipse([39, 41, 54, 56], fill=SKIN)
    d.ellipse([74, 41, 89, 56], fill=SKIN)                                     # deltoids
    # arms hanging, fists loosely closed (upper arm ~12 px, forearm ~10 px)
    both([(42, 42), (53, 44), (50, 72), (40, 70)], SKIN)                       # upper arm
    both([(40, 70), (50, 72), (47, 100), (39, 99)], SKIN)                      # forearm
    both([(37, 98), (48, 98), (48, 111), (38, 113)], SKIN)                     # fist
    # shorts, flared toward the hem
    poly([(48, 88), (80, 88), (86, 107), (42, 107)], SHORTS)
    # neck and head
    d.rectangle([58, 34, 70, 44], fill=SKIN)
    d.ellipse([52, 8, 76, 32], fill=SKIN)
    poly([(53, 24), (75, 24), (71, 35), (64, 37), (57, 35)], SKIN)             # jaw, chin at y=36
    d.rectangle([50, 21, 52, 29], fill=SKIN)
    d.rectangle([76, 21, 78, 29], fill=SKIN)                                   # ears
    # hair mass (flat for now; shaped and shaded in T4)
    poly([(51, 22), (52, 12), (58, 7), (66, 6), (75, 10), (77, 22), (72, 17), (64, 14), (56, 17)], HAIR)
    return im


if __name__ == "__main__":
    card = silhouette()
    card.save(os.path.join(HERE, "hero_card.png"))
    # compare: reference hero scaled to the same landmarks | my card, both x4, with landmark lines
    ref = Image.open(os.path.join(HERE, "..", "..", "style-guide", "references", "ref_hero_on_street.png")).convert("RGB")
    crop = ref.crop((330, 64, 650, 630))                                   # hero, hair top to feet
    s = 176 / crop.height
    crop = crop.resize((round(crop.width * s), 176), Image.LANCZOS)
    left = Image.new("RGB", (W, H), (60, 66, 92))
    left.paste(crop, (64 - crop.width // 2, 8))
    right = Image.new("RGB", (W, H), (60, 66, 92))
    right.paste(card, (0, 0), card)
    out = Image.new("RGB", (W * 8 + 12, H * 4), (20, 20, 24))
    for i, panel in enumerate((left, right)):
        big = panel.resize((W * 4, H * 4), Image.NEAREST)
        dd = ImageDraw.Draw(big)
        for y in (8, 36, 43, 91, 107, 136, 184):
            dd.line([(0, y * 4), (W * 4, y * 4)], fill=(255, 70, 70), width=1)
        out.paste(big, (i * (W * 4 + 12), 0))
    os.makedirs(os.path.join(HERE, "previews"), exist_ok=True)
    out.save(os.path.join(HERE, "previews", "t2_compare.png"))
    print("built hero_card.png and previews/t2_compare.png")
