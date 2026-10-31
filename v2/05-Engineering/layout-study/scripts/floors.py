"""Floor options: the plan's raised steel floor, a thin floor, no floor, and castors (the Lead's optional fourth).

Weights are the BASE assembly under the light build. Step height is room floor to the walking surface at the door.
"""
from inputs import p
from shapes import al_rhs, plate_kg
from v2_model import LIGHT, base_parts, geom, variant

CASTOR_KG = 1.2          # assumption: 75 mm locking castor rated well above 50 kg, each
CASTOR_N = 6             # 6 castors under about 300 kg leaves margin for an uneven floor
CASTOR_FRAME_H = 60      # assumption: 60 mm aluminium platform frame with castors in pockets
CASTOR_CLEAR = 15        # assumption: frame bottom above the floor when rolling


def castor_base_kg():
    g = geom()
    perim = 2 * (p("pod_w") + p("pod_d")) * 1e-3 * al_rhs(60, 100, 3)          # stiff ring for racking while moving
    joists = 2 * g["inner_w"] * 1e-3 * al_rhs(30, 60, 2)
    floor = plate_kg(g["inner_w"] * g["inner_d"] * 1e-6, 15, p("rho_ply")) + g["inner_w"] * g["inner_d"] * 1e-6 * 0.3
    feet = 4 * p("glide_kg")                                                     # parking feet so it stops rolling
    return perim + joists + floor + CASTOR_N * CASTOR_KG + feet + 6 * 0.15


def floor_options():
    raised = sum(pt.total for pt in base_parts(variant(LIGHT, floor="raised"), False))
    thin = sum(pt.total for pt in base_parts(LIGHT, False))
    none = sum(pt.total for pt in base_parts(variant(LIGHT, floor="none"), False))
    board = 15 + 3          # 15 mm ply + vinyl or carpet finish
    rows = [
        dict(key="raised", name="Raised steel floor (plan as written)", kg=raised,
             step=p("glide_h") + p("base_h") + 15,
             sound="Closed box: boards over a 100 mm cavity; seal the board joints and perimeter.",
             square="Best: the welded or bolted frame sets square and level; walls bolt to it.",
             level="6 M10 feet under the frame; needs a spanner unless the feet adjust from above.",
             cables="Under the floor, easy.",
             assembly="Longest: 6 frame bars, 2 joists, 4 bolted corners, 6 feet, then 2 boards screwed to the joists (a second fastener type and tool).",
             look="Same as v1.", status="calculation"),
        dict(key="thin", name="Thin floor inside an aluminium base band (PROPOSED)", kg=thin,
             step=board + 3,
             sound="Closed box: floor panels on a 3 mm seal mat, gasket to the base band; the room slab adds mass under it.",
             square="Good: the aluminium base band with corner keys sets square; floor panels float inside it.",
             level="8 glides adjusted from above with the same hex key; floor panels follow the room floor and carry no walls.",
             cables="Inside the back wall cavity and along the base band channel.",
             assembly="Quick: 4 rails and 6 corner keys, level, drop in 2 floor panels.",
             look="Base band unchanged except across the door, where it becomes a low threshold.", status="calculation"),
        dict(key="none", name="No floor (base band only)", kg=none, step=0,
             sound="Open box: sound and air leak under the walls into the room floor; floorless pods post the weakest numbers (market study).",
             square="As the thin floor (same base band).",
             level="As the thin floor.",
             cables="Base band channel only.",
             assembly="Quickest: 4 rails and 6 corner keys, level.",
             look="As the thin floor.", status="calculation"),
        dict(key="castors", name="Castor platform (optional, Lead's request)", kg=castor_base_kg(),
             step=CASTOR_CLEAR + CASTOR_FRAME_H + board,
             sound="Closed box like the raised floor, but the gap under the pod needs a skirt or drop seal when parked.",
             square="Needs a stiffer platform: the pod racks while rolling, and the glass door can go out of line.",
             level="Castors do not level; 4 parking feet are added.",
             cables="Under the platform; the power cord must be long and loose enough to move the pod.",
             assembly="Like the raised floor (knock-down platform), plus 6 castors.",
             look="Base band hides the castors if the frame stays 100 mm; a ramp is needed at the door.", status="assumption"),
    ]
    for r in rows:
        r["delta_thin"] = r["kg"] - thin
    return rows
