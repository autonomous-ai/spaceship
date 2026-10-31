"""The three sheet-metal parts ELECTRICAL makes, each in its own design (so its
drawing shows only that part):

    711001 ELECTRICAL - POWER UNIT - ENCLOSURE BODY   (1.0 mm 5052-H32, folded tray with front lips)
    711002 ELECTRICAL - POWER UNIT - FRONT PLATE      (1.5 mm 5052-H32, flat, black anodised AA20)
    711005 ELECTRICAL - HUB ZONE COVER PLATE          (1.5 mm 5052-H32, flat, black anodised AA20)

    python3 tools/fusion/run_script.py v2/01-CAD-Native/electrical/electrical_parts_cad.py \
        --label "ELECTRICAL Engineer" --arg parts=front,hub,body --arg export=1

One run builds all three, the flat plates first (fair-share queue rule). Each part opens its design
from Default Project / FocusPod v2, or makes it the way the PM set while the runner's --doc-new is
paused (2026-11-01): the script lists the folder first and makes nothing if any entry can't be read
(that entry could be this very design); a new design gets a name never used before and is saved
there at once, empty. Then the part is built, checked, saved, exported and closed. A part that
fails doesn't stop the others; the run fails at the end and names it.

Sizes come from the route model's parameters (electrical_model.py: pu_w, pu_h,
pu_d, hub_w) and are written here as this part's own user parameters with
their status. Cut-outs that wait on module data are HOLD (PM ruling
2026-11-01): the 86-plate openings (UTEN codes, H-ELE-04), the hub window and
the button and knob holes (the hub's size, ISS-060), the earth stud hole
(PEM data) and the mounting to B2's frame (WALL, IF-12, not cut yet). Every
sketch is fully constrained by the parameters; every feature is named.

Exports after the save: the .f3d, the STEP (Fusion writes cm, D-13) and a DXF in mm: the body's
flat pattern (Fusion's export), the plates' outline sketch written by flat_dxf.py with every line
and circle on the CUT layer only (D-89 part 4).
"""

import importlib
import os
import sys
import time

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
HERE = os.path.dirname(os.path.abspath(ARGS.get("script_path", globals().get("__file__", "."))))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import electrical_model as M  # noqa: E402
import flat_dxf  # noqa: E402

importlib.reload(M)
importlib.reload(flat_dxf)
FOLDER = "FocusPod v2"
MM = 0.1
V = M.values()
HOLD = "HOLD"

# part key: part number, name, Vietnamese, doc name stem, parameters (name, expression, unit, status, source)
PARTS = {
    "body": ("711001", "ELECTRICAL - POWER UNIT - ENCLOSURE BODY", "Điện - hộp nguồn - thân hộp",
             "711001_P01_ELECTRICAL-POWER-UNIT-ENCLOSURE-BODY", [
                 ("t", "1.0 mm", "mm", "PROPOSED", "5052-H32 aluminium 1.0 mm (README section 3)"),
                 ("w", "%.1f mm" % V["pu_w"], "mm", "assumption", "route model pu_w (300)"),
                 ("h", "%.1f mm" % V["pu_h"], "mm", "assumption", "route model pu_h (260)"),
                 ("d", "%.1f mm" % V["pu_d"], "mm", "calculation", "route model pu_d (72): felt face to 6 mm short of the skin"),
                 ("lip", "22 mm", "mm", "assumption", "front lips that carry the front plate's 4 M4 screws and clinch nuts: 22 mm keeps each hole (Ø5.4 here, Ø4.5 in the plate) 2 diameters from the edge (mechanical check C09)"),
                 ("hole_b", "19.1 mm", "mm", "source", "Heyco 2836 bushing hole (maker page, 2026-10-31)"),
                 ("lead_z1", "%.1f mm" % (V["trunk_z"] - 30 - V["pu_z0"]), "mm", "calculation",
                  "first lead exit up the right side from the bottom: Z 1070 (trunk Z 1100 less 30) less the unit's bottom Z 870"),
                 ("lead_z2", "%.1f mm" % (V["trunk_z"] + 10 - V["pu_z0"]), "mm", "calculation",
                  "second lead exit: Z 1110, 10 mm clear of the top bend"),
                 ("lead_y", "%.1f mm" % (V["y_bg"] - V["y_bf"]), "mm", "calculation",
                  "lead exits in the cassette's cable gap: 21.5 mm behind the unit's front"),
                 ("top_x", "%.1f mm" % (V["lt_x"] - V["pu_x0"]), "mm", "calculation", "light feed exit in the top: X 355 less the unit's left side X 95"),
                 ("sleeve_x", "%.1f mm" % (V["sl_x"] - V["pu_x0"]), "mm", "calculation", "mains and LAN sleeve entry in the bottom: X 146 less 95"),
                 ("sleeve_d", "25 mm", "mm", "assumption", "entry for the 20 mm flexible conduit"),
                 ("sleeve_y", "%.1f mm" % (V["sl_y"] - V["y_bf"]), "mm", "calculation", "sleeve centre 58 mm behind the unit's front"),
                 ("clinch_d", "5.4 mm", "mm", HOLD, "M4 clinch nut hole in each lip; nut and hole to confirm (H-ELE-11 family)"),
                 ("clinch_x", "30 mm", "mm", "assumption", "clinch nut centre from each side edge, along the top and bottom lips: 2 diameters clear of the lips' mitred corners (C09)"),
                 ("clinch_y", "lip / 2", "mm", "calculation", "clinch nut centre in the middle of the lip"),
             ]),
    "front": ("711002", "ELECTRICAL - POWER UNIT - FRONT PLATE", "Điện - hộp nguồn - mặt trước",
              "711002_P01_ELECTRICAL-POWER-UNIT-FRONT-PLATE", [
                  ("t", "1.5 mm", "mm", "PROPOSED", "5052-H32 aluminium 1.5 mm, black anodised AA20 (D-67)"),
                  ("w", "%.1f mm" % V["pu_w"], "mm", "assumption", "route model pu_w (300)"),
                  ("h", "%.1f mm" % V["pu_h"], "mm", "assumption", "route model pu_h (260)"),
                  ("box_a", "73 mm", "mm", HOLD, "opening for an 86-type back box mouth; the UTEN code and its box set it (H-ELE-04)"),
                  ("box_zc", "195 mm", "mm", "assumption", "86-plate openings' centre height from the plate's bottom (unit centre Z 1000 + 65)"),
                  ("box_x1", "80 mm", "mm", "assumption", "socket opening centre from the left edge"),
                  ("box_x2", "190 mm", "mm", "assumption", "LAN opening centre from the left edge"),
                  ("din_w", "37 mm", "mm", "source", "RCBO window: 2 modules of 18 mm + 1 (Schneider A9D32610 is 36 mm wide)"),
                  ("din_h", "45 mm", "mm", "source", "DIN 43880 front height 45 mm"),
                  ("din_x", "265 mm", "mm", "assumption", "RCBO window centre from the left edge"),
                  ("din_zc", "195 mm", "mm", "assumption", "RCBO window centre height, level with the plates"),
                  ("vent_l", "40 mm", "mm", "assumption", "vent slot length"),
                  ("vent_w", "4 mm", "mm", "assumption", "vent slot width"),
                  ("vent_n", "5", "", "assumption", "vent slots per row (two rows: bottom and top)"),
                  ("vent_p", "50 mm", "mm", "assumption", "vent slot pitch"),
                  ("vent_z1", "25 mm", "mm", "assumption", "bottom vent row centre from the bottom edge"),
                  ("vent_z2", "130 mm", "mm", "assumption", "top vent row centre (between the supplies and the plates)"),
                  ("screw_d", "4.5 mm", "mm", "assumption", "M4 screw clearance hole"),
                  ("screw_x", "30 mm", "mm", "calculation", "screw centre from each side edge, along the width: on the body's clinch nuts (clinch_x)"),
                  ("screw_y", "11 mm", "mm", "calculation", "screw centre from the top and bottom edges: the middle of the body's 22 mm lips (2.4 diameters from the edge, C09)"),
              ]),
    "hub": ("711005", "ELECTRICAL - HUB ZONE COVER PLATE", "Điện - mặt che vùng cảm biến",
            "711005_P01_ELECTRICAL-HUB-ZONE-COVER-PLATE", [
                ("t", "1.5 mm", "mm", "PROPOSED", "5052-H32 aluminium 1.5 mm, black anodised AA20 (D-67)"),
                ("w", "%.1f mm" % V["hub_w"], "mm", "DECIDED", "D-61, D-70: the 180 x 180 zone"),
                ("h", "%.1f mm" % V["hub_w"], "mm", "DECIDED", "D-61, D-70"),
                ("win_w", "120 mm", "mm", HOLD, "hub window width: the hub's size (ISS-060)"),
                ("win_h", "70 mm", "mm", HOLD, "hub window height (ISS-060)"),
                ("win_zc", "125 mm", "mm", "assumption", "hub window centre from the bottom edge"),
                ("btn_d", "16.2 mm", "mm", HOLD, "16 mm panel push button hole (button SKU HOLD)"),
                ("btn_p", "40 mm", "mm", "assumption", "button pitch (BOOST, TEST, CALL)"),
                ("btn_zc", "50 mm", "mm", "assumption", "button row centre from the bottom edge"),
                ("btn_x1", "35 mm", "mm", "assumption", "first button centre from the left edge: at least 2 diameters (32.4) from the edge (C09)"),
                ("knob_d", "7.5 mm", "mm", HOLD, "potentiometer bush hole (part HOLD)"),
                ("knob_x", "150 mm", "mm", "assumption", "LIGHT knob centre from the left edge"),
                ("screw_d", "4.5 mm", "mm", HOLD, "M4 fixing holes into the column (CEILING models the column)"),
                ("screw_e", "10 mm", "mm", "assumption", "fixing hole centre from each corner"),
            ]),
}


def vi(e):
    return adsk.core.ValueInput.createByString(e)


def ev(design: "adsk.fusion.Design", e):
    return design.unitsManager.evaluateExpression(e, "mm") * 10.0


def box(b: "adsk.fusion.BRepBody"):
    bb = b.boundingBox
    return [round(x * 10.0, 3) for x in (bb.minPoint.x, bb.minPoint.y, bb.minPoint.z, bb.maxPoint.x, bb.maxPoint.y, bb.maxPoint.z)]


H = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
VO = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation


def rect(sk: "adsk.fusion.Sketch", design: "adsk.fusion.Design", x0, y0, x1, y1, name):
    """Rectangle (sketch coordinates in mm expressions), dimensioned to the sketch origin."""
    a, b, c, d = (ev(design, e) for e in (x0, y0, x1, y1))
    r = sk.sketchCurves.sketchLines.addTwoPointRectangle(adsk.core.Point3D.create(a * MM, b * MM, 0),
                                                         adsk.core.Point3D.create(c * MM, d * MM, 0))
    gc = sk.geometricConstraints
    for ln in r:
        if not any(k.objectType in (adsk.fusion.HorizontalConstraint.classType(), adsk.fusion.VerticalConstraint.classType())
                   for k in ln.geometricConstraints):
            s0, s1 = ln.startSketchPoint.geometry, ln.endSketchPoint.geometry
            (gc.addHorizontal if abs(s0.y - s1.y) < 1e-9 else gc.addVertical)(ln)
    pts = []
    for ln in r:
        for p in (ln.startSketchPoint, ln.endSketchPoint):
            if all(p != q for q in pts):
                pts.append(p)
    near = lambda x, y: min(pts, key=lambda p: (p.geometry.x - x * MM) ** 2 + (p.geometry.y - y * MM) ** 2)  # noqa: E731
    p00, p10, p01 = near(a, b), near(c, b), near(a, d)
    tp = adsk.core.Point3D.create((a + c) / 2 * MM, (b + d) / 2 * MM, 0)
    dims = sk.sketchDimensions
    dims.addDistanceDimension(p00, p10, H, tp).parameter.expression = "(%s) - (%s)" % (x1, x0)
    dims.addDistanceDimension(p00, p01, VO, tp).parameter.expression = "(%s) - (%s)" % (y1, y0)
    for val, ex, orient, coinc in ((a, x0, H, gc.addVerticalPoints), (b, y0, VO, gc.addHorizontalPoints)):
        if abs(val) < 1e-9:
            coinc(p00, sk.originPoint)
        else:
            dims.addDistanceDimension(sk.originPoint, p00, orient, tp).parameter.expression = "abs(%s)" % ex
    return r


def circle(sk: "adsk.fusion.Sketch", design: "adsk.fusion.Design", cx, cy, d):
    x, y = ev(design, cx), ev(design, cy)
    c = sk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(x * MM, y * MM, 0), ev(design, d) / 2 * MM)
    g = c.centerSketchPoint.geometry
    tp = adsk.core.Point3D.create(g.x + 0.8, g.y + 0.8, 0)
    sk.sketchDimensions.addDiameterDimension(c, tp).parameter.expression = d
    for val, ex, orient, coinc in ((x, cx, H, sk.geometricConstraints.addVerticalPoints),
                                   (y, cy, VO, sk.geometricConstraints.addHorizontalPoints)):
        if abs(val) < 1e-9:
            coinc(c.centerSketchPoint, sk.originPoint)
        else:
            sk.sketchDimensions.addDistanceDimension(sk.originPoint, c.centerSketchPoint, orient, tp).parameter.expression = "abs(%s)" % ex
    return c


def flat_plate(design: "adsk.fusion.Design", comp: "adsk.fusion.Component", key):
    """A flat plate in the XZ plane (X along the width, Z up), thickness along -Y... built on XY for simplicity:
    X = width, Y = height, extruded t along +Z. The drawing's front view looks at it."""
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "OUTLINE AND CUT-OUTS - %s" % key.upper()
    rect(sk, design, "0 mm", "0 mm", "w", "h", "OUTLINE")
    if key == "front":
        for xc in ("box_x1", "box_x2"):
            rect(sk, design, "(%s) - box_a / 2" % xc, "box_zc - box_a / 2", "(%s) + box_a / 2" % xc, "box_zc + box_a / 2",
                 "86 PLATE OPENING (HOLD)")
        rect(sk, design, "din_x - din_w / 2", "din_zc - din_h / 2", "din_x + din_w / 2", "din_zc + din_h / 2", "RCBO WINDOW")
        for zc in ("vent_z1", "vent_z2"):
            for i in range(5):
                xc = "w / 2 + (%d - (vent_n - 1) / 2) * vent_p" % i
                rect(sk, design, "(%s) - vent_l / 2" % xc, "(%s) - vent_w / 2" % zc, "(%s) + vent_l / 2" % xc,
                     "(%s) + vent_w / 2" % zc, "VENT")
        for cx, cy in (("screw_x", "screw_y"), ("w - screw_x", "screw_y"), ("screw_x", "h - screw_y"), ("w - screw_x", "h - screw_y")):
            circle(sk, design, cx, cy, "screw_d")
    else:
        rect(sk, design, "w / 2 - win_w / 2", "win_zc - win_h / 2", "w / 2 + win_w / 2", "win_zc + win_h / 2", "HUB WINDOW (HOLD)")
        for i in range(3):
            circle(sk, design, "btn_x1 + %d * btn_p" % i, "btn_zc", "btn_d")
        circle(sk, design, "knob_x", "btn_zc", "knob_d")
        for cx, cy in (("screw_e", "screw_e"), ("w - screw_e", "screw_e"), ("screw_e", "h - screw_e"), ("w - screw_e", "h - screw_e")):
            circle(sk, design, cx, cy, "screw_d")
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: " + sk.name)
    # the plate is the profile with the most area that contains holes: pick the outer region
    outer = max((sk.profiles.item(i) for i in range(sk.profiles.count)),
                key=lambda p: p.areaProperties(adsk.fusion.CalculationAccuracy.MediumCalculationAccuracy).area)
    ei = comp.features.extrudeFeatures.createInput(outer, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ei.setDistanceExtent(False, vi("t"))
    f = comp.features.extrudeFeatures.add(ei)
    f.name = "EXTRUDE - PLATE %s" % key.upper()
    b = f.bodies.item(0)
    b.name = PARTS[key][1]
    return b, sk


def body_tray(design: "adsk.fusion.Design", comp: "adsk.fusion.Component", occ: "adsk.fusion.Occurrence"):
    """Folded tray: base (the back, w x h on XY at Z 0), four returns of depth d (outer faces on the outline,
    toward +Z = toward the room), four lips of `lip` turned inward at the front."""
    rule = design.designSheetMetalRules.itemByName("AL 5052 1.0 - POWER UNIT")
    if rule is None:
        rule = design.designSheetMetalRules.addByCopy(comp.activeSheetMetalRule, "AL 5052 1.0 - POWER UNIT")
    rule.thickness.expression = "%.4f mm" % ev(design, "t")
    rule.bendRadius.expression = "Thickness"
    rule.kFactor = 0.44
    rule.twoBendReliefShape = adsk.fusion.TwoBendReliefShapes.SquareTwoBendReliefShape
    comp.activeSheetMetalRule = rule
    occ.activate()
    try:
        sk = comp.sketches.add(comp.xYConstructionPlane)
        sk.name = "OUTLINE - BACK"
        rect(sk, design, "0 mm", "0 mm", "w", "h", "OUTLINE")
        if not sk.isFullyConstrained:
            raise RuntimeError("sketch not fully constrained: " + sk.name)
        ff = comp.features.flangeFeatures
        bfi = ff.createBaseFlangeInput([sk.profiles.item(0)])
        bfi.orientation = adsk.fusion.FlangeOrientations.SideOneFlangeOrientation
        bf = ff.add(bfi)
        bf.name = "BASE - BACK"
        body = bf.bodies.item(0)
        b0 = box(body)
        ztop = b0[5]                      # the base's face toward the room

        def edges_at(zv, keep=lambda e: True):
            """Straight edges lying at Z zv, read again from the body as it is now (a deleted trial
            feature can leave earlier edge objects stale)."""
            return [e for e in comp.bRepBodies.item(0).edges if e.geometry.objectType == adsk.core.Line3D.classType()
                    and abs(e.startVertex.geometry.z * 10 - zv) < 0.01 and abs(e.endVertex.geometry.z * 10 - zv) < 0.01
                    and keep(e)]
        if len(edges_at(ztop)) != 4:
            raise RuntimeError("body: expected 4 edges on the base's room face, got %d" % len(edges_at(ztop)))
        want = [0.0, 0.0, ev(design, "w"), ev(design, "h")]
        ret = None
        for pos in (adsk.fusion.BendPositionTypes.InsideBendPositionType, adsk.fusion.BendPositionTypes.OutsideBendPositionType):
            for flip in (False, True):
                efi = ff.createEdgeFlangeInput(edges_at(ztop), vi("d - 2 * t"))
                efi.heightDatumType = adsk.fusion.FlangeHeightDatumTypes.OuterFacesFlangeHeightDatumType
                efi.bendPositionType = pos
                efi.isFlipped = flip
                ef = ff.add(efi)
                b = box(comp.bRepBodies.item(0))
                # outer faces on the outline, and folded toward +Z: the open side must be +Z, or the part is the
                # mirror image of the design (the lead exits at X = w must face the pod's +X corner as fitted)
                ok = all(abs(g - w_) < 0.05 for g, w_ in zip([b[0], b[1], b[3], b[4]], want)) and b[5] - b[2] > 20 \
                    and b[5] > b0[5] + 10
                print("body returns, bend position %d flipped %s: box %s %s" % (pos, flip, b, "ok" if ok else "rejected"))
                if ok:
                    ret = ef
                    break
                ef.deleteMe()
            if ret:
                break
        if ret is None:
            raise RuntimeError("body: no return placement keeps the outer faces on the outline and folds toward +Z")
        ret.name = "FLANGE - RETURNS"
        body = comp.bRepBodies.item(0)
        b = box(body)
        zfront = b[5] if abs(b[5] - b0[5]) > 1 else b[2]

        def on_outline(e):
            s0 = e.startVertex.geometry
            return min(abs(s0.x * 10 - b[0]), abs(s0.x * 10 - b[3]), abs(s0.y * 10 - b[1]), abs(s0.y * 10 - b[4])) < 0.05

        def inner():
            return edges_at(zfront, lambda e: not on_outline(e) and e.length * 10 > 100)
        if len(inner()) != 4:
            raise RuntimeError("body: expected 4 inner front edges, got %d" % len(inner()))
        lip = None
        for flip in (False, True):
            efi = ff.createEdgeFlangeInput(inner(), vi("lip"))
            efi.isFlipped = flip
            efi.isMiteredCorners = True
            efi.heightDatumType = adsk.fusion.FlangeHeightDatumTypes.OuterFacesFlangeHeightDatumType
            f = ff.add(efi)
            b2 = box(comp.bRepBodies.item(0))
            inside = all(abs(b2[k] - b[k]) < 0.05 for k in (0, 1, 3, 4))
            print("body lips, flipped %s: box %s, %s" % (flip, b2, "inside" if inside else "rejected"))
            if inside and f.healthState == adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:
                lip = f
                break
            f.deleteMe()
        if lip is None:
            raise RuntimeError("body: no lip direction keeps the lips inside the box")
        lip.name = "FLANGE - FRONT LIPS"
        # depth back to front must be d: the lips' bend (radius t) adds to the returns' height, by how
        # much depends on Fusion's bend position, so measure it and fix the returns' height in whole t
        for _try in range(2):
            b3 = box(comp.bRepBodies.item(0))
            off = (b3[5] - b3[2]) - ev(design, "d")
            if abs(off) < 0.05:
                break
            k = round(off / ev(design, "t"))
            if abs(off - k * ev(design, "t")) > 0.05 or abs(k) > 3:
                raise RuntimeError("body: depth %.3f, not d; off by %.3f (not whole t)" % (b3[5] - b3[2], off))
            dist = adsk.fusion.EdgeFlangeFeatureDefinition.cast(ret.definition).distance
            n = 2 + k + (round((ev(design, "d") - dist.value * 10.0) / ev(design, "t")) - 2)
            dist.expression = "d - %d * t" % n
            adsk.doEvents()
            print("body: depth was off by %.3f mm; returns' height set to d - %d * t" % (off, n))
        b3 = box(comp.bRepBodies.item(0))
        if abs((b3[5] - b3[2]) - ev(design, "d")) > 0.05:
            raise RuntimeError("body: depth %.3f, not d %.3f" % (b3[5] - b3[2], ev(design, "d")))
    finally:
        design.activateRootComponent()
    return comp.bRepBodies.item(0)


AXIS_OF_PLANE = {"yZConstructionPlane": "x", "xZConstructionPlane": "y", "xYConstructionPlane": "z"}


def plane_at(design: "adsk.fusion.Design", comp: "adsk.fusion.Component", plane_base, offset, name):
    """A construction plane parallel to plane_base at model coordinate `offset` along its normal axis
    (tries +offset and -(offset), keeps the one that lands there), or the base plane itself at 0."""
    base = getattr(comp, plane_base)
    want = ev(design, offset)
    if abs(want) < 1e-9:
        return base
    ax = AXIS_OF_PLANE[plane_base]
    for e in (offset, "-(%s)" % offset):
        pin = comp.constructionPlanes.createInput()
        pin.setByOffset(base, vi(e))
        pl = comp.constructionPlanes.add(pin)
        o = pl.geometry.origin
        got = {"x": o.x, "y": o.y, "z": o.z}[ax] * 10.0
        if abs(got - want) < 0.01:
            pl.name = "PLANE - " + name
            pl.isLightBulbOn = False
            return pl
        pl.deleteMe()
    raise RuntimeError("could not place the plane for " + name)


def cut_hole(design: "adsk.fusion.Design", comp: "adsk.fusion.Component", body: "adsk.fusion.BRepBody", plane_base, offset, c1, c2, d, name, axis_map):
    """A through hole: circle on a plane at `offset`, cut symmetric 3 x t (the wall it crosses)."""
    pl = plane_at(design, comp, plane_base, offset, name)
    sk = comp.sketches.add(pl)
    sk.name = "HOLE - " + name
    # place the circle at the model point, then dimension along the sketch axes the model axes map to
    m = {"x": 0.0, "y": 0.0, "z": 0.0}
    m[axis_map[0]], m[axis_map[1]] = ev(design, c1), ev(design, c2)
    p = sk.modelToSketchSpace(adsk.core.Point3D.create(m["x"] * MM, m["y"] * MM, m["z"] * MM))
    c = sk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(p.x, p.y, 0), ev(design, d) / 2 * MM)
    g = c.centerSketchPoint.geometry
    tp = adsk.core.Point3D.create(g.x + 0.8, g.y + 0.8, 0)
    sk.sketchDimensions.addDiameterDimension(c, tp).parameter.expression = d
    o = sk.modelToSketchSpace(adsk.core.Point3D.create(0, 0, 0))
    for ax, ex in ((axis_map[0], c1), (axis_map[1], c2)):
        v = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}[ax]
        e = sk.modelToSketchSpace(adsk.core.Point3D.create(*v))
        sa = "x" if abs(e.x - o.x) > abs(e.y - o.y) else "y"
        sk.sketchDimensions.addDistanceDimension(sk.originPoint, c.centerSketchPoint, H if sa == "x" else VO,
                                                 tp).parameter.expression = "abs(%s)" % ex
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: " + sk.name)
    ei = comp.features.extrudeFeatures.createInput(sk.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation)
    ei.setSymmetricExtent(vi("3 * t"), True)
    ei.participantBodies = [comp.bRepBodies.item(0) if comp.bRepBodies.count == 1 else body]  # fresh, after earlier cuts
    f = comp.features.extrudeFeatures.add(ei)
    f.name = "CUT - " + name
    return f


def export(design: "adsk.fusion.Design", root: "adsk.fusion.Component", comp: "adsk.fusion.Component", key, repo, stem):
    em = design.exportManager
    out = {"f3d": "v2/01-CAD-Native/electrical/%s_CAD.f3d" % stem,
           "step": "v2/03-Manufacturing/electrical/%s_STEP.step" % stem,
           "dxf": "v2/03-Manufacturing/electrical/%s_DXF.dxf" % stem}
    for kind, mk in (("f3d", em.createFusionArchiveExportOptions), ("step", em.createSTEPExportOptions)):
        path = os.path.join(repo, out[kind])
        ok = False
        for _try in range(10):
            if em.execute(mk(path, root)) and os.path.getsize(path) > 500:
                ok = True
                break
            adsk.doEvents()
            time.sleep(3)
        print("export %s: %s" % (out[kind], ok))
        if not ok:
            raise RuntimeError("export failed: " + out[kind])
    path = os.path.join(repo, out["dxf"])
    if key == "body":
        b0 = comp.bRepBodies.item(0)
        planar = [f for f in b0.faces if f.geometry.objectType == adsk.core.Plane.classType()]
        stationary = max(planar, key=lambda f: f.area)
        fp = comp.flatPattern or comp.createFlatPattern(stationary)
        ok = em.execute(em.createDXFFlatPatternExportOptions(path, fp))
    else:
        sk = comp.sketches.itemByName("OUTLINE AND CUT-OUTS - %s" % key.upper())
        lines, circles, other = [], [], 0
        for i in range(sk.sketchCurves.count):
            c = sk.sketchCurves.item(i)
            if c.isConstruction:
                continue
            ln, ci = adsk.fusion.SketchLine.cast(c), adsk.fusion.SketchCircle.cast(c)
            if ln:
                a, b = ln.startSketchPoint.geometry, ln.endSketchPoint.geometry
                lines.append(((a.x * 10.0, a.y * 10.0), (b.x * 10.0, b.y * 10.0)))
            elif ci:
                g = ci.centerSketchPoint.geometry
                circles.append(((g.x * 10.0, g.y * 10.0), ci.radius * 10.0))
            else:
                other += 1
        if other:
            raise RuntimeError("%s: %d curves that are neither lines nor circles" % (sk.name, other))
        n = flat_dxf.write(path, lines, circles)
        ok = os.path.getsize(path) > 200
        print("DXF: %d lines and %d circles on layer %s, mm" % (n[0], n[1], flat_dxf.LAYER))
    print("export %s: %s" % (out["dxf"], ok))
    if not ok:
        raise RuntimeError("DXF export failed")


def _folder(app: "adsk.core.Application"):
    proj = [p for p in app.data.dataProjects if p.name == "Default Project"][0]
    return proj, proj.rootFolder.dataFolders.itemByName(FOLDER)


def open_or_create(app: "adsk.core.Application", name):
    """The design called `name`: activated if open, opened from FocusPod v2 if there, else made.
    PM ruling 2026-11-01: read every entry of the folder first, and make nothing if any can't be read
    (that entry could be this very design); a new design is saved there at once, empty."""
    docs = [app.documents.item(i) for i in range(app.documents.count)]
    docs = [d for d in docs if d.name == name or d.name.split(" v")[0] == name]
    if len(docs) > 1:
        raise RuntimeError("%d open documents are called %s" % (len(docs), name))
    if docs:
        docs[0].activate()
        return docs[0], "activated"
    proj, folder = _folder(app)
    # an entry still uploading (often a design saved a moment ago) reads as unreadable for a while, so read
    # the whole folder again a few times before giving up; nothing is made while any entry can't be read
    for attempt in range(6):
        n = folder.dataFiles.count
        found, unreadable = [], 0
        for i in range(n):
            try:
                f = folder.dataFiles.item(i)
                if f.name == name:
                    found.append(f)
            except Exception:
                unreadable += 1
        if not unreadable or found:
            break
        print("%s: %d of %d entries can't be read yet; reading again in 10 s (%d)" % (FOLDER, unreadable, n, attempt + 1))
        adsk.doEvents()
        time.sleep(10)
    app.data.activeProject = proj
    if len(found) > 1:
        raise RuntimeError("%d files are called %s in %s" % (len(found), name, FOLDER))
    if found:
        d = app.documents.open(found[0], True)
        if d is None:
            raise RuntimeError("could not open %s" % name)
        d.activate()
        return d, "opened (version %s)" % found[0].versionNumber
    if unreadable:
        raise RuntimeError("%d of the %d entries of %s can't be read, so %s isn't made (PM ruling 2026-11-01)"
                           % (unreadable, n, FOLDER, name))
    print("%s: all %d entries read, %s is not there: making it" % (FOLDER, n, name))
    d = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    if not d.saveAs(name, folder, "new, made by electrical_parts_cad.py", ""):
        d.close(False)
        raise RuntimeError("saveAs %s into %s failed" % (name, FOLDER))
    d.activate()
    return d, "made"


def clear_design(design: "adsk.fusion.Design"):
    """Empty a design that is opened again: the timeline and the components. User parameters stay and
    are updated in place (a parameter a feature used can't be deleted and re-added in the same run)."""
    tl = design.timeline
    if tl.count:
        tl.markerPosition = 0
        tl.deleteAllAfterMarker()
    root = design.rootComponent
    for i in range(root.occurrences.count - 1, -1, -1):
        root.occurrences.item(i).deleteMe()
    left = design.timeline.count + root.occurrences.count + root.bRepBodies.count + root.sketches.count
    if left:
        raise RuntimeError("%d timeline items, components, bodies or sketches left after clearing" % left)


def set_param(design: "adsk.fusion.Design", name, expr, unit, comment):
    p = design.userParameters.itemByName(name)
    if p is None:
        return design.userParameters.add(name, vi(expr), unit, comment)
    p.expression = expr
    p.comment = comment
    return p


def set_front_room_side(app: "adsk.core.Application", comp: "adsk.fusion.Component", zs):
    """Make the body design's Front (ViewCube) the view from the room side (its open side), +Y up, so
    the drawing's standard views line up in first-angle (WALL's set_front method: the drawing API has
    no view rotation). Geometry doesn't change; the save after this keeps it."""
    b = comp.bRepBodies.item(0).boundingBox
    mid = [(getattr(b.minPoint, a) + getattr(b.maxPoint, a)) / 2 for a in "xyz"]
    eye = list(mid)
    eye[2] += zs * 1000.0                          # 10 m out on the open side (cm)
    vp = app.activeViewport
    cam = vp.camera
    cam.cameraType = adsk.core.CameraTypes.OrthographicCameraType
    cam.target = adsk.core.Point3D.create(*mid)
    cam.eye = adsk.core.Point3D.create(*eye)
    cam.upVector = adsk.core.Vector3D.create(0, 1, 0)
    cam.isSmoothTransition = False
    vp.camera = cam
    vp.fit()
    if not vp.setCurrentAsFront():
        raise RuntimeError("setCurrentAsFront returned False")
    print("body: Front set to the room side (looking %sZ, +Y up)" % ("-" if zs > 0 else "+"))


def build_part(app: "adsk.core.Application", key):
    pn, name, vn, stem, params = PARTS[key]
    t0 = time.time()
    doc, how = open_or_create(app, stem + "_CAD")
    print("=== %s %s: %s" % (pn, name, how))
    try:
        design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
        root = design.rootComponent
        clear_design(design)
        for pname, expr, unit, status, src in params:
            set_param(design, pname, expr, unit, "%s: %s" % (status.upper(), src))
        root.partNumber = pn
        root.description = "%s | %s | %s" % (name, vn, M.REV)
        if key == "body":
            occ = root.occurrences.addNewSheetMetalComponent(adsk.core.Matrix3D.create())
            comp = occ.component
            comp.name, comp.partNumber = "%s %s" % (pn, name), pn
            comp.description = root.description
            body = body_tray(design, comp, occ)
            bb = box(body)
            t = ev(design, "t")
            zs = 1 if abs(bb[2]) < abs(bb[5]) else -1      # the returns fold toward +Z or -Z
            if zs != 1:
                raise RuntimeError("body opens toward -Z: that is the mirror image of the design; nothing saved")
            back_z = bb[2] if zs > 0 else bb[5]               # the back's outer face: Z 0, t or -t
            back = [e for e, v in (("0 mm", 0.0), ("t", t), ("-t", -t)) if abs(back_z - v) < 0.05]
            if not back:
                raise RuntimeError("body: the back's outer face is at Z %.3f, not 0 or +-t" % back_z)
            z = lambda e: "(%s) + (%s) * (%d)" % (back[0], e, zs)  # noqa: E731
            print("body: back face Z %s, returns toward %sZ" % (back[0], "+" if zs > 0 else "-"))
            # holes: right side (two lead exits), top (light feed), bottom (sleeve), lips (4 clinch nuts)
            cut_hole(design, comp, body, "yZConstructionPlane", "w", "lead_z1", z("d - lead_y"), "hole_b", "LEAD EXIT 1 RIGHT SIDE", ("y", "z"))
            cut_hole(design, comp, body, "yZConstructionPlane", "w", "lead_z2", z("d - lead_y"), "hole_b", "LEAD EXIT 2 RIGHT SIDE", ("y", "z"))
            cut_hole(design, comp, body, "xZConstructionPlane", "h", "top_x", z("d - lead_y"), "hole_b", "LIGHT FEED EXIT TOP", ("x", "z"))
            cut_hole(design, comp, body, "xZConstructionPlane", "0 mm", "sleeve_x", z("d - sleeve_y"), "sleeve_d", "SLEEVE ENTRY BOTTOM", ("x", "z"))
            for i, (cx, cy) in enumerate((("clinch_x", "clinch_y"), ("w - clinch_x", "clinch_y"),
                                          ("clinch_x", "h - clinch_y"), ("w - clinch_x", "h - clinch_y")), start=1):
                cut_hole(design, comp, body, "xYConstructionPlane", z("d - t / 2"), cx, cy, "clinch_d",
                         "CLINCH NUT HOLE %d IN THE LIP" % i, ("x", "y"))
            body = comp.bRepBodies.item(0)
            print("body box after holes %s" % box(body))
            body.name = name
        else:
            occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
            comp = occ.component
            comp.name, comp.partNumber = "%s %s" % (pn, name), pn
            comp.description = root.description
            body, _sk = flat_plate(design, comp, key)
        mat = design.materials.itemByName("Aluminum 5052")
        if mat is None:
            lib = app.materialLibraries.itemByName("Fusion Material Library")
            src = lib.materials.itemByName("Aluminum") if lib else None
            if src is not None:
                mat = design.materials.addByCopy(src, "Aluminum 5052")
                mat.materialProperties.itemById("structural_Density").value = 2680.0
        if mat is not None:
            body.material = mat
        tl = design.timeline
        unhealthy = [tl.item(i).name for i in range(tl.count)
                     if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
        loose = [sk.name for c in design.allComponents for sk in c.sketches if not sk.isFullyConstrained]
        props = comp.getPhysicalProperties(adsk.fusion.CalculationAccuracy.MediumCalculationAccuracy)
        vol = props.volume * 1000.0                          # cm3 -> mm3
        print("%s: box %s, volume %.0f mm3, mass %.3f kg (%s), timeline %d, unhealthy %d, loose sketches %d, "
              "parameters %d" % (pn, box(body), vol, props.mass, mat.name if mat else "no material: 2.68 g/cm3 by hand",
                                 tl.count, len(unhealthy), len(loose), design.userParameters.count))
        print("MASS|%s|%.4f" % (pn, vol * 2.68e-6))
        if unhealthy or loose:
            raise RuntimeError("checks failed: unhealthy %s, loose %s" % (unhealthy, loose))
        if key == "body":
            try:
                set_front_room_side(app, comp, zs)
            except Exception as e:      # the drawing can set it later; never fail the part for this
                print("body: Front not set (%s)" % e)
        if not doc.save("%s %s, by electrical_parts_cad.py" % (name, M.REV)):
            raise RuntimeError("save failed")
        print("saved %s_CAD in %s" % (stem, FOLDER))
        if ARGS.get("export") == "1":
            export(design, root, comp, key, ARGS["repo_root"], stem)
        print("%s done in %.0f s" % (pn, time.time() - t0))
    finally:
        print("closed:", doc.close(False))      # the saved version stays in the cloud


def run(_context):
    keys = [k for k in ARGS.get("parts", "front,hub,body").split(",") if k]
    bad = [k for k in keys if k not in PARTS]
    if bad:
        raise RuntimeError("parts must be among %s, not %s" % (sorted(PARTS), bad))
    app = adsk.core.Application.get()
    # ELECTRICAL's own route design, left open when the edit test after its rebuild failed (2026-10-31
    # 19:2x, runner: not saved or closed); its saved version is in the cloud. Close it, so it can't keep
    # a skeleton copy loaded for other runs. Only that name; nothing of anyone else's.
    for i in range(app.documents.count - 1, -1, -1):
        d = app.documents.item(i)
        if d.name.split(" v")[0] == "710000_P01_ELECTRICAL_CAD":
            print("closing ELECTRICAL's left-open route design %s (unsaved changes: %s; saved version kept)"
                  % (d.name, d.isModified))
            d.close(False)
    failed = []
    for key in keys:
        try:
            build_part(app, key)
        except Exception:
            import traceback
            print("PART FAILED %s\n%s" % (key, traceback.format_exc()))
            failed.append(key)
    if failed:
        raise RuntimeError("parts that failed: %s (the others built, saved and exported)" % ", ".join(failed))
