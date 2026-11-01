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
        # the overall sizes on the sides away from the balloons, so no leader crosses them (Reviewer 16's P3 on #411);
        # ELECTRICAL's profile is ballooned on section A-A, where it shows cut under the right run
        "overall_sides": {"x": "down", "y": "right"},
        "balloon_views": {"718101": "section_A"},
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
    # The ledge is seen as the room sees it, from the left (toward the right wall), with its plan from below; a section
    # at 1:2 through the bracket at Y 464.32 shows the folded top sitting on it, and the brackets' balloon goes on the
    # plan, clear of the cutting plane. The brackets are the list's HOLD envelopes until INTERIOR's next rebuild makes
    # them made parts, when this sheet and 810000 are drawn again.
    "810101": {
        "principal": "left",
        "views": ["below"],
        "balloon_views": {"818101": "below"},
        "sections": [
            {"letter": "A", "point": [1036, 464.32, 1000], "normal": [0, -1, 0], "scale": 0.5, "slice": 10,
             "window": [900, 1170, 905, 1075]},
        ],
        "notes": [
            "Fitted on site after the clock (assembly guide, step 22): the ledge top 811101 on its brackets 818101 on "
            "the right wall's lower panel R1, centred in the 1051 of wall beside the air column (Y -259.5 to 740.5), "
            "its top at Z 1067, 5 mm off the felt so it never touches the floating lining (INTERIOR feature rationale "
            "F-8101-01, F-8101-02; D-17, D-57).",
            "The brackets carry the ledge into R1's stiles through stand-offs and clearance holes in R1's cassette "
            "(F-8101-03).",
            "HOLD: the brackets 818101 are drawn as their held envelopes (the parts list's HOLD rows, rated for a 225 N "
            "lean at the front edge x 3), and their fixings are on hold with them. INTERIOR's next rebuild makes them "
            "made parts on R1's studs, and this sheet is drawn again then.",
        ],
    },
    # The INTERIOR GA: each assembly as fitted in the pod, and where it sits, from INTERIOR's feature rationale.
    "810000": {
        "notes": [
            "INTERIOR as fitted in the pod (D-70): the light shelf 810201 along the tops of the side and back walls "
            "(underside Z 2230), the work wall ledge 810101 on the right wall's lower panel R1 beside the air column "
            "(top Z 1067), and the screen rail 818102 above it on R2 (centre Z 1300) (INTERIOR feature rationale "
            "F-8102-02, F-8101-01, F-8103-01).",
            "All of it is fitted on site: the light shelf at step 19, the ledge and the screen rail at step 22, after "
            "the clock (assembly guide). The ledge and the rail stand 5 mm off the felt on stand-offs to WALL's "
            "stiles, so the floating linings carry nothing (D-17, D-57); the light shelf screws to the wall "
            "cassettes (F-8102-07).",
            "HOLD: the ledge's brackets 818101 and the screen rail 818102 are drawn as their held envelopes, and every "
            "fixing is on hold (F-8101-03, F-8103-02, F-8102-07). INTERIOR's next rebuild makes the brackets and the "
            "rail made parts on R1's and R2's studs, and this sheet is drawn again then.",
        ],
    },
}
