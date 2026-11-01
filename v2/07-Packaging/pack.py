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
Part numbers: a piece marked "TBD (owner)" takes the master BOM's number (../04-BOM/100000_P01_POD-MASTER_BOM.csv)
as soon as the owner's parts list carries its exact name, and every number on a label must be the BOM's (check K13).

    python3 v2/07-Packaging/pack.py                 # write every output
    python3 v2/07-Packaging/pack.py --check         # exit 1 if an output is stale or a check fails
    python3 v2/07-Packaging/pack.py --joints PATH   # check the bolt totals against that joints register
"""
import argparse
import copy
import csv
import itertools
import math
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
OUT_INSTALL = GUIDE_DIR / "100000_P04_POD-INSTALL-SHEET_INS.md"
TPL_PLAN = HERE / "templates" / "packing-plan.md"
TPL_GUIDE = HERE / "templates" / "assembly-guide.md"
TPL_INSTALL = HERE / "templates" / "install-sheet.md"

sys.path.insert(0, str(LAY / "scripts"))
from inputs import P as LAYP  # noqa: E402  (the layout study's inputs: value, unit, status, source, note)

KG_PER_LB = 0.45359237
MM_PER_IN = 25.4


SKEL_CSV = REPO / "v2" / "01-CAD-Native" / "skeleton" / "100000_P04_POD-SKELETON-PARAMETERS.csv"
MASTER_BOM = REPO / "v2" / "04-BOM" / "100000_P01_POD-MASTER_BOM.csv"
MANUF = REPO / "v2" / "03-Manufacturing"
STEP_READER = REPO / "tools" / "checks"     # stepfile.py, the mechanical checks' STEP reader (standard library only)
# Numbers on a label that are not master BOM rows, with the reason (check K13).
NOT_BOM_ROWS = {"109000": "the installation kit: the assembly tree's family 10 node; the master BOM lists its contents"}


def _load_skeleton(path=SKEL_CSV):
    """The skeleton's named values (its 'value' column, mm), so panel sizes follow the skeleton instead of typed numbers."""
    with open(path, encoding="utf-8") as f:
        return {r["parameter"]: float(r["value"]) for r in csv.DictReader(f)}


SK = _load_skeleton()


def sk(name):
    return SK[name]


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
    "crate_l": N(2210, "mm", "calculation", "this plan", "door unit 2106 (D-132: the kick strip 10 lower) + 2 x 5 edge foam + 2 x 45 end rails = 2206, rounded up"),
    "crate_w": N(1219, "mm", "calculation", "this plan", "the full 48 in deck: door 1177 + 2 x 5 edge foam + 2 x 15 side rails = 1217"),
    "crate_side_rail": N(15, "mm", "assumption", "this plan", "plywood side rail, so the 1177 door (FRONT's CAD: its magnetic seal half 2 mm past the glass) fits a 1219 crate"),
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
    "wrap": N(5, "mm", "assumption", "this plan", "per side on pallet 2, between a part's own size and its lane and tier: about 3 mm of PE foam wrap and the corner guards; a carton is its own outer box"),
    "dr_bed": N(10, "mm", "assumption", "this plan", "foam sheet under DR's flat front face: DR lies face down with its felt panel up and nothing on it (PM, 2026-11-01)"),
    "cad_tol": N(0.5, "mm", "assumption", "this plan", "check K14: how far a CAD box may pass the planned size (rounding)"),
    # installation kit aids (design review 2026-11-01)
    "stay_kg": N(1.5, "kg", "assumption", "this plan", "one clamp-on glass stay: a padded clamp on the fixed glass's top edge with a telescopic prop to the base band, so the glass stands while both people bring DR (step 10)"),
    "packer_h": N(7, "mm", "source", "step 11 (FRONT's door: the 7 mm running gap over the threshold)", "the setting packers the door stands on at hinge height while it is hung"),
    "packer_kg": N(0.05, "kg", "assumption", "this plan", "a pair of plastic setting packers"),
    "kit_aids_l": N(900, "mm", "assumption", "this plan", "the kit carton's length, for the collapsed glass stays"),
    # the room (install sheet, IF-17)
    "roof_work": N(150, "mm", "assumption", "this plan", "clear above the roof at its slot: room to drop the 68 mm roof sleeve in and for hands and the 5 mm key at the grille's 4 bolts (step 18, J-AIR-03)"),
    "spigot_lift": N(20, "mm", "assumption", "this plan", "DT and the ceiling halves are lifted over their 8 mm locating spigots and lowered on (J-FRONT-03, J-CEIL-01)"),
    "glide_min": N(8.5, "mm", "confirmed", "PM ruling on F-018 (joints register)", "the lowest glide setting: the band's bottom 8.5 mm above the floor"),
    "glide_max": N(15, "mm", "assumption", "ISS-054 (PROPOSED): the glides take the floor's 10 ± 5 mm", "the highest glide setting"),
    "lay_out": N(1000, "mm", "assumption", "this plan", "clear round the footprint while the pod goes together: the parts set down at their places (step 1) and the step stools"),
    # getting the pieces in (install sheet, check K15; US review 2026-11-01)
    "lift_door_w": N(1070, "mm", "calculation", "this plan, check K15", "the elevator's door: DR's 1030 mm face in its wrap goes across it with 20 mm a side for hands; a 42 in (1067) door is 3 mm short, so in practice 48 in"),
    "lift_door_h": N(2134, "mm", "source", "a common US elevator door, 84 in", "the elevator's door height"),
    "lift_car_w": N(2032, "mm", "source", "a common US passenger car, 80 in (the Lead's US review)", "the car's inside width"),
    "lift_car_d": N(1295, "mm", "source", "a common US passenger car, 51 in (the Lead's US review)", "the car's inside depth"),
    "lift_car_h": N(2286, "mm", "calculation", "this plan, check K15", "the car's inside height, 90 in: the soffit doesn't lean in under 84 in"),
    "typ_door_w": N(914, "mm", "source", "a common US passenger elevator door, 36 in (the Lead's US review)", "for the pieces a typical car can't take"),
    "typ_car_h": N(2438, "mm", "source", "a common US passenger car, 8 ft", "for the pieces a typical car can't take"),
    "lifter": N(100, "mm", "assumption", "this plan", "a suction lifter stands this far off the face of the pane it holds"),
    "hand_gap": N(20, "mm", "assumption", "this plan", "room a side for hands and the wrap when a piece goes through a door"),
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
    "t_light_shelf_s": N(600, "s", "assumption", "this plan", "fit and plug the light shelf along the wall tops (D-70; INTERIOR 810201, its fixings not listed yet)"),
    "t_ledge_two_s": N(120, "s", "assumption", "this plan", "hold the 1000 mm ledge in place while it is fixed (D-70; INTERIOR 810101)"),
    "t_ledge_one_s": N(600, "s", "assumption", "this plan", "fix the ledge's 2 brackets to R1's stiles and the screen rail to R2's stiles (D-70, IF-16; brackets 818101 and rail 818102 HOLD, their screws not listed yet)"),
    "t_carry_staged_s": N(20, "s", "assumption", "this plan (D-87)", "carry a pallet 2 part that step 1 set down at its place: a few steps"),
    "t_level_preset_s": N(240, "s", "assumption", "this plan (D-87)", "check the band with the spirit level and turn only the glides that are out; glides preset at the factory"),
    "t_hook_s": N(120, "s", "assumption", "this plan (D-87)", "hang a part on its tool-free hooks and check it"),
    "t_tilt_s": N(60, "s", "assumption", "this plan (design review)", "tilt a pane up in the crate on its padded long edge, both lifters at its top edge, onto the padded glass rest"),
    "t_stay_on_s": N(60, "s", "assumption", "this plan (design review)", "clamp one glass stay on the fixed glass and set its prop"),
    "t_stay_off_s": N(30, "s", "assumption", "this plan (design review)", "take one glass stay off"),
    "t_packer_s": N(30, "s", "assumption", "this plan (design review)", "lay the setting packers under the door, or slide them out"),
    "t_sleeve_s": N(90, "s", "assumption", "this plan (#263)", "from a step stool outside the front right corner, drop the roof sleeve through C2's roof slot onto its gasket on the exhaust fan box"),
    "t_grille_set_s": N(60, "s", "assumption", "this plan (#263, J-AIR-03)", "lay the roof grille on the sleeve's flange, holes on the rivnuts, and start its 4 bolts by hand; driving them is the register bolts' time"),
    "t_selftest_s": N(180, "s", "assumption", "this plan (D-87)", "power on and the hub's self-test: both fan pairs, the lights and the sensors run and it shows pass or fail"),
    "t_peel_tab_s": N(6, "s", "assumption", "this plan (D-87)", "pull one film panel off by its quick-release tab"),
    "t_peel_s": N(20, "s", "assumption", "this plan", "find the edge of a film panel with no tab and peel it, for comparison"),
}

# Site fixings the joints register doesn't count (its section 3.9 lists them as out of scope). Counts are working
# values for the time model and the parts kit until each owner's design gives them.
OTHER_FIXINGS = [
    dict(step=2, where="Base band corner keys (6 keys; the side bands carry the back-corner keys, D-129)", owner="BASE", count=0, size="none on site: hook studs and fixing bolts in the factory",
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
    dict(step=14, where="Intake riser and supply fan box in DR", owner="AIR and FRONT", count=0, size="not designed yet (HOLD)",
         status="HOLD in the register", note="time is in the step", text="their fixings in DR (AIR and FRONT design, on hold)"),
    dict(step=16, where="Air column on DR and the floor", owner="AIR", count=0, size="none on site: 2 hook studs set in the factory, 2 spigots",
         status="registered: J-AIR-02 (0 on site)", note="D-87: the column hangs on its hook studs",
         text="the column hangs on its 2 factory-set hook studs and stands on 2 spigots, no site bolts (J-AIR-02)"),
    dict(step=20, where="Light shelf", owner="INTERIOR", count=0, size="not in INTERIOR's parts list yet (HOLD)", status="HOLD (D-70)",
         note="time is in the step", text="the light shelf's fixings (INTERIOR's parts list 810201 names none yet)"),
    dict(step=23, where="Ledge and screen rail", owner="INTERIOR", count=0, size="brackets and rail on HOLD; screws not listed yet",
         status="HOLD (D-70, IF-16)", note="time is in the step",
         text="the ledge's 2 brackets 818101 on R1's stiles, on stand-offs through R1's cassette, and the screen rail 818102 on stand-offs to R2's stiles (INTERIOR; both HOLD)"),
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
    "SEALS": "Base seal and cable grommets",   # the door edge seals are in FRONT's parts lists (PM ruling, #105)
    "ELEC": "Switches and harness",   # ELECTRICAL's line: the power unit (in B2, its share from ELECTRICAL's parts list) + the kit 2-13
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
    carton: bool = False        # a carton or a kit box: its size is the outer box, so it gets no wrap on pallet 2

    def __post_init__(self):
        self.pn_declared, self.vi_declared = self.pn, self.vi
    status: str = ""


def S(*a):
    return tuple(sorted(a, reverse=True))


P04 = "skeleton P04 named values (100000_P04_POD-SKELETON-PARAMETERS.csv)"
FLOOR_W_MAX = 1219   # the floor panel with its lap, at most (PM ruling, packing group, 2026-10-31)
ELEC_PARTS = REPO / "v2" / "03-Manufacturing" / "electrical" / "710000_P01_ELECTRICAL-PARTS-LIST_BOM.csv"


def power_unit_share(parts=ELEC_PARTS):
    """B2's share of ELECTRICAL's roll-up line: the power unit 710001's mass in ELECTRICAL's parts list over the line's mass.
    Both are read from their files on every run, so a new ELECTRICAL CAD mass flows through (no typed share)."""
    with open(parts, encoding="utf-8") as f:
        unit = next(float(r["mass_each_kg"]) for r in csv.DictReader(f) if r["part_number"] == "710001")
    roll = read_rollup()
    return unit / roll[resolve(roll, "ELEC")]["kg_each"]


POWER_UNIT_SHARE = power_unit_share()
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
    Piece("1-01", "110401", "BASE - FLOOR PANEL ASSY - F1", "Tấm sàn F1 (cụm dán)", "F1", [("FLOOR", 1), ("MAT", 0.5)], S(sk("wall_depth") - sk("band_t"), FLOOR_W_MAX, sk("floor_t") + sk("mat_t")),
          "skeleton named values: wall_depth - band_t deep, floor_t + mat_t thick; 1219 wide at most with its lap (PM ruling, packing group)",
          1, 3, "BASE", note="the panel 111401 with its foam mat 111501 bonded under it at the factory (D-87)"),
    Piece("1-02", "TBD (BASE)", "BASE - FLOOR PANEL ASSY - F2", "Tấm sàn F2 (cụm dán)", "F2", [("FLOOR", 1), ("MAT", 0.5)], S(sk("wall_depth") - sk("band_t"), FLOOR_W_MAX, sk("floor_t") + sk("mat_t")),
          "as F1", 1, 3, "BASE", note="foam mat bonded under it at the factory (D-87)"),
    Piece("1-03", "210201", "WALL - PANEL ASSY - BACK LOWER - B1", "Vách hậu - cụm tấm dưới trái", "B1", [("B", 1)],
          S(sk("half_pw"), 1127, sk("outer_t")), "WALL 210201 P01 STEP: 1200.6 x 1126.6 x 46, its locating spigots 8 mm out of the top edge", 1, 4, "WALL"),
    Piece("1-04", "210202", "WALL - PANEL ASSY - BACK LOWER - B2", "Vách hậu - cụm tấm dưới phải", "B2",
          [("B", 1), ("ELEC", POWER_UNIT_SHARE)], S(sk("half_pw"), 1127, 88),
          "WALL 210202 P01 STEP with ELECTRICAL's power unit 710001 fitted (710000 P01 STEP): 1200.6 x 1126.6 x 87.5",
          1, 4, "WALL",
          note="carries the power unit 710001, fitted, wired and tested at the factory: its mass from ELECTRICAL's parts list, as a share of ELECTRICAL's roll-up line; foam block over the unit's face in the stack"),
    Piece("1-05", "210101", "WALL - PANEL ASSY - SIDE LOWER - LH", "Vách trái - cụm tấm dưới", "L1", [("L1R1", 1)],
          S(sk("side_l"), 1151, 48.5), "WALL 210101 P01 STEP: 1492.7 x 1150.7 x 48.3, spigots 8 mm out of the top edge, rivnuts and stop washers 2.3 mm proud", 1, 5, "WALL"),
    Piece("1-06", "210102", "WALL - PANEL ASSY - SIDE LOWER - RH", "Vách phải - cụm tấm dưới", "R1", [("L1R1", 1)],
          S(sk("side_l"), 1151, 48.5), "WALL 210102 P01 STEP, as L1", 1, 5, "WALL"),
    Piece("1-07", "TBD (WALL)", "WALL - PANEL ASSY - BACK UPPER - B3", "Vách hậu - cụm tấm trên trái", "B3", [("B", 1)],
          S(sk("half_pw"), sk("back_ph"), sk("outer_t")), P04, 1, 6, "WALL"),
    Piece("1-08", "TBD (WALL)", "WALL - PANEL ASSY - BACK UPPER - B4", "Vách hậu - cụm tấm trên phải", "B4", [("B", 1)],
          S(sk("half_pw"), sk("back_ph"), sk("outer_t")), P04, 1, 6, "WALL"),
    Piece("1-09", "210103", "WALL - PANEL ASSY - SIDE UPPER - LH", "Vách trái - cụm tấm trên", "L2", [("L2R2", 1)],
          S(sk("side_l"), sk("side_h"), 48.5), "WALL 210103 P01 STEP: 1492.7 x 1142.7 x 48.3, rivnuts and stop washers 2.3 mm proud", 1, 7, "WALL"),
    Piece("1-10", "210104", "WALL - PANEL ASSY - SIDE UPPER - RH", "Vách phải - cụm tấm trên", "R2", [("L2R2", 1)],
          S(sk("side_l"), sk("side_h"), 48.5), "WALL 210104 P01 STEP, as L2", 1, 7, "WALL"),
    Piece("1-11", "410101", "CEILING - PANEL ASSY - C1", "Trần - tấm trái (cụm)", "C1", [("C", 1)],
          S(sk("wall_depth"), sk("half_pw"), sk("outer_t")), "skeleton named values: wall_depth long, half_pw wide, outer_t", 1, 8, "CEILING"),
    Piece("1-12", "410102", "CEILING - PANEL ASSY - C2", "Trần - tấm phải (cụm)", "C2", [("C", 1), ("ROOF", 1)],
          S(sk("wall_depth"), sk("half_pw"), 70), "CEILING 410000 P01 STEP with AIR's roof sleeve 611601 seated loose in its roof slot (22 mm below the frame) and the grille 611602 over it (AIR 610000 P01 STEP): 70 thick", 1, 8, "CEILING",
          note="the roof sleeve and grille ride loose with C2 (#263), the grille's 4 bolts and washers (J-AIR-03) in a bag taped to the grille: the sleeve seated in C2's roof slot and taped, the grille taped flat over it; both come off at unpacking and go on after the soffit hangs (guide step 18)"),
    Piece("1-13", "510102", "LINING - CASSETTE - SIDE LOWER - RH", "Cassette tiêu âm - vách phải dưới", "R1", [("CS_LO", 1)],
          S(1445, sk("side_h"), 38), "WALL 510102 P01 STEP: tray 34 and the HOLD clip zones 4 mm on its back", 1, 15, "LINING"),
    Piece("1-14", "510104", "LINING - CASSETTE - SIDE UPPER - RH", "Cassette tiêu âm - vách phải trên", "R2", [("CS_UP", 1)],
          S(1445, 1092.74, 38), "WALL 510104 P01 STEP: tray 34 and the HOLD clip zones 4 mm on its back", 1, 15, "LINING"),
    Piece("1-15", "510101", "LINING - CASSETTE - SIDE LOWER - LH", "Cassette tiêu âm - vách trái dưới", "L1", [("CS_LO", 1)],
          S(1445, sk("side_h"), 38), "WALL 510101 P01 STEP: tray 34 and the HOLD clip zones 4 mm on its back", 1, 15, "LINING"),
    Piece("1-16", "510103", "LINING - CASSETTE - SIDE UPPER - LH", "Cassette tiêu âm - vách trái trên", "L2", [("CS_UP", 1)],
          S(1445, 1092.74, 38), "WALL 510103 P01 STEP: tray 34 and the HOLD clip zones 4 mm on its back", 1, 15, "LINING"),
    Piece("1-17", "510201", "LINING - CASSETTE - BACK LOWER - B1", "Cassette tiêu âm - vách hậu dưới trái", "B1", [("CB_LO", 1)],
          S(1166, sk("back_ph"), 38), "WALL 510201 P01 STEP: tray 34 and the HOLD clip zones 4 mm on its back", 1, 15, "LINING"),
    Piece("1-18", "510202", "LINING - CASSETTE - BACK LOWER - B2", "Cassette tiêu âm - vách hậu dưới phải", "B2", [("CB_LO", 1)],
          S(1166, sk("back_ph"), 38), "WALL 510202 P01 STEP: tray 34 and the HOLD clip zones 4 mm on its back", 1, 15, "LINING"),
    Piece("1-19", "TBD (WALL)", "LINING - CASSETTE - BACK UPPER - B3", "Cassette tiêu âm - vách hậu trên trái", "B3", [("CB_UP", 1)],
          S(1166, 1116.87, 38), "skeleton P04; 38 thick as B1's cassette in CAD (no CAD of its own yet)", 1, 15, "LINING"),
    Piece("1-20", "TBD (WALL)", "LINING - CASSETTE - BACK UPPER - B4", "Cassette tiêu âm - vách hậu trên phải", "B4", [("CB_UP", 1)],
          S(1166, 1116.87, 38), "skeleton P04; 38 thick as B1's cassette in CAD (no CAD of its own yet)", 1, 15, "LINING"),
    # ---------------- pallet 2, 96 x 48 in: tiers, bottom (tier 1) to top (tier 5)
    Piece("2-01", "360002", "FRONT - FIXED GLASS UNIT", "Cụm vách kính cố định", "-", [("FIX", PANE_SHARE)], S(2034, 1031, 12),
          "FRONT 360002 P01 STEP: the pane with its 180 seal half, 2034 x 1027 x 12 (its U-channels and U-seals ship elsewhere)", 2, 10, "FRONT", glass=True,
          note="the pane with its 180 seal; its U-channels and seals ship fitted on the sill (PM ruling), in DR and in DT (D-68)"),
    Piece("2-02", "360001", "FRONT - DOOR UNIT", "Cụm cửa kính", "-", [("DOOR", 1)], S(2106, 1177, 149),
          "FRONT 360001 P01 STEP without its hinges and its end brush 368008 (in the door's kit bag, fitted on site): 2105.5 x 1177 x 148.8 (D-132: the kick strip down to the band's bottom line, 10 mm taller; the magnetic seal half 2 mm past the glass, the pulls 70 a side); the hinge halves that sit in DL ship in DL (PM ruling)",
          2, 11, "FRONT", glass=True),
    Piece("2-03", "350003", "FRONT - DECOR BLOCK ASSY - DR", "Khối trang trí phải (cụm)", "DR", [("DR", 1), ("FIX", DR_CHANNEL_SHARE)], S(2290, 1020, 216),
          "FRONT 350003 P01 STEP: 2290 x 1020 x 215.5, the inner felt panel 10.5 mm proud of the back plate; AIR's reserved spaces in it are empty when it ships", 2, 10, "FRONT",
          note="lies on its flat front face on a foam sheet, felt panel up, nothing on it (PM, 2026-11-01)"),
    Piece("2-04", "110103", "BASE - BAND ASSY - BACK", "Viền chân nhôm - cạnh sau (cụm)", "-", [("BAND_B", 1), ("GLIDE", 3), ("BLOCKS", 3 / 8)],
          S(2420, 118, 40), "BASE 110000 P01 STEP, the back band 110103 without corner keys (D-129: the side bands carry them): tube 2420, glides 10 below, spigots 8 above", 2, 2, "BASE",
          note="3 glides fitted, each on its aluminium load block inside the band (BASE CAD; D-86); blocks split by glide count, 3 of 8; keyholes for the side bands' back-corner keys (D-129)"),
    Piece("2-05", "110101", "BASE - BAND ASSY - SIDE - LH", "Viền chân nhôm - cạnh trái (cụm)", "-", [("BAND_S", 1), ("GLIDE", 2), ("BLOCKS", 2 / 8), ("KEY", 2)],
          S(1517, 118, 48), "BASE 110000 P01 STEP, the side band 110101 (1517 x 118 x 40), plus its back-corner key's hook studs out of its inner wall: key face 1.5 inside the wall, M6 x 16 studs with a 1.8 head gap (corner-keys.csv, #241), 8 mm allowed until BASE's CAD carries the keys", 2, 2, "BASE",
          note="2 glides fitted, each on its load block inside the band (BASE CAD; D-86); the back-corner key 111211 against its inner wall (D-129) and the front-corner key 111212 in its front end, both fitted at the factory (J-BASE-02)"),
    Piece("2-06", "TBD (BASE)", "BASE - BAND ASSY - SIDE - RH", "Viền chân nhôm - cạnh phải (cụm)", "-", [("BAND_S", 1), ("GLIDE", 2), ("BLOCKS", 2 / 8), ("KEY", 2)],
          S(1517, 118, 48), "LH's mirror (BASE P01 CAD), with its two keys", 2, 2, "BASE",
          note="2 glides fitted, each on its load block inside the band (D-86); the back-corner key 111211 against its inner wall (D-129) and the front-corner key 111213 in its front end, both fitted at the factory (J-BASE-02)"),
    Piece("2-07", "TBD (BASE)", "BASE - BAND ASSY - FRONT - RH - UNDER THE FIXED GLASS", "Viền chân nhôm - trước phải, dưới kính", "-",
          [("BAND_FR", 0.663), ("GLIDE", 1), ("BLOCKS", 1 / 8), ("FIX", SILL_CHANNEL_SHARE)], S(729, 118, 40),
          "X 218 to about 947 (skeleton P04 front band; air report 7e); 118 high with its glide and spigots, as the side band's CAD (assumption); carries the glass's bottom U-channel (D-68)", 2, 2, "BASE",
          note="the sill: the fixed glass's bottom U-channel and its seal fitted at the factory with 4 M3 countersunk screws (PM ruling); share of the front-r line by length, 729 of 1100 mm (calculation); 1 glide on its load block (D-86)"),
    Piece("2-08", "TBD (BASE)", "BASE - DOOR THRESHOLD - 13 MM", "Ngưỡng cửa thấp 13 mm", "-", [("THRESH", 1)], S(1175, 60, 13),
          "skeleton P04 1175 x 60; 13 mm high (D-72)", 2, 3, "BASE"),
    Piece("2-09", "350001", "FRONT - DECOR BLOCK ASSY - DL", "Khối trang trí trái (cụm)", "DL", [("DL", 1)], S(2292, 308, 199),
          "FRONT 350001 P01 STEP: its hinge-side stops stand 30 mm past the skin", 2, 9, "FRONT",
          note="the hinge halves that sit in DL ship fitted in it (PM ruling); stands on its outer side, stops and seals up"),
    Piece("2-10", "610201", "AIR - SOFFIT", "Hộp gió trên cửa", "-",
          [("SOFFIT", 1), ("FANBOX_E", 1), ("FANS", 0.5)], S(2322, 359, 233),
          "AIR 610000 P01 STEP: the soffit 610201 with its exhaust fan box and fans (the roof sleeve ships with C2, #263)", 2, 17, "AIR",
          note="exhaust fan box 610402 with its 2 fans fitted inside the soffit's right end at the factory (D-87), the roof sleeve's gasket on its top; the exhaust cartridge ships on its own (2-19)"),
    Piece("2-11", "610101", "AIR - AIR COLUMN", "Cột dẫn gió", "-", [("COLUMN", 1)], S(2108, 359, 212),
          "AIR 610000 P01 STEP: the column 610101 with its faces, angles, plates, fill and kick grille, without the supply cartridge", 2, 16, "AIR"),
    Piece("2-12", "350002", "FRONT - DECOR BLOCK ASSY - DT", "Khối trang trí trên (cụm)", "DT", [("DT", 1), ("FIX", DT_CHANNEL_SHARE)], S(1699, 306, 203),
          "FRONT 350002 P01 STEP: the door's top stop and catch stand 26 mm below the skin", 2, 12, "FRONT"),
    Piece("2-13", "TBD (ELECTRICAL)", "ELECTRICAL - KIT - HARNESS, CORD SET, HUB ZONE, LIGHTS", "Bộ điện: dây, dây nguồn, hub, đèn", "-", [("ELEC", 1 - POWER_UNIT_SHARE)],
          S(600, 250, 200), "carton (assumption)", 2, 13, "ELECTRICAL", carton=True),
    Piece("2-14", "810201", "INTERIOR - LIGHT SHELF ASSY", "Kệ đèn hắt (cụm)", "-", [("SHELF", 1)], S(2332, 80, 60),
          "bundle (assumption): INTERIOR's parts list 810201, the 2332 back shelf and the two 991 side shelves (60 x 40 sections) "
          "two high, the down channel and the diffuser inside them", 2, 20, "INTERIOR"),
    Piece("2-15", "TBD (BASE)", "BASE - SMALL PARTS CARTON", "Thùng phụ kiện đế", "-",
          [("BAND_FL", 1), ("BAND_FR", 0.337), ("KEY", 2)], S(600, 400, 150),
          "carton (assumption): the front-left band pieces FL1 (with its knee key 111214) and FL2, faceted, under DL; the mesh intake piece under DR with DR's support, the closing plate (D-62) and the intake support rail with its inline key 111211",
          2, 2, "BASE", carton=True, note="mesh piece share of the front-r line by length, 371 of 1100 mm (calculation); the keys are fitted at the factory in the ends that carry them (J-BASE-02)"),
    Piece("2-16", "810101", "INTERIOR - WORK WALL LEDGE ASSY", "Bàn tựa vách làm việc (cụm)", "-", [("LEDGE", 1)], S(1000, 250, 120),
          "carton (assumption): INTERIOR's parts list, the 1000 x 250 ledge top 811101 with its 2 brackets 818101 (HOLD) "
          "and the screen rail 818102 (HOLD)", 2, 23, "INTERIOR", carton=True,
          note="one carton with the screen rail 818102 (HOLD), as the roll-up's ledge line carries both"),
    Piece("2-17", "610401", "AIR - SUPPLY FAN BOX", "Hộp quạt cấp", "-",
          [("RISER", 1), ("FANBOX_S", 1), ("FANS", 0.5)], S(2005, 516, 203),
          "AIR 610000 P01 STEP: the supply fan box 610401 joined with the intake riser 611501, both transitions and its 2 fans; the Air Engineer's next pass makes it 169 deep, plus D-130's intake boot under it", 2, 14, "AIR",
          note="the intake riser joined to the supply fan box at the factory, one plug-in connector (D-87)"),
    Piece("2-18", "610301", "AIR - SPLITTER CARTRIDGE - COMMON", "Ống tiêu âm (dùng chung)", "-", [("CART_S", 1)], S(1750, 314, 173),
          "AIR 610000 P01 STEP: the cartridge 610301 as it sits in the column", 2, 16, "AIR", note="the supply path's cartridge"),
    Piece("2-19", "610301", "AIR - SPLITTER CARTRIDGE - COMMON", "Ống tiêu âm (dùng chung)", "-", [("CART_E", 1)], S(1750, 314, 173),
          "AIR 610000 P01 STEP: the same part, as it sits in the soffit", 2, 17, "AIR", note="the exhaust path's cartridge"),
    Piece("2-20", "510301", "LINING - CASSETTE - CEILING - COMMON", "Cassette trần (dùng chung)", "C1", [("CC", 1)], S(1163, 1048, 74),
          "CEILING 410000 P01 STEP: 1160 x 1045 x 74, the tray with its ribs, felt, fill bays, clips and catches; returns 1163 x 1048 (PR #32)", 2, 19, "LINING"),
    Piece("2-21", "510301", "LINING - CASSETTE - CEILING - COMMON", "Cassette trần (dùng chung)", "C2", [("CC", 1)], S(1163, 1048, 74),
          "as 2-20", 2, 19, "LINING"),
    Piece("2-22", "109000", "POD - INSTALLATION KIT (OPEN FIRST)", "Bộ phụ kiện lắp (mở trước)", "-", [], S(900, 150, 80),
          "carton (assumption), long enough for the 2 collapsed glass stays", 2, 1, "KIT", carton=True, extra_kg=0.5 + 2 * 1.5 + 0.05,
          extra_note="not in the roll-up: the 5 mm hex key 108001, spare bolts and washers, 2 clamp-on glass stays (step 10), 2 setting packers (step 11), this guide, the label map (assumption)"),
    # ---------------- allowances: roll-up mass that rides inside the pieces above, with no label of its own
    Piece("A-1", "-", "40 x 40 corner edge tubes in L2, R2, C1, C2 (D-63)", "", "-", [("TUBES", 1)], (0, 0, 0), "-", 1, 0, "WALL", kind="allowance"),
    Piece("A-2", "-", "Bond beyond L1 and R1 (D-71)", "", "-", [("BOND", 1)], (0, 0, 0), "-", 1, 0, "WALL", kind="allowance"),
    Piece("A-3", "-", "Captive bolts, washers, rivnuts, stop washers, spigots, gaskets, fitted in the panels", "", "-",
          [("HW", 1)], (0, 0, 0), "-", 1, 0, "WALL", kind="allowance"),
    Piece("A-4", "-", "Base seal and cable grommets, fitted on the band and the panels (the door edge seals are in FRONT's parts)", "", "-",
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
    "1-01": ["F1 ENVELOPE", "F1-MAT ENVELOPE"], "1-02": ["F2 ENVELOPE", "F2-MAT ENVELOPE"],   # the mats ship bonded under the floor (D-87)
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
             12: "front", 15: "inside", 19: "inside"}
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
    dict(pn="918001", name="PACKAGING - PALLET - 48 X 40 IN, NEW WOOD, HEAT-TREATED, ISPM 15 STAMPED, 4-WAY (GMA)", kind="bought", qty=1, kg=lay("pal_std_kg"), wood=True,
         status=LAYP["pal_std_kg"].status, src="layout study S14 (PHS S-4840, 44 lb)", pallet=1),
    dict(pn="918002", name="PACKAGING - PALLET - 96 X 48 IN, NEW WOOD, HEAT-TREATED, ISPM 15 STAMPED, 4-WAY", kind="bought", qty=1, kg=lay("pal_long_kg"), wood=True,
         status=LAYP["pal_long_kg"].status, src="layout study S15 (Uline H-1627, 107 lb)", pallet=2),
    dict(pn="911001", name="PACKAGING - GLASS CRATE: ISPM 15 STAMPED TIMBER RUNNERS, RAILS AND LID SLATS, PLYWOOD SIDES", kind="made", qty=1, kg=MINE["crate_kg"].value, wood=True,
         status="assumption", src="this plan (crate_kg)", pallet=2),
    dict(pn="911002", name="PACKAGING - GLASS REST, A-FRAME, PADDED (PAIR)", kind="made", qty=1, kg=MINE["glass_rest_kg"].value,
         status="assumption", src="this plan (glass_rest_kg); flat-packed in the crate", pallet=2),
    dict(pn="911003", name="PACKAGING - TIER SEPARATOR: ISPM 15 STAMPED TIMBER BATTENS ON POSTS", kind="made", qty=4, kg=MINE["sep_kg"].value, wood=True,
         status="assumption", src="this plan (sep_kg)", pallet=2),
    dict(pn="918010", name="PACKAGING - PROTECTION SET, 48 X 40: fibreboard edge boards and cap board, corner guards, foam interleaf, PE sheets, straps, film",
         kind="bought", qty=1, kg=lay("pack_kg_std"), status=LAYP["pack_kg_std"].status, src="layout study pack_kg_std", pallet=1),
    dict(pn="918011", name="PACKAGING - PROTECTION SET, 96 X 48: fibreboard cap board, corner guards, foam, PE sheets, straps, film",
         kind="bought", qty=1, kg=lay("pack_kg_long"), status=LAYP["pack_kg_long"].status, src="layout study pack_kg_long", pallet=2),
    dict(pn="911010", name="PACKAGING - PART LABEL, 100 X 150 MM, ONE PER PIECE", kind="made", qty=None, kg=0.0, status="-", src="this plan"),
    dict(pn="911011", name="PACKAGING - PALLET LABEL AND DOCUMENT POUCH, 2 PER PALLET", kind="made", qty=4, kg=0.0, status="-", src="this plan"),
]

# ------------------------------------------------------------------------------------------- pallet layouts
# Pallet 1: one upright stack across the 40 in side, parts on edge with their along-size on the 48 in side.
# Listed from the open face. Felt faces meet felt faces (cassettes paired), ACP faces meet ACP faces (outer panels paired).
STACK1 = ["1-%02d" % i for i in range(1, 21)]

# Pallet 2: tiers from the deck up. Each lane runs along the 96 in side; its parts lie end to end. A lane says how its
# parts lie: flat (the thin size up) or on edge (the middle size up), and what lies under them (bed, mm). Its width is
# its widest part plus the wrap a side, and a tier is as tall as its tallest part plus its wrap and bed (tiers2): no typed
# widths, so a part that grows in CAD can't hide behind an old lane size.
TIERS2 = [
    dict(name="Tier 1: glass crate", crate=True),
    dict(name="Tier 2: DR face down, felt up, and the base band", lanes=[
        dict(tags=["2-03"], lie="flat", bed="dr_bed"),
        dict(tags=["2-04"], lie="edge"),
        dict(tags=["2-05", "2-07"], lie="edge"),
        dict(tags=["2-06"], lie="edge")]),
    dict(name="Tier 3: DL on its side, DT, soffit, air column", lanes=[
        dict(tags=["2-09"], lie="edge"),
        dict(tags=["2-12", "2-13"], lie="flat"),
        dict(tags=["2-10"], lie="flat"),
        dict(tags=["2-11"], lie="edge")]),
    dict(name="Tier 4: air parts, light shelf, threshold and cartons", lanes=[
        dict(tags=["2-17"], lie="flat"),
        dict(tags=["2-18"], lie="edge"),
        dict(tags=["2-19"], lie="edge"),
        dict(tags=["2-15", "2-16"], lie="edge"),
        dict(tags=["2-14"], lie="flat"),
        dict(tags=["2-08"], lie="edge")]),
    dict(name="Tier 5: ceiling cassettes (felt up, nothing on them) and the kit", lanes=[
        dict(tags=["2-20", "2-21"], lie="flat", bed="cass_foam"),
        dict(tags=["2-22"], lie="flat")]),
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
         A="Sets the left and right side bands on their glides. Then, with B at the other end, lowers the back band straight down between them: the slots in its end caps take both side bands' back-corner studs from below, and it comes to rest on its own glides (D-129). Then the front pieces, each offered 10 mm high, pushed along its studs and lowered onto its glides: FL1, then FL2 at the knee (under DL), then the intake support rail with the mesh intake piece under DR, DR's support and the closing plate, and last FR1, the piece under the fixed glass, onto the rail (J-BASE-02).",
         caution="Nobody lifts the back band or stands on it until B1 and B2 bolt through its top wall in step 4: until then only its weight holds it on the studs (J-BASE-02).",
         B="Checks the band with the spirit level, corner to corner, and turns only the glides that are out, from above with the hex key. The glides come preset from the factory (D-87); the glide is HOLD and must take the same 5 mm key (REQ-ASM-03).",
         check="Band level within the spirit level's bubble; the back band resting on its glides with both end caps down over the studs; every front piece hooked home; the mesh piece's support stands; the fixed glass's U-channel, fitted on the sill at the factory, is clean and undamaged.",
         ops=[carry("2-04"), carry("2-05"), carry("2-06"), carry("2-07"), carry("2-15"),
              op("set each band piece on its keys", 2, lay("t_place_hung_s"), 7, "t_place_hung_s"),
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
         A="Opens the crate. With B, tilts the fixed glass up on its padded long edge, both suction lifters at its top edge, onto the padded glass rest; then both carry it upright and drop its bottom edge into the U-channel already fitted on the sill, onto its setting blocks. A clamps the 2 glass stays from the kit on its top edge and sets their props on the base band, so the glass stands on its own.",
         B="With A, carries DR (2.3 m, 18 kg) to the right of the opening; both slide it in from the side so its channels take the glass's right and diagonal edges, back onto its stops. Drives 3 bolts into DR from each of R1's and R2's front bays (6); DR stands on its spigots on its support (J-FRONT-02). Only then do the stays come off.",
         caution="Nobody carries DR alone and nobody holds the glass by hand while DR comes in: the stays hold the glass, both people carry DR (2.3 m; the 2-person rule).",
         check="Glass seated in all three channels so far, its free edge plumb; DR on its stops; both stays back in the kit. Do this before the air column: DR's right-hand bolts can't be reached once it stands (J-FRONT-01).",
         ops=[op("tilt the fixed glass up onto the glass rest", 2, TIME["t_tilt_s"].value, 1, "t_tilt_s"),
              carry("2-01"), op("set the fixed glass in the sill's channel", 2, lay("t_fixed_preglazed_min") * 60, 1, "t_fixed_preglazed_min"),
              op("clamp a glass stay on", 1, TIME["t_stay_on_s"].value, 2, "t_stay_on_s"),
              carry("2-03"), op("slide DR onto the glass edges and its stops", 2, TIME["t_dr_slide_s"].value, 1, "t_dr_slide_s"),
              op("take a glass stay off", 1, TIME["t_stay_off_s"].value, 2, "t_stay_off_s")],
         joints={"J-FRONT-01": 6}),
    dict(n=11, title="Door (before DT)", tags=["2-02"],
         A="Lays the 2 setting packers from the kit (7 mm) on the threshold where the door's bottom corners land. With B, tilts the door unit up in the crate on its padded long edge, both suction lifters at its top edge (each lifts about 12 kg at the start), onto the padded glass rest; then both carry it upright (about 25 kg each) and stand it on the packers, so its hinge halves meet DL's at their height, and lower them on.",
         B="Secures the hinges as the named set requires (HOLD), slides the packers out, then swings the door slowly to 90 degrees and back, checking the 7 mm running gap over the threshold. The hinges hold the door at its closed position; there is no lock (D-83).",
         check="The door hangs before DT goes on: DT's underside is only 4 mm above the door top (PM ruling). Door swings freely, no rub.",
         ops=[op("lay the setting packers", 1, TIME["t_packer_s"].value, 1, "t_packer_s"),
              op("tilt the door up onto the glass rest", 2, TIME["t_tilt_s"].value, 1, "t_tilt_s"),
              carry("2-02"), op("hang the door and adjust", 2, lay("t_door_prehung_min") * 60, 1, "t_door_prehung_min"),
              op("slide the setting packers out", 1, TIME["t_packer_s"].value, 1, "t_packer_s")],
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
    dict(n=14, title="Air parts in DR: the intake riser with its supply fan box", tags=["2-17"],
         A="Before the wall linings (DR's inner face can't come off past R1's and R2's cassettes), lifts DR's removable inner face off; with B, slides in the intake riser, its supply fan box (2 fans) joined at its top in the factory, down to its foot over the mesh space (D-87).",
         B="Mates the fan box's plug-in connector; refits the inner face.",
         check="Riser foot sits over the opening; fan box connector latched; inner face back on all round.",
         ops=[op("DR inner face off and on", 1, TIME["t_face_s"].value, 2, "t_face_s"),
              carry("2-17"), op("slide the riser and fan box in", 2, TIME["t_slide_long_s"].value, 1, "t_slide_long_s"),
              op("plug the fan box", 1, lay("t_connector_s"), 1, "t_connector_s")],
         joints={}),
    dict(n=15, title="Wall linings: 8 cassettes", tags=["1-13", "1-14", "1-15", "1-16", "1-17", "1-18", "1-19", "1-20"],
         A="Hangs R1's and R2's cassettes first (the air column needs them), then L1, L2, B1 to B4, each on its clips. DR's inner face is already back on: it can't come off past R1's and R2's cassettes (the PM's ruling).",
         B="Hands each cassette up felt-out and lines it up with the hook-and-loop; checks each clip has locked.",
         check="Every bolt in its bay was driven before the bay is closed. Each cassette floats: it touches nothing but its clips.",
         ops=[*[carry(t) for t in ["1-13", "1-14", "1-15", "1-16", "1-17", "1-18", "1-19", "1-20"]],
              op("hang one cassette on its clips", 1, lay("t_leaf_s"), 8, "t_leaf_s")],
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
         A="With B, both on step stools, lifts the soffit (2.3 m), its exhaust fan box already fitted at the right end (D-87), and hangs it on its 4 hanger studs, set in the ceiling frame at the factory, the fan box under C2's roof slot.",
         B="Drives the soffit's 2 captive lock screws with the 5 mm key (J-AIR-01); with A, lifts the exhaust cartridge in through the open underside; plugs the fan box; closes the hinged underside.",
         check="Soffit underside at Z 2120, level; the fan box's top gasket square under the roof slot; the door still clears.",
         ops=[carry("2-10"), op("hang the soffit on its hanger studs", 2, TIME["t_hook_s"].value, 1, "t_hook_s"),
              carry("2-19"), op("lift the cartridge in", 2, lay("t_place_overhead_s"), 1, "t_place_overhead_s"),
              op("plug the fan box", 1, lay("t_connector_s"), 1, "t_connector_s"),
              op("close the hinged underside", 1, TIME["t_face_s"].value, 1, "t_face_s")],
         joints={"J-AIR-01": 2}),
    dict(n=18, title="Roof sleeve and grille", tags=[],
         parts="the roof sleeve 611601 and the roof grille 611602 with its 4 bolts and washers in their bag, which came off C2 (1-12) at unpacking",
         A="From a step stool outside the front right corner, drops the roof sleeve down through C2's roof slot onto the soft gasket on the exhaust fan box's top, its flange on the roof (#263); then lays the roof grille on over it and drives its 4 bolts, each with its washer, into the rivnuts in the sleeve's flange with the 5 mm key, snug (J-AIR-03).",
         B="Inside, opens the soffit's hinged underside and checks from below that the sleeve sits square on its gasket all round; closes the underside.",
         check="Sleeve square on its gasket all round; grille flat on the flange, its 4 bolts snug; no light through the slot with the pod lit.",
         ops=[op("drop the roof sleeve onto its gasket", 1, TIME["t_sleeve_s"].value, 1, "t_sleeve_s"),
              op("lay the grille on and start its bolts", 1, TIME["t_grille_set_s"].value, 1, "t_grille_set_s"),
              op("soffit underside open and closed, to check the sleeve", 1, TIME["t_face_s"].value, 2, "t_face_s")],
         joints={"J-AIR-03": 4}),
    dict(n=19, title="Ceiling linings: 2 cassettes", tags=["2-20", "2-21"],
         A="With B, lifts each ceiling cassette from below, fill side up, onto its clips behind the soffit.",
         B="Hooks the 2 safety catches of each cassette before A lets go.",
         check="Both catches on each cassette; front edges 3 mm behind the soffit.",
         ops=[carry("2-20"), carry("2-21"), op("lift each cassette onto its clips", 2, lay("t_place_overhead_s"), 2, "t_place_overhead_s"),
              op("hook a safety catch", 1, TIME["t_catch_s"].value, 4, "t_catch_s")],
         joints={}),
    dict(n=20, title="Light shelf", tags=["2-14"],
         A="Fits the light shelf along the tops of the side and back walls: the back shelf, the two side shelves, and the down-light channel with its diffuser on the right wall (INTERIOR 810201).",
         B="Plugs the light shelf feed.",
         check="Shelves straight; no cable shows.",
         ops=[carry("2-14"), op("fit and plug the light shelf", 1, TIME["t_light_shelf_s"].value, 1, "t_light_shelf_s")],
         joints={}),
    dict(n=21, title="Power on and self-test: fans run", tags=[],
         A="A qualified electrician connects the mains inlet (220 V for the prototype, REQ-SCP-02) and switches on.",
         B="Presses the hub's self-test button: both fan pairs, the lights and the sensors run, and it shows pass or fail (D-87). Then checks air out at the kick grille and into the soffit grille, and the CO2 reading.",
         check="Self-test passes and the fans run on both paths. The clock stops after the final check, the next step (REQ-ASM-01: closed, powered, fans running).",
         ops=[op("power on and self-test", 2, TIME["t_selftest_s"].value, 1, "t_selftest_s")],
         joints={}),
    dict(n=22, title="Final check and film", tags=[],
         A="Checks the door: swing to 90 degrees, no rub, closes onto DT's magnetic catch 368007 with the magnetic seal pair meeting on the glass edges (D-83), drop seal down on the threshold land when closed.",
         B="Checks the seals with the pod lit and the room dark: no light at any seam. Pulls each of the 15 film panels off by its quick-release tab (the 8 wall skins, the 3 decor blocks, both faces of both glass panes; D-87); cleans.",
         check="Every check in the final check list is ticked.",
         ops=[op("check door, seals and fans; clean", 2, lay("t_final_min") * 60, 1, "t_final_min"),
              op("pull one film panel by its tab", 1, TIME["t_peel_tab_s"].value, int(MINE["film_faces"].value), "t_peel_tab_s")],
         joints={}),
    dict(n=23, title="Work-wall ledge and screen rail", tags=["2-16"],
         A="Holds the 1000 mm ledge on the right (work) wall's lower panel R1, on its 2 brackets.",
         B="Fixes the ledge's brackets to R1's stiles and the screen rail to R2's stiles (INTERIOR 810101 and 818102, D-70).",
         check="Ledge level and firm.",
         ops=[carry("2-16"), op("hold the ledge", 2, TIME["t_ledge_two_s"].value, 1, "t_ledge_two_s"),
              op("fix the ledge and the screen rail", 1, TIME["t_ledge_one_s"].value, 1, "t_ledge_one_s")],
         joints={}),
]
CLOCK_LAST_STEP = 22     # REQ-ASM-01 clock: steps 1 to 22; step 23 is fit-out after it (PROPOSED)

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
        nm = re.match(r"\**\s*(\d+)", cells[1])   # the leading count: "16", "2 (the lock screws; ...)", "0 on site (...)"
        if jm and nm:
            sm = re.search(r"M6\s*[×x]\s*(\d+)", cells[2])   # the site bolt's size is the first one the row names
            size = "M6 x %s" % (sm.group(1) if sm else "16")
            rows[jm.group(1)] = (int(nm.group(1)), size)
        elif "Total" in cells[0]:
            total = int(re.sub(r"\D", "", cells[1]))
    return rows, total


# ------------------------------------------------------------------------------------------- part numbers
def read_bom(path=MASTER_BOM):
    """The master BOM's numbered rows: ({number: (name, Vietnamese name)}, {name: {numbers}})."""
    by_pn, by_name = {}, {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            pn = (r.get("part_number") or "").strip()
            if not re.fullmatch(r"\d{6}", pn):
                continue
            name = (r.get("name") or "").strip()
            by_pn.setdefault(pn, (name, (r.get("name_vi") or "").strip()))
            by_name.setdefault(name, set()).add(pn)
    return by_pn, by_name


def number_pieces(pieces, bom):
    """A piece marked "TBD (owner)" takes the master BOM's number for its exact name, and a numbered piece takes
    the BOM's Vietnamese name, so the labels carry the owner's words. Starts from what each piece was declared
    with, so it can run again. Returns the labels numbered from the BOM by name."""
    by_pn, by_name = bom
    filled = []
    for p in pieces:
        p.pn, p.vi = p.pn_declared, p.vi_declared
        if p.kind != "piece":
            continue
        if p.pn.startswith("TBD") and len(by_name.get(p.name, ())) == 1:
            p.pn = next(iter(by_name[p.name]))
            filled.append(p.tag)
        if p.pn in by_pn and by_pn[p.pn][0] == p.name and by_pn[p.pn][1]:
            p.vi = by_pn[p.pn][1]
    return filled


# ------------------------------------------------------------------------------------------- CAD sizes (check K14)
BASE_STEP = "base/110000_P01_BASE_STEP.step"
CEIL_STEP = "ceiling/410000_P01_CEILING_STEP.step"
INT_STEP = "interior/810000_P01_INTERIOR_STEP.step"
DR_STEP = "front/350003_P01_*_STEP.step"
AIR_STEP = "air/610000_P01_AIR_STEP.step"
# Each piece's own CAD as it ships, for check K14: its planned size must hold its CAD box. step: the STEP under
# v2/03-Manufacturing (a pattern); sub: the sub-assembly at the top of that STEP's tree, by part number (occ: which
# occurrence, when the STEP holds two); drop: part numbers, or a word of the name, that don't ship in this piece, with
# the reason; keep: only these part numbers; plus: CAD fitted to it from another STEP; same_as: a mirror with no CAD of
# its own; parts: a bundle or carton, each part of which must fit inside it. A piece with no entry has no CAD yet.
CAD = {
    "1-01": dict(step=BASE_STEP, sub="110401"),
    "1-02": dict(same_as="1-01", why="F2 is F1's mirror (BASE parts list)"),
    "1-03": dict(step="wall/210201_P01_*_STEP.step"),
    "1-04": dict(step="wall/210202_P01_*_STEP.step", plus=[dict(step="electrical/710000_P01_ELECTRICAL_STEP.step", sub="710001")]),
    "1-05": dict(step="wall/210101_P01_*_STEP.step"), "1-06": dict(step="wall/210102_P01_*_STEP.step"),
    "1-09": dict(step="wall/210103_P01_*_STEP.step"), "1-10": dict(step="wall/210104_P01_*_STEP.step"),
    "1-11": dict(step=CEIL_STEP, sub="410101"),
    "1-12": dict(step=CEIL_STEP, sub="410102", plus=[dict(step=AIR_STEP, sub="611601"), dict(step=AIR_STEP, sub="611602")]),
    "1-13": dict(step="wall/510102_P01_*_STEP.step"), "1-14": dict(step="wall/510104_P01_*_STEP.step"),
    "1-15": dict(step="wall/510101_P01_*_STEP.step"), "1-16": dict(step="wall/510103_P01_*_STEP.step"),
    "1-17": dict(step="wall/510201_P01_*_STEP.step"), "1-18": dict(step="wall/510202_P01_*_STEP.step"),
    "2-01": dict(step="front/360002_P01_*_STEP.step",
                 drop={"368004": "the U-profile channels ship on the sill, in DR and in DT (D-68, PM ruling)",
                       "368002": "the U-seals ship in those channels"}),
    "2-02": dict(step="front/360001_P01_*_STEP.step",
                 drop={"368101": "the hinges: their halves that sit in DL ship in DL (PM ruling); FRONT's hinge is one HOLD envelope",
                       "368008": "the kick strip's end brush ships in the door's kit bag and is fitted on site (PM ruling 2026-11-01, D-150 changed)"}),
    "2-03": dict(step=DR_STEP, drop={"RESERVED AIR SPACE": "AIR's parts ship on their own (D-59)"}),
    "2-04": dict(step=BASE_STEP, sub="110103",
                 drop={"111211": "D-129: the side bands carry the back-corner keys", "838001": "the keys' hook studs (D-129)",
                       "838010": "the keys' fixing screws (D-129)"}),
    "2-05": dict(step=BASE_STEP, sub="110101"),
    "2-06": dict(same_as="2-05", why="RH is LH's mirror (BASE parts list)"),
    "2-09": dict(step="front/350001_P01_*_STEP.step"),
    "2-12": dict(step="front/350002_P01_*_STEP.step"),
    "2-14": dict(parts=[dict(step=INT_STEP, sub="810201")]),
    "2-16": dict(parts=[dict(step=INT_STEP, sub="810101"), dict(step=INT_STEP, sub="818102")]),
    "2-10": dict(step=AIR_STEP, sub="610201", drop={"610301": "the exhaust cartridge ships on its own (2-19)"}),
    "2-11": dict(step=AIR_STEP, sub="610101", drop={"610301": "the supply cartridge ships on its own (2-18)"}),
    "2-17": dict(step=AIR_STEP, sub="610401"),
    "2-18": dict(step=AIR_STEP, sub="610101", keep={"610301"}),
    "2-19": dict(step=AIR_STEP, sub="610201", keep={"610301"}),
    "2-20": dict(step=CEIL_STEP, sub="510301", occ=1), "2-21": dict(step=CEIL_STEP, sub="510301", occ=2),
}
_STEP_CACHE = {}


def step_solids(pattern):
    """Every solid in the one STEP under v2/03-Manufacturing that matches pattern: its box in pod mm, part number, name
    and its path in the tree. Read with the mechanical checks' own reader."""
    hits = sorted(MANUF.glob(pattern))
    if len(hits) != 1:
        raise FileNotFoundError(f"{len(hits)} STEP files match v2/03-Manufacturing/{pattern}")
    if hits[0] not in _STEP_CACHE:
        if str(STEP_READER) not in sys.path:
            sys.path.insert(0, str(STEP_READER))
        from stepfile import StepFile, world_box
        sf = StepFile(str(hits[0]))
        out = []
        for inst in sf.instances():
            b = world_box(sf.solid(inst["solid"]), inst["frame"])
            if b:
                out.append(dict(box=b, pn=inst["part_number"], name=inst["name"], path=inst["path"]))
        _STEP_CACHE[hits[0]] = (hits[0], out)
    return _STEP_CACHE[hits[0]]


def cad_solids(spec):
    """The solids one CAD entry picks, with the files they came from."""
    path, solids = step_solids(spec["step"])
    out, files = [], {path}
    for sl in solids:
        top = sl["path"][1] if len(sl["path"]) > 1 else ""
        if spec.get("sub") and not (top.split(" ")[0] == spec["sub"] or sl["pn"] == spec["sub"]):
            continue
        if spec.get("occ") and not top.endswith(":%d" % spec["occ"]):
            continue
        base = sl["pn"].split("_")[0]
        if spec.get("keep") and base not in spec["keep"]:
            continue
        if any(base == d or d in sl["name"] for d in spec.get("drop", {})):
            continue
        out.append(sl)
    for extra in spec.get("plus", ()):
        more, mf = cad_solids(extra)
        out += more
        files |= mf
    return out, files


def box_dims(solids):
    lo = [min(sl["box"][k] for sl in solids) for k in range(3)]
    hi = [max(sl["box"][k + 3] for sl in solids) for k in range(3)]
    return tuple(sorted((hi[k] - lo[k] for k in range(3)), reverse=True))


def cad_size(tag):
    """(kind, dims or parts, files): kind is "box" (the piece's CAD box, sizes sorted), "parts" (each part's own box, for
    a bundle or carton) or None (no CAD yet)."""
    spec = CAD.get(tag)
    if spec and spec.get("same_as"):
        spec = CAD[spec["same_as"]]
    if not spec:
        return None, None, set()
    if spec.get("parts"):
        parts, files = [], set()
        for sub in spec["parts"]:
            solids, f = cad_solids(sub)
            files |= f
            # each solid on its own: the bundle's parts are one solid each (two brackets share one path in the tree)
            parts += [(sl["pn"].split("_")[0], box_dims([sl])) for sl in solids]
        return "parts", parts, files
    solids, files = cad_solids(spec)
    if not solids:
        raise ValueError(f"{tag}: its CAD entry picks no solid from {spec['step']}")
    return "box", box_dims(solids), files


# ------------------------------------------------------------------------------------------- getting it in (K15)
def tilt_in(L, t, D, H, dh, step=5.0):
    """A piece L long and t thick in the car's depth-height plane, leaned into a car D deep and H tall through a door dh
    high: its lower back corner slides along the floor to the door while its front end stays inside the car, at the
    flattest angle that allows. False if it would hit the car's ceiling or the door head before it is wholly inside."""
    b = -L
    while True:
        c = (D - b) / L
        phi = 0.0 if c >= 1 else math.acos(max(-1.0, c))
        if L * math.sin(phi) + t * math.cos(phi) > H:
            return False
        if b >= t * math.sin(phi):
            return True
        if math.cos(phi) < 1e-9 or -b * math.tan(phi) + t / math.cos(phi) > dh:
            return False
        b += step


def goes_in(dims, car, door):
    """Some face of the piece goes across the door (with room for hands) and it leans in (tilt_in)."""
    cw, cd, ch = car
    dw, dh = door
    gap = 2 * MINE["hand_gap"].value
    return any(across + gap <= dw and across + gap <= cw and tilt_in(L, t, cd, ch, dh)
               for across, t, L in itertools.permutations(dims))


def moving_size(p):
    """A piece as it is carried: in its wrap, a carton as it is, a pane on its suction lifters."""
    a, b, c = p.dims
    if p.glass:
        return (a, b, c + MINE["lifter"].value)
    w = 0.0 if p.carton else MINE["wrap"].value
    return (a + 2 * w, b + 2 * w, c + 2 * w)


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
    def __init__(self, joints_path=None, bom_path=None):
        self.roll = read_rollup()
        self.bom_path = Path(bom_path) if bom_path else MASTER_BOM
        self.bom = read_bom(self.bom_path) if self.bom_path.exists() else ({}, {})
        self.filled = number_pieces(PIECES, self.bom)
        self.tbd_left = {}
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
        """Pallet 2's tiers: each part's along, across and up sizes as it lies, with its wrap a side (none on a carton,
        which is its own outer box) and what lies under it; lane widths and tier heights follow from them."""
        out, z = [], lay("pal_long_h")
        cr = self.crate()
        deck_l, deck_w = MINE["pal_long_l_exact"].value, MINE["pal_std_l_exact"].value
        for i, tier in enumerate(TIERS2):
            lanes = []
            if tier.get("crate"):
                h = cr["outside_h"]
                lanes.append(dict(width=MINE["crate_w"].value, items=[dict(tag="CRATE", along=MINE["crate_l"].value,
                                                                             across=MINE["crate_w"].value, up=h)],
                                  length=MINE["crate_l"].value, lie="flat", ok=MINE["crate_l"].value <= deck_l))
            else:
                h = 0.0
                for ln in tier["lanes"]:
                    items = []
                    bed = MINE[ln["bed"]].value if ln.get("bed") else 0.0
                    for t in ln["tags"]:
                        p = PIECE[t]
                        a, b, c = p.dims
                        w = 0.0 if p.carton else MINE["wrap"].value
                        across, up = (c, b) if ln["lie"] == "edge" else (b, c)
                        items.append(dict(tag=t, along=a + 2 * w, across=across + 2 * w, up=up + 2 * w + bed, wrap=w, bed=bed))
                    width = max(it["across"] for it in items)
                    length = sum(it["along"] for it in items)
                    h = max([h] + [it["up"] for it in items])
                    lanes.append(dict(width=width, items=items, length=length, lie=ln["lie"], ok=length <= deck_l))
            width = sum(ln["width"] for ln in lanes)
            out.append(dict(name=tier["name"], z0=z, h=h, lanes=lanes, width=width,
                            ok=all(ln["ok"] for ln in lanes) and width <= deck_w))
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
        on_pallet = {t for t in STACK1} | {t for tr in TIERS2 for ln in tr.get("lanes", []) for t in ln["tags"]} | set(CRATE_TAGS)
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
        self.check_numbers()
        self.check_cad_sizes()
        self.check_delivery()

    def check_delivery(self):
        """K15: every piece goes into the install sheet's elevator, leaned in through its door; the glass out of its crate."""
        car = (MINE["lift_car_w"].value, MINE["lift_car_d"].value, MINE["lift_car_h"].value)
        door = (MINE["lift_door_w"].value, MINE["lift_door_h"].value)
        typ_car = (MINE["lift_car_w"].value, MINE["lift_car_d"].value, MINE["typ_car_h"].value)
        typ_door = (MINE["typ_door_w"].value, MINE["lift_door_h"].value)
        self.no_lift = [p.tag for p in self.shipped() if not goes_in(moving_size(p), car, door)]
        self.no_typical = [p.tag for p in self.shipped() if not goes_in(moving_size(p), typ_car, typ_door)]
        cr = self.crate()
        crate = (MINE["crate_l"].value, MINE["crate_w"].value, cr["outside_h"])
        self.crate_in = goes_in(crate, car, door)
        self.check("K15", "Every piece goes into the install sheet's elevator, leaned in through its door (the glass out of its crate)",
                   f"car {car[0]:g} x {car[1]:g} x {car[2]:g} mm inside, door {door[0]:g} x {door[1]:g}: not in: "
                   f"{self.no_lift or 'none'}; a typical car with a {typ_door[0]:g} mm door: not in: {self.no_typical or 'none'}; "
                   f"the crate itself: {'goes in' if self.crate_in else 'opened at the entrance'}", not self.no_lift)

    def check_cad_sizes(self):
        """K14: every piece's planned size holds its own CAD box, as it ships (a bundle or carton: each of its parts)."""
        tol = MINE["cad_tol"].value
        self.cad, over, none, errors = {}, [], [], []
        for p in self.shipped():
            try:
                kind, got, files = cad_size(p.tag)
            except (FileNotFoundError, ValueError) as e:
                errors.append(f"{p.tag}: {e}")
                continue
            self.cad[p.tag] = (kind, got, files)
            if kind is None:
                none.append(p.tag)
            elif kind == "box":
                if any(c > d + tol for c, d in zip(got, p.dims)):
                    over.append(f"{p.tag} CAD {dims_txt(got)} over planned {dims_txt(p.dims)}")
            else:
                for pn, d in got:
                    if any(c > e + tol for c, e in zip(d, p.dims)):
                        over.append(f"{p.tag} part {pn} {dims_txt(d)} over planned {dims_txt(p.dims)}")
        checked = len(self.cad) - len(none)
        self.check("K14", "Every piece's planned size holds its own CAD, as it ships",
                   f"{checked} pieces checked against {len({f for v in self.cad.values() for f in v[2]})} STEP files; "
                   f"no CAD yet: {len(none)} ({', '.join(none) or 'none'}); over: {over or 'none'}; unreadable: {errors or 'none'}",
                   not over and not errors)

    def check_numbers(self):
        """K13: every number on a label is the master BOM's number for that name; a TBD piece whose exact name the
        BOM numbers has been filled in (number_pieces), so only an owner's list still to come leaves it TBD."""
        by_pn, by_name = self.bom
        if not by_pn:
            self.check("K13", "Every part number on a label is the master BOM's", f"{self.bom_path.name} not found or empty", False)
            return
        ships = self.shipped()
        numbered = [p for p in ships if re.fullmatch(r"\d{6}", p.pn)]
        other = [f"{p.tag} {p.name} is {by_pn[p.pn][0]!r} in the BOM" for p in numbered if p.pn in by_pn and by_pn[p.pn][0] != p.name]
        unknown = [f"{p.tag} {p.pn}" for p in numbered if p.pn not in by_pn and p.pn not in NOT_BOM_ROWS]
        two = [f"{p.tag} {sorted(by_name[p.name])}" for p in ships if p.pn.startswith("TBD") and len(by_name.get(p.name, ())) > 1]
        loose = [p.tag for p in ships if not (re.fullmatch(r"\d{6}", p.pn) or re.fullmatch(r"TBD \([A-Z]+\)", p.pn))]
        left = {}
        for p in ships:
            if p.pn.startswith("TBD"):
                owner = p.pn[5:-1]
                left[owner] = left.get(owner, 0) + 1
        self.tbd_left = left
        self.check("K13", "Every part number on a label is the master BOM's number for that name",
                   f"{len(numbered)} of {len(ships)} pieces numbered, {len(self.filled)} of them from the BOM by name "
                   f"({', '.join(self.filled) or 'none'}); still TBD: "
                   f"{', '.join(f'{o} {n}' for o, n in sorted(left.items())) or 'none'}; named otherwise in the BOM: {other or 'none'}; "
                   f"not in the BOM: {unknown or 'none'}; two numbers for one name: {two or 'none'}; neither a number nor TBD: {loose or 'none'}",
                   not (other or unknown or two or loose))

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
    T["N_STEPS"] = str(len(STEPS))
    T["ROOM_H_GUIDE"] = f"{sk('pod_h') + max(MINE['roof_work'].value, MINE['spigot_lift'].value):g}"
    T["STEP_POWER"] = str(next(s["n"] for s in STEPS if s["title"].startswith("Power on")))
    T["STEP_FINAL"] = str(next(s["n"] for s in STEPS if s["title"].startswith("Final check")))
    T["STEP_LEDGE"] = str(next(s["n"] for s in STEPS if s["title"].startswith("Work-wall ledge")))
    T["WRAP"] = f"{MINE['wrap'].value:g}"
    T["DR_BED"] = f"{MINE['dr_bed'].value:g}"
    none = [p for p in m.shipped() if m.cad.get(p.tag, (None,))[0] is None]
    T["CAD_NONE"] = ", ".join(f"{p.tag} ({p.name.split(' - ', 1)[1].lower()})" for p in none) or "none"
    cad_rows = []
    for p in m.shipped():
        kind, got, files = m.cad.get(p.tag, (None, None, set()))
        same = (CAD.get(p.tag) or {}).get("same_as")
        if kind == "box":
            cad_txt = dims_txt(got) + (f" (as {same}: {CAD[p.tag]['why']})" if same else "")
        elif kind == "parts":
            cad_txt = "; ".join(f"{pn} {dims_txt(d)}" for pn, d in got)
        else:
            cad_txt = "no CAD yet"
        cad_rows.append([f"**{p.tag}**", p.name, dims_txt(p.dims), cad_txt,
                         ", ".join(sorted(f"`{f.name}`" for f in files)) or "-"])
    T["CAD_TABLE"] = md_table(["Label", "Piece", "Planned mm", "CAD mm, as it ships", "STEP"], cad_rows)
    T["TBD_LEFT"] = (f"{sum(m.tbd_left.values())} of {len(m.shipped())} pieces: "
                     + ", ".join(f"{o} {n}" for o, n in sorted(m.tbd_left.items()))) if m.tbd_left else "none"
    T["TBD_OWNERS"] = ", ".join(sorted(m.tbd_left)) or "-"
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
    T["TIERS_TABLE"] = md_table(["Tier", "Lane mm", "Label", "Piece", "kg", "Along × across × up with its wrap and bed, mm", "Fitted in step"], r2,
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
        parts = ", ".join(f"**{t}** {ux(PIECE[t].name)} ({PIECE[t].kg:.1f} kg)" for t in st["tags"]) or st.get("parts") or "none"
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
            + (f"- **Caution:** {st['caution']}\n" if st.get("caution") else "")
            + f"- **Check before the next step:** {st['check']}\n")
        srow.append([st["n"], st["title"], len(st["tags"]), tr["bolts"], tr["other"], f"{tr['two'] / 60:.1f}", f"{tr['one'] / 60:.1f}",
                     f"**{tr['elapsed'] / 60:.1f}**" + ("" if st["n"] <= CLOCK_LAST_STEP else " (after)")])
    G["STEPS"] = "\n".join(steps_md)
    G["AIR_MIN"] = f0(sum(tr["elapsed"] for st, tr in zip(STEPS, m.steps)
                          if any(PIECE[t].group == "AIR" for t in st["tags"]) or st["title"].startswith("Roof sleeve")) / 60)
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
    tiers, _h = m.tiers2()
    for tr in tiers:
        for ln in tr["lanes"]:
            for it in ln["items"]:
                if it["tag"] != "CRATE":
                    place[it["tag"]] = (f"pallet 2, {tr['name'].split(':')[0].lower()}, lane {ln['width']:.0f} mm, "
                                        + ("on edge" if ln["lie"] == "edge" else "flat"))
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


def install_tables(m, T):
    """The install sheet's numbers (IF-17): room height, floor, power, air, getting the pallets in."""
    I = dict(T)
    pod_h = sk("pod_h")
    I["POD_W"], I["POD_D"], I["POD_H"] = f"{sk('pod_w'):g}", f"{sk('pod_d'):g}", f"{pod_h:g}"
    I["ROOF_WORK"] = f"{MINE['roof_work'].value:g}"
    I["SPIGOT_LIFT"] = f"{MINE['spigot_lift'].value:g}"
    I["H_SPIGOTS"] = f"{pod_h + MINE['spigot_lift'].value:g}"
    I["ROOM_H"] = f"{pod_h + max(MINE['roof_work'].value, MINE['spigot_lift'].value):g}"
    I["GLIDE_MIN"], I["GLIDE_MAX"] = f"{MINE['glide_min'].value:g}", f"{MINE['glide_max'].value:g}"
    I["FLOOR_PV"] = f"{MINE['glide_max'].value - MINE['glide_min'].value:g}"
    I["LAY_OUT"] = f"{MINE['lay_out'].value / 1000:g}"
    I["LAY_W"] = f"{sk('pod_w') + 2 * MINE['lay_out'].value:g}"
    I["LAY_D"] = f"{sk('pod_d') + 2 * MINE['lay_out'].value:g}"
    with open(REPO / "v2/05-Engineering/electrical/710000_P01_ELECTRICAL-LOAD-TABLE_CALC.csv", encoding="utf-8") as f:
        loads = [r for r in csv.DictReader(f) if r["id"].startswith("LD")]
    I["LOAD_W"] = f"{sum(float(r['w_total_max'] or 0) for r in loads):.0f}"
    try:
        sleeve = box_of(cad_solids(dict(step=AIR_STEP, sub="611601"))[0])
        I["SLOT"] = f"X {sleeve[0]:.0f} to {sleeve[3]:.0f}, Y {sleeve[1]:.0f} to {sleeve[4]:.0f} (AIR 610000 P01 STEP, the roof sleeve)"
    except (FileNotFoundError, ValueError):
        I["SLOT"] = "behind DR, near the front right corner (AIR's CAD not found)"
    for k in ("lift_door_w", "lift_door_h", "lift_car_w", "lift_car_d", "lift_car_h", "typ_door_w"):
        I[k.upper()] = f"{MINE[k].value:g}"
        I[k.upper() + "_IN"] = f"{MINE[k].value / 25.4:.0f}"
    I["NOT_TYPICAL"] = (", ".join(f"{PIECE[t].pos if PIECE[t].pos != '-' else PIECE[t].name} ({t}, "
                                  f"{' × '.join(f'{v:g}' for v in moving_size(PIECE[t]))} mm as carried)" for t in m.no_typical) or "nothing")
    I["DR_FACE"] = f"{moving_size(PIECE['2-03'])[1]:g}"
    longest = max(m.shipped(), key=lambda p: p.dims[0])
    I["LONGEST"] = f"{longest.name} ({longest.tag}), {longest.dims[0]:g} mm"
    return I


def box_of(solids):
    """The box of some solids in pod mm: (x0, y0, z0, x1, y1, z1)."""
    return (tuple(min(sl["box"][k] for sl in solids) for k in range(3))
            + tuple(max(sl["box"][k + 3] for sl in solids) for k in range(3)))


def outputs(m):
    T = gen_tables(m)
    G = guide_tables(m, T)
    return {
        OUT_INSTALL: fill(TPL_INSTALL.read_text(encoding="utf-8"), install_tables(m, T)),
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
