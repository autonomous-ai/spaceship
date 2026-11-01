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
              "the outer face; back end square (BASE tube cut list)."],
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
    "notes": ["Both ends square (BASE tube cut list)."],
    "tolerance": "hole positions Ø0.4 to A|B|C (joints register R-J6); the other spigot rivnut holes ±0.1 from B along "
                 "the band (joints register 2.11: ST-02, ST-04); rivnut holes Ø9.53 +0.10/0 (maker); other hole sizes "
                 "+0.2/0 (assumption); cut length +0/-0.5, square ends (BASE cut list, assumption). Not ISO 2768 on the "
                 "anodised faces.",
}

PARTS = {
    "111101": BASE_SIDE_BAND,
    "111103": BASE_BACK_BAND,
}

NO_DRAWING = {}

# Assembly sheets (tools/drawgen/assembly.py): the band assembly with its factory-fitted hardware. What a STEP can't
# give: which views, where the sections cut (through a glide, a spigot and a J-BASE-01 bolt rivnut, each at 2:1 over
# the wall that holds it), the interface sizes along the band from the front spigot (datum B of 111101, R-J6), and
# the fixing order from the parts list's notes.
ASSEMBLIES = {
    "110101": {
        "views": ["above"],
        "unhatched": ["831001", "118002"],         # the spigots and the glides' stems (ISO 128-50)
        "sections": [
            {"letter": "A", "point": [-1230, -595, 50], "normal": [0, -1, 0], "scale": 2.0, "slice": 30,
             "window": [-1256, -1204, -2, 62]},
            {"letter": "B", "point": [-1230, -542.7, 50], "normal": [0, -1, 0], "scale": 2.0, "slice": 30,
             "window": [-1256, -1204, 86, 121]},
            {"letter": "C", "point": [-1230, -422.7, 50], "normal": [0, -1, 0], "scale": 2.0, "slice": 30,
             "window": [-1256, -1204, 86, 121]},
        ],
        "interfaces": [
            {"view": "above", "of": ["831001", "838003", "118002"], "along": "x",
             "origin": {"pn": "831001", "pick": "-Y"}, "side": "down",
             "words": "VIEW FROM ABOVE: the spigot, rivnut and glide centres along the band, from the front spigot "
                      "(datum B of 111101, joints register R-J6)"},
        ],
        "notes": [
            "Fitted at the factory (D-87), in this order: the six M6 rivnuts 838003 set in the band's top face "
            "(torque HOLD-01), a stop washer 831002 under the head of each of the four J-BASE-01 bolt rivnuts "
            "(joints register H-08); the two spigots 831001 screwed into their rivnuts with threadlocker; the M10 "
            "rivnuts 838006 set through the band's bottom face and the doublers 111601 (grip 4.5); the glides "
            "118002 preset; the end cap 118003 in the back end (BASE parts list notes).",
        ],
    },
}
