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
    inner = "+X" if hand == "LH" else "-X"
    return {"bent": {"vgroove": SKIN_GROOVE}, "notes": SKIN_NOTES, "tolerance": SKIN_TOLERANCE,
            "corner": out + "-Y-Z", "datum_faces": {"A": "-Z", "B": "-Y", "C": inner},
            "datum_words": {"A": "bottom edge (flush with the frame's bottom)",
                            "B": "front edge (2.26 seam to the decor block)",
                            "C": "back face (bonded to the frame through the 3 mm line)"}}


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


PARTS = {
    "511101": _tray("LH"),
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
