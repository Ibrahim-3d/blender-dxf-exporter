import bpy


class SVGTODWG_PG_export_settings(bpy.types.PropertyGroup):
    """Export settings stored on the Scene so they persist per .blend file."""

    objects_to_export: bpy.props.EnumProperty(
        name="Objects",
        description="Which objects to include in the export",
        items=[
            ("SELECTED", "Selected",     "Export selected objects only"),
            ("VISIBLE",  "Visible",       "Export all visible objects"),
            ("ALL",      "All in Scene",  "Export every object in the scene"),
        ],
        default="SELECTED",
    )

    output_format: bpy.props.EnumProperty(
        name="Output Format",
        description="File format to produce.\n"
                    "DXF  — text-based, opens in AutoCAD just like DWG.\n"
                    "DWG  — binary Autodesk format; requires ODA File Converter "
                    "(free) configured in addon Preferences",
        items=[
            ("DXF", "DXF (.dxf)",
             "AutoCAD Drawing Exchange Format — opens natively in AutoCAD"),
            ("DWG", "DWG (.dwg) via LibreDWG",
             "True binary DWG (R2000) — requires LibreDWG's dxf2dwg, "
             "see addon Preferences for setup"),
        ],
        default="DXF",
    )

    scale: bpy.props.FloatProperty(
        name="Scale",
        description="Multiply all coordinates by this factor.\n"
                    "E.g. if 1 Blender unit = 1 mm, keep at 1.0 with Units = MM",
        default=1.0,
        min=0.0001,
        max=100000.0,
        precision=4,
        step=10,
    )

    units: bpy.props.EnumProperty(
        name="Units",
        description="Unit system recorded in the DXF header ($INSUNITS).\n"
                    "Tells AutoCAD how to interpret the coordinate values",
        items=[
            ("MM",     "Millimeters", ""),
            ("CM",     "Centimeters", ""),
            ("M",      "Meters",      ""),
            ("INCHES", "Inches",      ""),
            ("FEET",   "Feet",        ""),
        ],
        default="MM",
    )

    layer_mode: bpy.props.EnumProperty(
        name="Layers",
        description="How to assign DXF layer names",
        items=[
            ("SINGLE",        "Single (layer 0)",  "All geometry on the default layer"),
            ("BY_OBJECT",     "By Object Name",    "Each object gets its own layer"),
            ("BY_COLLECTION", "By Collection",     "Each collection maps to a layer"),
        ],
        default="SINGLE",
    )

    output_splines: bpy.props.BoolProperty(
        name="Export as Splines",
        description="Export Bezier / NURBS curves as DXF SPLINE entities (AutoCAD 2000+).\n"
                    "Disable to convert curves to polylines for maximum compatibility",
        default=True,
    )

    tessellation_samples: bpy.props.IntProperty(
        name="Samples per Segment",
        description="Line segments per Bezier segment when 'Export as Splines' is disabled",
        default=12,
        min=2,
        max=256,
    )

    use_world_matrix: bpy.props.BoolProperty(
        name="Apply Object Transform",
        description="Apply each object's location, rotation, and scale before exporting",
        default=True,
    )


classes = (SVGTODWG_PG_export_settings,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.dxf_export_settings = bpy.props.PointerProperty(
        type=SVGTODWG_PG_export_settings
    )


def unregister():
    del bpy.types.Scene.dxf_export_settings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
