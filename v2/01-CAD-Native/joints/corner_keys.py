"""Corner key positions for the base band (joints register J-BASE-02, D-87).

Writes corner-keys.csv next to this file: one row per key (6 per pod), in pod
coordinates (conventions §4, mm), so BASE can place the keys, drill the fixing
holes and cut the keyholes, and the CAD build can check its cut angles.

    python3 v2/01-CAD-Native/joints/corner_keys.py          # write the CSV
    python3 v2/01-CAD-Native/joints/corner_keys.py --check  # fail if the CSV is stale

Inputs (status in brackets):
- Band: band_h x band_t tube (skeleton P04, 100 x 40), 1.5 wall (D-86), its bottom at
  glide_h (Z 10) on preset glides [source / decided]; read from the skeleton's CSV.
- Back band centre line pod_d / 2 - band_t / 2 (Y +830), its ends at pod_w / 2 - band_t
  (X -/+1210) against the side bands' inner walls (skeleton P04) [calculation].
- D-129 (PM ruling 2026-11-01, the pallet 2 re-plan): at the two back corners the side bands
  carry the keys, each against its inner wall from inside, with the stud bolts through that
  1.5 wall; the back band, lowered between both side bands' studs at once, takes them in one
  open slot at each end cap (its keyholes can't work: the band can't slide sideways onto
  studs at both ends). Going down, a cap meets the studs with its bottom edge, so the slot
  opens there and runs up past both studs; the heads come up into the tube through a notch
  in its bottom wall (BASE's fit check, 2026-11-01) [decided; the slot and notch PROPOSED].
- Front pieces: BASE's outer-face points, relayed by the PM on 2026-10-31 [source].
- Key: 35 wide, 75 tall, 30 long on its centre line, its stud face cut at the
  carrier's mitre; studs 26 and 60 above its bottom. Fixing holes, two M6 in its bottom,
  each with an 838010 flanged button head (flange up to 13.6) through a 7.0 hole in the
  carrier's bottom wall (this register, PROPOSED; the PM's ruling of 2026-11-01: no edge
  exception, every 7.0 hole at least 14 from the carrier's cut end, the screws at least
  14 apart):
  - 111212, 111213, 111214 and 111215 (FR1): 10.5 from the back face, 7.0 either side of
    the centre line;
  - 111211 (the back corners): 6.0 either side of the centre line, the +y one 10.5 from
    the back face and the -y one 17.8 (stepped 7.3), so each stays 14.0 from the side
    band's back end at Y 850 with the key turned either way. At FR1 that stepped hole
    would be 12.2 from the rail's end, so FR1 keeps the first layout under its own
    number, 111215.

Sign of the cut: in the key's own frame (x along the carrier toward the joint,
z up, y = z cross x, so y points to the left of x), a positive cut makes the
key longer on its +y side. The long side is always on the outside of the turn.
"""
import csv
import glob
import io
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "corner-keys.csv")
SKELETON_DIR = os.path.join(HERE, "..", "skeleton")


def skeleton():
    """{name: value in mm} from the highest skeleton parameter CSV (the named values, not our own numbers)."""
    found = glob.glob(os.path.join(SKELETON_DIR, "100000_P[0-9][0-9]_POD-SKELETON-PARAMETERS.csv"))
    path = max(found, key=lambda f: os.path.basename(f)[7:10])
    with open(path, newline="", encoding="utf-8") as fh:
        rows = {r["parameter"].strip(): r for r in csv.DictReader(fh)}
    return {k: float(r.get("value") or r.get("value_mm")) for k, r in rows.items()
            if (r.get("value") or r.get("value_mm") or "").replace(".", "", 1).replace("-", "", 1).isdigit()}


SK = skeleton()
BAND_T = SK["band_t"]          # skeleton band_t: the band's depth across (source)
BAND_BOTTOM_Z = SK["glide_h"]  # skeleton glide_h: the band's bottom on its preset glides
BAND_WALL = 1.5                # D-86 (decided)
BACK_Y = SK["pod_d"] / 2 - SK["band_t"] / 2      # back band centre line, Y +830
BACK_X = SK["pod_w"] / 2 - SK["band_t"]          # back band ends against the side bands, X -/+1210
KEY_LEN = 30.0         # PROPOSED: keeps the carrier's Ø7.0 holes 2 x 7 from its cut end
STUD_Z = (26.0, 60.0)  # above the key's bottom, PROPOSED
KEYHOLE_DROP = 10.0    # the moving piece is lowered 10 onto the studs (D-87)
SLOT_ABOVE = 2.0       # an open slot ends this far above the upper stud, so the band sits on its glides (PROPOSED)
NOTCH = (12.0, 9.0)    # the head notch in the back band's bottom wall: wide (the Ø10 head and 1 each side), deep
                       # from the end (the head's far face is 1.8 + 6 = 7.8 from the side band's face) (PROPOSED)
HEAD_GAP = 1.8         # each stud bolt's head off the face it stands from: the 1.5 plate and 0.3 (PROPOSED)
BOLT_LEN = 16.0        # 838001, M6 x 16 (joints register H-01)
FIX = {                # fixing holes in the key's frame: (x from its back face, y from its centre line), PROPOSED
    "111211": ((10.5, 6.0), (17.8, -6.0)),     # back corners: 14.0 from Y 850 either way round, 14.05 apart
    "other": ((10.5, 7.0), (10.5, -7.0)),      # 10.5 from the back and the side faces (C09), 14 apart
}
TAP = 5.03             # the key's M6 tap drill: C09 wants 2 x it from every face of the key
FIX_HOLE = 7.0         # the carrier's clearance hole: 2 x it from the carrier's cut end (PM ruling)
FLANGE = 13.6          # 838010's flange, at most: the screws stay at least 14 apart (PM ruling)
KEY_W = 35.0


def unit(v):
    n = math.hypot(v[0], v[1])
    return (v[0] / n, v[1] / n)


def left(u):
    """z cross u: the key's +y."""
    return (-u[1], u[0])


def mitre_centre(outer, u_in, u_out):
    """Centre of a mitre between two band pieces, from the outer-face corner.

    u_in is the carrier's direction toward the joint, u_out the next piece's
    direction away from it. The inner corner lies BAND_T / cos(turn / 2) from the
    outer one along the bisector of the two inward normals."""
    turn = math.atan2(u_in[0] * u_out[1] - u_in[1] * u_out[0], u_in[0] * u_out[0] + u_in[1] * u_out[1])
    # inward normal: toward the pod's inside, the side the band turns to
    side = 1.0 if turn > 0 else -1.0
    n_in = (side * left(u_in)[0], side * left(u_in)[1])
    n_out = (side * left(u_out)[0], side * left(u_out)[1])
    b = unit((n_in[0] + n_out[0], n_in[1] + n_out[1]))
    d = BAND_T / math.cos(turn / 2.0)
    inner = (outer[0] + d * b[0], outer[1] + d * b[1])
    return ((outer[0] + inner[0]) / 2.0, (outer[1] + inner[1]) / 2.0), inner, math.degrees(turn)


def joints():
    """(part, joint, carrier, keyhole piece, face centre, carrier direction, cut deg, source)."""
    rows = []
    # back corners (D-129): square, each key in a side band's back end with its stud face against the side
    # band's inner wall from inside, so its face is the wall's inner face, 1.5 in from X -/+1210; the studs
    # point into the pod, through the wall, into the back band's end caps (skeleton P04)
    rows.append(("111211", "back left corner", "left side band 111101, back end, against its inner wall",
                 "back band 111103, end cap at its left end", (-BACK_X - BAND_WALL, BACK_Y), (1.0, 0.0), 0.0,
                 "skeleton P04: pod_w / 2 - band_t, pod_d / 2 - band_t / 2; D-129"))
    rows.append(("111211", "back right corner", "right side band 111102, back end, against its inner wall",
                 "back band 111103, end cap at its right end", (BACK_X + BAND_WALL, BACK_Y), (-1.0, 0.0), 0.0,
                 "skeleton P04: pod_w / 2 - band_t, pod_d / 2 - band_t / 2; D-129"))
    # FL corner: left side band (heading -Y) turns onto FL1 toward the knee
    fl1_dir = unit((-1158.0 - -1250.0, -752.0 - -670.0))
    c, inner, turn = mitre_centre((-1250.0, -670.0), (0.0, -1.0), fl1_dir)
    rows.append(("111212", "front left corner (LH)", "left side band 111101, front end",
                 "FL1, end cap at the corner", c, (0.0, -1.0), -turn / 2.0,
                 "BASE: outer (-1250, -670), inner (-1210, -652.07), turn 48.29"))
    # knee: FL1 turns onto FL2
    fl2_dir = unit((-979.0 - -1158.0, -844.0 - -752.0))
    c2, inner2, turn2 = mitre_centre((-1158.0, -752.0), fl1_dir, fl2_dir)
    rows.append(("111214", "front left knee", "FL1, knee end", "FL2, end cap at the knee",
                 c2, fl1_dir, -turn2 / 2.0, "BASE: outer (-1158, -752), turn 14.51"))
    # FR corner: right side band (heading -Y) turns onto the intake piece's corner facet
    # (BASE: turn 48.04 to the right, inner corner (1210, -654.17))
    a = math.radians(-90.0 - 48.04)
    fr_dir = (math.cos(a), math.sin(a))
    c3, inner3, turn3 = mitre_centre((1250.0, -672.0), (0.0, -1.0), fr_dir)
    rows.append(("111213", "front right corner (RH)", "right side band 111102, front end",
                 "intake support rail, end cap at the corner", c3, (0.0, -1.0), -turn3 / 2.0,
                 "BASE: outer (1250, -672), inner (1210, -654.17), turn 48.04"))
    # inline: the intake support rail's end at X 915 meets FR1, square (FR1: Y -850 to -810).
    # BASE rulings 2026-11-01 (relayed by the PM): moved from X 947 to X 920 to keep the intake
    # mesh fully open, then to X 915 (a 32 mm stub) for the 30 mm key; FR1 runs X 218 to 915
    rows.append(("111215", "front right inline (X 915)", "intake support rail, end at X 915",
                 "FR1, end cap at X 915", (915.0, -830.0), (-1.0, 0.0), 0.0,
                 "BASE ruling 2026-11-01: FR1 X 218 to 915, Y -850 to -810, square cut (stub 32)"))
    checks = {"FL inner corner": (inner, (-1210.0, -652.07)), "FR inner corner": (inner3, (1210.0, -654.17))}
    return rows, checks, (turn, turn2, turn3)


def check_holes(pn, joint, face, u, cut, src, holes):
    """The PM's rules for the fixing holes, checked, not assumed: each 7.0 hole at least 14 from the carrier's cut
    end (the side band's back end at the back corners, the stud face's line elsewhere), the screws at least 14
    apart, and every tapped hole 2 x its drill from every face of the key (C09)."""
    (x1, y1), (x2, y2) = holes
    if math.hypot(x2 - x1, y2 - y1) < 14.0 - 1e-6:
        raise SystemExit("%s %s: fixing screws %.2f apart, under 14" % (pn, joint, math.hypot(x2 - x1, y2 - y1)))
    a = math.radians(cut)
    yv = left(u)
    nf = (math.cos(a) * u[0] - math.sin(a) * yv[0], math.cos(a) * u[1] - math.sin(a) * yv[1])
    for hx, hy in holes:
        if "D-129" in src:                       # the side band's back end, square across it
            end = SK["pod_d"] / 2 - hy
        else:                                    # the carrier ends at the stud face
            end = (face[0] - hx) * nf[0] + (face[1] - hy) * nf[1]
        if end < 2 * FIX_HOLE - 1e-6:
            raise SystemExit("%s %s: a 7.0 hole %.2f from the carrier's end, under 14" % (pn, joint, end))
    bx, by = face[0] - KEY_LEN * u[0], face[1] - KEY_LEN * u[1]
    for hx, hy in holes:
        kx = (hx - bx) * u[0] + (hy - by) * u[1]          # in the key's frame
        ky = (hx - bx) * yv[0] + (hy - by) * yv[1]
        face_d = (KEY_LEN - kx) * math.cos(a) - ky * math.sin(a)   # to the cut stud face, square to it
        for what, d in (("back", kx), ("side", KEY_W / 2 - abs(ky)), ("stud face", face_d)):
            if d < 2 * TAP - 1e-6:
                raise SystemExit("%s %s: tapped hole %.2f from the key's %s, under 2 x %.2f" % (pn, joint, d, what, TAP))


def build():
    rows, checks, turns = joints()
    for name, (got, want) in checks.items():
        if math.hypot(got[0] - want[0], got[1] - want[1]) > 0.05:
            raise SystemExit("%s: %s against BASE's %s" % (name, got, want))
    out = io.StringIO()
    w = csv.writer(out, lineterminator="\n")
    w.writerow(["part_number", "joint", "carrier_key_in_its_end", "keyhole_piece", "cut_deg_signed",
                "face_centre_x", "face_centre_y", "carrier_dir_x", "carrier_dir_y",
                "stud_normal_x", "stud_normal_y", "key_back_centre_x", "key_back_centre_y",
                "key_bottom_z", "key_top_z", "stud_z_low", "stud_z_high",
                "keyhole_entry_z_low", "keyhole_entry_z_high",
                "fix_hole_1_x", "fix_hole_1_y", "fix_hole_2_x", "fix_hole_2_y",
                "hook", "slot_end_z", "head_notch", "stud_bolts_through", "head_gap", "bolt_engagement", "status",
                "source"])
    z0 = BAND_BOTTOM_Z + BAND_WALL
    for pn, joint, carrier, partner, (cx, cy), u, cut, src in rows:
        y = left(u)
        a = math.radians(cut)
        # stud face's outward normal in the key frame is (cos a, -sin a)
        n = (math.cos(a) * u[0] - math.sin(a) * y[0], math.cos(a) * u[1] - math.sin(a) * y[1])
        bx, by = cx - KEY_LEN * u[0], cy - KEY_LEN * u[1]
        f1, f2 = [(bx + hx * u[0] + hy * y[0], by + hx * u[1] + hy * y[1]) for hx, hy in FIX.get(pn, FIX["other"])]
        check_holes(pn, joint, (cx, cy), u, cut, src, (f1, f2))
        s1, s2 = z0 + STUD_Z[0], z0 + STUD_Z[1]
        open_slot = "D-129" in src           # the back band goes straight down onto both side bands' studs
        if open_slot:
            hook = ("open slot: one 6.5 slot from the end cap's bottom edge, 12 wide at its mouth, up past both "
                    "studs; the band is lowered straight down between the side bands")
            entries = ("", "")
            notch = "%g wide, %g deep from the end, in the bottom wall on the band's centre line" % NOTCH
            through = "the side band's inner wall, 1.5: a 7.0 hole at each stud"
            engage = BOLT_LEN - BAND_WALL - HEAD_GAP
        else:
            hook = "keyhole: a 12 entry 10 below each stud, a 6.5 slot up to it; on along the studs, then down 10"
            entries = ("%.1f" % (s1 - KEYHOLE_DROP), "%.1f" % (s2 - KEYHOLE_DROP))
            notch = ""
            through = ""
            engage = BOLT_LEN - HEAD_GAP
        w.writerow([pn, joint, carrier, partner, "%.2f" % cut, "%.2f" % cx, "%.2f" % cy,
                    "%.4f" % u[0], "%.4f" % u[1], "%.4f" % n[0], "%.4f" % n[1],
                    "%.2f" % bx, "%.2f" % by, "%.1f" % z0, "%.1f" % (z0 + 75.0),
                    "%.1f" % s1, "%.1f" % s2, entries[0], entries[1],
                    "%.2f" % f1[0], "%.2f" % f1[1], "%.2f" % f2[0], "%.2f" % f2[1],
                    hook, ("%.1f" % (s2 + SLOT_ABOVE)) if open_slot else "", notch, through, "%.1f" % HEAD_GAP,
                    "%.1f" % engage, "PROPOSED; positions calculation", src])
    return out.getvalue(), turns


def main():
    text, turns = build()
    if "--check" in sys.argv:
        with open(OUT) as f:
            if f.read() != text:
                raise SystemExit("corner-keys.csv is stale: run corner_keys.py")
        print("corner-keys.csv is current")
        return
    with open(OUT, "w") as f:
        f.write(text)
    print("wrote %s (turns: FL %.2f, knee %.2f, FR %.2f deg)" % (os.path.relpath(OUT), *turns))


if __name__ == "__main__":
    main()
