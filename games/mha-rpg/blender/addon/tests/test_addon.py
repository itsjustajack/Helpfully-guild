"""Headless test of the built add-on zip (run with a Python that has `bpy`).

    python -I games/mha-rpg/blender/addon/tests/test_addon.py
"""
import importlib
import os
import sys
import tempfile
import zipfile

import bpy

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ZIP = os.path.join(HERE, "..", "mha_hero_tools-1.0.0.zip")

tmp = tempfile.mkdtemp()
pkg_dir = os.path.join(tmp, "mha_hero_tools")
with zipfile.ZipFile(ZIP) as z:
    z.extractall(pkg_dir)
sys.path.insert(0, tmp)
addon = importlib.import_module("mha_hero_tools")

bpy.ops.wm.read_factory_settings(use_empty=True)
addon.register()
ok = []


def check(name, cond):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + name)


# glove before hand must refuse politely, not crash
check("glove without hand is refused", bpy.ops.mha_hero.build(part="GLOVE") == {"CANCELLED"})
check("toon without body is refused", bpy.ops.mha_hero.build(part="TOON") == {"CANCELLED"})

expect = {"BODY": "MaleBase", "HAND": "HandBase", "GAUNTLET": "MidGauntlet", "GLOVE": "HeroGlove"}
for part, colname in expect.items():
    res = bpy.ops.mha_hero.build(part=part)
    check(f"{part} builds", res == {"FINISHED"} and colname in bpy.data.collections)

check("TOON applies", bpy.ops.mha_hero.build(part="TOON") == {"FINISHED"}
      and "InkOutline" in bpy.data.objects["SM_MaleBase"].modifiers)

# rebuilding replaces, never duplicates
before = len(bpy.data.objects)
bpy.ops.mha_hero.build(part="GAUNTLET")
check("rebuild does not duplicate", len(bpy.data.objects) == before)

check("panel registered", hasattr(bpy.types, "MHA_PT_panel"))
addon.unregister()
check("unregister clean", not hasattr(bpy.types, "MHA_PT_panel"))

print(f"{sum(ok)}/{len(ok)} passed")
sys.exit(0 if all(ok) else 1)
