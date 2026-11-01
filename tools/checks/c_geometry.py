#!/usr/bin/env python3
"""Geometry checks that run on the STEP files in the repo, without Fusion.

- C01 (offline part): outer shell closure. Points on the pod's back, side and
  top faces must each sit inside some body; open regions bigger than the
  reporting size are findings. Bodies are taken as their boxes, so a gap
  inside a faceted body's box is not seen (Fusion's exact check covers it).
- C02 (gap rules): minimum and maximum gaps between named bodies, from
  v2/04-Checks/config/gap-rules.csv (the same file the Fusion check reads).
  Offline, a gap is the gap between boxes, exact for box-shaped bodies.
- C08: mating holes across parts line up: coaxial holes in different parts
  must be nominally on one axis.
- C09: edge distance at least 2 hole diameters, hole spacing, sheet-metal
  bend radius and hole-to-bend distance, per part.

Models: the skeleton (v2/03-Manufacturing/skeleton/*.step, envelopes) and the
assembled design (every other assembly STEP in pod coordinates) are checked
separately, so envelopes never clash with the real parts.
"""

import csv
import fnmatch
import math
import os
import re
from collections import defaultdict

from common import (Finding, owner_for, rel, walk_files, num, pn_class, read_csv, reserved_spaces, reserved_label,
                    is_soft)
import stepfile as sf

POD_BOX = (-1250.0, -850.0, 0.0, 1250.0, 850.0, 2400.0)


# ----------------------------------------------------------------- loading

class Body:
    __slots__ = ("label", "solid", "frame", "box", "file", "part_number", "step")

    def __init__(self, label, solid, frame, box, file, part_number, step):
        self.label, self.solid, self.frame, self.box = label, solid, frame, box
        self.file, self.part_number, self.step = file, part_number, step


def load_step(path, cache={}):
    if path not in cache:
        cache[path] = sf.StepFile(path)
    return cache[path]


def bodies_of(root, path):
    s = load_step(path)
    out = []
    for inst in s.instances():
        so = s.solid(inst["solid"])
        box = sf.world_box(so, inst["frame"])
        if box is None:
            continue
        label = " / ".join([p for p in inst["path"] if p] + [so.name or ""])
        out.append(Body(label, so, inst["frame"], box, rel(root, path), inst["part_number"], s))
    return out


def in_pod(box, tol=5.0):
    return all(box[k] >= POD_BOX[k] - tol for k in range(3)) and all(box[k + 3] <= POD_BOX[k + 3] + tol
                                                                      for k in range(3))


def models(root):
    """{'skeleton': [bodies], 'assembly': [bodies]} plus a list of per-part
    STEP files (not in pod coordinates) for the per-part checks."""
    steps = walk_files(root, "v2/03-Manufacturing", exts=(".step", ".stp"))
    out = {"skeleton": [], "assembly": []}
    per_part = []
    for p in steps:
        r = rel(root, p)
        bs = bodies_of(root, p)
        if "/skeleton/" in r:
            out["skeleton"].extend(bs)
            continue
        s = load_step(p)
        _c, tops = s.usage_counts()
        is_asm = any(pn_class(t) == "assembly" for t in tops)
        if is_asm and bs and all(in_pod(b.box) for b in bs):
            out["assembly"].extend(bs)
        per_part.append(p)
    return out, per_part


# ----------------------------------------------------------------- C01 shell

SHELL_ZONES = [
    # face, fixed axis, value, inward sign, (axis a, lo, hi), (axis b, lo, hi), needs (glob of files)
    ("back", 1, 850.0, -1, (0, -1250.0, 1250.0), (2, 110.0, 2400.0), None),
    ("left", 0, -1250.0, +1, (1, -645.0, 850.0), (2, 110.0, 2400.0), None),
    ("right", 0, 1250.0, -1, (1, -645.0, 850.0), (2, 110.0, 2400.0), None),
    ("top", 2, 2400.0, -1, (0, -1250.0, 1250.0), (1, -645.0, 850.0), None),
    # the base zone (Z 10 to 110) once the BASE assembly exists; Z 0 to 10 is the glide gap
    ("back-base", 1, 850.0, -1, (0, -1250.0, 1250.0), (2, 10.0, 110.0), "v2/03-Manufacturing/base/*.step"),
    # the side faces start where the walls do: in front of Y -645 the outline is v1's faceted front, which
    # follows the decor blocks and is checked exactly in Fusion, not on a flat face
    ("left-base", 0, -1250.0, +1, (1, -645.0, 850.0), (2, 10.0, 110.0), "v2/03-Manufacturing/base/*.step"),
    ("right-base", 0, 1250.0, -1, (1, -645.0, 850.0), (2, 10.0, 110.0), "v2/03-Manufacturing/base/*.step"),
]


def _covered(p, boxes, eps=1e-6):
    for b in boxes:
        if b[0] - eps <= p[0] <= b[3] + eps and b[1] - eps <= p[1] <= b[4] + eps and b[2] - eps <= p[2] <= b[5] + eps:
            return True
    return False


def _subtract(r, c):
    """Rectangle r minus rectangle c, both (a0, a1, b0, b1): up to 4 pieces."""
    a0, a1, b0, b1 = r
    c0, c1, d0, d1 = c
    if c1 <= a0 or c0 >= a1 or d1 <= b0 or d0 >= b1:
        return [r]
    out = []
    if c0 > a0:
        out.append((a0, c0, b0, b1))
    if c1 < a1:
        out.append((c1, a1, b0, b1))
    m0, m1 = max(a0, c0), min(a1, c1)
    if d0 > b0:
        out.append((m0, m1, b0, d0))
    if d1 < b1:
        out.append((m0, m1, d1, b1))
    return out


def _merge(rects, tol=1e-6):
    """Join open rectangles that share a full edge, so one slot reads as one."""
    rects = list(rects)
    changed = True
    while changed:
        changed = False
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                a, b = rects[i], rects[j]
                if abs(a[2] - b[2]) < tol and abs(a[3] - b[3]) < tol and (abs(a[1] - b[0]) < tol or abs(b[1] - a[0]) < tol):
                    rects[i] = (min(a[0], b[0]), max(a[1], b[1]), a[2], a[3])
                elif abs(a[0] - b[0]) < tol and abs(a[1] - b[1]) < tol and (abs(a[3] - b[2]) < tol or abs(b[3] - a[2]) < tol):
                    rects[i] = (a[0], a[1], min(a[2], b[2]), max(a[3], b[3]))
                else:
                    continue
                rects.pop(j)
                changed = True
                break
            if changed:
                break
    return rects


SEAM_GAP = 2.26          # the decided metal-stop seam (PM ruling on F-008): narrower gaps are seams, not openings


def _touch(a, b, tol=1e-6):
    """Two rectangles overlap or share a boundary of positive length."""
    oa = min(a[1], b[1]) - max(a[0], b[0])
    ob = min(a[3], b[3]) - max(a[2], b[2])
    return (oa >= -tol and ob > tol) or (oa > tol and ob >= -tol)


def _components(rects):
    groups = []
    for r in rects:
        hit = [g for g in groups if any(_touch(r, x) for x in g)]
        merged = [r] + [x for g in hit for x in g]
        groups = [g for g in groups if g not in hit] + [merged]
    return groups


def shell_gaps(bodies, inset=1.0, seam=SEAM_GAP, root=None, faces=None):
    """Open regions on the pod's outer faces. Each body's box, where it
    reaches 1 mm inside a face, is grown by just over half a seam in the
    face's plane, so a decided 2.26 mm seam closes and anything wider stays
    open; every piece left is an opening (no size cut-off before joining).
    Touching pieces are joined into one region; its reported extent is
    grown back by the same margin. Each result: zone, axes, a and b (open
    ranges), near (the bodies bordering it)."""
    grow = seam / 2.0 + 0.1
    out = []
    for zone, ax, val, sign, (aa, a0, a1), (bb, b0, b1), needs in SHELL_ZONES:
        if needs and not (root and _glob_exists(root, needs)):
            continue
        if faces is not None and zone not in faces:
            continue                # its parts aren't all on main yet
        plane = val + sign * inset
        face_bodies = [b for b in bodies if b.box[ax] - 1e-6 <= plane <= b.box[ax + 3] + 1e-6]
        open_ = [(a0, a1, b0, b1)]
        for b in face_bodies:
            c = (b.box[aa] - grow, b.box[aa + 3] + grow, b.box[bb] - grow, b.box[bb + 3] + grow)
            open_ = [piece for r in open_ for piece in _subtract(r, c)]
        open_ = [r for r in open_ if r[1] - r[0] > 1e-3 and r[3] - r[2] > 1e-3]
        groups = []
        for g in _components(open_):
            box_area = (max(x[1] for x in g) - min(x[0] for x in g)) * (max(x[3] for x in g) - min(x[2] for x in g))
            area = sum((x[1] - x[0]) * (x[3] - x[2]) for x in g)
            # an L of thin strips isn't a hole its box covers: report each strip then, not the box of all of them
            groups.extend([g] if area >= 0.5 * box_area else [[x] for x in g])
        for g in groups:
            r = (max(a0, min(x[0] for x in g) - grow), min(a1, max(x[1] for x in g) + grow),
                 max(b0, min(x[2] for x in g) - grow), min(b1, max(x[3] for x in g) + grow))
            # a strip no wider than the decided seam along the face's own edge is the seam to a part of the next face
            # (a decor block in front, the band below), which this face can't see; that face reports what is missing
            edge_seam = ((r[0] <= a0 + 1e-3 or r[1] >= a1 - 1e-3) and r[1] - r[0] <= seam + 0.1) or \
                        ((r[2] <= b0 + 1e-3 or r[3] >= b1 - 1e-3) and r[3] - r[2] <= seam + 0.1)
            if edge_seam:
                continue
            near = sorted({b.label.split(" / ")[-1] for b in face_bodies
                           if b.box[aa] <= r[1] + 1e-3 and b.box[aa + 3] >= r[0] - 1e-3
                           and b.box[bb] <= r[3] + 1e-3 and b.box[bb + 3] >= r[2] - 1e-3})
            out.append({"zone": zone, "axes": ("XYZ"[aa], "XYZ"[bb]), "a": (r[0], r[1]), "b": (r[2], r[3]),
                        "near": near})
    return out


def _glob_exists(root, pattern):
    d = os.path.join(root, os.path.dirname(pattern))
    if not os.path.isdir(d):
        return False
    return any(fnmatch.fnmatch(f, os.path.basename(pattern)) for f in os.listdir(d))


# the assembled shell is checked face by face, once the parts that cover a face are all on main: before that, an
# "opening" there is mostly a part not merged yet (the back walls, a band, a decor block), not a gap in what is there.
# Each face lists the parts it needs, by the words in their names; the seams between parts already there are the
# gap rules' job. The skeleton is complete and is always checked.
# words may be joined by spaces or by the file names' hyphens (210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_CAD)
SHELL_FACE_NEEDS = {
    "back": (r"PANEL\W+ASSY\W+BACK\W+LOWER\W+(?:LH|B1)", r"PANEL\W+ASSY\W+BACK\W+LOWER\W+(?:RH|B2)", r"PANEL\W+ASSY\W+BACK\W+UPPER\W+(?:LH|B3)",
             r"PANEL\W+ASSY\W+BACK\W+UPPER\W+(?:RH|B4)", r"CEILING\W+PANEL\W+ASSY"),
    # a side face's bottom seam closes on its side band, so the band is one of its parts too
    "left": (r"PANEL\W+ASSY\W+SIDE\W+LOWER\W+LH", r"PANEL\W+ASSY\W+SIDE\W+UPPER\W+LH", r"DECOR\W+BLOCK\W+(ASSY\W+)?DL(?![A-Z0-9])",
             r"BAND\W+(ASSY\W+)?SIDE\W+LH"),
    "right": (r"PANEL\W+ASSY\W+SIDE\W+LOWER\W+RH", r"PANEL\W+ASSY\W+SIDE\W+UPPER\W+RH", r"DECOR\W+BLOCK\W+(ASSY\W+)?DR(?![A-Z0-9])",
              r"BAND\W+(ASSY\W+)?SIDE\W+RH"),
    "top": (r"CEILING\W+PANEL\W+ASSY\W+C1(?![A-Z0-9])", r"CEILING\W+PANEL\W+ASSY\W+C2(?![A-Z0-9])", r"DECOR\W+BLOCK\W+(ASSY\W+)?DT(?![A-Z0-9])"),
    # the back corners of the base are the side bands' ends, so each base face needs the bands that meet it
    "back-base": (r"BAND\W+(ASSY\W+)?BACK", r"BAND\W+(ASSY\W+)?SIDE\W+LH", r"BAND\W+(ASSY\W+)?SIDE\W+RH"),
    "left-base": (r"BAND\W+(ASSY\W+)?SIDE\W+LH", r"BAND\W+(ASSY\W+)?BACK"),
    "right-base": (r"BAND\W+(ASSY\W+)?SIDE\W+RH", r"BAND\W+(ASSY\W+)?BACK"),
}


def shell_faces_ready(mdl, bodies):
    """The shell faces whose parts are all on main (every face for the skeleton)."""
    zones = [z[0] for z in SHELL_ZONES]
    if mdl == "skeleton":
        return set(zones)
    labels = [b.label.upper() for b in bodies]
    return {z for z in zones if all(any(re.search(p, l) for l in labels) for p in SHELL_FACE_NEEDS.get(z, ()))}


def shell_ready(mdl, bodies):
    return bool(shell_faces_ready(mdl, bodies))


def check_shell(root, mdl, bodies):
    fs = []
    faces = shell_faces_ready(mdl, bodies)
    if not faces:
        return fs
    for g in shell_gaps(bodies, root=root, faces=faces):
        an, bn = g["axes"]
        (a0, a1), (b0, b1) = g["a"], g["b"]
        fs.append(Finding(
            "C01", "shell-open", "%s shell %s %s %.0f..%.0f %s %.0f..%.0f" % (mdl, g["zone"], an, a0, a1, bn, b0, b1),
            "severe",
            "The outer shell is open on the %s face of the %s: nothing covers %s %.0f to %.0f, %s %.0f to %.0f "
            "(a slot %.0f x %.0f mm). Bordered by: %s. Checked exactly, 1 mm inside the face, bodies "
            "as their boxes." % (g["zone"], mdl, an, a0, a1, bn, b0, b1, a1 - a0, b1 - b0,
                               ", ".join(g["near"]) or "nothing"),
            "Close it: extend the bordering panels to meet, or add the part that belongs there (a bought part that "
            "closes it, like an end cap, needs its body in the CAD, an ENVELOPE if the product is HOLD).",
            _near_file(bodies, g["near"]) or _file_of(bodies), owner_for(_near_file(bodies, g["near"]) or _file_of(bodies)),
            # the scope is the face, so a run that skips a face (its parts not on main) can't close what it found
            {"model": mdl if mdl == "skeleton" else "%s-%s" % (mdl, g["zone"]), "near": g["near"]}))
    return fs


def _near_file(bodies, near):
    """The one STEP file the bodies bordering an opening come from, or '' when they come from several."""
    files = sorted({b.file for b in bodies if b.label.split(" / ")[-1] in set(near or ())})
    return files[0] if len(files) == 1 else ""


def _file_of(bodies):
    files = sorted({b.file for b in bodies})
    return files[0] if len(files) == 1 else ""


# ----------------------------------------------------------------- C02 gap rules

def load_gap_rules(root):
    p = os.path.join(root, "v2/04-Checks/config/gap-rules.csv")
    return read_csv(p) if os.path.exists(p) else []


# the room's floor, which the pod stands on (D-132: the pod has no floor of its own): the plane Z 0, for gap rules that
# name it ('ROOM FLOOR'), such as D-151's kick strip over the floor
ROOM_FLOOR = Body("ROOM FLOOR (Z 0)", None, None, (-1e6, -1e6, -100.0, 1e6, 1e6, 0.0), "", "", None)


def check_gap_rules(root, mdl, bodies, rules):
    """One finding per rule group (the `group` column, else the rule id),
    listing every rule in it that fails."""
    fails = {}
    reserved = reserved_spaces(root)
    bodies = [b for b in bodies if not reserved_label(b.label, reserved)]   # reserved spaces have no seams yet
    bodies = [b for b in bodies if not re.search(r"(?<!\d)7100\d\d(?!\d)", b.label or "")]   # D-92: nor route bodies
    for r in rules:
        if r.get("models") and mdl not in r["models"].split():
            continue
        if (r.get("method") or "box").strip() == "exact":
            continue            # needs true distances (slanted or curved parts): the Fusion check measures it
        ra = re.compile(r["a"], re.I)
        rb = re.compile(r["b"], re.I)
        A = [b for b in bodies if ra.search(b.label)]
        B = [b for b in bodies if rb.search(b.label)]
        if rb.search(ROOM_FLOOR.label):
            B.append(ROOM_FLOOR)            # D-132, D-151: no floor in the pod; the room floor is the plane Z 0
        if not A or not B:
            continue
        lo, hi = num(r.get("min_gap_mm")), num(r.get("max_gap_mm"))
        worst = None
        for a in A:
            for b in B:
                if a is b:
                    continue
                g = sf.box_gap(a.box, b.box)
                if g > 50.0:              # only neighbours
                    continue
                if worst is None or g < worst[0]:
                    worst = (g, a, b)
        if worst is None:
            continue
        g, a, b = worst
        if (lo is not None and g < lo - 1e-6) or (hi is not None and g > hi + 1e-6):
            fails.setdefault(r.get("group") or r["id"], []).append((r, g, a, b, lo, hi))
    fs = []
    for grp, items in fails.items():
        r0 = items[0][0]
        sev = "severe" if any(it[0].get("severity") == "severe" for it in items) else (r0.get("severity") or "major")
        parts = []
        for r, g, a, b, lo, hi in items:
            parts.append("%s: %s to %s is %.1f mm, needs %s" % (
                r["id"], a.label.split(" / ")[-1], b.label.split(" / ")[-1], g, _range_text(lo, hi)))
        fs.append(Finding(
            "C02", "gap-" + grp, "%s %s" % (mdl, grp), sev,
            "%s. Rule source: %s. Why: %s" % ("; ".join(parts), r0.get("status_source", ""), r0.get("why", "")),
            r0.get("fix", ""), items[0][2].file, r0.get("owner") or owner_for(items[0][2].file),
            {"model": mdl, "rules": [{"id": r["id"], "gap_mm": round(g, 2), "a": a.label, "b": b.label}
                                     for r, g, a, b, lo, hi in items]}))
    return fs


def _range_text(lo, hi):
    if lo is not None and hi is not None:
        return "%g to %g mm" % (lo, hi)
    if lo is not None:
        return "at least %g mm" % lo
    return "at most %g mm" % hi


# ----------------------------------------------------------------- C08 alignment

def world_holes(bodies):
    out = []
    for b in bodies:
        for h in b.solid.holes:
            out.append((b, h.moved(b.frame)))
    return out


def check_alignment(root, mdl, bodies, capture=4.0, axial_gap=40.0):
    """Coaxial holes in different parts (axes parallel within 0.5 degrees,
    centres within `capture` mm sideways, within `axial_gap` mm along the
    axis) are taken as mating holes; a nominal offset over 0.05 mm is a
    finding."""
    fs = []
    hs = world_holes(bodies)
    cos_tol = math.cos(math.radians(0.5))
    seen = set()
    for i, (ba, ha) in enumerate(hs):
        for bb, hb in hs[i + 1:]:
            if ba is bb or ba.part_number == bb.part_number and ba.solid is bb.solid:
                continue
            if abs(sf.dot(ha.axis, hb.axis)) < cos_tol:
                continue
            lateral = sf.line_distance(hb.center, ha.center, ha.axis)
            if lateral > capture:
                continue
            along = abs(sf.dot((hb.center[0] - ha.center[0], hb.center[1] - ha.center[1], hb.center[2] - ha.center[2]),
                               ha.axis))
            if along - (ha.length + hb.length) / 2.0 > axial_gap:
                continue
            if lateral <= 0.05:
                continue
            key = tuple(sorted((ba.label, bb.label))) + (round(ha.center[0]), round(ha.center[1]), round(ha.center[2]))
            if key in seen:
                continue
            seen.add(key)
            clear = min(ha.diameter, hb.diameter)
            sev = "severe" if lateral > (max(ha.diameter, hb.diameter) - 6.0) / 2.0 else "major"
            fs.append(Finding(
                "C08", "hole-offset", "%s %s x %s at %s" % (mdl, ba.label.split(" / ")[-1], bb.label.split(" / ")[-1],
                                                           _pt(ha.center)),
                sev,
                "Mating holes are %.2f mm off axis in the CAD: %s (Ø%.2f) and %s (Ø%.2f) at %s. Holes that take the "
                "same bolt should share one nominal axis; tolerances come on top." % (
                    lateral, ba.label, ha.diameter, bb.label, hb.diameter, _pt(ha.center)),
                "Put both holes on the same axis, driven by one shared parameter or sketch point.",
                ba.file, owner_for(ba.file, ba.part_number),
                {"model": mdl, "offset_mm": round(lateral, 3)}))
    return fs


JOINT_HOLE_SIZES = ((5.9, 6.1), (6.3, 7.3), (9.4, 9.8))    # rivnut thread bore, M6 clearance, rivnut hole


def _box_hits_segment(box, p0, p1, pad=0.5):
    lo = [min(p0[k], p1[k]) - pad for k in range(3)]
    hi = [max(p0[k], p1[k]) + pad for k in range(3)]
    return all(box[k] <= hi[k] and box[k + 3] >= lo[k] for k in range(3))


RIVNUT_LABEL = re.compile(r"\b(RIVNUT|RIVET NUT)\b", re.I)


def check_hole_sizes(root, mdl, bodies, hole_rules=None, capture=4.0, plane=15.0):
    """Hole-size rules that depend on the mate: a clearance hole in the rule's
    size band is flagged only when it faces a rivnut in another part (a
    rivnut's hole or its thread bore on the same axis), so a blind rivet's
    6.5 mm hole is left alone. Needs the assembled model."""
    hole_rules = hole_rules if hole_rules is not None else load_hole_rules(root)
    fs = []
    hs = world_holes(bodies)
    rivnut_axes = [(b, h) for b, h in hs if (9.4 <= h.diameter <= 9.8) or
                   (RIVNUT_LABEL.search(b.label) and 5.9 <= h.diameter <= 6.1)]
    done = set()
    for hr in hole_rules:
        lo, hi = num(hr.get("min_dia_mm")), num(hr.get("max_dia_mm"))
        if lo is None or hi is None:
            continue
        for b, h in hs:
            if not lo <= h.diameter <= hi:
                continue
            faces = [rb for rb, rh in rivnut_axes if rb.part_number != b.part_number
                     and abs(sf.dot(rh.axis, h.axis)) > 0.9999
                     and sf.line_distance(rh.center, h.center, h.axis) <= capture
                     and abs(sf.dot(tuple(rh.center[k] - h.center[k] for k in range(3)), h.axis)) <= plane]
            if not faces or (b.part_number, hr["id"]) in done:
                continue
            done.add((b.part_number, hr["id"]))
            n = sum(1 for bb, x in hs if bb.part_number == b.part_number and lo <= x.diameter <= hi)
            fs.append(Finding(
                "C08", "hole-size-" + hr["id"], "%s %s holes Ø%.2f" % (mdl, b.label.split(" / ")[-1], h.diameter),
                hr.get("severity") or "major",
                "%s has %d hole(s) of Ø%.2f facing a rivnut (%s). %s. Rule: %s." % (
                    b.label, n, h.diameter, faces[0].label.split(" / ")[-1], hr.get("message", ""),
                    hr.get("status_source", "")),
                hr.get("fix", ""), b.file, owner_for(b.file, b.part_number),
                {"model": mdl, "dia_mm": round(h.diameter, 2), "count": n}))
    return fs


def check_unmatched(root, mdl, bodies, capture=4.0, search=60.0, plane=15.0):
    """Bolt patterns across assemblies: a joint hole (rivnut thread, M6
    clearance or rivnut hole) in one STEP file whose partner file has joint
    holes on the same joint plane (parallel axes, within `plane` mm along
    the axis) nearby, but none within `capture` mm of its axis. That is a
    pattern that doesn't match (the nearest candidate is reported). Holes
    with no candidates at all within `search` mm are left alone: the other
    side may not be modelled yet. Only holes in different files are paired,
    so a panel's own factory joints don't count; and a clearance hole and a
    rivnut in two parts of one file, on one axis, are matched there and are
    left out (FRONT's DR access panel into DR's own back-ring rivnuts, #105)."""
    fs = []
    hs = [(b, h) for b, h in world_holes(bodies) if any(lo <= h.diameter <= hi for lo, hi in JOINT_HOLE_SIZES)]
    seen = set()

    def kind(x):                      # a nut side (rivnut hole or its thread) or a clearance hole
        return "clear" if 6.3 <= x.diameter <= 7.3 else "nut"

    def own_joint(b, h):
        """A bolt into a nut in its own file (DR's access panel into DR's own rivnuts): a clearance hole and a nut
        side of another body of the same file on one axis. It is matched there, not across files."""
        for ob, x in hs:
            if ob is b or ob.file != b.file or kind(x) == kind(h) or abs(sf.dot(x.axis, h.axis)) < 0.9999:
                continue
            if abs(sf.dot(tuple(x.center[k] - h.center[k] for k in range(3)), h.axis)) <= plane and \
                    sf.line_distance(x.center, h.center, h.axis) <= capture:
                return True
        return False
    for b, h in hs:
        if own_joint(b, h):
            continue
        best = None
        for ob, x in hs:
            if ob.file == b.file or abs(sf.dot(x.axis, h.axis)) < 0.9999:
                continue
            d_ax = abs(sf.dot(tuple(x.center[k] - h.center[k] for k in range(3)), h.axis))
            if d_ax > plane:
                continue
            lat = sf.line_distance(x.center, h.center, h.axis)
            if best is None or lat < best[0]:
                best = (lat, ob, x)
        if best is None or best[0] <= capture or best[0] > search:
            continue
        lat, ob, x = best
        # one finding per joint axis in each file (a rivnut's hole and its thread bore share one)
        t = sf.dot(h.center, h.axis)
        foot = tuple(h.center[k] - h.axis[k] * t for k in range(3))
        key = (b.file, round(foot[0]), round(foot[1]), round(foot[2]))
        if key in seen:
            continue
        seen.add(key)
        fs.append(Finding(
            "C08", "hole-unmatched", "%s %s hole Ø%.1f at %s" % (mdl, b.label.split(" / ")[-1], h.diameter,
                                                               _pt(h.center)),
            "severe",
            "The Ø%.2f joint hole in %s at %s has no partner on its axis in %s: the nearest joint hole there "
            "(Ø%.2f in %s at %s) is %.1f mm off, so the bolt can't go in." % (
                h.diameter, b.label, _pt(h.center), ob.file, x.diameter, ob.label.split(" / ")[-1], _pt(x.center), lat),
            "Take both sides' hole patterns from one shared source (one parameter set both link to).",
            b.file, owner_for(b.file, b.part_number), {"model": mdl, "offset_mm": round(lat, 1), "other": ob.file}))
    return fs


# D-135 (PM, 2026-11-01): the ACP skin flexes 2 mm or less under a 100 N push at a bay's centre, edges simply
# supported. The skin is bonded to every frame member, so its free spans are the bays between members; WALL's span
# table (v2/01-CAD-Native/wall/ACP-SPANS.md: plate on 4 edges, 3 mm ACP with 0.21 mm skins) gives 1.99 mm for a
# 274.8 mm clear bay, so 275 mm clear is the widest bay that passes (the Lead's figure).
ACP_BAY_MAX = 275.0
WALL_FRAME = re.compile(r"(\d{6})\s+WALL\W+PANEL\W+FRAME\W+([A-Z0-9 -]+?)(?=:\d|\s*/|$)", re.I)


def acp_bays(bodies):
    """The bays of every wall panel frame: {frame label: [(short span, (u0, u1, v0, v1)), ...]}, in the frame's own
    plane (its two long box axes), each bay the frame's outline less every member, as rectangles."""
    frames = {}
    for b in bodies:
        m = WALL_FRAME.search(b.label or "")
        if m:
            frames.setdefault("%s %s" % (m.group(1), m.group(2).strip()), []).append(b)
    out = {}
    for name, members in frames.items():
        lo = [min(b.box[k] for b in members) for k in range(3)]
        hi = [max(b.box[k + 3] for b in members) for k in range(3)]
        ext = [hi[k] - lo[k] for k in range(3)]
        n = min(range(3), key=lambda k: ext[k])            # the frame's depth axis
        u, v = [k for k in range(3) if k != n]
        bays = [(lo[u], hi[u], lo[v], hi[v])]
        for b in members:
            c = (b.box[u], b.box[u + 3], b.box[v], b.box[v + 3])
            bays = [piece for r in bays for piece in _subtract(r, c)]
        bays = [r for r in bays if r[1] - r[0] > 1.0 and r[3] - r[2] > 1.0]
        out[name] = sorted(((round(min(r[1] - r[0], r[3] - r[2]), 1), tuple(round(x, 1) for x in r)) for r in bays),
                           reverse=True)
    return out


def check_acp_bays(root, mdl, bodies, limit=ACP_BAY_MAX):
    """D-135: every wall panel bay under the ACP skin at most `limit` mm clear across its short span."""
    fs = []
    for name, bays in sorted(acp_bays(bodies).items()):
        wide = [x for x in bays if x[0] > limit + 0.5]
        if not wide:
            continue
        pn = name.split()[0]
        f = next((b.file for b in bodies if WALL_FRAME.search(b.label or "") and pn in b.label), "")
        fs.append(Finding(
            "C09", "acp-bay", "%s %s" % (mdl, name), "major",
            "%s has %d bay(s) wider than %.0f mm clear under the ACP skin, the widest %.1f mm: the skin would flex "
            "over 2 mm under a 100 N push at its centre (D-135; WALL's span table: 274.8 mm clear gives 1.99 mm)."
            % (name, len(wide), limit, wide[0][0]),
            "Add a member so every bay is %.0f mm clear or less (members about 300 apart, D-135)." % limit,
            f, owner_for(f, pn), {"widest_mm": wide[0][0], "bays_over": len(wide)}))
    return fs


def _pt(p):
    return "X %.0f Y %.0f Z %.0f" % p


# ----------------------------------------------------------------- C09 per part

def load_bend_rules(root):
    p = os.path.join(root, "v2/04-Checks/config/sheet-rules.csv")
    return read_csv(p) if os.path.exists(p) else []


def _rule_for(material, rules):
    m = (material or "").lower()
    for r in rules:
        if r["match"] and re.search(r["match"], m, re.I):
            return r
    return next((r for r in rules if r["match"] in ("", "*", "default")), None)


def load_hole_rules(root):
    p = os.path.join(root, "v2/04-Checks/config/hole-rules.csv")
    return read_csv(p) if os.path.exists(p) else []


def load_edge_exceptions(root):
    """pn -> rows of v2/04-Checks/config/edge-exceptions.csv: edge distances the PM accepted for one hole size
    of one part, with the ruling. A row lets at most max_short_edges parallel edge lines sit under the
    2-diameter rule, each at least min_edge_mm from the hole centre; every other edge keeps the rule."""
    p = os.path.join(root, "v2/04-Checks/config/edge-exceptions.csv")
    out = {}
    if os.path.exists(p):
        for row in read_csv(p):
            if row.get("part_number"):
                out.setdefault(row["part_number"].strip(), []).append(row)
    return out


def _edge_accepted(rows, hole, edges, need):
    """The accepting row for this hole, or None (see load_edge_exceptions)."""
    short = [e for e in edges if e[0] + 1e-6 < need]
    ax = sf.norm(hole.axis)

    def across(p):                  # the foot seen along the hole: a plate's top and bottom edge are one edge
        t = sf.dot(sf._sub(p, hole.center), ax)
        return sf._sub(p, sf._mul(ax, t))
    lines = []
    for e in short:
        if not any(sum((across(e[2])[k] - across(f[2])[k]) ** 2 for k in range(3)) ** 0.5 < 0.5 for f in lines):
            lines.append(e)         # one edge line, however many segments or faces carry it
    for row in rows:
        if abs((num(row.get("hole_dia_mm")) or 0) - hole.diameter) > 0.05:
            continue
        lo, n_max = num(row.get("min_edge_mm")) or 0.0, int(num(row.get("max_short_edges")) or 0)
        if len(lines) <= n_max and all(e[0] + 0.05 >= lo for e in short) and \
                all(abs(abs(sf.dot(e[1], lines[0][1])) - 1.0) < 1e-3 for e in short):
            return row
    return None


# the Lead's ruling (2026-11-01, CEILING's fan bulkheads): the 2-diameter rule is for fastener holes, not openings.
# A round cut over the biggest fastener clearance, or one its part row names as an opening, is an opening, checked by
# a web rule: material of at least 2 x the sheet's thickness, and at least 3 mm, to any edge and to the next hole, as
# laser cutting needs
OPENING_DIA = 20.0          # mm: over the 5 mm key's Ø19 access hole, the biggest fastener clearance
OPENING_WEB = 3.0           # mm, laser cutting
OPENING_WORDS = re.compile(r"\b(?:openings?|bores?|cut-?outs?|vents?)\b", re.I)
DIA_IN_TEXT = re.compile(r"[\u00d8\u2300\u03a6]\s*(\d+(?:\.\d+)?)")


def is_opening(hole, row_text=""):
    """An opening (fan bore, air or cable opening), not a fastener hole: over OPENING_DIA, or a size its part's row
    names together with 'opening', 'bore', 'cut-out' or 'vent'."""
    if hole.diameter > OPENING_DIA + 1e-6:
        return True
    if row_text and OPENING_WORDS.search(row_text):
        return any(abs(float(d) - hole.diameter) <= 0.5 for d in DIA_IN_TEXT.findall(row_text))
    return False


def _opening_web_need(hole, so):
    t = hole.length if hole.length and hole.length > 0.05 else (getattr(so, "thickness", None) or 0.0)
    return max(2.0 * t, OPENING_WEB), t


def check_part_features(root, path, materials, rules, edge_factor=2.0, hole_rules=None, edge_exceptions=None,
                        row_texts=None):
    """Per-part checks on a STEP file. materials: part number -> material text."""
    fs = []
    hole_rules = hole_rules if hole_rules is not None else load_hole_rules(root)
    edge_exceptions = edge_exceptions if edge_exceptions is not None else load_edge_exceptions(root)
    s = load_step(path)
    r = rel(root, path)
    done = set()
    for inst in s.instances():
        so = s.solid(inst["solid"])
        k = (inst["part_number"], so.id)
        if k in done:
            continue
        done.add(k)
        pn = inst["part_number"]
        part = "%s %s" % (pn, (so.name or "").strip())
        # the edge-distance and spacing rules are for rigid sheet and machined parts (the owner's rule 9, "for the
        # sheet parts"): a hole near the edge of a felt, fill, foam or gasket can't tear out under load
        holes = [] if is_soft(inst.get("name") or "") or is_soft(so.name or "") else so.holes
        text = (row_texts or {}).get(pn, "")
        opening = {id(h): is_opening(h, text) for h in holes}
        for h in holes:
            edges = sf.free_edge_distances(so, h)
            if not edges:
                continue
            e = min(x[0] for x in edges)
            if opening[id(h)]:
                need, t = _opening_web_need(h, so)
                web = e - h.diameter / 2.0
                if web + 1e-6 < need:
                    fs.append(Finding(
                        "C09", "opening-web", "%s opening Ø%.1f at %s" % (part, h.diameter, _pt(h.center)), "major",
                        "Opening Ø%.2f in %s leaves %.1f mm of material to the free edge; an opening needs at least "
                        "%.1f mm (2 x the %.1f mm sheet, and 3 mm for laser cutting: the Lead's ruling, 2026-11-01). "
                        "Opening centre %s in the part's own coordinates." % (
                            h.diameter, part, web, need, t, _pt(h.center)),
                        "Leave at least %.1f mm of material round the opening, or join that edge to its neighbour "
                        "(a 3 mm rim on a free edge of a plate that carries a fan is too weak)." % need,
                        r, owner_for(r, pn), {"web_mm": round(web, 2), "dia_mm": round(h.diameter, 2)}))
                continue
            need = edge_factor * h.diameter
            if e + 1e-6 < need:
                rows = edge_exceptions.get(pn, [])
                if rows and _edge_accepted(rows, h, edges, need):
                    continue        # an edge distance the PM accepted, with its rationale
                sev = "severe" if e < 1.5 * h.diameter else "major"
                ruled = ""
                for row in rows:
                    if abs((num(row.get("hole_dia_mm")) or 0) - h.diameter) <= 0.05:
                        ruled = " %s accepts this hole only as: %s" % (row.get("ruling", "A PM ruling"),
                                                                       row.get("reason", ""))
                fs.append(Finding(
                    "C09", "edge-distance", "%s hole Ø%.1f at %s" % (part, h.diameter, _pt(h.center)), sev,
                    "Hole Ø%.2f in %s is %.1f mm from the free edge (centre to edge), %.2f diameters; the rule is at "
                    "least %g diameters (%.1f mm). Hole centre %s in the part's own coordinates.%s" % (
                        h.diameter, part, e, e / h.diameter, edge_factor, need, _pt(h.center), ruled),
                    "Move the hole to at least %.1f mm from the edge, or justify a smaller distance with a "
                    "calculation in the feature rationale." % need,
                    r, owner_for(r, pn), {"edge_mm": round(e, 2), "dia_mm": round(h.diameter, 2)}))
        # spacing between holes in the same wall
        for i, a in enumerate(holes):
            for b in holes[i + 1:]:
                if abs(abs(sf.dot(a.axis, b.axis)) - 1.0) > 1e-4:
                    continue
                if abs(sf.dot((b.center[0] - a.center[0], b.center[1] - a.center[1], b.center[2] - a.center[2]),
                              a.axis)) > 0.5:
                    continue        # different walls
                c2c = sf.line_distance(b.center, a.center, a.axis)
                if opening[id(a)] or opening[id(b)]:
                    need, t = _opening_web_need(a if opening[id(a)] else b, so)
                    web = c2c - (a.diameter + b.diameter) / 2.0
                    if 1e-3 < c2c and web + 1e-6 < need:
                        fs.append(Finding(
                            "C09", "opening-web", "%s opening web at %s and %s" % (part, _pt(a.center), _pt(b.center)),
                            "major",
                            "Ø%.2f and Ø%.2f in %s leave %.1f mm of material between them; next to an opening that "
                            "needs at least %.1f mm (2 x the %.1f mm sheet, and 3 mm for laser cutting: the Lead's "
                            "ruling, 2026-11-01)." % (a.diameter, b.diameter, part, web, need, t),
                            "Space them to leave at least %.1f mm of material." % need,
                            r, owner_for(r, pn), {"web_mm": round(web, 2)}))
                    continue
                need = 2.0 * max(a.diameter, b.diameter)
                if 1e-3 < c2c < need:
                    fs.append(Finding(
                        "C09", "hole-spacing", "%s holes at %s and %s" % (part, _pt(a.center), _pt(b.center)), "major",
                        "Holes Ø%.2f and Ø%.2f in %s are %.1f mm apart centre to centre, under 2 diameters (%.1f mm), "
                        "leaving %.1f mm of material between them." % (
                            a.diameter, b.diameter, part, c2c, need, c2c - (a.diameter + b.diameter) / 2.0),
                        "Space the holes at least %.1f mm apart or merge them into a slot." % need,
                        r, owner_for(r, pn), {"c2c_mm": round(c2c, 2)}))
        # sheet-metal bends
        if so.bends:
            mat = materials.get(pn, "")
            rule = _rule_for(mat, rules)
            kmin = num(rule["min_inner_radius_t"]) if rule else 1.0
            hb_t = num(rule.get("hole_to_bend_t")) if rule else 2.0
            for bd in so.bends:
                t = bd.thickness
                if bd.inner_radius + 1e-6 < kmin * t:
                    fs.append(Finding(
                        "C09", "bend-radius", "%s bend at %s" % (part, _pt(bd.axis_point)), "severe",
                        "Bend inner radius %.2f mm in %s (%s, t %.2f) is under the minimum %.2f x t = %.2f mm (%s)." % (
                            bd.inner_radius, part, mat or "material not in a parts list", t, kmin, kmin * t,
                            (rule or {}).get("status_source", "default 1.0 x t, assumption")),
                        "Raise the inner bend radius to at least %.2f mm or change the material or temper." % (kmin * t),
                        r, owner_for(r, pn), {"r_mm": round(bd.inner_radius, 2), "t_mm": t}))
                for h in holes:
                    d = sf.hole_to_bend(h, bd)
                    if d is None:
                        continue
                    need = hb_t * t + bd.inner_radius
                    if d < need - 1e-6 and d > -h.diameter:
                        fs.append(Finding(
                            "C09", "hole-to-bend", "%s hole Ø%.1f at %s" % (part, h.diameter, _pt(h.center)), "major",
                            "Hole Ø%.2f in %s has %.1f mm from its edge to the bend; the rule is %.1f x t + r = %.1f mm "
                            "(t %.2f, r %.2f; %s). The hole will distort when the part is bent." % (
                                h.diameter, part, d, hb_t, need, t, bd.inner_radius,
                                (rule or {}).get("status_source", "assumption")),
                            "Move the hole at least %.1f mm from the bend or add a relief cut." % need,
                            r, owner_for(r, pn), {"hole_to_bend_mm": round(d, 2)}))
    return fs
