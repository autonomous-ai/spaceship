"""The kick strip's hinge end and its brush seal through the door's swing (plan view, from the floor to Z 105), for
the hinge pivots the HOLD hinge might have (PM ruling 2026-11-01: show that the brush only wipes BASE's plate and
never binds before it is named).

    python3 v2/01-CAD-Native/front/door_swing.py [--overlap 2] [--swing 110]

Reads the door's own parameters (door_unit.py, through the drawing specs' evaluator), so it follows the model: the
kick strip's hinge end (X kick_x0) and depth (glass line +/- kick_d / 2), DL's door face (XL + dl_w), where BASE welds
its 2 mm plate into FL2's door end (the Lead's ruling of 2026-11-01), running from FL2's inner face (Y -802.6,
BASE's) inward to the strip's back line. The brush's carrier sits on the strip's end face and its pile tips reach
`overlap` past the plate's face, pressed.

The door opens outward (-Y). For a pivot P and an opening angle t, each point turns about P. Checked for each pivot,
from shut to the full swing in 0.25 deg steps:
- the gap between the strip's end face and the plate never drops below its closed value (the pile is never squeezed
  harder than when the door is shut: it can't bind);
- while a pile tip still reaches the plate's face, how far it moves past the plate's edges (it should only wipe the
  face);
- the angle at which every tip has left the plate.
For each pivot X, the script finds the pivot Y closest to the glass that keeps the gap: the hinge must have its pivot
at least that far out (a condition for the HOLD hinge as much as for the brush: inside it, the strip's own corner
would reach the plate).
"""
import argparse
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "02-Drawings", "front"))
import drawing_specs as DS  # noqa: E402

FL2_INNER_Y = -802.6     # BASE: FL2's inner face, where its door-end plate starts (BASE Engineer, 2026-11-01)


def geometry():
    v = DS.V_DOOR
    return {"x_end": v["kick_x0"], "y_out": -v["glass_y"] - v["kick_d"] / 2, "y_in": -v["glass_y"] + v["kick_d"] / 2,
            "x_plate": -v["pod_w"] / 2 + v["dl_w"], "py0": FL2_INNER_Y, "py1": -v["glass_y"] + v["kick_d"] / 2}


def turn(p, c, t):
    """p turned about c by the opening angle t (radians): a point right of the pivot moves to -Y."""
    dx, dy = p[0] - c[0], p[1] - c[1]
    return (c[0] + dx * math.cos(t) + dy * math.sin(t), c[1] - dx * math.sin(t) + dy * math.cos(t))


def sweep(g, pivot, overlap, swing):
    """(smallest gap strip end to plate, largest pass of a tip past a plate edge while touching, release angle)."""
    corners = [(g["x_end"], g["y_out"]), (g["x_end"], g["y_in"])]
    tips = [(g["x_plate"] - overlap, y) for y in (g["y_out"], (g["y_out"] + g["y_in"]) / 2, g["y_in"])]
    gap, edge, release = 1e9, 0.0, None
    for i in range(int(swing * 4) + 1):
        t = math.radians(i / 4.0)
        gap = min(gap, min(turn(p, pivot, t)[0] for p in corners) - g["x_plate"])
        on = [q for q in (turn(p, pivot, t) for p in tips) if q[0] <= g["x_plate"] + 1e-9]
        for q in on:
            edge = max(edge, q[1] - g["py1"], g["py0"] - q[1])
        if not on and release is None:
            release = i / 4.0
    return gap, edge, release


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--overlap", type=float, default=2.0)
    ap.add_argument("--swing", type=float, default=110.0)
    a = ap.parse_args(argv)
    g = geometry()
    shut = g["x_end"] - g["x_plate"]
    print("kick strip's hinge end X %.1f, Y %.1f to %.1f; plate face X %.1f, Y %.1f to %.1f; slot %.1f; pile tips %.1f past "
          "the plate; swing 0 to %.0f deg" % (g["x_end"], g["y_out"], g["y_in"], g["x_plate"], g["py0"], g["py1"], shut,
                                              a.overlap, a.swing))
    rows = []
    for px in (-990.0, -985.0, -980.0, -976.0, -972.0, -968.0, -964.0, g["x_end"], -950.0, -940.0):
        best, py = None, -770.0
        while py <= g["y_in"]:
            gap, edge, rel = sweep(g, (px, py), a.overlap, a.swing)
            if gap >= shut - 1e-6:
                best = (py, edge, rel)
            py += 0.25
        rows.append((px, best))
        if best:
            print("pivot X %7.1f: the gap holds for pivot Y %7.2f or further out (%.2f outside the strip's outside face); "
                  "there the tips pass a plate edge by %.2f and let go at %.1f deg" % (
                      px, best[0], g["y_out"] - best[0], best[1], best[2] if best[2] is not None else float("nan")))
        else:
            print("pivot X %7.1f: no pivot Y keeps the gap" % px)
    return rows


if __name__ == "__main__":
    main()
