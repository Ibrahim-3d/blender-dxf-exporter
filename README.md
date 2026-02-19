# DXF / DWG Exporter for Blender

A Blender addon that exports **Curve** and **Grease Pencil** objects to AutoCAD-compatible **DXF** and **DWG** files.

- **DXF output** works out of the box — no external tools needed
- **DWG output** uses [LibreDWG](https://github.com/LibreDWG/libredwg) (open source, GPLv3+) for conversion

## Features

- Export Bezier, NURBS, and Poly curves
- Export Grease Pencil strokes (legacy and new GP)
- Spline or polyline output modes
- Layer mapping: single layer, by object name, or by collection
- Configurable scale and units (mm, cm, m, inches, feet)
- World transform support
- Produces valid DXF R2000 (AC1015) with proper entity handles

## Install

1. Download the latest `svg_to_dwg.zip` from [Releases](https://github.com/Ibrahim-3d/svg-to-dwg/releases) (or build it yourself from source)
2. In Blender: **Edit > Preferences > Add-ons > Install** (dropdown arrow top-right) > select the zip
3. Enable the checkbox next to **"DXF / DWG Exporter — Curves & Grease Pencil"**

## DWG Setup (optional)

DXF export works immediately. For DWG output you need LibreDWG's `dxf2dwg`:

1. Download `libredwg-*-win64.zip` from [LibreDWG releases](https://github.com/LibreDWG/libredwg/releases)
2. Extract `dxf2dwg.exe` and the DLL files into the addon's `bin/` folder
3. In Blender: **Edit > Preferences > Add-ons** > expand the addon > click **Auto-detect** to verify

## Usage

### Sidebar Panel
1. Open a 3D Viewport, press **N** to show the sidebar
2. Go to the **DXF Export** tab
3. Choose your settings and click **Export DXF** or **Export DWG**

### File Menu
**File > Export > AutoCAD DXF / DWG**

## Uninstall

1. **Edit > Preferences > Add-ons**
2. Search for "DXF"
3. Click the **dropdown arrow** next to the addon name
4. Click **Remove**

## License

GPL-3.0-or-later — same license as Blender and LibreDWG.
