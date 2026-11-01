"""FRONT's parts that drawgen draws (D-139: each team keeps its own entries here, in its own PRs; tools/drawgen's
owner reviews the code and a team's first entries). See tools/drawgen/teams/README.md for what an entry holds."""

# A decor frame's tube (D-120: each tube its own part; the frame 3513x4 is its weldment, drawn in Fusion as an
# assembly of its tubes, D-139). Its length and end cuts are its cut list row's; its holes are drilled after welding,
# located from the frame's joint faces, as J-FRAME-01 has it for the welded frames (D-131 moves FRONT's cores to it).
DECOR_TUBE = {
    "corner": "-X-Y-Z",
    "material_has": "aluminium", "material_why": "the decor frames' 6063-T6 tube until D-131's steel switch",
    "notes": [
        "Cut from 6063-T6 aluminium tube to the length and end cuts shown, as the frame's cut list row gives them "
        "(D-120); mill finish, hidden (D-79). TIG-welded into its frame in the frame's jig (its weldment drawing).",
        "Holes, where the tables show them: drilled after welding by CNC or a drill jig that locates on the frame's "
        "joint faces, at the places the frame's weldment drawing gives (as J-FRAME-01 for the welded frames); this "
        "sheet shows them on the tube for reference. Rivnuts 838003 are set after that.",
    ],
    "tolerance": "cut length +0/-0.5 and end angles ±0.25° (assumption, as the BASE and WALL cut lists); hole "
                 "positions to the frame's weldment drawing (R-J6: Ø0.4 to its datums); rivnut holes Ø9.53 +0.10/0 "
                 "(maker); other hole sizes +0.2/0 (assumption). Not ISO 2768 on the tube.",
}

# DT's 11 tube parts (#232); 352204's sheet waits for the generator: its 75.39 deg angle arc runs into the border
_DT = ["352201", "352202", "352203", "352204", "352205", "352206", "352207", "352208", "352209", "352210", "352211"]

# DR's 22 tube parts (#232, #287: F09 is 352322). 352321 (C10) is refused as an open section: the DT joint turns
# 5.5 mm before the back ring, so it is a 5.5 x 15 mm wedge of tube; FRONT's fix is with the Lead
_DR = ["3523%02d" % n for n in range(1, 23)]

# DL's 16 tube parts (#232)
_DL = ["3521%02d" % n for n in range(1, 17)]

PARTS = {pn: DECOR_TUBE for pn in _DT + _DR + _DL}

# the door stops: aluminium angle cut to length (DL's hinge-side stop in 3 numbers, D-120 and D-123; DT's top stop).
# Refused today as open sections ("folded sheet"); they draw once the generator reads bought profiles (the Lead,
# 2026-11-01, as for 368004)
DOOR_STOP = {
    "corner": "-X-Y-Z",
    "notes": ["Aluminium angle 6063-T6 cut to length, black anodised matte 20 um (AA20); bonded with structural tape "
              "(DL's pieces, HOLD: product) or screwed (DT's top stop), as its parts-list row says."],
    "tolerance": "cut length ±0.5, square ends (assumption); hole sizes +0.2/0 (assumption). Not ISO 2768 on the "
                 "anodised faces.",
}
for _pn in ("351105", "351106", "351107", "351203"):
    PARTS[_pn] = DOOR_STOP

NO_DRAWING = {}
