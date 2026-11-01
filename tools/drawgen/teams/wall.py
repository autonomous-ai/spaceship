"""WALL's parts that drawgen draws (D-139: each team keeps its own entries here, in its own PRs; tools/drawgen's
owner reviews the code and a team's first entries). See tools/drawgen/teams/README.md for what an entry holds."""

# WALL side frames: they sit on two spigots (round hole + slot) in the bottom rail; the joints register positions
# every bolt hole from the round one (R-J6, R-J13), so that hole is datum B. D-131: welded, galvanized steel; the
# notes are J-FRAME-01's (joints register 3.17), and the entry refuses a parts list that still says aluminium.
WALL_FRAME = {
    "datums": "spigot",
    "material_has": "steel", "material_why": "D-131's welded, galvanized steel frame",
    # the bottom rail's cassette-ledge rivets (lower panels): plain Ø3.3 holes, drilled after welding, for the
    # closed-end countersunk blind rivets 838012 (ISO 15974, Ø3.2; D-166) - not M4 tap drills
    "rivet_holes": {3.3: "blind rivet 838012, closed end, countersunk, Ø3.2 (ISO 15974)"},
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
                 "(joints register section 4); rivnut holes Ø10.00 +0.10/0 (D-163, Sherex CAL2-610-4.2); other "
                 "hole sizes +0.2/0 (assumption); cut lengths ±0.5 (parts list); welded frame: seam faces flat within "
                 "0.5, skin-side "
                 "faces within ±0.5 of one plane lying free, diagonals equal within 1.5, measured on a flat table "
                 "after welding, before the holes; straighten cold or reject, never clamp flat (J-FRAME-01).",
}

# WALL side skins (D-139: drawn by drawgen as V-grooved and folded panels, #341): the 3 mm Alcorest ACP with its 46 mm
# back return folded round the frame's back end. The groove, the fold and the film rules are the maker's own:
# Nhom Viet Dung, "Huong dan thi cong tam ACP Alcorest" No. 01/2021/HDTC-VD (sections 1.1, 2.1, 2.2, 4.1, 4.4, 4.5,
# figures 4.4 and 4.5), the guide for the panel HW-SEL A1 lists (Alcorest outdoor, 3 x 0.21, PE core, PVDF).
SKIN_GROOVE = ("groove A of the Alcorest guide: a 110° V on the back face with a 2 mm flat root, leaving 0.1 to 0.5 of "
               "core on the 0.21 outer skin; fold 90°, outside radius over 2 (guide 01/2021/HDTC-VD, 4.4, 4.5)")
SKIN_NOTES = [
    "GROOVE AND FOLD (Alcorest guide 01/2021/HDTC-VD, 4.1, 4.4, 4.5, figures 4.4 and 4.5): rout the groove from the "
    "back with a carbide end mill (2 to 4 flutes, 20 000 to 30 000 rpm, 3 to 5 m/min) or a carbide disc cutter (for "
    "example 12 in, 3 000 to 5 000 rpm, 5 m/min) shaped to the 110° V with its 2 mm flat root. The root never touches "
    "the outer aluminium: 0.1 to 0.5 of core stays on it. Clamp the panel between two rigid supports and fold evenly "
    "along the whole edge; an outside radius under 2 cracks the face and voids the maker's warranty.",
    "Outside radius 2 min, per the maker's guide No. 01/2021/HDTC-VD; the first fold of each batch is a test fold "
    "that confirms the blank and the core left before the batch. The blank develops along the outer face at that "
    "radius: 0.86 less than the sum of the sharp outside lengths (the Lead's ruling, 2026-11-01).",
    "BOND (D-137, bond spec section 8): Sikaflex-252, one joint at least 12 wide x 3 on every frame member, the 3 set "
    "by fixing-tape pieces in line with the bead, and one 3 mm joint, as wide as the return allows up to 12, between "
    "the return and the frame's back end; both faces pre-treated with an abrasive pad, Sika Aktivator-205 and Sika "
    "Primer-210; laid face down on a flat table with the ACP face as datum.",
    "FILM (guide 1.1, 2.2): fit every panel with the arrows printed on its film the same way; peel the film by hand, "
    "no heat, within 45 days of the start of fitting; no marker, vinyl or tape on the coated face after that.",
    "Edges flush with the frame's top and bottom: the outside reveal is the 2.26 seam gap (D-23).",
]
SKIN_TOLERANCE = ("cut sizes ±0.5 (CNC router; assumption, guideline 6.3); the blank and the fold line as the batch's "
                  "test fold confirms them (HOLD H16); fold 90° ±1° (assumption); outside radius 2 min (Alcorest guide "
                  "4.5); colour difference between panels ΔE 2 or less (Alcorest guide 2.1).")


def _skin(hand):
    """A side skin's entry: LH skins (L1, L2) have their outer face at -X, RH skins (R1, R2) at +X."""
    out = "-X" if hand == "LH" else "+X"
    return {"bent": {"vgroove": SKIN_GROOVE}, "notes": SKIN_NOTES, "tolerance": SKIN_TOLERANCE,
            # A and B on the faces the views show edge on; no C: the skin has no holes, and its back face shows edge
            # on only in the section (the WALL Drawings Engineer's trial on #343)
            "corner": out + "-Y-Z", "datum_faces": {"A": "-Z", "B": "-Y"},
            "datum_words": {"A": "bottom edge (flush with the frame's bottom)",
                            "B": "front edge (2.26 seam to the decor block)"}}


# WALL's lining trays (D-17, D-37): 0.5 galvanized steel folded into a pan, four returns toward the room and 12 mm lips
# turned in to hold the felt; the model has its bends (1 x t), so drawgen draws from the STEP and the tray's DXF.
TRAY_NOTES = [
    "TRAY: galvanized steel sheet 0.5, DX51D+Z (EN 10346). Blank laser cut or punched from its DXF, then folded on a "
    "press brake: the four returns 90° toward the room, then the four 12 lips 90° inward; inside radius 1 x t (the "
    "model's; the factory's tooling confirms it); corner reliefs as the DXF.",
    "The floating inner leaf (D-17): no screw ever joins it to the frame. It hangs on the wall clips, which only hold, "
    "and its bottom return sits on the panel's cassette ledge and its pad (the Lead's ruling of 2026-11-01).",
    "The felt, a part of its own, is held by the lips over the 24 air gap (D-17).",
]
TRAY_TOLERANCE = ("blank sizes ±0.5; fold positions ±0.5; folds 90° ±1°; the back flat within 2 over its length "
                  "(assumption, guideline 6.3)")


def _tray(hand):
    """A side tray's entry: LH trays (L1, L2) have their back at -X, RH trays (R1, R2) at +X."""
    back = "-X" if hand == "LH" else "+X"
    # datums on the faces the principal view shows edge on (it looks at the back): B the bottom, C the front
    return {"bent": True, "notes": TRAY_NOTES, "tolerance": TRAY_TOLERANCE,
            "corner": back + "-Y-Z", "datum_faces": {"B": "-Z", "C": "-Y"},
            "datum_words": {"B": "bottom face (on the ledge's pad)",
                            "C": "front face (at the cassette's front end)"}}


# WALL's cassette ledges (D-170): a 1.5 galvanized steel angle under each lower cassette, riveted to the bottom rail's
# room face after welding with closed-end countersunk blind rivets, the heads flush in countersinks machined in the upright
LEDGE_NOTES = [
    "LEDGE (D-170): galvanized steel sheet 1.5, DX51D+Z (EN 10346), Z100. Blank laser cut from its DXF with its 6 rivet "
    "holes Ø3.3; each hole countersunk Ø6.7 x 120° by machining on the upright's room face; then folded 90° on a press "
    "brake, inside radius 1 x t (the model's; K 0.44 in the DXF, an assumption until the factory's bend table).",
    "Fitted after the frame is welded and touched up (J-FRAME-01): held on the bottom rail's room face as the drill jig "
    "for the rail's plain Ø3.3 holes, then riveted with 6 closed-end countersunk blind rivets 838012 (ISO 15974, Ø3.2 x 8; "
    "D-166), the heads flush, 0 to 0.3 under the face, so they stay clear of the cassette's tray.",
    "The pad 848015 (PORON 4701-40, 18 wide, PSA) goes on the leg's flat past its bend; the cassette's bottom return rests "
    "on it (D-170).",
]
LEDGE_TOLERANCE = ("blank ±0.5; fold 90° ±1° (assumption); rivet holes ±0.2 to each other and to the ends (assumption: "
                   "the ledge is the rail's drill jig); countersinks Ø6.7 +0.2/0 at 120° ±1°, so every head (Ø5.8 to "
                   "6.7) sits flush or under, with 0.52 of the upright left under it")
LEDGE = {"bent": True, "notes": LEDGE_NOTES, "tolerance": LEDGE_TOLERANCE,
         "rivet_holes": {3.3: "blind rivet 838012, closed end, countersunk, Ø3.2 (ISO 15974)"}}

PARTS = {
    "511101": _tray("LH"),
    "211701": LEDGE,
    "211101": WALL_FRAME,
    "211102": WALL_FRAME,
    "211301": _skin("LH"),
    "211302": _skin("RH"),
    "211303": _skin("LH"),
    "211304": _skin("RH"),
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
