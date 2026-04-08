import os
import bpy
from . import dxf_writer


class SVGTODWG_AP_preferences(bpy.types.AddonPreferences):
    """
    Addon-level settings (Edit > Preferences > Add-ons > DXF/DWG Exporter).
    Persists across all .blend files.
    """

    bl_idname = __package__

    dxf2dwg_path: bpy.props.StringProperty(
        name="dxf2dwg Executable",
        description="Path to LibreDWG's dxf2dwg executable.\n"
                    "Leave empty to auto-detect (bundled bin/ folder or system PATH).\n"
                    "Download from: https://github.com/LibreDWG/libredwg/releases",
        subtype="FILE_PATH",
        default="",
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split    = True
        layout.use_property_decorate = False

        box = layout.box()
        box.label(text="DWG Conversion — LibreDWG (GPLv3+, open source)", icon="FILE_BLEND")

        col = box.column(align=True)
        col.prop(self, "dxf2dwg_path")

        row = col.row()
        row.operator("svgtodwg.detect_dxf2dwg", icon="VIEWZOOM", text="Auto-detect")

        # Status
        exe = self._resolve_exe()
        if exe:
            col.label(text=f"Ready: {exe}", icon="CHECKMARK")
        else:
            col.label(text="Not found — DWG export unavailable", icon="INFO")

        box.separator()
        box.label(text="Setup options (pick one):", icon="QUESTION")
        col2 = box.column(align=True)
        col2.label(text="A)  Download libredwg-*-win64.zip from the GitHub releases page,")
        col2.label(text="     extract, and place dxf2dwg.exe + DLLs into this addon's bin/ folder.")
        col2.label(text="B)  Set the path above to where you extracted dxf2dwg.exe.")

    def _resolve_exe(self):
        """Return the usable exe path or None."""
        manual = self.dxf2dwg_path.strip()
        if manual and os.path.isfile(manual):
            return manual
        return dxf_writer.find_dxf2dwg()


class SVGTODWG_OT_detect_dxf2dwg(bpy.types.Operator):
    """Search for dxf2dwg in the addon's bin/ folder and system PATH"""

    bl_idname  = "svgtodwg.detect_dxf2dwg"
    bl_label   = "Auto-detect dxf2dwg"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        path = dxf_writer.find_dxf2dwg()
        if path:
            prefs = context.preferences.addons[__package__].preferences
            prefs.dxf2dwg_path = path
            self.report({"INFO"}, f"Found: {path}")
        else:
            self.report(
                {"WARNING"},
                "dxf2dwg not found. Download LibreDWG from "
                "github.com/LibreDWG/libredwg/releases and place "
                "dxf2dwg.exe in the addon's bin/ folder.",
            )
        return {"FINISHED"}


classes = (
    SVGTODWG_AP_preferences,
    SVGTODWG_OT_detect_dxf2dwg,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
