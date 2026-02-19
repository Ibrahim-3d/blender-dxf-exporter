import os
import bpy


class SVGTODWG_PT_export_panel(bpy.types.Panel):
    """Sidebar panel — 3D Viewport N-panel > DXF Export tab."""

    bl_label       = "DXF / DWG Export"
    bl_idname      = "SVGTODWG_PT_export_panel"
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI"
    bl_category    = "DXF Export"

    def draw(self, context):
        layout   = self.layout
        settings = context.scene.dxf_export_settings

        layout.use_property_split    = True
        layout.use_property_decorate = False

        # ── Output format ─────────────────────────────────────────────────
        box = layout.box()
        box.label(text="Output Format", icon="FILE_BLANK")
        box.prop(settings, "output_format")
        if settings.output_format == "DWG":
            from . import dxf_writer
            try:
                prefs   = context.preferences.addons[__package__].preferences
                manual  = prefs.dxf2dwg_path.strip()
            except Exception:
                manual = ""
            exe = (manual if manual and os.path.isfile(manual)
                   else dxf_writer.find_dxf2dwg() or "")
            icon = "CHECKMARK" if exe else "ERROR"
            msg  = "LibreDWG: ready" if exe else "LibreDWG: dxf2dwg not found (see Preferences)"
            box.label(text=msg, icon=icon)

        # ── Source objects ─────────────────────────────────────────────────
        box2 = layout.box()
        box2.label(text="Source Objects", icon="OBJECT_DATA")
        box2.prop(settings, "objects_to_export")
        box2.prop(settings, "use_world_matrix")

        # ── Scale / Units ─────────────────────────────────────────────────
        box3 = layout.box()
        box3.label(text="Scale & Units", icon="EMPTY_ARROWS")
        box3.prop(settings, "scale")
        box3.prop(settings, "units")

        # ── Layers ────────────────────────────────────────────────────────
        box4 = layout.box()
        box4.label(text="Layers", icon="RENDERLAYERS")
        box4.prop(settings, "layer_mode")

        # ── Curve output ─────────────────────────────────────────────────
        box5 = layout.box()
        box5.label(text="Curve Output", icon="CURVE_DATA")
        box5.prop(settings, "output_splines")
        if not settings.output_splines:
            box5.prop(settings, "tessellation_samples")

        # ── Export button ─────────────────────────────────────────────────
        layout.separator()
        label = "Export DXF" if settings.output_format == "DXF" else "Export DWG"
        layout.operator("svgtodwg.export_dxf", text=label, icon="EXPORT")


classes = (SVGTODWG_PT_export_panel,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
