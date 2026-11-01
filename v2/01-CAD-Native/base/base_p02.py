"""BASE revision P02: the rest of the base, loaded by base_build.py with --arg rev=P02.

Executed inside base_build.py's namespace (it uses its helpers and adds to its
PARTS, BASE_PARAMS, MATERIALS, steps and hardware). Adds:

  right side band 110102 / 111102 (mirror of the left; the back key at BR, D-129)
  front band pieces: FL1 111104, FL2 111105 (DL's two facets), FL2's door-side
      end cap 111110, FR1 111106 (under the fixed glass)
  the DR intake (D-62): mesh 111107, support rail 111108, closing plate 111109

The front keys 111212 to 111214 are the Joints Engineer's (J-BASE-02), placed
by reference. The pod has no floor and no threshold (D-132): people stand on
the room floor, and each band piece's inner face carries the lip seal 118001
(p02_seal_runs). Fixings of the closing plate HOLD.
"""

P02_PARAMS = [
    ("mesh_front", "105 mm", "mm", "confirmed", "DR intake mesh: 105 on the front and 266 on the facet (D-62)"),
    ("mesh_t", "2 mm", "mm", "assumption", "intake mesh thickness (expanded aluminium, 80 % free, black; product HOLD)"),
    ("rail_w", "20 mm", "mm", "assumption", "DR support rail flange under DR's bottom edge"),
    ("rail_h", "30 mm", "mm", "assumption", "DR support rail leg"),
    ("rail_t", "2 mm", "mm", "assumption", "DR support rail thickness (aluminium angle)"),
    ("rail_set", "20 mm", "mm", "assumption", "rail set back behind the mesh, so it blocks none of the mesh face"),
    ("cp_t", "2 mm", "mm", "assumption", "closing plate between the intake space and the pod (D-62)"),
    ("fr_stub", "32 mm", "mm", "confirmed",
     "the intake's band stub left of the mesh, carrying the inline key 111215 (111211's first layout under its own number since D-144; 30 long) "
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
    "seal_r": ("118001", "BASE - BASE SEAL - LIP - ROOM FLOOR - HOLD", "Gioăng môi sát sàn", "PI", "band_r"),
    "seal_fr1": ("118001", "BASE - BASE SEAL - LIP - ROOM FLOOR - HOLD", "Gioăng môi sát sàn", "PI", "front_r"),
    "seal_se": ("118001", "BASE - BASE SEAL - LIP - ROOM FLOOR - HOLD", "Gioăng môi sát sàn", "PI", "front_r"),
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
# FR1 / intake joint (PM ruling 2026-11-01): 27 mm left of the mesh, so the inline key 111215 (D-144) sits in
# a short band stub of the intake under the glass's right end and no key sits behind the mesh
X_FR_JOINT = "x_fr_joint"


BATCH1 = ("band_r", "band_r_tube", "front_r", "fr1", "sill", "seal_r", "seal_fr1", "seal_se")   # F2, its foam and spigots, the threshold went (D-132)


# batch 2: the front-left pieces under DL (with --arg batch2=1; its method sample first: --arg part=fl1)
BATCH2 = ("front_l", "fl1", "fl2", "cap_l")

P02_BATCH_KEYS = BATCH1 + (BATCH2 if ARGS.get("batch2") == "1" else ())


def p02_setup(keys=P02_BATCH_KEYS):
    """Adds the P02 parameters and the parts of this batch (keys) to base_build's tables."""
    global SUB_DESIGNS, WITH_ASSEMBLY
    BASE_PARAMS.extend(P02_PARAMS)
    if "fl1" in keys or "fl2" in keys:
        BASE_PARAMS.extend(front_dl_params())     # DL's spigot points, FRONT's named values (J-FRONT-02)
    PARTS.update({k: P02_PARTS[k] for k in keys})
    mats = {k: ("Aluminum", None, None) for k in ("band_r_tube", "fl1", "fl2", "cap_l", "fr1", "rail", "cplate", "sill")}
    mats.update({"mesh": ("Aluminum", "Expanded mesh 80% free, 540 kg/m3 (ASSUMPTION)", 540.0),
                 "seal_r": MATERIALS["seal_l"], "seal_fr1": MATERIALS["seal_l"], "seal_se": MATERIALS["seal_l"]})
    MATERIALS.update({k: m for k, m in mats.items() if k in keys})
    SUB_DESIGNS = tuple(SUB_DESIGNS) + tuple(k for k in ("band_r", "front_r") if k in keys)
    if "band_r_tube" in keys:     # its back end carries a corner key (D-129): its part design follows each assembly save, as 111101's
        WITH_ASSEMBLY = tuple(WITH_ASSEMBLY) + ("band_r_tube",)
    PART_BUILDS.update({k: fns for k, fns in (
        ("band_r_tube", ("step_p02_band_r",)), ("fr1", ("step_p02_fr1",)), ("sill", ("step_p02_sill",)),
        ("fl1", ("step_p02_fl1",)))
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
    # 111215 in its stub's end, D-144, and FR1 goes on last, down onto the studs)
    keyholes_x(design, "fr1", X_FR_JOINT, "-pod_d / 2 + band_t / 2", -1, "FR1 END")    # through the end plate
    print("P02: front band pieces built (FL1, FL2 with its cap, FR1 with its keyed end plate)")


def step_p02_fr1(design):
    """FR1 under the fixed glass, X 218.5 to x_fr_joint: a 100 x 40 x 1.5 tube, open at the door
    opening (bought end cap 118003) and closed at the joint by its band_wall end plate, which takes the
    keyholes for the intake's inline key 111215 (D-144; FR1 goes on last, down onto the studs). Its glides
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


def step_p02_intake(design):
    """DR intake (D-62): the mesh in the band's outline (front 105 + facet), the
    support rail rail_set behind it under DR's bottom edge, and the closing plate
    at the walls' front edge between the intake space and the pod."""
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
    # down to the band's bottom line: the lip seal under it reaches the room floor (D-132)
    plan_solid(design, "cplate", "INTAKE CLOSING PLATE - DR", cp, z0="glide_h", h="band_h")
    print("P02: DR intake: mesh, support rail flange, closing plate")


def sill_end_plate_pts():
    """The sill's door-end plate outline on the plane X = X_FR0, as (y expr, z expr): the profile's inner faces (kerb,
    seat, drop, ledge, flange) and its bottom edge on the band's bottom line, from FR1's inner face to the kerb. Corners
    2, 4 and 5 meet an inside bend (relieved on the blank, make_outputs.py); corner 3 wraps the drop-to-seat bend."""
    y_fr, y_fl = "-pod_d / 2 + band_t", "-pod_d / 2 + band_t + sl_t"
    y_dw, y_c1 = "-glass_y - ch_w / 2 - sl_t", "-glass_y + ch_w / 2"
    z_lb, z_sb = "wall_z0 - sl_t", "wall_z0 - ch_h - sl_t"
    z_fl, z_kb = "wall_z0 - sl_flange", "glide_h"
    return [(y_fr, z_kb), (y_c1, z_kb), (y_c1, z_sb), (y_dw, z_sb), (y_dw, z_lb), (y_fl, z_lb), (y_fl, z_fl), (y_fr, z_fl)]


def step_p02_sill(design):
    """The fixed glass's sill (FRONT's answer and the PM ruling of 2026-11-01): a bent 2 mm
    profile, black AA20, from the door opening's right edge to sl_x1. A flange down FR1's inner
    face (riveted, HOLD), a ledge flush with the band top over to the channel, a drop wall, the
    seat under FRONT's U-channel (Z 93 to 95, 4 flush M3 rivnuts take the channel's screws), and
    a kerb down to the band's bottom line (D-132: no floor under it now, so the glass's load, about
    280 N, goes into FR1; the seat detail is being settled with FRONT). The channel is screwed on at
    the factory and ships on the sill with FR1 (PM ruling)."""
    v = lambda e: ev(design, e)  # noqa: E731
    comp = find_comp(design, "sill")
    x0 = X_FR0
    pl = offset_plane(comp, "yz", x0, v(x0), "PLANE - SILL LEFT END (DOOR OPENING)")
    y_fr, y_fl = "-pod_d / 2 + band_t", "-pod_d / 2 + band_t + sl_t"
    y_dw, y_c0 = "-glass_y - ch_w / 2 - sl_t", "-glass_y - ch_w / 2"
    y_c1, y_kb = "-glass_y + ch_w / 2", "-glass_y + ch_w / 2 + sl_t"
    z_top, z_lb = "wall_z0", "wall_z0 - sl_t"
    z_st, z_sb = "wall_z0 - ch_h", "wall_z0 - ch_h - sl_t"
    z_fl, z_kb = "wall_z0 - sl_flange", "glide_h"
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
    # the door-end plate (Reviewer 8's P1 on #303; the PM's ruling of 2026-11-01): welded into the sill's door end, it
    # closes the space under the ledge and seat, from FR1's inner face to the kerb and down to the band's bottom line,
    # so the seal line turns this corner: FR1's lip, this plate's lip along its bottom edge to the floor, then FRONT's
    # seal at the kick strip's end. Its outline is the sill's inner faces; one part with the sill (welded, ground flush).
    sk2 = comp.sketches.add(pl)
    sk2.name = "SECTION - SILL DOOR-END PLATE (WELDED IN): FR1'S INNER FACE TO THE KERB, DOWN TO glide_h"
    polygon(design, sk2, [pt(ey, ez) for ey, ez in sill_end_plate_pts()], Y, Z)
    check_sketch(sk2)
    body = single_body(comp)
    # a new body, then combined: an extrude join that only touches the body along faces makes a second body (extrude())
    ej = comp.features.extrudeFeatures.createInput(one_profile(sk2), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ej.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(vi("sl_t")), direc)
    fj = comp.features.extrudeFeatures.add(ej)
    fj.name = "EXTRUDE - SILL DOOR-END PLATE sl_t (WELDED IN)"
    tools = adsk.core.ObjectCollection.create()
    tools.add(fj.bodies.item(0))
    ci = comp.features.combineFeatures.createInput(body, tools)
    ci.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
    ci.isKeepToolBodies = False
    comp.features.combineFeatures.add(ci).name = "COMBINE - SILL DOOR-END PLATE INTO THE SILL (WELDED)"
    single_body(comp, PARTS["sill"][1])
    print("P02: sill %s (its door end closed by the welded plate)" % fmt_box(bbox_mm(single_body(comp))))


P02_STEPS = [step_p02_band_r, step_p02_fr1, step_p02_sill]   # batch 1 (F2 and the threshold went, D-132)

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
    # FR1's 2 glides with their doublers, gl_e_f in from each end (clear of the keyed end's last 30 mm)
    yf = v("-pod_d / 2 + band_t / 2")
    for xg in (v("%s + gl_e_f" % X_FR0), v("%s - gl_e_f" % X_FR_JOINT)):
        out.append(("front_r", "glide", (xg, yf, 0.0), None))
        out.append(("front_r", "doubler", (xg, yf, zd), "z-90"))
    # FR1's open end at the door opening is in view now (no threshold, D-132): the same flat cap as the side bands'
    out.append(("front_r", "cap", (v("%s + cap_t / 2" % X_FR0), yf, v("glide_h")), "z-90"))
    return out


def p02_seal_runs(design):
    """The lip seal's runs on this batch's band pieces (D-132), as seal_runs: the right side band's inner face up to
    the back band's inner face, and FR1's inner face from the door opening to its keyed end (the intake piece's run
    comes with the intake)."""
    v = lambda e: ev(design, e)  # noqa: E731
    runs = []
    xi, yb = "%s - band_t" % XR_, "%s - band_t" % YB
    if "band_r_tube" in PARTS:
        runs.append(("seal_r", "band_r", "X = %.2f (side band RH, inner face)" % v(xi), Y_MITRE_IN_R, yb,
                     [("%s - seal_t" % xi, Y_MITRE_IN_R), (xi, Y_MITRE_IN_R), (xi, yb), ("%s - seal_t" % xi, yb)]))
    if "sill" in PARTS:
        # the sill's door-end plate (Reviewer 8's P1 on #303): its lip runs the closed end's whole bottom edge, from
        # FR1's inner face to the kerb's outer face. Its leg is bonded on the plate's pod side; its envelope there starts
        # where FR1's lip envelope ends (Y -pod_d/2 + band_t + seal_t), so the two only touch. Its fin sits under the
        # plate, flush with the plate's outer face (p02_seal_fins), so FRONT's brush on the kick strip's end closes on
        # one flat face from the floor up and the seal line has no gap at the corner.
        xp, yr, yk = "(%s + sl_t)" % X_FR0, "(-pod_d / 2 + band_t)", "(-glass_y + ch_w / 2)"
        runs.append(("seal_se", "front_r", "X = %.2f (the sill's door-end plate, its bottom edge)" % v(X_FR0), yr,
                     "(%s + sl_t)" % yk,
                     [(xp, "(%s + seal_t)" % yr), ("(%s + seal_t)" % xp, "(%s + seal_t)" % yr), ("(%s + seal_t)" % xp, yk),
                      (xp, yk)]))
    if "fr1" in PARTS:
        # with the sill's door-end plate, FR1's lip starts at the plate's pod side (the plate's lip turns the corner)
        yf, x0 = "-pod_d / 2 + band_t", ("(%s + sl_t)" % X_FR0 if "sill" in PARTS else X_FR0)
        runs.append(("seal_fr1", "front_r", "Y = %.2f (FR1, inner face)" % v(yf), x0, X_FR_JOINT,
                     [(x0, yf), (X_FR_JOINT, yf), (X_FR_JOINT, "%s + seal_t" % yf), (x0, "%s + seal_t" % yf)]))
    return runs


def p02_seal_fins(design):
    """Fins of a lip that reach past its plan envelope, below the band's bottom line only: {run key: plan rectangle}.
    The sill's door-end plate's lip has its fin under the plate (2 mm), flush with the plate's outer face X_FR0, from
    FR1's inner face to the kerb's outer face; it is joined to that run's envelope, from the room floor to glide_h."""
    if "sill" not in PARTS:
        return {}
    xp, yr, yk = "(%s + sl_t)" % X_FR0, "(-pod_d / 2 + band_t)", "(-glass_y + ch_w / 2 + sl_t)"
    return {"seal_se": [(X_FR0, yr), (xp, yr), (xp, yk), (X_FR0, yk)]}

def p02_export(design, out):
    """The batch's facts for make_outputs.py: tube cuts, the sill's section (for its flat pattern) and length."""
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
            "outer_face_length": round(ln - v("band_wall"), 2), "inner_face_length": round(ln - v("band_wall"), 2),
            "front_end": "square at the door opening, closed by the flat end cap 118003 (in view, D-132)",
            "back_end": "square, closed by a welded 1.5 end plate (100 x 40) with 2 keyholes at X %.1f; %.1f over the plate"
                        % (v(X_FR_JOINT), ln)}
    if "sill" in keys:
        out["sill"] = {"t": v("sl_t"), "length": round(v("sl_x1 - %s" % X_FR0), 2), "x0": v(X_FR0),
                       "legs_outside": {"flange": v("sl_flange"), "ledge": round(v("(-glass_y - ch_w / 2) - (-pod_d / 2 + band_t)"), 2),
                                        "drop": v("ch_h + sl_t"), "seat": v("ch_w + 2 * sl_t"),
                                        "kerb": round(v("wall_z0 - ch_h - glide_h"), 2)},
                       "screws_x": [v("ch_screw_x1 + %d * ch_screw_p" % i) for i in range(3)] + [v("ch_screw_x4")],
                       "rivnut_hole": v("ch_rn_hole"),
                       # the welded door-end plate, as cut: u along Y from FR1's inner face, w up from the band's bottom
                       "end_plate": {"outline": [[round(v(ey) - v("-pod_d / 2 + band_t"), 2), round(v(ez) - v("glide_h"), 2)]
                                                 for ey, ez in sill_end_plate_pts()],
                                     "inside_bend_corners": [2, 4, 5]}}


# ---------------------------------------------------------------- batch 2: the front-left pieces under DL

FRONT_DL = "v2/01-CAD-Native/front/dl_block.py"
FRONT_DL_WANT = ("sp_ax", "sp_ay", "sp_bx", "sp_by")


def front_dl_params(prefix="dlf_"):
    """FRONT's named values for DL's two spigots on the band (J-FRONT-02: sp_ax, sp_ay on FL1, sp_bx, sp_by on
    FL2), read from FRONT's DL model with every value they need, so one source drives both models (linked, not
    copied). FRONT's own names get the prefix, as some clash with BASE's (sp_e); skeleton names stay. A name that
    is neither FRONT's nor the skeleton's stops the build."""
    import re
    path = os.path.join(REPO, FRONT_DL)
    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), path)
    # FRONT's list mixes literals with its module's string constants (XL + " + dl_w - ..."): each entry is read
    # on its own, with those constants and nothing else
    consts, own = {}, None
    for node in tree.body:
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1):
            continue
        tgt, val = node.targets[0], node.value
        if isinstance(tgt, ast.Tuple) and isinstance(val, ast.Tuple) and len(tgt.elts) == len(val.elts):
            pairs = list(zip(tgt.elts, val.elts))           # XL, XR = "-pod_w / 2", "pod_w / 2"
        else:
            pairs = [(tgt, val)]
        for t, el in pairs:
            if isinstance(t, ast.Name) and isinstance(el, ast.Constant) and isinstance(el.value, str):
                consts[t.id] = el.value
        if isinstance(tgt, ast.Name):
            if tgt.id == "OWN" and isinstance(node.value, ast.List):
                own = []
                for el in node.value.elts:
                    try:
                        own.append(ast.literal_eval(el))
                    except ValueError:
                        own.append(eval(compile(ast.Expression(el), path, "eval"), {"__builtins__": {}}, dict(consts)))
    if own is None:
        raise RuntimeError("no OWN list in %s" % FRONT_DL)
    rows = {r[0]: r for r in own}
    skel = {r[0] for r in skeleton_params()}
    ident = re.compile(r"[A-Za-z_][A-Za-z_0-9]*")
    funcs = {"sqrt", "abs", "sin", "cos", "tan", "asin", "acos", "atan", "mm", "deg", "rad"}
    order, seen = [], set()

    def visit(n):
        if n in seen:
            return
        seen.add(n)
        for tok in ident.findall(rows[n][1]):
            if tok in rows:
                visit(tok)
            elif tok not in skel and tok not in funcs:
                raise RuntimeError("FRONT's %s uses %s, which is neither FRONT's nor the skeleton's" % (n, tok))
        order.append(n)
    for n in FRONT_DL_WANT:
        visit(n)
    out = []
    for n in order:
        name, expr, unit, status, desc = rows[n][:5]
        expr2 = ident.sub(lambda m: prefix + m.group(0) if m.group(0) in rows else m.group(0), expr)
        out.append((prefix + name, expr2, unit, status, "FRONT's %s in %s: %s" % (n, FRONT_DL, desc)))
    print("  FRONT's DL spigot values linked: %s" % ", ".join(r[0] for r in out))
    return out


# FL1's corner mitre with the left side band and its knee mitre with FL2, in plan (expressions)
D1X, D1Y = "(dl_x2 / %s)" % L1, "(-(dl_y2 - dl_y1) / %s)" % L1          # FL1's direction, corner to knee
P1X, P1Y = "((dl_y2 - dl_y1) / %s)" % L1, D1X                           # Z x D1, to its left
FC_CX, FC_CY = "(%s + band_t / 2)" % XL_, "((-dl_y1 + %s) / 2)" % Y_MITRE_IN     # corner face centre (-1230, -661.03)
FC_KX, FC_KY = "((%s + dl_x2 + %s) / 2)" % (XL_, IL2_X), "((-dl_y2 + %s) / 2)" % IL2_Y   # knee face centre
# a mitre face's width along it: band_t / cos(half the turn), cos(half) = sqrt((1 + cos(turn)) / 2)
W_CORNER = "(band_t / sqrt((1 + (dl_y2 - dl_y1) / %s) / 2))" % L1
W_KNEE = "(band_t / sqrt((1 + %s) / 2))" % DOT


def unit_xy(x, y):
    n = math.hypot(x, y)
    return (x / n, y / n)


def end_face(body, centre_xy, normal_xy, tol=1.0):
    """The planar vertical face whose normal is +-normal_xy and whose plan centre is within tol of centre_xy
    (the outer face of an end plate, not its inner face 1.5 behind)."""
    best = None
    for f in body.faces:
        if f.geometry.surfaceType != adsk.core.SurfaceTypes.PlaneSurfaceType:
            continue
        n = adsk.core.Plane.cast(f.geometry).normal
        if abs(n.z) > 1e-3 or abs(abs(n.x * normal_xy[0] + n.y * normal_xy[1]) - 1.0) > 1e-3:
            continue
        bb = f.boundingBox
        d = math.hypot((bb.minPoint.x + bb.maxPoint.x) * 5.0 - centre_xy[0], (bb.minPoint.y + bb.maxPoint.y) * 5.0 - centre_xy[1])
        if d < tol and (best is None or d < best[0]):
            best = (d, f)
    if best is None:
        raise RuntimeError("no end face near (%.2f, %.2f)" % centre_xy)
    return best[1]


def face_edges(face, z_bottom):
    """The face's straight bottom edge (at Z = z_bottom mm) and its longest vertical edge."""
    bottom = side = None
    for e in face.edges:
        a, b = e.startVertex.geometry, e.endVertex.geometry
        if e.geometry.curveType != adsk.core.Curve3DTypes.Line3DCurveType:
            continue
        if abs(a.z - b.z) < 1e-5 and abs(a.z * 10.0 - z_bottom) < 0.01:
            if bottom is None or e.length > bottom.length:
                bottom = e
        elif abs(a.x - b.x) < 1e-5 and abs(a.y - b.y) < 1e-5:
            if side is None or e.length > side.length:
                side = e
    if bottom is None or side is None:
        raise RuntimeError("end face: no bottom or vertical edge")
    return bottom, side


def keyholes_on_face(design, key, centre_xy, normal_xy, width_expr, label):
    """Keyholes for a front joint in an end plate on a mitred face (J-BASE-02): a Ø12 entry kh_drop below each
    stud's seat and a 6.5 slot up to the seat, on the face's centre line, the second stud st_z2 - st_z1 higher.
    No angles: the holes sit at offsets from the face's bottom edge and one vertical edge (half the face's
    width, width_expr), and the slot is cut from a sketch on the face whose lines are tied to those two edges
    and cut band_wall each way (only the plate is there). Each feature is patterned up Z for the second stud."""
    v = lambda e: ev(design, e)  # noqa: E731
    c = find_comp(design, key)
    body = c.bRepBodies.item(0)
    z_off = {"entry": "band_wall + st_z1 - kh_drop", "seat": "band_wall + st_z1"}
    w_off = "%s / 2" % width_expr
    feats = []
    for part, dia in (("entry", "kh_entry"), ("seat", "kh_slot")):
        face = end_face(body, centre_xy, normal_xy)
        bottom, side = face_edges(face, v("glide_h"))
        before = body.volume
        for default_dir in (True, False):
            hin = c.features.holeFeatures.createSimpleInput(vi(dia))
            pt = p3(centre_xy[0], centre_xy[1], v("glide_h + %s" % z_off[part]))
            if not hin.setPositionByPlaneAndOffsets(face, pt, bottom, vi(z_off[part]), side, vi(w_off)):
                raise RuntimeError("keyhole %s %s: could not place it on the end face" % (part, label))
            hin.setDistanceExtent(vi("band_wall"))
            hin.isDefaultDirection = default_dir
            hin.participantBodies = [body]
            hf = c.features.holeFeatures.add(hin)
            if body.volume < before - 1e-6:
                break
            hf.deleteMe()                 # it went out of the plate, not into it: the other way
            face = end_face(body, centre_xy, normal_xy)
            bottom, side = face_edges(face, v("glide_h"))
        else:
            raise RuntimeError("keyhole %s %s cut nothing either way" % (part, label))
        hf.name = "HOLE - KEYHOLE %s - %s" % ("ENTRY D12" if part == "entry" else "SEAT (SLOT END)", label)
        feats.append(hf)
    face = end_face(body, centre_xy, normal_xy)
    bottom, side = face_edges(face, v("glide_h"))
    # without the face's own edges: a face sketch projects the plate's outline and the holes just cut, and the
    # slot across them made 6 profiles (FL1 sample, 2026-11-01); only the two edges it's tied to are projected
    sk = c.sketches.addWithoutEdges(face)
    sk.name = "KEYHOLE SLOT - %s - FROM THE ENTRY UP TO THE SEAT, ON THE MITRED END PLATE" % label
    pb, ps = sk.project(bottom).item(0), sk.project(side).item(0)
    ux, uy = -normal_xy[1], normal_xy[0]                     # along the face, level
    hw = v("kh_slot") / 2
    ze, zs = v("glide_h + %s" % z_off["entry"]), v("glide_h + %s" % z_off["seat"])
    cx, cy = centre_xy
    q = [(cx - ux * hw, cy - uy * hw, ze), (cx + ux * hw, cy + uy * hw, ze),
         (cx + ux * hw, cy + uy * hw, zs), (cx - ux * hw, cy - uy * hw, zs)]
    sp = [sk.modelToSketchSpace(p3(*pt)) for pt in q]
    lines = sk.sketchCurves.sketchLines
    l0 = lines.addByTwoPoints(sp[0], sp[1])                                  # the slot's bottom
    l1 = lines.addByTwoPoints(l0.endSketchPoint, sp[2])                      # a long side
    l2 = lines.addByTwoPoints(l1.endSketchPoint, sp[3])                      # its top
    l3 = lines.addByTwoPoints(l2.endSketchPoint, l0.startSketchPoint)        # the other long side
    gc = sk.geometricConstraints
    for ln, ref in ((l0, pb), (l2, pb), (l1, ps), (l3, ps)):
        gc.addParallel(ln, ref)
    sd = sk.sketchDimensions
    # the long side nearer the vertical edge sits at w / 2 - kh_slot / 2 from it, the other kh_slot further
    se = side.startVertex.geometry
    near, far = (l1, l3) if math.hypot(q[1][0] - se.x * 10.0, q[1][1] - se.y * 10.0) < \
        math.hypot(q[0][0] - se.x * 10.0, q[0][1] - se.y * 10.0) else (l3, l1)

    def tp(ln):
        g = ln.startSketchPoint.geometry
        return adsk.core.Point3D.create(g.x + 0.3, g.y + 0.3, 0)
    for a, bb, expr in ((pb, l0, z_off["entry"]), (pb, l2, z_off["seat"]), (ps, near, "%s - kh_slot / 2" % w_off),
                        (near, far, "kh_slot")):
        sd.addOffsetDimension(a, bb, tp(bb)).parameter.expression = expr
    check_sketch(sk)
    ei = c.features.extrudeFeatures.createInput(one_profile(sk), adsk.fusion.FeatureOperations.CutFeatureOperation)
    ei.setSymmetricExtent(vi("band_wall"), False)
    ei.participantBodies = [body]
    f = c.features.extrudeFeatures.add(ei)
    f.name = "CUT - KEYHOLE SLOT - %s" % label
    feats.append(f)
    coll = adsk.core.ObjectCollection.create()
    for ft in feats:
        coll.add(ft)
    pats = c.features.rectangularPatternFeatures
    pin = pats.createInput(coll, c.zConstructionAxis, vi("2"), vi("st_z2 - st_z1"),
                           adsk.fusion.PatternDistanceType.ExtentPatternDistanceType)
    pin.setDirectionTwo(c.xConstructionAxis, vi("1"), vi("1 mm"))
    pats.add(pin).name = "PATTERN - KEYHOLES - %s" % label


def keyhole_check(design, key, row_pn, joint, centre_xy, normal_xy):
    """The built keyholes against the Joints Engineer's corner-keys.csv: each round part's axis along the
    face's normal, on the face's centre line, at the entry and seat heights. Returns what is off."""
    v = lambda e: ev(design, e)  # noqa: E731
    with open(os.path.join(REPO, "v2/01-CAD-Native/joints/corner-keys.csv"), encoding="utf-8") as fh:
        r = [x for x in csv.DictReader(fh) if x["part_number"] == row_pn and x["joint"] == joint][0]
    want_c = (float(r["face_centre_x"]), float(r["face_centre_y"]))
    want = {v("kh_entry"): sorted([float(r["keyhole_entry_z_low"]), float(r["keyhole_entry_z_high"])]),
            v("kh_slot"): sorted([float(r["stud_z_low"]), float(r["stud_z_high"])])}
    body = find_comp(design, key).bRepBodies.item(0)
    off = []
    if math.hypot(centre_xy[0] - want_c[0], centre_xy[1] - want_c[1]) >= 0.05:
        off.append("face centre (%.2f, %.2f) vs (%.2f, %.2f)" % (centre_xy + want_c))
    for dia, zs in want.items():
        got = []
        for org, d in holes_of(body, dia):
            if abs(abs(d[0] * normal_xy[0] + d[1] * normal_xy[1]) - 1.0) > 1e-3:
                continue
            # the axis line's distance from the face centre's vertical line, in plan
            dx, dy = org[0] - centre_xy[0], org[1] - centre_xy[1]
            across = abs(-dx * normal_xy[1] + dy * normal_xy[0])
            got.append((round(org[2], 2), round(across, 3)))
        zs_got = sorted({g[0] for g in got})
        if zs_got != [round(z, 2) for z in zs] or any(g[1] >= 0.05 for g in got):
            off.append("Ø%.1f at %s (want Z %s on the centre line)" % (dia, got, zs))
    print("  %s keyholes against corner-keys.csv (%s, %s): %s" % (PARTS[key][0], row_pn, joint, "; ".join(off) or "MATCH"))
    return off


def hole_that_cuts(design, key, plane, label, xyz, dims, dia_expr, depth_expr, want_dir):
    """hole() that checks the hole took material from the part: if it cut nothing (the FL1 sample's knee key
    holes, 2026-11-01), it is taken out and drilled the other way; if that cuts nothing either, the run stops."""
    body = find_comp(design, key).bRepBodies.item(0)
    for d in (want_dir, None):
        if d is None:
            d = want_dir.copy()
            d.scaleBy(-1)
        before = body.volume
        hf = hole(design, key, plane, label, xyz, dims, dia_expr, depth_expr, d)
        body = find_comp(design, key).bRepBodies.item(0)
        if body.volume < before - 1e-6:
            return hf
        hf.deleteMe()
        sk = find_comp(design, key).sketches.itemByName("HOLE POSITION - %s" % label)
        if sk is not None:
            sk.deleteMe()
        print("  %s: cut nothing drilled one way, drilling the other way" % label)
    raise RuntimeError("%s: the hole cuts nothing either way (xyz %s)" % (label, [round(c, 2) for c in xyz]))


def step_p02_fl1(design):
    """FL1 (111104): DL's outer facet piece, from the corner mitre with the left side band to the knee mitre with
    FL2. Its corner end is closed by a 1.5 end plate with the keyholes for the side band's front key 111212; its
    knee end carries the knee key 111214 (2 fixing holes in its bottom wall); its top wall has the rivnut hole for
    DL's round-hole spigot at FRONT's named point (J-FRONT-02). Glides: with the batch (not in this sample)."""
    v = lambda e: ev(design, e)  # noqa: E731
    fl1 = [P(design, XL_, "-dl_y1"), P(design, "%s + dl_x2" % XL_, "-dl_y2"), P(design, IL2_X, IL2_Y),
           P(design, "%s + band_t" % XL_, Y_MITRE_IN)]
    corner = (v(FC_CX), v(FC_CY))
    plan_tube(design, "fl1", "FRONT FACET 1 LH", fl1, "", closed_near=corner)
    n_corner = unit_xy(v(D1X), v(D1Y) - 1.0)          # the corner mitre's normal: side band (0, -1) + FL1's direction
    keyholes_on_face(design, "fl1", corner, n_corner, W_CORNER, "FL1 CORNER (111212)")
    c = find_comp(design, "fl1")
    bot = [p for p in c.constructionPlanes if p.name == "PLANE - BAND BOTTOM Z = glide_h"]
    bot = bot[0] if bot else offset_plane(c, "xy", "glide_h", v("glide_h"), "PLANE - BAND BOTTOM Z = glide_h")
    top = offset_plane(c, "xy", "wall_z0", v("wall_z0"), "PLANE - BAND TOP Z = wall_z0")
    down = Z.copy()
    down.scaleBy(-1)
    # the knee key 111214's 2 fixing screws (J-BASE-02): ck_x - ck_e back from the knee face's centre along FL1,
    # ck_y / 2 - ck_e either side
    for sgn, lab in ((1, "1"), (-1, "2")):
        xf = "%s - %s * (ck_x - ck_e) + %d * %s * (ck_y / 2 - ck_e)" % (FC_KX, D1X, sgn, P1X)
        yf = "%s - %s * (ck_x - ck_e) + %d * %s * (ck_y / 2 - ck_e)" % (FC_KY, D1Y, sgn, P1Y)
        hole_that_cuts(design, "fl1", bot, "KNEE KEY FIXING %s (111214)" % lab, (v(xf), v(yf), v("glide_h")),
             [(X, xf), (Y, yf)], "ck_fix_hole", "band_wall", Z)
    hole_that_cuts(design, "fl1", top, "DL SPIGOT RIVNUT - ROUND HOLE (J-FRONT-02)", (v("dlf_sp_ax"), v("dlf_sp_ay"), v("wall_z0")),
         [(X, "dlf_sp_ax"), (Y, "dlf_sp_ay")], "rn_hole", "band_wall", down)
    off = keyhole_check(design, "fl1", "111212", "front left corner (LH)", corner, n_corner)
    with open(os.path.join(REPO, "v2/01-CAD-Native/joints/corner-keys.csv"), encoding="utf-8") as fh:
        r = [x for x in csv.DictReader(fh) if x["part_number"] == "111214"][0]
    fix = centres(c.bRepBodies.item(0), v("ck_fix_hole"), "z")
    print("  111104 holes (centre across the axis, diameter; axis): %s" % holes_of_all(c.bRepBodies.item(0)))
    want = [(float(r["fix_hole_1_x"]), float(r["fix_hole_1_y"])), (float(r["fix_hole_2_x"]), float(r["fix_hole_2_y"]))]
    ok = all(any(abs(g[0] - w[0]) < 0.05 and abs(g[1] - w[1]) < 0.05 for g in fix) for w in want)
    print("  111104 knee key 111214's fixing holes against corner-keys.csv: %s (got %s, want %s)" % (
        "MATCH" if ok else "OFF", fix, want))
    if off or not ok:
        raise RuntimeError("FL1 sample: off against corner-keys.csv")
    print("P02: FL1 %s" % fmt_box(bbox_mm(single_body(c))))
