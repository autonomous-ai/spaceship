"""CEILING's entries for drawgen (D-139: each team keeps its own entries here, in its own PRs; tools/drawgen's owner
reviews the code and a team's first entries). See tools/drawgen/teams/README.md for what an entry holds."""

# A ceiling frame's members get no sheets of their own (D-162): each member's drawing is its row in its frame's cut list
# on the frame's weldment sheet (411101, 411102), which also carries the holes made after welding. No ceiling member has
# a before-weld feature: its length and end cuts (the mitre plates' cut-backs too) are the cut list's, every joint hole
# is made after welding (J-FRAME-01), and the seam's 1 x 45 lead-in is ground with the closing face's beads after
# welding.
# The frames' weldment sheets wait for the generator's weldment hooks.
PARTS = {}

NO_DRAWING = {}

# Assembly sheets (tools/drawgen/assembly.py). CEILING's list names a panel's parts by the key 'assy_c1' (C1) and
# 'assy_c2' (C2), not by its number: the entry gives the key. The build-up (D-147 (2)): a section across the panel
# near its outer side member, at 1:2, its layers named and their faces given from the frame's room face.
ASSEMBLIES = {
    "410101": {
        "parent_keys": ["assy_c1"],
        "sections": [
            {"letter": "A", "point": [-600, 100, 2377], "normal": [0, -1, 0], "scale": 0.5,
             "window": [-1201.7, -1000, 2350, 2405], "stack": True},
        ],
    },
    "410102": {
        "parent_keys": ["assy_c2"],
        "sections": [
            {"letter": "A", "point": [600, 100, 2377], "normal": [0, -1, 0], "scale": 0.5,
             "window": [1000, 1201.7, 2350, 2405], "stack": True},
        ],
    },
    # The ceiling as the room sees it, from below (the two cassettes under the panels), with the front view; the
    # fitting order from the assembly guide (steps 7 and 18) and the joints register (J-CEIL-01, J-CEIL-02).
    "410000": {
        "parent_keys": ["ceiling"],
        "principal": "bottom",
        "notes": [
            "Fitted on site, C1 410101 then C2 410102 (assembly guide, step 7): each lifted from inside onto its back "
            "spigots on B3, its side against its side wall's upper panel, C2 dropping past C1's lead-in (CEILING feature "
            "rationale F-4111-12). Then the closing seam's 4 pins M6 x 25 838002 (J-CEIL-02), the 8 back-edge and the "
            "8 side-edge bolts M6 x 16 838001 (J-CEIL-01); the C1-C2 gap even, 4.3 to 6.7.",
            "The two ceiling cassettes 510301 (step 18): each lifted from below, fill side up, onto its clips behind "
            "the soffit, its 2 safety catches hooked before it's let go; their front edges 3 behind the soffit.",
        ],
    },
}
