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
    ("tube_w", "20 mm", "mm", "confirmed", "D-34, D-54: 20 x 40 members (the 20 mm face lies in the plane of the panel); D-131 keeps the outside sections in steel"),
    ("tube_t", "1.0 mm", "mm", "source", "J-FRAME-01 (D-131; the joints register's gauges): the side, seam, front and back members "
     "and cross member 1 in 1.0 mm galvanized steel; every perimeter member, every 40 x 40 member and any member with a "
     "site bolt, spigot, stopped-joint rivnut or hanger stud (cross member 1 carries the soffit's, J-AIR-01)"),
    ("tube_t_in", "0.8 mm", "mm", "source", "J-FRAME-01 (D-131): cross members 2 and 3 in 0.8 mm; they carry the lining's clips "
     "and catches but no site joint"),
    ("back_w", "40 mm", "mm", "confirmed",
     "R-J3 (joints register 2.4): the ceiling's back member is 40 x 40, so the back panel's top tube overlaps it by 34 and its rivnuts sit on a 40 mm face"),
    ("mp_t", "2 mm", "mm", "source", "J-FRAME-01 (D-131): the mitre plates 831007 and 831008, 2.0 thick, welded into every frame corner"),
    # each plate is a square-ended laser blank a little shorter than its mitre, so both ends sit 0.5 inside the frame's
    # faces on both plate faces (the Lead's steer 2026-11-01, #308: a plate the mitre's full length poked out at the
    # outer corner); the weld fills the step and is ground flush. Start and length along the mitre from the frame's
    # outer corner, as the joints register gives them (and joints/frame_steel_check.py's PLATE_BLANKS checks them)
    ("mp45_x0", "1.75 mm", "mm", "source", "the joints register's H-40 (831007, #308): its blank starts 1.75 along the mitre from the frame's outer corner"),
    ("mp45_l", "26.5 mm", "mm", "source", "the joints register's H-40 (831007, #308): its blank is 26.5 long (the mitre is 28.28)"),
    ("mp_sb_x0", "3.15 mm", "mm", "source", "the joints register's H-41 (831008, #308): its blank starts 3.15 along the mitre from the frame's outer corner"),
    ("mp_sb_l", "41.5 mm", "mm", "source", "the joints register's H-41 (831008, #308): its blank is 41.5 long (the mitre is 44.72)"),
    ("cb45", "mp_t / 2 * sqrt(2)", "mm", "calculation", "J-FRAME-01: each 20 x 40 member at a 45 deg corner is cut back 1.41 along "
     "its length, so the plate fits and the outside sizes stay"),
    ("cb_sb", "mp_t / 2 * sqrt(tube_w * tube_w + back_w * back_w) / tube_w", "mm", "calculation",
     "J-FRAME-01: the side and seam members cut back 2.24 where they meet the 40 x 40 back member (831008)"),
    ("cb_bs", "mp_t / 2 * sqrt(tube_w * tube_w + back_w * back_w) / back_w", "mm", "calculation",
     "J-FRAME-01: the back member cut back 1.12 at each end (831008)"),
    ("fr_n", "3", "", "confirmed", PM_RULING + ": 3 cross members between the side and seam members"),
    ("fr_pitch", "(wall_depth - tube_w) / (fr_n + 1)", "mm", "calculation",
     "centre spacing of the cross members, front member to back member: (1495 - 20) / 4 = 368.75, 400 or less (D-16)"),
    # ---- site joints (joints register V2-ENG-JNT-01; the register owns the bolt lines, PM ruling 2026-10-31)
    ("hole_clr", "7 mm", "mm", "confirmed", "R-J6 (joints register 2.9): bolt clearance hole, positioned to +/-0.2 from the spigot hole"),
    ("hole_acc", "19 mm", "mm", "confirmed", "joints register 2.2, 2.9: access hole, so the 18 mm head washer goes in with the bolt"),
    ("hole_rvn", "10.0 mm", "mm", "source", "D-163 (pod-wide ruling 2026-11-01): the M6 rivnut 838003 is Sherex CAL2-610-4.2, the "
     "knurled round body, in a round drilled hole Ø10.00 +0.10 (was CAH2's Ø9.53; T06's spin-out test, 4 N·m or more in the "
     "real tubes, confirms it; the joints register's H-03)"),
    ("spig_hole", "8.5 mm", "mm", "confirmed", "R-J13: spigot hole 8.5, round at one end of the edge, an 8.5 x 14 slot along it at the other"),
    ("spig_slot", "14 mm", "mm", "confirmed", "R-J13: the spigot slot's length along the edge (+/-2.75 of travel for the 8 mm spigot)"),
    ("lead_in", "1 mm", "mm", "confirmed", "R-J9 (joints register 2.10): 1 x 45 deg lead-in on the lower edges of the C1-C2 faces, so C2 drops past C1 without catching the seal"),
    # J-CEIL-01's counts, start points and pitches are the skeleton's named values (v4, PR #94):
    # n_ceil_side_bolt, n_ceil_back_bolt, ceil_side_y0, ceil_side_pitch, ceil_back_x0, ceil_back_pitch
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
     "PM rulings 2026-11-01: two captive screws (5 mm key) lock the soffit, so taking a cassette out can never free it; "
     "in cross member 1 since DR's new panel face (the room-side rail's loaded edge 18 mm away), over the soffit's left "
     "inlet plenum where no cartridge is, reached through its left hinged underside; C2's cross member carries the "
     "mirrored rivnuts unused, so the member stays one part"),
    ("lock_dx", "150 mm", "mm", "assumption", "spacing of the two soffit lock screws along cross member 1"),
    # DT's bolts (J-FRONT-03): DT's back plate bolts to the front tubes, from inside them through the bays
    ("dt_x1", "449 mm", "mm", "source", "joints register J-FRONT-03 (3.13) and 2.9: DT's right end over C2, so its edge "
     "with the ceiling runs 1650.74 from C1's frame end (X -1201.74 to +449)"),
    ("dt_bolt_n", "4", "", "source", "J-FRONT-03: 4 bolts M6 x 16 along DT's edge with the ceiling at the 220 rule "
     "(2.9): X -981.74, -578.16, -174.58 in C1's front tube and +228.99 in C2's"),
    ("dt_pitch", "(dt_x1 + close_gap / 2 + half_fw - 2 * bolt_edge_inset) / (dt_bolt_n - 1)", "mm", "calculation",
     "J-FRONT-03: the 220 rule's pitch along DT's 1650.74 edge, 403.58"),
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
    ("fill_t", "40 mm", "mm", "confirmed", "D-24: 40 mm PET fill rides on the cassette back (24 kg/m3 by default, D-81)"),
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
    ("cable_hole", "19.1 mm", "mm", "confirmed",
     "PM ruling 2026-11-01: the panel hole ELECTRICAL's cable bushing needs, in the front and back returns: the voice cockpit route from the back wall to the front (REQ-VCK-03, D-41) and the spare path (ISS-069)"),
    ("sprk_d", "150 mm", "mm", "assumption", "reserved round zone for a later sprinkler drop (REQ-US-01)"),
    # the roof sleeve's flange lies on C2's skin round the slot with the roof grille's 4 rivnuts 838003 (J-AIR-03): the
    # skin takes a hole_slv clearance hole under each (D-177; the layout CEILING's, 2026-11-01, HOLD-04's rule: each rivnut
    # 2 hole diameters from every free edge, the skin's slot edge too): 2 on the slot's left side, 2 on its back side
    # BEHIND cross member 1, whose front face is too near the slot for a set rivnut's bulge. AIR's model carries the same
    # names (AIR's sleeve)
    ("slv_rn_e", "20.0 mm", "mm", "calculation", "rivnut centre to any free edge: 2 x the Ø10.00 hole (D-163; HOLD-04's rule; "
     "was 19.2 for the Ø9.53)"),
    ("slv_rn_in", "20 mm", "mm", "assumption", "the rivnuts this far in from the slot's corners along their sides"),
    ("slv_bulge", "14 mm", "mm", "assumption", "a set rivnut's blind-side bulge, about 14 across (the hole FRONT clears for body and "
     "bulge, DR model fr_hole_jf; Sherex gives no size)"),
    ("slv_rn_clr", "1 mm", "mm", "assumption", "the bulge's clearance to cross member 1's back face"),
    ("slv_rn_yb", "(pod_d / 2 - wall_depth) + cs_front - x1_ov + tube_w + slv_bulge / 2 + slv_rn_clr", "mm", "calculation",
     "the back side's rivnuts behind cross member 1: its back face plus half the bulge plus the clearance (Y -273)"),
    # D-177 (PM ruling 2026-11-01): each skin hole passes a set rivnut (its body and the bulge right under the 1 mm flange,
    # which sits in the skin's thickness) wherever the sleeve lands in its slot. The flange's butyl ring, outside the four
    # holes, seals them and the sleeve's gap in the slot (J-AIR-03; AIR's list)
    ("slv_fit", "1.0 mm", "mm", "confirmed", "D-177: the roof sleeve is 1.0 smaller a side than the roof slot, so it drops in at "
     "its size tolerance (AIR's walls take it; the flange, its rivnuts and the grille stay where they are)"),
    ("slv_pos", "0.5 mm", "mm", "calculation", "the flange's rivnut hole and the skin's hole, each placed to +/-0.2 (laser and "
     "CNC cut, assumption), rounded up"),
    ("slv_rn_body", "9.91 mm", "mm", "source", "the set rivnut's knurled body at its largest, CAL2-610-4.2 (D-163; the joints "
     "register's ST-03)"),
    ("hole_slv", "slv_bulge + 2 * (slv_fit + slv_pos)", "mm", "calculation", "D-177: the Ø17 clearance hole in C2's skin under "
     "each sleeve rivnut: the set bulge, plus the sleeve's play in its slot and the positions on each side"),
]

# Part numbers: CEILING 41xxxx, ceiling cassette 5103xx (assemblies) and
# 513xxx (parts), LINING bought items 518xxx (PM ruling 2026-10-31,
# conventions section 6). Checked against the reserved list by the tests.
RESERVED = {"110006", "110002", "120001", "211000", "210001", "210003", "210005", "350011", "830001", "830005",
            "412201", "412205"}   # the last two: cancelled by Control (C2's side and cross member 1 are C1's), never reused

# key: part number, name, Vietnamese name, kind (MP made, PI bought, HS
# assembly, HOLD envelope), material key
PARTS = {
    "ceiling": ("410000", "CEILING", "Trần", "HS", None),
    "assy_c1": ("410101", "CEILING - PANEL ASSY - C1", "Trần - tấm trái (cụm)", "HS", None),
    "assy_c2": ("410102", "CEILING - PANEL ASSY - C2", "Trần - tấm phải (cụm)", "HS", None),
    # the frames are assemblies of member parts (D-120), welded galvanized steel (D-131, J-FRAME-01: no cleats);
    # member numbers from the master BOM's allocation (v2/04-BOM/number-allocation.csv)
    "frame_c1": ("411101", "CEILING - PANEL FRAME - C1", "Trần trái - khung thép", "HS", None),
    "frame_c2": ("411102", "CEILING - PANEL FRAME - C2", "Trần phải - khung thép", "HS", None),
    "m_side": ("412101", "CEILING - FRAME SIDE MEMBER - COMMON", "Trần - thanh cạnh của khung (dùng chung)", "MP", "steel_fr"),
    "m_seam_c1": ("412102", "CEILING - FRAME SEAM MEMBER - C1", "Trần trái - thanh mối nối của khung", "MP", "steel_fr"),
    "m_front_c1": ("412103", "CEILING - FRAME FRONT MEMBER - C1", "Trần trái - thanh trước của khung", "MP", "steel_fr"),
    "m_back_c1": ("412104", "CEILING - FRAME BACK MEMBER 40 X 40 - C1", "Trần trái - thanh sau 40x40 của khung", "MP", "steel_fr"),
    "m_x1": ("412105", "CEILING - FRAME CROSS MEMBER 1 - COMMON", "Trần - thanh ngang 1 của khung (dùng chung)", "MP", "steel_fr"),
    "m_seam_c2": ("412202", "CEILING - FRAME SEAM MEMBER - C2", "Trần phải - thanh mối nối của khung", "MP", "steel_fr"),
    "m_front_c2": ("412203", "CEILING - FRAME FRONT MEMBER - C2", "Trần phải - thanh trước của khung", "MP", "steel_fr"),
    "m_back_c2": ("412204", "CEILING - FRAME BACK MEMBER 40 X 40 - C2", "Trần phải - thanh sau 40x40 của khung", "MP", "steel_fr"),
    "m_cross": ("412001", "CEILING - FRAME CROSS MEMBER - PLAIN - COMMON", "Trần - thanh ngang trơn của khung (dùng chung)", "MP", "steel_fr"),
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

# the frame members' part keys (D-120): the side member and cross member 1 are one part each for both
# frames (Control's allocation 2026-11-01: C2's is C1's turned over; 412201 and 412205 cancelled)
MEMBER_KEYS = ("m_side", "m_x1", "m_seam_c1", "m_front_c1", "m_back_c1", "m_seam_c2", "m_front_c2", "m_back_c2", "m_cross")
# The common members' C2 copies: C1's part turned 180 deg about the pod's Y axis (the side member, upside down:
# every feature is centred across its 40 face and the mitres are vertical) or Z axis (cross member 1, end for
# end: its one hanger hole is centred across its width, at the same distance from the seam end). The copy's
# origin (the pod's, as the part is built in place in C1) goes to turned_origin(key); test_ceiling_offline.py
# proves every feature of C2's own layout lands on C1's turned.
TURNED = {"m_side": "y", "m_x1": "z"}


def turned_origin(key):
    """Where C2's copy of a common member takes the pod origin: turning about Y through the frame's mid
    depth sends it to Z = 2 x (ZF0 + frame_t / 2); about Z through cross member 1's centre line, to
    Y = 2 x its centre."""
    if TURNED[key] == "y":
        return ("0 mm", "0 mm", "2 * %s + frame_t" % ZF0)
    return ("0 mm", "2 * (%s) + tube_w" % cross_y0(1), "0 mm")


# finish and process per part (master BOM columns); bought HOLD items' masses come from
# the joints register (H-10, H-11)
FRAME_FINISH = ("its members pre-galvanized Z100; every weld's burnt zone wire-brushed and coated with 2-component "
                "zinc-rich epoxy (J-FRAME-01); the bond prep on the skin face (D-137)")
FINISH = {
    "frame_c1": FRAME_FINISH, "frame_c2": FRAME_FINISH,
    "skin_c1": "ACP EV3038 Dark Yellow (D-12)", "skin_c2": "ACP EV3038 Dark Yellow (D-12)", "tray": "galvanised (Z coating, grade to confirm)",
    "rib": "galvanised (Z coating, grade to confirm)", "felt": "Dark Gray (D-79)",
    **{k: "pre-galvanized Z100; each weld's burnt zone wire-brushed and coated with 2-component zinc-rich epoxy "
          "(J-FRAME-01); the bond prep on the skin face (D-137)" for k in MEMBER_KEYS},
}
PROCESS = {
    "frame_c1": "welded in a jig (D-131, J-FRAME-01): the corners with their mitre plates, then the T joints; no vent or drain "
                "holes; every joint hole made after welding, from the joint faces",
    "frame_c2": "welded in a jig (D-131, J-FRAME-01): the corners with their mitre plates, then the T joints; no vent or drain "
                "holes; every joint hole made after welding, from the joint faces",
    "skin_c1": "CNC routed ACP", "skin_c2": "CNC routed ACP, roof slot and four Ø17 pass-through openings routed", "tray": "sheet metal: laser cut, bent", "rib": "sheet metal: cut, bent",
    "felt": "CNC knife cut", "fill_a": "cut", "fill_b": "cut", "fill_c": "cut", "fill_d": "cut",
    # the members (D-120): cut from galvanized steel tube (D-131); mitred where they meet the corners (D-117), cut back
    #      for the mitre plates; holes CNC or jig drilled after welding
    **{k: "tube cut to length (mitred ends where it meets the corners, cut back for the 2.0 mitre plate), welded into "
          "the frame; holes CNC or jig drilled after welding (+/-0.2 from the spigot hole, R-J6)" for k in MEMBER_KEYS},
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
    "rivnut": ("838003", "HARDWARE - RIVET NUT - M6 - STEEL ZINC - SHEREX CAL2-610-4.2", "Tán rút M6 thép mạ kẽm",
               "PI", "pc", "n_ceil_back_bolt + 4", "n_ceil_back_bolt + cj_pin_n + 2", 0.0067,
               "calculation: body 9.5 x 14.86 with an M6 bore and a 12.96 x 0.76 head (SHX2 sizes), steel 7850 kg/m3"),
    "washer": ("838004", "HARDWARE - WASHER - M6 LARGE - ISO 7093-1 6.4 X 18 A2", "Long đen to M6 inox",
               "PI", "pc", "n_ceil_side_bolt", "n_ceil_side_bolt + cj_pin_n", 0.0028,
               "calculation: 6.4 x 18 x 1.6 (ISO 7093-1), 7900 kg/m3"),
    "retainer": ("838005", "HARDWARE - CAPTIVE RETAINER - M6 HEAD - GROMMET FOR 19 HOLE", "Vòng giữ đầu bulong",
                 "HOLD", "pc", "n_ceil_side_bolt", "n_ceil_side_bolt", 0.001,
                 "assumption: a small grommet; part not chosen (HOLD-02)"),
    "stopw": ("831002", "HARDWARE - STOP WASHER - Ø10.5 X Ø20 X 1.5 - AL", "Long đen chặn nhôm",
              "MP", "pc", "n_ceil_back_bolt", "n_ceil_back_bolt", 0.0009, "calculation: 10.5 x 20 x 1.5, 2700 kg/m3"),
    # the mitre plates welded into the frames' corners (D-131, J-FRAME-01; the joints register's H-40 and H-41)
    "plate45": ("831007", "HARDWARE - MITRE PLATE - 20 X 40 - 45 DEG - 2.0 STEEL", "Tấm đệm góc vát 20 × 40 - 45° - thép 2.0",
                "MP", "pc", "2", "2", 0.0166, "source: joints register H-40 (#308), 26.5 x 40 x 2.0 steel, 16.6 g"),
    "plate_sb": ("831008", "HARDWARE - MITRE PLATE - 20 X 40 TO 40 X 40 - 2.0 STEEL",
                 "Tấm đệm góc vát 20 × 40 với 40 × 40 - thép 2.0", "MP", "pc", "2", "2", 0.0261,
                 "source: joints register H-41 (#308), 41.5 x 40 x 2.0 steel, 26.1 g"),
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
    "steel_fr": ("Galvanized steel S280GD+Z or SGC400 (yield 280 MPa or more), Z100", 7850.0, "source",
                 "J-FRAME-01 (D-131): strip-galvanized structural steel tube, certified yield 280 MPa or more (EN 10346 "
                 "S280GD+Z or JIS G3302 SGC400), zinc Z100; lot check HOLD-09"),
    "acp": ("ACP 3 mm EV3038, 3.5 kg/m2", 3.5 / 0.003, "calculation", "3.5 kg/m2 (layout study acp3_kgm2, PM ruling) / 3 mm"),
    "felt": ("PET felt 9 mm, 1.8 kg/m2", 1.8 / 0.009, "calculation", "1.8 kg/m2 (layout study pet9_kgm2) / 9 mm; the factory's felt is unverified (D-31)"),
    "fill": ("PET fill 24 kg/m3 (Sorberpoly 2D)", 24.0, "confirmed",
             "D-81: 24 kg/m3 by default, the grade Pyrotek lists and the wall sample's T02 tests; else back to 32 (D-54)"),
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
    env = {"ceil": math.ceil, "floor": math.floor, "abs": abs, "min": min, "max": max, "sqrt": math.sqrt}
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


def member_shapes(half):
    """Each member of one ceiling frame as its own part (D-120), in the pod system: its outline in
    plan, extruded over the frame's depth. The four outer corners are mitred from the outer corner
    to the inner corner (D-117): 45 deg at the front corners; at the back the 40 x 40 back member is
    cut 26.57 deg off square and the side and seam members 63.43 deg; the cross members stay square
    between the side and seam members, welded to them (D-131). Every mitred end is cut back half the
    2.0 mitre plate's thickness square to its mitre, so the plate welded between them fits and the
    outside sizes stay (J-FRAME-01): along the member, 1.41 at a 45 deg corner, 2.24 off the side and
    seam members and 1.12 off the back member at the back corners.
    Returns [(code, part key, body name, long axis, [(x, y) expressions], z0, z1)]."""
    s = side_sign(half)

    def X(d):           # X at distance d outward from the frame's closing-seam edge
        return "%s(close_gap / 2 + %s)" % ("-" if s < 0 else "", d)
    xsi = X("half_fw - tube_w")                          # side member's bay-side face
    xmi = X("tube_w")                                    # seam member's bay-side face
    yfo, yfi = YW, "%s + tube_w" % YW                    # front member: front and back faces
    ybo, ybi = YB, "%s - back_w" % YB                    # back member: back and front faces
    h = half.lower()

    def along_y(xo, xi):                                 # the side or seam member, cut back at both ends
        return [(xo, "%s + cb45" % yfo), (xo, "%s - cb_sb" % ybo), (xi, "%s - cb_sb" % ybi), (xi, "%s + cb45" % yfi)]
    out = [
        ("SIDE", "m_side", "SIDE MEMBER", "y", along_y(X("half_fw"), X("half_fw - tube_w"))),
        ("SEAM", "m_seam_" + h, "SEAM MEMBER", "y", along_y(X("0 mm"), X("tube_w"))),
        ("FRONT", "m_front_" + h, "FRONT MEMBER", "x", [(X("half_fw - cb45"), yfo), (X("cb45"), yfo),
                                                         (X("tube_w + cb45"), yfi), (X("half_fw - tube_w - cb45"), yfi)]),
        ("BACK", "m_back_" + h, "BACK MEMBER 40X40", "x", [(X("half_fw - cb_bs"), ybo), (X("cb_bs"), ybo),
                                                             (X("tube_w + cb_bs"), ybi),
                                                             (X("half_fw - tube_w - cb_bs"), ybi)]),
    ]
    for k in range(1, 4):
        y0 = cross_y0(k)
        y1 = "%s + tube_w" % y0
        out.append(("X%d" % k, "m_x1" if k == 1 else "m_cross", "CROSS MEMBER %d" % k, "x",
                    [(xsi, y0), (xmi, y0), (xmi, y1), (xsi, y1)]))
    return [(code, key, name, axis, pts, ZF0, ZF1) for code, key, name, axis, pts in out]


def frame_members(half):
    """Members of one ceiling frame in the pod system, as boxes: half 'C1' (-X) or 'C2' (+X).
    The frame is half_fw wide: from the closing seam (X = +-close_gap / 2, the 5.5 mm frame
    gap, R-J11) to the side wall's stop (one seam_gap inside the side frames). With the mitred
    corners (D-117) the side and seam members run the full depth and the front and the 40 x 40
    back member (R-J3) the full width; the cross members stay between the side and the seam.
    Returns [(code, name, axis, (x0, x1, y0, y1, z0, z1))]: each member's bounding box (its
    outline is member_shapes)."""
    out = []
    side = xr(half, "half_fw - tube_w", "half_fw")
    seam = xr(half, "0 mm", "tube_w")
    inner = xr(half, "tube_w", "half_fw - tube_w")
    # each mitred end cut back for its mitre plate (member_shapes): the boxes stop short of the frame's outside by that much
    out.append(("SIDE", "SIDE MEMBER", "y", side + (YW + " + cb45", YB + " - cb_sb", ZF0, ZF1)))
    out.append(("SEAM", "SEAM MEMBER", "y", seam + (YW + " + cb45", YB + " - cb_sb", ZF0, ZF1)))
    out.append(("FRONT", "FRONT MEMBER", "x", xr(half, "cb45", "half_fw - cb45") + (YW, YW + " + tube_w", ZF0, ZF1)))
    out.append(("BACK", "BACK MEMBER 40X40", "x", xr(half, "cb_bs", "half_fw - cb_bs") + (YB + " - back_w", YB, ZF0, ZF1)))
    for k in range(1, 4):
        y0 = cross_y0(k)
        out.append(("X%d" % k, "CROSS MEMBER %d" % k, "x", inner + (y0, y0 + " + tube_w", ZF0, ZF1)))
    return out


def member_wall(key):
    """The member's wall (J-FRAME-01, D-131): cross members 2 and 3 (the plain common part) at 0.8, every other at 1.0."""
    return "tube_t_in" if key == "m_cross" else "tube_t"


def plate_corners(half):
    """The frame's four corners and the mitre plate welded into each (J-FRAME-01, D-131; the joints CAD README's placement):
    [(name, plate key, outer corner (x, y), inner corner (x, y))] in the pod system; the plate's origin sits at the outer
    corner on the skin-side face (Z = ZF1), its +X along the mitre to the inner corner, +Y down across the frame's 40.
    831007 where two 20 x 40 members meet at 45 deg (the front corners), 831008 where a 20 x 40 meets the 40 x 40 back
    member (the back corners)."""
    s = side_sign(half)

    def X(d):
        return "%s(close_gap / 2 + %s)" % ("-" if s < 0 else "", d)
    yfo, yfi, ybo, ybi = YW, "%s + tube_w" % YW, YB, "%s - back_w" % YB
    return [("PLATE FRONT SIDE", "mp45", (X("half_fw"), yfo), (X("half_fw - tube_w"), yfi)),
            ("PLATE FRONT SEAM", "mp45", (X("0 mm"), yfo), (X("tube_w"), yfi)),
            ("PLATE BACK SIDE", "mp_sb", (X("half_fw"), ybo), (X("half_fw - tube_w"), ybi)),
            ("PLATE BACK SEAM", "mp_sb", (X("0 mm"), ybo), (X("tube_w"), ybi))]


PLATE_HW = {"mp45": "plate45", "mp_sb": "plate_sb"}     # plate_corners' keys -> the HARDWARE rows (831007, 831008)


def plate_length(pkey):
    """The mitre plate blank's length along its mitre (the joints register, #308): 26.5 (831007, two 20 x 40) or 41.5
    (831008, 20 x 40 to 40 x 40)."""
    return "mp45_l" if pkey == "mp45" else "mp_sb_l"


def plate_start(pkey):
    """Where the blank starts along its mitre from the frame's outer corner (the joints register, #308): 1.75 (831007)
    or 3.15 (831008)."""
    return "mp45_x0" if pkey == "mp45" else "mp_sb_x0"


def plate_outline(vals, half, name):
    """The mitre plate at one corner, in plan (mm): the Joints Engineer's blank (831007, 831008: native model and STEP,
    #294, shortened in #308), from plate_start to plate_start + plate_length along the mitre from the outer corner and
    mp_t thick, centred on the mitre line. Both square ends sit 0.5 or more inside the frame's faces on both plate
    faces; the weld fills the steps at both ends and is ground flush (J-FRAME-01). [(x, y)], a rectangle."""
    import math
    _n, k, o, i = next(c for c in plate_corners(half) if c[0] == name)
    ox, oy, ix, iy = (ev(vals, e) for e in (o[0], o[1], i[0], i[1]))
    L, t = math.hypot(ix - ox, iy - oy), vals["mp_t"] / 2
    ux, uy = (ix - ox) / L, (iy - oy) / L
    nx, ny = -uy, ux
    a = ev(vals, plate_start(k))
    b = a + ev(vals, plate_length(k))
    ax, ay, bx, by = ox + a * ux, oy + a * uy, ox + b * ux, oy + b * uy
    return [(round(x, 6), round(y, 6)) for x, y in ((ax - t * nx, ay - t * ny), (bx - t * nx, by - t * ny),
                                                    (bx + t * nx, by + t * ny), (ax + t * nx, ay + t * ny))]

def plate_local(pkey):
    """The plate's outline in its own frame [(x, y) expressions], as the Joints Engineer models it: X along its mitre
    from the frame's outer corner (0), the blank from plate_start for plate_length, Y across its mp_t thickness, centred
    (a rectangle: one shape for every corner, never turned over)."""
    t = "mp_t / 2"
    x0, L = plate_start(pkey), plate_length(pkey)
    x1 = "(%s + %s)" % (x0, L)
    return [(x0, "-(%s)" % t), (x1, "-(%s)" % t), (x1, t), (x0, t)]

def plate_places(vals, half):
    """[(name, plate key, origin (x, y, z) mm, angle about Z in degrees, turned over)] for the build: each plate's origin
    at its outer corner at the frame's mid depth, its X turned to the mitre's direction, and turned over about its own X
    where the corner's outline is the standard one mirrored (plate_outline against plate_local)."""
    import math
    out = []
    for name, pkey, o, i in plate_corners(half):
        ox, oy, ix, iy = (ev(vals, e) for e in (o[0], o[1], i[0], i[1]))
        L = math.hypot(ix - ox, iy - oy)
        ux, uy = (ix - ox) / L, (iy - oy) / L
        nx, ny = -uy, ux
        got = sorted((round((x - ox) * ux + (y - oy) * uy, 4), round((x - ox) * nx + (y - oy) * ny, 4))
                     for x, y in plate_outline(vals, half, name))
        std = sorted((round(ev(vals, a), 4), round(ev(vals, b), 4)) for a, b in plate_local(pkey))
        mir = sorted((a, round(-b, 4) + 0.0) for a, b in std)
        got = [(a, b + 0.0) for a, b in got]
        if got == std:
            over = False
        elif got == mir:
            over = True
        else:
            raise ValueError("%s %s: the plate's outline is neither the standard one nor it turned over" % (half, name))
        zc = ev(vals, ZF0) + vals["frame_t"] / 2
        out.append((name, pkey, (ox, oy, zc), math.degrees(math.atan2(uy, ux)), over))
    return out


def plate_boxes(vals, half):
    """[(name, plate key, (x0, x1, y0, y1, z0, z1))] in mm: each mitre plate's box, its plan outline (plate_outline)
    over the frame's depth: the blank's rectangle along the corner's mitre."""
    out = []
    for name, pkey, _o, _i in plate_corners(half):
        pts = plate_outline(vals, half, name)
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        out.append((name, pkey, (min(xs), max(xs), min(ys), max(ys), ev(vals, ZF0), ev(vals, ZF1))))
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
    ys = "ceil_side_y0 + bolt_edge_inset"
    rows = [
        ("SIDE BOLT CLEARANCE", "SIDE", "out", (side_x_out, ys, zc), "hole_clr", "n_ceil_side_bolt", "ceil_side_pitch", "y"),
        ("SIDE BOLT ACCESS", "SIDE", "in", (side_x_in, ys, zc), "hole_acc", "n_ceil_side_bolt", "ceil_side_pitch", "y"),
    ]
    if s < 0:
        rows.append(("SEAM PIN CLEARANCE", "SEAM", "out", (seam_x_out, ys, zc), "hole_clr", "cj_pin_n", "cj_pin_pitch", "y"))
    else:
        rows.append(("SEAM PIN RIVNUT", "SEAM", "out", (seam_x_out, ys, zc), "hole_rvn", "cj_pin_n", "cj_pin_pitch", "y"))
        rows.append(("SEAM PIN ACCESS", "SEAM", "in", (seam_x_in, ys, zc), "hole_acc", "cj_pin_n", "cj_pin_pitch", "y"))
    # the skeleton's back lines start at each frame's outer end (X -/+ ceil_back_x0), first bolt
    # bolt_edge_inset in; a row here starts at its lowest X and runs toward +X
    bx0 = "-(ceil_back_x0 - bolt_edge_inset)" if s < 0 else \
        "(ceil_back_x0 - bolt_edge_inset - (n_ceil_back_bolt - 1) * ceil_back_pitch)"
    rows.append(("BACK RIVNUT", "BACK", "bottom", (bx0, "cj_back_y", ZF0), "hole_rvn", "n_ceil_back_bolt", "ceil_back_pitch", "x"))
    rows.append(("BACK SPIGOT ROUND", "BACK", "bottom", ("%scj_spig_x0" % ("-" if s < 0 else ""), "cj_back_y", ZF0),
                 "spig_hole", "1", "0 mm", "x"))
    hx = "%shang_x" % ("-" if s < 0 else "")
    rows.append(("SOFFIT HANGER FRONT", "FRONT", "bottom", (hx, "%s + tube_w / 2" % YW, ZF0), "hole_rvn", "1", "0 mm", "x"))
    rows.append(("SOFFIT HANGER X1", "X1", "bottom", (hx, "%s + tube_w / 2" % cross_y0(1), ZF0), "hole_rvn", "1", "0 mm", "x"))
    # the soffit's lock rivnuts: in cross member 1 (PM ruling 2026-11-01, DR's new panel face: off C1's front member),
    # mirrored in C2 so cross member 1 stays one part; only C1's take the lock screws (C2's sit over the column)
    rows.append(("SOFFIT LOCK", "X1", "bottom", ("-lock_x" if s < 0 else "lock_x - lock_dx", "%s + tube_w / 2" % cross_y0(1), ZF0),
                 "hole_rvn", "2", "lock_dx", "x"))
    # DT's bolts (J-FRONT-03): Ø7.0 through the front tube's front wall (Y -645) into DT's rivnuts, the head reached
    # through Ø19 in its back wall from the open bay; along DT's edge from C1's frame end at the 220 rule: 3 in C1, 1 in C2
    dx0 = "(-(close_gap / 2 + half_fw) + bolt_edge_inset)"
    first, count = (dx0, "dt_bolt_n - 1") if s < 0 else ("%s + (dt_bolt_n - 1) * dt_pitch" % dx0, "1")
    rows.append(("DT BOLT CLEARANCE", "FRONT", "out", (first, YW, zc), "hole_clr", count, "dt_pitch", "x"))
    rows.append(("DT BOLT ACCESS", "FRONT", "in", (first, "%s + tube_w" % YW, zc), "hole_acc", count, "dt_pitch", "x"))
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


def sleeve_rivnuts():
    """[(name, x, y)] in the pod system: the roof grille's 4 rivnuts in the sleeve's flange over C2's skin, 2 on the
    slot's left side and 2 on its back side behind cross member 1 (J-AIR-03; AIR's air_model.sleeve_rivnuts)."""
    return [("SLEEVE RIVNUT LEFT FRONT", "slot_x0 - slv_rn_e", "slot_y0 + slv_rn_in"),
            ("SLEEVE RIVNUT LEFT BACK", "slot_x0 - slv_rn_e", "slot_y0 + slot_d - slv_rn_in"),
            ("SLEEVE RIVNUT BACK LEFT", "slot_x0 + slv_rn_in", "slv_rn_yb"),
            ("SLEEVE RIVNUT BACK RIGHT", "slot_x0 + slot_w - slv_rn_in", "slv_rn_yb")]


def skin_c2_holes():
    """[(name, x, y)] of the Ø hole_slv clearance holes under the sleeve's rivnuts (D-177), in the C2 skin's own system
    (roof_slot_box's)."""
    ox = "(seam_gap / 2 + half_pw)"
    return [(n, "(%s) - %s" % (x, ox), "(%s) - %s" % (y, YW)) for n, x, y in sleeve_rivnuts()]


# cassette, in CS-510301
CS_X0, CS_X1 = "(-cs_w / 2)", "(cs_w / 2)"
CS_Y0, CS_Y1 = "cs_gap", "(cs_gap + cs_d)"

# The tray's two Ø19.1 cable holes, in its front and back returns on the cassette's centre line,
# mid gap: the one height ELECTRICAL's grommets and draw wire take (F-188, PM ruling 2026-11-01:
# one height for the whole run, read from one shared value). CABLE_HOLE_ZC is local to
# CS-510301 (the tray build cuts the holes there); CABLE_HOLE_Z and CABLE_HOLE_X are the pod's
# (Z 2337.5, X -583 / 583 at P04's values; test_ceiling_offline.py checks both).
CABLE_HOLE_ZC = "-(tray_t + gap_h / 2)"
CABLE_HOLE_Z = "(%s + %s)" % (CASSETTE_CS["C1"][2], CABLE_HOLE_ZC)
CABLE_HOLE_X = {h: CASSETTE_CS[h][0] for h in CASSETTE_CS}
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

def rib_section():
    """The rib's hat section in its own frame, as the build draws it: centre line X 0, the flanges' top at Z 0
    (against the tray base's underside), the crown's underside at Z -gap_h; [(x, z) expressions], the corners in
    order: 0 and 11 the left flange's free edge, 5 and 6 the right one's."""
    c, f, t, h = "rib_crown / 2", "rib_fl", "tray_t", "gap_h"
    return [("-(%s + %s)" % (c, f), "0 mm"), ("-(%s - %s)" % (c, t), "0 mm"), ("-(%s - %s)" % (c, t), "-(%s - %s)" % (h, t)),
            ("(%s - %s)" % (c, t), "-(%s - %s)" % (h, t)), ("(%s - %s)" % (c, t), "0 mm"), ("(%s + %s)" % (c, f), "0 mm"),
            ("(%s + %s)" % (c, f), "-%s" % t), ("(%s)" % c, "-%s" % t), ("(%s)" % c, "-(%s)" % h),
            ("-(%s)" % c, "-(%s)" % h), ("-(%s)" % c, "-%s" % t), ("-(%s + %s)" % (c, f), "-%s" % t)]


# the rib's four folds (real folds: the Lead's ruling 2026-11-01 on #335, the model, its STEP and its DXF agree): the
# outside corners 1, 4, 8 and 9 of rib_section take bend_r + tray_t, the inside corners 10, 2, 3 and 7 bend_r; each
# outside corner pairs with the inside one a sheet away on both axes (1-10, 9-2, 8-3, 4-7)
RIB_FOLDS = [(1, "outside"), (4, "outside"), (8, "outside"), (9, "outside"),
             (10, "inside"), (2, "inside"), (3, "inside"), (7, "inside")]


def rib_fold_radius(side):
    return "bend_r + tray_t" if side == "outside" else "bend_r"


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
              "ceil_side_y0", "ceil_side_pitch", "ceil_back_x0", "ceil_back_pitch", "cj_back_y", "ceil_bolt_z"):
        print(n, round(v[n], 3))
    print(tray_flat(v))
    for half in ("C1", "C2"):
        for name, d, xyz in hole_positions(v, half):
            print(half, name, d, tuple(round(c, 2) for c in xyz))
