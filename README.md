<div align="center">

# Blender DXF/DWG Exporter

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](LICENSE)
[![Blender](https://img.shields.io/badge/Blender-3.6%2B-orange?logo=blender&logoColor=white)](https://www.blender.org/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?logo=python&logoColor=white)](https://www.python.org/)

**Export Blender Curves and Grease Pencil objects to AutoCAD-compatible DXF and DWG files.**

DXF output works out of the box — no external tools needed.
DWG output uses [LibreDWG](https://github.com/LibreDWG/libredwg) (open-source, GPLv3+).

</div>

---

## Features

- **Curve export** — Bezier, NURBS, and Poly curves
- **Grease Pencil export** — legacy and new GP stroke objects
- **Output modes** — spline or polyline representation
- **Layer mapping** — single layer, by object name, or by collection
- **Units & scale** — mm, cm, m, inches, feet with configurable scale factor
- **World transform** — respects object transforms in the scene
- **Valid DXF R2000** — produces standards-compliant AC1015 files with proper entity handles
- **DWG conversion** — optional DWG output via LibreDWG's `dxf2dwg`

## Requirements

| Dependency | Required | Notes |
|-----------|----------|-------|
| Blender 3.6+ | Yes | Tested on 3.6 – 4.x |
| LibreDWG | Only for DWG | [Download here](https://github.com/LibreDWG/libredwg/releases) |

## Installation

1. Download `dxf_dwg_exporter.zip` from [Releases](https://github.com/Ibrahim-3d/blender-dxf-exporter/releases)
2. In Blender: **Edit > Preferences > Add-ons > Install** (dropdown arrow, top-right) > select the zip
3. Enable the checkbox next to **"DXF / DWG Exporter — Curves & Grease Pencil"**

### DWG Setup (optional)

DXF export works immediately. For DWG output:

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

### Export Settings

| Setting | Options | Default |
|---------|---------|---------|
| Output format | DXF / DWG | DXF |
| Curve mode | Spline / Polyline | Spline |
| Layer mapping | Single / By Object / By Collection | By Object |
| Units | mm, cm, m, in, ft | mm |
| Scale | Any positive float | 1.0 |

## Uninstall

1. **Edit > Preferences > Add-ons**
2. Search for "DXF"
3. Click the dropdown arrow next to the addon name
4. Click **Remove**

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a pull request.

By contributing to this project, you agree to the [Contributor License Agreement](CLA.md).

## License

This project is licensed under the [GNU Affero General Public License v3.0](LICENSE) (AGPL-3.0-or-later).

## Third-Party Notices

This addon optionally uses [LibreDWG](https://github.com/LibreDWG/libredwg) for DWG conversion, which is licensed under GPLv3+. See [THIRD_PARTY_NOTICES.md](dxf_dwg_exporter/THIRD_PARTY_NOTICES.md) for details.
