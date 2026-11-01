"""Offline checks of the FRONT drawing specs, before any Fusion run (no Fusion needed).

    python3 v2/02-Drawings/front/check_drawing_specs.py [drawing ...]

For each drawing in drawing_specs.py (all of them when none is named):
- no dimension placed twice: two dimensions that measure the same model extent along the same axis, in one view or
  two (make_drawing_front.py skips the second at run time too, on the snapped points; this finds them in the spec);
- no closed chain: an extent that other dimensions on the same axis already give end to end (ISO 129-1: no more
  dimensions than needed; one of the chain would be the same dimension again);
- the views clear the notes and title images at their real size (IMG_W wide, the height from the rendered PNG) and
  each other, and stay on the sheet. A view's size is its model box times its scale; an iso view's is estimated from
  the 3D box the other views give (width (dx + dy) cos 30, height (dx + dy) sin 30 + dz), so it is a guide only.
Exit 0 clean, 1 when something is found.
"""
import importlib.util
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("front_drawing_specs_check", os.path.join(HERE, "drawing_specs.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

VIEW_AXES = {"front": (("X", 1), ("Z", 1)), "top": (("X", 1), ("Y", 1)), "left": (("Y", -1), ("Z", 1))}
PX_MM = 10.0          # render_notes.py's resolution
CLEAR = 3.0           # mm kept between a view and an image or another view


def measure_key(vk, side, a, b):
    if vk not in VIEW_AXES:
        return None
    k = 0 if side in ("below", "above") else 1
    axis, sign = VIEW_AXES[vk][k]
    lo, hi = sorted((sign * a[k], sign * b[k]))
    return axis, round(lo, 1), round(hi, 1)


def _chain(lo, hi, ivs, depth=0):
    """Dimensions (indices) that run end to end from lo to hi, two or more of them; None if there is no such chain."""
    for a, b, j in ivs:
        if abs(a - lo) < 0.05 and b < hi - 0.05:
            rest = _chain(b, hi, [iv for iv in ivs if iv[2] != j], depth + 1)
            if rest:
                return [j] + rest
        if abs(a - lo) < 0.05 and abs(b - hi) < 0.05 and depth > 0:
            return [j]
    return None


def png_h_mm(path):
    with open(path, "rb") as fh:
        head = fh.read(24)
    return int.from_bytes(head[20:24], "big") / PX_MM


def box3(sp):
    """The 3D model box (x0, x1, y0, y1, z0, z1) from the views' 2D boxes, None where no view gives an axis."""
    out = {}
    for vk, (u0, v0, u1, v1) in sp.get("box", {}).items():
        if vk not in VIEW_AXES:
            continue
        for (axis, sign), (lo, hi) in zip(VIEW_AXES[vk], ((u0, u1), (v0, v1))):
            lo, hi = sorted((sign * lo, sign * hi))
            out.setdefault(axis, (lo, hi))
    return out


def view_rects(sp):
    rects = {}
    b3 = box3(sp)
    for vk, (cx, cy) in sp["views"].items():
        sc = sp["scales"].get(vk, sp["scale"])
        if vk in sp.get("box", {}) and vk in VIEW_AXES:
            u0, v0, u1, v1 = sp["box"][vk]
            w, h = abs(u1 - u0) * sc, abs(v1 - v0) * sc
        elif vk == "iso" and all(k in b3 for k in "XYZ"):
            dx, dy, dz = (b3[k][1] - b3[k][0] for k in "XYZ")
            w = (dx + dy) * math.cos(math.radians(30)) * sc
            h = ((dx + dy) * math.sin(math.radians(30)) + dz) * sc
        else:
            continue
        rects[vk] = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    return rects


def overlap(a, b, gap):
    return a[0] < b[2] + gap and b[0] < a[2] + gap and a[1] < b[3] + gap and b[1] < a[3] + gap


def check(key):
    sp = S.SPECS[key]
    found = []
    seen = {}
    for i, (vk, a, b, side, gap) in enumerate(sp.get("dims", [])):
        k = measure_key(vk, side, a, b)
        if k is None:
            continue
        if k in seen:
            found.append("dimension %d (%s %s to %s) measures %s %.1f to %.1f again, as dimension %d in %s" % (
                i, vk, a, b, k[0], k[1], k[2], seen[k][0], seen[k][1]))
        else:
            seen[k] = (i, vk)
    by_axis = {}
    for k, (i, vk) in seen.items():
        by_axis.setdefault(k[0], []).append((k[1], k[2], i))
    for axis, ivs in by_axis.items():
        for lo, hi, i in ivs:
            chain = _chain(lo, hi, [(a, b, j) for a, b, j in ivs if j != i])
            if chain:
                found.append("dimension %d (%s %.1f to %.1f) closes a chain with dimensions %s" % (
                    i, axis, lo, hi, ", ".join(str(j) for j in chain)))
    sw, sh = S.SHEETS[sp["sheet"]]
    imgs = {}
    for name in ("notes", "title"):
        path = os.path.join(HERE, ".notes", "%s_%s.png" % (sp["drawing"], name.upper()))
        if os.path.exists(path):
            x0, ytop = sp["images"][name]
            imgs[name] = (x0, ytop - png_h_mm(path), x0 + S.IMG_W, ytop)
        else:
            found.append("no %s image yet (run render_notes.py)" % name)
    rects = view_rects(sp)
    for vk, r in rects.items():
        if r[0] < 10 or r[1] < 10 or r[2] > sw - 10 or r[3] > sh - 10:
            found.append("view %s %s runs off the sheet's 10 mm border" % (vk, tuple(round(x) for x in r)))
        for name, ir in imgs.items():
            if overlap(r, ir, CLEAR):
                found.append("view %s %s overlaps the %s image %s" % (vk, tuple(round(x) for x in r), name,
                                                                     tuple(round(x) for x in ir)))
    ks = list(rects)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            if overlap(rects[ks[i]], rects[ks[j]], CLEAR):
                found.append("views %s and %s overlap" % (ks[i], ks[j]))
    if "notes" in imgs and "title" in imgs and overlap(imgs["notes"], imgs["title"], 1.0):
        found.append("the notes and title images overlap")
    return found


def main(argv):
    keys = argv or list(S.ORDER)
    bad = 0
    for key in keys:
        found = check(key)
        print("%-10s %s" % (key, "ok" if not found else "%d finding(s)" % len(found)))
        for f in found:
            print("    " + f)
        bad += bool(found)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
