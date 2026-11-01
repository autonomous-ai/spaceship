"""Step pictures for the assembly guide: exact line drawings of the parts' own CAD, made outside Fusion.

    DG=$HOME/.cache/spaceship-drawgen/venv-ocp7.8.1-mupdf1.27.2/bin/python   # drawgen's own Python (tools/drawgen/run.sh)
    $DG v2/02-Drawings/30-Assembly-Instructions/step_drawings.py                    # every step's picture, into img/
    $DG v2/02-Drawings/30-Assembly-Instructions/step_drawings.py --steps 2,4 --out DIR   # a sample, written elsewhere
    $DG v2/02-Drawings/30-Assembly-Instructions/step_drawings.py --check            # redraw in a scratch folder: same bytes?

For each guide step that fits parts (v2/07-Packaging/pack.py's STEPS), every piece fitted up to that step is drawn
from its own CAD on main, picked by pack.py's CAD map with its rules (sub-assembly, occurrence, keep, drop, plus). A
piece with no CAD yet is drawn dashed from its skeleton P04 block and labelled CAD TO COME, so nobody takes a block
for the real part. Hidden lines are removed exactly (drawgen's hidden-line projection, never the polygonal one).

The step's new pieces are black and heavy, each with a balloon holding its packing label, the number the guide's
step names in its Parts line; the pieces fitted before are light grey. Each step has its own camera (CAMERAS), picked
so the step's action shows, and an arrow where the direction of a move matters (MOVES). The step's fixings, as the
guide counts them, are listed under the picture.

Balloons come from drawgen's assembly mode through its public functions only (hlr, AView, Occ, Item, Side,
place_balloons, Sheet); the read-back (check_pdf) reads each PDF back with drawgen's public readers before its PNG
is written: every balloon holds one of the step's labels, every label has its balloon, each balloon's leader ends on
its own part in 3D, and each part with no CAD carries its CAD TO COME note. The PNGs are what the guide shows
(pack.py puts each under its step); they redraw byte for byte the same (--check).
"""

import argparse
import math
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "tools" / "drawgen"))

import fitz  # noqa: E402  PyMuPDF, in drawgen's own Python
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex  # noqa: E402
from OCP.BRepExtrema import BRepExtrema_DistShapeShape  # noqa: E402
from OCP.STEPCAFControl import STEPCAFControl_Reader  # noqa: E402
from OCP.TCollection import TCollection_ExtendedString  # noqa: E402
from OCP.TDataStd import TDataStd_Name  # noqa: E402
from OCP.TDF import TDF_Label, TDF_LabelSequence  # noqa: E402
from OCP.TDocStd import TDocStd_Document  # noqa: E402
from OCP.TopAbs import TopAbs_SOLID  # noqa: E402
from OCP.TopExp import TopExp_Explorer  # noqa: E402
from OCP.TopLoc import TopLoc_Location  # noqa: E402
from OCP.TopoDS import TopoDS  # noqa: E402
from OCP.XCAFDoc import XCAFDoc_DocumentTool  # noqa: E402
from OCP.gp import gp_Pnt, gp_Trsf, gp_Vec  # noqa: E402

import assembly  # noqa: E402  drawgen's assembly mode: public names only
import geom  # noqa: E402
import readback  # noqa: E402
from project import View  # noqa: E402
from sheet import MM, Sheet  # noqa: E402

# pack.py loads the layout study's inputs.py, and drawgen has an inputs.py (and an assembly.py) of its own: drawgen's
# modules are loaded first, pack.py then gets the layout study's inputs, and drawgen's goes back for drawgen's code
_DRAWGEN_INPUTS = sys.modules.pop("inputs", None)
sys.path.insert(0, str(REPO / "v2" / "07-Packaging"))
import pack  # noqa: E402
if _DRAWGEN_INPUTS is not None:
    sys.modules["inputs"] = _DRAWGEN_INPUTS

IMG = HERE / "img"
SHEET = "A3"                    # 420 x 297 mm, landscape
DPI = 120                       # 1984 x 1403 px
AREA = (48.0, 52.0, 372.0, 262.0)   # the parts' box on the sheet (x0, y0, x1, y1, mm); balloon lanes round it
GREY = (0.62, 0.62, 0.62)
W_NEW, W_OLD, W_MOVE = 0.5, 0.18, 0.7
DASH_TBC = (2.0, 1.2)           # a part with no CAD yet: its skeleton block, dashed
TEXT, HEAD = 2.5, 3.5
TBC = "CAD TO COME"
MARGIN = (22.0, 12.0)           # the sheet's free margins left and right (drawgen's Sheet.is_free)

# Each step's camera: the direction toward the viewer (pod system: +X right, +Y back, +Z up) and the pieces left out
# so the step's action shows (a cut-away, said under the picture).
_SHELL = ("1-09", "1-10")                                   # the ceiling halves
_FRONT = ("2-01", "2-02", "2-03", "2-08", "2-11")           # the glass, the door and the decor blocks
_OPEN = ("2-01", "2-02", "2-08", "2-11")                     # the front but DR: the glass, the door, DL and DT
BACK_LEFT = (-0.55, 0.68, 0.48)
FRONT_RIGHT = (0.52, -0.78, 0.36)
FRONT_LEFT = (-0.52, -0.78, 0.36)
INSIDE = (0.12, -0.55, 0.83)
INSIDE_LEFT = (-0.48, -0.58, 0.66)
CAMERAS = {
    2: dict(n=FRONT_RIGHT),
    3: dict(n=BACK_LEFT), 4: dict(n=BACK_LEFT), 5: dict(n=BACK_LEFT), 6: dict(n=BACK_LEFT),
    7: dict(n=FRONT_LEFT),
    8: dict(n=FRONT_LEFT),
    9: dict(n=FRONT_RIGHT),
    10: dict(n=FRONT_RIGHT),
    11: dict(n=FRONT_RIGHT),
    13: dict(n=INSIDE_LEFT, hide=_SHELL + _FRONT),     # the riser goes in where DR's inner face came off
    14: dict(n=INSIDE, hide=_SHELL + _FRONT),
    15: dict(n=INSIDE_LEFT, hide=_SHELL + _OPEN),
    16: dict(n=INSIDE_LEFT, hide=_SHELL + _OPEN),
    17: dict(n=(0.35, -0.45, 0.82)),
    18: dict(n=INSIDE, hide=_SHELL + _FRONT),
    19: dict(n=INSIDE_LEFT, hide=_SHELL + _OPEN),
    22: dict(n=INSIDE_LEFT, hide=_SHELL + _OPEN),
}
# A move whose direction matters: the piece, and the way it goes (pod system).
DOWN = (0.0, 0.0, -1.0)
MOVES = {
    2: [("2-04", DOWN)],
    3: [("1-01", DOWN), ("1-02", DOWN)],
    5: [("1-05", DOWN), ("1-06", DOWN)],
    6: [("1-07", DOWN), ("1-08", DOWN)],
    7: [("1-09", DOWN), ("1-10", DOWN)],
    8: [("2-08", (0.0, 1.0, 0.0))],                  # pulled in on its 2 pins onto its stops (D-169)
    9: [("2-03", (-1.0, 0.0, 0.0))],
    11: [("2-11", DOWN)],
}
# A part that goes into another is drawn lifted clear of it by this much (mm, pod system), with an arrow into place.
EXPLODE = {
    13: {"2-16": (0.0, 0.0, 700.0)},                 # down into DR, its inner face off
    14: {"2-23": (-450.0, 0.0, 0.0)},                # R1's fill, into R1's bays from the room before its cassette
    15: {"2-17": (0.0, -700.0, 0.0)},                # into the air column from the front, its front face off
    16: {"2-18": (0.0, 0.0, -600.0)},                # up through the soffit's open underside onto its rest
    17: {"611601": (0.0, 0.0, 450.0), "611602": (0.0, 0.0, 800.0)},   # down through C2's roof slot; the grille over it
    19: {"2-13": (0.0, 0.0, 450.0)},                 # down onto the tops of the side and back walls
}
# A piece that ships without CAD of its own but is drawn from another piece's CAD where it goes in: R1's fill bag, from
# the fill in R1's STEP (R1 itself drops it: pack.py's CAD map).
PICTURE_CAD = {"2-23": dict(step="wall/210102_P01_*_STEP.step", keep={"211502"})}
# Parts fitted in a later step than the piece they ship with: drawn from that step on, ballooned by their part number.
LATE = {"1-10": [(17, "611601", dict(step=pack.AIR_STEP, sub="611601")), (17, "611602", dict(step=pack.AIR_STEP, sub="611602"))]}


# ------------------------------------------------------------------ the parts' solids

_TREES = {}


def _name(lab):
    a = TDataStd_Name()
    return a.Get().ToExtString() if lab.FindAttribute(TDataStd_Name.GetID_s(), a) else ""


def _solids(shape):
    out, e = [], TopExp_Explorer(shape, TopAbs_SOLID)
    while e.More():
        out.append(TopoDS.Solid_s(e.Current()))
        e.Next()
    return out


def leaves(path):
    """[(part number, product name, occurrence names from the top, [solids in the file's top coordinates, mm])] for
    every body in a STEP (OCC's XCAF reader). The trail is named as the mechanical checks' reader names it (the top's
    product, then each occurrence), so pack.py's CAD rules apply unchanged."""
    path = Path(path)
    if path not in _TREES:
        doc = TDocStd_Document(TCollection_ExtendedString("XmlOcaf"))
        r = STEPCAFControl_Reader()
        r.SetNameMode(True)
        if int(r.ReadFile(str(path))) != 1 or not r.Transfer(doc):
            raise RuntimeError("STEP read failed: %s" % path)
        st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
        tops = TDF_LabelSequence()
        st.GetFreeShapes(tops)
        out = []

        def walk(lab, loc, trail):
            if st.IsAssembly_s(lab):
                comps = TDF_LabelSequence()
                st.GetComponents_s(lab, comps)
                for i in range(1, comps.Length() + 1):
                    c = comps.Value(i)
                    ref = TDF_Label()
                    st.GetReferredShape_s(c, ref)
                    walk(ref, loc.Multiplied(st.GetLocation_s(c)), trail + [_name(c) or _name(ref)])
                return
            shape = st.GetShape_s(lab)
            if not loc.IsIdentity():
                shape = shape.Moved(loc)
            name = _name(lab)
            out.append((geom.part_number_of(name) or "", name, trail, _solids(shape)))

        for i in range(1, tops.Length() + 1):
            walk(tops.Value(i), TopLoc_Location(), [_name(tops.Value(i))])
        _TREES[path] = out
    return _TREES[path]


def one_step_file(pattern):
    hits = sorted(pack.MANUF.glob(pattern))
    if len(hits) != 1:
        raise FileNotFoundError("%d STEP files match v2/03-Manufacturing/%s" % (len(hits), pattern))
    return hits[0]


def pick(spec):
    """The solids one pack.py CAD entry picks, by pack.cad_solids' own rules (sub, occ, keep, drop, plus)."""
    out = []
    for pn, name, trail, solids in leaves(one_step_file(spec["step"])):
        top = trail[1] if len(trail) > 1 else ""
        if spec.get("sub") and not (top.split(" ")[0] == spec["sub"] or pn == spec["sub"]):
            continue
        if spec.get("occ") and not top.endswith(":%d" % spec["occ"]):
            continue
        base = pn.split("_")[0]
        if spec.get("keep") and base not in spec["keep"]:
            continue
        if any(base == d or d in name for d in spec.get("drop", {})):
            continue
        out += solids
    for extra in spec.get("plus", ()):
        out += pick(extra)
    return out


def late_specs(tag):
    return [sp for _n, _pn, sp in LATE.get(tag, [])]


def piece_solids(tag):
    """(solids, has_cad): the piece's solids from its CAD on main; with no CAD entry, its skeleton P04 blocks."""
    spec = pack.CAD.get(tag) or PICTURE_CAD.get(tag)
    if spec:
        if "parts" in spec:
            solids = [s for sp in spec["parts"] for s in pick(sp)]
        else:
            late = late_specs(tag)
            spec = dict(spec, plus=[sp for sp in spec.get("plus", ()) if sp not in late])
            solids = pick(spec)
        if not solids:
            raise LookupError("%s: its CAD entry picks no solid" % tag)
        return solids, True
    codes = {b.split(" ")[0] for b in pack.SKEL.get(tag, [])}
    solids = [s for _pn, name, _t, ss in leaves(pack.SKELETON_STEP) if name.split(" ")[0] in codes for s in ss]
    return solids, False


class Blank(int):
    """The item number place_balloons writes in its circle: nothing (the packing label goes in after, it is wider),
    while drawgen's own messages still format it as a number."""

    def __str__(self):
        return ""


class Part:
    """One thing a picture draws: a packing label's piece (or a part fitted later than its piece), its solids, whether
    they are its own CAD, and the step that fits it."""

    def __init__(self, label, solids, cad, step):
        self.label, self.solids, self.cad, self.step = label, solids, cad, step
        self.shape = geom.compound(solids)


def parts_up_to(n):
    """Every part fitted in steps 1 to n, in fitting order; a piece with neither CAD nor a skeleton block is skipped
    (its step names it; the picture can't)."""
    out = []
    for st in pack.STEPS:
        if st["n"] > n:
            break
        for tag in st["tags"]:
            solids, cad = piece_solids(tag)
            if solids:
                out.append(Part(tag, solids, cad, st["n"]))
        for tag, extras in LATE.items():
            for step, pn, sp in extras:
                if step == st["n"]:
                    out.append(Part(pn, pick(sp), True, step))
    return out


def new_labels(st):
    """What the step's text names as its new parts: its Parts line (the labels), and the parts LATE fits here."""
    return list(st["tags"]) + [pn for extras in LATE.values() for step, pn, _sp in extras if step == st["n"]]


def picture_steps():
    return [st["n"] for st in pack.STEPS if st["n"] in CAMERAS]


# ------------------------------------------------------------------ drawing

def _prim_points(p, scale):
    """A 2D primitive as a polyline (view mm), fine enough at this scale."""
    if p.kind == "line":
        return [p.p, p.q]
    if p.kind == "arc":
        k = max(2, int(math.ceil(abs(p.a1 - p.a0) * p.r * scale / 0.8)), int(abs(p.a1 - p.a0) / (math.pi / 36)))
        return [(p.c[0] + p.r * math.cos(p.a0 + (p.a1 - p.a0) * i / k), p.c[1] + p.r * math.sin(p.a0 + (p.a1 - p.a0) * i / k))
                for i in range(k + 1)]
    pts = []
    q = p.pts
    for i in range(0, len(q) - 3, 3):
        for k in range(0 if not pts else 1, 9):
            t = k / 8.0
            a, b, c, d = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3
            pts.append((a * q[i][0] + b * q[i + 1][0] + c * q[i + 2][0] + d * q[i + 3][0],
                        a * q[i][1] + b * q[i + 1][1] + c * q[i + 2][1] + d * q[i + 3][1]))
    return pts


def camera(n):
    nv = geom.vnorm(CAMERAS[n]["n"])
    x = geom.vnorm(geom.vcross((0.0, 0.0, 1.0), nv))
    return View("step%d" % n, nv, x, geom.vcross(nv, x))


def _box3(solids):
    return assembly.box_of(solids)


def exploded(p, e):
    """The part moved by e (mm): drawn clear of what it goes into."""
    t = gp_Trsf()
    t.SetTranslation(gp_Vec(*e))
    return Part(p.label, [geom.transformed(s_, t) for s_ in p.solids], p.cad, p.step)


def draw_step(n, out_dir):
    """Draw step n's picture: (pdf bytes, png path, record of what it shows)."""
    st = next(s for s in pack.STEPS if s["n"] == n)
    hide = set(CAMERAS[n].get("hide", ()))
    lift = EXPLODE.get(n, {})
    parts = [exploded(p, lift[p.label]) if p.step == n and p.label in lift else p
             for p in parts_up_to(n) if p.label not in hide or p.step == n]
    new = [p for p in parts if p.step == n]
    if not new:
        raise LookupError("step %d: nothing to draw" % n)
    view = camera(n)
    per = assembly.hlr([p.shape for p in parts], view)
    sh = Sheet(SHEET, creator="step_drawings.py", title="Assembly guide step %d" % n, subject=st["title"])
    occs, items = [], []
    for k, (p, prims) in enumerate(zip(parts, per)):
        o = assembly.Occ(p.label, p.label, p.solids)
        it = assembly.Item(p.label, None, [o], ref=p.step != n)
        it.no = Blank(k + 1)            # place_balloons draws the circle; the label goes in below (it is wider)
        occs.append(o)
        items.append(it)
    av = assembly.AView("principal", view, [[q for q in ps if q.vis] for ps in per])
    moves = []
    for label, e in lift.items():       # from the lifted part toward where it goes
        p = next(q for q in new if q.label == label)
        L = math.sqrt(sum(v * v for v in e))
        d = tuple(-v / L for v in e)
        b = _box3(p.solids)
        c = ((b[0] + b[3]) / 2, (b[1] + b[4]) / 2, (b[2] + b[5]) / 2)
        half = sum(abs(d[k]) * (b[k + 3] - b[k]) / 2 for k in range(3))
        anchor = tuple(c[k] + d[k] * half for k in range(3))
        moves.append((label, view.to2d(tuple(anchor[k] + d[k] * 0.15 * L for k in range(3))),
                      view.to2d(tuple(anchor[k] + d[k] * 0.85 * L for k in range(3)))))
    for label, d in MOVES.get(n, []):
        p = next((q for q in new if q.label == label), None)
        if p is None:
            raise LookupError("step %d: an arrow for %s, which the step doesn't fit" % (n, label))
        b = _box3(p.solids)
        c = ((b[0] + b[3]) / 2, (b[1] + b[4]) / 2, (b[2] + b[5]) / 2)
        half = sum(abs(d[k]) * (b[k + 3] - b[k]) / 2 for k in range(3))
        anchor = tuple(c[k] - d[k] * half for k in range(3))
        moves.append((label, view.to2d(tuple(anchor[k] - d[k] * 420.0 for k in range(3))),
                      view.to2d(tuple(anchor[k] - d[k] * 70.0 for k in range(3)))))
    x0, y0, x1, y1 = av.extent
    for _lb, a, b in moves:
        x0, y0, x1, y1 = min(x0, a[0], b[0]), min(y0, a[1], b[1]), max(x1, a[0], b[0]), max(y1, a[1], b[1])
    av.scale = min((AREA[2] - AREA[0]) / (x1 - x0), (AREA[3] - AREA[1]) / (y1 - y0))
    av.off = ((AREA[0] + AREA[2]) / 2 - av.scale * (x0 + x1) / 2, (AREA[1] + AREA[3]) / 2 - av.scale * (y0 + y1) / 2)

    class Assy:     # what place_balloons reads: the occurrences in the view's order, their shapes, its name
        pn = "step %d" % n
        shapes = [p.shape for p in parts]

    Assy.occs = occs
    # the parts: grey (fitted before) under black (this step); a part with no CAD dashed
    order = sorted(range(len(parts)), key=lambda i: parts[i].step == n)
    obst = []
    for i in order:
        p = parts[i]
        colour, width = ((0, 0, 0), W_NEW) if p.step == n else (GREY, W_OLD)
        dashes = None if p.cad else "[%s] 0" % " ".join("%.3f" % (v * MM) for v in DASH_TBC)
        shp = sh.page.new_shape()
        for q in av.prims[i]:
            pts = [av.S(v) for v in _prim_points(q, av.scale)]
            shp.draw_polyline([sh.P(*v) for v in pts])
            obst += list(zip(pts[:-1], pts[1:]))
        shp.finish(width=width * MM, color=colour, dashes=dashes, closePath=False, lineCap=1, lineJoin=1)
        shp.commit()
    sh.add_obstacles(obst)
    # title, fixings and legend first, so the balloons keep clear of them
    sh.text(24.0, sh.H - 18.0, "STEP %d. %s" % (n, st["title"].upper()), HEAD, bold=True)
    notes = fixings_lines(st)
    if hide & {p.label for p in parts_up_to(n)}:
        notes.append("Left out so the step shows: %s." % ", ".join(sorted(hide & {p.label for p in parts_up_to(n)})))
    legend = "Black: this step's parts, each with its packing label. Grey: parts fitted before."
    if any(not p.cad for p in parts):
        legend += " Dashed: a part whose CAD is still to come, drawn as the skeleton's block (%s)." % TBC
    y = 30.0
    for line in notes + [legend]:
        for ln in sh.wrap(line, TEXT, sh.W - 48.0):
            sh.text(24.0, y, ln, TEXT)
            y -= 4.0
    # arrows where the direction of a move matters, next to the moving part
    moved = []
    for label, a, b in moves:
        a2, b2 = av.S(a), av.S(b)
        u = (b2[0] - a2[0], b2[1] - a2[1])
        L = math.hypot(*u)
        if L < 4.0:
            raise LookupError("step %d: %s's move points at the viewer; pick another camera" % (n, label))
        tip = b2
        base = (tip[0] - u[0] / L * 5.0, tip[1] - u[1] / L * 5.0)
        sh.line(a2, base, W_MOVE)
        sh.arrow(tip, u, 5.0, 2.4)
        moved.append(dict(label=label, start=a2, tip=tip))
    sh.flush()
    # balloons on this step's parts, from drawgen's assembly mode; the label written inside each
    recs = assembly.place_balloons(sh, Assy, {"principal": av}, {"principal": assembly.Side()},
                                   items=[it for it, p in zip(items, parts) if p.step == n])
    balloons = []
    for r in recs:
        c = r["centre"]
        size = TEXT
        while sh.text_width(r["pn"], size) > 2 * assembly.B_R - 1.0 and size > 1.8:   # a 6-digit part number goes down to 1.8
            size -= 0.1
        sh.text(c[0], c[1], r["pn"], size, "center", valign="mid")
        p = next(q for q in parts if q.label == r["pn"])
        tbc = None
        if not p.cad:       # the note next to its balloon: below, above, then beside it, nearest first
            R = assembly.B_R
            spots = [(0.0, -R - 3.6, "center"), (0.0, R + 1.4, "center"), (R + 1.5, -1.25, "left"), (-R - 1.5, -1.25, "right")]
            spots += [(dx * k, dy * k, a) for k in (1.6, 2.2) for dx, dy, a in spots[:4]]
            for dx, dy, anchor in spots:
                x, y = c[0] + dx, c[1] + dy
                box = sh.text_box(x, y, TBC, TEXT, anchor)
                x += max(0.0, MARGIN[0] + 0.5 - box[0]) - max(0.0, box[2] - (sh.W - MARGIN[1] - 0.5))   # kept on the sheet
                box = sh.text_box(x, y, TBC, TEXT, anchor)
                if sh.is_free(box):
                    sh.text(x, y, TBC, TEXT, anchor)
                    tbc = (x, y)
                    break
        balloons.append(dict(label=r["pn"], centre=c, tip3d=r["tip3d"], end=r["end"], tbc=tbc))
    sh.flush()
    pdf = sh.doc.tobytes(garbage=3, deflate=True)
    png = Path(out_dir) / pack.step_image(n).name
    rec = dict(step=n, title=st["title"], new=[p.label for p in new], drawn=[p.label for p in parts], lifted=sorted(lift),
               no_cad=[p.label for p in parts if not p.cad], balloons=balloons, arrows=moved,
               hidden=sorted(hide & {p.label for p in parts_up_to(n)}))
    return pdf, png, rec


_MODEL = []


def model():
    """pack.py's model (the joints register's sizes and part numbers), read once."""
    if not _MODEL:
        _MODEL.append(pack.Model())
    return _MODEL[0]


def fixings_lines(st):
    """The step's fixings as the guide's step words them: the joints register's bolts and the other site fixings."""
    m = model()
    out = []
    for j, c in st["joints"].items():
        size = m.register.get(j, (0, "M6 x 16"))[1]
        out.append(pack.ux("%d x %s %s (%s)" % (c, m.pn.get(size, ""), size, j)).replace("  ", " "))
    for fx in pack.OTHER_FIXINGS:
        if fx["step"] == st["n"]:
            out.append(pack.ux(fx["text"]))
    return ["Fixings in this step: %s." % "; ".join(out)] if out else ["No fixings in this step."]


# ------------------------------------------------------------------ read-back

TIP_TOL = 0.05      # mm: a balloon's leader ends on its own part


def check_pdf(pdf, rec, parts):
    """Read the picture's PDF back: [faults]. Every balloon holds one of the step's labels and every new part has
    one; each leader ends on its own part (3D); every part with no CAD carries its CAD TO COME note."""
    faults = []
    doc = fitz.open("pdf", pdf)
    page = doc[0]
    sheet_h = page.rect.height / MM
    circles = [c for c in readback.pdf_circles(page, sheet_h) if abs(c[2] - assembly.B_R) < 0.05]
    texts = readback.text_boxes(page, sheet_h)
    found = []
    for cx, cy, r, _n in circles:
        inside = [t for t in texts if t[0] > cx - r and t[2] < cx + r and t[1] > cy - r and t[3] < cy + r]
        if len(inside) != 1:
            faults.append("a balloon at (%.0f, %.0f) holds %d texts" % (cx, cy, len(inside)))
            continue
        found.append(inside[0][4])
    want = sorted(rec["new"])
    if sorted(found) != want:
        faults.append("balloons %s, the step names %s" % (sorted(found), want))
    by = {p.label: p for p in parts}
    for b in rec["balloons"]:
        p = by[b["label"]]
        v = BRepBuilderAPI_MakeVertex(gp_Pnt(*b["tip3d"])).Vertex()
        d = BRepExtrema_DistShapeShape(v, p.shape)
        if not d.IsDone() or d.Value() > TIP_TOL:
            faults.append("%s's balloon ends %.2f mm off its part" % (b["label"], d.Value() if d.IsDone() else -1))
    tbc = [t for t in texts if t[4] == TBC]
    if len(tbc) != len([lb for lb in rec["new"] if lb in rec["no_cad"]]):
        faults.append("%d %s notes for %d new parts with no CAD" % (len(tbc), TBC, len([lb for lb in rec["new"] if lb in rec["no_cad"]])))
    return faults


def render(pdf, png):
    doc = fitz.open("pdf", pdf)
    pix = doc[0].get_pixmap(dpi=DPI, alpha=False)
    Path(png).parent.mkdir(parents=True, exist_ok=True)
    Path(png).write_bytes(pix.tobytes("png"))


def make(steps, out_dir, verbose=True):
    """Draw, read back and write each step's PNG; returns {step: record}; raises on a read-back fault."""
    recs = {}
    for n in steps:
        pdf, png, rec = draw_step(n, out_dir)
        lift = EXPLODE.get(n, {})
        faults = check_pdf(pdf, rec, [exploded(p, lift[p.label]) if p.step == n and p.label in lift else p for p in parts_up_to(n)])
        if faults:
            render(pdf, Path(out_dir) / ("FAILED-" + png.name))      # to see what went wrong; never the guide's name
            raise AssertionError("step %d: %s" % (n, "; ".join(faults)))
        render(pdf, png)
        recs[n] = rec
        if verbose:
            print("STEP %d: %s (%d parts, %d new, %d balloons, %d arrows%s)" % (
                n, png.name, len(rec["drawn"]), len(rec["new"]), len(rec["balloons"]), len(rec["arrows"]),
                ", no CAD yet: " + ", ".join(rec["no_cad"]) if rec["no_cad"] else ""))
    return recs


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--steps", help="a sample: these steps only (comma separated)")
    ap.add_argument("--out", default=str(IMG), help="where the PNGs go (default: the guide's img/)")
    ap.add_argument("--check", action="store_true", help="redraw in a scratch folder and compare with img/")
    a = ap.parse_args(argv)
    steps = [int(s) for s in a.steps.split(",")] if a.steps else picture_steps()
    unknown = [s for s in steps if s not in CAMERAS]
    if unknown:
        ap.error("no picture for step(s) %s; the steps with pictures are %s" % (unknown, picture_steps()))
    if a.check:
        with tempfile.TemporaryDirectory() as tmp:
            make(steps, tmp, verbose=False)
            bad = [pack.step_image(n).name for n in steps
                   if not (IMG / pack.step_image(n).name).exists()
                   or (IMG / pack.step_image(n).name).read_bytes() != (Path(tmp) / pack.step_image(n).name).read_bytes()]
        if bad:
            print("NOT CURRENT: %s (run step_drawings.py)" % ", ".join(bad))
            return 1
        print("OK: %d step pictures redraw byte for byte the same" % len(steps))
        return 0
    make(steps, a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
