"""The transitions' clearance to FRONT's DR: the least distance from each piece to every DR tube, the glass and its
U-profile, and to DR's other parts (skin, panels, seals) for the record. The brief's rule: at least 6 mm to every
DR tube and glass face (the Lead's brief, 2026-11-01).

Usage: python clearance.py DR.step GLASS.step PIECE.step [PIECE.step ...]
FRONT's reserved air spaces in DR's STEP are left out (they are the spaces these parts fill)."""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
# the generator goes last on the path, so its modules (its own sheetmetal.py among them) never shadow this folder's
sys.path.append(os.path.join(REPO, "tools", "drawgen"))

import geom  # noqa: E402  (the drawing generator's STEP reader, read only: product names and solids)
from OCP.BRepExtrema import BRepExtrema_DistShapeShape  # noqa: E402

RULE = 6.0
SKIN_RULE = 4.0                 # the Lead's 4 mm rule to DR's skin (2026-11-01: closer risks a rattle)
TUBE_PREFIX = ("352",)          # DR's frame tubes (351306's members)
GLASS = ("361003", "368004", "368002", "368003")    # the fixed glass, its U-profile and seals
SKIN = ("351301",)              # DR's skin
RULES = {"tube": RULE, "glass": RULE, "skin": SKIN_RULE}


def kind(name):
    pn = name[:6]
    if pn.startswith(TUBE_PREFIX):
        return "tube"
    if pn in GLASS:
        return "glass"
    if pn in SKIN:
        return "skin"
    return "other"


def _box(shape):
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib
    bb = Bnd_Box()
    BRepBndLib.Add_s(shape, bb)
    return bb


def distances(dr_path, glass_path, pieces, near=None):
    """[(piece, other, kind, distance, point on the piece, point on the other)] for every piece solid and every DR
    and glass solid; with near, only the pairs whose bounding boxes come within near mm (the others are further)."""
    others = []
    for path in (dr_path, glass_path):
        for name, solids in geom.read_step(path):
            if "RESERVED" in name.upper():
                continue
            for s in solids:
                others.append((name, s, _box(s)))
    rows = []
    for ppath in pieces:
        for pname, psolids in geom.read_step(ppath):
            for ps in psolids:
                pb = _box(ps)
                for oname, os_, ob in others:
                    if near is not None and pb.Distance(ob) > near:
                        continue
                    d = BRepExtrema_DistShapeShape(ps, os_)
                    d.Perform()
                    if not d.IsDone():
                        raise RuntimeError("distance failed: %s to %s" % (pname, oname))
                    p, q = d.PointOnShape1(1), d.PointOnShape2(1)
                    rows.append((pname, oname, kind(oname), d.Value(), (p.X(), p.Y(), p.Z()), (q.X(), q.Y(), q.Z())))
    return rows


def main(argv):
    dr, gl, pieces = argv[0], argv[1], argv[2:]
    rows = distances(dr, gl, pieces)
    bad = 0
    for pname in sorted({r[0] for r in rows}):
        mine = sorted([r for r in rows if r[0] == pname], key=lambda r: r[3])
        print(pname)
        for _p, oname, k, v, a, b in mine[:8]:
            flag = "BELOW %g" % RULES[k] if k in RULES and v < RULES[k] - 1e-6 else ""
            bad += bool(flag)
            print("   %7.2f  %-5s %-58s at (%.1f, %.1f, %.1f) %s" % (v, k, oname[:58], a[0], a[1], a[2], flag))
        tubes = [r for r in mine if r[2] in ("tube", "glass")]
        if tubes:
            print("   nearest tube or glass: %.2f mm (%s)" % (tubes[0][3], tubes[0][1][:50]))
    print("PASS" if not bad else "FAIL: %d below the rule (6 mm to tubes and glass, 4 to the skin)" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
