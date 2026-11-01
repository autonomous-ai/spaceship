"""CEILING's entries for drawgen (D-139: each team keeps its own entries here, in its own PRs; tools/drawgen's owner
reviews the code and a team's first entries). See tools/drawgen/teams/README.md for what an entry holds."""

# A ceiling frame's members get no sheets of their own (D-162): each member's drawing is its row in its frame's cut list
# on the frame's weldment sheet (411101, 411102), which also carries the holes made after welding. No ceiling member has
# a before-weld feature: its length and end cuts (the mitre plates' cut-backs too) are the cut list's, every joint hole
# is made after welding (J-FRAME-01), and the seam's 1 x 45 lead-in is ground with the closing face's beads after
# welding.
# The frames' weldment sheets come from the generator's weldment hooks (#365): the frame's bodies are its members', and
# its cut list is the team's tube cut list, with the mitre plates welded in (J-FRAME-01).
# Datums: each half drops onto the back panel's two spigots (R-J13) through its back member's round hole and slot
# (F-4111-10), so A is the frame's underside (the seat), B the round spigot hole, and C the closing face, since ST-04
# runs from the round hole to the closing face (+/-0.1, joints register 2.11). C1's closing face is its +X face, C2's
# its -X face.
CEILING_FRAME = {
    "datums": "spigot", "spigot_dia": 8.5, "spigot_slot": True,
    "material_has": "steel", "material_why": "D-131's welded, galvanized steel frame",
    "cut_list": {"file": "410000_P01_CEILING-TUBE-CUT-LIST_BOM.csv", "welded_in": ["831007", "831008"]},
    "a_words": "the frame's underside (Z 2354), the back member's seat on the back panel's top tube",
    "notes": [
        "FRAME: welded, galvanized steel box tube (D-131, J-FRAME-01). Corners mitred, with a 2.0 mm mitre plate "
        "welded into each mitre (831007 at the front corners, 831008 at the back ones, placed as the joints CAD "
        "README gives); the T joints direct. Every corner and T joint welded all round, continuously, so each tube "
        "stays sealed. MIG brazing with CuSi3 wire (ISO 24373 S Cu 6560) under argon preferred; or short-arc MAG with "
        "G3Si1 wire (ISO 14341-A) if the factory's welding procedure passes J-T7's coupons (HOLD-22).",
        "Weld in a jig that holds every member flat and square on its skin side: diagonally opposite corners in "
        "turn, then the T joints from the middle out, alternating sides; the frame cools in the jig. Beads on the "
        "skin-side faces, the seam faces and any face a skin return covers ground flush (0 to 0.2 proud, never more "
        "than 0.3 below the face), and so is the weld over each plate's trimmed end at an outer corner.",
        "Pre-galvanized tube, zinc Z100: no hot-dip galvanizing after welding, so no vent or drain holes. Every "
        "burnt zone wire-brushed and coated with a 2-component zinc-rich epoxy (about 40 µm dry; assumption).",
        "Every joint hole is made after welding and the touch-up, by CNC or a drill jig that locates on the frame's "
        "joint faces and spigot hole; the seam member's 1 x 45° lead-in is ground with the closing face's beads "
        "(F-4111-12). Rivnuts 838003 (zinc-plated steel, D-163) are set after the touch-up, before the bond.",
    ],
    "tolerance": "hole and slot positions Ø0.4 to A|B|C (R-J6); the closing face and the spigot slot ±0.1 from B "
                 "(ST-04, joints register 2.11); rivnut holes Ø10.00 +0.10/0 (D-163); other hole sizes +0.2/0 "
                 "(assumption); cut lengths ±0.5 (parts list); welded frame: outer size ±0.5 (parts list, "
                 "assumption), seam faces flat within 0.5, skin-side faces within ±0.5 of one plane lying free, "
                 "diagonals equal within 1.5, measured on a flat table after welding, before the holes; straighten "
                 "cold or reject, never clamp flat (J-FRAME-01).",
}

PARTS = {
    "411101": dict(CEILING_FRAME, c_face="+X", c_words="the closing face (X -2.75), C1's face of J-CEIL-02's seam"),
    "411102": dict(CEILING_FRAME, c_face="-X", c_words="the closing face (X 2.75), C2's face of J-CEIL-02's seam"),
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
