"""BASE's parts that drawgen draws (D-139: each team keeps its own entries here, in its own PRs; tools/drawgen's
owner reviews the code and a team's first entries). See tools/drawgen/teams/README.md for what an entry holds."""

# BASE side band: the wall above stands on the band's two spigots (their rivnut holes FB-05), so the front one is
# datum B as on the frames (joints register R-J6, R-J13, 2.11; Reviewer 5's D-114 pass on #202).
BASE_SIDE_BAND = {
    "datums": "spigot", "spigot_dia": 9.53, "spigot_pick": "-Y", "spigot_slot": False,
    "c_face": "-X", "key_notes": True,
    "a_words": "top face (the wall seat, Z 110)",
    "c_words": "the outer face (X -1250, flush with the ACP)",
    "notes": ["Front end: mitre to the DL decor block's outer facet band piece, 24.14° from square, long point on "
              "the outer face; back end square, closed by the flat end cap 118003 no deeper than 2 (BASE tube cut "
              "list, D-129)."],
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
    "c_face": "+Y", "key_notes": True,
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
           "closed by the flat end cap 118003 no deeper than 2 (BASE tube cut list, D-129)."])

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
              "the intake's inline key 111215 (joints register J-BASE-02, D-144).",
              "No holes in the top wall: it is in view in front of the glass, so the 2 glides are levelled by turning "
              "their base (BASE feature rationale FB-24)."],
    "tolerance": "hole positions ±0.2 from B along the band and from C across it (joints register R-J6); keyhole seats "
                 "±0.2 from A (they set the band's height on the key's studs; assumption); keyhole slots 6.5 +0.1/0, "
                 "entries Ø12 +0.2/0 (assumption); glide nut holes Ø13 +0.10/0 (HOLD with the nut); cut length "
                 "+0/-0.5, square ends (BASE cut list, assumption). Not ISO 2768 on the anodised faces.",
}

PARTS = {
    "111101": BASE_SIDE_BAND,
    "111102": BASE_SIDE_BAND_RH,
    "111103": BASE_BACK_BAND,
    "111106": BASE_FR1,
}

NO_DRAWING = {
    "111601": "D-89 part 4: a flat plate with one hole, cut from sheet; its DXF and its full parts-list row are the "
              "drawing (BASE feature rationale FD-03)",
}
