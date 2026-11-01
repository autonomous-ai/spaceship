"""CEILING's entries for drawgen (D-139: each team keeps its own entries here, in its own PRs; tools/drawgen's owner
reviews the code and a team's first entries). See tools/drawgen/teams/README.md for what an entry holds."""

PARTS = {}

NO_DRAWING = {}

# Assembly sheets (tools/drawgen/assembly.py). CEILING's list names a panel's parts by the key 'assy_c1' (C1) and
# 'assy_c2' (C2), not by its number: the entry gives the key. The build-up (D-147 (2)): a section across the panel
# near its outer side member, at 1:2, its layers named and their faces given from the frame's room face.
ASSEMBLIES = {
    # The ceiling cassette (both panels take one, the list's key 'cassette'). CEILING's entry facts for it (after
    # Reviewer 5's Hold on #306, 2026-11-01): the tray's datums A (the base's top face, the back, toward the frame),
    # B (the front return's outer face) and C (the centre plane); the rib centre lines at +-193.33 from C; the clip
    # and catch centres across from C and along from B; the order of fitting and fixing, with HOLD where undecided.
    # The build-up (D-147 (2)) at 1:2 across the first clips, over the tray's edge and a rib, its faces from A. The
    # section is lettered D, after the datums.
    "510301": {
        "parent_keys": ["cassette"],
        "datums": [
            {"letter": "A", "pn": "513101", "face": "+Z", "view": "section_D",
             "words": "the tray's base, its top face: the back, toward the frame"},
            {"letter": "B", "pn": "513101", "face": "-Y", "view": "principal",
             "words": "the tray's front return, its outer face"},
            {"letter": "C", "pn": "513101", "median": "x", "view": "principal",
             "words": "between its side returns' outer faces"},
        ],
        "centre_lines": [{"view": "principal", "of": ["513102"]}],
        "interfaces": [
            {"view": "principal", "of": ["513102", "518001", "518002"], "along": "x",
             "origin": {"pn": "513101", "pick": "-X"}, "sign": "view", "list": True, "origin_line": True,
             "words": "VIEW FROM ABOVE, across the cassette from datum C: the rib, clip and catch centres"},
            {"view": "principal", "of": ["518001", "518002"], "along": "y",
             "origin": {"pn": "513101", "face": "-Y"}, "list": True,
             "words": "VIEW FROM ABOVE, along the cassette from datum B: the clip and catch centres"},
        ],
        "balloon_views": {"518001": "principal", "518002": "principal"},
        "sections": [
            {"letter": "D", "point": [-583, -266, 2353], "normal": [0, -1, 0], "scale": 0.5,
             "window": [-1165, -740, 2310, 2395], "slice": 10, "stack": True,
             "stack_from": {"pn": "513101", "face": "+Z"}},
        ],
        "notes": [
            "Fitting and fixing order (CEILING): (1) the tray 513101, its lips turned in; (2) the two ribs 513102 "
            "to the base's underside, their flanges against it and their crowns carrying the felt (H09); (3) the "
            "felt 513201 onto the lips and the rib crowns (H09); how it passes the 12 lips is the factory's call "
            "(HOLD); (4) the fill strips 513301 to 513303 on datum A, notched round the clips and catches (H10); "
            "(5) the clips 518001 and the catches 518002 (HOLD).",
        ],
    },
    "410101": {
        "parent_keys": ["assy_c1"],
        "sections": [
            {"letter": "A", "point": [-600, 100, 2377], "normal": [0, -1, 0], "scale": 0.5,
             "window": [-1201.7, -1000, 2350, 2405], "stack": True},
        ],
    },
}
