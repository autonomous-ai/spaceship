"""CEILING's entries for drawgen (D-139: each team keeps its own entries here, in its own PRs; tools/drawgen's owner
reviews the code and a team's first entries). See tools/drawgen/teams/README.md for what an entry holds."""

PARTS = {}

NO_DRAWING = {}

# Assembly sheets (tools/drawgen/assembly.py). CEILING's list names a panel's parts by the key 'assy_c1' (C1) and
# 'assy_c2' (C2), not by its number: the entry gives the key. The build-up (D-147 (2)): a section across the panel
# near its outer side member, at 1:2, its layers named and their faces given from the frame's room face.
ASSEMBLIES = {
    # The ceiling cassette (both panels take one, the list's key 'cassette'): its rib centre lines and the clip and
    # catch positions from the cassette's centre (Reviewer 5's Hold on #306), and its build-up at 1:2 across the
    # first clip, over the tray's edge and the first rib (D-147 (2)).
    "510301": {
        "parent_keys": ["cassette"],
        "centre_lines": [{"view": "principal", "of": ["513102"]}],
        "interfaces": [
            {"view": "principal", "of": ["513102", "518001", "518002"], "along": "x",
             "origin": {"pn": "513101", "pick": "-X"}, "sign": "view",
             "words": "VIEW FROM ABOVE: the rib, clip and catch centres across the cassette, from its centre (the "
                      "tray's)"},
            {"view": "principal", "of": ["518001", "518002"], "along": "y",
             "origin": {"pn": "513101", "pick": "-Y"}, "sign": "view",
             "words": "VIEW FROM ABOVE: the clip and catch centres along the cassette, from its centre"},
        ],
        "sections": [
            {"letter": "A", "point": [-583, -266, 2353], "normal": [0, -1, 0], "scale": 0.5,
             "window": [-1165, -740, 2310, 2395], "stack": True},
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
