# Blender Addon Development - Complete Documentation Reference

> Compiled from official Blender docs and community resources.
> Covers both the legacy `bl_info` system and the new Blender 4.2+ Extension system.

---

## Table of Contents

1. [Addon vs Extension (Blender 4.2+)](#1-addon-vs-extension-blender-42)
2. [Project Structure](#2-project-structure)
3. [bl_info Dictionary (Legacy)](#3-bl_info-dictionary-legacy)
4. [blender_manifest.toml (Extensions)](#4-blender_manifesttoml-extensions)
5. [Register / Unregister](#5-register--unregister)
6. [Operators](#6-operators)
7. [Panels](#7-panels)
8. [Properties (bpy.props)](#8-properties-bpyprops)
9. [PropertyGroup](#9-propertygroup)
10. [Addon Preferences](#10-addon-preferences)
11. [UI Layout System](#11-ui-layout-system)
12. [Menus & Keymap Integration](#12-menus--keymap-integration)
13. [Multi-File Addon Structure](#13-multi-file-addon-structure)
14. [Modal Operators & Timers](#14-modal-operators--timers)
15. [Gotchas & Common Pitfalls](#15-gotchas--common-pitfalls)
16. [Best Practices](#16-best-practices)
17. [Development Environment Setup](#17-development-environment-setup)
18. [Complete Minimal Example](#18-complete-minimal-example)
19. [Complete Multi-File Example](#19-complete-multi-file-example)
20. [Key API Reference Links](#20-key-api-reference-links)

---

## 1. Addon vs Extension (Blender 4.2+)

Starting with **Blender 4.2**, the new **Extensions system** replaces the legacy addon system for distribution. Extensions use `blender_manifest.toml` instead of `bl_info`.

| Feature | Legacy Addon | Extension (4.2+) |
|---------|-------------|-------------------|
| Metadata | `bl_info` dict in `__init__.py` | `blender_manifest.toml` file |
| Distribution | ZIP file | Extensions platform / ZIP |
| Dependencies | Manual | Bundled Python wheels |
| Permissions | None | Declared (files, network, etc.) |
| Compatibility | All Blender versions | Blender 4.2+ |

**You can support both** by including both `bl_info` and `blender_manifest.toml` in your addon.

---

## 2. Project Structure

### Single-File Addon
```
my_addon.py          # Everything in one file
```

### Multi-File Addon (Package)
```
my_addon/
    __init__.py           # bl_info + register/unregister + imports
    blender_manifest.toml # Extension manifest (Blender 4.2+)
    operators.py          # Operator classes
    panels.py             # Panel classes
    properties.py         # PropertyGroup classes
    preferences.py        # AddonPreferences class
    utils.py              # Helper functions
```

### Larger Addon Structure
```
my_addon/
    __init__.py
    blender_manifest.toml
    operators/
        __init__.py
        mesh_ops.py
        object_ops.py
    panels/
        __init__.py
        main_panel.py
        settings_panel.py
    properties/
        __init__.py
        scene_props.py
        object_props.py
    utils/
        __init__.py
        math_utils.py
        file_utils.py
```

---

## 3. bl_info Dictionary (Legacy)

```python
bl_info = {
    "name": "My Addon Name",
    "author": "Your Name",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),          # Minimum Blender version (major, minor, patch)
    "location": "View3D > Sidebar > My Tab",  # Where to find in UI
    "description": "Short description of what the addon does",
    "warning": "",                  # Optional warning text
    "doc_url": "",                  # Documentation URL
    "tracker_url": "",              # Bug tracker URL
    "category": "Object",          # Category for Preferences > Add-ons
}
```

### Valid Categories
`3D View`, `Add Curve`, `Add Mesh`, `Animation`, `Compositing`, `Development`,
`Game Engine`, `Import-Export`, `Lighting`, `Material`, `Mesh`, `Node`,
`Object`, `Paint`, `Physics`, `Render`, `Rigging`, `Scene`, `Sequencer`,
`System`, `Text Editor`, `UV`

---

## 4. blender_manifest.toml (Extensions)

```toml
schema_version = "1.0.0"

# Required fields
id = "my_addon_name"
version = "1.0.0"
name = "My Addon Name"
tagline = "Short description up to 64 chars, no ending punctuation"
maintainer = "Your Name <email@example.com>"
type = "add-on"

# License (SPDX format)
license = [
    "SPDX:GPL-3.0-or-later",
]

# Minimum Blender version
blender_version_min = "4.2.0"

# Optional: Maximum Blender version (exclusive - this version is NOT supported)
# blender_version_max = "5.1.0"

# Optional fields
website = "https://example.com"
copyright = [
    "2024 Your Name",
]

# Tags (predefined by Blender)
tags = ["Object", "Mesh"]

# Platforms (omit for all platforms)
# platforms = ["windows-x64", "macos-arm64", "linux-x64"]

# Python wheel dependencies
# wheels = ["./wheels/some_package-1.0.0-py3-none-any.whl"]

# Permissions - declare what your addon needs
# [permissions]
# files = "Import/export functionality"
# network = "Check for updates"
# clipboard = "Copy results to clipboard"
# camera = "Access webcam"
# microphone = "Access microphone"
```

### Valid Extension Tags
`3D View`, `Add Curve`, `Add Mesh`, `Animation`, `Bake`, `Camera`,
`Compositing`, `Development`, `Geometry Nodes`, `Grease Pencil`,
`Import-Export`, `Lighting`, `Material`, `Mesh`, `Modeling`, `Node`,
`Object`, `Paint`, `Physics`, `Render`, `Rigging`, `Scene`, `Sculpt`,
`Sequencer`, `Text Editor`, `Tracking`, `User Interface`, `UV`

---

## 5. Register / Unregister

Every addon must have `register()` and `unregister()` functions.

```python
import bpy

# List all classes to register
classes = (
    MY_OT_my_operator,
    MY_PT_my_panel,
    MyPropertyGroup,
    MyAddonPreferences,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # Register properties AFTER classes
    bpy.types.Scene.my_props = bpy.props.PointerProperty(type=MyPropertyGroup)

def unregister():
    # Unregister properties BEFORE classes
    del bpy.types.Scene.my_props

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
```

### Class Naming Convention
Blender enforces naming: `{ADDON}_{TYPE}_{name}`

| Type Code | Class Type |
|-----------|-----------|
| `OT` | Operator |
| `PT` | Panel |
| `MT` | Menu |
| `UL` | UIList |
| `HT` | Header |
| `KM` | KeyMap |

Example: `MYADDON_OT_do_something`, `MYADDON_PT_main_panel`

---

## 6. Operators

Operators are the primary way to execute actions in Blender.

```python
import bpy

class MYADDON_OT_simple_operator(bpy.types.Operator):
    """Tooltip description for this operator"""
    bl_idname = "myaddon.simple_operator"     # Unique ID (category.name)
    bl_label = "Do Something"                  # Display name
    bl_description = "Detailed description"    # Tooltip (overrides docstring)
    bl_options = {'REGISTER', 'UNDO'}          # Options set

    # --- Operator Properties (shown in F9 redo panel) ---
    my_float: bpy.props.FloatProperty(
        name="Value",
        default=1.0,
        min=0.0,
        max=10.0,
    )
    my_enum: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ('OPT_A', "Option A", "First option"),
            ('OPT_B', "Option B", "Second option"),
        ],
        default='OPT_A',
    )

    @classmethod
    def poll(cls, context):
        """Controls when the operator is available (grayed out if False)"""
        return context.active_object is not None

    def invoke(self, context, event):
        """Called when operator is triggered by user (before execute).
        Use for dialogs, file browsers, or getting mouse position."""
        # Open a properties dialog
        return context.window_manager.invoke_props_dialog(self)
        # Or just run execute:
        # return self.execute(context)

    def execute(self, context):
        """Main operator logic. Must return a status set."""
        obj = context.active_object
        obj.location.x += self.my_float
        self.report({'INFO'}, f"Moved {obj.name}")
        return {'FINISHED'}

    def draw(self, context):
        """Custom layout for the operator properties popup"""
        layout = self.layout
        layout.prop(self, "my_float")
        layout.prop(self, "my_enum")
```

### Operator Return Values
| Value | Meaning |
|-------|---------|
| `{'FINISHED'}` | Operator completed successfully |
| `{'CANCELLED'}` | Operator was cancelled |
| `{'RUNNING_MODAL'}` | Operator is running in modal mode |
| `{'PASS_THROUGH'}` | Pass the event to other operators |
| `{'INTERFACE'}` | Operator handled but no changes to undo |

### bl_options Flags
| Flag | Meaning |
|------|---------|
| `REGISTER` | Display in info window and support redo |
| `UNDO` | Push an undo step after execution |
| `UNDO_GROUPED` | Group undo pushes |
| `BLOCKING` | Block anything else from using the cursor |
| `MACRO` | Use to define a macro operator |
| `GRAB_CURSOR` | Grab the mouse cursor during execution |
| `GRAB_CURSOR_X` | Grab cursor X only |
| `GRAB_CURSOR_Y` | Grab cursor Y only |
| `PRESET` | Display a preset button |
| `INTERNAL` | Remove from search results |

### Invoke Helpers
```python
# Property dialog popup
return context.window_manager.invoke_props_dialog(self)

# Confirm dialog
return context.window_manager.invoke_confirm(self, event)

# File browser
return context.window_manager.invoke_props_popup(self, event)

# Use for file select operators:
context.window_manager.fileselect_add(self)
return {'RUNNING_MODAL'}
```

---

## 7. Panels

Panels define UI sections in Blender's interface.

```python
class MYADDON_PT_main_panel(bpy.types.Panel):
    bl_label = "My Addon"                  # Panel header text
    bl_idname = "MYADDON_PT_main_panel"    # Unique ID
    bl_space_type = 'VIEW_3D'              # Which editor
    bl_region_type = 'UI'                  # Which region
    bl_category = "My Tab"                 # Sidebar tab name
    bl_context = "objectmode"              # Optional: only show in this mode
    bl_options = {'DEFAULT_CLOSED'}        # Optional: collapsed by default

    @classmethod
    def poll(cls, context):
        """Control when panel is visible"""
        return context.active_object is not None

    def draw_header(self, context):
        """Draw in the panel header (e.g., a checkbox)"""
        layout = self.layout
        layout.label(icon='OBJECT_DATA')

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Draw properties and operators
        layout.prop(scene.my_props, "my_property")
        layout.operator("myaddon.simple_operator")
```

### Sub-Panels
```python
class MYADDON_PT_sub_panel(bpy.types.Panel):
    bl_label = "Sub Settings"
    bl_idname = "MYADDON_PT_sub_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "My Tab"
    bl_parent_id = "MYADDON_PT_main_panel"   # Makes this a sub-panel
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text="Sub panel content")
```

### Common Space Types
| bl_space_type | Editor |
|---------------|--------|
| `VIEW_3D` | 3D Viewport |
| `PROPERTIES` | Properties Editor |
| `NODE_EDITOR` | Node Editor |
| `IMAGE_EDITOR` | Image/UV Editor |
| `SEQUENCE_EDITOR` | Video Sequencer |
| `CLIP_EDITOR` | Movie Clip Editor |
| `TEXT_EDITOR` | Text Editor |
| `DOPESHEET_EDITOR` | Dope Sheet |
| `GRAPH_EDITOR` | Graph Editor |
| `NLA_EDITOR` | NLA Editor |
| `OUTLINER` | Outliner |
| `FILE_BROWSER` | File Browser |
| `PREFERENCES` | Preferences |

### Common Region Types
| bl_region_type | Region |
|----------------|--------|
| `UI` | Sidebar (N-panel) |
| `TOOLS` | Tool shelf (T-panel) |
| `HEADER` | Header bar |
| `WINDOW` | Main window area |
| `TOOL_HEADER` | Tool header |

### Properties Editor Contexts (bl_context)
`objectmode`, `mesh_edit`, `curve_edit`, `surface_edit`, `text_edit`,
`armature_edit`, `pose_mode`, `particle_edit`, `weightpaint`,
`vertexpaint`, `texturepaint`, `sculpt_mode`

For Properties editor panels:
`scene`, `world`, `object`, `modifier`, `particle`, `physics`,
`constraint`, `data`, `material`, `texture`, `render`, `output`

---

## 8. Properties (bpy.props)

All property types and their parameters:

### BoolProperty
```python
my_bool: bpy.props.BoolProperty(
    name="Enable",                    # Display name
    description="Toggle feature",     # Tooltip
    default=False,                    # Default value
    options={'ANIMATABLE'},           # Options set
    subtype='NONE',                   # Subtype
    update=None,                      # Callback: update(self, context)
)
```

### IntProperty
```python
my_int: bpy.props.IntProperty(
    name="Count",
    description="Number of items",
    default=1,
    min=0,                            # Hard minimum
    max=100,                          # Hard maximum
    soft_min=0,                       # Soft minimum (UI slider range)
    soft_max=50,                      # Soft maximum (UI slider range)
    step=1,                           # Increment step
    subtype='NONE',                   # 'PIXEL', 'UNSIGNED', 'PERCENTAGE', 'FACTOR', 'ANGLE', 'TIME', 'DISTANCE'
    update=None,
)
```

### FloatProperty
```python
my_float: bpy.props.FloatProperty(
    name="Scale",
    description="Scaling factor",
    default=1.0,
    min=0.0,
    max=100.0,
    soft_min=0.0,
    soft_max=10.0,
    step=10,                          # Step (divided by 100 in UI)
    precision=3,                      # Decimal places displayed
    subtype='NONE',                   # 'PIXEL', 'UNSIGNED', 'PERCENTAGE', 'FACTOR', 'ANGLE', 'TIME', 'DISTANCE', 'TEMPERATURE'
    unit='NONE',                      # 'LENGTH', 'AREA', 'VOLUME', 'ROTATION', 'TIME', 'VELOCITY', 'ACCELERATION', 'MASS', 'CAMERA', 'POWER'
    update=None,
)
```

### StringProperty
```python
my_string: bpy.props.StringProperty(
    name="Name",
    description="Enter a name",
    default="",
    maxlen=256,                       # Max character length
    subtype='NONE',                   # 'FILE_PATH', 'DIR_PATH', 'FILE_NAME', 'BYTE_STRING', 'PASSWORD', 'NONE'
    update=None,
)
```

### EnumProperty
```python
my_enum: bpy.props.EnumProperty(
    name="Mode",
    description="Select mode",
    items=[
        # (identifier, name, description, icon, number)
        ('OPTION_A', "Option A", "Description for A", 'MESH_CUBE', 0),
        ('OPTION_B', "Option B", "Description for B", 'MESH_SPHERE', 1),
        ('OPTION_C', "Option C", "Description for C", 'MESH_CONE', 2),
    ],
    default='OPTION_A',
    update=None,
)

# Dynamic enum items via callback:
def get_enum_items(self, context):
    items = []
    for i, obj in enumerate(context.scene.objects):
        items.append((obj.name, obj.name, "", i))
    return items

my_dynamic_enum: bpy.props.EnumProperty(
    name="Object",
    items=get_enum_items,
)

# Flag enum (multiple selection):
my_flags: bpy.props.EnumProperty(
    name="Flags",
    items=[...],
    options={'ENUM_FLAG'},
    default={'OPTION_A', 'OPTION_C'},
)
```

### FloatVectorProperty
```python
my_color: bpy.props.FloatVectorProperty(
    name="Color",
    description="Pick a color",
    default=(1.0, 1.0, 1.0),
    min=0.0,
    max=1.0,
    subtype='COLOR',                  # 'COLOR', 'TRANSLATION', 'DIRECTION', 'VELOCITY', 'ACCELERATION', 'EULER', 'QUATERNION', 'XYZ', 'COLOR_GAMMA', 'LAYER', 'LAYER_MEMBER', 'NONE'
    size=3,                           # Number of components (2-4, or up to 32)
)

my_vector: bpy.props.FloatVectorProperty(
    name="Position",
    subtype='TRANSLATION',
    size=3,
)
```

### IntVectorProperty
```python
my_ivec: bpy.props.IntVectorProperty(
    name="Dimensions",
    default=(1, 1, 1),
    min=0,
    size=3,
)
```

### BoolVectorProperty
```python
my_bvec: bpy.props.BoolVectorProperty(
    name="Axes",
    default=(True, True, False),
    size=3,
    subtype='XYZ',
)
```

### PointerProperty
```python
my_object: bpy.props.PointerProperty(
    name="Target",
    description="Reference to an object",
    type=bpy.types.Object,            # Can be Object, Material, Image, etc.
    poll=None,                         # Optional filter callback
)
```

### CollectionProperty
```python
my_collection: bpy.props.CollectionProperty(
    type=MyPropertyGroup,              # Must be a PropertyGroup subclass
)
```

### Common Property Options
| Option | Meaning |
|--------|---------|
| `HIDDEN` | Don't show in UI |
| `SKIP_SAVE` | Don't save in .blend file |
| `ANIMATABLE` | Allow animation keyframes |
| `LIBRARY_EDITABLE` | Allow editing from linked data |
| `PROPORTIONAL` | (internal) |
| `ENUM_FLAG` | Allow multiple enum selections |

### Update Callbacks
```python
def my_update_callback(self, context):
    """Called whenever the property value changes"""
    print(f"Value changed to: {self.my_property}")
    # Trigger redraw if needed
    if context.area:
        context.area.tag_redraw()

my_property: bpy.props.FloatProperty(
    name="Value",
    update=my_update_callback,
)
```

---

## 9. PropertyGroup

Group multiple properties together for organization and reuse.

```python
class MySettings(bpy.types.PropertyGroup):
    """A group of properties for this addon"""

    enabled: bpy.props.BoolProperty(
        name="Enabled",
        default=True,
    )
    count: bpy.props.IntProperty(
        name="Count",
        default=5,
        min=1,
        max=100,
    )
    mode: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ('FAST', "Fast", "Quick processing"),
            ('QUALITY', "Quality", "High quality processing"),
        ],
    )
```

### Where to Attach PropertyGroups

```python
def register():
    bpy.utils.register_class(MySettings)

    # Attach to Scene (shared across all objects, saved in .blend)
    bpy.types.Scene.my_settings = bpy.props.PointerProperty(type=MySettings)

    # Attach to Object (per-object settings, saved in .blend)
    bpy.types.Object.my_settings = bpy.props.PointerProperty(type=MySettings)

    # Attach to WindowManager (temporary, NOT saved in .blend)
    bpy.types.WindowManager.my_settings = bpy.props.PointerProperty(type=MySettings)

    # Attach to Mesh (per-mesh data)
    bpy.types.Mesh.my_settings = bpy.props.PointerProperty(type=MySettings)

    # Attach to Material (per-material)
    bpy.types.Material.my_settings = bpy.props.PointerProperty(type=MySettings)

def unregister():
    del bpy.types.Scene.my_settings
    # del bpy.types.Object.my_settings  # etc.
    bpy.utils.unregister_class(MySettings)
```

### Accessing Properties
```python
# In operator execute():
settings = context.scene.my_settings
print(settings.count)

# In panel draw():
layout.prop(context.scene.my_settings, "enabled")
layout.prop(context.scene.my_settings, "count")
```

### Nested PropertyGroups
```python
class InnerGroup(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name="Value")

class OuterGroup(bpy.types.PropertyGroup):
    inner: bpy.props.PointerProperty(type=InnerGroup)
    name: bpy.props.StringProperty(name="Name")

# Register InnerGroup BEFORE OuterGroup
```

### CollectionProperty with PropertyGroup
```python
class ListItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    value: bpy.props.IntProperty(name="Value")

# In register:
bpy.types.Scene.my_list = bpy.props.CollectionProperty(type=ListItem)
bpy.types.Scene.my_list_index = bpy.props.IntProperty(name="Index", default=0)

# Add/remove items:
item = context.scene.my_list.add()
item.name = "New Item"
item.value = 42

context.scene.my_list.remove(index)
context.scene.my_list.move(old_index, new_index)
```

---

## 10. Addon Preferences

Persistent settings accessible from Edit > Preferences > Add-ons.

```python
class MyAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__  # Must match addon module name

    # Preference properties
    filepath: bpy.props.StringProperty(
        name="Default Path",
        subtype='DIR_PATH',
        default="",
    )
    debug_mode: bpy.props.BoolProperty(
        name="Debug Mode",
        default=False,
    )
    quality: bpy.props.EnumProperty(
        name="Quality",
        items=[
            ('LOW', "Low", "Fast but lower quality"),
            ('HIGH', "High", "Slower but better quality"),
        ],
        default='HIGH',
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "filepath")
        layout.prop(self, "debug_mode")
        layout.prop(self, "quality")
```

### Accessing Preferences
```python
# In an operator or panel:
def execute(self, context):
    prefs = context.preferences.addons[__package__].preferences
    if prefs.debug_mode:
        print("Debug mode is on!")
    return {'FINISHED'}
```

---

## 11. UI Layout System

### Basic Layout Methods
```python
def draw(self, context):
    layout = self.layout

    # --- Simple elements ---
    layout.label(text="Hello World")
    layout.label(text="With Icon", icon='WORLD_DATA')
    layout.separator()
    layout.separator(factor=2.0)  # Larger separator

    # --- Properties ---
    layout.prop(context.scene.my_settings, "my_float")
    layout.prop(context.scene.my_settings, "my_enum", text="Choose")
    layout.prop(context.scene.my_settings, "my_bool", toggle=True)  # Toggle button
    layout.prop(context.scene.my_settings, "my_enum", expand=True)  # Radio buttons

    # --- Operators ---
    layout.operator("myaddon.my_operator")
    layout.operator("myaddon.my_operator", text="Custom Label", icon='PLAY')

    # Pass properties to operator:
    op = layout.operator("myaddon.my_operator")
    op.my_float = 5.0
    op.my_enum = 'OPTION_B'
```

### Layout Containers
```python
def draw(self, context):
    layout = self.layout

    # --- Row (horizontal) ---
    row = layout.row()
    row.prop(data, "prop1")
    row.prop(data, "prop2")

    row = layout.row(align=True)  # No spacing between elements
    row.operator("myaddon.op1", icon='TRIA_LEFT', text="")
    row.operator("myaddon.op2", icon='TRIA_RIGHT', text="")

    # --- Column (vertical, same as default) ---
    col = layout.column()
    col.prop(data, "prop1")
    col.prop(data, "prop2")

    col = layout.column(align=True)  # No vertical spacing

    # --- Box (bordered container) ---
    box = layout.box()
    box.label(text="Settings")
    box.prop(data, "prop1")
    box.prop(data, "prop2")

    # --- Split (percentage-based columns) ---
    split = layout.split(factor=0.3)
    col1 = split.column()
    col1.label(text="Label:")
    col2 = split.column()
    col2.prop(data, "prop1", text="")

    # --- Grid Flow (auto-wrapping grid) ---
    grid = layout.grid_flow(row_major=True, columns=3, even_columns=True, even_rows=True, align=False)
    for i in range(9):
        grid.label(text=f"Item {i}")

    # --- Nested layouts ---
    box = layout.box()
    row = box.row()
    row.label(text="Left")
    col = row.column()
    col.prop(data, "prop1")
    col.prop(data, "prop2")
```

### Layout Properties
```python
layout.enabled = False          # Gray out everything
layout.active = False           # Dim everything
layout.alert = True             # Red highlight
layout.scale_x = 2.0            # Scale width
layout.scale_y = 1.5            # Scale height
layout.alignment = 'CENTER'     # 'LEFT', 'CENTER', 'RIGHT', 'EXPAND'
layout.use_property_split = True   # Label | Property two-column layout
layout.use_property_decorate = True  # Show animation dot
```

### Template Methods (Special UI Elements)
```python
# List (UIList integration)
layout.template_list("MY_UL_list", "", scene, "my_collection", scene, "my_collection_index")

# Color picker
layout.template_color_picker(data, "color_prop")

# Object/data ID selector (eyedropper)
layout.template_ID(context.object, "data")

# Preview (thumbnail)
layout.template_preview(material)

# Curve mapping
layout.template_curve_mapping(data, "curve_prop")

# Image
layout.template_image(data, "image", data.image_user)
```

---

## 12. Menus & Keymap Integration

### Custom Menu
```python
class MYADDON_MT_main_menu(bpy.types.Menu):
    bl_label = "My Addon Menu"
    bl_idname = "MYADDON_MT_main_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("myaddon.operator_a")
        layout.operator("myaddon.operator_b")
        layout.separator()
        layout.menu("MYADDON_MT_sub_menu")  # Sub-menu
```

### Appending to Existing Menus
```python
def menu_func(self, context):
    self.layout.operator("myaddon.my_operator")

def menu_func_import(self, context):
    self.layout.operator("myaddon.import_operator", text="My Format (.xyz)")

def register():
    # Add to Object menu in 3D Viewport
    bpy.types.VIEW3D_MT_object.append(menu_func)

    # Add to File > Import menu
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

    # Add to beginning of menu (prepend)
    bpy.types.VIEW3D_MT_mesh_add.prepend(menu_func)

def unregister():
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)
```

### Pie Menu
```python
class MYADDON_MT_pie_menu(bpy.types.Menu):
    bl_label = "My Pie Menu"
    bl_idname = "MYADDON_MT_pie_menu"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # Items are placed: West, East, South, North, NW, NE, SW, SE
        pie.operator("myaddon.op_left", icon='TRIA_LEFT')
        pie.operator("myaddon.op_right", icon='TRIA_RIGHT')
        pie.operator("myaddon.op_down", icon='TRIA_DOWN')
        pie.operator("myaddon.op_up", icon='TRIA_UP')
```

### Keymap Registration
```python
addon_keymaps = []

def register():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        # Create keymap for 3D Viewport in Object Mode
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')

        # Add shortcut: Ctrl+Shift+T
        kmi = km.keymap_items.new(
            "myaddon.my_operator",    # Operator bl_idname
            type='T',                  # Key
            value='PRESS',             # Key event
            ctrl=True,                 # Modifier keys
            shift=True,
        )
        # Optionally set operator properties
        kmi.properties.my_float = 5.0

        addon_keymaps.append((km, kmi))

        # Pie menu shortcut
        kmi = km.keymap_items.new(
            "wm.call_menu_pie",
            type='A',
            value='PRESS',
            alt=True,
        )
        kmi.properties.name = "MYADDON_MT_pie_menu"
        addon_keymaps.append((km, kmi))

def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
```

---

## 13. Multi-File Addon Structure

### __init__.py with Hot Reload Support
```python
bl_info = {
    "name": "My Addon",
    "author": "Your Name",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "category": "Object",
    "description": "My addon description",
}

# Support reloading
if "bpy" in locals():
    import importlib
    importlib.reload(operators)
    importlib.reload(panels)
    importlib.reload(properties)
else:
    from . import operators
    from . import panels
    from . import properties

import bpy


def register():
    properties.register()
    operators.register()
    panels.register()


def unregister():
    panels.unregister()
    operators.unregister()
    properties.unregister()


if __name__ == "__main__":
    register()
```

### operators.py
```python
import bpy

class MYADDON_OT_my_operator(bpy.types.Operator):
    bl_idname = "myaddon.my_operator"
    bl_label = "My Operator"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.report({'INFO'}, "Operator executed!")
        return {'FINISHED'}


classes = (
    MYADDON_OT_my_operator,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
```

### panels.py
```python
import bpy

class MYADDON_PT_main_panel(bpy.types.Panel):
    bl_label = "My Addon"
    bl_idname = "MYADDON_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "My Addon"

    def draw(self, context):
        layout = self.layout
        props = context.scene.my_addon_props

        layout.prop(props, "my_float")
        layout.operator("myaddon.my_operator")


classes = (
    MYADDON_PT_main_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
```

### properties.py
```python
import bpy

class MyAddonProperties(bpy.types.PropertyGroup):
    my_float: bpy.props.FloatProperty(
        name="My Float",
        default=1.0,
        min=0.0,
        max=10.0,
    )

classes = (
    MyAddonProperties,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.my_addon_props = bpy.props.PointerProperty(type=MyAddonProperties)

def unregister():
    del bpy.types.Scene.my_addon_props
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
```

---

## 14. Modal Operators & Timers

### Modal Operator (responds to user input continuously)
```python
class MYADDON_OT_modal_operator(bpy.types.Operator):
    bl_idname = "myaddon.modal_operator"
    bl_label = "Modal Operator"
    bl_options = {'REGISTER', 'UNDO'}

    _initial_mouse_x = 0
    _initial_value = 0.0

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            delta = event.mouse_x - self._initial_mouse_x
            context.object.location.x = self._initial_value + delta * 0.01
            return {'RUNNING_MODAL'}

        elif event.type == 'LEFTMOUSE':
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.object.location.x = self._initial_value
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.object:
            self._initial_mouse_x = event.mouse_x
            self._initial_value = context.object.location.x
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object")
            return {'CANCELLED'}
```

### Timer-Based Modal Operator
```python
class MYADDON_OT_timer_modal(bpy.types.Operator):
    bl_idname = "myaddon.timer_modal"
    bl_label = "Timer Modal"

    _timer = None

    def modal(self, context, event):
        if event.type == 'ESC':
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            # Do periodic work here
            print("Timer tick!")

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)  # 100ms interval
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
```

### Application Timers (bpy.app.timers)
```python
import bpy

def my_timer_function():
    """Run every 5 seconds"""
    print("Timer fired!")
    return 5.0  # Return interval for next call, or None to stop

# Register:
bpy.app.timers.register(my_timer_function)

# First call after delay:
bpy.app.timers.register(my_timer_function, first_interval=10.0)

# Persistent (survives file load):
bpy.app.timers.register(my_timer_function, persistent=True)

# Unregister:
if bpy.app.timers.is_registered(my_timer_function):
    bpy.app.timers.unregister(my_timer_function)
```

### Application Handlers
```python
import bpy
from bpy.app.handlers import persistent

@persistent  # Survives file load
def load_handler(dummy):
    """Called after a .blend file is loaded"""
    print("File loaded!")

@persistent
def frame_change_handler(scene):
    """Called on every frame change"""
    print(f"Frame: {scene.frame_current}")

def register():
    bpy.app.handlers.load_post.append(load_handler)
    bpy.app.handlers.frame_change_post.append(frame_change_handler)

def unregister():
    bpy.app.handlers.load_post.remove(load_handler)
    bpy.app.handlers.frame_change_post.remove(frame_change_handler)
```

### Common Handlers
| Handler | When Triggered |
|---------|---------------|
| `load_post` | After file load |
| `save_pre` / `save_post` | Before/after file save |
| `frame_change_pre` / `frame_change_post` | Before/after frame change |
| `depsgraph_update_post` | After dependency graph update |
| `render_pre` / `render_post` | Before/after render |
| `render_complete` | After render completes |
| `undo_pre` / `undo_post` | Before/after undo |

---

## 15. Gotchas & Common Pitfalls

### Threading
- **Python threads are NOT supported** for accessing Blender data
- Threads that call `bpy` functions will cause crashes
- Use `bpy.app.timers` for async-like behavior instead
- If you must use threads, only use them for non-Blender work (network requests, file I/O) and communicate results back via timers

### Data References
- **Never store references** to Blender data (objects, meshes, etc.) long-term
- Blender data can be invalidated by undo/redo, file load, or other operations
- Always fetch data fresh from `context` when needed

### Edit Mode
- Mesh data in edit mode lives in `bmesh` and is separate from `mesh.vertices`
- Changes to `mesh.vertices` won't be visible in edit mode
- Toggle to object mode to modify mesh data, or use `bmesh`

### Operator Context
- Some operators require specific contexts to run
- Use `bpy.ops.object.select_all(action='DESELECT')` not `bpy.ops.object.select_all('DESELECT')`
- Override context if needed: `bpy.ops.object.delete({'selected_objects': [obj]})`

### File Paths
- Always use `bpy.path.abspath("//relative_path")` to resolve Blender relative paths
- Use `os.path` or `pathlib` for cross-platform path handling

### Registration Order
- Register PropertyGroup classes **before** classes that reference them
- Register properties on types **after** `register_class()` calls
- Unregister in **reverse** order

---

## 16. Best Practices

### Code Style
- Follow PEP 8 (Python style guide)
- Use **single quotes** for enums: `'OPTION_A'`
- Use **double quotes** for user-visible strings: `"My Label"`
- Class naming: `ADDON_OT_operator_name` format

### Performance
- Avoid `bpy.ops` when direct data access is possible (bpy.ops has overhead)
- Modify lists/dicts in place instead of creating new ones
- Use `foreach_get` / `foreach_set` for bulk mesh data access
- Minimize `depsgraph_update_post` handler work (runs very frequently)

### Undo
- Always include `'UNDO'` in `bl_options` for operators that modify data
- This ensures users can Ctrl+Z your operator's changes

### Error Handling
- Use `self.report({'ERROR'}, "message")` for user-facing errors
- Use `self.report({'WARNING'}, "message")` for warnings
- Use `self.report({'INFO'}, "message")` for info messages

### Clean Unregistration
- Always clean up everything in `unregister()`
- Remove keymaps, handlers, timers, properties, and classes
- Delete scene/object properties with `del bpy.types.Scene.my_prop`

---

## 17. Development Environment Setup

### IDE Setup (VS Code Recommended)
1. Install Python extension
2. Install `fake-bpy-module` for autocomplete:
   ```
   pip install fake-bpy-module-latest
   ```
   Or for a specific version:
   ```
   pip install fake-bpy-module-4.0
   ```

### Development Symlink (avoid copying files)
```bash
# Windows
mklink /d "C:\Users\YOU\AppData\Roaming\Blender Foundation\Blender\4.0\scripts\addons\my_addon" "C:\Projects\my_addon"

# Mac/Linux
ln -s "/path/to/dev/my_addon" "/path/to/blender/scripts/addons/my_addon"
```

### Hot Reload in Blender
- **F3** > "Reload Scripts" to reload all addons
- Or use the reload pattern in `__init__.py` (see Section 13)

### Blender Console for Testing
- Open via: Editor Type > Python Console
- Quick test code: `bpy.ops.myaddon.my_operator()`

### Enable Developer Extras
- Edit > Preferences > Interface > Developer Extras
- Enables: Right-click > "Edit Source" on UI elements, operator search details, etc.

### Building Extension Package
```bash
# From Blender command line or system terminal
blender --command extension build --source-dir /path/to/addon --output-dir /path/to/output
```

---

## 18. Complete Minimal Example

A single-file addon that adds a panel with a button:

```python
bl_info = {
    "name": "Hello World Addon",
    "author": "Your Name",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Hello Tab",
    "description": "A simple hello world addon",
    "category": "Object",
}

import bpy


class HELLO_OT_say_hello(bpy.types.Operator):
    """Print hello to console and info bar"""
    bl_idname = "hello.say_hello"
    bl_label = "Say Hello"
    bl_options = {'REGISTER', 'UNDO'}

    name: bpy.props.StringProperty(
        name="Name",
        default="World",
    )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        self.report({'INFO'}, f"Hello, {self.name}!")
        return {'FINISHED'}


class HELLO_PT_main_panel(bpy.types.Panel):
    bl_label = "Hello World"
    bl_idname = "HELLO_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Hello"

    def draw(self, context):
        layout = self.layout
        layout.operator("hello.say_hello")


classes = (
    HELLO_OT_say_hello,
    HELLO_PT_main_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
```

---

## 19. Complete Multi-File Example

### my_addon/__init__.py
```python
bl_info = {
    "name": "My Complete Addon",
    "author": "Your Name",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > My Addon",
    "description": "A complete multi-file addon example",
    "category": "Object",
}

if "bpy" in locals():
    import importlib
    importlib.reload(properties)
    importlib.reload(operators)
    importlib.reload(panels)
    importlib.reload(preferences)
else:
    from . import properties
    from . import operators
    from . import panels
    from . import preferences

import bpy


def register():
    preferences.register()
    properties.register()
    operators.register()
    panels.register()


def unregister():
    panels.unregister()
    operators.unregister()
    properties.unregister()
    preferences.unregister()


if __name__ == "__main__":
    register()
```

### my_addon/blender_manifest.toml
```toml
schema_version = "1.0.0"
id = "my_complete_addon"
version = "1.0.0"
name = "My Complete Addon"
tagline = "A complete multi-file addon example"
maintainer = "Your Name <you@example.com>"
type = "add-on"
license = ["SPDX:GPL-3.0-or-later"]
blender_version_min = "4.2.0"
tags = ["Object"]
```

### my_addon/properties.py
```python
import bpy

class MYADDON_PG_settings(bpy.types.PropertyGroup):
    scale_factor: bpy.props.FloatProperty(
        name="Scale Factor",
        description="Factor to scale by",
        default=2.0,
        min=0.1,
        max=100.0,
    )
    apply_to_all: bpy.props.BoolProperty(
        name="Apply to All",
        description="Apply to all selected objects",
        default=False,
    )
    axis: bpy.props.EnumProperty(
        name="Axis",
        items=[
            ('X', "X", "X axis"),
            ('Y', "Y", "Y axis"),
            ('Z', "Z", "Z axis"),
            ('ALL', "All", "All axes"),
        ],
        default='ALL',
    )

classes = (MYADDON_PG_settings,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.my_addon = bpy.props.PointerProperty(type=MYADDON_PG_settings)

def unregister():
    del bpy.types.Scene.my_addon
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
```

### my_addon/operators.py
```python
import bpy

class MYADDON_OT_scale_object(bpy.types.Operator):
    """Scale the active or selected objects"""
    bl_idname = "myaddon.scale_object"
    bl_label = "Scale Object"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        settings = context.scene.my_addon
        factor = settings.scale_factor
        axis = settings.axis

        objects = context.selected_objects if settings.apply_to_all else [context.active_object]

        for obj in objects:
            if axis in ('X', 'ALL'):
                obj.scale.x *= factor
            if axis in ('Y', 'ALL'):
                obj.scale.y *= factor
            if axis in ('Z', 'ALL'):
                obj.scale.z *= factor

        self.report({'INFO'}, f"Scaled {len(objects)} object(s) by {factor}")
        return {'FINISHED'}

classes = (MYADDON_OT_scale_object,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
```

### my_addon/panels.py
```python
import bpy

class MYADDON_PT_main(bpy.types.Panel):
    bl_label = "My Addon"
    bl_idname = "MYADDON_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "My Addon"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.my_addon

        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(settings, "scale_factor")
        layout.prop(settings, "axis")
        layout.prop(settings, "apply_to_all")

        layout.separator()
        layout.operator("myaddon.scale_object", icon='FULLSCREEN_ENTER')

classes = (MYADDON_PT_main,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
```

### my_addon/preferences.py
```python
import bpy

class MYADDON_AP_preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    default_scale: bpy.props.FloatProperty(
        name="Default Scale",
        default=2.0,
        min=0.1,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "default_scale")

classes = (MYADDON_AP_preferences,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
```

---

## 20. Key API Reference Links

### Official Documentation
- [Blender Python API (current)](https://docs.blender.org/api/current/index.html)
- [Addon Tutorial - Blender 5.0 Manual](https://docs.blender.org/manual/en/latest/advanced/scripting/addon_tutorial.html)
- [API Overview](https://docs.blender.org/api/current/info_overview.html)
- [Best Practices](https://docs.blender.org/api/current/info_best_practice.html)
- [Quickstart](https://docs.blender.org/api/current/info_quickstart.html)
- [Gotchas](https://docs.blender.org/api/current/info_gotcha.html)
- [Tips and Tricks](https://docs.blender.org/api/current/info_tips_and_tricks.html)

### API Type References
- [Operator](https://docs.blender.org/api/current/bpy.types.Operator.html)
- [Panel](https://docs.blender.org/api/current/bpy.types.Panel.html)
- [Menu](https://docs.blender.org/api/current/bpy.types.Menu.html)
- [UILayout](https://docs.blender.org/api/current/bpy.types.UILayout.html)
- [UIList](https://docs.blender.org/api/current/bpy.types.UIList.html)
- [PropertyGroup](https://docs.blender.org/api/current/bpy.types.PropertyGroup.html)
- [AddonPreferences](https://docs.blender.org/api/current/bpy.types.AddonPreferences.html)
- [Property Definitions (bpy.props)](https://docs.blender.org/api/current/bpy.props.html)
- [Application Timers](https://docs.blender.org/api/current/bpy.app.timers.html)

### Core Modules
- [bpy.context](https://docs.blender.org/api/current/bpy.context.html) - Current application state
- [bpy.data](https://docs.blender.org/api/current/bpy.data.html) - All data in the .blend file
- [bpy.ops](https://docs.blender.org/api/current/bpy.ops.html) - All built-in operators
- [bpy.types](https://docs.blender.org/api/current/bpy.types.html) - All type definitions
- [bpy.utils](https://docs.blender.org/api/current/bpy.utils.html) - Utility functions
- [bpy.path](https://docs.blender.org/api/current/bpy.path.html) - Path utilities
- [bpy.app.handlers](https://docs.blender.org/api/current/bpy.app.handlers.html) - Event handlers
- [mathutils](https://docs.blender.org/api/current/mathutils.html) - Vector, Matrix, Euler, Quaternion
- [bmesh](https://docs.blender.org/api/current/bmesh.html) - Advanced mesh editing

### Extension System
- [How to Create Extensions](https://docs.blender.org/manual/en/latest/advanced/extensions/getting_started.html)
- [Addon Dev Setup](https://developer.blender.org/docs/handbook/extensions/addon_dev_setup/)

### Community Resources
- [Using UILists in Blender](https://sinestesia.co/blog/tutorials/using-uilists-in-blender/)
- [Blender Artists - Python Support](https://blenderartists.org/c/coding/python-support/19)
- [Blender Developer Forum](https://devtalk.blender.org/)
