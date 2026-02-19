import bpy
import os

_EXPORTABLE = {"CURVE", "GPENCIL", "GREASEPENCIL"}


class SVGTODWG_OT_export_dxf(bpy.types.Operator):
    """Export Curve and Grease Pencil objects to AutoCAD DXF or DWG format"""

    bl_idname  = "svgtodwg.export_dxf"
    bl_label   = "Export AutoCAD DXF / DWG"
    bl_options = {"REGISTER"}

    filepath:    bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(
        default="*.dxf;*.dwg", options={"HIDDEN"}
    )
    filename_ext = ".dxf"

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def invoke(self, context, event):
        settings = context.scene.dxf_export_settings
        ext = ".dwg" if settings.output_format == "DWG" else ".dxf"
        blend_name = os.path.splitext(bpy.path.basename(bpy.data.filepath))[0]
        self.filepath = (blend_name or "export") + ext
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def draw(self, context):
        layout   = self.layout
        settings = context.scene.dxf_export_settings

        layout.use_property_split    = True
        layout.use_property_decorate = False

        col = layout.column(align=True)
        col.prop(settings, "objects_to_export")
        col.prop(settings, "use_world_matrix")

        layout.separator()

        col2 = layout.column(align=True)
        col2.prop(settings, "output_format")

        layout.separator()

        col3 = layout.column(align=True)
        col3.prop(settings, "scale")
        col3.prop(settings, "units")

        layout.separator()
        layout.prop(settings, "layer_mode")

        layout.separator()

        col5 = layout.column(align=True)
        col5.prop(settings, "output_splines")
        if not settings.output_splines:
            col5.prop(settings, "tessellation_samples")

    # ── execute ───────────────────────────────────────────────────────────────

    def execute(self, context):
        from . import dxf_writer

        settings = context.scene.dxf_export_settings
        mode     = settings.objects_to_export
        fmt      = settings.output_format

        # Gather objects
        if mode == "SELECTED":
            objects = [o for o in context.selected_objects if o.type in _EXPORTABLE]
        elif mode == "VISIBLE":
            objects = [o for o in context.visible_objects  if o.type in _EXPORTABLE]
        else:
            objects = [o for o in context.scene.objects    if o.type in _EXPORTABLE]

        if not objects:
            self.report(
                {"WARNING"},
                "No exportable objects — select Curve or Grease Pencil objects",
            )
            return {"CANCELLED"}

        # ── DXF output ────────────────────────────────────────────────────
        if fmt == "DXF":
            filepath = bpy.path.ensure_ext(self.filepath, ".dxf")
            try:
                dxf_writer.export_dxf(filepath, objects, settings)
            except Exception as exc:
                self.report({"ERROR"}, f"DXF export failed: {exc}")
                return {"CANCELLED"}

            self.report(
                {"INFO"},
                f"Exported {len(objects)} object(s) → {os.path.basename(filepath)}",
            )
            return {"FINISHED"}

        # ── DWG output (via LibreDWG dxf2dwg) ────────────────────────────
        # Resolve dxf2dwg executable: preference path → bundled → PATH
        try:
            prefs = context.preferences.addons[__package__].preferences
            manual = prefs.dxf2dwg_path.strip()
        except Exception:
            manual = ""

        dxf2dwg_exe = ""
        if manual and os.path.isfile(manual):
            dxf2dwg_exe = manual
        else:
            dxf2dwg_exe = dxf_writer.find_dxf2dwg() or ""

        if not dxf2dwg_exe:
            self.report(
                {"ERROR"},
                "dxf2dwg (LibreDWG) not found.\n"
                "Download from github.com/LibreDWG/libredwg/releases, "
                "extract dxf2dwg.exe + DLLs into this addon's bin/ folder, "
                "or set the path in Preferences.",
            )
            return {"CANCELLED"}

        dwg_path = bpy.path.ensure_ext(self.filepath, ".dwg")

        # Step 1: write intermediate DXF
        dxf_tmp = os.path.splitext(dwg_path)[0] + "_tmp_export.dxf"
        try:
            dxf_writer.export_dxf(dxf_tmp, objects, settings)
        except Exception as exc:
            self.report({"ERROR"}, f"DXF write step failed: {exc}")
            return {"CANCELLED"}

        # Step 2: convert DXF → DWG
        try:
            dxf_writer.convert_dxf_to_dwg(dxf_tmp, dwg_path, dxf2dwg_exe)
        except Exception as exc:
            self.report({"ERROR"}, f"DWG conversion failed: {exc}")
            return {"CANCELLED"}
        finally:
            if os.path.isfile(dxf_tmp):
                os.remove(dxf_tmp)

        self.report(
            {"INFO"},
            f"Exported {len(objects)} object(s) → {os.path.basename(dwg_path)} (DWG)",
        )
        return {"FINISHED"}


# ── File > Export menu ────────────────────────────────────────────────────────

def _menu_func_export(self, context):
    self.layout.operator(
        SVGTODWG_OT_export_dxf.bl_idname,
        text="AutoCAD DXF / DWG",
        icon="EXPORT",
    )


classes = (SVGTODWG_OT_export_dxf,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_export.append(_menu_func_export)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(_menu_func_export)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
