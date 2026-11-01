"""GA sheet 1, the whole pod 100000, for the drawing generator (D-158; the PM's rulings of 2026-11-01).

Read by tools/drawgen/pod_assembly.py, not by assembly.py: the pod has no team STEP of its own (it is drawn from every
team's), so it isn't in ASSEMBLIES. No PARTS or NO_DRAWING here: the pod's parts are drawn on their teams' sheets.
"""

POD = {
    "principal": "front",
    "views": ["above", "from_left"],
    "sections": [
        # A-A through the door's middle, X -373.5 = (the door's left edge X -961 + its bottom right X 214) / 2
        # (skeleton P04: door_xl 289 and door_xbr 1464 from the pod's side at X -1250), seen from the left
        {"letter": "A", "point": [-373.5, 0, 1200], "normal": [-1, 0, 0], "on": "above"},
        # B-B at mid depth, Y 0, seen from the front
        {"letter": "B", "point": [0, 0, 1200], "normal": [0, -1, 0], "on": "above"},
    ],
    "interfaces": [
        {"view": "principal", "of": ["410000", "610000"], "along": "y", "at": "max",
         "origin": {"pn": "110000", "face": "-Z"}, "side": "right",
         "words": "FRONT VIEW: heights from the room floor (Z 0, under the glides): the roof skin's top 2400 (D-21) "
                  "and the overall top 2402, AIR's roof grille 611602 (PM ruling 2026-11-01: the room's ceiling must "
                  "clear the overall height)"},
    ],
    # the packaging isn't on the pod as it stands
    "leave_out": ["910000"],
    "notes": [
        "Pod axes (conventions section 4): origin on the room floor at the pod's centre; +X right seen from outside "
        "facing the door, +Y back, +Z up; the front is the door side.",
        "No floor and no threshold (D-132): people stand on the room floor, and the base stands on its glides "
        "(glide_h 10, skeleton P04).",
        "Walls and ceiling are 84 deep: ACP 3, bond 3 (D-137), steel frame 40 (D-131), gap 4, lining cassette 34 "
        "(skeleton P04, stack_t). Seams 2.26 at a metal stop; the closing seams B1-B2, B3-B4 and C1-C2 have a 5.5 "
        "frame gap (joints register 2.8).",
        "Still to come (WALL): the back upper panels B3 and B4 and their cassettes 510203 and 510204 are not "
        "modelled yet, so the back wall's upper half is empty in the views and sections; this sheet is drawn again "
        "when they are (PM ruling 2026-11-01).",
        "Sections A-A and B-B cut the teams' parts as modelled; each assembly's own sheets give its build-ups, "
        "fixings and sizes.",
    ],
}
