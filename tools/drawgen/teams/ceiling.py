"""CEILING's entries for drawgen (D-139: each team keeps its own entries here, in its own PRs; tools/drawgen's owner
reviews the code and a team's first entries). See tools/drawgen/teams/README.md for what an entry holds."""

# A ceiling frame's member (D-120: each member its own part; the frames 411101 and 411102 are their weldments). Its
# length and end cuts are its cut list row's; D-131 makes it welded galvanized steel (J-FRAME-01), and its joint holes
# are made after welding, located from the frame's joint faces and spigot hole, as the frame's own sheet places them.
CEILING_MEMBER = {
    "corner": "-X-Y-Z",
    "material_has": "steel", "material_why": "D-131's welded, galvanized steel frame",
    "notes": [
        "Cut from pre-galvanized steel tube (S280GD+Z or SGC400, Z100) to the length and end cuts shown, as the frame's "
        "cut list row gives them (D-120, D-131); each mitred end cut back square to its mitre for the 2.0 mitre plate "
        "(J-FRAME-01). Welded into its frame (411101 or 411102) in the frame's jig.",
        "Holes, where the tables show them: made after welding and the zinc-rich touch-up, by CNC or a drill jig that "
        "locates on the frame's joint faces and its spigot hole (J-FRAME-01); this sheet shows them on the tube for "
        "reference. Rivnuts 838003 are set after that.",
    ],
    "tolerance": "cut length +0/-0.5 and end angles ±0.25° (the cut list, assumption); hole positions to the frame's "
                 "datums (R-J6: Ø0.4 to A|B|C, the spigot hole and slot ±0.1); rivnut holes Ø9.53 +0.10/0 (maker); "
                 "other hole sizes +0.2/0 (assumption). Not ISO 2768 on the tube.",
}

# the members of both frames (D-120 numbers): side 412101 and cross member 1 412105 serve both frames (C2's turned),
# the plain cross member 412001 four times
PARTS = {pn: CEILING_MEMBER for pn in ("412101", "412102", "412103", "412104", "412105", "412202", "412203", "412204",
                                        "412001")}

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
