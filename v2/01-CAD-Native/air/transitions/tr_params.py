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
    ("sb_y0", -819.0, "mm", "source", "FRONT's DR STEP (#313, 541fe7f; the same at c65a3fa): the box space's front at Y -819 after the 3 mm glue line"),
    ("sb_d", 155.0, "mm", "source", "AIR's model (air report 7e)"),
    ("sb_z0", 1650.0, "mm", "source", "AIR's model: the box Z 1650 to 1950"),
    ("sb_h", 300.0, "mm", "source", "AIR's model"),
    ("sb_t", 3.0, "mm", "source", "D-124: the fan box casings in 3 mm aluminium (CEILING, 2026-11-01)"),
    ("sb_lin_t", 50.0, "mm", "source", "D-121: the supply box's 50 mm linings on its two end walls, from Z 1795 to the top (CEILING)"),
    # ---- the intake riser (CEILING's 611501)
    ("rs_x0", 959.0, "mm", "source", "FRONT's DR STEP (#313, 541fe7f; the same at c65a3fa): the riser space X 959 to 1098, 3 mm right with the glue line"),
    ("rs_w", 139.0, "mm", "source", "AIR's model: the riser 139 wide"),
    ("rs_y0", -803.0, "mm", "source", "AIR's model (follow-up): the riser Y -803 to -653"),
    ("rs_d", 150.0, "mm", "source", "AIR's model (follow-up, the air report's D-130 table): the riser 150 deep"),
    ("rs_z1", 1386.0, "mm", "confirmed", "the Lead's ruling 2026-11-01: the riser cut 60 mm shorter, its top at Z 1386 (was 1445), so the lower duct's walls widen at 20 degrees or less; CEILING cuts it in AIR's next rebuild"),
    ("rs_t", 1.0, "mm", "confirmed", "D-61: 1 mm galvanised steel riser"),
    # ---- the lower transition (riser to box): two halves, 1 mm galvanised steel
    ("lt_t", 1.0, "mm", "confirmed", "the Lead's ruling 2026-11-01: the lower duct in 1 mm galvanised steel, as the riser"),
    ("lt_r", 1.0, "mm", "confirmed", "the Lead's ruling 2026-11-01: inside radius = thickness"),
    ("lt_cr", 0.5, "mm", "assumption", "the slip clearance each side, the lower duct's collar inside the riser's top"),
    ("lt_cb", 0.5, "mm", "assumption", "the slip clearance each side, the lower duct's collar inside the box's bottom"),
    ("lt_hb", 25.0, "mm", "assumption", "the collar's depth into the riser: rivets at mid depth, 12.5 from both edges"),
    ("lt_ht", 20.0, "mm", "assumption", "the collar's depth into the box: rivets 10 above the box's edge and 10 under the collar's top, which stays 8 under the lip angle's rivet line (Z about 1678) and 28 under the bulkhead"),
    ("lt_throat_r", 100.0, "mm", "confirmed", "the Lead's ruling 2026-11-01: the riser kink rounded, step-bent to about R 100 (the air side of the left wrapper)"),
    ("lt_throat_n", 4.0, "", "assumption", "bends in the rounded throat: three of about 14.4 degrees, 25 mm apart, so each step's flange takes a rivet, and a last one of lt_throat_last"),
    ("lt_throat_last", 9.0, "deg", "assumption", "the throat's last bend: small, so the last step (where the slant starts, the cheeks' first kink and the right wall's kink) sits high enough for the walls to widen at 19.9 degrees (four equal bends give 20.2)"),
    ("lt_div_max", 20.0, "deg", "confirmed", "the Lead's ruling 2026-11-01: the slant's two walls at most 20 degrees apart"),
    ("lt_lean", 13.5, "mm", "calculation", "the cheeks' lean between their two kinks, the same front and back so the two cheeks are one part: the riser's centre Y -728 to the box's -741.5"),
    ("lt_flange_w", 17.0, "mm", "calculation", "the wrappers' flanges onto the cheeks: each rivet 8.5 from the fold line (the cheek's edge) and 8.5 from the flange's free edge, 2 hole diameters both ways (the mechanical checks' edge rule)"),
    ("flange_hole_in", 8.5, "mm", "calculation", "a flange rivet's centre from its fold line: 2 x the 4.1 hole from the cheek's edge"),
    ("lt_relief", 3.0, "mm", "assumption", "corner relief: each fold stops this far from a corner where two folds meet (more than r + t)"),
    ("riser_chamfer", 8.0, "mm", "confirmed", "the Lead's ruling 2026-11-01: the riser's front-right upright edge chamfered 8 x 8 (6.8 from DR's skin)"),
    ("lt_corner_r", 10.0, "mm", "calculation", "the right wrapper's upright web's front fold, inside radius 10: its outside round keeps 0.7 mm inside the riser's chamfer with the collar's 0.5 slip (R 9.5 would leave 0.02), and 8.6 mm off DR's skin above the riser"),
    ("lt_corner_trim", 11.0, "mm", "calculation", "the cheeks' right edge beside that fold stops on its tangent, 11 mm in (r + t): inside the riser's chamfer and 10.7 mm off DR's skin"),
    ("lt_corner_hole_in", 19.5, "mm", "calculation", "that web's flange rivets: 19.5 from the fold line, so 8.5 from the trimmed cheek edge (2 hole diameters) and the head (12 across) 10.5 mm off DR's skin"),
    ("lt_corner_flange_w", 28.0, "mm", "calculation", "that web's flanges: 19.5 + 8.5 to the free edge (2 hole diameters)"),
    ("skin_nx", -0.66855, "", "source", "FRONT's DR STEP (#313, c65a3fa): the skin facet's inside face beside the riser (351301), its normal into the block"),
    ("skin_ny", 0.743668, "", "source", "FRONT's DR STEP (#313, c65a3fa): the same normal"),
    ("skin_px", 1247.994, "mm", "source", "FRONT's DR STEP (#313, c65a3fa): a point on that face"),
    ("skin_py", -669.769, "mm", "source", "FRONT's DR STEP (#313, c65a3fa): a point on that face"),
    ("skin_rule", 4.0, "mm", "confirmed", "the Lead's 4 mm rule to DR's skin (2026-11-01: closer risks a rattle)"),
    # ---- the upper transition (box to column): a shell and a floor, 2 mm aluminium, with turning vanes
    ("ut_t", 2.0, "mm", "confirmed", "the Lead's ruling 2026-11-01: the upper duct in 2 mm aluminium (the air report's breakout figure)"),
    ("ut_r", 2.0, "mm", "confirmed", "the Lead's ruling 2026-11-01: inside radius = thickness"),
    ("ut_c", 0.5, "mm", "assumption", "the skirts' clearance outside the box's walls"),
    ("ut_skirt_z", 1932.0, "mm", "calculation", "the front and left skirts' bottom edge: 8.5 mm from the cross tube over the box (352322, top Z 1923.86, back face Y -824), the 6 mm rule"),
    ("ut_roof_z", 2112.0, "mm", "calculation", "the roof's outer face: an 8 mm gasket face above the window's top (2102) on the back wall, and 8 mm under DR's band tube (352316, Z 2120), the 6 mm rule"),
    ("ut_back_y", -646.5, "mm", "source", "the back wall's outer face on DR's frame face (FRONT's DR STEP, #313, 541fe7f; the same at c65a3fa): the gasket 848013 (4.0) squeezes to the panel's 2.36 mm"),
    ("ut_right_x", 1158.0, "mm", "calculation", "the right wall's outer face: 6 mm from DR's bolt-line tube (352308, X 1164)"),
    ("bolt_tube_x0", 1164.0, "mm", "source", "FRONT's DR STEP (#313, 541fe7f; the same at c65a3fa): DR's bolt-line tube 352308's left face (its front face on the back ring's, Y -666.5)"),
    ("ut_floor_z", 1881.0, "mm", "calculation", "the floor's outer face: 14 mm under the window (Z 1895), room for the gasket face"),
    ("win_x0", 961.0, "mm", "confirmed", "the Lead's ruling 2026-11-01: DR's panel opening X 961 to 1146, Z 1895 to 2102 (FRONT's next DR run); the duct's outlet window the same"),
    ("win_x1", 1146.0, "mm", "confirmed", "the Lead's ruling 2026-11-01"),
    ("win_z0", 1895.0, "mm", "confirmed", "the Lead's ruling 2026-11-01"),
    ("win_z1", 2102.0, "mm", "confirmed", "the Lead's ruling 2026-11-01"),
    ("fac_x", 1023.5, "mm", "calculation", "the facet wall starts on the front wall's line here: 6.3 mm from the front ring's facet side tube (352302's corner at X 1029.7, Y -824) and 14.3 mm inside C04's face (352317, parallel to it)"),
    ("c04_ax", 1049.7, "mm", "source", "FRONT's DR STEP (#313, 541fe7f; the same at c65a3fa): C04's inner face, front end X (the glue line moved it 3 mm in)"),
    ("c04_ay", -817.11, "mm", "source", "FRONT's DR STEP (#313, 541fe7f; the same at c65a3fa): C04's inner face, front end Y"),
    ("c04_bx", 1217.23, "mm", "source", "FRONT's DR STEP (#313, 541fe7f; the same at c65a3fa): C04's inner face, back end X"),
    ("c04_by", -666.5, "mm", "source", "FRONT's DR STEP (#313, 541fe7f; the same at c65a3fa): C04's inner face, back end Y"),
    ("ramp_y", -770.0, "mm", "assumption", "the floor's ramp beside the box runs from the front wall's bottom edge (Z 1932) down to the floor here"),
    ("ut_tab_w", 17.0, "mm", "calculation", "corner tabs and floor flanges: a rivet 8.5 from the fold line and 8.5 from the free edge"),
    ("vane_t", 1.0, "mm", "source", "the air report's vane sets: 1 mm aluminium (calc.py VANES_KG)"),
    ("vane_r", 32.0, "mm", "assumption", "the vanes' inside radius: about the spacing between vanes along the turn"),
    ("vane1_n", 3.0, "", "assumption", "vanes in the turn from the box's top to the run across, along its mitre from the outlet's left edge under the roof (X 733, Z 2110) to its right edge at the box's top (X 927, Z 1950); three keep every vane's curve above the box (four put the lowest 7 mm into it)"),
    ("vane_lead", 6.0, "mm", "assumption", "a vane's straight lead before its curve"),
    ("vane_leg", 40.0, "mm", "assumption", "a vane's straight leg after its curve, which carries its two end tabs"),
    ("vane_tab", 17.0, "mm", "calculation", "a vane tab: its rivet 8.5 from the fold line and the free edge"),
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

# part numbers from Control (D-63: Control allocates; Control's post of 2026-11-01 in its group, all 9 free on main,
# in every open PR, on recent branches and in the chats); the files carry them
NUMBERS = {
    "LT": "610403",      # AIR - RISER TRANSITION (assembly, in place of 618103)
    "LT-L": "611701",    # AIR - RISER TRANSITION - LEFT WRAPPER
    "LT-R": "611702",    # AIR - RISER TRANSITION - RIGHT WRAPPER
    "LT-C": "611703",    # AIR - RISER TRANSITION - CHEEK (2 per pod)
    "UT": "610404",      # AIR - SUPPLY TRANSITION (assembly, in place of 618102)
    "UT-S": "611801",    # AIR - SUPPLY TRANSITION - SHELL
    "UT-F": "611802",    # AIR - SUPPLY TRANSITION - FLOOR
    "UT-VA": "611803",   # AIR - SUPPLY TRANSITION - VANE - OVER THE BOX (3 per pod)
    "UT-VB": "611804",   # AIR - SUPPLY TRANSITION - VANE - BESIDE THE BOX (2 per pod)
}
