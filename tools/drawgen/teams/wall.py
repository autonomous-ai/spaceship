"""WALL's parts that drawgen draws (D-139: each team keeps its own entries here, in its own PRs; tools/drawgen's
owner reviews the code and a team's first entries). See tools/drawgen/teams/README.md for what an entry holds."""

# WALL side frames: they sit on two spigots (round hole + slot) in the bottom rail; the joints register positions
# every bolt hole from the round one (R-J6, R-J13), so that hole is datum B. D-131: welded, galvanized steel; the
# notes are J-FRAME-01's (joints register 3.17), and the entry refuses a parts list that still says aluminium.
WALL_FRAME = {
    "datums": "spigot",
    "material_has": "steel", "material_why": "D-131's welded, galvanized steel frame",
    "notes": [
        "FRAME: welded, galvanized steel box tube (D-131, J-FRAME-01). Corners mitred, with a 2.0 mm mitre plate "
        "welded into each mitre (831007 to 831009, placed as the joints CAD README gives). Every corner and T joint "
        "welded all round, continuously, so each tube stays sealed. MIG brazing with CuSi3 wire (ISO 24373 S Cu 6560) "
        "under argon preferred; or short-arc MAG with G3Si1 wire (ISO 14341-A) if the factory's welding procedure "
        "passes J-T7's coupons (HOLD-22).",
        "Weld in a jig that holds every member flat and square on its skin side: diagonally opposite corners in "
        "turn, then the T joints from the middle out, alternating sides; the frame cools in the jig. Beads on the "
        "skin-side faces and the seam faces ground flush (0 to 0.2 proud, never more than 0.3 below the face).",
        "Pre-galvanized tube, zinc Z100: no hot-dip galvanizing after welding, so no vent or drain holes. Every "
        "burnt zone wire-brushed and coated with a 2-component zinc-rich epoxy (about 40 µm dry; assumption).",
        "Every joint hole is made after welding and the touch-up, by CNC or a drill jig that locates on the frame's "
        "joint faces and spigot hole; rivnuts 838003 (zinc-plated steel) are set after the touch-up.",
    ],
    "tolerance": "hole and slot positions Ø0.4 to A|B|C (R-J6); spigot hole and slot ±0.1 from the frame ends "
                 "(joints register section 4); rivnut holes Ø9.53 +0.10/0 (maker); other hole sizes +0.2/0 "
                 "(assumption); cut lengths ±0.5 (parts list); welded frame: seam faces flat within 0.5, skin-side "
                 "faces within ±0.5 of one plane lying free, diagonals equal within 1.5, measured on a flat table "
                 "after welding, before the holes; straighten cold or reject, never clamp flat (J-FRAME-01).",
}

PARTS = {
    "211101": WALL_FRAME,
    "211102": WALL_FRAME,
}

_FILL = ("D-128: a fill piece with through-notches only goes on its own DXF with a full parts-list row (WALL's D-123 "
         "piece split), so no drawing; D-123 cancels this set number")
NO_DRAWING = {
    "211501": _FILL, "211502": _FILL, "211503": _FILL, "211504": _FILL, "211601": _FILL, "211602": _FILL,
}

# Assembly sheets (tools/drawgen/assembly.py): the lining cassettes. WALL's STEP models the four held cassette clips
# as one shape without a number, 'NO-PN-HOLD-H03 HOLD - CASSETTE CLIP ZONES (H03, NO PART NAMED)': each of its four
# bodies is one clip 518001 (the list's 4), drawn and ballooned as that part until it is named (HOLD-08).
# Datums as the ceiling cassette's (CEILING's facts for 510301), which these trays match (feature rationale F20):
# A the tray's back face (toward the panel frame), B the end return's outer face (the front one on a side cassette,
# the one at the side wall on a back cassette), C the bottom return's outer face. The clip centres run across from B
# and up from C in the principal view, and the build-up (D-147 (2)) is a 1:2 section through the lowest clip, its
# faces from A, lettered D after the datums. The fitting order is the one WALL's feature rationale gives (F20, F22,
# F23) and the parts list's notes.
_ORDER = ("Fitting order (WALL's feature rationale F20, F22, F23 and the parts list): (1) the tray, its 34 mm "
          "returns turned in as 12 mm lips; (2) the felt, dropped in behind the lips, 1 mm clear inside the "
          "returns: the lips hold it with no glue (settles H09), over the 24 mm air gap (D-17); (3) the clips "
          "518001 in their four zones, 100 from the cassette's top and bottom on the panel frame's studs (HOLD "
          "H03, HOLD-08). The cassette is a floating inner leaf that clips onto the panel frame from inside (D-17, "
          "D-47). Items marked * go as their rows say: the hook-and-loop pads 848011 only line the cassette up and "
          "carry no load (D-47); the edge seal 848012 only touches across the 2.26 gap (R-J18).")


def _cassette(tray, back, end, **more):
    return dict(more, **{
        "envelopes": {"NO-PN-HOLD-H03": "518001"},
        "datums": [
            {"letter": "A", "pn": tray, "face": back, "view": "section_D",
             "words": "the tray's back face, toward the panel frame"},
            {"letter": "B", "pn": tray, "face": end, "view": "principal",
             "words": "the tray's end return, its outer face"},
            {"letter": "C", "pn": tray, "face": "-Z", "view": "principal",
             "words": "the tray's bottom return, its outer face"},
        ],
        "interfaces": [
            {"view": "principal", "of": ["518001"], "along": "x", "origin": {"pn": tray, "face": end}, "list": True,
             "words": "the clip centres across the cassette, from datum B (principal view)"},
            {"view": "principal", "of": ["518001"], "along": "y", "origin": {"pn": tray, "face": "-Z"}, "list": True,
             "words": "the clip centres up the cassette, from datum C (principal view)"},
        ],
        # 10 below the clip's centre (still through it), so its trace doesn't lie along the clip's ordinate line
        "sections": [{"letter": "D", "around": "518001", "offset": 10, "normal": [0, 0, -1], "half": 70, "scale": 0.5,
                      "slice": 10,
                      "stack": True, "stack_from": {"pn": tray, "face": back}}],
        "notes": [_ORDER],
    })


ASSEMBLIES = {
    "510101": _cassette("511101", "-X", "-Y"),      # L1: back face toward -X, front return toward -Y
    # R1 and R2 seen from the wall side too (Reviewer 9 on #350), where their clips are: the view from the right
    "510102": _cassette("511102", "+X", "-Y", principal="right", overall_sides={"y": "right"}),
    "510103": _cassette("511103", "-X", "-Y"),      # L2
    "510104": _cassette("511104", "+X", "-Y", principal="right", overall_sides={"y": "right"}),
    "510201": _cassette("511201", "+Y", "-X"),      # B1: back face toward +Y, its end at the left side wall
    # B2: its end at the right side wall, the left edge of its rear view, so the overall height goes on the right
    "510202": _cassette("511202", "+Y", "+X", overall_sides={"y": "right"}),
}
