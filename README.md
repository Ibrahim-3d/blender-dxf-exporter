# Blender DXF/DWG Exporter

A Blender addon that exports Curve and Grease Pencil objects to AutoCAD-compatible DXF and DWG files. DXF works out of the box with zero dependencies. DWG output is available through [LibreDWG](https://github.com/LibreDWG/libredwg) (open-source, GPLv3+).

## Features

- Export Bezier, NURBS, and Poly curves as DXF splines or polylines
- Export Grease Pencil strokes (both legacy and Blender 4.x GP objects)
- Layer mapping by object name, collection, or single layer
- Configurable units (mm, cm, m, inches, feet) and scale factor
- Applies world transforms so exported geometry matches your scene
- Produces valid DXF R2000 (AC1015) with proper entity handles and all required sections
- Optional DWG output via LibreDWG with auto-detection

## Installation

1. Download [`dxf_dwg_exporter.zip`](https://github.com/Ibrahim-3d/blender-dxf-exporter/releases/latest) from the Releases page
2. In Blender, go to **Edit > Preferences > Add-ons**
3. Click the dropdown arrow (top-right) and select **Install from Disk**
4. Select the downloaded zip and enable the addon

> Requires Blender 3.6 or newer. Tested on 3.6 through 4.x.

### DWG setup (optional)

DXF export needs nothing extra. To also export DWG files:

1. Download the latest `libredwg-*-win64.zip` from [LibreDWG releases](https://github.com/LibreDWG/libredwg/releases)
2. Extract `dxf2dwg.exe` and all `.dll` files into the addon's `bin/` folder
3. Open **Edit > Preferences > Add-ons**, expand the addon, and click **Auto-detect** to verify

You can also point the addon to any location where `dxf2dwg` is installed via the preferences path field.

## Usage

### From the sidebar

1. Open a 3D Viewport and press **N** to show the sidebar
2. Switch to the **DXF Export** tab
3. Configure your settings and click **Export DXF** or **Export DWG**

### From the file menu

**File > Export > AutoCAD DXF / DWG**

This opens a file browser with the same export options.

## Export settings

| Setting | Options | Default |
|---------|---------|---------|
| Objects | Selected / Visible / All in Scene | Selected |
| Output format | DXF / DWG | DXF |
| Curve mode | Spline / Polyline | Spline |
| Tessellation | 2–256 samples per segment (polyline mode only) | 12 |
| Layer mapping | Single (layer 0) / By Object Name / By Collection | Single |
| Units | mm, cm, m, in, ft | mm |
| Scale | Any positive float | 1.0 |
| Apply transform | Yes / No | Yes |

When exporting as **splines**, Bezier and NURBS curves are written as native DXF SPLINE entities with full control point and knot data. NURBS weights are preserved for rational curves. When exporting as **polylines**, curves are tessellated into LWPOLYLINE entities for maximum compatibility with older CAD software.

## Uninstall

1. Go to **Edit > Preferences > Add-ons**
2. Search for "DXF"
3. Click the dropdown arrow next to the addon and select **Remove**

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a pull request.

## License

[GPL-3.0-or-later](LICENSE), consistent with the Blender manifest.
The installable add-on includes its program grant and complete GPL text.
See [LICENSING.md](LICENSING.md) for historical rights and packaging requirements.

This addon optionally uses [LibreDWG](https://github.com/LibreDWG/libredwg) for DWG conversion (GPLv3+). See [THIRD_PARTY_NOTICES.md](dxf_dwg_exporter/THIRD_PARTY_NOTICES.md) for attribution and optional-binary distribution requirements.
