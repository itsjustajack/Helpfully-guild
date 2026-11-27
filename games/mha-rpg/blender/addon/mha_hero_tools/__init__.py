"""MHA Hero Tools: buttons that run the MHA RPG builder scripts.

Panel: 3D View > N side panel > "MHA Hero" tab.
Each button runs one builder script bundled in ./builders (the same scripts
as games/mha-rpg/blender/*.py). Every builder only replaces its own collection.
"""
import os
import runpy

import bpy

BUILDERS = os.path.join(os.path.dirname(__file__), "builders")

# (enum id, button label, script file, description) in the order to click them
PARTS = [
    ("BODY", "1. Male Base Body", "male_base.py", "Build the locked base body (bald, A-pose)"),
    ("HAND", "2. Test Hand", "hand_base.py", "Build the right test hand at the origin"),
    ("GAUNTLET", "3. Mid-Gauntlet", "mid_gauntlet.py", "Build the Mid-Gauntlet support gear"),
    ("GLOVE", "4. Hero Glove", "hero_glove.py", "Fit the hero glove to the test hand (needs step 2)"),
    ("TOON", "5. Anime Look", "toon_look.py", "Cel shader + ink outline on the body (needs step 1)"),
]
_SCRIPTS = {p[0]: p[2] for p in PARTS}


class MHA_OT_build(bpy.types.Operator):
    """Run one MHA builder script"""
    bl_idname = "mha_hero.build"
    bl_label = "Build MHA Part"
    bl_options = {"REGISTER", "UNDO"}

    part: bpy.props.EnumProperty(
        name="Part",
        items=[(p[0], p[1], p[3]) for p in PARTS],
    )

    def execute(self, context):
        path = os.path.join(BUILDERS, _SCRIPTS[self.part])
        if not os.path.isfile(path):
            self.report({"ERROR"}, f"Missing builder file: {os.path.basename(path)}")
            return {"CANCELLED"}
        if context.object and context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        try:
            runpy.run_path(path, run_name="__mha_builder__")
        except SystemExit as e:          # builders exit with a message when a step is missing
            self.report({"WARNING"}, str(e))
            return {"CANCELLED"}
        self.report({"INFO"}, f"Built: {self.part.title()}")
        return {"FINISHED"}


class MHA_PT_panel(bpy.types.Panel):
    bl_label = "MHA Hero Tools"
    bl_idname = "MHA_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MHA Hero"

    def draw(self, context):
        col = self.layout.column(align=True)
        for pid, label, _f, _d in PARTS:
            col.operator(MHA_OT_build.bl_idname, text=label).part = pid
        self.layout.label(text="Tip: press period (.) on the numpad to zoom to it")


classes = (MHA_OT_build, MHA_PT_panel)


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
