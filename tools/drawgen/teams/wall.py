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
