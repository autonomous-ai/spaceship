"""AIR's entries for drawgen (D-139: each team keeps its own entries here, in its own PRs; tools/drawgen's owner
reviews the code and a team's first entries). See tools/drawgen/teams/README.md for what an entry holds."""

PARTS = {}

NO_DRAWING = {}

# Assembly sheets (tools/drawgen/assembly.py). The air column is seen from the pod (its front face, with the hub
# zone and the kick grille), from both sides, and in a section across it that shows what its faces hide: the fill,
# the corner angles and the supply cartridge 610301 (a reference outline: it ships on its own and slides in on site,
# D-61).
ASSEMBLIES = {
    "610101": {
        "principal": "rear",
        "views": ["from_left", "from_right"],
    },
    # The fan boxes: what they hold and how they're joined, from the feature rationale (F-6102-09, F-6104-01 to -07),
    # D-121 (each box's bulkhead and linings, inside its casing) and the assembly guide (steps 13, 16, 17). The supply
    # box's bulkhead, fans and linings show only in a section across it (A-A), so their balloons go there. The fans'
    # fixing, the lip's rivets, the pads, the buffer and the transitions are HOLD, as their rows say.
    "610401": {
        "sections": [
            {"letter": "A", "point": [830, -741.5, 1800], "normal": [0, -1, 0], "scale": 0.5, "slice": 10,
             "window": [670, 990, 1640, 1960]},
        ],
        "balloon_views": {"611404": "section_A", "618401": "section_A", "611407": "section_A"},
        "notes": [
            "Joined at the factory and shipped as one unit (D-87): the casing 611402 on top of the intake riser 611501, "
            "the riser transition 618103 between them. The casing is open at its bottom and its top, where the air "
            "passes (AIR feature rationale F-6104-01, F-6104-02). Inside it (section A-A), the two fans 618401 stand "
            "on the 2 mm bulkhead 611404, each over its Ø135 bore, and blow up into the supply transition 618102; "
            "only the two end walls are lined (611407), from 70 above the fans to the open top, so the air reaches "
            "them (D-121).",
            "The unit's weight sits on the lip angle 611408, riveted to the casing's front wall, through two rubber "
            "pads 618402 on DR's shelf tube F08; the riser buffer 618501, in a rivet nut 838003 on the riser's front "
            "face, touches DR's cross tube F07 and holds the unit upright (F-6104-05 to F-6104-07).",
            "On site the unit slides into DR, down to the riser's foot over the mesh space, and the fan box's plug-in "
            "connector is mated (assembly guide, step 13). Its fixings in DR are on hold with AIR and FRONT (the same "
            "step).",
            "HOLD: the fans' screws through the bulkhead, with the fans' mounting (618401 is HOLD in the parts list); "
            "the lip's 3 rivets, with the casing's; the pads and the buffer (products HOLD); and the two transitions, "
            "drawn as their held envelopes until they are designed (F-6104-03, F-6104-04).",
        ],
    },
    "610402": {
        "notes": [
            "Fitted in the soffit at the factory, at its right end under C2's roof slot (D-87; AIR feature rationale "
            "F-6102-09). The casing 611401 is open on its left face, where the exhaust cartridge's air comes in, and "
            "at its top, where the two fans 618401 blow up into the roof sleeve 611601.",
            "On site, once the soffit hangs, the fan box is plugged in before the hinged underside closes (assembly "
            "guide, step 16), and the roof sleeve drops through C2's roof slot onto the soft gasket on the box's top "
            "(step 17, #263).",
            "HOLD: the fans' fixing in the casing (618401 is HOLD in the parts list).",
        ],
        # the fans' balloon on the view from the left, where the fans show clear of the casing's walls (from above,
        # the left fan sits against the casing's wall, so the two arrows would meet)
        "balloon_views": {"618401": "from_left"},
    },
}
