"""Spaceship (FocusPod v2) CEILING: parameters and layout, without Fusion.

The Fusion build (`ceiling_build.py`), the offline tests and the exports
(parts list, cut list, flat pattern check) all read this file, so the layout
is written once.

Parameters come from two places:

1. The pod skeleton (the highest revision in `../skeleton/`, P04 as updated in
   place by PR #58), loaded at build time with its own names, expressions,
   statuses and sources: skin_t, bond_t, frame_t, outer_t, half_pw (skin width),
   half_fw (frame width), close_gap, ceil_bolt_z, bolt_edge_inset, spigot_inset
   and the rest. No skeleton number is copied here.
2. The ceiling's own parameters (`CEILING_PARAMS` below), written as
   expressions of the skeleton's. Each carries its status and source
   (conventions.md section 9).

Coordinates (conventions.md section 4): pod origin on the room floor at the
pod centre, +X right (seen from outside, facing the door), +Y back, +Z up.
The ceiling cassette is one part for both halves (COMMON, PM ruling
2026-10-31); it has its own system CS-510301, see `CASSETTE_CS`.
"""

import csv
import glob
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REV = "P01"


def current_skeleton_csv():
    """The skeleton's parameter list with the highest revision in ../skeleton/."""
    found = glob.glob(os.path.join(HERE, "..", "skeleton", "100000_P[0-9][0-9]_POD-SKELETON-PARAMETERS.csv"))
    if not found:
        raise FileNotFoundError("no skeleton parameter CSV next to the ceiling folder")
    path = max(found, key=lambda f: os.path.basename(f)[7:10])
    return os.path.abspath(path), os.path.basename(path)[7:10]


SKELETON_CSV, SKELETON_REV = current_skeleton_csv()


def use_skeleton(path):
    """Point the model at another skeleton parameter list (for a test build against an
    open skeleton PR); returns its revision."""
    global SKELETON_CSV, SKELETON_REV
    SKELETON_CSV = os.path.abspath(path)
    SKELETON_REV = os.path.basename(path)[7:10]
    return SKELETON_REV

# Ceiling parameters the skeleton may take over; the skeleton's own then wins.
SKELETON_MAY_DEFINE = {"seam_gap"}

PM_RULING = "PM ruling on the CEILING plan, 2026-10-31"

# name, expression, unit ("mm" or "" for a count), status, source.
# A parameter may use only the skeleton's parameters and the ones above it.
CEILING_PARAMS = [
    # ---- outer panel C1 / C2: frame and skin (D-16, D-34, D-42, D-55)
    ("seam_gap", "2.26 mm", "mm", "confirmed",
     "PM ruling 2026-10-31 (Fusion group): the Joints Engineer's 2.26 mm, set by a metal stop washer, on every frame-to-frame seam; the skeleton's own value replaces this one once it carries it"),
    ("tube_w", "20 mm", "mm", "confirmed", "D-34, D-54: aluminium 20 x 40 x 1.2 members (the 20 mm face lies in the plane of the panel)"),
    ("tube_t", "1.2 mm", "mm", "confirmed", "D-54: the frames stay 1.2 mm (rivnut grip check passed); D-85 keeps the ceiling's cross members at 1.2 too, since they carry the overhead clips and catches (T07, T08 test on 1.2)"),
    ("back_w", "40 mm", "mm", "confirmed",
     "R-J3 (joints register 2.4): the ceiling's back member is 40 x 40, so the back panel's top tube overlaps it by 34 and its rivnuts sit on a 40 mm face"),
    ("fr_n", "3", "", "confirmed", PM_RULING + ": 3 cross members between the side and seam members"),
    ("fr_pitch", "(wall_depth - tube_w) / (fr_n + 1)", "mm", "calculation",
     "centre spacing of the cross members, front member to back member: (1495 - 20) / 4 = 368.75, 400 or less (D-16)"),
    # ---- site joints (joints register V2-ENG-JNT-01; the register owns the bolt lines, PM ruling 2026-10-31)
    ("hole_clr", "7 mm", "mm", "confirmed", "R-J6 (joints register 2.9): bolt clearance hole, positioned to +/-0.2 from the spigot hole"),
    ("hole_acc", "19 mm", "mm", "confirmed", "joints register 2.2, 2.9: access hole, so the 18 mm head washer goes in with the bolt"),
    ("hole_rvn", "9.53 mm", "mm", "source", "H-03 Sherex CAH3-610-4.2 rivnut: hole 9.53 +0.10 (joints register 2.1, SHX)"),
    ("spig_hole", "8.5 mm", "mm", "confirmed", "R-J13: spigot hole 8.5, round at one end of the edge, an 8.5 x 14 slot along it at the other"),
    ("spig_slot", "14 mm", "mm", "confirmed", "R-J13: the spigot slot's length along the edge (+/-2.75 of travel for the 8 mm spigot)"),
    ("lead_in", "1 mm", "mm", "confirmed", "R-J9 (joints register 2.10): 1 x 45 deg lead-in on the lower edges of the C1-C2 faces, so C2 drops past C1 without catching the seal"),
    ("cj_side_y0", "pod_d / 2 - wall_depth + bolt_edge_inset", "mm", "confirmed",
     "PM ruling 2026-10-31 (the register owns the bolt lines): J-CEIL-01 side edges run along the ceiling from its front end, first bolt 220 in (Y -425; joints register 2.9)"),
    ("cj_side_pitch", "(wall_depth - 2 * bolt_edge_inset) / (n_ceil_side_bolt - 1)", "mm", "calculation",
     "J-CEIL-01 side edges along the ceiling's 1495: 351.67 (joints register 2.9)"),
    ("cj_back_n", "4", "", "confirmed",
     "PM correction 2026-10-31: 4 bolts per back panel, as the joints register 3.5 (16 on the ceiling's edges); the skeleton's n_ceil_back_bolt (3) is being corrected"),
    ("cj_back_x0", "close_gap / 2 + bolt_edge_inset", "mm", "calculation",
     "J-CEIL-01 back edges on the frame (PM ruling 2026-10-31): first bolt 220 in from the frame's centre-seam end (|X| 222.75; joints register 2.9)"),
    ("cj_back_pitch", "(half_fw - 2 * bolt_edge_inset) / (cj_back_n - 1)", "mm", "calculation",
     "J-CEIL-01 back edges along the 1198.99 frame: 253.00 (joints register 2.9)"),
    ("cj_back_y", "pod_d / 2 - outer_t + frame_t / 2", "mm", "confirmed",
     "R-J15 (joints register 2.4): the back edges' bolt line on the back panel's top tube centre (Y +824)"),
    ("cj_pin_n", "4", "", "confirmed", "J-CEIL-02 (joints register 3.6): 4 pins at the 220 mm rule along the C1-C2 seam"),
    ("cj_pin_pitch", "(wall_depth - 2 * bolt_edge_inset) / (cj_pin_n - 1)", "mm", "calculation",
     "J-CEIL-02 pins along the ceiling's 1495 from Y -645 + 220, as the side edges (joints register 2.9)"),
    ("cj_spig_x0", "close_gap / 2 + spigot_inset", "mm", "calculation",
     "R-J13: spigots 100 in from each frame end. The round hole sits at the centre-seam end, since ST-04 runs from the round hole to the closing face (+/-0.1); the slot at the side end lets the side bolts pull C1 and C2 onto their stops"),
    ("cj_spig_x1", "close_gap / 2 + half_fw - spigot_inset", "mm", "calculation", "R-J13: the slot 100 in from the frame's side end"),
    # ---- soffit hangers (D-87: the soffit hangs on tool-free hooks; PROPOSED by CEILING/AIR 2026-11-01)
    ("x1_ov", "16 mm", "mm", "confirmed",
     "PM ruling 2026-11-01 (D-87 hooks): cross member X1 sits this far over the soffit's back edge, so the soffit's back hangers have a member above them; its back face stays over the cassette for the clips"),
    ("hang_x", "inner_w / 4", "mm", "calculation", "PM ruling 2026-11-01: soffit keyhole studs at the middle of each ceiling half's front member and X1 (clear of the clips, the catches and the roof slot)"),
    ("lock_x", "inner_w / 2 - 66 mm", "mm", "assumption",
     "PM ruling 2026-11-01: two captive screws (5 mm key) lock the soffit, so taking a cassette out can never free it; both in C1's front member over the soffit's left inlet plenum, where no cartridge is, reached through the left hinged underside (X -1100 and -950)"),
    ("lock_dx", "150 mm", "mm", "assumption", "spacing of the two soffit lock screws along the front member"),
    # ---- roof exhaust slot in C2 only (D-60, D-61; PM ruling 2026-10-31: the two skins are two parts)
    ("slot_x0", "872 mm", "mm", "source", "air report 7e (sized on skeleton P04): roof slot X 872 to 1157, over the soffit's exhaust fan box"),
    ("slot_w", "285 mm", "mm", "source", "air report 7e: roof slot 285 x 294"),
    ("slot_d", "294 mm", "mm", "source", "air report 7e: roof slot 285 x 294"),
    ("slot_y0", "-620 mm", "mm", "confirmed", "D-61, PM ruling 2026-10-31: roof slot Y -620 to -326, 5 mm clear of the frame's front member"),
    # ---- the cassette: one part for both halves (CS-510301)
    ("cs_front", "360 mm", "mm", "confirmed",
     "D-60 soffit over the door head, 360 deep and 220 tall (Z 2120 to 2340), flush with the air column's face (PM rulings 2026-10-31, air group); the cassettes stop at its back face (PM ruling 2026-10-31)"),
    ("cs_gap", "3 mm", "mm", "assumption",
     "edge gap round the cassette to the next lining, the other cassette or the top decor block; the 3.2 mm PORON gasket (selection D) just touches across it"),
    ("cs_w", "inner_w / 2 - 2 * cs_gap", "mm", "calculation", "cassette width: half the 2338 inside width less a gap each side = 1163"),
    ("cs_d", "wall_depth - stack_t - cs_front - 2 * cs_gap", "mm", "calculation",
     "cassette length front to back: the 1414 envelope (decor back plate to the back lining face) less the soffit and a gap each end = 1408 with no soffit"),
    ("tray_t", "0.5 mm", "mm", "confirmed", "D-37: galvanised steel tray 0.5 mm (DX51D+Z, selection B)"),
    ("tray_h", "cass_t", "mm", "calculation",
     PM_RULING + ": the returns run the full cassette depth (34) and turn in under the felt edge"),
    ("lip_w", "12 mm", "mm", "confirmed", PM_RULING + ": a 12 mm lip under the felt edge"),
    ("bend_r", "tray_t", "mm", "assumption", "inside bend radius 1 x t for 0.5 mm DX51D (the sheet metal rule's bend radius is its Thickness); the factory's tooling sets it (guideline 9)"),
    ("felt_t", "9 mm", "mm", "confirmed", "D-17: 9 mm PET felt on the cassette face (plan VT03-PET)"),
    ("felt_c", "1 mm", "mm", "assumption", "felt edge clearance inside the returns, so the felt drops onto the lips"),
    ("gap_h", "tray_h - felt_t - 2 * tray_t", "mm", "calculation",
     "air gap between the tray base and the felt (24): the cable path (D-41) and the acoustic gap (D-17)"),
    ("rib_n", "2", "", "confirmed", PM_RULING + ": 2 ribs keep the felt flat"),
    ("rib_off", "cs_w / 6", "mm", "calculation",
     "rib centre from the cassette centre line: with 2 ribs the felt spans 3 equal widths of cs_w / 3 = 388"),
    ("rib_crown", "20 mm", "mm", "assumption", "flat width of the rib that carries the felt"),
    ("rib_fl", "12 mm", "mm", "assumption", "rib top flange width against the tray base; the rib-to-tray joint is HOLD"),
    ("rib_end", "5 mm", "mm", "assumption", "clearance from each rib end to the returns"),
    ("fill_t", "40 mm", "mm", "confirmed", "D-24: 40 mm PET fill rides on the cassette back (25 kg/m3 by default, PM ruling 2026-10-31)"),
    ("fill_c", "5 mm", "mm", "assumption",
     "fill clearance to the frame members, clips and catches, so the cassette never touches the frame (D-17)"),
    ("fill_min", "100 mm", "mm", "assumption", "a fill strip shorter than this isn't made (a bay mostly over the soffit)"),
    ("fill_hw", "inner_w / 4 - close_gap / 2 - tube_w - fill_c", "mm", "calculation",
     "half length of a fill strip, set by the seam member over the cassette's inner edge and used on both sides, so both cassettes stay the same part"),
    # ---- HOLD envelopes: space kept for parts not yet named (guideline 4.3)
    ("clip_w", "40 mm", "mm", "assumption", "clip space along X; HOLD H03 / ISS-076 until a clip is named with its rating"),
    ("clip_d", "30 mm", "mm", "assumption", "clip space out from the member face; HOLD H03 / ISS-076"),
    ("clip_h", "30 mm", "mm", "assumption", "clip space above the tray; HOLD H03 / ISS-076"),
    ("catch_w", "40 mm", "mm", "assumption", "safety catch space along X; HOLD H04 / ISS-076"),
    ("catch_d", "30 mm", "mm", "assumption", "safety catch space out from the member face; HOLD H04 / ISS-076"),
    ("catch_h", "40 mm", "mm", "assumption", "safety catch space above the tray, up the member face; HOLD H04 / ISS-076"),
    # ---- cables, sprinkler reserve (no lights in the cassettes: PM ruling 2026-10-31, the lights
    #      move to a light shelf along the tops of the side and back walls)
    ("cable_hole", "20 mm", "mm", "assumption",
     "cable hole in the front and back returns for a grommet: the voice cockpit route from the back wall to the front (REQ-VCK-03, D-41) and the spare path (ISS-069); grommet HOLD"),
    ("sprk_d", "150 mm", "mm", "assumption", "reserved round zone for a later sprinkler drop (REQ-US-01)"),
]

# Part numbers: CEILING 41xxxx, ceiling cassette 5103xx (assemblies) and
# 513xxx (parts), LINING bought items 518xxx (PM ruling 2026-10-31,
# conventions section 6). Checked against the reserved list by the tests.
RESERVED = {"110006", "110002", "120001", "211000", "210001", "210003", "210005", "350011", "830001", "830005"}

# key: part number, name, Vietnamese name, kind (MP made, PI bought, HS
# assembly, HOLD envelope), material key
PARTS = {
    "ceiling": ("410000", "CEILING", "Trần", "HS", None),
    "assy_c1": ("410101", "CEILING - PANEL ASSY - C1", "Trần - tấm trái (cụm)", "HS", None),
    "assy_c2": ("410102", "CEILING - PANEL ASSY - C2", "Trần - tấm phải (cụm)", "HS", None),
    "frame_c1": ("411101", "CEILING - PANEL FRAME - C1", "Trần trái - khung nhôm", "MP", "al"),
    "frame_c2": ("411102", "CEILING - PANEL FRAME - C2", "Trần phải - khung nhôm", "MP", "al"),
    "skin_c1": ("411301", "CEILING - SKIN - C1", "Trần trái - tấm ốp alu", "MP", "acp"),
    "skin_c2": ("411302", "CEILING - SKIN - C2", "Trần phải - tấm ốp alu (có khe thoát gió)", "MP", "acp"),
    "cassette": ("510301", "LINING - CASSETTE - CEILING - COMMON", "Cassette trần (dùng chung trái/phải)", "HS", None),
    "tray": ("513101", "LINING - TRAY - CEILING", "Khay thép cassette trần", "MP", "steel"),
    "rib": ("513102", "LINING - RIB - CEILING", "Gân đỡ tấm tiêu âm trần", "MP", "steel"),
    "felt": ("513201", "LINING - FELT - CEILING", "Tấm tiêu âm PET 9 mm - trần", "MP", "felt"),
    "fill_a": ("513301", "LINING - FILL - CEILING - BAY A", "Bông PET 40 mm - trần - ô A", "MP", "fill"),
    "fill_b": ("513302", "LINING - FILL - CEILING - BAY B", "Bông PET 40 mm - trần - ô B", "MP", "fill"),
    "fill_c": ("513303", "LINING - FILL - CEILING - BAY C", "Bông PET 40 mm - trần - ô C", "MP", "fill"),
    "fill_d": ("513304", "LINING - FILL - CEILING - BAY D", "Bông PET 40 mm - trần - ô D", "MP", "fill"),
    "clip": ("518001", "LINING - CASSETTE CLIP", "Kẹp treo cassette", "HOLD", "hold"),
    "catch": ("518002", "LINING - CEILING SAFETY CATCH", "Dây an toàn cassette trần", "HOLD", "hold"),
}

# finish and process per part (master BOM columns); bought HOLD items' masses come from
# the joints register (H-10, H-11)
FINISH = {
    "frame_c1": "mill finish with the bond prep (D-79)", "frame_c2": "mill finish with the bond prep (D-79)",
    "skin_c1": "ACP EV3038 Dark Yellow (D-12)", "skin_c2": "ACP EV3038 Dark Yellow (D-12)", "tray": "galvanised (Z coating, grade to confirm)",
    "rib": "galvanised (Z coating, grade to confirm)", "felt": "Dark Gray (D-79)",
}
PROCESS = {
    "frame_c1": "tube cut to length, CNC or jig drilled (holes +/-0.2 from the spigot hole, R-J6), frame joint HOLD (H11)",
    "frame_c2": "tube cut to length, CNC or jig drilled (holes +/-0.2 from the spigot hole, R-J6), frame joint HOLD (H11)",
    "skin_c1": "CNC routed ACP", "skin_c2": "CNC routed ACP, roof slot routed", "tray": "sheet metal: laser cut, bent", "rib": "sheet metal: cut, bent",
    "felt": "CNC knife cut", "fill_a": "cut", "fill_b": "cut", "fill_c": "cut", "fill_d": "cut",
}
HOLD_MASS = {   # kg each, status, source
    "clip": (0.040, "assumption", "joints register H-10 and PM ruling 2026-10-31: 0.040 kg each (D-81's working figure) until a named clip is weighed (HOLD-08)"),
    "catch": (0.100, "assumption", "PM ruling 2026-10-31 for the BOM check: 0.100 kg each until a named catch is weighed (joints register H-11, HOLD-08)"),
}

# Joint hardware fitted in the factory to each ceiling half (joints register 2.1 numbers and
# names, D-63; every rivnut, stop washer, retainer and pre-fitted bolt goes in at the factory,
# REQ-ASM-10). key: part number, name, Vietnamese name, class, unit, count per half as an
# expression for C1 and for C2, mass each (kg, per m for lengths), mass status and source.
# J-CEIL-01 side edges: the wall is the nut side, the ceiling's side tube holds the captive
# M6 x 16 bolts. Back edges: the ceiling is the nut side (rivnuts with stop washers in its back
# member; the joint gasket on that face). J-CEIL-02: C1 has plain holes and the bulb seal, C2
# the rivnuts with the captive M6 x 25 pins.
HARDWARE = {
    "bolt16": ("838001", "HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC", "Bulong lục giác chìm M6 × 16",
               "PI", "pc", "n_ceil_side_bolt", "n_ceil_side_bolt", 0.0062,
               "calculation: head 10 x 6 less the socket, shank 6 x 16 at 85% for the thread, steel 7850 kg/m3"),
    "bolt25": ("838002", "HARDWARE - SOCKET HEAD BOLT - M6 X 25 - ISO 4762 8.8 ZINC", "Bulong lục giác chìm M6 × 25 (chốt mối nối khép)",
               "PI", "pc", "0", "cj_pin_n", 0.0079,
               "calculation: head 10 x 6 less the socket, shank 6 x 25 at 85% for the thread, steel 7850 kg/m3"),
    "rivnut": ("838003", "HARDWARE - RIVET NUT - M6 - SHEREX CAH3-610-4.2", "Tán rút M6",
               "PI", "pc", "cj_back_n + 4", "cj_back_n + cj_pin_n + 2", 0.0023,
               "calculation: body 9.5 x 14.86 with an M6 bore and a 12.96 x 0.76 head (SHX sizes), 2700 kg/m3"),
    "washer": ("838004", "HARDWARE - WASHER - M6 LARGE - ISO 7093-1 6.4 X 18 A2", "Long đen to M6 inox",
               "PI", "pc", "n_ceil_side_bolt", "n_ceil_side_bolt + cj_pin_n", 0.0028,
               "calculation: 6.4 x 18 x 1.6 (ISO 7093-1), 7900 kg/m3"),
    "retainer": ("838005", "HARDWARE - CAPTIVE RETAINER - M6 HEAD - GROMMET FOR 19 HOLE", "Vòng giữ đầu bulong",
                 "HOLD", "pc", "n_ceil_side_bolt", "n_ceil_side_bolt", 0.001,
                 "assumption: a small grommet; part not chosen (HOLD-02)"),
    "stopw": ("831002", "HARDWARE - STOP WASHER - Ø10.5 X Ø20 X 1.5 - AL", "Long đen chặn nhôm",
              "MP", "pc", "cj_back_n", "cj_back_n", 0.0009, "calculation: 10.5 x 20 x 1.5, 2700 kg/m3"),
    "gasket": ("848001", "SEALS - JOINT GASKET - 8 X 3.97 - PORON 4701-40 PSA", "Gioăng mối nối 3.97",
               "PI", "m", "half_fw / 1000 mm", "half_fw / 1000 mm", 0.0076,
               "calculation: per metre, 8 x 3.97 at 240 kg/m3 (assumption for the foam's density)"),
    "bulb": ("848004", "SEALS - CLOSING SEAM BULB SEAL - GAP 4 TO 7 - EPDM OR TPE", "Gioăng ống mối nối khép",
             "HOLD", "m", "wall_depth / 1000 mm", "0", 0.07,
             "assumption: per metre, a hollow EPDM bulb of about 60 mm2 at 1200 kg/m3; part HOLD-12"),
}

# material key: name in the CAD, density kg/m3, status, source
MATERIALS = {
    "al": ("Aluminium 6063-T6, mill finish (D-79)", 2700.0, "source", "6063-T6, mill finish with the bond spec's surface prep (D-79)"),
    "steel": ("Galvanised steel DX51D+Z", 7850.0, "source", "EN 10346 DX51D+Z (selection B): 0.5 mm = 3.93 kg/m2"),
    "acp": ("ACP 3 mm EV3038, 3.5 kg/m2", 3.5 / 0.003, "calculation", "3.5 kg/m2 (layout study acp3_kgm2, PM ruling) / 3 mm"),
    "felt": ("PET felt 9 mm, 1.8 kg/m2", 1.8 / 0.009, "calculation", "1.8 kg/m2 (layout study pet9_kgm2) / 9 mm; the factory's felt is unverified (D-31)"),
    "fill": ("PET fill 25 kg/m3 (Sorberpoly 2D)", 25.0, "confirmed",
             "PM ruling 2026-10-31 (linings, weight): 25 kg/m3 by default; the wall sample's T02 confirms it, else back to 32 (D-54)"),
    "hold": ("HOLD envelope - no mass", 1.0, "assumption", "space only; the real part's mass comes with its datasheet"),
}

# The cassette's own system CS-510301 (one part, used at C1-CASS and C2-CASS):
# origin at the cassette envelope's centre line (X), its front plane (Y: the
# decor's back plate Y -645, or the soffit's back face, cs_front behind it, D-60) and its top (Z, the tray base top, 4 mm under the
# roof frame). Axes parallel to the pod's. Pod position of the origin:
CASSETTE_CS = {
    "C1": ("-inner_w / 4", "pod_d / 2 - wall_depth + cs_front", "pod_h - stack_t + cass_t"),
    "C2": ("inner_w / 4", "pod_d / 2 - wall_depth + cs_front", "pod_h - stack_t + cass_t"),
}

# ---------------------------------------------------------------- expressions

_MM = re.compile(r"(?<![A-Za-z_])(\d+(?:\.\d+)?)\s*mm\b")


def to_python(expr):
    """Fusion expression -> Python expression in mm (only what this pack uses).
    Fusion separates function arguments with ";"."""
    return _MM.sub(r"\1", expr).replace(";", ",")


def load_skeleton(path=None):
    """[(name, expression, unit, status, source)] from the skeleton's own CSV."""
    path = path or SKELETON_CSV
    rows = []
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            # skeleton v4 (PR #94) gives each parameter its unit ("-" for a count); older lists were all mm
            unit = (r.get("unit") or "mm").strip()
            unit = "" if unit in ("-", "") else unit
            rows.append((r["parameter"], r["expression"], unit, r["status"],
                         "skeleton %s: %s" % (SKELETON_REV, r["source"])))
    return rows


def all_params(skeleton_rows=None):
    sk = skeleton_rows if skeleton_rows is not None else load_skeleton()
    have = {r[0] for r in sk}
    clash = [p[0] for p in CEILING_PARAMS if p[0] in have and p[0] not in SKELETON_MAY_DEFINE]
    if clash:
        raise ValueError("ceiling parameter names clash with the skeleton: %s" % clash)
    own = []
    for p in CEILING_PARAMS:
        if p[0] in have:
            continue
        own.append(p)
    return list(sk) + own


def evaluate(params, overrides=None):
    """Values in mm (or plain numbers) for every parameter, in order."""
    env = {"ceil": math.ceil, "floor": math.floor, "abs": abs, "min": min, "max": max, "sqrt": math.sqrt}
    overrides = overrides or {}
    vals = {}
    for name, expr, _unit, _st, _src in params:
        e = overrides.get(name, expr)
        vals[name] = float(eval(to_python(e), {"__builtins__": {}}, dict(env, **vals)))
    return vals


def ev(vals, expr):
    env = {"ceil": math.ceil, "floor": math.floor, "abs": abs, "min": min, "max": max}
    return float(eval(to_python(expr), {"__builtins__": {}}, dict(env, **vals)))


# ---------------------------------------------------------------- layout
# Every body is a box given by six expressions (x0, x1, y0, y1, z0, z1), in
# the frame named by `frame`: "pod" (pod system) or "cs" (CS-510301).

YW = "(pod_d / 2 - wall_depth)"      # front plane of the walls and ceiling (decor back plate)
YB = "(pod_d / 2)"                   # back face
ZF0 = "(pod_h - outer_t)"            # underside of the ceiling frame
ZF1 = "(pod_h - outer_t + frame_t)"  # top of the frame (the bond line and the skin sit above it)
ZSKIN = "(pod_h - skin_t)"           # underside of the skin


def side_sign(half):
    return -1 if half == "C1" else 1


def xr(half, a, b):
    """X range of a member of one ceiling frame, a and b measured outward from the frame's
    closing-seam edge (X = +-close_gap / 2), as expressions."""
    a, b = "close_gap / 2 + %s" % a, "close_gap / 2 + %s" % b
    return ("-(%s)" % b, "-(%s)" % a) if side_sign(half) < 0 else ("(%s)" % a, "(%s)" % b)


def frame_members(half):
    """Members of one ceiling frame in the pod system. half 'C1' (-X) or 'C2' (+X).
    The frame is half_fw wide: from the closing seam (X = +-close_gap / 2, the 5.5 mm frame
    gap, R-J11) to the side wall's stop (one seam_gap inside the side frames). The 40 x 40
    back member runs the frame's full width (R-J3); the side and seam members stop at it.
    Returns [(code, name, axis, (x0, x1, y0, y1, z0, z1))]; axis = the long axis."""
    out = []
    yb0 = YB + " - back_w"
    side = xr(half, "half_fw - tube_w", "half_fw")
    seam = xr(half, "0 mm", "tube_w")
    inner = xr(half, "tube_w", "half_fw - tube_w")
    out.append(("SIDE", "SIDE MEMBER", "y", side + (YW, yb0, ZF0, ZF1)))
    out.append(("SEAM", "SEAM MEMBER", "y", seam + (YW, yb0, ZF0, ZF1)))
    out.append(("FRONT", "FRONT MEMBER", "x", inner + (YW, YW + " + tube_w", ZF0, ZF1)))
    out.append(("BACK", "BACK MEMBER 40X40", "x", xr(half, "0 mm", "half_fw") + (yb0, YB, ZF0, ZF1)))
    for k in range(1, 4):
        y0 = cross_y0(k)
        out.append(("X%d" % k, "CROSS MEMBER %d" % k, "x", inner + (y0, y0 + " + tube_w", ZF0, ZF1)))
    return out


def cross_y0(k):
    """Front face Y of cross member k. X1 sits x1_ov over the soffit's back edge (D-87 hangers);
    X2 and X3 keep the fr_pitch spacing from the front member."""
    if k == 1:
        return "%s + cs_front - x1_ov" % YW
    return "%s + %d * fr_pitch" % (YW, k)


def joint_holes(half):
    """The site-joint holes of one ceiling frame (joints register 3.5, 3.6, 2.9), as hole rows:
    (name, member code, face, (x, y, z) of the row's first hole centre, diameter, count, pitch,
    pattern axis). face: the member face the hole goes through, 'out' (the face toward the
    side wall or the seam), 'in' (the opposite face, toward the frame's own bay) or 'bottom'.
    A row's first hole is the one with the lowest coordinate along its pattern axis, and the
    row runs toward +axis. The slot of the spigot pair is a separate item (spigot_slot)."""
    s = side_sign(half)
    zc = "ceil_bolt_z"
    side_x_out = "%s(close_gap / 2 + half_fw)" % ("-" if s < 0 else "")
    side_x_in = "%s(close_gap / 2 + half_fw - tube_w)" % ("-" if s < 0 else "")
    seam_x_out = "%s(close_gap / 2)" % ("-" if s < 0 else "")
    seam_x_in = "%s(close_gap / 2 + tube_w)" % ("-" if s < 0 else "")
    ys = "cj_side_y0"
    rows = [
        ("SIDE BOLT CLEARANCE", "SIDE", "out", (side_x_out, ys, zc), "hole_clr", "n_ceil_side_bolt", "cj_side_pitch", "y"),
        ("SIDE BOLT ACCESS", "SIDE", "in", (side_x_in, ys, zc), "hole_acc", "n_ceil_side_bolt", "cj_side_pitch", "y"),
    ]
    if s < 0:
        rows.append(("SEAM PIN CLEARANCE", "SEAM", "out", (seam_x_out, ys, zc), "hole_clr", "cj_pin_n", "cj_pin_pitch", "y"))
    else:
        rows.append(("SEAM PIN RIVNUT", "SEAM", "out", (seam_x_out, ys, zc), "hole_rvn", "cj_pin_n", "cj_pin_pitch", "y"))
        rows.append(("SEAM PIN ACCESS", "SEAM", "in", (seam_x_in, ys, zc), "hole_acc", "cj_pin_n", "cj_pin_pitch", "y"))
    bx0 = "-(close_gap / 2 + half_fw - bolt_edge_inset)" if s < 0 else "cj_back_x0"
    rows.append(("BACK RIVNUT", "BACK", "bottom", (bx0, "cj_back_y", ZF0), "hole_rvn", "cj_back_n", "cj_back_pitch", "x"))
    rows.append(("BACK SPIGOT ROUND", "BACK", "bottom", ("%scj_spig_x0" % ("-" if s < 0 else ""), "cj_back_y", ZF0),
                 "spig_hole", "1", "0 mm", "x"))
    hx = "%shang_x" % ("-" if s < 0 else "")
    rows.append(("SOFFIT HANGER FRONT", "FRONT", "bottom", (hx, "%s + tube_w / 2" % YW, ZF0), "hole_rvn", "1", "0 mm", "x"))
    rows.append(("SOFFIT HANGER X1", "X1", "bottom", (hx, "%s + tube_w / 2" % cross_y0(1), ZF0), "hole_rvn", "1", "0 mm", "x"))
    if s < 0:
        rows.append(("SOFFIT LOCK", "FRONT", "bottom", ("-lock_x", "%s + tube_w / 2" % YW, ZF0), "hole_rvn", "2", "lock_dx", "x"))
    return rows


def spigot_slot(half):
    """The 8.5 x 14 spigot slot along X in the back member's bottom face, at the side end:
    (centre x, y, z, width, length) as expressions."""
    return ("%scj_spig_x1" % ("-" if side_sign(half) < 0 else ""), "cj_back_y", ZF0, "spig_hole", "spig_slot")


def hole_positions(vals, half):
    """Every joint hole centre of one half in mm: [(row name, diameter, (x, y, z))], the slot as
    one item at its centre."""
    out = []
    for name, _m, _f, (x, y, z), dia, n, pitch, axis in joint_holes(half):
        x0, y0, z0, d, nn, p = (ev(vals, e) for e in (x, y, z, dia, n, pitch))
        for k in range(int(round(nn))):
            out.append((name, d, (x0 + (k * p if axis == "x" else 0), y0 + (k * p if axis == "y" else 0), z0)))
    sx, sy, sz, sw, _sl = (ev(vals, e) for e in spigot_slot(half))
    out.append(("BACK SPIGOT SLOT", sw, (sx, sy, sz)))
    return out


def skin_box():
    """A ceiling skin in its own system: origin at one end of its front edge, Z = 0 on its
    underside (the bond line), running toward -X. C1's skin has its origin on the seam
    edge (X = -seam_gap / 2), C2's on its side edge (X = seam_gap / 2 + half_pw), so both
    are the same rectangle; C2's carries the roof slot (PM ruling 2026-10-31: two parts)."""
    return ("-half_pw", "0 mm", "0 mm", "wall_depth", "0 mm", "skin_t")


SKIN_PLACES = {"C1": ("-seam_gap / 2", YW, ZSKIN), "C2": ("seam_gap / 2 + half_pw", YW, ZSKIN)}


def roof_slot_box():
    """The roof slot (D-61) in the C2 skin's own system, as a through cut."""
    ox = "(seam_gap / 2 + half_pw)"
    return ("slot_x0 - %s" % ox, "slot_x0 + slot_w - %s" % ox, "slot_y0 - %s" % YW, "slot_y0 + slot_d - %s" % YW,
            "0 mm", "skin_t")


# cassette, in CS-510301
CS_X0, CS_X1 = "(-cs_w / 2)", "(cs_w / 2)"
CS_Y0, CS_Y1 = "cs_gap", "(cs_gap + cs_d)"
FELT_Z0, FELT_Z1 = "(-tray_h + tray_t)", "(-tray_h + tray_t + felt_t)"


def member_front_cs(k):
    """Y in CS-510301 of the front face of frame member k (0 = front member,
    1..3 = cross members, 4 = the 40 x 40 back member). The cassette origin sits
    cs_front behind the front plane YW (D-60 soffit)."""
    if k == 4:
        return "(wall_depth - back_w - cs_front)"
    if k == 1:
        return "(-x1_ov)"
    return "(%d * fr_pitch - cs_front)" % k


def member_back_cs(k):
    return "(%s + tube_w)" % member_front_cs(k)


def clip_boxes():
    """6 clips: on the back faces of cross members 1..3, over the ribs. The back face keeps
    every clip over the cassette for any soffit up to about 385 mm (D-60)."""
    out = []
    for k in (1, 2, 3):
        for side in (-1, 1):
            xc = "(%s * rib_off)" % ("-1" if side < 0 else "1")
            yb = member_back_cs(k)
            out.append(("CLIP X%d %s" % (k, "L" if side < 0 else "R"),
                        ("%s - clip_w / 2" % xc, "%s + clip_w / 2" % xc, yb, "%s + clip_d" % yb, "0 mm", "clip_h")))
    return out


def catch_boxes():
    """2 safety catches: on the front face of cross member 2, over the ribs (the clips use its back face)."""
    out = []
    for side in (-1, 1):
        xc = "(%s * rib_off)" % ("-1" if side < 0 else "1")
        yf = member_front_cs(2)
        out.append(("CATCH %s" % ("L" if side < 0 else "R"),
                    ("%s - catch_w / 2" % xc, "%s + catch_w / 2" % xc, "%s - catch_d" % yf, yf, "0 mm", "catch_h")))
    return out


FILL_KEYS = ("fill_a", "fill_b", "fill_c", "fill_d")


def fill_strips(vals=None):
    """Fill strips on the tray back, one per frame bay that lies over the cassette.
    Which bays get a strip is decided from the values at build time (vals); the boxes
    stay expressions, so the strips follow later edits. Strips of the same size and
    notches are one part. Returns [(key, bay, (x0, x1, y0, y1, z0, z1), [notch boxes])]."""
    vals = vals if vals is not None else evaluate(all_params())
    strips, kinds = [], {}
    for bay in range(4):
        y0 = "max(%s + tube_w; cs_gap) + fill_c" % member_front_cs(bay)
        y1 = "min(%s; cs_gap + cs_d) - fill_c" % member_front_cs(bay + 1)
        if ev(vals, y1) - ev(vals, y0) < vals["fill_min"]:
            continue
        box = ("-fill_hw", "fill_hw", y0, y1, "0 mm", "fill_t")
        bv = tuple(ev(vals, e) for e in box)
        notches, sig = [], []
        for name, b in clip_boxes() + catch_boxes():
            nb = ("%s - fill_c" % b[0], "%s + fill_c" % b[1], "%s - fill_c" % b[2], "%s + fill_c" % b[3], "0 mm", "fill_t")
            nv = tuple(ev(vals, e) for e in nb)
            if overlap(bv, nv):
                notches.append((name, nb))
                sig.append((round(nv[0], 3), round(nv[1], 3), round(nv[2] - bv[2], 3), round(nv[3] - bv[2], 3)))
        key = (round(bv[3] - bv[2], 3), tuple(sorted(sig)))
        if key not in kinds:
            kinds[key] = FILL_KEYS[len(kinds)]
        strips.append((kinds[key], bay, box, notches))
    return strips


def sprinkler_points():
    """Two candidate zones for a later sprinkler drop (REQ-US-01), one each side so the
    cassette stays one part: in the middle of the outer felt spans (X' +-cs_w / 3) and of the
    first frame bay over the cassette, clear of ribs, clips and members."""
    y = "(%s + %s) / 2" % (member_back_cs(1), member_front_cs(2))
    return [("-cs_w / 3", y), ("cs_w / 3", y)]


def rib_boxes():
    """Rib outline boxes (for clash checks); the rib itself is a hat section."""
    out = []
    for side in (-1, 1):
        xc = "(%s * rib_off)" % ("-1" if side < 0 else "1")
        out.append(("RIB %s" % ("L" if side < 0 else "R"),
                    ("%s - rib_crown / 2 - rib_fl" % xc, "%s + rib_crown / 2 + rib_fl" % xc,
                     CS_Y0 + " + tray_t + rib_end", CS_Y1 + " - tray_t - rib_end", FELT_Z1, "-tray_t")))
    return out


def boxes_mm(vals, boxes):
    return [(n, tuple(ev(vals, e) for e in b)) for n, b in boxes]


def overlap(a, b, tol=1e-6):
    return all(a[2 * i] < b[2 * i + 1] - tol and b[2 * i] < a[2 * i + 1] - tol for i in range(3))


# ---------------------------------------------------------------- flat pattern of the tray

def tray_flat(vals, k=0.44):
    """Flat blank of the tray (mm) by the K-factor rule, for checking Fusion's flat
    pattern: outside sizes w x d, returns tray_h deep overall (two bends each), lips
    lip_w wide (outside), inside radius r = t. Each 90 degree bend takes r + t off
    each straight it meets (outside setback) and adds its bend allowance."""
    t, r = vals["tray_t"], vals["bend_r"]
    ba = math.pi / 2 * (r + k * t)
    w, d, h, lip = vals["cs_w"], vals["cs_d"], vals["tray_h"], vals["lip_w"]
    so = r + t
    base_w, base_d = w - 2 * so, d - 2 * so
    ret = h - 2 * so
    lip_f = lip - so
    side = 2 * ba + ret + lip_f
    return {"bend_allowance": ba, "blank_w": base_w + 2 * side, "blank_d": base_d + 2 * side, "k_factor": k,
            "return_flat": ret, "lip_flat": lip_f}


if __name__ == "__main__":
    p = all_params()
    v = evaluate(p)
    for n in ("half_pw", "half_fw", "fr_pitch", "cs_w", "cs_d", "gap_h", "rib_off", "fill_hw", "inner_w",
              "cj_side_y0", "cj_side_pitch", "cj_back_x0", "cj_back_pitch", "cj_back_y", "ceil_bolt_z"):
        print(n, round(v[n], 3))
    print(tray_flat(v))
    for half in ("C1", "C2"):
        for name, d, xyz in hole_positions(v, half):
            print(half, name, d, tuple(round(c, 2) for c in xyz))
