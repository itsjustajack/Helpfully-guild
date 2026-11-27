"""Copy the builder scripts into the add-on and zip it.

    python3 games/mha-rpg/blender/addon/make_addon.py
Output: games/mha-rpg/blender/addon/mha_hero_tools-<version>.zip
"""
import os
import re
import shutil
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
PKG = os.path.join(HERE, "mha_hero_tools")
SCRIPTS = ["male_base.py", "hand_base.py", "mid_gauntlet.py", "hero_glove.py", "toon_look.py"]

dst = os.path.join(PKG, "builders")
shutil.rmtree(dst, ignore_errors=True)
os.makedirs(dst)
for s in SCRIPTS:
    shutil.copy2(os.path.join(SRC, s), dst)

version = re.search(r'^version\s*=\s*"([^"]+)"',
                    open(os.path.join(PKG, "blender_manifest.toml")).read(), re.M).group(1)
out = os.path.join(HERE, f"mha_hero_tools-{version}.zip")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(PKG):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            full = os.path.join(root, f)
            z.write(full, os.path.relpath(full, PKG))   # manifest at zip root
print("built", out)
