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
              "the outer face; back end square, closed by the flat end cap 118003 no deeper than 2 (BASE tube cut list, "
              "D-129).",
              "The back corner key 111211 goes in the back end at the factory (D-129, joints register J-BASE-02): its 2 "
              "button head screws 838010 come up through the bottom wall's Ø7.0 holes, and its 2 hook stud bolts "
              "838001 go through the inner wall's Ø7.0 holes into it, heads 1.8 off the wall, for the back band's end "
              "plate slots."],
    "tolerance": "hole positions Ø0.4 to A|B|C (joints register R-J6; stack ST-03 leaves 0.05 mm); the back spigot "
                 "rivnut hole ±0.1 from B along the band (joints register 2.11); rivnut holes Ø9.53 +0.10/0 (maker); "
                 "other hole sizes +0.2/0 (assumption); cut length +0/-0.5, end angle ±0.25° (BASE cut list, "
                 "assumption). Not ISO 2768 on the anodised faces.",
}

# BASE back band: B1 and B2 stand on its spigots. Datum B is the spigot rivnut under B1's round spigot hole, by the
# closing seam (X -102.75: BASE feature rationale FB-05, WALL 211201 F03), so B2's round spigot is within ±0.1 of it
# (joints register 2.11, ST-02 and ST-04); the scheme of the side band (PM ruling on #202: both band tubes read the
# same).
BASE_BACK_BAND = {
    "datums": "spigot", "spigot_dia": 9.53, "spigot_near": {"X": -102.75}, "spigot_slot": False,
    "c_face": "+Y",
    "a_words": "top face (the wall seat, Z 110)",
    "c_words": "the outer face (Y 850, flush with the ACP)",
    "notes": ["Both ends square, each closed by a 1.5 end plate welded in flush, 2420 over both plates (D-129). Each "
              "plate has one slot open at its bottom edge on the band's centre line, 12 wide at the edge and narrowing "
              "to 6.5 over its bottom 6, then 6.5 up to its round end, for the side band's 2 key studs as the band is "
              "lowered onto them; the bottom wall has a 12 x 9 notch at each end for the stud heads; each plate's "
              "bottom edge has a 1 x 45° bevel on its side-band side (joints register J-BASE-02, FR-15)."],
    "tolerance": "hole positions Ø0.4 to A|B|C (joints register R-J6); the other spigot rivnut holes ±0.1 from B along "
                 "the band (joints register 2.11: ST-02, ST-04); rivnut holes Ø9.53 +0.10/0 (maker); the end plate "
                 "slots 6.5 +0.1/0 wide, ±0.2 on the band's centre line (they set the corner across the band, FR-15; "
                 "assumption); other hole sizes +0.2/0 (assumption); cut length +0/-0.5, square ends, 2420 +0/-0.5 over "
                 "the welded plates (BASE cut list, assumption). Not ISO 2768 on the anodised faces.",
}

# BASE right side band: 111101's mirror (its own number, D-120), under R1; the same datum scheme, from its front
# spigot rivnut hole, C its outer face. Its front end meets the intake's facet piece under DR.
BASE_SIDE_BAND_RH = dict(
    BASE_SIDE_BAND, c_face="+X", c_words="the outer face (X 1250, flush with the ACP)",
    notes=["Front end: mitre to the intake's facet piece under DR, long point on the outer face; back end square, "
           "closed by the flat end cap 118003 no deeper than 2 (BASE tube cut list, D-129).",
           "The back corner key 111211 goes in the back end at the factory (D-129, joints register J-BASE-02): its 2 "
           "button head screws 838010 come up through the bottom wall's Ø7.0 holes, and its 2 hook stud bolts 838001 "
           "go through the inner wall's Ø7.0 holes into it, heads 1.8 off the wall, for the back band's end plate "
           "slots."])

# BASE FR1, the band under the fixed glass (X 218.5 to x_fr_joint 915): no wall stands on it, so no spigots. It goes on
# last, down onto the intake's inline key studs through the 2 keyholes in its welded end plate (joints register
# J-BASE-02), so the keyed end is datum B; A its bottom face on the glides, C its outer face. Origin at their corner.
BASE_FR1 = {
    "corner": "+X-Y-Z",
    "datum_words": {"A": "the bottom face (Z 10, on its glides)",
                    "B": "the keyed end plate's outer face (X 915, on the intake piece's end, J-BASE-02)",
                    "C": "the outer face (Y -850, the band's front line)"},
    "notes": ["Door end (X 218.5): square and open, closed by the flat end cap 118003, in view at the door opening "
              "(D-132). Keyed end (X 915): square, closed by a 1.5 end plate welded in flush, with the 2 keyholes for "
              "the intake's inline key 111211 (joints register J-BASE-02).",
              "No holes in the top wall: it is in view in front of the glass, so the 2 glides are levelled by turning "
              "their base (BASE feature rationale FB-24)."],
    "tolerance": "hole positions ±0.2 from B along the band and from C across it (joints register R-J6); keyhole seats "
                 "±0.2 from A (they set the band's height on the key's studs; assumption); keyhole slots 6.5 +0.1/0, "
                 "entries Ø12 +0.2/0 (assumption); glide nut holes Ø13 +0.10/0 (HOLD with the nut); cut length "
                 "+0/-0.5, square ends (BASE cut list, assumption). Not ISO 2768 on the anodised faces.",
}

# pn: (team, kind, spec). kind "part" = one part on its sheet; "tabulated" = D-89 part 1, the listed numbers on
# the first one's sheet.
SPECS = {
    "211101": ("wall", "part", WALL_FRAME),
    "211102": ("wall", "part", WALL_FRAME),
    "211501": ("wall", "tabulated", {"covers": ["211501", "211502", "211503", "211504"]}),
    "111101": ("base", "part", BASE_SIDE_BAND),
    "111102": ("base", "part", BASE_SIDE_BAND_RH),
    "111103": ("base", "part", BASE_BACK_BAND),
    "111106": ("base", "part", BASE_FR1),
}

# Parts that need no drawing at all, and why (drawgen won't make one).
NO_DRAWING = {
    "811205": "cancelled (D-126: a bought LED profile's clip-in diffuser takes its place); before that, D-125 gave "
              "the plain strip a full parts-list line and no drawing",
}

# The sample the Lead reviews before anything else is generated (brief): frame, its RH pair, the table drawing,
# the tube. The plate of the first sample (811205) needed no drawing under D-125 and is cancelled by D-126.
SAMPLE = ["211101", "211102", "211501", "111101"]
