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
