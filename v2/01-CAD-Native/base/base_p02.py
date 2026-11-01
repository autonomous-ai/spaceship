"""BASE revision P02: the rest of the base, loaded by base_build.py with --arg rev=P02.

Executed inside base_build.py's namespace (it uses its helpers and adds to its
PARTS, BASE_PARAMS, MATERIALS, steps and hardware). Adds:

  right side band 110102 / 111102 (mirror of the left, keyholes at BR)
  floor panel F2 110402 / 111402 / 111502 with the upper half-lap and the air
      column's two locator spigots 111801 (CEILING's outline, PM 2026-10-31)
  door threshold 111701, 13 mm (D-72)
  front band pieces: FL1 111104, FL2 111105 (DL's two facets), FL2's door-side
      end cap 111110, FR1 111106 (under the fixed glass)
  the DR intake (D-62): mesh 111107, support rail 111108, closing plate 111109

The front keys 111212 to 111214 are the Joints Engineer's (J-BASE-02, HOLD-14);
they are added when drawn. Fixings of the threshold and the closing plate HOLD.
"""

P02_PARAMS = [
    ("lap_clear", "1 mm", "mm", "assumption", "clearance past F1's lap end in F2's rebate"),
    ("loc_s1_x", "989 mm", "mm", "source", "air column locator spigot S1, round hole (CEILING, PM 2026-10-31)"),
    ("loc_s1_y", "-605 mm", "mm", "source", "S1 Y (CEILING)"),
    ("loc_s2_x", "1126 mm", "mm", "source", "air column locator spigot S2, slot (CEILING)"),
    ("loc_s2_y", "-337 mm", "mm", "source", "S2 Y (CEILING)"),
    ("loc_d", "8 mm", "mm", "source", "locator spigot Ø8, 8 proud (CEILING; PM approved the factory-fitted head-from-below)"),
    ("loc_proud", "8 mm", "mm", "source", "spigot height above the floor top (CEILING)"),
    ("loc_head_d", "16 mm", "mm", "assumption", "spigot head under the ply, in a cut-out in the bonded mat"),
    ("loc_head_t", "2 mm", "mm", "assumption", "spigot head thickness, inside the 3 mm mat"),
    ("loc_mat_cut", "17 mm", "mm", "assumption", "cut-out in F2's mat around each spigot head"),
    ("th_up", "6 mm", "mm", "confirmed", "threshold's upright at the toe (D-72: up to 6 mm upright, then 1:2)"),
    ("th_land", "30 mm", "mm", "assumption", "flat land under the door's drop seal, centred on the glass line"),
    ("th_wall", "2 mm", "mm", "assumption", "threshold extrusion's wall"),
    ("mesh_front", "105 mm", "mm", "confirmed", "DR intake mesh: 105 on the front and 266 on the facet (D-62)"),
    ("mesh_t", "2 mm", "mm", "assumption", "intake mesh thickness (expanded aluminium, 80 % free, black; product HOLD)"),
    ("rail_w", "20 mm", "mm", "assumption", "DR support rail flange under DR's bottom edge"),
    ("rail_h", "30 mm", "mm", "assumption", "DR support rail leg"),
    ("rail_t", "2 mm", "mm", "assumption", "DR support rail thickness (aluminium angle)"),
    ("rail_set", "20 mm", "mm", "assumption", "rail set back behind the mesh, so it blocks none of the mesh face"),
    ("cp_t", "2 mm", "mm", "assumption", "closing plate between the intake space and the pod (D-62)"),
    ("fr_stub", "32 mm", "mm", "confirmed",
     "the intake's band stub left of the mesh, carrying the inline key 111211 (30 long since the Joints Engineer's change of 2026-11-01) "
     "behind no mesh, with 2 to spare (PM ruling 2026-11-01: the joint moves left of the mesh)"),
    ("x_fr_joint", "pod_w / 2 - dr_xc - mesh_front - fr_stub", "mm", "confirmed",
     "the FR1 / intake joint, X 915 (PM rulings 2026-11-01: X 920 for the 25 mm key, then X 915 for the 30 mm key): "
     "FR1 runs X 218.5 to here; the intake from here, its mesh from X 947"),
    # fixed glass sill on FR1 (FRONT's answer 2026-11-01; PM: the U-channel ships fitted on it)
    ("ch_w", "15 mm", "mm", "source", "FRONT: the glass's bottom U-channel, Bohle 15 x 15 x 1.5, Y -706.5 to -691.5 (centred on glass_y)"),
    ("ch_h", "15 mm", "mm", "source", "FRONT: channel underside Z 95, top Z 110 (the band top, the glass's visible bottom line)"),
    ("sl_t", "2 mm", "mm", "assumption", "sill sheet: aluminium 2 mm, bent, black anodised AA20 (D-67 look)"),
    ("sl_flange", "40 mm", "mm", "assumption", "sill's fixing flange down FR1's inner face (blind rivets, HOLD)"),
    ("sl_x1", "965 mm", "mm", "source", "FRONT: the channel's underside runs to X 964.1, so the sill reaches X 965"),
    ("ch_screw_x1", "269.4 mm", "mm", "source", "FRONT's channel holes (F-368004-02): the first at X 269.4"),
    ("ch_screw_p", "214.9 mm", "mm", "source", "FRONT's pitch for the first 3 channel holes: X 269.4, 484.3, 699.2"),
    ("ch_screw_x4", "905 mm", "mm", "confirmed",
     "the last channel screw at X 905: on FR1's sill seat, 2 hole diameters from FR1's end at x_fr_joint (joints register J-FRONT-04, "
     "the Lead 2026-11-01: X 905 or less; FRONT's 914.1 moves)"),
    ("ch_rn_hole", "5 mm", "mm", "assumption", "hole for the flush-head M3 rivnut in the sill seat (product with the Joints Engineer, HOLD)"),
]

P02_PARTS = {
    "band_r": ("110102", "BASE - BAND ASSY - SIDE - RH", "Viền chân nhôm - cạnh phải (cụm)", "HS", None),
    "band_r_tube": ("111102", "BASE - BAND TUBE - SIDE - RH", "Viền chân nhôm 100x40 - cạnh phải", "MP", "band_r"),
    "floor_assy2": ("110402", "BASE - FLOOR PANEL ASSY - F2", "Tấm sàn F2 (cụm dán)", "BS", None),
    "floor_f2": ("111402", "BASE - FLOOR PANEL - F2", "Tấm sàn mỏng - F2", "MP", "floor_assy2"),
    "mat_f2": ("111502", "BASE - FLOOR FOAM - F2 - CLOSED-CELL 3 MM", "Tấm lót sàn F2 - xốp kín 3 mm", "MP",
               "floor_assy2"),
    # hardware-like: its holding copy sits at the root (deleted in step 7); the real copies go in F2's assembly
    "loc_spigot": ("111801", "BASE - LOCATOR SPIGOT - AIR COLUMN - D8", "Chốt định vị cột gió", "MP", None),
    "threshold": ("111701", "BASE - DOOR THRESHOLD - 13 MM", "Ngưỡng cửa 13 mm", "MP", None),
    "front_l": ("110104", "BASE - BAND ASSY - FRONT - LH", "Viền chân trước - trái (cụm)", "HS", None),
    "fl1": ("111104", "BASE - BAND TUBE - FRONT - FACET 1 - LH", "Viền chân trước - mặt vát 1", "MP", "front_l"),
    "fl2": ("111105", "BASE - BAND TUBE - FRONT - FACET 2 - LH", "Viền chân trước - mặt vát 2", "MP", "front_l"),
    "cap_l": ("111110", "BASE - BAND END CAP - DOOR SIDE - LH", "Nắp đầu viền chân - phía cửa", "MP", "front_l"),
    "front_r": ("110106", "BASE - BAND ASSY - FRONT - FIXED GLASS", "Viền chân trước - dưới kính cố định (cụm)", "HS", None),
    "fr1": ("111106", "BASE - BAND TUBE - FRONT - FIXED GLASS", "Viền chân trước - dưới kính cố định", "MP", "front_r"),
    "intake": ("110107", "BASE - INTAKE ASSY - DR", "Cụm cửa gió dưới khối phải", "HS", None),
    "mesh": ("111107", "BASE - INTAKE MESH - DR", "Lưới cửa gió", "MP", "intake"),
    "rail": ("111108", "BASE - INTAKE SUPPORT RAIL - DR", "Thanh đỡ khối phải", "MP", "intake"),
    "cplate": ("111109", "BASE - INTAKE CLOSING PLATE - DR", "Tấm ngăn cửa gió", "MP", "intake"),
    "sill": ("111301", "BASE - SILL - FIXED GLASS", "Bậu đỡ kính cố định", "MP", "front_r"),
}

# plan points used by several parts (expressions), from the skeleton's facet parameters
XL_, XR_ = "-pod_w / 2", "pod_w / 2"
A1, B1 = "dl_x2", "(dl_y2 - dl_y1)"
A2, B2 = "(dl_x3 - dl_x2)", "(dl_y3 - dl_y2)"
L1 = "sqrt(%s ^ 2 + %s ^ 2)" % (A1, B1)
L2 = "sqrt(%s ^ 2 + %s ^ 2)" % (A2, B2)
DOT = "((%s * %s + %s * %s) / (%s * %s))" % (B1, B2, A1, A2, L1, L2)
IL2_X = "(%s + dl_x2 + band_t * (%s / %s + %s / %s) / (1 + %s))" % (XL_, B1, L1, B2, L2, DOT)
IL2_Y = "(-dl_y2 + band_t * (%s / %s + %s / %s) / (1 + %s))" % (A1, L1, A2, L2, DOT)
# FL2's inner line at X = -pod_w/2 + dl_x3 (its square end), and at DL's door face (cap)
Y_FL2_IN_END = "(%s - (%s + dl_x3 - %s) * %s / %s)" % (IL2_Y, XL_, IL2_X, B2, A2)
Y_CAP_IN = "(%s - (%s + dl_w - %s) * %s / %s)" % (IL2_Y, XL_, IL2_X, B2, A2)
DXR, DYR = "dr_xc", "(pod_d / 2 - dr_yc)"
LR = "sqrt(%s ^ 2 + %s ^ 2)" % (DXR, DYR)
Y_MITRE_IN_R = "(-dr_yc + band_t * (%s - %s) / %s)" % (LR, DYR, DXR)
F_FRONT = "(%s / (%s + %s))" % (DYR, LR, DXR)       # inner-corner shift per unit offset, front mitre (0.383)
F_SIDE = "(%s / (%s + %s))" % (DXR, LR, DYR)        # same at the side band's mitre (0.446)
X_MESH0 = "(%s - dr_xc - mesh_front)" % XR_          # the mesh's left end, X 947
X_FR0 = "(%s + fix_xbl)" % XL_                       # FR1's left end at the door opening, X 218
# FR1 / intake joint (PM ruling 2026-11-01): 27 mm left of the mesh, so the inline key 111211 sits in
# a short band stub of the intake under the glass's right end and no key sits behind the mesh
X_FR_JOINT = "x_fr_joint"


BATCH1 = ("band_r", "band_r_tube", "floor_assy2", "floor_f2", "mat_f2", "loc_spigot", "threshold",
          "front_r", "fr1", "sill")


P02_BATCH_KEYS = BATCH1


def p02_setup(keys=BATCH1):
    """Adds the P02 parameters and the parts of this batch (keys) to base_build's tables."""
    global SUB_DESIGNS, HOLDING_KEYS, WITH_ASSEMBLY
    BASE_PARAMS.extend(P02_PARAMS)
    if "loc_spigot" in keys:
        HOLDING_KEYS = tuple(HOLDING_KEYS) + ("loc_spigot",)
    PARTS.update({k: P02_PARTS[k] for k in keys})
    mats = {k: ("Aluminum", None, None) for k in ("band_r_tube", "fl1", "fl2", "cap_l", "fr1", "rail",
                                                   "cplate", "threshold", "sill")}
    mats.update({"floor_f2": MATERIALS["floor_f1"], "mat_f2": MATERIALS["mat_f1"], "loc_spigot": ("Steel", None, None),
                 "mesh": ("Aluminum", "Expanded mesh 80% free, 540 kg/m3 (ASSUMPTION)", 540.0)})
    MATERIALS.update({k: m for k, m in mats.items() if k in keys})
    SUB_DESIGNS = tuple(SUB_DESIGNS) + tuple(k for k in ("band_r", "front_r", "floor_assy2") if k in keys)
    if "band_r_tube" in keys:     # its back end carries a corner key (D-129): its part design follows each assembly save, as 111101's
        WITH_ASSEMBLY = tuple(WITH_ASSEMBLY) + ("band_r_tube",)
    PART_BUILDS.update({k: fns for k, fns in (
        ("band_r_tube", ("step_p02_band_r",)), ("fr1", ("step_p02_fr1",)), ("sill", ("step_p02_sill",)),
        ("floor_f2", ("floor_panel_f2",)), ("loc_spigot", ("loc_spigot_part",)), ("threshold", ("step_p02_threshold",)))
        if k in keys})


def tube_from_plan(design, key, label, outline, bore_rect):
    """A 100 x 40 band tube from a plan outline (any angle), hollowed by a bore
    polygon (inner offset of the long faces, running past the ends)."""
    return band_tube(design, key, label, outline, bore_rect, "plan outline")


def step_p02_band_r(design):
    outline = [P(design, XR_, YB), P(design, XR_, "-dr_yc"),
               P(design, "%s - band_t" % XR_, Y_MITRE_IN_R), P(design, "%s - band_t" % XR_, YB)]
    bore = [P(design, "%s - band_t + band_wall" % XR_, "-dr_yc - 20 mm"), P(design, "%s - band_wall" % XR_, "-dr_yc - 20 mm"),
            P(design, "%s - band_wall" % XR_, "%s + 20 mm" % YB), P(design, "%s - band_t + band_wall" % XR_, "%s + 20 mm" % YB)]
    band_tube(design, "band_r_tube", "SIDE RH", outline, bore, "length along Y")
    v = lambda e: ev(design, e)  # noqa: E731
    back_key_holes(design, "band_r_tube", 1, "BR")            # D-129: the back right key sits in this band's back end
    c = find_comp(design, "band_r_tube")
    top = offset_plane(c, "xy", "wall_z0", v("wall_z0"), "PLANE - BAND TOP Z = wall_z0")
    bot = [p for p in c.constructionPlanes if p.name == "PLANE - BAND BOTTOM Z = glide_h"][0]
    down, up = Z.copy(), Z.copy()
    down.scaleBy(-1)
    xb = "%s - jb_x" % XR_
    y1b = "base_side_y0 + jb_e"                     # skeleton v4 named start (R1 mirrors L1)
    hole(design, "band_r_tube", top, "J-BASE-01 RIVNUT - R1", (v(xb), v(y1b), v("wall_z0")),
         [(X, xb), (Y, y1b)], "rn_hole", "band_wall", down, ("yConstructionAxis", "jb_n", "side_l - 2 * jb_e"))
    y1s = "base_side_y0 + sp_e"
    hole(design, "band_r_tube", top, "SPIGOT RIVNUT - R1", (v(xb), v(y1s), v("wall_z0")),
         [(X, xb), (Y, y1s)], "rn_hole", "band_wall", down, ("yConstructionAxis", "2", "side_l - 2 * sp_e"))
    # J-BASE-02: the front corner key 111213 sits in this band's front end (its carrier, joints
    # register PR #99): 2 x Ø7.0 in the bottom wall, 10 from the key's back face (ck_x behind the
    # mitre face's centre), 7.5 either side of the band's centre line
    yk = "(-dr_yc + %s) / 2 + ck_x - ck_e" % Y_MITRE_IN_R
    xk = "%s - band_t / 2 - (ck_y / 2 - ck_e)" % XR_
    hole(design, "band_r_tube", bot, "CORNER KEY FIXING - FR (111213)", (v(xk), v(yk), v("glide_h")),
         [(X, xk), (Y, yk)], "ck_fix_hole", "band_wall", up, ("xConstructionAxis", "2", "ck_y - 2 * ck_e"))
    xg = "%s - band_t / 2 - gl_dx" % XR_
    yg0, gext = "-dr_yc + gl_e_f", "pod_d / 2 - gl_e_b + dr_yc - gl_e_f"
    hole(design, "band_r_tube", top, "GLIDE KEY ACCESS - SIDE RH", (v(xg), v(yg0), v("wall_z0")),
         [(X, xg), (Y, yg0)], "gl_key_hole", "band_wall", down, ("yConstructionAxis", "gl_n_side", gext))
    hole(design, "band_r_tube", bot, "GLIDE NUT - SIDE RH", (v(xg), v(yg0), v("glide_h")),
         [(X, xg), (Y, yg0)], "gl_nut_hole", "band_wall", up, ("yConstructionAxis", "gl_n_side", gext))
    print("P02: right side band built")


def step_p02_front(design):
    # FL1: DL's first facet, from the FL corner mitre to the knee mitre
    fl1 = [P(design, XL_, "-dl_y1"), P(design, "%s + dl_x2" % XL_, "-dl_y2"), P(design, IL2_X, IL2_Y),
           P(design, "%s + band_t" % XL_, Y_MITRE_IN)]
    bore_note = "bore: the tube's inside, 1.5 mm in from each face"
    plan_tube(design, "fl1", "FRONT FACET 1 LH", fl1, bore_note)
    fl2 = [P(design, "%s + dl_x2" % XL_, "-dl_y2"), P(design, "%s + dl_x3" % XL_, "-dl_y3"),
           P(design, "%s + dl_x3" % XL_, Y_FL2_IN_END), P(design, IL2_X, IL2_Y)]
    plan_tube(design, "fl2", "FRONT FACET 2 LH", fl2, bore_note)
    cap = [P(design, "%s + dl_x3" % XL_, "-dl_y3"), P(design, "%s + dl_w" % XL_, "-dl_y3"),
           P(design, "%s + dl_w" % XL_, Y_CAP_IN), P(design, "%s + dl_x3" % XL_, Y_FL2_IN_END)]
    plan_solid(design, "cap_l", "BAND END CAP - DOOR SIDE LH", cap)
    fr1 = [P(design, X_FR0, "-pod_d / 2"), P(design, X_FR_JOINT, "-pod_d / 2"),
           P(design, X_FR_JOINT, "-pod_d / 2 + band_t"), P(design, X_FR0, "-pod_d / 2 + band_t")]
    v = lambda e: ev(design, e)  # noqa: E731
    plan_tube(design, "fr1", "FRONT FIXED GLASS", fr1, bore_note,
              closed_near=(v(X_FR_JOINT), v("-pod_d / 2 + band_t / 2")))
    # FR1 is the keyhole piece of the inline joint (joints register PR #99: the intake carries
    # 111211 in its stub's end and FR1 goes on last, down onto the studs)
    keyholes_x(design, "fr1", X_FR_JOINT, "-pod_d / 2 + band_t / 2", -1, "FR1 END")    # through the end plate
    print("P02: front band pieces built (FL1, FL2 with its cap, FR1 with its keyed end plate)")


def step_p02_fr1(design):
    """FR1 under the fixed glass, X 218.5 to x_fr_joint: a 100 x 40 x 1.5 tube, open at the door
    opening (bought end cap 118003) and closed at the joint by its band_wall end plate, which takes the
    keyholes for the intake's inline key 111211 (FR1 goes on last, down onto the studs). Its glides
    are levelled by turning their base: FR1's top is in view in front of the glass, so it has no key
    holes on top (the glide's spec: spanner flats on the base, HOLD)."""
    v = lambda e: ev(design, e)  # noqa: E731
    fr1 = [P(design, X_FR0, "-pod_d / 2"), P(design, X_FR_JOINT, "-pod_d / 2"),
           P(design, X_FR_JOINT, "-pod_d / 2 + band_t"), P(design, X_FR0, "-pod_d / 2 + band_t")]
    plan_tube(design, "fr1", "FRONT FIXED GLASS", fr1, "", closed_near=(v(X_FR_JOINT), v("-pod_d / 2 + band_t / 2")))
    keyholes_x(design, "fr1", X_FR_JOINT, "-pod_d / 2 + band_t / 2", -1, "FR1 END")    # through the end plate
    c = find_comp(design, "fr1")
    bot = [p for p in c.constructionPlanes if p.name == "PLANE - BAND BOTTOM Z = glide_h"][0]
    up = Z.copy()
    xg0, yg = "%s + gl_e_f" % X_FR0, "-pod_d / 2 + band_t / 2"
    hole(design, "fr1", bot, "GLIDE NUT - FR1", (v(xg0), v(yg), v("glide_h")), [(X, xg0), (Y, yg)],
         "gl_nut_hole", "band_wall", up, ("xConstructionAxis", "2", "%s - %s - 2 * gl_e_f" % (X_FR_JOINT, X_FR0)))
    print("P02: FR1 %s, keyed end plate at X %.1f" % (fmt_box(bbox_mm(single_body(c))), v(X_FR_JOINT)))


def keyholes_x(design, key, x_face_expr, y_expr, into_sign, label):
    """Keyholes for a front joint (Ø12 entry kh_drop below each stud's seat,
    6.5 slot up to it, the second stud st_z2 - st_z1 higher), in an end plate on a
    YZ plane at x_face_expr, centred on Y = y_expr, cut band_wall deep toward
    into_sign * X (into the piece)."""
    v = lambda e: ev(design, e)  # noqa: E731
    c = find_comp(design, key)
    body = c.bRepBodies.item(0)
    pl = offset_plane(c, "yz", x_face_expr, v(x_face_expr), "PLANE - END PLATE (KEYHOLES) - %s" % label)
    z_seat = "glide_h + band_wall + st_z1"
    z_entry = "glide_h + band_wall + st_z1 - kh_drop"
    xf = v(x_face_expr)
    into = X.copy()
    into.scaleBy(into_sign)
    pat = ("zConstructionAxis", "2", "st_z2 - st_z1")
    hole(design, key, pl, "KEYHOLE ENTRY D12 - %s" % label, (xf, v(y_expr), v(z_entry)), [(Y, y_expr), (Z, z_entry)],
         "kh_entry", "band_wall", into, pat)
    hole(design, key, pl, "KEYHOLE SEAT (SLOT END) - %s" % label, (xf, v(y_expr), v(z_seat)), [(Y, y_expr), (Z, z_seat)],
         "kh_slot", "band_wall", into, pat)
    sk = c.sketches.add(pl)
    sk.name = "KEYHOLE SLOT - %s - FROM THE ENTRY UP TO THE SEAT" % label
    half = "kh_slot / 2"
    polygon(design, sk, [P3(design, x_face_expr, "%s - %s" % (y_expr, half), z_entry),
                         P3(design, x_face_expr, "%s + %s" % (y_expr, half), z_entry),
                         P3(design, x_face_expr, "%s + %s" % (y_expr, half), z_seat),
                         P3(design, x_face_expr, "%s - %s" % (y_expr, half), z_seat)], Y, Z)
    check_sketch(sk)
    ei = c.features.extrudeFeatures.createInput(one_profile(sk), adsk.fusion.FeatureOperations.CutFeatureOperation)
    n = pl.geometry.normal
    direc = adsk.fusion.ExtentDirections.PositiveExtentDirection if n.x * into.x > 0 else \
        adsk.fusion.ExtentDirections.NegativeExtentDirection
    ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(vi("band_wall")), direc)
    ei.participantBodies = [body]
    f = c.features.extrudeFeatures.add(ei)
    f.name = "CUT - KEYHOLE SLOT - %s" % label
    coll = adsk.core.ObjectCollection.create()
    coll.add(f)
    pats = c.features.rectangularPatternFeatures
    pin = pats.createInput(coll, c.zConstructionAxis, vi("2"), vi("st_z2 - st_z1"),
                           adsk.fusion.PatternDistanceType.ExtentPatternDistanceType)
    pin.setDirectionTwo(c.xConstructionAxis, vi("1"), vi("1 mm"))
    pats.add(pin).name = "PATTERN - KEYHOLE SLOTS - %s" % label


def plan_tube(design, key, label, outline, _note, closed_near=None):
    """Tube from a plan quadrilateral: outside prism, then shelled to band_wall
    with its end faces removed (open ends). closed_near = (x, y) mm keeps the end
    face nearest that point: it stays as a band_wall end plate (the 1.5 mm end cap
    that takes a corner key's keyholes, joints register J-BASE-02)."""
    comp = find_comp(design, key)
    plane = offset_plane(comp, "xy", "glide_h", ev(design, "glide_h"), "PLANE - BAND BOTTOM Z = glide_h")
    sk = comp.sketches.add(plane)
    sk.name = "PLAN - %s - OUTLINE" % label
    polygon(design, sk, outline, X, Y)
    check_sketch(sk)
    f = extrude(comp, one_profile(sk), "band_h", "EXTRUDE - %s - TUBE OUTSIDE" % label)
    body = f.bodies.item(0)
    body.name = "%s - TUBE" % PARTS[key][1]
    # the bore: shell the prism's side faces (2 long faces and open ends)
    faces = adsk.core.ObjectCollection.create()
    top_face = max(body.faces, key=lambda fc: fc.boundingBox.maxPoint.z)
    bot_face = min(body.faces, key=lambda fc: fc.boundingBox.minPoint.z)
    ends = [fc for fc in body.faces if fc != top_face and fc != bot_face and
            fc.area * 100.0 < (ev(design, "band_t") + 1.0) * ev(design, "band_h") * 1.2]   # the short faces
    if closed_near:
        def dist(fc):
            c = fc.boundingBox
            cx, cy = (c.minPoint.x + c.maxPoint.x) * 5.0, (c.minPoint.y + c.maxPoint.y) * 5.0
            return (cx - closed_near[0]) ** 2 + (cy - closed_near[1]) ** 2
        ends.remove(min(ends, key=dist))
    for fc in ends:
        faces.add(fc)
    si = comp.features.shellFeatures.createInput(faces, False)
    si.insideThickness = vi("band_wall")
    sf = comp.features.shellFeatures.add(si)
    sf.name = "SHELL - %s - WALL band_wall, ENDS OPEN" % label
    print("  %-34s %s" % (PARTS[key][1], fmt_box(bbox_mm(single_body(comp)))))


def plan_solid(design, key, label, outline, z0="glide_h", h="band_h"):
    comp = find_comp(design, key)
    plane = offset_plane(comp, "xy", z0, ev(design, z0), "PLANE - Z = %s" % z0)
    sk = comp.sketches.add(plane)
    sk.name = "PLAN - %s" % label
    polygon(design, sk, outline, X, Y)
    check_sketch(sk)
    extrude(comp, one_profile(sk), h, "EXTRUDE - %s" % label)
    b = single_body(comp, PARTS[key][1])
    print("  %-34s %s" % (PARTS[key][1], fmt_box(bbox_mm(b))))
    return b


def f2_outline_exprs():
    x0, x1 = "fl_seam / 2", "%s - band_t - fl_gap" % XR_
    y0, y1 = YW, "%s - band_t - fl_gap" % YB
    xr = "-fl_seam / 2 + lap_w + lap_clear"         # F2's rebate end, past F1's lap
    xt0, xt1, yt = X_FR0, X_MESH0, "-glass_y + ch_w / 2"
    return x0, x1, y0, y1, xr, xt0, xt1, yt


def step_p02_floor_f2(design):
    floor_panel_f2(design)
    foam_f2(design)
    loc_spigot_part(design)
    print("P02: F2 with its rebate and locator holes, its foam, the locator spigot")


def floor_panel_f2(design):
    v = lambda e: ev(design, e)  # noqa: E731
    x0, x1, y0, y1, xr, xt0, xt1, yt = f2_outline_exprs()
    comp = find_comp(design, "floor_f2")
    plane = offset_plane(comp, "xy", "mat_t", v("mat_t"), "PLANE - FLOOR UNDERSIDE Z = mat_t")
    sk = comp.sketches.add(plane)
    sk.name = "PLAN - FLOOR PANEL F2 (WITH THE TAB UNDER THE SILL'S KERB)"
    # the tab: F2 runs forward under the fixed glass, from the door opening to the mesh, to carry
    # the sill's kerb (the glass's load) and floor the strip between the glass line and Y -645
    outline = [P(design, x0, y0), P(design, xt0, y0), P(design, xt0, yt), P(design, xt1, yt), P(design, xt1, y0),
               P(design, x1, y0), P(design, x1, y1), P(design, x0, y1)]
    polygon(design, sk, outline, X, Y)
    check_sketch(sk)
    extrude(comp, one_profile(sk), "fl_t", "EXTRUDE - FLOOR PANEL F2 - PLYWOOD fl_t")
    sk2 = comp.sketches.add(plane)
    sk2.name = "PLAN - F2 SEAM REBATE (LOWER HALF)"
    polygon(design, sk2, [P(design, x0, y0), P(design, xr, y0), P(design, xr, y1), P(design, x0, y1)], X, Y)
    check_sketch(sk2)
    extrude(comp, one_profile(sk2), "fl_t / 2", "CUT - F2 SEAM REBATE - LOWER HALF",
            op=adsk.fusion.FeatureOperations.CutFeatureOperation, body=single_body(comp))
    up = Z.copy()
    for tag, xs, ys in (("S1", "loc_s1_x", "loc_s1_y"), ("S2", "loc_s2_x", "loc_s2_y")):
        hole(design, "floor_f2", plane, "AIR COLUMN LOCATOR SPIGOT %s" % tag, (v(xs), v(ys), v("mat_t")),
             [(X, xs), (Y, ys)], "loc_d", "fl_t", up)
    single_body(comp, "%s - PANEL" % PARTS["floor_f2"][1])


def foam_f2(design):
    v = lambda e: ev(design, e)  # noqa: E731
    x0, x1, y0, y1, xr, xt0, xt1, yt = f2_outline_exprs()
    up = Z.copy()
    comp = find_comp(design, "mat_f2")
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "PLAN - FLOOR MAT F2 (WITH THE TAB)"
    polygon(design, sk, [P(design, xr, y0), P(design, xt0, y0), P(design, xt0, yt), P(design, xt1, yt), P(design, xt1, y0),
                         P(design, x1, y0), P(design, x1, y1), P(design, xr, y1)], X, Y)
    check_sketch(sk)
    extrude(comp, one_profile(sk), "mat_t", "EXTRUDE - FLOOR FOAM F2")
    for tag, xs, ys in (("S1", "loc_s1_x", "loc_s1_y"), ("S2", "loc_s2_x", "loc_s2_y")):
        hole(design, "mat_f2", comp.xYConstructionPlane, "CUT-OUT FOR THE SPIGOT HEAD %s" % tag, (v(xs), v(ys), 0.0),
             [(X, xs), (Y, ys)], "loc_mat_cut", "mat_t", up)
    single_body(comp, "%s - SHEET" % PARTS["mat_f2"][1])


def loc_spigot_part(design):
    comp = find_comp(design, "loc_spigot")
    revolve_section(design, comp, "AIR COLUMN LOCATOR SPIGOT", [
        PZ(design, "0 mm", "0 mm"), PZ(design, "loc_head_d / 2", "0 mm"), PZ(design, "loc_head_d / 2", "loc_head_t"),
        PZ(design, "loc_d / 2", "loc_head_t"), PZ(design, "loc_d / 2", "loc_head_t + fl_t + loc_proud - 1 mm"),
        PZ(design, "loc_d / 2 - 1 mm", "loc_head_t + fl_t + loc_proud"), PZ(design, "0 mm", "loc_head_t + fl_t + loc_proud")])


def step_p02_threshold(design):
    """13 mm door threshold (D-72): a 6 mm upright at the toe, a 1:2 bevel up to
    thresh_h, a flat land centred on the glass line, then down to the floor top
    at the floor's front edge (level inside). Extruded along X between DL's door
    face and the fixed glass's left edge; two pockets from below keep it light."""
    v = lambda e: ev(design, e)  # noqa: E731
    comp = find_comp(design, "threshold")
    x0 = "%s + dl_w" % XL_
    pl = offset_plane(comp, "yz", x0, v(x0), "PLANE - THRESHOLD LEFT END")
    ytoe = "-glass_y - th_land / 2 - 2 * (thresh_h - th_up)"
    ybev = "-glass_y - th_land / 2"
    yland = "-glass_y + th_land / 2"
    xv = v(x0)
    def pt(ey, ez):
        return (ey, ez, (xv, v(ey), v(ez)))
    sk = comp.sketches.add(pl)
    sk.name = "SECTION - THRESHOLD 13 MM"
    polygon(design, sk, [pt(ytoe, "0 mm"), pt(ytoe, "th_up"), pt(ybev, "thresh_h"), pt(yland, "thresh_h"),
                         pt(YW, "floor_top"), pt(YW, "0 mm")], Y, Z)
    check_sketch(sk)
    ei = comp.features.extrudeFeatures.createInput(one_profile(sk), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    n = pl.geometry.normal
    direc = adsk.fusion.ExtentDirections.PositiveExtentDirection if n.x > 0 else \
        adsk.fusion.ExtentDirections.NegativeExtentDirection
    ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(vi("fix_xbl - dl_w")), direc)
    f = comp.features.extrudeFeatures.add(ei)
    f.name = "EXTRUDE - THRESHOLD - LENGTH fix_xbl - dl_w"
    body = single_body(comp, PARTS["threshold"][1])
    yb1 = "%s + th_wall" % ytoe
    yb2 = "%s - th_wall / 2" % ybev
    yb3 = "%s + th_wall / 2" % ybev
    yb4 = "%s - th_wall" % YW
    # two pockets from below, each from its own one-rectangle sketch
    for tag, pts in (("TOE", [pt(yb1, "0 mm"), pt(yb2, "0 mm"), pt(yb2, "th_up - th_wall"), pt(yb1, "th_up - th_wall")]),
                     ("LAND", [pt(yb3, "0 mm"), pt(yb4, "0 mm"), pt(yb4, "floor_top - th_wall"),
                               pt(yb3, "floor_top - th_wall")])):
        skp = comp.sketches.add(pl)
        skp.name = "SECTION - THRESHOLD POCKET - %s" % tag
        polygon(design, skp, pts, Y, Z)
        check_sketch(skp)
        ci = comp.features.extrudeFeatures.createInput(one_profile(skp), adsk.fusion.FeatureOperations.CutFeatureOperation)
        ci.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(vi("fix_xbl - dl_w")), direc)
        ci.participantBodies = [body]
        comp.features.extrudeFeatures.add(ci).name = "CUT - THRESHOLD POCKET FROM BELOW - %s" % tag
    print("P02: threshold %s" % fmt_box(bbox_mm(single_body(comp))))


def step_p02_intake(design):
    """DR intake (D-62): the mesh in the band's outline (front 105 + facet), the
    support rail rail_set behind it under DR's bottom edge, and the closing plate
    at the walls' front edge between the intake space and the pod."""
    v = lambda e: ev(design, e)  # noqa: E731
    fx, fy = "%s - dr_xc" % XR_, "-pod_d / 2"                  # the mesh's front corner
    mesh = [P(design, X_MESH0, fy), P(design, fx, fy), P(design, XR_, "-dr_yc"),
            P(design, "%s - mesh_t" % XR_, "-dr_yc + mesh_t * %s" % F_SIDE),
            P(design, "%s - mesh_t * %s" % (fx, F_FRONT), "%s + mesh_t" % fy), P(design, X_MESH0, "%s + mesh_t" % fy)]
    plan_solid(design, "mesh", "INTAKE MESH - DR (FRONT AND FACET)", mesh)
    r0, r1 = "(mesh_t + rail_set)", "(mesh_t + rail_set + rail_w)"
    rail_out = [P(design, X_MESH0, "%s + %s" % (fy, r0)), P(design, "%s - %s * %s" % (fx, r0, F_FRONT), "%s + %s" % (fy, r0)),
                P(design, "%s - %s" % (XR_, r0), "-dr_yc + %s * %s" % (r0, F_SIDE)),
                P(design, "%s - %s" % (XR_, r1), "-dr_yc + %s * %s" % (r1, F_SIDE)),
                P(design, "%s - %s * %s" % (fx, r1, F_FRONT), "%s + %s" % (fy, r1)),
                P(design, X_MESH0, "%s + %s" % (fy, r1))]
    plan_solid(design, "rail", "INTAKE SUPPORT RAIL - DR (FLANGE)", rail_out, z0="wall_z0 - rail_t", h="rail_t")
    cp = [P(design, X_MESH0, "%s - cp_t" % YW), P(design, "%s - band_t" % XR_, "%s - cp_t" % YW),
          P(design, "%s - band_t" % XR_, YW), P(design, X_MESH0, YW)]
    plan_solid(design, "cplate", "INTAKE CLOSING PLATE - DR", cp, z0="mat_t", h="wall_z0 - mat_t")
    print("P02: DR intake: mesh, support rail flange, closing plate")


def step_p02_sill(design):
    """The fixed glass's sill (FRONT's answer and the PM ruling of 2026-11-01): a bent 2 mm
    profile, black AA20, from the door opening's right edge to sl_x1. A flange down FR1's inner
    face (riveted, HOLD), a ledge flush with the band top over to the channel, a drop wall, the
    seat under FRONT's U-channel (Z 93 to 95, 4 flush M3 rivnuts take the channel's screws), and
    a kerb down to F2's front tab, which carries the glass's load (about 280 N) to the floor. The
    channel is screwed on at the factory and ships on the sill with FR1 (PM ruling)."""
    v = lambda e: ev(design, e)  # noqa: E731
    comp = find_comp(design, "sill")
    x0 = X_FR0
    pl = offset_plane(comp, "yz", x0, v(x0), "PLANE - SILL LEFT END (DOOR OPENING)")
    y_fr, y_fl = "-pod_d / 2 + band_t", "-pod_d / 2 + band_t + sl_t"
    y_dw, y_c0 = "-glass_y - ch_w / 2 - sl_t", "-glass_y - ch_w / 2"
    y_c1, y_kb = "-glass_y + ch_w / 2", "-glass_y + ch_w / 2 + sl_t"
    z_top, z_lb = "wall_z0", "wall_z0 - sl_t"
    z_st, z_sb = "wall_z0 - ch_h", "wall_z0 - ch_h - sl_t"
    z_fl, z_kb = "wall_z0 - sl_flange", "floor_top"
    xv = v(x0)

    def pt(ey, ez):
        return (ey, ez, (xv, v(ey), v(ez)))
    sk = comp.sketches.add(pl)
    sk.name = "SECTION - SILL (FLANGE, LEDGE, DROP, SEAT, KERB)"
    polygon(design, sk, [pt(y_fr, z_top), pt(y_c0, z_top), pt(y_c0, z_st), pt(y_kb, z_st), pt(y_kb, z_kb),
                         pt(y_c1, z_kb), pt(y_c1, z_sb), pt(y_dw, z_sb), pt(y_dw, z_lb), pt(y_fl, z_lb),
                         pt(y_fl, z_fl), pt(y_fr, z_fl)], Y, Z)
    check_sketch(sk)
    ei = comp.features.extrudeFeatures.createInput(one_profile(sk), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    n = pl.geometry.normal
    direc = adsk.fusion.ExtentDirections.PositiveExtentDirection if n.x > 0 else \
        adsk.fusion.ExtentDirections.NegativeExtentDirection
    ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(vi("sl_x1 - %s" % x0)), direc)
    f = comp.features.extrudeFeatures.add(ei)
    f.name = "EXTRUDE - SILL - LENGTH sl_x1 - X_FR0"
    single_body(comp, PARTS["sill"][1])
    seat = offset_plane(comp, "xy", z_st, v(z_st), "PLANE - SILL SEAT TOP Z = wall_z0 - ch_h")
    down = Z.copy()
    down.scaleBy(-1)
    hole(design, "sill", seat, "CHANNEL SCREW RIVNUT - M3 FLUSH (HOLD) - 1 TO 3", (v("ch_screw_x1"), v("-glass_y"), v(z_st)),
         [(X, "ch_screw_x1"), (Y, "-glass_y")], "ch_rn_hole", "sl_t", down,
         ("xConstructionAxis", "3", "2 * ch_screw_p"))
    seat4 = offset_plane(comp, "xy", z_st, v(z_st), "PLANE - SILL SEAT TOP (LAST SCREW)")
    hole(design, "sill", seat4, "CHANNEL SCREW RIVNUT - M3 FLUSH (HOLD) - 4", (v("ch_screw_x4"), v("-glass_y"), v(z_st)),
         [(X, "ch_screw_x4"), (Y, "-glass_y")], "ch_rn_hole", "sl_t", down)
    print("P02: sill %s" % fmt_box(bbox_mm(single_body(comp))))


P02_STEPS = [step_p02_band_r, step_p02_fr1, step_p02_sill, step_p02_floor_f2, step_p02_threshold]   # batch 1

# the right side panel's skeleton envelopes join the clash check, as the left ones do (P01)
_skeleton_boxes_p01 = skeleton_boxes


def skeleton_boxes(design):
    v = lambda e: ev(design, e)  # noqa: E731
    out = _skeleton_boxes_p01(design)
    xr, yb, yw, z0 = v(XR_), v(YB), v(YW), v("panel_z0")
    ot, st, ct, sh = v("outer_t"), v("stack_t"), v("cass_t"), v("side_h")
    out += [("skeleton R1", (xr - ot, yw + v("seam_gap"), z0, xr, yb, z0 + sh)),
            ("skeleton R1-CASS", (xr - st, yw, z0, xr - st + ct, yb - st + ct, z0 + sh))]
    return out


EXPECTED_WITH_SKELETON.extend([
    ("838003", "skeleton R1", "rivnut heads sit in clearance holes in the wall's bottom member (WALL)"),
    ("831001", "skeleton R1", "locating spigots enter the wall's bottom tube (WALL)"),
])


def p02_hardware(design):
    """Right band's J-BASE-01 hardware and glides, F2's locator spigots."""
    v = lambda e: ev(design, e)  # noqa: E731
    out = []
    z_top, sw, head = v("wall_z0"), v("sw_t"), v("rn_head_t")
    n, jb_e, sp_e = int(round(v("jb_n"))), v("jb_e"), v("sp_e")
    xb, y0, ln = v("%s - jb_x" % XR_), v("base_side_y0"), v("side_l")
    for i in range(n):
        t = jb_e + i * (ln - 2 * jb_e) / (n - 1)
        out.append(("band_r", "washer", (xb, y0 + t, z_top), None))
        out.append(("band_r", "rivnut", (xb, y0 + t, z_top + sw), None))
    for t in (sp_e, ln - sp_e):
        out.append(("band_r", "rivnut", (xb, y0 + t, z_top), None))
        out.append(("band_r", "pin", (xb, y0 + t, z_top + head), None))
    xg, xd, zd = v("%s - band_t / 2 - gl_dx" % XR_), v("%s - band_t / 2" % XR_), v("glide_h + band_wall")
    yg0, gext = v("-dr_yc + gl_e_f"), v("pod_d / 2 - gl_e_b + dr_yc - gl_e_f")
    ng = int(round(v("gl_n_side")))
    for i in range(ng):
        out.append(("band_r", "glide", (xg, yg0 + i * gext / (ng - 1), 0.0), None))
        out.append(("band_r", "doubler", (xd, yg0 + i * gext / (ng - 1), zd), "z180"))
    for xs, ys in (("loc_s1_x", "loc_s1_y"), ("loc_s2_x", "loc_s2_y")):
        out.append(("floor_assy2", "loc_spigot", (v(xs), v(ys), v("mat_t - loc_head_t")), None))
    # FR1's 2 glides with their doublers, gl_e_f in from each end (clear of the keyed end's last 30 mm)
    yf = v("-pod_d / 2 + band_t / 2")
    for xg in (v("%s + gl_e_f" % X_FR0), v("%s - gl_e_f" % X_FR_JOINT)):
        out.append(("front_r", "glide", (xg, yf, 0.0), None))
        out.append(("front_r", "doubler", (xg, yf, zd), "z-90"))
    return out

def p02_export(design, out):
    """The batch's facts for make_outputs.py: tube cuts, F2's outline and holes, the sill's section
    (for its flat pattern) and length, the threshold's length."""
    v = lambda e: ev(design, e)  # noqa: E731
    keys = PARTS
    if "band_r_tube" in keys:
        yi, yo = v(Y_MITRE_IN_R), v("-dr_yc")
        out["tubes"][PARTS["band_r_tube"][0]] = {
            "section": "100 x 40 x %.1f" % v("band_wall"), "axis": "Y",
            "outer_face_length": round(v(YB) - yo, 2), "inner_face_length": round(v(YB) - yi, 2),
            "front_end": "mitre to the intake's facet piece: %.2f deg from square, long point on the outer face"
                         % math.degrees(math.atan2(yi - yo, v("band_t"))),
            "back_end": "square, flush with the back face: its key 111211 inside and the flat end cap 118003 (D-129)"}
    if "fr1" in keys:
        ln = v("%s - %s" % (X_FR_JOINT, X_FR0))
        out["tubes"][PARTS["fr1"][0]] = {
            "section": "100 x 40 x %.1f" % v("band_wall"), "axis": "X",
            "outer_face_length": round(ln, 2), "inner_face_length": round(ln, 2),
            "front_end": "square at the door opening, for the end cap",
            "back_end": "square at X %.1f, closed by a welded 1.5 end plate with 2 keyholes" % v(X_FR_JOINT)}
    if "floor_f2" in keys:
        x0, x1, y0, y1, xr, xt0, xt1, yt = f2_outline_exprs()
        out["floor_f2"] = {"outline": [[v(x0), v(y0)], [v(xt0), v(y0)], [v(xt0), v(yt)], [v(xt1), v(yt)], [v(xt1), v(y0)],
                                       [v(x1), v(y0)], [v(x1), v(y1)], [v(x0), v(y1)]],
                           "rebate": [v(x0), v(xr)], "rebate_depth": v("fl_t / 2"), "foam_x0": v(xr),
                           "spigots": [[v("loc_s1_x"), v("loc_s1_y")], [v("loc_s2_x"), v("loc_s2_y")]],
                           "spigot_hole": v("loc_d"), "foam_cut": v("loc_mat_cut")}
    if "sill" in keys:
        out["sill"] = {"t": v("sl_t"), "length": round(v("sl_x1 - %s" % X_FR0), 2), "x0": v(X_FR0),
                       "legs_outside": {"flange": v("sl_flange"), "ledge": round(v("(-glass_y - ch_w / 2) - (-pod_d / 2 + band_t)"), 2),
                                        "drop": v("ch_h + sl_t"), "seat": v("ch_w + 2 * sl_t"),
                                        "kerb": round(v("wall_z0 - ch_h - floor_top"), 2)},
                       "screws_x": [v("ch_screw_x1 + %d * ch_screw_p" % i) for i in range(3)] + [v("ch_screw_x4")],
                       "rivnut_hole": v("ch_rn_hole")}
    if "threshold" in keys:
        out["threshold"] = {"length": round(v("fix_xbl - dl_w"), 2), "x0": v("%s + dl_w" % XL_)}
