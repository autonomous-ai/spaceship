"""WALL's parts that drawgen draws (D-139: each team keeps its own entries here, in its own PRs; tools/drawgen's
owner reviews the code and a team's first entries). See tools/drawgen/teams/README.md for what an entry holds."""

# WALL side frames: they sit on two spigots (round hole + slot) in the bottom rail; the joints register positions
# every bolt hole from the round one (R-J6, R-J13), so that hole is datum B.
WALL_FRAME = {
    "datums": "spigot",
    "notes": ["MEMBER JOINTS: INTERNAL CLEATS, CRIMPED AND BONDED (D-115); cleat part numbers per the joints "
              "register. No welds."],
    "tolerance": "hole and slot positions Ø0.4 to A|B|C (R-J6); spigot hole and slot ±0.1 from the frame ends "
                 "(joints register section 4); rivnut holes Ø9.53 +0.10/0 (maker); other hole sizes +0.2/0 "
                 "(assumption); cut lengths ±0.5, square ends (parts list); joined frame: overall sizes ±0.5, "
                 "diagonals within 1.0, bond face flat within 1.0 (assumption).",
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
