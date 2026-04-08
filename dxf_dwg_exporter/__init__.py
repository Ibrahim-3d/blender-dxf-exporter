bl_info = {
    "name":        "DXF / DWG Exporter — Curves & Grease Pencil",
    "author":      "Ibrahim-3d",
    "version":     (1, 1, 0),
    "blender":     (3, 6, 0),
    "location":    "File > Export > AutoCAD DXF / DWG  |  3D Viewport > Sidebar > DXF Export",
    "description": "Export Blender Curve and Grease Pencil objects to AutoCAD DXF (or DWG via "
                   "LibreDWG). No external dependencies for DXF output.",
    "category":    "Import-Export",
}

# ── Hot-reload support (Blender F3 > Reload Scripts) ─────────────────────────
if "bpy" in locals():
    import importlib
    importlib.reload(properties)
    importlib.reload(preferences)
    importlib.reload(operators)
    importlib.reload(panels)
    importlib.reload(dxf_writer)
else:
    from . import properties
    from . import preferences
    from . import operators
    from . import panels
    from . import dxf_writer

import bpy


def register():
    properties.register()
    preferences.register()   # preferences before operators (operators reference prefs)
    operators.register()
    panels.register()


def unregister():
    panels.unregister()
    operators.unregister()
    preferences.unregister()
    properties.unregister()


if __name__ == "__main__":
    register()
