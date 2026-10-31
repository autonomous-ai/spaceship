#!/usr/bin/env python3
"""Spaceship (FocusPod v2): packing plan, pallet layouts and the 2-person assembly guide.

One list of shipped pieces drives every output:
  910000_P01_PACKING-LIST_BOM.csv          the packing list, one row per labelled piece
  910000_P01_PACKAGING-PLAN_PKG.md         the packing plan (from templates/packing-plan.md)
  910001_P01_PALLET-1-48X40_PKG.svg        pallet 1 diagram
  910002_P01_PALLET-2-96X48_PKG.svg        pallet 2 diagram
  ../02-Drawings/30-Assembly-Instructions/100000_P04_POD-ASSEMBLY-GUIDE_INS.md
                                           the numbered assembly guide (from templates/assembly-guide.md)

Masses: the layout study's P04 roll-up, ../05-Engineering/layout-study/out/parts-decided-P04.csv, is the
mass source for every part (PM, packing group, 2026-10-31). This script reads it and copies no mass.
Pallet tares, pack allowances and the unit times of the time model come from the layout study's
scripts/inputs.py, read at run time. Every other number is defined below with its status and source.

    python3 v2/07-Packaging/pack.py                 # write every output
    python3 v2/07-Packaging/pack.py --check         # exit 1 if an output is stale or a check fails
    python3 v2/07-Packaging/pack.py --joints PATH   # check the bolt totals against that joints register
"""
import argparse
import copy
import csv
import json
import io
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
LAY = REPO / "v2" / "05-Engineering" / "layout-study"
ROLLUP_CSV = LAY / "out" / "parts-decided-P04.csv"
JOINTS_MD = REPO / "v2" / "05-Engineering" / "joints" / "joints-register.md"
GUIDE_DIR = REPO / "v2" / "02-Drawings" / "30-Assembly-Instructions"

OUT_LIST = HERE / "910000_P01_PACKING-LIST_BOM.csv"
OUT_PLAN = HERE / "910000_P01_PACKAGING-PLAN_PKG.md"
OUT_SVG = {1: HERE / "910001_P01_PALLET-1-48X40_PKG.svg", 2: HERE / "910002_P01_PALLET-2-96X48_PKG.svg"}
OUT_GUIDE = GUIDE_DIR / "100000_P04_POD-ASSEMBLY-GUIDE_INS.md"
TPL_PLAN = HERE / "templates" / "packing-plan.md"
TPL_GUIDE = HERE / "templates" / "assembly-guide.md"

sys.path.insert(0, str(LAY / "scripts"))
from inputs import P as LAYP  # noqa: E402  (the layout study's inputs: value, unit, status, source, note)

KG_PER_LB = 0.45359237
MM_PER_IN = 25.4


def lay(name):
    return LAYP[name].value


def lay_ref(name):
    v = LAYP[name]
    src = f", {v.source}" if v.source else ""
    return f"{v.value} {v.unit} ({v.status}{src}; layout study `{name}`)"


# ------------------------------------------------------------------------------------------- numbers
@dataclass
class N:
    value: float
    unit: str
    status: str
    source: str
    note: str = ""


MINE = {
    # glass crate (packaging part 911001, made)
    "crate_l": N(2200, "mm", "calculation", "this plan", "door unit 2089 + 2 x 5 edge foam + 2 x 45 end rails = 2189, rounded up"),
    "crate_w": N(1219, "mm", "calculation", "this plan", "the full 48 in deck: door 1175 + 2 x 5 edge foam + 2 x 17 side rails = 1219"),
    "crate_side_rail": N(17, "mm", "assumption", "this plan", "plywood side rail, so the 1175 door fits a 1219 crate"),
    "crate_end_rail": N(45, "mm", "assumption", "this plan", "timber end rail"),
    "edge_foam": N(5, "mm", "assumption", "this plan", "closed-cell foam between a glass edge and the crate"),
    "crate_bed": N(15, "mm", "assumption", "this plan", "timber runners and slats under the door layer"),
    "door_blocks": N(75, "mm", "calculation", "this plan", "foam blocks that lift the door's glass clear of its lower pull: 70 mm pull space (FRONT PR #27) + 5"),
    "crate_sep": N(12, "mm", "assumption", "this plan", "plywood separator between the door layer and the fixed glass layer, on posts"),
    "glass_foam": N(10, "mm", "assumption", "this plan", "foam pad above and below a pane"),
    "crate_lid": N(15, "mm", "assumption", "this plan", "slatted lid"),
    "crate_kg": N(30.0, "kg", "assumption", "this plan", "runners, slats, rails, separator, lid and foam; the glass packer's own crate replaces this number"),
    "glass_rest_kg": N(6.0, "kg", "assumption", "this plan", "two padded timber A-frame glass rests, flat-packed in the crate"),
    # pallet 2 tiers
    "sep_h": N(20, "mm", "assumption", "this plan", "tier separator: battens carried on posts, so no load rests on a decor skin, the felt or the glass"),
    "sep_kg": N(4.0, "kg", "assumption", "this plan", "one separator: 5 battens 22 x 95 x 1219 and 4 posts"),
    "cass_foam": N(10, "mm", "assumption", "this plan", "foam sheet under the ceiling cassettes' fill strips on the top tier"),
    # stated limits
    "pal_std_l_exact": N(1219.2, "mm", "calculation", "requirements C1", "48 in exactly; the controlling number for 'fits the pallet'"),
    "pal_std_w_exact": N(1016.0, "mm", "calculation", "requirements C1", "40 in exactly"),
    "pal_long_l_exact": N(2438.4, "mm", "calculation", "requirements C1", "96 in exactly"),
    "time_target_min": N(60, "min", "confirmed", "REQ-ASM-01", "about 1 hour for 2 people"),
    "time_limit_min": N(240, "min", "confirmed", "REQ-ASM-01", "never more than 4 hours"),
    "part_limit_kg": N(20, "kg", "confirmed", "D-03, REQ-LGT-02", "every part except the glass"),
    "door_a": N(810, "mm", "confirmed", "REQ-ASM-06 (rule PROPOSED, ISS-048)", "smallest size of a part must be 810 or less"),
    "door_b": N(2032, "mm", "confirmed", "REQ-ASM-06 (rule PROPOSED, ISS-048)", "middle size of a part must be 2032 or less"),
    "film_faces": N(15, "faces", "calculation", "this plan (D-87)", "faces that show and get film: 8 wall skins, 3 decor blocks, both faces of the door and the fixed glass"),
    "film_faces_all": N(17, "faces", "calculation", "this plan", "every ACP and glass face, the 2 roof skins too: the untrimmed case, for comparison"),
    "long_part": N(1600, "mm", "assumption", "layout study scripts/assembly.py", "a part longer than this, or over 15 kg, is carried by both people"),
    "heavy_part": N(15, "kg", "assumption", "layout study scripts/assembly.py", "see long_part"),
}

# Unit times added by this plan for steps the layout study's model doesn't have. All assumptions until the timed
# prototype trial (REQ-ASM-01: 'then a timed trial on the prototype').
TIME = {
    "t_dr_slide_s": N(120, "s", "assumption", "this plan", "slide DR in from the side onto the fixed glass's right and diagonal edges and onto its stops"),
    "t_slide_long_s": N(120, "s", "assumption", "this plan", "slide one long air part (riser or cartridge) into its housing, 2 people"),
    "t_face_s": N(60, "s", "assumption", "this plan", "lift one felt-covered face or section off, or back on"),
    "t_catch_s": N(60, "s", "assumption", "this plan", "hook one ceiling cassette safety catch (HOLD, D-47)"),
    "t_light_shelf_s": N(600, "s", "assumption", "this plan", "fit and plug the light shelf trims along the wall tops (D-70, not designed yet)"),
    "t_ledge_two_s": N(120, "s", "assumption", "this plan", "hold the 1000 mm ledge in place while it is fixed (D-70, not designed yet)"),
    "t_ledge_one_s": N(600, "s", "assumption", "this plan", "fix the ledge and the screen mount to the work wall's mounting points (D-70, IF-16, not designed yet)"),
    "t_carry_staged_s": N(20, "s", "assumption", "this plan (D-87)", "carry a pallet 2 part that step 1 set down at its place: a few steps"),
    "t_level_preset_s": N(240, "s", "assumption", "this plan (D-87)", "check the band with the spirit level and turn only the glides that are out; glides preset at the factory"),
    "t_hook_s": N(120, "s", "assumption", "this plan (D-87)", "hang a part on its tool-free hooks and check it"),
    "t_selftest_s": N(180, "s", "assumption", "this plan (D-87)", "power on and the hub's self-test: both fan pairs, the lights and the sensors run and it shows pass or fail"),
    "t_peel_tab_s": N(6, "s", "assumption", "this plan (D-87)", "pull one film panel off by its quick-release tab"),
    "t_peel_s": N(20, "s", "assumption", "this plan", "find the edge of a film panel with no tab and peel it, for comparison"),
}

# Site fixings the joints register doesn't count (its section 3.9 lists them as out of scope). Counts are working
# values for the time model and the parts kit until each owner's design gives them.
OTHER_FIXINGS = [
    dict(step=2, where="Base band corner keys (6 keys)", owner="BASE", count=0, size="none on site: hook studs and fixing bolts in the factory",
         status="registered: J-BASE-02 (0 on site, 20 in the factory)", note="D-87: the keys hook in; part numbers 111211 to 111214 (joints register)",
         text="the 6 corner keys hook in, no site bolts (J-BASE-02)"),
    dict(step=9, where="DL on the base band", owner="FRONT and BASE", count=0, size="none: spigots", status="registered: J-FRONT-02 (spigots)",
         note="DL stands on its spigots; its bolts are J-FRONT-01's, into the side walls",
         text="DL stands on its spigots on the band, no bolts (J-FRONT-02)"),
    dict(step=10, where="DR on its support behind the mesh band piece", owner="FRONT and BASE", count=0, size="none: spigots",
         status="registered: J-FRONT-02 (spigots)", note="D-62: the block's own support carries it; the mesh carries no load",
         text="DR stands on its spigots on its support, no bolts (J-FRONT-02)"),
    dict(step=11, where="Door hinges on DL", owner="FRONT", count=0, size="per the named hinge set (HOLD)",
         status="HOLD in the register (D-46, ISS-002)", note="time is in the door step; the hinge halves that sit in DL ship fitted in DL (PM)",
         text="the hinge set's own locking parts (FRONT; the hinges are HOLD until a rated set is named)"),
    dict(step=15, where="Intake riser and supply fan box in DR", owner="AIR and FRONT", count=0, size="not designed yet (HOLD)",
         status="HOLD in the register", note="time is in the step", text="their fixings in DR (AIR and FRONT design, on hold)"),
    dict(step=16, where="Air column", owner="AIR", count=0, size="tool-free hooks (D-87)", status="not designed yet",
         note="time is in the step", text="the column hangs on tool-free hooks (D-87; AIR design)"),
    dict(step=17, where="Soffit with its exhaust fan box", owner="AIR", count=0, size="tool-free hooks (D-87)", status="not designed yet",
         note="time is in the step", text="the soffit hangs on tool-free hooks (D-87; AIR design)"),
    dict(step=19, where="Light shelf", owner="INTERIOR", count=0, size="not designed yet (HOLD)", status="HOLD (D-70)",
         note="time is in the step", text="the light shelf's fixings (INTERIOR design, not designed yet)"),
    dict(step=22, where="Ledge and screen mount", owner="INTERIOR", count=0, size="not designed yet (HOLD)",
         status="HOLD (D-70, IF-16)", note="time is in the step",
         text="their fixings to the work wall's mounting points (INTERIOR design, not designed yet)"),
]


# ------------------------------------------------------------------------------------------- roll-up
def read_rollup(path=ROLLUP_CSV):
    rows = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows[r["item"]] = dict(group=r["group"], qty=float(r["qty"]), kg_each=float(r["kg_each"]),
                                   kg_total=float(r["kg_total"]), status=r["status"], source=r["source"])
    return rows


# Short handles for the roll-up's item texts (exact text, so a change in the roll-up fails loudly).
R = {
    "L1R1": "L1 and R1, lower side outer panels",
    "L2R2": "L2 and R2, upper side outer panels",
    "B": "B1 to B4, back outer panels",
    "TUBES": "40 x 40 corner edge tubes",
    "BOND": "Bond over this study's",
    "CS_LO": "Wall cassette, side, lower",
    "CS_UP": "Wall cassette, side, upper",
    "CB_LO": "Wall cassette, back, lower",
    "CB_UP": "Wall cassette, back, upper",
    "C": "Ceiling outer panels C1 and C2",
    "CC": "Ceiling cassettes",
    "CLIPS": "Named clips and catches",
    "BAND_B": "Base band piece 100x40 - back",
    "BAND_S": "Base band piece 100x40 - side",
    "BAND_FL": "Base band piece 100x40 - front-l",
    "BAND_FR": "Base band piece 100x40 - front-r",
    "KEY": "Corner key",
    "GLIDE": "Levelling glide",
    "BLOCKS": "Glide load blocks",
    "THRESH": "Door threshold",
    "FLOOR": "Floor panels, 9 mm",
    "MAT": "Floor mat",
    "DL": "Decor block - left",
    "DR": "Decor block - right",
    "DT": "Decor block - top",
    "DOOR": "Door unit 360001",
    "FIX": "Fixed glass unit 360002",
    "CART_S": "Supply cartridge",
    "CART_E": "Exhaust cartridge",
    "COLUMN": "Air column",
    "SOFFIT": "Soffit",
    "FANBOX_S": "Supply fan box",
    "FANBOX_E": "Exhaust fan box",
    "RISER": "Intake riser",
    "ROOF": "Roof slot grille",
    "FANS": "Four 12 V fans",
    "SEALS": "Door edge seals, base seal",
    "ELEC": "Switches and harness",   # ELECTRICAL's line: power unit 2.80 kg (in B2) + harness, cord set, hub zone, lights
    "SHELF": "Light shelf",
    "LEDGE": "Work-wall ledge",
    "HW": "M6 bolts, rivnuts",
    "VOICE": "Voice cockpit kit reserve",
}


def resolve(roll, handle):
    """The one roll-up line whose item text starts with this handle's prefix (fails loudly on none or several)."""
    hits = [k for k in roll if k.startswith(R[handle])]
    if len(hits) != 1:
        raise KeyError(f"roll-up handle {handle!r} ('{R[handle]}...') matches {len(hits)} lines: {hits}")
    return hits[0]


# ------------------------------------------------------------------------------------------- pieces
@dataclass
class Piece:
    tag: str            # label number: pallet-slot, e.g. "1-03"
    pn: str             # part number, or "TBD (owner)"
    name: str           # conventions section 5
    vi: str             # Vietnamese name
    pos: str            # position code (conventions section 4), or "-"
    mass: list          # [(roll-up handle, units)] ; units of that roll-up line this piece carries
    dims: tuple         # (long, mid, thin) mm, the packing envelope
    dims_src: str
    pallet: int
    step: int           # assembly step that fits it (0 = not fitted: packaging or a kit)
    group: str
    extra_kg: float = 0.0       # mass not in the roll-up (assumption), with its note
    extra_note: str = ""
    extra_status: str = "assumption"
    glass: bool = False
    kind: str = "piece"         # piece | allowance | later
    note: str = ""
    kg: float = 0.0
    status: str = ""


def S(*a):
    return tuple(sorted(a, reverse=True))


P04 = "skeleton P04 (S33)"
# ELECTRICAL's roll-up line (S43) is 4.94 kg: the power unit in B2 2.80, harness parts 1.00, cord set 0.50, hub zone 0.38, lights 0.26.
POWER_UNIT_SHARE = 2.80 / 4.94
# The fixed glass unit's roll-up line is FRONT's 29.58 kg (PR #28 parts list): pane 28.584, 180 seal 0.2, U-profile 0.557 and
# U-seal 0.241 in four pieces, 745 bottom, 1446 right, 804 diagonal and 303 top (mm). The channels ship fitted in the parts
# that hold them: the bottom one on BASE's sill (PM ruling), the right and diagonal in DR, the top in DT (D-68).
FIX_UNIT_KG = 29.58
CHANNEL_KG_PER_MM = (0.557 + 0.241) / (745 + 1446 + 804 + 303)
SILL_CHANNEL_SHARE = 745 * CHANNEL_KG_PER_MM / FIX_UNIT_KG
DR_CHANNEL_SHARE = (1446 + 804) * CHANNEL_KG_PER_MM / FIX_UNIT_KG
DT_CHANNEL_SHARE = 303 * CHANNEL_KG_PER_MM / FIX_UNIT_KG
PANE_SHARE = 1 - SILL_CHANNEL_SHARE - DR_CHANNEL_SHARE - DT_CHANNEL_SHARE
PIECES = [
    # ---------------- pallet 1, 48 x 40 in: upright stack, listed from the open face (first out) to the back
    Piece("1-01", "111401", "BASE - FLOOR PANEL - F1", "Tấm sàn mỏng - F1", "F1", [("FLOOR", 1), ("MAT", 0.5)], S(1455, 1219, 12),
          "1455 deep (skeleton P04, S33); 1219 wide at most with its lap (PM ruling, packing group); 9 mm ply (D-72) + 3 mm foam (D-76)",
          1, 3, "BASE", note="foam mat 111501 bonded under it at the factory (D-87)"),
    Piece("1-02", "TBD (BASE)", "BASE - FLOOR PANEL - F2", "Tấm sàn mỏng - F2", "F2", [("FLOOR", 1), ("MAT", 0.5)], S(1455, 1219, 12),
          "as F1", 1, 3, "BASE", note="foam mat bonded under it at the factory (D-87)"),
    Piece("1-03", "TBD (WALL)", "WALL - PANEL ASSY - BACK LOWER - LH", "Vách hậu - cụm tấm dưới trái", "B1", [("B", 1)],
          S(1200.61, 1118.61, 46), P04, 1, 4, "WALL"),
    Piece("1-04", "TBD (WALL)", "WALL - PANEL ASSY - BACK LOWER - RH", "Vách hậu - cụm tấm dưới phải", "B2",
          [("B", 1), ("ELEC", POWER_UNIT_SHARE)], S(1200.61, 1118.61, 84),
          "skeleton P04 (S33); the power unit's face stands 38 mm proud of the frame face: felt plane Y 766 against the frame at Y 804 (ELECTRICAL PR #64, calculation)",
          1, 4, "WALL",
          note="carries the power unit 710001, fitted, wired and tested at the factory: 2.80 kg of ELECTRICAL's roll-up line (S43); foam block over the unit's face in the stack"),
    Piece("1-05", "210101", "WALL - PANEL ASSY - SIDE LOWER - LH", "Vách trái - cụm tấm dưới", "L1", [("L1R1", 1)],
          S(1492.74, 1142.74, 46), P04 + "; WALL L1 CAD", 1, 5, "WALL"),
    Piece("1-06", "TBD (WALL)", "WALL - PANEL ASSY - SIDE LOWER - RH", "Vách phải - cụm tấm dưới", "R1", [("L1R1", 1)],
          S(1492.74, 1142.74, 46), P04, 1, 5, "WALL"),
    Piece("1-07", "TBD (WALL)", "WALL - PANEL ASSY - BACK UPPER - LH", "Vách hậu - cụm tấm trên trái", "B3", [("B", 1)],
          S(1200.61, 1118.61, 46), P04, 1, 6, "WALL"),
    Piece("1-08", "TBD (WALL)", "WALL - PANEL ASSY - BACK UPPER - RH", "Vách hậu - cụm tấm trên phải", "B4", [("B", 1)],
          S(1200.61, 1118.61, 46), P04, 1, 6, "WALL"),
    Piece("1-09", "TBD (WALL)", "WALL - PANEL ASSY - SIDE UPPER - LH", "Vách trái - cụm tấm trên", "L2", [("L2R2", 1)],
          S(1492.74, 1142.74, 46), P04, 1, 7, "WALL"),
    Piece("1-10", "TBD (WALL)", "WALL - PANEL ASSY - SIDE UPPER - RH", "Vách phải - cụm tấm trên", "R2", [("L2R2", 1)],
          S(1492.74, 1142.74, 46), P04, 1, 7, "WALL"),
    Piece("1-11", "410101", "CEILING - PANEL ASSY - C1", "Trần - tấm trái (cụm)", "C1", [("C", 1)],
          S(1495, 1203.61, 46), "CEILING PR #32 CAD skin 1203.61 x 1495; 46 mm outer panel (P04)", 1, 8, "CEILING"),
    Piece("1-12", "410102", "CEILING - PANEL ASSY - C2", "Trần - tấm phải (cụm)", "C2", [("C", 1), ("ROOF", 1)],
          S(1495, 1203.61, 60), "as C1; the roof sleeve stands 14 mm below the frame (air report 7e)", 1, 8, "CEILING",
          note="roof slot grille and sleeve fitted at the factory (PROPOSED)"),
    Piece("1-13", "TBD (WALL)", "LINING - CASSETTE - SIDE LOWER - RH", "Cassette tiêu âm - vách phải dưới", "R1", [("CS_LO", 1)],
          S(1445, 1142.74, 34), P04, 1, 14, "LINING"),
    Piece("1-14", "TBD (WALL)", "LINING - CASSETTE - SIDE UPPER - RH", "Cassette tiêu âm - vách phải trên", "R2", [("CS_UP", 1)],
          S(1445, 1092.74, 34), P04, 1, 14, "LINING"),
    Piece("1-15", "510101", "LINING - CASSETTE - SIDE LOWER - LH", "Cassette tiêu âm - vách trái dưới", "L1", [("CS_LO", 1)],
          S(1445, 1142.74, 34), P04 + "; WALL L1 CAD", 1, 14, "LINING"),
    Piece("1-16", "TBD (WALL)", "LINING - CASSETTE - SIDE UPPER - LH", "Cassette tiêu âm - vách trái trên", "L2", [("CS_UP", 1)],
          S(1445, 1092.74, 34), P04, 1, 14, "LINING"),
    Piece("1-17", "TBD (WALL)", "LINING - CASSETTE - BACK LOWER - LH", "Cassette tiêu âm - vách hậu dưới trái", "B1", [("CB_LO", 1)],
          S(1166, 1118.61, 34), P04, 1, 14, "LINING"),
    Piece("1-18", "TBD (WALL)", "LINING - CASSETTE - BACK LOWER - RH", "Cassette tiêu âm - vách hậu dưới phải", "B2", [("CB_LO", 1)],
          S(1166, 1118.61, 34), P04, 1, 14, "LINING"),
    Piece("1-19", "TBD (WALL)", "LINING - CASSETTE - BACK UPPER - LH", "Cassette tiêu âm - vách hậu trên trái", "B3", [("CB_UP", 1)],
          S(1166, 1116.87, 34), P04, 1, 14, "LINING"),
    Piece("1-20", "TBD (WALL)", "LINING - CASSETTE - BACK UPPER - RH", "Cassette tiêu âm - vách hậu trên phải", "B4", [("CB_UP", 1)],
          S(1166, 1116.87, 34), P04, 1, 14, "LINING"),
    # ---------------- pallet 2, 96 x 48 in: tiers, bottom (tier 1) to top (tier 5)
    Piece("2-01", "360002", "FRONT - FIXED GLASS UNIT", "Cụm vách kính cố định", "-", [("FIX", PANE_SHARE)], S(2033, 1031, 12),
          "FRONT PR #28 CAD: pane 1026.23 x 2033 with the 180 seal on its free edge", 2, 10, "FRONT", glass=True,
          note="the pane with its 180 seal; its U-channels and seals ship fitted on the sill (PM ruling), in DR and in DT (D-68)"),
    Piece("2-02", "360001", "FRONT - DOOR UNIT", "Cụm cửa kính", "-", [("DOOR", 1)], S(2089, 1175, 149),
          "FRONT PR #27 CAD: Z 27 to 2116, glass 1175 wide, pull spaces 149 deep; hinge halves that sit in DL ship in DL (PM ruling)",
          2, 11, "FRONT", glass=True),
    Piece("2-03", "TBD (FRONT)", "FRONT - DECOR BLOCK - DR", "Khung trang trí - khối phải", "DR", [("DR", 1), ("FIX", DR_CHANNEL_SHARE)], S(2290, 1016, 205),
          "layout study bounding box (S02); the real block is faceted", 2, 10, "FRONT"),
    Piece("2-04", "110103", "BASE - BAND ASSY - BACK", "Viền chân nhôm - cạnh sau (cụm)", "-", [("BAND_B", 1), ("GLIDE", 3), ("BLOCKS", 3 / 8)],
          S(2420, 110, 40), "BASE P01 CAD 111103 (2420 x 40 x 100) + glides 10 below", 2, 2, "BASE", note="3 glides fitted, each on its aluminium load block inside the band (BASE CAD; D-86); blocks split by glide count, 3 of 8"),
    Piece("2-05", "110101", "BASE - BAND ASSY - SIDE - LH", "Viền chân nhôm - cạnh trái (cụm)", "-", [("BAND_S", 1), ("GLIDE", 2), ("BLOCKS", 2 / 8)],
          S(1517, 110, 40), "BASE P01 CAD 111101 (outer face 1517) + glides", 2, 2, "BASE",
          note="2 glides fitted, each on its load block inside the band (BASE CAD; D-86)"),
    Piece("2-06", "TBD (BASE)", "BASE - BAND ASSY - SIDE - RH", "Viền chân nhôm - cạnh phải (cụm)", "-", [("BAND_S", 1), ("GLIDE", 2), ("BLOCKS", 2 / 8)],
          S(1517, 110, 40), "LH's mirror (BASE P01 CAD)", 2, 2, "BASE",
          note="2 glides fitted, each on its load block inside the band (D-86)"),
    Piece("2-07", "TBD (BASE)", "BASE - BAND ASSY - FRONT - RH - UNDER THE FIXED GLASS", "Viền chân nhôm - trước phải, dưới kính", "-",
          [("BAND_FR", 0.663), ("GLIDE", 1), ("BLOCKS", 1 / 8), ("FIX", SILL_CHANNEL_SHARE)], S(729, 110, 40),
          "X 218 to about 947 (skeleton P04 front band; air report 7e); carries the glass's bottom U-channel (D-68)", 2, 2, "BASE",
          note="the sill: the fixed glass's bottom U-channel and its seal fitted at the factory with 4 M3 countersunk screws (PM ruling); share of the front-r line by length, 729 of 1100 mm (calculation); 1 glide on its load block (D-86)"),
    Piece("2-08", "TBD (BASE)", "BASE - DOOR THRESHOLD - 13 MM", "Ngưỡng cửa thấp 13 mm", "-", [("THRESH", 1)], S(1175, 60, 13),
          "skeleton P04 1175 x 60; 13 mm high (D-72)", 2, 3, "BASE"),
    Piece("2-09", "TBD (FRONT)", "FRONT - DECOR BLOCK - DL", "Khung trang trí - khối trái", "DL", [("DL", 1)], S(2290, 278, 205),
          "layout study bounding box (S02)", 2, 9, "FRONT", note="the hinge halves that sit in DL ship fitted in it (PM ruling)"),
    Piece("2-10", "TBD (AIR)", "AIR - SOFFIT WITH THE EXHAUST FAN BOX AND 2 FANS", "Hộp gió trên cửa + hộp quạt thải", "-",
          [("SOFFIT", 1), ("FANBOX_E", 1), ("FANS", 0.5)], S(2332, 360, 220),
          "air report 7e: the fan box (X 867 to 1161, Z 2162 to 2335) sits inside the soffit's envelope", 2, 17, "AIR",
          note="exhaust fan box with its 2 fans fitted inside the soffit's right end at the factory (D-87)"),
    Piece("2-11", "TBD (AIR)", "AIR - AIR COLUMN", "Cột dẫn gió", "-", [("COLUMN", 1)], S(2105, 360, 217), "air report 7e", 2, 16, "AIR"),
    Piece("2-12", "TBD (FRONT)", "FRONT - DECOR BLOCK - DT", "Khung trang trí - khối trên", "DT", [("DT", 1), ("FIX", DT_CHANNEL_SHARE)], S(1697, 280, 205),
          "layout study bounding box (S02)", 2, 12, "FRONT"),
    Piece("2-13", "TBD (ELECTRICAL)", "ELECTRICAL - KIT - HARNESS, CORD SET, HUB ZONE, LIGHTS", "Bộ điện: dây, dây nguồn, hub, đèn", "-", [("ELEC", 1 - POWER_UNIT_SHARE)],
          S(600, 250, 200), "carton (assumption)", 2, 13, "ELECTRICAL"),
    Piece("2-14", "TBD (INTERIOR)", "INTERIOR - LIGHT SHELF", "Kệ đèn", "-", [("SHELF", 1)], S(2332, 80, 50),
          "bundle (assumption): the roll-up's 4.43 m in lengths up to the 2332 back wall", 2, 19, "INTERIOR"),
    Piece("2-15", "TBD (BASE)", "BASE - SMALL PARTS CARTON", "Thùng phụ kiện đế", "-",
          [("BAND_FL", 1), ("BAND_FR", 0.337), ("KEY", 6)], S(600, 400, 150),
          "carton (assumption): front-left band piece (faceted, under DL), mesh intake piece under DR with DR's support and the closing plate (D-62), 6 corner keys",
          2, 2, "BASE", note="mesh piece share of the front-r line by length, 371 of 1100 mm (calculation)"),
    Piece("2-16", "TBD (INTERIOR)", "INTERIOR - LEDGE AND SCREEN MOUNT CARTON", "Kệ làm việc + giá màn hình", "-", [("LEDGE", 1)], S(1000, 250, 120),
          "carton (assumption): the 1000 mm ledge (D-70) with its 2 brackets, and the screen mount", 2, 22, "INTERIOR",
          extra_kg=1.0, extra_note="screen mount, not in the roll-up (D-70, IF-16; assumption)"),
    Piece("2-17", "TBD (AIR)", "AIR - INTAKE RISER WITH THE SUPPLY FAN BOX AND 2 FANS", "Ống hút gió đứng + hộp quạt cấp", "-",
          [("RISER", 1), ("FANBOX_S", 1), ("FANS", 0.5)], S(1845, 460, 155),
          "air report 7e: riser Z 105 to 1445 joined to the fan box Z 1650 to 1950, X 645 to 1094 (calculation)", 2, 15, "AIR",
          note="riser and supply fan box joined at the factory, one plug-in connector (D-87)"),
    Piece("2-18", "TBD (AIR)", "AIR - CARTRIDGE - SUPPLY", "Ống tiêu âm cấp gió", "-", [("CART_S", 1)], S(1750, 314, 173),
          "air report 7e", 2, 16, "AIR"),
    Piece("2-19", "TBD (AIR)", "AIR - CARTRIDGE - EXHAUST", "Ống tiêu âm thải gió", "-", [("CART_E", 1)], S(1750, 314, 173),
          "air report 7e (same part as the supply cartridge)", 2, 17, "AIR"),
    Piece("2-20", "510301", "LINING - CASSETTE - CEILING - COMMON", "Cassette trần (dùng chung)", "C1", [("CC", 1)], S(1163, 1048, 74),
          "CEILING PR #32 CAD: returns 1163 x 1048, tray 34 + fill 40", 2, 18, "LINING"),
    Piece("2-21", "510301", "LINING - CASSETTE - CEILING - COMMON", "Cassette trần (dùng chung)", "C2", [("CC", 1)], S(1163, 1048, 74),
          "as 2-22", 2, 18, "LINING"),
    Piece("2-22", "109000", "POD - INSTALLATION KIT (OPEN FIRST)", "Bộ phụ kiện lắp (mở trước)", "-", [], S(300, 150, 80),
          "carton (assumption)", 2, 1, "KIT", extra_kg=0.5,
          extra_note="not in the roll-up: the 5 mm hex key 108001, spare bolts and washers, this guide, the label map (assumption)"),
    # ---------------- allowances: roll-up mass that rides inside the pieces above, with no label of its own
    Piece("A-1", "-", "40 x 40 corner edge tubes in L2, R2, C1, C2 (D-63)", "", "-", [("TUBES", 1)], (0, 0, 0), "-", 1, 0, "WALL", kind="allowance"),
    Piece("A-2", "-", "Bond beyond L1 and R1 (D-71)", "", "-", [("BOND", 1)], (0, 0, 0), "-", 1, 0, "WALL", kind="allowance"),
    Piece("A-3", "-", "Captive bolts, washers, rivnuts, stop washers, spigots, gaskets, fitted in the panels", "", "-",
          [("HW", 1)], (0, 0, 0), "-", 1, 0, "WALL", kind="allowance"),
    Piece("A-4", "-", "Door edge seals, base seal, grommets, fitted on the band, DL, DT and the panels", "", "-",
          [("SEALS", 1)], (0, 0, 0), "-", 2, 0, "BASE", kind="allowance"),
    Piece("L-1", "-", "Voice cockpit kit reserve: ships later, outside the cap (D-11, D-81)", "", "-", [("VOICE", 1)], (0, 0, 0), "-",
          0, 0, "ELECTRICAL", kind="later"),
    Piece("A-5", "-", "Wall cassette clips: 32 of the 44 named clips, on the wall panels and cassettes", "", "-",
          [("CLIPS", 1.28 / 2.16)], (0, 0, 0), "-", 1, 0, "LINING", kind="allowance",
          note="split by count at the roll-up's 40 g a clip and 100 g a lanyard (calculation)"),
    Piece("A-6", "-", "Ceiling clips and catches: 12 clips and 4 lanyards, with the ceiling cassettes", "", "-",
          [("CLIPS", 0.88 / 2.16)], (0, 0, 0), "-", 2, 0, "LINING", kind="allowance",
          note="split by count at the roll-up's 40 g a clip and 100 g a lanyard (calculation)"),
]

PIECE = {p.tag: p for p in PIECES}

# Each label's body in skeleton P04's STEP (v2/03-Manufacturing/skeleton/), for the step pictures. The air parts, kits and
# cartons have no skeleton body yet; the step pictures show them when their own CAD lands.
SKELETON_STEP = REPO / "v2" / "03-Manufacturing" / "skeleton" / "100000_P04_POD-SKELETON_STEP.step"
SKEL = {
    "1-01": ["F1 ENVELOPE"], "1-02": ["F2 ENVELOPE"],
    "1-03": ["B1 ENVELOPE"], "1-04": ["B2 ENVELOPE"], "1-05": ["L1 ENVELOPE"], "1-06": ["R1 ENVELOPE"],
    "1-07": ["B3 ENVELOPE"], "1-08": ["B4 ENVELOPE"], "1-09": ["L2 ENVELOPE"], "1-10": ["R2 ENVELOPE"],
    "1-11": ["C1 ENVELOPE"], "1-12": ["C2 ENVELOPE"],
    "1-13": ["R1-CASS ENVELOPE"], "1-14": ["R2-CASS ENVELOPE"], "1-15": ["L1-CASS ENVELOPE"], "1-16": ["L2-CASS ENVELOPE"],
    "1-17": ["B1-CASS ENVELOPE"], "1-18": ["B2-CASS ENVELOPE"], "1-19": ["B3-CASS ENVELOPE"], "1-20": ["B4-CASS ENVELOPE"],
    "2-01": ["FIXED GLASS"], "2-02": ["DOOR GLASS", "KICK ENVELOPE"], "2-03": ["DR FACETED"],
    "2-04": ["BAND-BACK ENVELOPE"], "2-05": ["BAND-L ENVELOPE"], "2-06": ["BAND-R ENVELOPE"], "2-07": ["BAND-FR ENVELOPE"],
    "2-08": ["THRESHOLD ENVELOPE"], "2-09": ["DL FACETED"], "2-12": ["DT FACETED"], "2-15": ["BAND-FL ENVELOPE"],
    "2-20": ["C1-CASS ENVELOPE"], "2-21": ["C2-CASS ENVELOPE"],
}
# Camera per step for the pictures: "back" looks from behind, left and above; "front" from the front, right and above;
# "inside" from above with the ceiling and the front hidden, to show the linings.
STEP_VIEW = {2: "back", 3: "back", 4: "back", 5: "back", 6: "back", 7: "back", 8: "back", 9: "front", 10: "front", 11: "front",
             12: "front", 14: "inside", 18: "inside"}
OUT_STEP_BODIES = GUIDE_DIR / "100000_P04_POD-ASSEMBLY-GUIDE-STEP-BODIES_DATA.json"


def step_image(n):
    return GUIDE_DIR / "img" / ("100000_P04_POD-ASSEMBLY-GUIDE-STEP-%02d_IMG.png" % n)


def skeleton_bodies(path=SKELETON_STEP):
    return sorted(set(re.findall(r"MANIFOLD_SOLID_BREP\('([^']*)'", Path(path).read_text(encoding="utf-8", errors="replace"))))


def step_bodies_json():
    rows = []
    for st in STEPS:
        new = [b for t in st["tags"] for b in SKEL.get(t, [])]
        if not new:
            continue
        rows.append(dict(step=st["n"], title=st["title"], view=STEP_VIEW.get(st["n"], "front"), new=new,
                         image=str(step_image(st["n"]).relative_to(REPO))))
    return json.dumps(dict(source=str(SKELETON_STEP.relative_to(REPO)), steps=rows), indent=1) + "\n"

# ---------------- packaging (910000 PACKAGING), part numbers PROPOSED in the 91 band (conventions section 6)
PACKAGING = [
    dict(pn="910001", name="PACKAGING - PALLET LOAD 1 - 48 X 40", kind="assembly", qty=1, kg=None, status="-", src="this plan"),
    dict(pn="910002", name="PACKAGING - PALLET LOAD 2 - 96 X 48", kind="assembly", qty=1, kg=None, status="-", src="this plan"),
    dict(pn="918001", name="PACKAGING - PALLET - 48 X 40 IN, NEW WOOD, 4-WAY (GMA)", kind="bought", qty=1, kg=lay("pal_std_kg"),
         status=LAYP["pal_std_kg"].status, src="layout study S14 (PHS S-4840, 44 lb)", pallet=1),
    dict(pn="918002", name="PACKAGING - PALLET - 96 X 48 IN, NEW WOOD, 4-WAY", kind="bought", qty=1, kg=lay("pal_long_kg"),
         status=LAYP["pal_long_kg"].status, src="layout study S15 (Uline H-1627, 107 lb)", pallet=2),
    dict(pn="911001", name="PACKAGING - GLASS CRATE", kind="made", qty=1, kg=MINE["crate_kg"].value,
         status="assumption", src="this plan (crate_kg)", pallet=2),
    dict(pn="911002", name="PACKAGING - GLASS REST, A-FRAME, PADDED (PAIR)", kind="made", qty=1, kg=MINE["glass_rest_kg"].value,
         status="assumption", src="this plan (glass_rest_kg); flat-packed in the crate", pallet=2),
    dict(pn="911003", name="PACKAGING - TIER SEPARATOR (BATTENS ON POSTS)", kind="made", qty=4, kg=MINE["sep_kg"].value,
         status="assumption", src="this plan (sep_kg)", pallet=2),
    dict(pn="918010", name="PACKAGING - PROTECTION SET, 48 X 40: edge boards, corner guards, foam interleaf, PE sheets, cap board, straps, film",
         kind="bought", qty=1, kg=lay("pack_kg_std"), status=LAYP["pack_kg_std"].status, src="layout study pack_kg_std", pallet=1),
    dict(pn="918011", name="PACKAGING - PROTECTION SET, 96 X 48: corner guards, foam, PE sheets, cap board, straps, film",
         kind="bought", qty=1, kg=lay("pack_kg_long"), status=LAYP["pack_kg_long"].status, src="layout study pack_kg_long", pallet=2),
    dict(pn="911010", name="PACKAGING - PART LABEL, 100 X 150 MM, ONE PER PIECE", kind="made", qty=None, kg=0.0, status="-", src="this plan"),
    dict(pn="911011", name="PACKAGING - PALLET LABEL AND DOCUMENT POUCH, 2 PER PALLET", kind="made", qty=4, kg=0.0, status="-", src="this plan"),
]

# ------------------------------------------------------------------------------------------- pallet layouts
# Pallet 1: one upright stack across the 40 in side, parts on edge with their along-size on the 48 in side.
# Listed from the open face. Felt faces meet felt faces (cassettes paired), ACP faces meet ACP faces (outer panels paired).
STACK1 = ["1-%02d" % i for i in range(1, 21)]

# Pallet 2: tiers from the deck up. Each lane runs along the 96 in side; its parts lie end to end.
TIERS2 = [
    dict(name="Tier 1: glass crate", height=None, crate=True, lanes=[dict(width=1219, tags=["CRATE"])]),
    dict(name="Tier 2: DR and the base band", height=205, lanes=[
        dict(width=1016, tags=["2-03"]),
        dict(width=50, tags=["2-04"], on_edge=True),
        dict(width=50, tags=["2-05", "2-07"], on_edge=True),
        dict(width=50, tags=["2-06"], on_edge=True),
        dict(width=40, tags=["2-08"], on_edge=True)]),
    dict(name="Tier 3: DL, soffit, air column, DT", height=360, lanes=[
        dict(width=278, tags=["2-09"]),
        dict(width=360, tags=["2-10"]),
        dict(width=217, tags=["2-11"], on_edge=True),
        dict(width=280, tags=["2-12", "2-13"]),
        dict(width=80, tags=["2-14"])]),
    dict(name="Tier 4: air parts and cartons", height=320, lanes=[
        dict(width=460, tags=["2-17"]),
        dict(width=400, tags=["2-15", "2-16"]),
        dict(width=173, tags=["2-18"], on_edge=True),
        dict(width=173, tags=["2-19"], on_edge=True)]),
    dict(name="Tier 5: ceiling cassettes (felt up, nothing on them) and the kit", height=None, lanes=[
        dict(width=1048, tags=["2-20", "2-21"]),
        dict(width=150, tags=["2-22"])]),
]
CRATE_TAGS = ["2-02", "2-01"]   # inside the crate, bottom to top: door, then the fixed glass (fitted first)

GROUP_COLOUR = {"BASE": "#8d6e63", "WALL": "#c9a227", "CEILING": "#d9b44a", "LINING": "#7f8c8d", "FRONT": "#2f6f8f",
                "AIR": "#4e9a6e", "ELECTRICAL": "#9b59b6", "INTERIOR": "#b5651d", "KIT": "#555555", "PACK": "#bbbbbb"}


# ------------------------------------------------------------------------------------------- assembly steps
def op(text, who, secs, n=1, src=""):
    return dict(text=text, who=who, secs=float(secs), n=n, src=src)


def carry(tag):
    """Carry one piece to its place: from pallet 1's stack, or a few steps for a pallet 2 part that step 1 set down at its place (D-87)."""
    p = PIECE[tag]
    both = p.glass or p.kg > MINE["heavy_part"].value or p.dims[0] > MINE["long_part"].value
    staged = p.pallet == 2
    secs = TIME["t_carry_staged_s"].value if staged else lay("t_carry_s")
    return op(f"carry {tag} {p.pos if p.pos != '-' else ''}".strip(), 2 if both else 1, secs, 1,
              "t_carry_staged_s" if staged else "t_carry_s")


BOLT = lay("t_bolt_captive_s")

# joints: {joint ID: [count, size]} for the bolts of the joints register; other: [(text, count)] for the rest
STEPS = [
    dict(n=1, title="Unpack and set the parts down at their places", tags=["2-22"],
         A="Cuts the straps and film on pallet 2 and hands the tiers down, top first: the OPEN FIRST kit and the ceiling cassettes, then tiers 4 to 2. Leaves the glass crate closed on the pallet.",
         B="Sets every part from pallet 2 down at its own place round the pod, as the label map shows, felt and ACP faces up on floor protection; opens the kit (hex key, this guide, label map) and ticks the packing list.",
         check="Every label on the packing list is found and lies at its place. Nothing leans on the glass crate. Pallet 1 stays strapped until step 3.",
         ops=[op("open pallet 1, packed in fitting order", 2, lay("t_unpack_std_ordered_min") * 60, 1, "t_unpack_std_ordered_min"),
              op("unload pallet 2 tiers 5 to 2, each part to its place", 2, lay("t_unpack_long_ordered_min") * 60, 1, "t_unpack_long_ordered_min")],
         joints={}),
    dict(n=2, title="Base band", tags=["2-04", "2-05", "2-06", "2-07", "2-15"],
         A="Sets the back band on its glides, then the left and right side bands, each hooked onto its corner key, then the front pieces: front-left under DL, the piece under the fixed glass, and the mesh intake piece under DR with DR's support and closing plate. Every piece locates itself on its key.",
         B="Checks the band with the spirit level, corner to corner, and turns only the glides that are out, from above with the hex key. The glides come preset from the factory (D-87); the glide is HOLD and must take the same 5 mm key (REQ-ASM-03).",
         check="Band level within the spirit level's bubble; every corner key hooked home; the mesh piece's support stands; the fixed glass's U-channel, fitted on the sill at the factory, is clean and undamaged.",
         ops=[carry("2-04"), carry("2-05"), carry("2-06"), carry("2-07"), carry("2-15"),
              op("set each band piece on its keys", 2, lay("t_place_hung_s"), 6, "t_place_hung_s"),
              op("check the level, turn the glides that are out", 2, TIME["t_level_preset_s"].value, 1, "t_level_preset_s")],
         joints={}),
    dict(n=3, title="Floor and threshold", tags=["1-01", "1-02", "2-08"],
         A="Lays floor panel F1 (left), its foam already bonded underneath (D-87), lapped edge up.",
         B="Lays F2 (right) into F1's lap, then sets the 13 mm threshold across the door opening, level with the floor.",
         check="Floor flat, no gap at the lap; the base seal 118001 at the floor's edge closes the 4 mm gap to the band's inner face all round (D-86); threshold seated; cover the floor with the packing film for the rest of the work.",
         ops=[carry("1-01"), carry("1-02"), carry("2-08"),
              op("lay each floor panel and the threshold", 2, lay("t_place_s"), 3, "t_place_s")],
         joints={}),
    dict(n=4, title="Lower back wall: B1, B2", tags=["1-03", "1-04"],
         A="Stands B1 on its band spigots (round hole and slot), skin out, and holds it upright; then B2 the same, against B1. B2 carries the power unit, wired and tested at the factory (11.6 kg).",
         B="From inside, through the fill pockets: first the 3 pins of the B1-B2 closing seam, snug only; then B1's and B2's 4 base bolts each (pins first: joints register 2.7, R-J11).",
         check="Both panels sit down on their stops; the B1-B2 gap looks even top to bottom (5.5 mm nominal).",
         ops=[carry("1-03"), carry("1-04"),
              op("set each panel on its spigots", 2, lay("t_place_hung_s"), 2, "t_place_hung_s")],
         joints={"J-BASE-01": 8, "J-WALL-03": 3}),
    dict(n=5, title="Lower side walls: L1, R1", tags=["1-05", "1-06"],
         A="Stands L1 on its band spigots against B1's edge and holds it; then R1 against B2.",
         B="Drives the 4 base bolts of each, then the 3 lower back-corner bolts each side (L1-B1, R1-B2), from the back panels' bays.",
         check="Corners closed onto their stops; side panels' front edges in line with the band's front end.",
         ops=[carry("1-05"), carry("1-06"),
              op("set each panel on its spigots", 2, lay("t_place_hung_s"), 2, "t_place_hung_s")],
         joints={"J-BASE-01": 8, "J-WALL-02": 6}),
    dict(n=6, title="Upper back wall: B3, B4", tags=["1-07", "1-08"],
         A="Lifts B3 onto B1's top spigots (step stool), then B4 onto B2's, dropping past the closing seam's lead-in chamfer.",
         B="First the 3 pins of the B3-B4 closing seam, snug only; then the 4 horizontal-seam bolts under each (B1-B3, B2-B4).",
         check="Seams closed; skins flush across the horizontal seam.",
         ops=[carry("1-07"), carry("1-08"),
              op("set each panel on its spigots", 2, lay("t_place_hung_s"), 2, "t_place_hung_s")],
         joints={"J-WALL-01": 8, "J-WALL-03": 3}),
    dict(n=7, title="Upper side walls: L2, R2", tags=["1-09", "1-10"],
         A="Lifts L2 onto L1's spigots against B3's edge, then R2 onto R1 against B4.",
         B="Drives the 4 horizontal-seam bolts each (L1-L2, R1-R2), then the 3 upper back-corner bolts each side (L2-B3, R2-B4) FINGER-TIGHT only.",
         check="The 6 upper corner bolts are finger-tight, so the wall tops can follow the ceiling (R-J9).",
         ops=[carry("1-09"), carry("1-10"),
              op("set each panel on its spigots", 2, lay("t_place_hung_s"), 2, "t_place_hung_s")],
         joints={"J-WALL-01": 8, "J-WALL-02": 6}),
    dict(n=8, title="Ceiling: C1, C2", tags=["1-11", "1-12"],
         A="With B on a second stool, lifts C1 from inside onto its back spigots (on B3), its side against L2; then C2 the same, dropping past C1's lead-in. C2 carries the roof slot.",
         B="Drives the 4 pins of the C1-C2 closing seam, then the 8 back-edge bolts up from the back panels' top bays, then the 8 side-edge bolts; last, tightens the 6 upper corner bolts left finger-tight in step 7.",
         check="Ceiling seams closed; the C1-C2 gap even (4.3 to 6.7 mm); all 6 upper corner bolts now tight.",
         ops=[carry("1-11"), carry("1-12"),
              op("lift and set each ceiling half from inside", 2, lay("t_place_overhead_s"), 2, "t_place_overhead_s"),
              op("tighten the 6 upper corner bolts (second visit)", 1, BOLT, 6, "t_bolt_captive_s")],
         joints={"J-CEIL-02": 4, "J-CEIL-01": 16}),
    dict(n=9, title="Left decor block DL", tags=["2-09"],
         A="With B, carries DL (2.3 m) from its place to the front-left and stands it on its spigots on the band, against L1 and L2's front edges, hinge halves toward the door opening.",
         B="Drives 3 bolts into DL from each of L1's and L2's front bays (6). DL stands on its spigots on the band and needs no bolt there (J-FRONT-02).",
         check="DL plumb (spirit level on its door-side face); the hinge halves free.",
         ops=[carry("2-09"), op("stand DL on the band", 2, lay("t_place_s"), 1, "t_place_s")],
         joints={"J-FRONT-01": 6}),
    dict(n=10, title="Fixed glass, then the right decor block DR", tags=["2-01", "2-03"],
         A="Opens the crate. With B, lifts the fixed glass out on 2 suction lifters, carries it upright and drops its bottom edge into the U-channel already fitted on the sill, onto its setting blocks; then holds it upright with both lifters.",
         B="Brings DR (2.3 m, 18 kg) to the right of the opening and slides it in from the side so its channels take the glass's right and diagonal edges, back onto its stops; drives 3 bolts into DR from each of R1's and R2's front bays (6); DR stands on its spigots on its support (J-FRONT-02). A lets go only now.",
         check="Glass seated in all three channels so far, its free edge plumb; DR on its stops. Do this before the air column: DR's right-hand bolts can't be reached once it stands (J-FRONT-01).",
         ops=[carry("2-01"), op("set the fixed glass in the sill's channel and hold it", 2, lay("t_fixed_preglazed_min") * 60, 1, "t_fixed_preglazed_min"),
              carry("2-03"), op("slide DR onto the glass edges and its stops", 2, TIME["t_dr_slide_s"].value, 1, "t_dr_slide_s")],
         joints={"J-FRONT-01": 6}),
    dict(n=11, title="Door (before DT)", tags=["2-02"],
         A="With B, lifts the door unit out of the crate on 2 suction lifters (about 25 kg each), carries it upright and lowers its hinge halves onto DL's.",
         B="Secures the hinges as the named set requires (HOLD), then swings the door slowly to 90 degrees and back, checking the 7 mm running gap over the threshold. The hinges hold the door at its closed position; there is no lock (D-83).",
         check="The door hangs before DT goes on: DT's underside is only 4 mm above the door top (PM ruling). Door swings freely, no rub.",
         ops=[carry("2-02"), op("hang the door and adjust", 2, lay("t_door_prehung_min") * 60, 1, "t_door_prehung_min")],
         joints={}),
    dict(n=12, title="Top decor block DT, from above", tags=["2-12"],
         A="From a step stool outside the front, with B on a second stool, lowers DT from above onto DL and DR so its slot takes the glass's top edge.",
         B="Drives DT's 4 bolts to the ceiling (J-FRONT-03).",
         check="The glass's top edge is in DT's channel; 4 mm head gap over the door all along; the top band line straight; the door's strike 368102 closes onto the 35 N magnetic catch 368007 in DT's underside (D-83).",
         ops=[carry("2-12"), op("lower DT from above", 2, lay("t_place_overhead_s"), 1, "t_place_overhead_s")],
         joints={"J-FRONT-03": 4}),
    dict(n=13, title="Electrics, first fix (power off)", tags=["2-13"],
         A="Plugs the factory-tested harness together at each panel seam and runs the plug-in feeds for the light shelf and the hub to their ends (D-87).",
         B="Hands parts from the electrical kit and checks each connector against the wiring diagram (ELECTRICAL design).",
         check="Every seam connector latched before any cassette closes its bay.",
         ops=[carry("2-13"), op("plug one connector", 1, lay("t_connector_s"), 6, "t_connector_s")],
         joints={}),
    dict(n=14, title="Wall linings: 8 cassettes", tags=["1-13", "1-14", "1-15", "1-16", "1-17", "1-18", "1-19", "1-20"],
         A="Hangs R1's and R2's cassettes first (the air column needs them), then L1, L2, B1 to B4, each on its clips.",
         B="Hands each cassette up felt-out and lines it up with the hook-and-loop; checks each clip has locked.",
         check="Every bolt in its bay was driven before the bay is closed. Each cassette floats: it touches nothing but its clips.",
         ops=[*[carry(t) for t in ["1-13", "1-14", "1-15", "1-16", "1-17", "1-18", "1-19", "1-20"]],
              op("hang one cassette on its clips", 1, lay("t_leaf_s"), 8, "t_leaf_s")],
         joints={}),
    dict(n=15, title="Air parts in DR: the intake riser with its supply fan box", tags=["2-17"],
         A="Lifts DR's removable inner face off; with B, slides in the intake riser, its supply fan box (2 fans) joined at its top in the factory, down to its foot over the mesh space (D-87).",
         B="Mates the fan box's plug-in connector; refits the inner face.",
         check="Riser foot sits over the opening; fan box connector latched; inner face back on all round.",
         ops=[op("DR inner face off and on", 1, TIME["t_face_s"].value, 2, "t_face_s"),
              carry("2-17"), op("slide the riser and fan box in", 2, TIME["t_slide_long_s"].value, 1, "t_slide_long_s"),
              op("plug the fan box", 1, lay("t_connector_s"), 1, "t_connector_s")],
         joints={}),
    dict(n=16, title="Air column and supply cartridge", tags=["2-11", "2-18"],
         A="With B, hangs the air column (2.1 m) on its tool-free hooks in the front-right corner (D-87), its back on DR's inner face and its right side on R1's and R2's linings; lifts its front face off.",
         B="With A, slides the supply cartridge into the column; plugs the hub into the cable chase; A refits the front face.",
         check="Kick grille clear at the floor; the hub zone at about Z 1200 faces the room.",
         ops=[carry("2-11"), op("hang the column on its hooks", 2, TIME["t_hook_s"].value, 1, "t_hook_s"),
              op("column front face off and on", 1, TIME["t_face_s"].value, 2, "t_face_s"),
              carry("2-18"), op("slide the cartridge in", 2, TIME["t_slide_long_s"].value, 1, "t_slide_long_s"),
              op("plug the hub", 1, lay("t_connector_s"), 1, "t_connector_s")],
         joints={}),
    dict(n=17, title="Soffit and exhaust cartridge", tags=["2-10", "2-19"],
         A="With B, both on step stools, lifts the soffit (2.3 m), its exhaust fan box already fitted at the right end (D-87), and hangs it on its tool-free hooks under the ceiling frame, the fan box under C2's roof sleeve.",
         B="With A, lifts the exhaust cartridge in through the open underside; plugs the fan box; closes the hinged underside.",
         check="Soffit underside at Z 2120, level; the fan box meets the roof sleeve; the door still clears.",
         ops=[carry("2-10"), op("hang the soffit on its hooks", 2, TIME["t_hook_s"].value, 1, "t_hook_s"),
              carry("2-19"), op("lift the cartridge in", 2, lay("t_place_overhead_s"), 1, "t_place_overhead_s"),
              op("plug the fan box", 1, lay("t_connector_s"), 1, "t_connector_s"),
              op("close the hinged underside", 1, TIME["t_face_s"].value, 1, "t_face_s")],
         joints={}),
    dict(n=18, title="Ceiling linings: 2 cassettes", tags=["2-20", "2-21"],
         A="With B, lifts each ceiling cassette from below, fill side up, onto its clips behind the soffit.",
         B="Hooks the 2 safety catches of each cassette before A lets go.",
         check="Both catches on each cassette; front edges 3 mm behind the soffit.",
         ops=[carry("2-20"), carry("2-21"), op("lift each cassette onto its clips", 2, lay("t_place_overhead_s"), 2, "t_place_overhead_s"),
              op("hook a safety catch", 1, TIME["t_catch_s"].value, 4, "t_catch_s")],
         joints={}),
    dict(n=19, title="Light shelf", tags=["2-14"],
         A="Fits the light shelf trims along the tops of the side and back walls (INTERIOR design).",
         B="Plugs the light shelf feed.",
         check="Trims straight; no cable shows.",
         ops=[carry("2-14"), op("fit and plug the light shelf", 1, TIME["t_light_shelf_s"].value, 1, "t_light_shelf_s")],
         joints={}),
    dict(n=20, title="Power on and self-test: fans run", tags=[],
         A="A qualified electrician connects the mains inlet (220 V for the prototype, REQ-SCP-02) and switches on.",
         B="Presses the hub's self-test button: both fan pairs, the lights and the sensors run, and it shows pass or fail (D-87). Then checks air out at the kick grille and into the soffit grille, and the CO2 reading.",
         check="Self-test passes and the fans run on both paths. The clock stops after step 21's final check (REQ-ASM-01: closed, powered, fans running).",
         ops=[op("power on and self-test", 2, TIME["t_selftest_s"].value, 1, "t_selftest_s")],
         joints={}),
    dict(n=21, title="Final check and film", tags=[],
         A="Checks the door: swing to 90 degrees, no rub, closes onto DT's magnetic catch 368007 with the magnetic seal pair meeting on the glass edges (D-83), drop seal down on the threshold land when closed.",
         B="Checks the seals with the pod lit and the room dark: no light at any seam. Pulls each of the 15 film panels off by its quick-release tab (the 8 wall skins, the 3 decor blocks, both faces of both glass panes; D-87); cleans.",
         check="Every check in the final check list is ticked.",
         ops=[op("check door, seals and fans; clean", 2, lay("t_final_min") * 60, 1, "t_final_min"),
              op("pull one film panel by its tab", 1, TIME["t_peel_tab_s"].value, int(MINE["film_faces"].value), "t_peel_tab_s")],
         joints={}),
    dict(n=22, title="Work-wall ledge and screen mount", tags=["2-16"],
         A="Holds the 1000 mm ledge on the right (work) wall at its mounting points.",
         B="Fixes the ledge and the screen mount (INTERIOR design, D-70).",
         check="Ledge level and firm.",
         ops=[carry("2-16"), op("hold the ledge", 2, TIME["t_ledge_two_s"].value, 1, "t_ledge_two_s"),
              op("fix the ledge and the screen mount", 1, TIME["t_ledge_one_s"].value, 1, "t_ledge_one_s")],
         joints={}),
]
CLOCK_LAST_STEP = 21     # REQ-ASM-01 clock: steps 1 to 21; step 22 is fit-out after it (PROPOSED)

# The joints register's bolt count (section 3.9), pinned from PR #23 at aed1590 for when the file isn't on this branch.
REGISTER_PINNED = {"J-WALL-01": (16, "M6 x 16"), "J-WALL-02": (12, "M6 x 16"), "J-WALL-03": (6, "M6 x 25"),
                   "J-BASE-01": (16, "M6 x 16"), "J-CEIL-01": (16, "M6 x 16"), "J-CEIL-02": (4, "M6 x 25"),
                   "J-FRONT-01": (12, "M6 x 16")}
REGISTER_PINNED_SRC = "joints register section 3.9, PR #23 at aed1590 (pinned copy: the file isn't on this branch yet)"


HW_PN_PINNED = {"M6 x 16": "838001", "M6 x 25": "838002", "washer": "838004", "key": "108001"}


def read_register_pn(path):
    """Part numbers of the bolts, the head washer and the hex key from the register's hardware set (section 2.1)."""
    text = Path(path).read_text(encoding="utf-8")
    out = {}
    for key, hid in (("M6 x 16", "H-01"), ("M6 x 25", "H-01P"), ("washer", "H-09"), ("key", "H-07")):
        mo = re.search(r"\|\s*" + re.escape(hid) + r"\s*\|\s*\*\*(\d{6})\*\*", text)
        if mo:
            out[key] = mo.group(1)
    return out


def read_register(path):
    """Bolt count table from the joints register's section 3.9: {joint: (count, size)} and the stated total."""
    text = Path(path).read_text(encoding="utf-8")
    m = re.search(r"###\s*3\.9\s+Bolt count(.*?)(\n###|\n## )", text, re.S)
    if not m:
        raise ValueError(f"no '3.9 Bolt count' section in {path}")
    rows, total = {}, None
    for line in m.group(1).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        jm = re.match(r"(J-[A-Z]+-\d+)", cells[0])
        if jm and cells[1].isdigit():
            size = "M6 x 25" if "25" in cells[2] else "M6 x 16"
            rows[jm.group(1)] = (int(cells[1]), size)
        elif "Total" in cells[0]:
            total = int(re.sub(r"\D", "", cells[1]))
    return rows, total


# ------------------------------------------------------------------------------------------- time model
def step_ops(st, other_fixings):
    """A step's operations, with one captive-bolt drive per register bolt and per counted outside fixing."""
    bolts = sum(st["joints"].values())
    other = sum(f["count"] for f in other_fixings if f["step"] == st["n"])
    ops = list(st["ops"])
    if bolts + other:   # every register bolt and counted fixing is one captive-bolt drive by one person
        ops.append(op("drive the step's bolts and fixings", 1, BOLT, bolts + other, "t_bolt_captive_s"))
    return ops, bolts, other


def ops_time(ops):
    """(2-person s, 1-person s, elapsed s): 2-person work runs once, 1-person work is shared, plus the hand-off allowance."""
    two = sum(o["secs"] * o["n"] for o in ops if o["who"] == 2)
    one = sum(o["secs"] * o["n"] for o in ops if o["who"] == 1)
    return two, one, (two + one / 2) * (1 + lay("inefficiency"))


def clock_min(steps, other_fixings, upto=None):
    upto = CLOCK_LAST_STEP if upto is None else upto
    return sum(ops_time(step_ops(st, other_fixings)[0])[2] for st in steps if st["n"] <= upto) / 60


# ------------------------------------------------------------------------------------------- model
class Model:
    def __init__(self, joints_path=None):
        self.roll = read_rollup()
        self.checks = []          # (id, what, result, pass)
        self.issues = []
        for p in PIECES:
            kg, stat = 0.0, set()
            for h, u in p.mass:
                r = self.roll[resolve(self.roll, h)]
                kg += r["kg_each"] * u
                stat.add(r["status"])
            kg += p.extra_kg
            if p.extra_kg:
                stat.add(p.extra_status)
            p.kg = kg
            p.status = "; ".join(sorted(stat))
        # register
        self.reg_src = REGISTER_PINNED_SRC
        self.register, self.reg_total = dict(REGISTER_PINNED), 82
        path = Path(joints_path) if joints_path else (JOINTS_MD if JOINTS_MD.exists() else None)
        self.pn = dict(HW_PN_PINNED)
        if path:
            self.register, self.reg_total = read_register(path)
            self.pn.update(read_register_pn(path))
            self.reg_src = f"`{path.relative_to(REPO) if path.is_relative_to(REPO) else path}` section 3.9"
        self.steps = self.time_steps()
        self.run_checks()

    # ---- pallets
    def shipped(self, pallet=None):
        return [p for p in PIECES if p.kind == "piece" and (pallet is None or p.pallet == pallet)]

    def allowances(self, pallet):
        return [p for p in PIECES if p.kind == "allowance" and p.pallet == pallet]

    def packaging(self, pallet):
        out = []
        for it in PACKAGING:
            if it.get("pallet") == pallet and it["kg"]:
                out.append(it)
        return out

    def net(self, pallet):
        return sum(p.kg for p in self.shipped(pallet)) + sum(p.kg for p in self.allowances(pallet))

    def tare(self, pallet):
        return sum(it["kg"] * it["qty"] for it in self.packaging(pallet))

    def gross(self, pallet):
        return self.net(pallet) + self.tare(pallet)

    def stack1(self):
        """Upright stack on pallet 1: per piece, along and up sizes; totals."""
        rows, t = [], 0.0
        max_up = lay("max_load_h") - lay("pal_std_h") - lay("pack_cap_h")
        for tag in STACK1:
            p = PIECE[tag]
            a, b, c = p.dims
            opts = [(x, y) for x, y in ((b, a), (a, b)) if x <= MINE["pal_std_l_exact"].value and y <= max_up]
            along, up = min(opts, key=lambda o: o[1]) if opts else (b, a)
            rows.append(dict(tag=tag, along=along, up=up, thick=c, fits=bool(opts)))
            t += c
        n = len(STACK1)
        total = t + (n - 1) * lay("pack_gap") + 2 * lay("edge_board")
        height = lay("pal_std_h") + max(r["up"] for r in rows) + lay("pack_cap_h")
        return rows, total, height, max_up

    def crate(self):
        door, fix = PIECE["2-02"], PIECE["2-01"]
        inner_l = MINE["crate_l"].value - 2 * MINE["crate_end_rail"].value
        inner_w = MINE["crate_w"].value - 2 * MINE["crate_side_rail"].value
        ef = MINE["edge_foam"].value
        door_layer = MINE["door_blocks"].value + 8.76 + 70 + MINE["glass_foam"].value   # FRONT PR #27: glass 8.76, pull space 70 a side
        fix_layer = MINE["glass_foam"].value + fix.dims[2] + MINE["glass_foam"].value
        inside_h = door_layer + MINE["crate_sep"].value + fix_layer
        outside_h = MINE["crate_bed"].value + inside_h + MINE["crate_lid"].value
        fits = dict(
            door_len=door.dims[0] + 2 * ef <= inner_l, door_w=door.dims[1] + 2 * ef <= inner_w,
            fix_len=fix.dims[0] + 2 * ef <= inner_l, fix_w=fix.dims[1] + 2 * ef <= inner_w,
            crate_on_deck=MINE["crate_l"].value <= lay("pal_long_l") and MINE["crate_w"].value <= MINE["pal_long_l_exact"].value)
        return dict(inner_l=inner_l, inner_w=inner_w, door_layer=door_layer, fix_layer=fix_layer, inside_h=inside_h,
                    outside_h=outside_h, height=max(outside_h, 0), fits=fits)

    def tiers2(self):
        out, z = [], lay("pal_long_h")
        cr = self.crate()
        for i, tier in enumerate(TIERS2):
            lanes, ok = [], True
            if tier.get("crate"):
                h = cr["outside_h"]
                lanes.append(dict(width=MINE["crate_w"].value, items=[dict(tag="CRATE", along=MINE["crate_l"].value,
                                                                             across=MINE["crate_w"].value, up=h)],
                                  length=MINE["crate_l"].value, ok=True))
            else:
                h = tier["height"]
                if h is None:   # top tier: as tall as its tallest part plus the foam
                    h = max(PIECE[t].dims[2] for ln in tier["lanes"] for t in ln["tags"]) + MINE["cass_foam"].value
                for ln in tier["lanes"]:
                    items, length = [], 0.0
                    for t in ln["tags"]:
                        a, b, c = PIECE[t].dims
                        if ln.get("on_edge"):
                            across, up = c, b
                        else:
                            across, up = b, c
                        good = across <= ln["width"] and up <= h
                        if not good:
                            ok = False
                        items.append(dict(tag=t, along=a, across=across, up=up, ok=good))
                        length += a
                    lane_ok = length <= lay("pal_long_l")
                    ok = ok and lane_ok
                    lanes.append(dict(width=ln["width"], items=items, length=length, ok=lane_ok and all(i["ok"] for i in items)))
            width = sum(ln["width"] for ln in lanes)
            out.append(dict(name=tier["name"], z0=z, h=h, lanes=lanes, width=width,
                            ok=ok and width <= MINE["pal_long_l_exact"].value and width <= lay("pal_long_w") + 0.2))
            z += h
            if i < len(TIERS2) - 1:
                z += MINE["sep_h"].value
        height = z + lay("pack_cap_h")
        return out, height

    # ---- time
    def time_steps(self):
        rows = []
        for st in STEPS:
            ops, bolts, other = step_ops(st, OTHER_FIXINGS)
            two, one, el = ops_time(ops)
            rows.append(dict(n=st["n"], two=two, one=one, elapsed=el, bolts=bolts, other=other, ops=ops))
        return rows

    def time_total(self, upto=None):
        return sum(r["elapsed"] for r in self.steps if upto is None or r["n"] <= upto)

    def bolts_by_joint(self):
        out = {}
        for st in STEPS:
            for j, c in st["joints"].items():
                out[j] = out.get(j, 0) + c
        return out

    # ---- checks
    def check(self, cid, what, result, ok):
        self.checks.append(dict(id=cid, what=what, result=result, ok=bool(ok)))

    def run_checks(self):
        # K1 roll-up accounting
        used = {}
        for p in PIECES:
            for h, u in p.mass:
                k = resolve(self.roll, h)
                used[k] = used.get(k, 0.0) + u
        bad = [k for k, r in self.roll.items() if abs(used.get(k, 0.0) - r["qty"]) > 1e-6]
        unknown = [k for k in used if k not in self.roll]
        self.check("K1", "Every roll-up line is shipped exactly once, or marked as shipping later",
                   f"{len(self.roll)} lines, {sum(r['qty'] * r['kg_each'] for r in self.roll.values()):.1f} kg; "
                   f"{len(bad)} lines miscounted, {len(unknown)} unknown", not bad and not unknown)
        # K2 20 kg
        heavy = [p for p in self.shipped() if p.kg > MINE["part_limit_kg"].value and not p.glass]
        top = max((p for p in self.shipped() if not p.glass), key=lambda p: p.kg)
        self.check("K2", "Every piece 20 kg or less except the glass (D-03)",
                   f"heaviest non-glass piece {top.tag} {top.name} {top.kg:.1f} kg; over 20 kg: {len(heavy)}", not heavy)
        # K3 doorway
        fails = [p for p in self.shipped() if not (p.dims[2] <= MINE["door_a"].value and p.dims[1] <= MINE["door_b"].value)]
        self.check("K3", "Every piece passes the 810 x 2032 doorway rule (REQ-ASM-06)",
                   f"{len(self.shipped())} pieces, {len(fails)} fail", not fails)
        # K4 pallet 1
        rows, thick, h1, max_up = self.stack1()
        misfit = [r["tag"] for r in rows if not r["fits"]]
        self.check("K4", "Pallet 1: each upright piece within 1219.2 along and the height limit; stack within 1016",
                   f"stack {thick:.0f} mm of 1016; loaded height {h1:.0f} mm of 1829; misfits {misfit or 'none'}",
                   not misfit and thick <= MINE["pal_std_w_exact"].value and h1 <= lay("max_load_h"))
        # K5 pallet 2
        tiers, h2 = self.tiers2()
        bad_t = [t["name"] for t in tiers if not t["ok"]]
        self.check("K5", "Pallet 2: lanes within 1219 across and 2438 along, parts within their tier, loaded height 1829 or less",
                   f"loaded height {h2:.0f} mm; widest tier {max(t['width'] for t in tiers):.0f} mm; "
                   f"longest lane {max(ln['length'] for t in tiers for ln in t['lanes']):.0f} mm; failing tiers {bad_t or 'none'}",
                   not bad_t and h2 <= lay("max_load_h"))
        # K6 crate
        cr = self.crate()
        self.check("K6", "Glass crate: door and fixed glass fit inside with edge foam; crate on the deck",
                   f"inside {cr['inner_l']:.0f} x {cr['inner_w']:.0f} x {cr['inside_h']:.0f} mm; outside height {cr['outside_h']:.0f} mm; "
                   + ", ".join(k for k, v in cr["fits"].items() if not v) if not all(cr["fits"].values())
                   else f"inside {cr['inner_l']:.0f} x {cr['inner_w']:.0f} x {cr['inside_h']:.0f} mm; outside height {cr['outside_h']:.0f} mm; all fit",
                   all(cr["fits"].values()))
        # K7 bolts against the joints register
        mine = self.bolts_by_joint()
        diff = {j: (mine.get(j, 0), self.register.get(j, (0, ""))[0]) for j in set(mine) | set(self.register)
                if mine.get(j, 0) != self.register.get(j, (0, ""))[0]}
        total = sum(mine.values())
        n16 = sum(c for j, c in mine.items() if self.register.get(j, (0, "M6 x 16"))[1] == "M6 x 16")
        n25 = total - n16
        self.check("K7", "The guide's bolts match the joints register, joint by joint",
                   f"guide {total} ({n16} x M6 x 16, {n25} x M6 x 25); register {self.reg_total}; differences {diff or 'none'}",
                   not diff and total == self.reg_total)
        # K8 time
        clock = self.time_total(CLOCK_LAST_STEP)
        self.check("K8", "Assembly time within REQ-ASM-01's 4 hour limit (clock: steps 1 to %d)" % CLOCK_LAST_STEP,
                   f"{clock / 60:.0f} min for 2 people ({2 * clock / 3600:.1f} person-hours); target about "
                   f"{MINE['time_target_min'].value:.0f} min; limit {MINE['time_limit_min'].value:.0f} min",
                   clock / 60 <= MINE["time_limit_min"].value)
        # K9 first out, first fitted
        steps1 = [PIECE[t].step for t in STACK1]
        mono1 = all(a <= b for a, b in zip(steps1, steps1[1:]))
        crate_ok = PIECE[CRATE_TAGS[-1]].step <= PIECE[CRATE_TAGS[0]].step
        self.check("K9", "First out is first fitted: pallet 1 from its open face; inside the crate, the top pane is fitted first",
                   f"pallet 1 steps {steps1[0]} to {steps1[-1]}, never going back: {mono1}; crate top {CRATE_TAGS[-1]} "
                   f"(step {PIECE[CRATE_TAGS[-1]].step}) over {CRATE_TAGS[0]} (step {PIECE[CRATE_TAGS[0]].step})", mono1 and crate_ok)
        # K10 labels
        nolab = [p.tag for p in self.shipped() if not p.pn or not p.pos]
        on_pallet = {t for t in STACK1} | {t for tr in TIERS2 for ln in tr["lanes"] for t in ln["tags"]} | set(CRATE_TAGS)
        missing = [p.tag for p in self.shipped() if p.tag not in on_pallet]
        extra = [t for t in on_pallet if t != "CRATE" and t not in PIECE]
        self.check("K10", "Every piece has a label (part number or owner, position code) and a place on a pallet",
                   f"{len(self.shipped())} labelled pieces; without a place: {missing or 'none'}; unknown tags: {extra or 'none'}",
                   not nolab and not missing and not extra)
        # K11 every shipped piece is fitted by a step
        fitted = {t for st in STEPS for t in st["tags"]}
        unfitted = [p.tag for p in self.shipped() if p.tag not in fitted]
        wrong = [p.tag for p in self.shipped() if p.tag in fitted and not any(p.tag in st["tags"] and st["n"] == p.step for st in STEPS)]
        self.check("K11", "Every labelled piece is fitted in the step its label names",
                   f"unfitted {unfitted or 'none'}; step mismatches {wrong or 'none'}", not unfitted and not wrong)
        self.check_skeleton()

    def check_skeleton(self):
        if not SKELETON_STEP.exists():
            self.check("K12", "Every skeleton body maps to one label (step pictures)", f"{SKELETON_STEP.name} not found", False)
            return
        have = skeleton_bodies()
        mapped = [b for bs in SKEL.values() for b in bs]
        missing = sorted(set(mapped) - set(have))
        unmapped = sorted(set(have) - set(mapped))
        twice = sorted({b for b in mapped if mapped.count(b) > 1})
        bad_tags = [t for t in SKEL if t not in PIECE]
        self.check("K12", "Every skeleton body maps to exactly one label, for the step pictures",
                   f"{len(have)} bodies in the skeleton STEP; not in it {missing or 'none'}; unmapped {unmapped or 'none'}; "
                   f"twice {twice or 'none'}; unknown labels {bad_tags or 'none'}", not (missing or unmapped or twice or bad_tags))

    def ok(self):
        return all(c["ok"] for c in self.checks)


# ------------------------------------------------------------------------------------------- formatting
def f1(x):
    return f"{x:,.1f}"


def f0(x):
    return f"{x:,.0f}"


def dims_txt(d):
    return " x ".join(("%g" % round(v, 2)) for v in d)


def ux(text):
    """Multiplication sign for the Markdown outputs ('M6 x 16' reads 'M6 × 16'); the CSV keeps plain ASCII."""
    return re.sub(r"(?<=[0-9A-Za-z)]) x (?=[0-9A-Z(])", " × ", text)


def md_table(head, rows, align=None):
    align = align or ["---"] * len(head)
    out = ["| " + " | ".join(ux(h) for h in head) + " |", "| " + " | ".join(align) + " |"]
    for r in rows:
        out.append("| " + " | ".join(ux(str(c)) for c in r) + " |")
    return "\n".join(out)


def gen_tables(m):
    T = {}
    rows1, thick1, h1, max_up = m.stack1()
    tiers, h2 = m.tiers2()
    cr = m.crate()
    g1, g2 = m.gross(1), m.gross(2)
    n1, n2 = m.net(1), m.net(2)
    clock = m.time_total(CLOCK_LAST_STEP)
    total = m.time_total()
    later = sum(p.kg for p in PIECES if p.kind == "later")
    rollup_total = sum(r["qty"] * r["kg_each"] for r in m.roll.values())
    not_in = sum(p.extra_kg for p in PIECES if p.kind == "piece")
    reg_bolts = sum(c for c, _ in m.register.values())
    T["ROLLUP_TOTAL"] = f1(rollup_total - later)
    T["ROLLUP_CSV_TOTAL"] = f1(rollup_total)
    T["LATER_KG"] = f1(later)
    T["NOT_IN_ROLLUP_KG"] = f1(not_in)
    T["SHIPPED_NET"] = f1(n1 + n2)
    T["GROSS_TOTAL"] = f0(g1 + g2)
    T["G1"], T["G2"] = f0(g1), f0(g2)
    T["N1"], T["N2"] = f1(n1), f1(n2)
    T["H1"], T["H2"] = f0(h1), f0(h2)
    T["STACK1"] = f0(thick1)
    T["PIECES_N"] = str(len(m.shipped()))
    T["PIECES_1"], T["PIECES_2"] = str(len(m.shipped(1))), str(len(m.shipped(2)))
    T["CLOCK_MIN"] = f0(clock / 60)
    T["CLOCK_PH"] = f"{2 * clock / 3600:.1f}"
    T["TOTAL_MIN"] = f0(total / 60)
    T["REG_BOLTS"] = str(reg_bolts)
    T["REG_SRC"] = m.reg_src
    T["OTHER_FIX"] = str(sum(f["count"] for f in OTHER_FIXINGS))
    mine = m.bolts_by_joint()
    T["N16"] = str(sum(c for j, c in mine.items() if m.register.get(j, (0, "M6 x 16"))[1] == "M6 x 16"))
    T["N25"] = str(sum(c for j, c in mine.items() if m.register.get(j, (0, "M6 x 16"))[1] == "M6 x 25"))
    T["CHECKS_OK"] = "all pass" if m.ok() else "FAIL: " + ", ".join(c["id"] for c in m.checks if not c["ok"])
    heaviest = max((p for p in m.shipped() if not p.glass), key=lambda p: p.kg)
    T["HEAVIEST"] = f"{heaviest.name} ({heaviest.tag}) at {heaviest.kg:.1f} kg"
    T["PN16"], T["PN25"], T["PNW"], T["PNKEY"] = m.pn["M6 x 16"], m.pn["M6 x 25"], m.pn["washer"], m.pn["key"]
    T["KIT_TAG"] = next(p.tag for p in m.shipped() if p.pn == "109000")
    T["DOOR_KG"] = f1(PIECE["2-02"].kg)
    T["FIX_KG"] = f1(PIECE["2-01"].kg)

    # pallets at a glance
    T["PALLETS"] = md_table(
        ["Pallet", "Deck mm (in)", "Pieces", "Net kg", "Gross kg (lb)", "Loaded height mm (in)", "Volume ft3 (reference)", "Density lb/ft3 (reference)"],
        [[f"1: 48 x 40 in, upright stack ([diagram]({OUT_SVG[1].name}))", "1219 x 1016 (48 x 40)", T["PIECES_1"], f1(n1),
          f"{f0(g1)} ({f0(g1 / KG_PER_LB)})", f"{f0(h1)} ({h1 / MM_PER_IN:.1f})",
          f"{48 * 40 * h1 / MM_PER_IN / 1728:.1f}", f"{g1 / KG_PER_LB / (48 * 40 * h1 / MM_PER_IN / 1728):.1f}"],
         [f"2: 96 x 48 in, five tiers ([diagram]({OUT_SVG[2].name}))", "2438 x 1219 (96 x 48)", T["PIECES_2"], f1(n2),
          f"{f0(g2)} ({f0(g2 / KG_PER_LB)})", f"{f0(h2)} ({h2 / MM_PER_IN:.1f})",
          f"{96 * 48 * h2 / MM_PER_IN / 1728:.1f}", f"{g2 / KG_PER_LB / (96 * 48 * h2 / MM_PER_IN / 1728):.1f}"],
         ["**Both**", "", T["PIECES_N"], f"**{f1(n1 + n2)}**", f"**{f0(g1 + g2)}** ({f0((g1 + g2) / KG_PER_LB)})", "", "", ""]],
        ["---", "---", "---:", "---:", "---:", "---:", "---:", "---:"])

    # pallet 1 stack
    r1 = []
    for i, r in enumerate(rows1, 1):
        p = PIECE[r["tag"]]
        r1.append([i, f"**{p.tag}**", p.pos, p.name, f"{p.kg:.1f}", f"{r['along']:g} x {r['up']:g}", f"{r['thick']:g}", p.step])
    T["STACK1_TABLE"] = md_table(["Out", "Label", "Pos.", "Piece", "kg", "Along × up, mm", "Thick mm", "Fitted in step"], r1,
                                 ["---:", "---", "---", "---", "---:", "---", "---:", "---:"])
    T["STACK1_SUM"] = (f"{len(rows1)} pieces, {f0(sum(r['thick'] for r in rows1))} mm of parts + {len(rows1) - 1} foam "
                       f"interleaves of {lay('pack_gap')} mm + 2 edge boards of {lay('edge_board')} mm = **{f0(thick1)} mm of "
                       f"{MINE['pal_std_w_exact'].value:g}** across the 40 in side. Tallest piece {f0(max(r['up'] for r in rows1))} mm up: "
                       f"{lay('pal_std_h')} deck + {f0(max(r['up'] for r in rows1))} + {lay('pack_cap_h')} cap = **{f0(h1)} mm loaded**.")
    # pallet 2 tiers
    r2 = []
    for t in tiers:
        for ln in t["lanes"]:
            for it in ln["items"]:
                if it["tag"] == "CRATE":
                    r2.append([t["name"], "crate", "-", f"GLASS CRATE 911001 with {', '.join(CRATE_TAGS[::-1])}",
                               f"{m.crate_mass():.1f}", f"{MINE['crate_l'].value:g} x {MINE['crate_w'].value:g} x {f0(t['h'])}", "10, 11"])
                    continue
                p = PIECE[it["tag"]]
                r2.append([t["name"], f"{ln['width']:g}", f"**{p.tag}**", p.name, f"{p.kg:.1f}",
                           f"{it['along']:g} x {it['across']:g} x {it['up']:g}", p.step])
    T["TIERS_TABLE"] = md_table(["Tier", "Lane mm", "Label", "Piece", "kg", "Along × across × up, mm", "Fitted in step"], r2,
                                ["---", "---:", "---", "---", "---:", "---", "---"])
    hl = [f"{lay('pal_long_h')} deck"] + [f"{f0(t['h'])} ({t['name'].split(':')[0].lower()})" for t in tiers]
    T["TIERS_SUM"] = (" + ".join(hl) + f" + {len(tiers) - 1} separators of {MINE['sep_h'].value:g} + {lay('pack_cap_h')} cap = "
                      f"**{f0(h2)} mm loaded** of {lay('max_load_h')}. Widest tier {f0(max(t['width'] for t in tiers))} mm of "
                      f"{MINE['crate_w'].value:g}; longest lane {f0(max(ln['length'] for t in tiers for ln in t['lanes']))} mm of "
                      f"{lay('pal_long_l')}.")
    T["CRATE_SUM"] = (f"Outside {MINE['crate_l'].value:g} x {MINE['crate_w'].value:g} x {f0(cr['outside_h'])} mm; inside "
                      f"{f0(cr['inner_l'])} x {f0(cr['inner_w'])} x {f0(cr['inside_h'])} mm: the door layer {f0(cr['door_layer'])} mm "
                      f"(door on {MINE['door_blocks'].value:g} mm foam blocks so its lower pull hangs free), a {MINE['crate_sep'].value:g} mm "
                      f"separator, then the fixed glass layer {f0(cr['fix_layer'])} mm on top, because it is fitted first (step 10). "
                      f"Door {dims_txt(PIECE['2-02'].dims[:2])} mm and fixed glass {dims_txt(PIECE['2-01'].dims[:2])} mm each keep "
                      f"{MINE['edge_foam'].value:g} mm of edge foam all round.")

    # packing lists per pallet
    for pal in (1, 2):
        rows = []
        for p in m.shipped(pal):
            rows.append([f"**{p.tag}**", p.pn, p.name, p.vi, p.pos, f"{p.kg:.2f}", p.status, dims_txt(p.dims), p.step])
        for a in m.allowances(pal):
            rows.append(["-", "-", a.name, "", "-", f"{a.kg:.2f}", a.status, "inside the pieces", "-"])
        for it in m.packaging(pal):
            rows.append(["-", it["pn"] + " (PROPOSED)", it["name"], "", "-", f"{it['kg'] * it['qty']:.2f}", it["status"],
                         "-", "-"])
        rows.append(["", "", "**Gross**", "", "", f"**{m.gross(pal):.1f}**", "", "", ""])
        T[f"LIST{pal}"] = md_table(["Label", "Part number", "Piece", "Vietnamese", "Pos.", "kg", "Status", "Size mm", "Step"], rows,
                                   ["---", "---", "---", "---", "---", "---:", "---", "---", "---:"])
    # roll-up reconciliation
    rec = []
    for item, r in m.roll.items():
        where = []
        for p in PIECES:
            for h, u in p.mass:
                if resolve(m.roll, h) == item:
                    where.append(f"{p.tag}" + ("" if abs(u - 1) < 1e-9 else f" x {u:g}"))
        rec.append([r["group"], item, f"{r['qty']:g}", f"{r['kg_total']:.2f}", r["status"], ", ".join(where)])
    T["RECON"] = md_table(["Group", "Roll-up line", "Qty", "kg", "Status", "Carried by"], rec,
                          ["---", "---", "---:", "---:", "---", "---"])
    # checks
    T["CHECKS"] = md_table(["Check", "What", "Result", "Pass"],
                           [[c["id"], c["what"], c["result"], "yes" if c["ok"] else "**NO**"] for c in m.checks],
                           ["---", "---", "---", "---"])
    # packaging BOM
    pb = []
    for it in PACKAGING:
        qty = it["qty"] if it["qty"] is not None else len(m.shipped())
        kg = "-" if it["kg"] is None else f"{it['kg']:.1f}"
        pb.append([it["pn"], it["name"], it["kind"], qty, kg, it["status"], it["src"]])
    T["PKG_BOM"] = md_table(["Part number (PROPOSED)", "Name", "Kind", "Qty", "kg each", "Status", "Source"], pb,
                            ["---", "---", "---", "---:", "---:", "---", "---"])
    # numbers used
    used = []
    for k in ["pal_std_l", "pal_std_w", "pal_std_h", "pal_std_kg", "pal_long_l", "pal_long_w", "pal_long_h", "pal_long_kg",
              "max_load_h", "pack_gap", "edge_board", "pack_cap_h", "pack_kg_std", "pack_kg_long"]:
        v = LAYP[k]
        used.append([f"`{k}`", f"{v.value:g} {v.unit}", v.status, f"layout study {v.source}".strip(), v.note])
    for k, v in MINE.items():
        used.append([f"`{k}`", f"{v.value:g} {v.unit}", v.status, v.source, v.note])
    T["NUMBERS"] = md_table(["Name", "Value", "Status", "Source", "Note"], used)
    # labels list (short)
    lab = []
    for p in m.shipped():
        lab.append([f"**{p.tag}**", p.pn, p.pos, p.name, f"{p.kg:.1f}", "2" if (p.glass or p.kg > MINE['heavy_part'].value or p.dims[0] > MINE['long_part'].value) else "1",
                    p.step])
    T["LABELS"] = md_table(["Label", "Part number", "Pos.", "Name on the label", "kg", "People to lift", "Step"], lab,
                           ["---", "---", "---", "---", "---:", "---:", "---:"])
    return T


def guide_tables(m, T):
    G = dict(T)
    steps_md = []
    srow = []
    for st, tr in zip(STEPS, m.steps):
        parts = ", ".join(f"**{t}** {ux(PIECE[t].name)} ({PIECE[t].kg:.1f} kg)" for t in st["tags"]) or "none"
        bolts = []
        for j, c in st["joints"].items():
            size = m.register.get(j, (0, 'M6 x 16'))[1]
            bolts.append(f"{c} × {m.pn.get(size, '')} {ux(size)} ({j})")
        for fx in OTHER_FIXINGS:
            if fx["step"] == st["n"]:
                bolts.append(ux(fx["text"]))
        tool = " Tool: the 5 mm hex key." if (st["joints"] or any(f["step"] == st["n"] and f["count"] for f in OTHER_FIXINGS)) else ""
        clock = "" if st["n"] <= CLOCK_LAST_STEP else ", after the clock"
        img = step_image(st["n"])
        pic = (f"![Step {st['n']}](img/{img.name})\n\n" if img.exists() else "")
        steps_md.append(
            f"### Step {st['n']}. {st['title']}{clock}\n\n{pic}"
            f"- **Time:** about {tr['elapsed'] / 60:.0f} min for 2 people.\n"
            f"- **Parts:** {parts}.\n"
            f"- **Fasteners:** {'; '.join(bolts) if bolts else 'none'}.{tool}\n"
            f"- **Person A:** {st['A']}\n"
            f"- **Person B:** {st['B']}\n"
            f"- **Check before the next step:** {st['check']}\n")
        srow.append([st["n"], st["title"], len(st["tags"]), tr["bolts"], tr["other"], f"{tr['two'] / 60:.1f}", f"{tr['one'] / 60:.1f}",
                     f"**{tr['elapsed'] / 60:.1f}**" + ("" if st["n"] <= CLOCK_LAST_STEP else " (after)")])
    G["STEPS"] = "\n".join(steps_md)
    G["AIR_MIN"] = f0(sum(tr["elapsed"] for st, tr in zip(STEPS, m.steps) if st["n"] in (15, 16, 17)) / 60)
    G["LEVEL_MIN"] = f0(lay("t_level_min"))
    G["COLUMN_FITTED_KG"] = f1(PIECE["2-11"].kg + PIECE["2-18"].kg)
    G["COLUMN_OVER_KG"] = f1(PIECE["2-11"].kg + PIECE["2-18"].kg - MINE["part_limit_kg"].value)
    clock = m.time_total(CLOCK_LAST_STEP)
    srow.append(["", f"**Clock, steps 1 to {CLOCK_LAST_STEP}**", "", sum(r["bolts"] for r in m.steps),
                 sum(r["other"] for r in m.steps[:CLOCK_LAST_STEP]), "", "", f"**{clock / 60:.0f}**"])
    G["TIME_TABLE"] = md_table(["Step", "What", "Pieces", "Register bolts", "Other fixings", "2-person min", "1-person min (shared)", "Elapsed min"],
                               srow, ["---:", "---", "---:", "---:", "---:", "---:", "---:", "---:"])
    # bolt totals
    mine = m.bolts_by_joint()
    br = []
    for j in sorted(m.register):
        c, size = m.register[j]
        where = ", ".join(f"step {st['n']}: {st['joints'][j]}" for st in STEPS if j in st["joints"])
        br.append([j, f"{m.pn.get(size, '')} {size}", where, mine.get(j, 0), c, "yes" if mine.get(j, 0) == c else "**NO**"])
    n16 = sum(mine.get(j, 0) for j, (c, s) in m.register.items() if s == "M6 x 16")
    n25 = sum(mine.get(j, 0) for j, (c, s) in m.register.items() if s == "M6 x 25")
    br.append(["**Total**", f"{n16} x M6 x 16, {n25} x M6 x 25", "", f"**{sum(mine.values())}**", f"**{m.reg_total}**",
               "yes" if sum(mine.values()) == m.reg_total else "**NO**"])
    G["BOLTS"] = md_table(["Joint", "Bolt", "Where in this guide", "Guide", "Register", "Match"], br,
                          ["---", "---", "---", "---:", "---:", "---"])
    G["OTHER_FIXINGS"] = md_table(["Step", "Fixing", "Owner", "Count used here", "Size", "Status", "Note"],
                                  [[f["step"], f["where"], f["owner"], f["count"], ux(f["size"]), f["status"], f["note"]] for f in OTHER_FIXINGS],
                                  ["---:", "---", "---", "---:", "---", "---", "---"])
    # D-87 and the film, priced
    inef = 1 + lay("inefficiency")
    film_tab = MINE["film_faces"].value * TIME["t_peel_tab_s"].value / 2 * inef / 60
    film_all = MINE["film_faces_all"].value * TIME["t_peel_s"].value / 2 * inef / 60
    G["FILM_MIN"], G["FILM_ALL_MIN"], G["FILM_SAVES"] = f"{film_tab:.1f}", f"{film_all:.1f}", f"{film_all - film_tab:.1f}"
    G["FILM_FACES"], G["FILM_FACES_ALL"] = f0(MINE["film_faces"].value), f0(MINE["film_faces_all"].value)
    G["REG_BOLT_MIN"] = f"{sum(c for c, _ in m.register.values()) * BOLT / 2 * inef / 60:.0f}"

    # unit times
    ut = []
    for k in ["t_unpack_std_ordered_min", "t_unpack_long_ordered_min", "t_carry_s", "t_place_s", "t_place_hung_s", "t_place_overhead_s",
              "t_bolt_captive_s", "t_level_min", "t_fixed_preglazed_min", "t_door_prehung_min", "t_connector_s", "t_leaf_s",
              "t_elec_min", "t_final_min", "inefficiency"]:
        v = LAYP[k]
        ut.append([f"`{k}`", f"{v.value:g} {v.unit}", v.status, "layout study `scripts/inputs.py`", v.note])
    for k, v in TIME.items():
        ut.append([f"`{k}`", f"{v.value:g} {v.unit}", v.status, v.source, v.note])
    G["UNIT_TIMES"] = md_table(["Name", "Value", "Status", "Source", "What it is"], ut)
    # biggest time sinks
    top = sorted(((st, tr) for st, tr in zip(STEPS, m.steps) if st["n"] <= CLOCK_LAST_STEP), key=lambda x: -x[1]["elapsed"])[:5]
    G["TOP_STEPS"] = "\n".join(f"{i}. Step {st['n']} ({st['title']}): {tr['elapsed'] / 60:.0f} min." for i, (st, tr) in enumerate(top, 1))
    return G


def fill(template, values):
    def rep(mo):
        k = mo.group(1)
        if k not in values:
            raise KeyError(f"template placeholder {{{{{k}}}}} has no value")
        return values[k]
    return re.sub(r"\{\{([A-Z0-9_]+)\}\}", rep, template)


def packing_csv(m):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["label", "part_number", "name", "name_vi", "position", "pallet", "place", "fitted_in_step", "kg", "kg_status",
                "mass_source", "size_mm", "size_source", "glass", "note"])
    place = {t: f"pallet 1, stack slot {i} from the open face" for i, t in enumerate(STACK1, 1)}
    for tr in TIERS2:
        for ln in tr["lanes"]:
            for t in ln["tags"]:
                place[t] = f"pallet 2, {tr['name'].split(':')[0].lower()}, lane {ln['width']:g} mm"
    for i, t in enumerate(CRATE_TAGS):
        place[t] = f"pallet 2, tier 1, glass crate, layer {i + 1} from the bottom"
    for p in m.shipped():
        src = "; ".join(f"roll-up: {resolve(m.roll, h)}" + ("" if abs(u - 1) < 1e-9 else f" x {u:g}") for h, u in p.mass)
        if p.extra_kg:
            src = (src + "; " if src else "") + p.extra_note
        w.writerow([p.tag, p.pn, p.name, p.vi, p.pos, p.pallet, place[p.tag], p.step, f"{p.kg:.3f}", p.status, src,
                    dims_txt(p.dims), p.dims_src, "yes" if p.glass else "no", p.note])
    return buf.getvalue()


# ------------------------------------------------------------------------------------------- SVG
def svg_text(x, y, s, size=12, anchor="start", weight="normal", fill="#222"):
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f'<text x="{x:.1f}" y="{y:.1f}" font-family="Helvetica, Arial, sans-serif" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{fill}">{s}</text>'


def svg_pallet1(m):
    rows, thick, h1, _ = m.stack1()
    sc = 0.36
    W, H = 1180, 820
    ox, oy = 70, 720
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
           f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
           svg_text(20, 30, "910001 P01  PALLET LOAD 1 - 48 x 40 in (1219 x 1016 mm) - upright stack, side view across the 40 in side", 15, weight="bold"),
           svg_text(20, 50, f"Gross {m.gross(1):.0f} kg, loaded height {h1:.0f} mm, stack {thick:.0f} of 1016 mm. Open face on the LEFT: take pieces in label order. Units mm. DRAFT.", 12)]
    # deck
    deck_w = MINE["pal_std_w_exact"].value
    out.append(f'<rect x="{ox}" y="{oy}" width="{deck_w * sc:.1f}" height="{lay("pal_std_h") * sc:.1f}" fill="#d2b48c" stroke="#7a5c2e"/>')
    out.append(svg_text(ox + deck_w * sc / 2, oy + 30, "48 x 40 pallet, 121", 11, "middle"))
    x = ox + lay("edge_board") * sc
    out.append(f'<rect x="{ox}" y="{oy - 1500 * sc:.1f}" width="{lay("edge_board") * sc:.1f}" height="{1500 * sc:.1f}" fill="#999"/>')
    for r in rows:
        p = PIECE[r["tag"]]
        w = r["thick"] * sc
        h = r["up"] * sc
        out.append(f'<rect x="{x:.1f}" y="{oy - h:.1f}" width="{max(w, 1.0):.1f}" height="{h:.1f}" fill="{GROUP_COLOUR[p.group]}" stroke="#333" stroke-width="0.4"/>')
        out.append(f'<g transform="translate({x + w / 2 + 3:.1f},{oy - 6:.1f}) rotate(-90)">' +
                   svg_text(0, 0, f"{p.tag} {p.pos} {p.kg:.1f} kg (step {p.step})", 8) + "</g>")
        x += w + lay("pack_gap") * sc
    out.append(f'<rect x="{x - lay("pack_gap") * sc:.1f}" y="{oy - 1500 * sc:.1f}" width="{lay("edge_board") * sc:.1f}" height="{1500 * sc:.1f}" fill="#999"/>')
    top = oy - (h1 - lay("pal_std_h")) * sc
    out.append(f'<line x1="{ox - 10}" y1="{top:.1f}" x2="{ox + deck_w * sc + 10:.1f}" y2="{top:.1f}" stroke="#c0392b" stroke-dasharray="4 3"/>')
    out.append(svg_text(ox + deck_w * sc + 14, top + 4, f"top of load {h1:.0f} (limit 1829)", 11, fill="#c0392b"))
    lim = oy - (lay("max_load_h") - lay("pal_std_h")) * sc
    out.append(f'<line x1="{ox - 10}" y1="{lim:.1f}" x2="{ox + deck_w * sc + 10:.1f}" y2="{lim:.1f}" stroke="#555" stroke-dasharray="2 4"/>')
    out.append(svg_text(ox + deck_w * sc + 14, lim + 4, "1829 limit", 11))
    out.append(svg_text(ox - 8, oy - 1520 * sc, "OPEN FACE", 11, weight="bold"))
    # legend
    ly = 90
    for g in ["BASE", "WALL", "CEILING", "LINING"]:
        out.append(f'<rect x="{W - 230}" y="{ly}" width="14" height="14" fill="{GROUP_COLOUR[g]}"/>')
        out.append(svg_text(W - 210, ly + 12, g, 12))
        ly += 22
    out.append(svg_text(W - 230, ly + 20, "Pairs face to face:", 11))
    out.append(svg_text(W - 230, ly + 36, "ACP to ACP, felt to felt,", 11))
    out.append(svg_text(W - 230, ly + 52, "4 mm foam between every piece.", 11))
    out.append("</svg>")
    return "\n".join(out) + "\n"


def svg_pallet2(m):
    tiers, h2 = m.tiers2()
    sc = 0.30
    W, H = 1500, 1080
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
           f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
           svg_text(20, 30, "910002 P01  PALLET LOAD 2 - 96 x 48 in (2438 x 1219 mm) - five tiers", 15, weight="bold"),
           svg_text(20, 50, f"Gross {m.gross(2):.0f} kg, loaded height {h2:.0f} mm. Left: side elevation along the 96 in side. Right: each tier from above. Units mm. DRAFT.", 12)]
    # side elevation
    ox, oy = 40, 620
    L = MINE["pal_long_l_exact"].value
    out.append(f'<rect x="{ox}" y="{oy}" width="{L * sc:.1f}" height="{lay("pal_long_h") * sc:.1f}" fill="#d2b48c" stroke="#7a5c2e"/>')
    out.append(svg_text(ox + L * sc / 2, oy + 24, "96 x 48 pallet, 121", 11, "middle"))
    for t in tiers:
        y0 = oy - (t["z0"] - lay("pal_long_h") + t["h"]) * sc
        out.append(f'<rect x="{ox}" y="{y0:.1f}" width="{L * sc:.1f}" height="{t["h"] * sc:.1f}" fill="none" stroke="#999" stroke-dasharray="3 3"/>')
        # tallest lane drawn
        for ln in t["lanes"]:
            xx = ox
            for it in ln["items"]:
                col = "#e8e8e8" if it["tag"] == "CRATE" else GROUP_COLOUR[PIECE[it["tag"]].group]
                out.append(f'<rect x="{xx:.1f}" y="{y0 + (t["h"] - it["up"]) * sc:.1f}" width="{it["along"] * sc:.1f}" height="{it["up"] * sc:.1f}" fill="{col}" fill-opacity="0.35" stroke="#333" stroke-width="0.4"/>')
                xx += it["along"] * sc
        out.append(svg_text(ox + L * sc + 8, y0 + t["h"] * sc / 2 + 4, f"{t['name']} ({t['h']:.0f})", 10))
    top = oy - (h2 - lay("pal_long_h")) * sc
    out.append(f'<line x1="{ox - 10}" y1="{top:.1f}" x2="{ox + L * sc + 10:.1f}" y2="{top:.1f}" stroke="#c0392b" stroke-dasharray="4 3"/>')
    out.append(svg_text(ox, top - 6, f"top of load {h2:.0f} (limit 1829)", 11, fill="#c0392b"))
    # plans per tier
    px, py = 40, 700
    sp = 0.12
    col_w = 2438 * sp + 30
    for i, t in enumerate(tiers):
        cx = px + (i % 3) * (col_w + 120)
        cy = py + (i // 3) * (1219 * sp + 60)
        out.append(svg_text(cx, cy - 6, t["name"], 10, weight="bold"))
        out.append(f'<rect x="{cx}" y="{cy}" width="{2438 * sp:.1f}" height="{1219 * sp:.1f}" fill="none" stroke="#7a5c2e"/>')
        yy = cy
        for ln in t["lanes"]:
            xx = cx
            for it in ln["items"]:
                col = "#e8e8e8" if it["tag"] == "CRATE" else GROUP_COLOUR[PIECE[it["tag"]].group]
                out.append(f'<rect x="{xx:.1f}" y="{yy:.1f}" width="{it["along"] * sp:.1f}" height="{it["across"] * sp:.1f}" fill="{col}" fill-opacity="0.6" stroke="#333" stroke-width="0.4"/>')
                if it["across"] * sp >= 7:
                    label = "CRATE: 2-01 over 2-02" if it["tag"] == "CRATE" else it["tag"]
                    out.append(svg_text(xx + 3, yy + min(it["across"] * sp, 12) - 2, label, 7))
                xx += it["along"] * sp
            yy += ln["width"] * sp
    # legend
    ly = 80
    for g in ["BASE", "FRONT", "AIR", "LINING", "ELECTRICAL", "INTERIOR", "KIT"]:
        out.append(f'<rect x="{W - 200}" y="{ly}" width="14" height="14" fill="{GROUP_COLOUR[g]}"/>')
        out.append(svg_text(W - 180, ly + 12, g, 12))
        ly += 22
    out.append(svg_text(W - 200, ly + 16, "Glass crate: light grey.", 11))
    out.append("</svg>")
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------------------------------- outputs
def crate_mass(self):
    return sum(PIECE[t].kg for t in CRATE_TAGS) + MINE["crate_kg"].value + MINE["glass_rest_kg"].value


Model.crate_mass = crate_mass


def outputs(m):
    T = gen_tables(m)
    G = guide_tables(m, T)
    return {
        OUT_LIST: packing_csv(m),
        OUT_PLAN: fill(TPL_PLAN.read_text(encoding="utf-8"), T),
        OUT_SVG[1]: svg_pallet1(m),
        OUT_SVG[2]: svg_pallet2(m),
        OUT_GUIDE: fill(TPL_GUIDE.read_text(encoding="utf-8"), G),
        OUT_STEP_BODIES: step_bodies_json(),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="fail if an output is stale or a check fails")
    ap.add_argument("--joints", help="joints register file to check the bolt totals against")
    a = ap.parse_args(argv)
    m = Model(a.joints)
    outs = outputs(m)
    for c in m.checks:
        print(f"[{c['id']}] {'PASS' if c['ok'] else 'FAIL'}  {c['what']}: {c['result']}")
    if a.check:
        stale = [p for p, s in outs.items() if not p.exists() or p.read_text(encoding="utf-8") != s]
        for p in stale:
            print(f"STALE: {p.relative_to(REPO)}")
        if stale or not m.ok():
            print("FAILED")
            return 1
        print("OK: outputs current, all checks pass")
        return 0
    for p, s in outs.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(s, encoding="utf-8")
        print(f"wrote {p.relative_to(REPO)}")
    return 0 if m.ok() else 1


if __name__ == "__main__":
    sys.exit(main())
