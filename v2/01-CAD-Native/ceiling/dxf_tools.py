"""DXF helpers for the ceiling's cut files (standard library only).

- relayer(): puts Fusion's flat-pattern layers onto the project's CUT / BEND /
  MARK layers (guideline 9). The geometry is copied unchanged.
- write_dxf(): writes simple 1:1 mm cut files (lines, closed polylines,
  circles) for the flat parts that aren't sheet metal (felt, fill, skin) and
  for the rib blank.
- summary(): unit, layers, entity counts and extents of a DXF, for the checks.

Fusion's flat-pattern layer names (DXFFlatPatternExportOptions, 2706.1):
OUTER_PROFILES and INTERIOR_PROFILES are cut lines, BEND the bend lines,
BEND_EXTENT the edges of each bend zone.
"""

import re

LAYER_MAP = {
    "OUTER_PROFILES": "CUT",
    "INTERIOR_PROFILES": "CUT",
    "BEND": "BEND",
    "BEND_UP": "BEND",
    "BEND_DOWN": "BEND",
    "BEND_EXTENT": "MARK",
}


def _pairs(text):
    lines = text.splitlines()
    if len(lines) % 2:
        lines.append("")
    return [(lines[i], lines[i + 1]) for i in range(0, len(lines), 2)]


def relayer(src, dst, mapping=LAYER_MAP, default="MARK"):
    """Rename every layer reference (group code 8, and layer table names, code 2
    inside LAYER records). Returns {old: new} for the layers seen."""
    text = open(src, encoding="utf-8", errors="replace").read()
    pairs = _pairs(text)
    seen = {}
    out = []
    in_layer_table, in_layer_rec = False, False
    for code, val in pairs:
        c, v = code.strip(), val.strip()
        if c == "0":
            in_layer_rec = in_layer_table and v == "LAYER"
            if v == "ENDTAB":
                in_layer_table = False
        if c == "2" and v == "LAYER" and not in_layer_rec:
            in_layer_table = True
        if (c == "8" or (c == "2" and in_layer_rec)) and v not in ("0", "LAYER"):
            new = mapping.get(v, default)
            seen[v] = new
            val = val.replace(v, new)
        out.append((code, val))
    out = world_circles(out)
    # merge duplicate layer records that now share a name: keep the first
    result, names, skip = [], set(), False
    i = 0
    while i < len(out):
        code, val = out[i]
        if code.strip() == "0" and val.strip() == "LAYER" and in_table_layer(out, i):
            j = i + 1
            name = None
            while j < len(out) and out[j][0].strip() != "0":
                if out[j][0].strip() == "2":
                    name = out[j][1].strip()
                j += 1
            if name in names:
                i = j
                continue
            names.add(name)
        result.append((code, val))
        i += 1
    with open(dst, "w", encoding="utf-8", newline="\n") as fh:
        for code, val in result:
            fh.write("%s\n%s\n" % (code, val))
    return seen


def world_circles(pairs):
    """Circles that Fusion writes with the extrusion direction (0, 0, -1) have a mirrored
    object coordinate system (X(world) = -X(file)). Rewrite them in world coordinates
    (negate X, extrusion (0, 0, 1)), so every CAM reader places them the same way.
    Same circle, same size; only how the file states it changes."""
    out = list(pairs)
    i = 0
    while i < len(out):
        c, v = out[i][0].strip(), out[i][1].strip()
        if c == "0" and v in ("CIRCLE", "ARC"):
            j = i + 1
            while j < len(out) and out[j][0].strip() != "0":
                j += 1
            ent = out[i + 1:j]
            codes = {p[0].strip(): k for k, p in enumerate(ent)}
            if "230" in codes and float(ent[codes["230"]][1]) < -0.5:
                if v == "ARC":
                    raise ValueError("ARC with a mirrored OCS: not handled")
                k = codes["10"]
                ent[k] = (ent[k][0], repr(-float(ent[k][1])))
                k = codes["230"]
                ent[k] = (ent[k][0], "1")
                out[i + 1:j] = ent
            i = j
            continue
        i += 1
    return out


def in_table_layer(out, i):
    """True when the LAYER entity at i sits inside the LAYER table."""
    for k in range(i - 1, -1, -1):
        c, v = out[k][0].strip(), out[k][1].strip()
        if c == "0" and v in ("TABLE", "ENDTAB", "SECTION", "ENDSEC"):
            if v == "TABLE":
                return k + 1 < len(out) and out[k + 1][1].strip() == "LAYER"
            return False
    return False


def write_dxf(path, entities, layers=("CUT", "BEND", "MARK")):
    """entities: ("LINE", layer, (x1, y1), (x2, y2)) | ("POLY", layer, [(x, y), ...]) closed |
    ("CIRCLE", layer, (cx, cy), r). Units mm ($INSUNITS 4), AutoCAD R12 entities."""
    colours = {"CUT": 7, "BEND": 1, "MARK": 3}
    w = []

    def g(c, v):
        w.append("%d\n%s" % (c, v))
    g(0, "SECTION"); g(2, "HEADER")
    g(9, "$INSUNITS"); g(70, 4)
    g(9, "$MEASUREMENT"); g(70, 1)
    g(0, "ENDSEC")
    g(0, "SECTION"); g(2, "TABLES")
    g(0, "TABLE"); g(2, "LAYER"); g(70, len(layers))
    for name in layers:
        g(0, "LAYER"); g(2, name); g(70, 0); g(62, colours.get(name, 7)); g(6, "CONTINUOUS")
    g(0, "ENDTAB")
    g(0, "ENDSEC")
    g(0, "SECTION"); g(2, "ENTITIES")
    for e in entities:
        kind, layer = e[0], e[1]
        if kind == "LINE":
            (x1, y1), (x2, y2) = e[2], e[3]
            g(0, "LINE"); g(8, layer)
            g(10, "%.4f" % x1); g(20, "%.4f" % y1); g(30, "0.0")
            g(11, "%.4f" % x2); g(21, "%.4f" % y2); g(31, "0.0")
        elif kind == "POLY":
            pts = e[2]
            g(0, "POLYLINE"); g(8, layer); g(66, 1); g(70, 1)
            g(10, "0.0"); g(20, "0.0"); g(30, "0.0")
            for x, y in pts:
                g(0, "VERTEX"); g(8, layer); g(10, "%.4f" % x); g(20, "%.4f" % y); g(30, "0.0")
            g(0, "SEQEND"); g(8, layer)
        elif kind == "CIRCLE":
            (cx, cy), r = e[2], e[3]
            g(0, "CIRCLE"); g(8, layer); g(10, "%.4f" % cx); g(20, "%.4f" % cy); g(30, "0.0"); g(40, "%.4f" % r)
        else:
            raise ValueError(kind)
    g(0, "ENDSEC")
    g(0, "EOF")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(w) + "\n")


def summary(path):
    """{'insunits': n, 'entities': {(type, layer): count}, 'extents': (xmin, ymin, xmax, ymax), 'layers': set}"""
    pairs = _pairs(open(path, encoding="utf-8", errors="replace").read())
    ins = None
    ents = {}
    xs, ys = [], []
    in_ent = False
    cur = None
    layer = None
    for k, (c, v) in enumerate(pairs):
        c, v = c.strip(), v.strip()
        if c == "9" and v == "$INSUNITS" and k + 1 < len(pairs):
            ins = int(pairs[k + 1][1].strip())
        if c == "2" and v == "ENTITIES":
            in_ent = True
            continue
        if in_ent and c == "0":
            if cur and cur not in ("VERTEX", "SEQEND"):
                ents[(cur, layer)] = ents.get((cur, layer), 0) + 1
            cur, layer = v, None
            if v == "ENDSEC":
                in_ent = False
                cur = None
        elif in_ent:
            if c == "8":
                layer = v
            elif c in ("10", "11"):
                xs.append(float(v))
            elif c in ("20", "21"):
                ys.append(float(v))
    layers = {l for (_t, l) in ents}
    ext = (min(xs), min(ys), max(xs), max(ys)) if xs else None
    return {"insunits": ins, "entities": ents, "extents": ext, "layers": layers}


if __name__ == "__main__":
    import sys
    for p in sys.argv[1:]:
        s = summary(p)
        print(p, s["insunits"], s["extents"], sorted(s["entities"].items()))
