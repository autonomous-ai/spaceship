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
}
