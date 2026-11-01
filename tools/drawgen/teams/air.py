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
    # The fan boxes: what they hold and how they're joined, from the feature rationale (F-6102-09, F-6104-01 to -03)
    # and the assembly guide (steps 13, 16, 17). The fans' fixing and the transitions are HOLD, as their rows say.
    "610401": {
        "notes": [
            "Joined at the factory and shipped as one unit (D-87): the casing 611402 on top of the intake riser 611501, "
            "the riser transition 618103 between them, the two fans 618401 in the casing's top, blowing up into the "
            "supply transition 618102. The casing is open at its bottom and its top, where the air passes (AIR "
            "feature rationale F-6104-01, F-6104-02).",
            "On site the unit slides into DR, down to the riser's foot over the mesh space, and the fan box's plug-in "
            "connector is mated (assembly guide, step 13). Its fixings in DR are on hold with AIR and FRONT (the same "
            "step).",
            "HOLD: the fans' fixing in the casing (618401 is HOLD in the parts list), and the two transitions, drawn "
            "as their held envelopes until the AIR follow-up designs them (F-6104-03).",
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
