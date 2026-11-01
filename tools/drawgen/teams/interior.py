"""INTERIOR's parts that drawgen draws (D-139: each team keeps its own entries here, in its own PRs; tools/drawgen's
owner reviews the code and a team's first entries). See tools/drawgen/teams/README.md for what an entry holds."""

# INTERIOR's folded aluminium parts (D-139; #335's bent sheet mode): each drawn from the INTERIOR STEP and its own DXF,
# the folds read from the model, which folds each bend to an inside radius equal to the sheet (the Lead's ruling
# 2026-11-01 on #335; K 0.44 in the DXFs, an assumption until the factory's bend table sets it)
PARTS = {pn: {"bent": True} for pn in ("811101", "811201", "811202", "811203")}

NO_DRAWING = {
    "811205": "cancelled (D-126: a bought LED profile's clip-in diffuser takes its place); before that, D-125 gave "
              "the plain strip a full parts-list line and no drawing",
}
