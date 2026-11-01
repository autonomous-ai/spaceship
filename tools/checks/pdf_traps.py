"""Read an exported drawing PDF back for the PM's four drawing traps (2026-11-01, after CEILING's first
sample), for C05: what reached the paper, not what a script meant to draw.

    python3 tools/checks/pdf_traps.py DRAWING.pdf [--allow-hidden-views N]

1. Letter height: every text at least 2.5 mm capital height (font size x 0.718, as the reviewers measure,
   ISO 3098); title-block texts at least 1.8 mm (Fusion's TITLEBLOCK layer; on a generated sheet with no
   layers, the drawn box in the frame's bottom-right corner, else the corner's 190 x 60 mm). Fusion inserts a picture 58 mm wide whatever its pixels,
   so a notes picture can print its text about 1.6 mm high. -> major
2. The first-angle symbol: its outline must have 4 corners. Sharing a sketch with the circles, Fusion's PDF
   export dropped a corner and printed a triangle. Read from the symbol's layer (Fusion names a sketch's layer
   after the sketch: "PROJECTION SYMBOL - FIRST ANGLE"); a layer holding only curves is the circles. -> major
3. Hidden lines: Fusion ignores the view style given at creation, so views show hidden lines unless it is set
   again. Fusion puts them on its "Hidden" layer and writes each dash as its own short line, so the pieces are
   grouped into the view regions they sit in; a drawing that keeps hidden lines on purpose in N views passes
   with allow_hidden_views=N (an allow list, like config/clash-allow.csv). -> minor
4. A dimension printed twice: the same value twice among the texts on Fusion's "FD_Dimensions" layer. Two
   different features can share a value, so it asks for a look. -> minor

PyMuPDF reads the layers: get_drawings() gives each path's layer, get_texttrace() each text's.
"""

import argparse
import sys
from collections import Counter

MM = 72.0 / 25.4
CAP = 0.718                       # capital height / font size, the reviewers' figure (Helvetica 718/1000 em)
BODY_MIN, TITLE_BLOCK_MIN = 2.5, 1.8
TITLE_ZONE = (190.0, 60.0)        # mm from the frame's bottom-right corner, when no title-block box is drawn there
SYMBOL = "PROJECTION SYMBOL - FIRST ANGLE"
VIEW_GAP = 6.0                    # mm: hidden pieces closer than this are one view's


def _text(t):
    return "".join(chr(c[0]) for c in t["chars"])


def _corners(path):
    """The corners of a path's straight pieces (lines, quads, rectangles), rounded to 0.1 mm; curves left out."""
    out = set()
    for it in path["items"]:
        if it[0] == "l":
            pts = [it[1], it[2]]
        elif it[0] == "qu":
            q = it[1]
            pts = [q.ul, q.ur, q.lr, q.ll]
        elif it[0] == "re":
            r = it[1]
            pts = [r.tl, r.tr, r.br, r.bl]
        else:
            continue
        out |= {(round(p.x / MM, 1), round(p.y / MM, 1)) for p in pts}
    return out


def _regions(rects, gap=VIEW_GAP):
    """Rectangles (mm) joined into regions where they come within `gap` of each other."""
    parent = list(range(len(rects)))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for i, a in enumerate(rects):
        for j in range(i + 1, len(rects)):
            b = rects[j]
            if a[0] - gap <= b[2] and b[0] - gap <= a[2] and a[1] - gap <= b[3] and b[1] - gap <= a[3]:
                parent[root(i)] = root(j)
    out = {}
    for i, r in enumerate(rects):
        o = out.setdefault(root(i), list(r))
        o[0], o[1], o[2], o[3] = min(o[0], r[0]), min(o[1], r[1]), max(o[2], r[2]), max(o[3], r[3])
    return [tuple(round(c, 1) for c in o) for o in out.values()]


def _title_block(drawings, w, h):
    """The title block's box (mm) on a sheet with no layers: the largest drawn box, up to 200 x 120 mm, whose
    bottom-right corner is a frame's (a drawn box covering over half the page); else TITLE_ZONE in the corner
    of the first frame, or of the page less 10 mm."""
    rects = [tuple(c / MM for c in (d["rect"].x0, d["rect"].y0, d["rect"].x1, d["rect"].y1)) for d in drawings]
    frames = [r for r in rects if r[2] - r[0] > 0.5 * w and r[3] - r[1] > 0.5 * h]
    corner = [r for r in rects if 20.0 < r[2] - r[0] <= 200.0 and 20.0 < r[3] - r[1] <= 120.0 and
              any(abs(r[2] - f[2]) < 1.0 and abs(r[3] - f[3]) < 1.0 for f in frames)]
    if corner:
        return max(corner, key=lambda r: (r[2] - r[0]) * (r[3] - r[1]))
    inner = min(frames, key=lambda f: (f[2] - f[0]) * (f[3] - f[1])) if frames else (10.0, 10.0, w - 10.0, h - 10.0)
    return (inner[2] - TITLE_ZONE[0], inner[3] - TITLE_ZONE[1], inner[2], inner[3])


def read(path):
    """Per page: its size (mm), the small texts, the symbol outlines' corner counts, the hidden-line view
    regions and the dimension texts."""
    import fitz
    pages = []
    for page in fitz.open(path):
        w, h = page.rect.width / MM, page.rect.height / MM
        drawings = page.get_drawings()
        tb = _title_block(drawings, w, h)
        small = []
        dims = []
        for t in page.get_texttrace():
            s = _text(t).strip()
            if not s:
                continue
            layer = t.get("layer") or ""
            cap = t["size"] / MM * CAP
            x0, y0, x1, y1 = (c / MM for c in t["bbox"])
            in_tb = layer == "TITLEBLOCK" or (x0 >= tb[0] - 0.5 and y0 >= tb[1] - 0.5 and x1 <= tb[2] + 0.5 and
                                              y1 <= tb[3] + 0.5)
            if cap < (TITLE_BLOCK_MIN if in_tb else BODY_MIN) - 1e-6:
                small.append((round(cap, 2), s, layer or ("title block" if in_tb else "")))
            if layer == "FD_Dimensions" and any(ch.isdigit() for ch in s):
                dims.append(s)
        symbols = {}
        hidden = []
        for d in drawings:
            layer = d.get("layer") or ""
            if layer.startswith(SYMBOL) and "CIRCLES" not in layer:
                symbols.setdefault(layer, set()).update(_corners(d))
            elif layer == "Hidden":
                r = d["rect"]
                hidden.append((r.x0 / MM, r.y0 / MM, r.x1 / MM, r.y1 / MM))
        pages.append({"size_mm": (round(w, 1), round(h, 1)), "small_texts": small,
                      "symbol_corners": {k: len(v) for k, v in symbols.items() if v},     # curves only: the circles
                      "hidden_pieces": len(hidden),
                      "hidden_views": _regions(hidden), "dimension_texts": dims})
    return pages


def findings(path, allow_hidden_views=0):
    """[(rule, severity, message, fix)] for the four traps, every page of one drawing PDF."""
    out = []
    pages = read(path)
    for n, pg in enumerate(pages, start=1):
        on = " (sheet %d)" % n if len(pages) > 1 else ""
        if pg["small_texts"]:
            least = min(c for c, _s, _l in pg["small_texts"])
            sample = "; ".join("%r %.2f mm" % (s[:30], c) for c, s, _l in pg["small_texts"][:3])
            out.append(("letter-height", "major",
                        "%d texts%s print under 2.5 mm capital height (title-block labels under 1.8), the smallest "
                        "%.2f mm: %s." % (len(pg["small_texts"]), on, least, sample),
                        "Size text by its capital height: font size = 2.5 / 0.718 = 3.5 mm or more; a picture "
                        "inserted in Fusion comes in 58 mm wide, so scale it to its real width "
                        "(tools/fusion/fusion_drawing.py insert_image)."))
        for layer, k in sorted(pg["symbol_corners"].items()):
            if k != 4:
                out.append(("symbol-outline", "major",
                            "The first-angle symbol's outline%s (layer %r) has %d corners, not 4%s." % (
                                on, layer, k, ": it prints as a triangle" if k == 3 else ""),
                            "Draw the outline alone in its own sketch, the circles in another "
                            "(tools/fusion/fusion_drawing.py first_angle_symbol)."))
        views = len(pg["hidden_views"])
        if views > allow_hidden_views:
            out.append(("hidden-lines", "minor",
                        "Hidden lines show in %d view region(s)%s (%d dash pieces on Fusion's Hidden layer)%s." % (
                            views, on, pg["hidden_pieces"],
                            "; %d allowed" % allow_hidden_views if allow_hidden_views else ""),
                        "Set the view style again on the made view (Fusion ignores the input's style; "
                        "tools/fusion/fusion_drawing.py base_view); or, if the drawing keeps them on purpose, "
                        "list it with the number of views and the reason."))
        twice = sorted(v for v, c in Counter(pg["dimension_texts"]).items() if c > 1)
        if twice:
            out.append(("dimension-twice", "minor",
                        "Dimension value(s) printed more than once%s: %s." % (on, ", ".join(twice)),
                        "Give each size once (ISO 129-1); two different features may share a value, so check "
                        "which this is (tools/fusion/fusion_drawing.py DimensionSet)."))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("pdf", nargs="+")
    ap.add_argument("--allow-hidden-views", type=int, default=0)
    a = ap.parse_args(argv)
    bad = 0
    for p in a.pdf:
        fs = findings(p, a.allow_hidden_views)
        print("%s: %s" % (p, "clear" if not fs else "%d finding(s)" % len(fs)))
        for rule, sev, msg, _fix in fs:
            print("  %-6s %-16s %s" % (sev, rule, msg))
        bad += bool(fs)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
