"""Build AIR's two transitions outside Fusion: each part's STEP (mm, pod coordinates) and developed DXF, its fold table,
the two assembly STEPs with every copy placed, and a summary; then the checks.

    python build.py --out DIR [--dr DR.step --glass GLASS.step] [--summary FILE.json]
    python build.py --summary FILE.json --rows        (AIR's parts list rows for the two transitions)

Run with the drawing generator's OCC venv (~/.cache/spaceship-drawgen/venv-ocp7.8.1-mupdf1.27.2/bin/python).
File names use the part numbers in tr_params.NUMBERS once Control allocates them, the working keys until then.
Checks: each part is one valid solid whose volume is the one its definition gives; its flat, developed from the STEP
alone (check_flat.py), matches its DXF; no two pieces overlap, nor any piece and the fan box, its linings and
bulkhead and the riser (modelled from AIR's sizes); with --dr and --glass, every piece keeps 6 mm to DR's tubes and
the glass (clearance.py)."""

import argparse
import csv
import math
import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import check_flat  # noqa: E402
import clearance  # noqa: E402
import lower  # noqa: E402
import rivets as R  # noqa: E402
import sheetmetal as S  # noqa: E402
import upper  # noqa: E402
from tr_params import NUMBERS, P  # noqa: E402

REV = "P01"
# placed copies whose outer skin faces the duct's inside: the back cheek is the front one moved back (lower.py)
INSIDE_OUT = {("LT-C", 2)}


def pieces():
    """[(key, part, [translations of its copies])] and the assemblies' contents."""
    lw, rw, ch = lower.parts()
    sh, fl, vs = upper.parts()
    va, vb = vs[0], vs[len(vs) - 2]
    a_moves = [tuple(np.round(v.walls[v.name + " LEAD"].pts[1] - va.walls[va.name + " LEAD"].pts[1], 9))
               for v in vs if " VANE A" in v.name]
    b_moves = [tuple(np.round(v.walls[v.name + " LEAD"].pts[1] - vb.walls[vb.name + " LEAD"].pts[1], 9))
               for v in vs if " VANE B" in v.name]
    va.name = "AIR - SUPPLY TRANSITION - VANE - OVER THE BOX"
    vb.name = "AIR - SUPPLY TRANSITION - VANE - BESIDE THE BOX"
    L = lower.levels()
    return [("LT-L", lw, [(0, 0, 0)]), ("LT-R", rw, [(0, 0, 0)]), ("LT-C", ch, [(0, 0, 0), (0, L["cheek_shift"], 0)]),
            ("UT-S", sh, [(0, 0, 0)]), ("UT-F", fl, [(0, 0, 0)]), ("UT-VA", va, a_moves), ("UT-VB", vb, b_moves)]


def fname(key, kind, ext):
    num = NUMBERS.get(key)
    names = {"LT-L": "AIR-RISER-TRANSITION-LEFT-WRAPPER", "LT-R": "AIR-RISER-TRANSITION-RIGHT-WRAPPER",
             "LT-C": "AIR-RISER-TRANSITION-CHEEK", "UT-S": "AIR-SUPPLY-TRANSITION-SHELL",
             "UT-F": "AIR-SUPPLY-TRANSITION-FLOOR", "UT-VA": "AIR-SUPPLY-TRANSITION-VANE-OVER-THE-BOX",
             "UT-VB": "AIR-SUPPLY-TRANSITION-VANE-BESIDE-THE-BOX", "LT": "AIR-RISER-TRANSITION",
             "UT": "AIR-SUPPLY-TRANSITION"}
    return "%s_%s_%s_%s.%s" % (num or key, REV, names[key], kind, ext)


def moved(shape, v):
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    from OCP.gp import gp_Trsf, gp_Vec
    tr = gp_Trsf()
    tr.SetTranslation(gp_Vec(*map(float, v)))
    return BRepBuilderAPI_Transform(shape, tr, True).Shape()


def product_name(key, part):
    return "%s %s" % (NUMBERS.get(key) or key, part.name)


def build(out, dr=None, glass=None, summary_path=None):
    os.makedirs(out, exist_ok=True)
    summary = {"parts": {}, "faults": []}
    shapes = {}
    for key, part, copies in pieces():
        sh = part.solid()
        n, ok, vol, bb = S.solid_checks(sh)
        exp = part.expected_volume()
        if n != 1 or not ok or abs(vol - exp) > 1e-6 * max(1.0, exp):
            summary["faults"].append("%s: %d solids, valid %s, volume %.3f against %.3f" % (key, n, ok, vol, exp))
        shapes[key] = sh
        step = os.path.join(out, fname(key, "STEP", "step"))
        dxf = os.path.join(out, fname(key, "DXF", "dxf"))
        S.write_step([(product_name(key, part), sh)], step, part.name)
        loops = S.flat_outline(part.flat_regions())
        S.write_dxf(dxf, loops, part.flat_holes(), part.bend_lines(), part.flat_cutouts())
        with open(os.path.join(out, fname(key, "FOLDS", "csv")), "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["fold", "x0", "y0", "x1", "y1", "angle_deg", "inside_radius_mm", "direction_as_drawn",
                        "bend_allowance_mm", "k_factor", "thickness_mm"])
            for tag, c0, c1, ang, direction, ba, _ea, _eb in part.bend_lines():
                fold = next(f for f in part.folds if (f.tag or "") == tag)
                w.writerow([tag, "%.4f" % c0[0], "%.4f" % c0[1], "%.4f" % c1[0], "%.4f" % c1[1], "%.3f" % ang,
                            "%.2f" % fold.rin, direction, "%.4f" % ba, P.k_factor, part.t])
        xs = [p[0] for p in loops[0]]
        ys = [p[1] for p in loops[0]]
        faults, _dev = check_flat.check(step, dxf, P.k_factor, verbose=False)
        summary["faults"] += ["%s flat: %s" % (key, f) for f in faults]
        summary["parts"][key] = dict(number=NUMBERS.get(key), name=part.name, material=part.material, t=part.t,
                                     qty=len(copies), mass_kg=round(vol * 1e-9 * part.density, 4),
                                     flat=[round(max(xs) - min(xs), 2), round(max(ys) - min(ys), 2)],
                                     folds=len(part.folds), holes=len(part.flat_holes()),
                                     cutouts=len(part.flat_cutouts()), box=[round(v, 2) for v in bb],
                                     copies=[list(map(float, c)) for c in copies], flat_check="PASS" if not faults
                                     else "FAIL")
    # assemblies: every copy placed
    placed = []
    for key, part, copies in pieces():
        for i, c in enumerate(copies):
            placed.append((key, "%s %d" % (product_name(key, part), i + 1), moved(shapes[key], c)))
    for akey, title in (("LT", "AIR - RISER TRANSITION"), ("UT", "AIR - SUPPLY TRANSITION")):
        S.write_step([(nm, sh) for k, nm, sh in placed if k.startswith(akey + "-")],
                     os.path.join(out, fname(akey, "STEP", "step")), title)
    # the rivets: every hole's mate and stack, and each set rivet's head and tail (for the checks only)
    sts, rfaults = R.stacks(pieces(), inside_out=INSIDE_OUT)
    summary["faults"] += rfaults
    summary["rivets"] = [dict(stack=d, grip_mm=g, rivet=rv_, count=n,
                              duct=("LT" if "steel" in d.split(" + ")[0] else "UT"))
                         for (d, g, rv_), n in sorted(R.table(sts).items())]
    rv = R.solids(sts)
    summary["overlaps"] = overlaps([(nm, sh) for _k, nm, sh in placed] + rv)
    summary["faults"] += ["overlap: %s" % o for o in summary["overlaps"]]
    summary["slips"] = slips([(nm, sh) for k, nm, sh in placed if k.startswith("LT-")])
    # the collars slip 0.5 inside the riser and the box; the right wrapper's slant passes 0.42 under the box's right
    # wall's bottom edge (0.5 across, at its 32 degrees)
    summary["faults"] += ["%s is %.3f: the collar's slip is 0.5" % (k, v) for k, v in summary["slips"].items()
                          if v < 0.4]
    if dr and glass:
        import tempfile
        tmp = tempfile.mkdtemp(prefix="airtr-rivets-")
        rpath = os.path.join(tmp, "RIVETS.step")
        S.write_step(rv, rpath, "AIR TRANSITIONS - SET RIVETS (check only)")
        rows = clearance.distances(dr, glass, [os.path.join(out, fname(k, "STEP", "step")) for k in ("LT", "UT")]
                                   + [rpath], near=30.0)
        near, skin = {}, {}
        for pname, oname, kind, v, a, _b in rows:
            store = near if kind in ("tube", "glass") else (skin if kind == "skin" else None)
            if store is not None and (pname not in store or v < store[pname][0]):
                store[pname] = (round(v, 2), oname[:60], [round(x, 1) for x in a])
        for store, rule in ((near, clearance.RULE), (skin, clearance.SKIN_RULE)):
            summary["faults"] += ["%s is %.2f mm from %s" % (p, v[0], v[1]) for p, v in store.items()
                                  if v[0] < rule - 1e-6]
        for store in (near, skin):
            rv = {k: v for k, v in store.items() if k.startswith("RIVET")}
            for k in rv:
                del store[k]
            if rv:
                k = min(rv, key=lambda q: rv[q][0])
                store["the nearest set rivet (%s)" % k] = rv[k]
        summary["clearance"] = near
        summary["skin"] = skin
        summary["faults"] += ["%s is %.2f mm from %s" % (p, v[0], v[1]) for p, v in near.items()
                              if v[0] < clearance.RULE and not p.startswith("the nearest set rivet")]
    if summary_path:
        with open(summary_path, "w") as fh:
            json.dump(summary, fh, indent=1, default=str)
    return summary


# AIR's parts list rows for the two transitions (CEILING owns the list; these rows are this folder's, in place of the
# HOLD rows 618102 and 618103 under 610401): (key, Vietnamese name, kind, parent key, per parent, source)
LIST_ROWS = [
    ("LT", "Ống chuyển hút (cụm)", "HS", None, 1,
     "the Lead's rulings 2026-11-01: the shop build (two wrappers and two cheeks), the riser kink rounded (R 100) "
     "and the riser's top cut to Z 1386 (its walls 19.9 degrees apart); in place of 618103"),
    ("LT-L", "Ống chuyển hút - vách bao trái", "MP", "LT", 1, "the Lead's rulings 2026-11-01; transitions/lower.py"),
    ("LT-R", "Ống chuyển hút - vách bao phải", "MP", "LT", 1, "the Lead's rulings 2026-11-01; transitions/lower.py"),
    ("LT-C", "Ống chuyển hút - tấm má (trước và sau)", "MP", "LT", 2,
     "the Lead's rulings 2026-11-01; transitions/lower.py: one part, front and back"),
    ("UT", "Ống chuyển cấp (cụm)", "HS", None, 1,
     "the Lead's rulings 2026-11-01: the shop build (a shell and a floor) with turning vanes, the box at X 680, the "
     "right wall to X 1158 and DR's opening X 961 to 1146, Z 1895 to 2102; in place of 618102"),
    ("UT-S", "Ống chuyển cấp - vỏ", "MP", "UT", 1, "the Lead's rulings 2026-11-01; transitions/upper.py"),
    ("UT-F", "Ống chuyển cấp - tấm đáy", "MP", "UT", 1, "the Lead's rulings 2026-11-01; transitions/upper.py"),
    ("UT-VA", "Ống chuyển cấp - cánh hướng gió trên hộp quạt", "MP", "UT", 3,
     "the air report's turning vanes (calc.py VANE_K); transitions/upper.py"),
    ("UT-VB", "Ống chuyển cấp - cánh hướng gió cạnh hộp quạt", "MP", "UT", 2,
     "the air report's turning vanes (calc.py VANE_K); transitions/upper.py"),
]
ASSY_NAMES = {"LT": "AIR - RISER TRANSITION", "UT": "AIR - SUPPLY TRANSITION"}


def min_rect(loop):
    """The least-area rectangle round a flat's outline: (long side, short side)."""
    pts = np.array(loop, float)
    best = None
    n = len(pts)
    for i in range(n):
        d = pts[(i + 1) % n] - pts[i]
        if np.linalg.norm(d) < 1e-9:
            continue
        u = d / np.linalg.norm(d)
        v = np.array([-u[1], u[0]])
        a, b = pts @ u, pts @ v
        w, h = a.max() - a.min(), b.max() - b.min()
        if best is None or w * h < best[0] * best[1]:
            best = (w, h)
    return tuple(sorted(best, reverse=True))


def list_rows(summary, supply_box="610401"):
    """The parts list rows (CSV lines, the list's columns) from a build's summary (masses, holes, folds, boxes) and
    the parts themselves (fold radii, the flat's least rectangle)."""
    import io
    parts = summary["parts"]
    built = {k: p for k, p, _c in pieces()}
    rivets = {d: sum(r["count"] for r in summary.get("rivets", []) if r["duct"] == d) for d in ("LT", "UT")}
    out = io.StringIO()
    w = csv.writer(out, lineterminator="\n")
    for key, vi, kind, parent, per, source in LIST_ROWS:
        num = NUMBERS[key]
        if kind == "HS":
            kids = [(k, p) for k, p in parts.items() if k.startswith(key + "-")]
            mass = sum(p["mass_kg"] * p["qty"] for _k, p in kids)
            w.writerow([num, ASSY_NAMES[key], vi, "HS", supply_box, 1, 1, "", "", "", "", "", "", "", "",
                        "%.3f" % mass, "calculation (sum of its parts)", REV, "DRAFT",
                        source + "; riveted (%d closed-end blind rivets, the Joints register's) and sealed (sealant "
                        "HOLD)" % rivets[key]])
            continue
        p = parts[key]
        steel = "steel" in p["material"].lower()
        bb = p["box"]
        size = sorted([bb[3] - bb[0], bb[4] - bb[1], bb[5] - bb[2]], reverse=True)
        mat = "Galvanised steel DX51D+Z" if steel else "Aluminium 5052-H32 sheet (alloy HOLD)"
        fin = "galvanised" if steel else "mill finish (hidden, D-79)"
        part = built[key]
        radii = sorted({round(f.rin, 2) for f in part.folds})
        r_txt = " and ".join("R %g" % r for r in radii)
        holes = "%d hole%s" % (p["holes"], "" if p["holes"] == 1 else "s")
        proc = ("sheet metal: laser cut (%s%s), %d folds at %s, K %s (its DXF and fold table)"
                % (holes, ", %d cut-out" % p["cutouts"] if p["cutouts"] else "", p["folds"], r_txt, P.k_factor))
        fw, fh = min_rect(S.flat_outline(part.flat_regions())[0])
        size_s = "%.1f x %.1f x %.1f, %.1f sheet; flat %.1f x %.1f" % (size[0], size[1], size[2], p["t"], fw, fh)
        w.writerow([NUMBERS[key], p["name"], vi, "MP", NUMBERS[parent], per, per, mat, fin, proc, "", "", "", size_s,
                    "ISO 2768-m; its drawing to come (the generator's folds along any line, #369)",
                    "%.3f" % p["mass_kg"], "calculation (CAD geometry x density, transitions/build.py)", REV, "DRAFT",
                    source])
    return out.getvalue()


def riser_solid(z0=252.0):
    """The intake riser as AIR's sizes and the Lead's rulings give it: 1 mm walls, its top at Z 1386, its front-right
    upright edge chamfered 8 x 8 (the wall folded round it, so the inside is chamfered too)."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
    from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
    from OCP.gp import gp_Pnt, gp_Vec

    def prism(off):
        x0, x1, y0, y1, c = P.rs_x0 + off, P.rs_x1 - off, P.rs_y0 + off, P.rs_y1 - off, P.riser_chamfer
        # the chamfer's inside face stays parallel to the outside one, off the wall's thickness
        c_in = c - 2 * off * (math.sqrt(2) - 1) if off else c
        pts = [(x0, y0), (x1 - c_in, y0), (x1, y0 + c_in), (x1, y1), (x0, y1)]
        poly = BRepBuilderAPI_MakePolygon()
        for x, y in pts:
            poly.Add(gp_Pnt(x, y, z0 - (1.0 if off else 0.0)))
        poly.Close()
        face = BRepBuilderAPI_MakeFace(poly.Wire()).Face()
        return BRepPrimAPI_MakePrism(face, gp_Vec(0, 0, P.rs_z1 - z0 + (2.0 if off else 0.0))).Shape()
    return BRepAlgoAPI_Cut(prism(0.0), prism(P.rs_t)).Shape()


def slips(named):
    """Each lower piece's least distance to the riser's and the fan box's walls (the collars' slip: 0.5 by design)."""
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
    from OCP.gp import gp_Pnt
    box = BRepAlgoAPI_Cut(BRepPrimAPI_MakeBox(gp_Pnt(P.sb_x0, P.sb_y0, P.sb_z0), gp_Pnt(P.sb_x1, P.sb_y1, P.sb_z0 + P.sb_h)).Shape(),
                          BRepPrimAPI_MakeBox(gp_Pnt(P.sb_x0 + P.sb_t, P.sb_y0 + P.sb_t, P.sb_z0 - 1),
                                              gp_Pnt(P.sb_x1 - P.sb_t, P.sb_y1 - P.sb_t, P.sb_z0 + P.sb_h + 1)).Shape()).Shape()
    out = {}
    for nm, sh in named:
        for other, o in (("riser", riser_solid()), ("fan box", box)):
            d = BRepExtrema_DistShapeShape(sh, o)
            d.Perform()
            out["%s to the %s" % (nm, other)] = round(d.Value(), 3)
    return out


def overlaps(named):
    """Pairs of pieces (and set rivets), or a piece and the fan box, its linings and bulkhead or the riser, sharing
    more than 0.001 mm3 (the box and riser modelled from AIR's sizes); pairs whose bounding boxes don't meet are
    skipped."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut
    from OCP.BRepGProp import BRepGProp
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
    from OCP.GProp import GProp_GProps
    from OCP.gp import gp_Pnt

    def vol(sh):
        g = GProp_GProps()
        BRepGProp.VolumeProperties_s(sh, g)
        return g.Mass()

    def box(x0, x1, y0, y1, z0, z1):
        return BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, z0), gp_Pnt(x1, y1, z1)).Shape()

    def tube(x0, x1, y0, y1, z0, z1, t):
        return BRepAlgoAPI_Cut(box(x0, x1, y0, y1, z0, z1), box(x0 + t, x1 - t, y0 + t, y1 - t, z0 - 1, z1 + 1)).Shape()
    lin = P.sb_lin_t
    riser = riser_solid()
    others = [("FAN BOX", tube(P.sb_x0, P.sb_x1, P.sb_y0, P.sb_y1, P.sb_z0, P.sb_z0 + P.sb_h, P.sb_t)),
              ("FAN BOX LINING LEFT", box(P.sb_x0 + P.sb_t, P.sb_x0 + P.sb_t + lin, P.sb_y0 + P.sb_t, P.sb_y1 - P.sb_t,
                                          1795, P.sb_z0 + P.sb_h)),
              ("FAN BOX LINING RIGHT", box(P.sb_x1 - P.sb_t - lin, P.sb_x1 - P.sb_t, P.sb_y0 + P.sb_t, P.sb_y1 - P.sb_t,
                                           1795, P.sb_z0 + P.sb_h)),
              ("FAN BOX BULKHEAD", box(P.sb_x0 + P.sb_t, P.sb_x1 - P.sb_t, P.sb_y0 + P.sb_t, P.sb_y1 - P.sb_t, 1698, 1700)),
              ("RISER", riser)]
    out = []
    boxes = {}
    for nm, sh in named + others:
        boxes[nm] = clearance._box(sh)
    for (a, sa), (b, sb) in itertools.combinations(named + others, 2):
        if a in dict(others) and b in dict(others):
            continue
        if boxes[a].IsOut(boxes[b]):
            continue
        c = BRepAlgoAPI_Common(sa, sb)
        c.Build()
        v = vol(c.Shape())
        if v > 1e-3:
            out.append("%s and %s share %.3f mm3" % (a, b, v))
    return out


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out")
    ap.add_argument("--dr")
    ap.add_argument("--glass")
    ap.add_argument("--summary", help="write the build's summary (JSON) here, outside the parts' folder")
    ap.add_argument("--rows", action="store_true", help="print AIR's parts list rows from --summary and stop")
    a = ap.parse_args(argv)
    if a.rows:
        with open(a.summary) as fh:
            print(list_rows(json.load(fh)), end="")
        return 0
    s = build(a.out, a.dr, a.glass, a.summary)
    for k, p in s["parts"].items():
        print("%-6s %-48s x%d  %.3f kg  flat %s  folds %d  holes %d  %s" % (
            k, p["name"][:48], p["qty"], p["mass_kg"], p["flat"], p["folds"], p["holes"], p["flat_check"]))
    for r in s.get("rivets", []):
        print("rivets %s x%d  grip %.1f  %s: %s" % (r["duct"], r["count"], r["grip_mm"], r["stack"], r["rivet"]))
    for p, v in (s.get("clearance") or {}).items():
        print("nearest DR tube or glass to %s: %.2f mm (%s)" % (p[:60], v[0], v[1]))
    for p, v in (s.get("skin") or {}).items():
        print("DR's skin to %s: %.2f mm" % (p[:60], v[0]))
    print("overlaps: %d" % len(s["overlaps"]))
    print("collar slips: least %.3f mm (%s)" % min((v, k) for k, v in s["slips"].items()))
    print("PASS" if not s["faults"] else "FAIL:\n  " + "\n  ".join(s["faults"]))
    return 1 if s["faults"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
