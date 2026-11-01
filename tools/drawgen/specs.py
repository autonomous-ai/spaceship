"""Which parts drawgen draws, and the few choices a STEP can't give: datums, extra notes and the tolerance note.

Everything else (views, sections, holes, sizes, names, material, finish, revision) is read from the part's STEP,
its team parts list and the feature registers each time the drawing is made. Tolerances are the project's own,
from the joints register, the parts lists and the team drawings; never a blanket ISO 2768 (guideline 3.2).
"""

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

# BASE side band: the wall above stands on the band's two spigots (their rivnut holes FB-05), so the front one is
# datum B as on the frames (joints register R-J6, R-J13, 2.11; Reviewer 5's D-114 pass on #202).
BASE_SIDE_BAND = {
    "datums": "spigot", "spigot_dia": 9.53, "spigot_pick": "-Y", "spigot_slot": False,
    "c_face": "-X",
    "a_words": "top face (the wall seat, Z 110)",
    "c_words": "the outer face (X -1250, flush with the ACP)",
    "notes": ["Front end: mitre to the DL decor block's outer facet band piece, 24.14° from square, long point on "
              "the outer face; back end square (BASE tube cut list)."],
    "tolerance": "hole positions Ø0.4 to A|B|C (joints register R-J6; stack ST-03 leaves 0.05 mm); the back spigot "
                 "rivnut hole ±0.1 from B along the band (joints register 2.11); rivnut holes Ø9.53 +0.10/0 (maker); "
                 "other hole sizes +0.2/0 (assumption); cut length +0/-0.5, end angle ±0.25° (BASE cut list, "
                 "assumption). Not ISO 2768 on the anodised faces.",
}

# pn: (team, kind, spec). kind "part" = one part on its sheet; "tabulated" = D-89 part 1, the listed numbers on
# the first one's sheet.
SPECS = {
    "211101": ("wall", "part", WALL_FRAME),
    "211102": ("wall", "part", WALL_FRAME),
    "211501": ("wall", "tabulated", {"covers": ["211501", "211502", "211503", "211504"]}),
    "111101": ("base", "part", BASE_SIDE_BAND),
}

# Parts that need no drawing at all, and why (drawgen won't make one).
NO_DRAWING = {
    "811205": "cancelled (D-126: a bought LED profile's clip-in diffuser takes its place); before that, D-125 gave "
              "the plain strip a full parts-list line and no drawing",
}

# The sample the Lead reviews before anything else is generated (brief): frame, its RH pair, the table drawing,
# the tube. The plate of the first sample (811205) needed no drawing under D-125 and is cancelled by D-126.
SAMPLE = ["211101", "211102", "211501", "111101"]
