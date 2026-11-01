"""GA sheet 1, the whole pod 100000, for the drawing generator (D-158; the PM's rulings of 2026-11-01).

Read by tools/drawgen/pod_assembly.py, not by assembly.py: the pod has no team STEP of its own (it is drawn from every
team's), so it isn't in ASSEMBLIES. No PARTS or NO_DRAWING here: the pod's parts are drawn on their teams' sheets.
"""

POD = {
    "principal": "front",
    "views": ["above", "from_left", "from_right"],
    "sections": [
        # A-A through the door's middle, X -373.5 = (the door's left edge X -961 + its bottom right X 214) / 2
        # (skeleton P04: door_xl 289 and door_xbr 1464 from the pod's side at X -1250), seen from the left
        {"letter": "A", "point": [-373.5, 0, 1200], "normal": [-1, 0, 0], "on": "above", "words": "the door's middle"},
        # B-B at mid depth, Y 0, seen from the front
        {"letter": "B", "point": [0, 0, 1200], "normal": [0, -1, 0], "on": "above", "words": "mid depth"},
        # C-C, a plan at Z 1000 seen from above: the door, the fixed glass, DL and DR, the walls' build-up in plan
        # (Reviewer 5 on #377: a section through the fixed glass)
        {"letter": "C", "point": [0, 0, 1000], "normal": [0, 0, 1], "on": "principal",
         "words": "through the door and the fixed glass"},
    ],
    # The door turned open for its clear opening (guideline 5.1: the door's clear size at a stated open position;
    # REQ-US-03: the clear width with the door open 90 deg goes on the GA). It opens outward on its left hinges
    # (D-19). The hinge isn't named (HOLD H01), so the pivot is taken on D-154's limit, the kick strip's outer face
    # Y -709, in the middle of the 11 mm gap between the leaf's hinge edge (X -961) and DL's door face (X -972);
    # the hinges' HOLD spaces (368101, boxes, not hinges) are left out.
    "door": {"unit": "360001", "pivot": [-966.5, -709.0], "angle": 90, "left_out": ["368101"]},
    # Clear sizes (Reviewer 5 on #377; guideline 5.1: inside sizes and the door's clear opening): each the free
    # stretch along one axis through the pod's bodies from a start inside the room, its ends the parts named (any
    # part number in a body's chain; "floor" = the room floor, Z 0, nothing in between); tried at each search
    # position until it is measured between those parts and its value finds a free place on its view. "beam": the
    # stretch's section where it is wider than a line (the doorway's depth, or its width for the height). A size
    # without a view is given in the notes only.
    "clear": [
        {"name": "inside width", "view": "section_C", "along": "x", "start": [0.0, 300.0, 1000.0],
         "search": {"y": [300.0, 500.0, 100.0, 650.0, -100.0, -300.0]}, "ends": [["510101"], ["510102"]],
         "label": "INSIDE %s"},
        {"name": "inside depth", "view": "section_C", "along": "y", "start": [-373.5, 0.0, 1000.0],
         "search": {"x": [-373.5, -500.0, -250.0, -650.0, -150.0]}, "ends": [["361001"], ["510201"]],
         "label": "INSIDE %s"},
        {"name": "clear height", "view": "section_B", "along": "z", "start": [-600.0, 0.0, 1200.0],
         "search": {"x": [-600.0, 600.0, -300.0, 300.0, -900.0, 900.0]}, "ends": [["floor"], ["510301"]],
         "label": "CLEAR %s"},
        {"name": "door clear height", "view": "section_A", "along": "z", "start": [-505.0, -681.0, 1200.0],
         "beam": {"x": [-940.0, -70.0], "y": [-850.0, -640.0]}, "draw_at": {"y": -681.0}, "open": True,
         "offset": "left", "ends": [["floor"], ["368007", "351203"]], "label": "DOOR CLEAR %s"},
        {"name": "door clear width", "view": "section_C", "along": "x", "start": [-373.5, -700.0, 1000.0],
         "beam": {"y": [-850.0, -640.0]}, "open": True, "outside": "down",
         "ends": [["351103"], ["368003", "361003", "368004"]], "label": "DOOR CLEAR %s"},
        {"name": "door clear width at the foot", "along": "x", "start": [-373.5, -700.0, 115.0],
         "beam": {"y": [-850.0, -640.0]}, "open": True, "ends": [["351103"], ["368003", "361003", "368004"]]},
        {"name": "door clear width at the head", "along": "x", "start": [-500.0, -700.0, 2089.0],
         "beam": {"y": [-850.0, -640.0]}, "open": True, "ends": [["351103"], ["368003", "361003", "368004"]]},
    ],
    # Position codes (guideline 5.1; PM ruling 2026-11-01: L1 to R2, B1 to B4, C1 to C3), each on a view that shows
    # its panel face on; the back's are seen from inside, in B-B
    "codes": {"from_left": ["L1", "L2"], "from_right": ["R1", "R2"], "above": ["C1", "C2"],
              "section_B": ["B1", "B2", "B3", "B4"]},
    "codes_words": "B3 and B4 aren't modelled yet (WALL); the pod has two ceiling halves, so there is no C3.",
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
    ],
}
