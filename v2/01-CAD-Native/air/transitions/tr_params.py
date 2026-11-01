"""AIR transitions: every number the two ducts are built from, with its status and source (mm).

Statuses as the project uses them: confirmed (a ruling or a fixed fact), source (read from another team's model
or a maker's data), calculation (from other values here), assumption (a design choice to be proven).
"""

import math

# (name, value, unit, status, source)
PARAMS = [
    # ---- folds (the Lead's ruling 2026-11-01 in this group: folds at R = t, K 0.44, as the project's other parts)
    ("k_factor", 0.44, "", "confirmed", "the Lead's ruling 2026-11-01; the project's rule for folded parts (D-159; CEILING, WALL, ELECTRICAL)"),
    # ---- the supply fan box (CEILING's 611402), as moved by the Lead's ruling of 2026-11-01 12:22
    ("sb_x0", 680.0, "mm", "confirmed", "the Lead's ruling 2026-11-01: the box moves 7 mm right, X 680 to 980 (6.3 mm to DR's B06)"),
    ("sb_w", 300.0, "mm", "source", "AIR's model (air report 7e): the box 300 x 155 x 300"),
    ("sb_y0", -819.0, "mm", "source", "FRONT's DR STEP (#313, 541fe7f): the box space's front at Y -819 after the 3 mm glue line"),
    ("sb_d", 155.0, "mm", "source", "AIR's model (air report 7e)"),
    ("sb_z0", 1650.0, "mm", "source", "AIR's model: the box Z 1650 to 1950"),
    ("sb_h", 300.0, "mm", "source", "AIR's model"),
    ("sb_t", 3.0, "mm", "source", "D-124: the fan box casings in 3 mm aluminium (CEILING, 2026-11-01)"),
    ("sb_lin_t", 50.0, "mm", "source", "D-121: the supply box's 50 mm linings on its two end walls, from Z 1795 to the top (CEILING)"),
    # ---- the intake riser (CEILING's 611501)
    ("rs_x0", 959.0, "mm", "source", "FRONT's DR STEP (#313, 541fe7f): the riser space X 959 to 1098, 3 mm right with the glue line"),
    ("rs_w", 139.0, "mm", "source", "AIR's model: the riser 139 wide"),
    ("rs_y0", -803.0, "mm", "source", "AIR's model (follow-up): the riser Y -803 to -653"),
    ("rs_d", 150.0, "mm", "source", "AIR's model (follow-up, the air report's D-130 table): the riser 150 deep"),
    ("rs_z1", 1445.0, "mm", "source", "AIR's model: the riser's top, open, at Z 1445"),
    ("rs_t", 1.0, "mm", "confirmed", "D-61: 1 mm galvanised steel riser"),
    # ---- the lower transition (riser to box): two halves, 1 mm galvanised steel
    ("lt_t", 1.0, "mm", "confirmed", "the Lead's ruling 2026-11-01: the lower duct in 1 mm galvanised steel, as the riser"),
    ("lt_r", 1.0, "mm", "confirmed", "the Lead's ruling 2026-11-01: inside radius = thickness"),
    ("lt_cr", 0.5, "mm", "assumption", "the slip clearance each side, the lower duct's collar inside the riser's top"),
    ("lt_cb", 0.5, "mm", "assumption", "the slip clearance each side, the lower duct's collar inside the box's bottom"),
    ("lt_hb", 25.0, "mm", "assumption", "the collar's depth into the riser: rivets at mid depth, 12.5 from both edges"),
    ("lt_ht", 20.0, "mm", "assumption", "the collar's depth into the box: rivets 10 above the box's edge and 10 under the collar's top, which stays 8 under the lip angle's rivet line (Z about 1678) and 28 under the bulkhead"),
    ("lt_relief", 3.0, "mm", "assumption", "corner relief: each fold stops this far from a corner where two folds meet (more than r + t)"),
    ("seam_hole_in", 6.0, "mm", "assumption", "a seam rivet's centre from the seam flange's fold line (outside the fold's zone)"),
    ("seam_w", 15.0, "mm", "calculation", "seam flange width: the hole 6 from the fold line plus 2 x the hole from the free edge (the project's edge rule)"),
    ("rivet_d", 4.0, "mm", "assumption", "closed-end blind rivets, 4.0 (the fan box casing's rivet, HOLD at the RFQ)"),
    ("rivet_hole", 4.1, "mm", "assumption", "the hole for a 4.0 blind rivet (maker's figure at the RFQ)"),
    ("rivet_pitch", 50.0, "mm", "assumption", "the most between seam rivets"),
    ("rivet_end", 12.0, "mm", "assumption", "the first rivet from a seam's end"),
    ("dens_steel", 7850.0, "kg/m3", "source", "galvanised steel DX51D+Z (the project's figure, AIR's model)"),
    ("dens_al", 2700.0, "kg/m3", "source", "aluminium 5052 (the project's figure, AIR's model)"),
]


class _P:
    def __init__(self, rows):
        self._rows = {r[0]: r for r in rows}
        for name, val, _u, _s, _src in rows:
            setattr(self, name, float(val))

    def row(self, name):
        return self._rows[name]

    def rows(self):
        return list(self._rows.values())


P = _P(PARAMS)

# derived: the box's and the riser's outlines (calculation)
P.sb_x1 = P.sb_x0 + P.sb_w
P.sb_y1 = P.sb_y0 + P.sb_d
P.rs_x1 = P.rs_x0 + P.rs_w
P.rs_y1 = P.rs_y0 + P.rs_d


def statuses_ok():
    return all(r[3] in ("confirmed", "source", "calculation", "assumption") for r in PARAMS)


assert statuses_ok()
assert math.isclose(P.sb_x1, 980.0)
