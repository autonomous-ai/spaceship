"""FRONT's parts that drawgen draws (D-139: each team keeps its own entries here, in its own PRs; tools/drawgen's
owner reviews the code and a team's first entries). See tools/drawgen/teams/README.md for what an entry holds."""

# A decor frame's tube that keeps a sheet of its own under D-162 (two cuts at one end). Its length and end cuts are its
# row in the frame's cut list, which governs (D-162: the cut list is the members' drawing), so the sheet takes the cut
# list's tolerances. None of the four has a hole (Reviewer 8 on #320).
DECOR_TUBE = {
    "corner": "-X-Y-Z",
    "material_has": "aluminium", "material_why": "the decor frames' 6063-T6 tube until D-131's steel switch",
    "notes": [
        "Cut from 6063-T6 aluminium tube to the length and end cuts shown, as the frame's cut list row gives them "
        "(D-120, D-162: the cut list governs); mill finish, hidden (D-79). TIG-welded into its frame in the frame's "
        "jig (its weldment drawing).",
    ],
    "tolerance": "as the frame's cut list (D-162): cut length ±0.5 and end angles ±0.5°.",
}

# D-162 (the Lead's ruling, 2026-11-01): a welded frame's member is drawn by its row in the frame's cut list, on the
# frame's weldment sheet (section, length, both end angles and how they lean); a member keeps a sheet of its own only
# for an end the row can't state. Four FRONT members have two cuts at one end (the Mechanical Checker's C05 end rule,
# #357, on #313's STEPs): DT's catch and stop rail 352207 and DR's facet and chamfer tubes 352317, 352318, 352319.
TWO_CUT = ["352207", "352317", "352318", "352319"]
PARTS = {pn: DECOR_TUBE for pn in TWO_CUT}
# 352207's default view looked at its mitred end face-on (Reviewer 7 on #320): a principal view along the cut's plane
# its second cut is too small at 1:5 for a dimension (#313's DT model: the end edges 27.37 at 50.9 deg and 2.74 square)
PARTS["352207"] = dict(DECOR_TUBE, principal={"look": "-Z", "x": "+X"}, notes=DECOR_TUBE["notes"] + [
    "Two cuts at its right end (D-162: why it keeps this sheet): along DR's joint line at 50.9° from square, and its "
    "back corner (the top edge in the principal view) cut square for the last 2.74 across the tube, at DT's right "
    "edge; the 1422.77 runs to that square cut (DT's model, #313)."])

# DT's 11, DR's 21 (352321 cancelled) and DL's 16 tube parts (#232, #287)
_DT = ["3522%02d" % n for n in range(1, 12)]
_DR = ["3523%02d" % n for n in range(1, 23) if n != 21]
_DL = ["3521%02d" % n for n in range(1, 17)]
NO_DRAWING = {pn: "D-162: a welded frame member with one plane cut at each end; its row in its frame's cut list, on "
                  "the frame's weldment sheet, is its drawing (section, length, both end angles and the lean)"
              for pn in _DT + _DR + _DL if pn not in TWO_CUT}

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

