"""Painterly pass: makes a render look hand-painted, the same way for everything in it.

    python -I paint_filter.py in.png out.png
Needs: pip install opencv-python-headless  (free). Steps: edge-preserving
paint smoothing, brush/canvas texture, soft dark outlines, warm grade, vignette.
"""
import sys

import cv2
import numpy as np

src, dst = sys.argv[1], sys.argv[2]
img = cv2.imread(src)
h, w = img.shape[:2]

# 1) paint: flatten small detail, keep edges (like brush shapes)
paint = cv2.stylization(img, sigma_s=22, sigma_r=0.22)
paint = cv2.addWeighted(paint, 0.55, img, 0.45, 0)

# 2) brush / canvas texture
rng = np.random.default_rng(3)
n = rng.normal(0, 1, (h, w)).astype(np.float32)
fine = cv2.GaussianBlur(n, (0, 0), 0.9)
coarse = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 4.0)
tex = fine / np.abs(fine).max() * 0.035 + coarse / np.abs(coarse).max() * 0.05
f = paint.astype(np.float32) * (1.0 + tex)[..., None]

# 3) soft dark outlines where objects meet (painted ink, subtle)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(cv2.GaussianBlur(gray, (0, 0), 1.6), 50, 130)
edges = cv2.GaussianBlur(cv2.dilate(edges, np.ones((2, 2), np.uint8)), (0, 0), 0.8).astype(np.float32) / 255.0
f *= (1.0 - 0.10 * edges)[..., None]

# 4) warm storybook grade: warm highlights, cool-blue shadows, a little more colour
f = f / 255.0
lum = f.mean(axis=2, keepdims=True)
f = f + (np.array([0.02, 0.0, -0.025]) * lum) + (np.array([-0.02, 0.0, 0.035]) * (1 - lum) * 0.6)
mean = f.mean(axis=2, keepdims=True)
f = mean + (f - mean) * 1.18
f = np.clip(f, 0, 1) ** 0.95

# 5) vignette
yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h * 0.48) / (h / 2)) ** 2)
f *= (1.0 - 0.55 * np.clip(r - 0.45, 0, 1) ** 1.3)[..., None]

cv2.imwrite(dst, (np.clip(f, 0, 1) * 255).astype(np.uint8))
print("painted", dst)
