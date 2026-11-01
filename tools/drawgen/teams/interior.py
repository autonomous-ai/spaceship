"""INTERIOR's parts that drawgen draws (D-139: each team keeps its own entries here, in its own PRs; tools/drawgen's
owner reviews the code and a team's first entries). See tools/drawgen/teams/README.md for what an entry holds."""

# INTERIOR's folded aluminium parts (D-139; #335's bent sheet mode): each drawn from the INTERIOR STEP and its own DXF,
# the folds read from the model, which folds each bend to an inside radius equal to the sheet (D-159; K 0.44 in the
# DXFs, an assumption until the factory's bend table sets it)
FOLDS = ("two folds to 90°, inside radius equal to the sheet, real folds in the model, flat blank from its DXF at K 0.44 "
         "(D-159; K is an assumption until the factory's bend table)")
FINISH = "Powder coat charcoal (RAL HOLD) after folding, edges deburred first."
TOL = ("cut ±0.5 and bent ±0.5 (the INTERIOR parts list, assumption); fold angles 90° ±1° (assumption); folded "
       "sizes are outside sizes.")
TOL_HOLE = TOL + " The Ø10 cable hole +0.2/0, its centre ±0.5 from the blank's edges (assumption: a cable pass, not a fit)."


def entry(sheet_t, part, hole):
    return {"bent": True,
            "notes": ["%s mm aluminium sheet, 5052-H32 (alloy HOLD; D-85): %s." % (sheet_t, part),
                      "Folds: " + FOLDS + ".", FINISH],
            "tolerance": TOL_HOLE if hole else TOL}


PARTS = {
    "811101": entry("1.5", "the work wall ledge's top, front lip and back flange", False),
    "811201": entry("1.0", "the light shelf's back run; the Ø10 cable hole is ELECTRICAL's feed", True),
    "811202": entry("1.0", "the light shelf's left run, 811203's mirror with no cable hole", False),
    "811203": entry("1.0", "the light shelf's right run; the Ø10 cable hole is ELECTRICAL's call-light drop", True),
}

NO_DRAWING = {
    "811205": "cancelled (D-126: a bought LED profile's clip-in diffuser takes its place); before that, D-125 gave "
              "the plain strip a full parts-list line and no drawing",
}

# Assembly sheets (tools/drawgen/assembly.py; D-158). The light shelf is fitted on site along the wall tops (the
# assembly guide's step 19); where each run sits, how it's fixed and what ELECTRICAL hangs on it come from INTERIOR's
# feature rationale (F-8102-01 to -07). Two sections at 1:2 show how the parts meet: across the right run with
# ELECTRICAL's LED profile under it (A-A), and in plan through the corner where the right run butts the back run (B-B).
ASSEMBLIES = {
    "810201": {
        "sections": [
            {"letter": "A", "point": [1136, 0, 2250], "normal": [0, -1, 0], "scale": 0.5, "slice": 10,
             "window": [1090, 1180, 2205, 2280]},
            # B-B looks up, as the view from below does, so its window is in that view's X and Y (pod +X and -Y); it
            # cuts at mid-lip height, through both lips and both back flanges
            {"letter": "B", "point": [1136, 736, 2240], "normal": [0, 0, -1], "scale": 0.5, "slice": 10,
             "window": [1080, 1175, -775, -680]},
        ],
        "notes": [
            "Fitted on site, after the ceiling cassettes, along the tops of the side and back walls (assembly guide, "
            "step 19): the back run 811201 on the back wall's lining (Y 766), full width (X -1166 to 1166); the side "
            "runs 811202 LH and 811203 RH on the side walls' linings, from the soffit's back face (Y -285) to the back "
            "run, which they butt (INTERIOR feature rationale F-8102-03, F-8102-04). The underside at Z 2230, the back "
            "flange's top at Z 2270 (F-8102-02).",
            "HOLD: each run's back flange is screwed to the wall cassettes; the fixing and its spacing are on hold "
            "with WALL's cassette tray (F-8102-07), and the parts list names no fixing yet.",
            "ELECTRICAL's up-light strip runs on each run's bottom, inside the U, aimed at the felt ceiling; the U is "
            "its wiring channel (F-8102-01). ELECTRICAL's down-light LED profile 718101 clips under the right run "
            "(F-8102-05). The feed comes through the back run's Ø10 hole at X 355 and the call light's drop through "
            "the right run's at Y -209.5, both at Z 2250 (F-8102-06); the feed is plugged in at step 19.",
        ],
    },
}
