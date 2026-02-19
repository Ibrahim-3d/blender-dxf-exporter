"""
DXF writer for Blender Curve and Grease Pencil objects.

Produces a fully valid ASCII DXF R2000 (AC1015) file with proper entity handles,
all eight required TABLES, BLOCKS (*Model_Space / *Paper_Space), and the OBJECTS
section.  Compatible with AutoCAD and LibreDWG's dxf2dwg converter.

No external Python dependencies — pure stdlib + Blender's mathutils.
"""

import os
import subprocess
import bpy
from mathutils import Vector, Matrix


# ── Handle counter ────────────────────────────────────────────────────────────
# Every DXF R2000 object needs a unique hex handle (group code 5).

class _HandleSeq:
    """Simple auto-incrementing hex handle allocator."""
    def __init__(self, start=0x20):
        self._next = start
    def next(self):
        h = format(self._next, 'X')
        self._next += 1
        return h


# ── Group-code helper ─────────────────────────────────────────────────────────

def _gc(code, value):
    return f"{code:>3}\n{value}\n"


# ── Coordinate transform ──────────────────────────────────────────────────────

def _xform(co, matrix, scale):
    v = matrix @ Vector((float(co[0]), float(co[1]), float(co[2])))
    return (v.x * scale, v.y * scale, v.z * scale)


# ── DXF entity builders (handle-aware) ────────────────────────────────────────

def _entity_lwpolyline(points_xy, handle, owner_handle,
                       layer="0", closed=False, elevation=0.0):
    flags = 1 if closed else 0
    out = [
        "  0\nLWPOLYLINE\n",
        _gc(5, handle),
        _gc(330, owner_handle),   # owner: *Model_Space block record
        "100\nAcDbEntity\n",
        _gc(8, layer),
        "100\nAcDbPolyline\n",
        _gc(90, len(points_xy)),
        _gc(70, flags),
        _gc(38, f"{elevation:.6f}"),
        # Extrusion direction (WCS normal) — prevents AutoCAD "Y axis normalizing"
        _gc(210, "0.0"),
        _gc(220, "0.0"),
        _gc(230, "1.0"),
    ]
    for x, y in points_xy:
        out.append(_gc(10, f"{x:.8f}"))
        out.append(_gc(20, f"{y:.8f}"))
    return "".join(out)


def _entity_spline(control_points, knots, degree, handle, owner_handle,
                   layer="0", closed=False, weights=None):
    flags = 0
    if closed:
        flags |= 1
    has_w = (
        weights is not None
        and len(weights) == len(control_points)
        and any(abs(w - 1.0) > 1e-9 for w in weights)
    )
    if has_w:
        flags |= 4
    out = [
        "  0\nSPLINE\n",
        _gc(5, handle),
        _gc(330, owner_handle),
        "100\nAcDbEntity\n",
        _gc(8, layer),
        "100\nAcDbSpline\n",
        # Extrusion direction (WCS normal)
        _gc(210, "0.0"),
        _gc(220, "0.0"),
        _gc(230, "1.0"),
        _gc(70, flags),
        _gc(71, degree),
        _gc(72, len(knots)),
        _gc(73, len(control_points)),
        _gc(74, 0),
        _gc(42, "0.0000001"),
        _gc(43, "0.0000001"),
        _gc(44, "0.0000000001"),
    ]
    for k in knots:
        out.append(_gc(40, f"{k:.10f}"))
    if has_w:
        for w in weights:
            out.append(_gc(41, f"{w:.8f}"))
    for x, y, z in control_points:
        out.append(_gc(10, f"{x:.8f}"))
        out.append(_gc(20, f"{y:.8f}"))
        out.append(_gc(30, f"{z:.8f}"))
    return "".join(out)


# ── DXF sections (handle-aware) ───────────────────────────────────────────────

UNITS_CODES = {"MM": 4, "CM": 5, "M": 6, "INCHES": 1, "FEET": 2}


def _write_dxf_file(f, entity_parts, layers, units_code):
    """
    Write a complete, valid DXF R2000 file to open file handle *f*.
    Handles are assigned sequentially to all objects.
    """
    H = _HandleSeq(start=0x20)

    # Pre-allocate well-known handles (match AutoCAD conventions)
    h_blkrec_table    = "1"   # BLOCK_RECORD table (a.k.a. BLOCK_CONTROL)
    h_ltype_table     = "2"
    h_layer_table     = "3"
    h_style_table     = "4"
    h_view_table      = "5"
    h_ucs_table       = "6"
    h_vport_table     = "7"
    h_appid_table     = "8"
    h_dimstyle_table  = "9"
    h_dict_root       = "C"
    h_dict_group      = "D"

    h_ltype_bylayer   = H.next()   # ByLayer linetype record
    h_ltype_byblock   = H.next()   # ByBlock linetype record
    h_ltype_cont      = H.next()   # Continuous linetype record

    # Layer handles
    layer_handles = {}
    for name in layers:
        layer_handles[name] = H.next()

    h_style_standard  = H.next()
    h_vport_active    = H.next()
    h_appid_acad      = H.next()

    # Block handles (block record + layout entity in BLOCKS section)
    h_mspace_blkrec   = H.next()   # BLOCK_RECORD for *Model_Space
    h_pspace_blkrec   = H.next()   # BLOCK_RECORD for *Paper_Space
    h_mspace_block    = H.next()   # BLOCK entity
    h_mspace_endblk   = H.next()   # ENDBLK entity
    h_pspace_block    = H.next()
    h_pspace_endblk   = H.next()

    # ── HEADER ────────────────────────────────────────────────────────────
    f.write(
        "  0\nSECTION\n  2\nHEADER\n"
        "  9\n$ACADVER\n  1\nAC1015\n"
        f"  9\n$INSUNITS\n 70\n{units_code}\n"
        "  9\n$MEASUREMENT\n 70\n1\n"
        "  9\n$LTSCALE\n 40\n1.0\n"
        # UCS origin and axes — prevents "Y axis normalizing" recovery
        "  9\n$UCSORG\n 10\n0.0\n 20\n0.0\n 30\n0.0\n"
        "  9\n$UCSXDIR\n 10\n1.0\n 20\n0.0\n 30\n0.0\n"
        "  9\n$UCSYDIR\n 10\n0.0\n 20\n1.0\n 30\n0.0\n"
        "  0\nENDSEC\n"
    )

    # ── CLASSES ───────────────────────────────────────────────────────────
    f.write("  0\nSECTION\n  2\nCLASSES\n  0\nENDSEC\n")

    # ── TABLES ────────────────────────────────────────────────────────────
    f.write("  0\nSECTION\n  2\nTABLES\n")

    # -- VPORT --
    f.write(
        f"  0\nTABLE\n  2\nVPORT\n  5\n{h_vport_table}\n"
        "100\nAcDbSymbolTable\n 70\n1\n"
        f"  0\nVPORT\n  5\n{h_vport_active}\n"
        f"330\n{h_vport_table}\n"
        "100\nAcDbSymbolTableRecord\n"
        "100\nAcDbViewportTableRecord\n"
        "  2\n*Active\n 70\n0\n"
        " 10\n0.0\n 20\n0.0\n"
        " 11\n1.0\n 21\n1.0\n"
        " 12\n0.0\n 22\n0.0\n"
        " 13\n0.0\n 23\n0.0\n"
        " 14\n0.5\n 24\n0.5\n"
        " 15\n0.5\n 25\n0.5\n"
        " 16\n0.0\n 26\n0.0\n 36\n1.0\n"
        " 17\n0.0\n 27\n0.0\n 37\n0.0\n"
        " 40\n1.0\n 41\n1.6\n 42\n50.0\n"
        " 43\n0.0\n 44\n0.0\n"
        " 50\n0.0\n 51\n0.0\n"
        " 71\n0\n 72\n1000\n 73\n1\n 74\n3\n"
        " 75\n0\n 76\n0\n 77\n0\n 78\n0\n"
        "  0\nENDTAB\n"
    )

    # -- LTYPE --
    f.write(
        f"  0\nTABLE\n  2\nLTYPE\n  5\n{h_ltype_table}\n"
        "100\nAcDbSymbolTable\n 70\n3\n"
        # ByBlock
        f"  0\nLTYPE\n  5\n{h_ltype_byblock}\n"
        f"330\n{h_ltype_table}\n"
        "100\nAcDbSymbolTableRecord\n"
        "100\nAcDbLinetypeTableRecord\n"
        "  2\nByBlock\n 70\n0\n"
        "  3\n\n 72\n65\n 73\n0\n 40\n0.0\n"
        # ByLayer
        f"  0\nLTYPE\n  5\n{h_ltype_bylayer}\n"
        f"330\n{h_ltype_table}\n"
        "100\nAcDbSymbolTableRecord\n"
        "100\nAcDbLinetypeTableRecord\n"
        "  2\nByLayer\n 70\n0\n"
        "  3\n\n 72\n65\n 73\n0\n 40\n0.0\n"
        # Continuous
        f"  0\nLTYPE\n  5\n{h_ltype_cont}\n"
        f"330\n{h_ltype_table}\n"
        "100\nAcDbSymbolTableRecord\n"
        "100\nAcDbLinetypeTableRecord\n"
        "  2\nContinuous\n 70\n0\n"
        "  3\nSolid line\n 72\n65\n 73\n0\n 40\n0.0\n"
        "  0\nENDTAB\n"
    )

    # -- LAYER --
    f.write(
        f"  0\nTABLE\n  2\nLAYER\n  5\n{h_layer_table}\n"
        f"100\nAcDbSymbolTable\n 70\n{len(layers)}\n"
    )
    for name, color in layers.items():
        f.write(
            f"  0\nLAYER\n  5\n{layer_handles[name]}\n"
            f"330\n{h_layer_table}\n"
            "100\nAcDbSymbolTableRecord\n"
            "100\nAcDbLayerTableRecord\n"
            f"  2\n{name}\n 70\n0\n"
            f" 62\n{color}\n"
            "  6\nContinuous\n"
        )
    f.write("  0\nENDTAB\n")

    # -- STYLE --
    f.write(
        f"  0\nTABLE\n  2\nSTYLE\n  5\n{h_style_table}\n"
        "100\nAcDbSymbolTable\n 70\n1\n"
        f"  0\nSTYLE\n  5\n{h_style_standard}\n"
        f"330\n{h_style_table}\n"
        "100\nAcDbSymbolTableRecord\n"
        "100\nAcDbTextStyleTableRecord\n"
        "  2\nStandard\n 70\n0\n"
        " 40\n0.0\n 41\n1.0\n 50\n0.0\n 71\n0\n 42\n0.2\n"
        "  3\ntxt\n  4\n\n"
        "  0\nENDTAB\n"
    )

    # -- VIEW --
    f.write(
        f"  0\nTABLE\n  2\nVIEW\n  5\n{h_view_table}\n"
        "100\nAcDbSymbolTable\n 70\n0\n"
        "  0\nENDTAB\n"
    )

    # -- UCS --
    f.write(
        f"  0\nTABLE\n  2\nUCS\n  5\n{h_ucs_table}\n"
        "100\nAcDbSymbolTable\n 70\n0\n"
        "  0\nENDTAB\n"
    )

    # -- APPID --
    f.write(
        f"  0\nTABLE\n  2\nAPPID\n  5\n{h_appid_table}\n"
        "100\nAcDbSymbolTable\n 70\n1\n"
        f"  0\nAPPID\n  5\n{h_appid_acad}\n"
        f"330\n{h_appid_table}\n"
        "100\nAcDbSymbolTableRecord\n"
        "100\nAcDbRegAppTableRecord\n"
        "  2\nACAD\n 70\n0\n"
        "  0\nENDTAB\n"
    )

    # -- DIMSTYLE --
    f.write(
        f"  0\nTABLE\n  2\nDIMSTYLE\n  5\n{h_dimstyle_table}\n"
        "100\nAcDbSymbolTable\n 70\n0\n"
        "  0\nENDTAB\n"
    )

    # -- BLOCK_RECORD --
    f.write(
        f"  0\nTABLE\n  2\nBLOCK_RECORD\n  5\n{h_blkrec_table}\n"
        "100\nAcDbSymbolTable\n 70\n2\n"
        f"  0\nBLOCK_RECORD\n  5\n{h_mspace_blkrec}\n"
        f"330\n{h_blkrec_table}\n"
        "100\nAcDbSymbolTableRecord\n"
        "100\nAcDbBlockTableRecord\n"
        "  2\n*Model_Space\n"
        f"  0\nBLOCK_RECORD\n  5\n{h_pspace_blkrec}\n"
        f"330\n{h_blkrec_table}\n"
        "100\nAcDbSymbolTableRecord\n"
        "100\nAcDbBlockTableRecord\n"
        "  2\n*Paper_Space\n"
        "  0\nENDTAB\n"
    )

    f.write("  0\nENDSEC\n")   # end TABLES

    # ── BLOCKS ────────────────────────────────────────────────────────────
    def _block(name, h_blk, h_endblk, h_blkrec):
        return (
            f"  0\nBLOCK\n  5\n{h_blk}\n"
            f"330\n{h_blkrec}\n"
            "100\nAcDbEntity\n  8\n0\n"
            "100\nAcDbBlockBegin\n"
            f"  2\n{name}\n 70\n0\n"
            " 10\n0.0\n 20\n0.0\n 30\n0.0\n"
            f"  3\n{name}\n  1\n\n"
            f"  0\nENDBLK\n  5\n{h_endblk}\n"
            f"330\n{h_blkrec}\n"
            "100\nAcDbEntity\n  8\n0\n"
            "100\nAcDbBlockEnd\n"
        )

    f.write(
        "  0\nSECTION\n  2\nBLOCKS\n"
        + _block("*Model_Space",
                 h_mspace_block, h_mspace_endblk, h_mspace_blkrec)
        + _block("*Paper_Space",
                 h_pspace_block, h_pspace_endblk, h_pspace_blkrec)
        + "  0\nENDSEC\n"
    )

    # ── ENTITIES ──────────────────────────────────────────────────────────
    f.write("  0\nSECTION\n  2\nENTITIES\n")
    for ent_func in entity_parts:
        ent_func(f, H.next(), h_mspace_blkrec)
    f.write("  0\nENDSEC\n")

    # ── OBJECTS ────────────────────────────────────────────────────────────
    f.write(
        "  0\nSECTION\n  2\nOBJECTS\n"
        f"  0\nDICTIONARY\n  5\n{h_dict_root}\n"
        "100\nAcDbDictionary\n"
        "281\n1\n"
        f"  3\nACAD_GROUP\n350\n{h_dict_group}\n"
        f"  0\nDICTIONARY\n  5\n{h_dict_group}\n"
        f"330\n{h_dict_root}\n"
        "100\nAcDbDictionary\n"
        "281\n1\n"
        "  0\nENDSEC\n"
    )

    f.write("  0\nEOF\n")


# ── Bezier helpers ────────────────────────────────────────────────────────────

def _bezier_knots(n_segs):
    k = [0.0, 0.0, 0.0, 0.0]
    for i in range(1, n_segs):
        k += [float(i)] * 3
    k += [float(n_segs)] * 4
    return k


def _sample_cubic_bezier(p0, p1, p2, p3, n):
    pts = []
    for i in range(n + 1):
        t  = i / n
        mt = 1.0 - t
        x  = mt**3*p0[0] + 3*mt**2*t*p1[0] + 3*mt*t**2*p2[0] + t**3*p3[0]
        y  = mt**3*p0[1] + 3*mt**2*t*p1[1] + 3*mt*t**2*p2[1] + t**3*p3[1]
        z  = mt**3*p0[2] + 3*mt**2*t*p1[2] + 3*mt*t**2*p2[2] + t**3*p3[2]
        pts.append((x, y, z))
    return pts


# ── Spline converters (return callables for deferred handle assignment) ───────
# Each converter returns a list of "writer functions":
#   writer(file, handle, owner_handle) → writes one entity to file.

def _convert_bezier(spline, matrix, scale, layer, output_splines, tess_samples):
    bpts = spline.bezier_points
    n    = len(bpts)
    if n < 2:
        return []

    closed = spline.use_cyclic_u
    n_segs = n if closed else n - 1

    T = []
    for bp in bpts:
        T.append((
            _xform(bp.co,           matrix, scale),
            _xform(bp.handle_left,  matrix, scale),
            _xform(bp.handle_right, matrix, scale),
        ))

    if output_splines:
        cps = []
        for i in range(n_segs):
            i1 = (i + 1) % n
            p0_co, _,      p0_hr = T[i]
            p1_co, p1_hl,  _     = T[i1]
            if i == 0:
                cps.append(p0_co)
            cps.append(p0_hr)
            cps.append(p1_hl)
            cps.append(p1_co)
        knots = _bezier_knots(n_segs)

        def _write(f, h, owner):
            f.write(_entity_spline(cps, knots, 3, h, owner, layer=layer))
        return [_write]

    else:
        pts = []
        for i in range(n_segs):
            i1 = (i + 1) % n
            p0_co, _,      p0_hr = T[i]
            p1_co, p1_hl,  _     = T[i1]
            seg = _sample_cubic_bezier(p0_co, p0_hr, p1_hl, p1_co, tess_samples)
            pts.extend(seg if i == 0 else seg[1:])
        if closed and pts:
            pts.append(pts[0])
        xy   = [(p[0], p[1]) for p in pts]
        elev = pts[0][2] if pts else 0.0

        def _write(f, h, owner):
            f.write(_entity_lwpolyline(xy, h, owner, layer=layer,
                                        closed=closed, elevation=elev))
        return [_write]


def _convert_nurbs(spline, matrix, scale, layer, output_splines):
    pts = spline.points
    n   = len(pts)
    if n < 2:
        return []

    closed  = spline.use_cyclic_u
    degree  = max(1, spline.order_u - 1)
    cps     = [_xform(p.co[:3], matrix, scale) for p in pts]
    weights = [p.co[3] for p in pts]

    if output_splines:
        n_knots    = n + degree + 1
        n_interior = n_knots - 2 * (degree + 1)
        knots = [0.0] * (degree + 1)
        for i in range(max(0, n_interior)):
            knots.append(float(i + 1))
        end_val = float(max(0, n_interior) + 1) if n_interior >= 0 else 1.0
        knots.extend([end_val] * (degree + 1))
        if knots[-1] > 0:
            mx = knots[-1]
            knots = [k / mx for k in knots]
        is_rational = any(abs(w - 1.0) > 1e-6 for w in weights)

        def _write(f, h, owner):
            f.write(_entity_spline(
                cps, knots, degree, h, owner,
                layer=layer, closed=closed,
                weights=weights if is_rational else None,
            ))
        return [_write]

    else:
        xy   = [(x, y) for x, y, z in cps]
        elev = cps[0][2] if cps else 0.0
        if closed and xy:
            xy.append(xy[0])

        def _write(f, h, owner):
            f.write(_entity_lwpolyline(xy, h, owner, layer=layer,
                                        closed=closed, elevation=elev))
        return [_write]


def _convert_poly(spline, matrix, scale, layer):
    pts = spline.points
    if len(pts) < 2:
        return []
    closed = spline.use_cyclic_u
    coords = [_xform(p.co[:3], matrix, scale) for p in pts]
    xy     = [(x, y) for x, y, z in coords]
    elev   = coords[0][2] if coords else 0.0
    if closed and xy:
        xy.append(xy[0])

    def _write(f, h, owner):
        f.write(_entity_lwpolyline(xy, h, owner, layer=layer, elevation=elev))
    return [_write]


# ── Grease Pencil ─────────────────────────────────────────────────────────────

def _convert_gp_legacy(obj, matrix, scale, layer):
    writers = []
    for gp_layer in obj.data.layers:
        frame = gp_layer.active_frame
        if frame is None:
            continue
        for stroke in frame.strokes:
            pts = [_xform(p.co, matrix, scale) for p in stroke.points]
            if len(pts) < 2:
                continue
            xy   = [(p[0], p[1]) for p in pts]
            elev = pts[0][2]
            def _write(f, h, owner, _xy=xy, _el=elev):
                f.write(_entity_lwpolyline(_xy, h, owner,
                                            layer=layer, elevation=_el))
            writers.append(_write)
    return writers


def _convert_gp_new(obj, matrix, scale, layer):
    writers = []
    try:
        for gp_layer in obj.data.layers:
            frame = gp_layer.current_frame()
            if frame is None:
                continue
            for stroke in frame.drawing.strokes:
                pts = [_xform(p.position, matrix, scale) for p in stroke.points]
                if len(pts) < 2:
                    continue
                closed = getattr(stroke, "cyclic", False)
                xy     = [(p[0], p[1]) for p in pts]
                elev   = pts[0][2]
                def _write(f, h, owner, _xy=xy, _cl=closed, _el=elev):
                    f.write(_entity_lwpolyline(_xy, h, owner,
                                                layer=layer, closed=_cl, elevation=_el))
                writers.append(_write)
    except Exception:
        pass
    return writers


# ── Layer registry ────────────────────────────────────────────────────────────

_ACAD_COLORS = [7, 1, 2, 3, 4, 5, 6]


def _build_layers(objects, layer_mode):
    layers    = {"0": 7}
    color_idx = [0]

    def _new(name):
        if name not in layers:
            layers[name] = _ACAD_COLORS[color_idx[0] % len(_ACAD_COLORS)]
            color_idx[0] += 1
        return name

    def resolve(obj):
        if layer_mode == "BY_OBJECT":
            return _new(obj.name[:255])
        if layer_mode == "BY_COLLECTION":
            cols = obj.users_collection
            return _new(cols[0].name[:255] if cols else "0")
        return "0"

    return layers, resolve


# ── LibreDWG  DXF → DWG conversion ───────────────────────────────────────────

def find_dxf2dwg():
    import shutil as _shutil
    addon_dir = os.path.dirname(os.path.abspath(__file__))
    bundled   = os.path.join(addon_dir, "bin", "dxf2dwg.exe")
    if os.path.isfile(bundled):
        return bundled
    bundled_nix = os.path.join(addon_dir, "bin", "dxf2dwg")
    if os.path.isfile(bundled_nix):
        return bundled_nix
    found = _shutil.which("dxf2dwg")
    if found:
        return found
    return None


def convert_dxf_to_dwg(dxf_path, dwg_path, dxf2dwg_exe):
    if not os.path.isfile(dxf2dwg_exe):
        raise RuntimeError(f"dxf2dwg not found at:\n{dxf2dwg_exe}")
    cmd = [dxf2dwg_exe, "-y", "-o", dwg_path, dxf_path]
    result = subprocess.run(cmd, capture_output=True, timeout=120)
    if result.returncode != 0 or not os.path.isfile(dwg_path):
        stderr = result.stderr.decode("utf-8", errors="replace")
        stdout = result.stdout.decode("utf-8", errors="replace")
        raise RuntimeError(
            f"dxf2dwg conversion failed (code {result.returncode}).\n"
            f"stdout: {stdout[:300]}\n"
            f"stderr: {stderr[:300]}"
        )


# ── Main export entry point ───────────────────────────────────────────────────

def export_dxf(filepath, objects, settings):
    exportable      = {"CURVE", "GPENCIL", "GREASEPENCIL"}
    layers, resolve = _build_layers(objects, settings.layer_mode)
    entity_writers  = []       # list of  (f, handle, owner) → None  callables

    for obj in objects:
        if obj.type not in exportable:
            continue
        matrix = obj.matrix_world if settings.use_world_matrix else Matrix.Identity(4)
        scale  = settings.scale
        layer  = resolve(obj)

        if obj.type == "CURVE":
            for spline in obj.data.splines:
                if spline.type == "BEZIER":
                    entity_writers += _convert_bezier(
                        spline, matrix, scale, layer,
                        settings.output_splines,
                        settings.tessellation_samples,
                    )
                elif spline.type == "NURBS":
                    entity_writers += _convert_nurbs(
                        spline, matrix, scale, layer,
                        settings.output_splines,
                    )
                elif spline.type == "POLY":
                    entity_writers += _convert_poly(
                        spline, matrix, scale, layer,
                    )
        elif obj.type == "GPENCIL":
            entity_writers += _convert_gp_legacy(obj, matrix, scale, layer)
        elif obj.type == "GREASEPENCIL":
            entity_writers += _convert_gp_new(obj, matrix, scale, layer)

    units_code = UNITS_CODES.get(settings.units, 4)

    with open(filepath, "w", encoding="utf-8", newline="\r\n") as f:
        _write_dxf_file(f, entity_writers, layers, units_code)
