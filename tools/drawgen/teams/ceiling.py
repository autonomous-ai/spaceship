"""CEILING's entries for drawgen (D-139: each team keeps its own entries here, in its own PRs; tools/drawgen's owner
reviews the code and a team's first entries). See tools/drawgen/teams/README.md for what an entry holds."""

# A ceiling frame's members get no sheets of their own (D-162): each member's drawing is its row in its frame's cut list
# on the frame's weldment sheet (411101, 411102), which also carries the holes made after welding. No ceiling member has
# a before-weld feature: its length and end cuts (the mitre plates' cut-backs too) are the cut list's, every joint hole
# is made after welding (J-FRAME-01), and the seam's 1 x 45 lead-in is ground with the closing face's beads after
# welding.
# The frames' weldment sheets wait for the generator's weldment hooks.
# The ceiling cassette's tray and ribs (D-17, D-37): 0.5 galvanized steel, folded on a press brake; v12's model folds
# them at their real radii (inside 0.5, K 0.44), so drawgen draws each from the STEP and its DXF (#335's bent mode).
# The facts are CEILING's feature rationale (F-513101-01 to -07, F-513102-01 to -04) and its parts list's rows.
TRAY_NOTES = [
    "TRAY: galvanized steel sheet 0.5, DX51D+Z (EN 10346). Blank laser cut from its DXF, then folded on a press "
    "brake: the four returns 90° toward the room (34 deep overall), then the four 12 lips 90° inward; inside radius "
    "0.5, K 0.44 (CEILING feature rationale F-513101-02 to -04; assumptions until the factory's tooling sets them); "
    "corner reliefs as the DXF.",
    "The ceiling cassette's back skin (D-17): it hangs on its 6 clips under the panel frames, with 2 safety catches "
    "(D-47, D-81; F-513101-06, F-513101-07: HOLD-08), and the felt is held by the lips over the 24 air gap "
    "(F-513101-03).",
    "The two Ø19.1 holes in the front and back returns take ELECTRICAL's cable bushing (F-513101-05).",
]
TRAY_TOLERANCE = ("cut ±0.2 and bent ±0.5 (the CEILING parts list, assumption); folds 90° ±1° (assumption); the Ø19.1 "
                  "holes +0.2/0, their centres ±0.5 (assumption: a bushing's panel hole); the base flat within 2 over "
                  "its length (assumption, guideline 6.3)")
RIB_NOTES = [
    "RIB: galvanized steel sheet 0.5, DX51D+Z (EN 10346), cut from its DXF and folded into a hat: crown 20, height "
    "24, flanges 2 x 12 (CEILING feature rationale F-513102-01); inside radius 0.5, K 0.44 (assumptions until the "
    "factory's tooling sets them).",
    "Two per cassette, under the tray's base at X' ±193.33, their flanges against it and their crowns carrying the "
    "felt; 1034 long, 5 clear of each return (F-513102-02, F-513102-03). HOLD: the rib's fixing to the tray (H09, "
    "F-513102-04).",
]
RIB_TOLERANCE = "length ±1 and bends ±0.5 (the CEILING parts list, assumption); folds 90° ±1° (assumption)"

PARTS = {
    "513101": {"bent": True, "notes": TRAY_NOTES, "tolerance": TRAY_TOLERANCE},
    "513102": {"bent": True, "notes": RIB_NOTES, "tolerance": RIB_TOLERANCE},
}

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
}
