"""BASE revision P02: the rest of the base, loaded by base_build.py with --arg rev=P02.

Executed inside base_build.py's namespace (it uses its helpers and adds to its
PARTS, BASE_PARAMS, MATERIALS, steps and hardware). Adds:

  right side band 110102 / 111102 (mirror of the left; the back key at BR, D-129)
  front band pieces: FL1 111104, FL2 111105 (DL's two facets; FL2 with its door-end
      block welded on), FR1 111106 (under the fixed glass)
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
    ("ch_w", "fgl_gu_prof_w", "mm", "source",
     "FRONT's U-channel width (gu_prof_w, Bohle 15 x 15 x 1.5), linked: Y -706.5 to -691.5, centred on glass_y"),
    ("ch_h", "fgl_gu_prof_d", "mm", "source",
     "FRONT's U-channel depth (gu_prof_d), linked: its underside Z 95, its top Z 110 (the band top, the glass's visible bottom line)"),
    ("sl_t", "2 mm", "mm", "assumption", "sill sheet: aluminium 2 mm, bent, black anodised AA20 (D-67 look)"),
    ("sl_flange", "40 mm", "mm", "assumption", "sill's fixing flange down FR1's inner face (blind rivets, HOLD)"),
    # the channel's holes as FRONT sets them (fixed_glass.py gs_*), from FRONT's linked glass lines (Reviewer 8's P3 on #303:
    # the sill's end and rivnuts follow an edit as FRONT's channel does)
    ("ch_z95", "fgl_fg_vis_zb - fgl_gu_prof_d", "mm", "calculation", "the channel's underside, Z 95 (FRONT's _Z95)"),
    ("ch_free_x", "(fgl_fg_lc + fgl_fg_gap - fgl_fg_lnz * ch_z95) / fgl_fg_lnx", "mm", "calculation",
     "the channel's left end: the pane's free edge at its underside (FRONT's front_lib.free_x(Z 95), X 219.4)"),
    ("ch_right_x", "(fgl_fg_rc + fgl_gu_prof_d - fgl_fg_rnz * ch_z95) / fgl_fg_rnx", "mm", "calculation",
     "the channel's right end at its underside (FRONT's front_lib.right_x(Z 95, gu_prof_d), X 964.1)"),
    ("ch_end", "50 mm", "mm", "source", "channel screws 50 from each end (PM ruling 2026-11-01; FRONT's gs_end)"),
    ("sl_x1", "x_fr_joint + 50 mm", "mm", "calculation",
     "the sill's right end, X 965, tied to FR1's joint: past the channel's right end (ch_right_x, 964.1); the intake's "
     "closing plate closes it (D-150, batch 3)"),
    ("ch_screw_x1", "ch_free_x + ch_end", "mm", "calculation", "the first channel hole, X 269.4 (FRONT's gs_xl + gs_end)"),
    ("ch_screw_p", "(ch_right_x - ch_free_x - 2 * ch_end) / 3", "mm", "calculation",
     "the pitch of the first 3 channel holes, 214.9: X 269.4, 484.3, 699.2 (FRONT's gs_p)"),
    ("ch_screw_x4", "x_fr_joint - 10 mm", "mm", "confirmed",
     "the last channel screw at X 905, tied to FR1's joint: 2 hole diameters from FR1's end (joints register J-FRONT-04, "
     "the Lead 2026-11-01; FRONT's gs_x4 = FR1's joint - 10)"),
    ("fep_t", "2 mm", "mm", "assumption",
     "FL2's door-end plate: 2 mm aluminium, welded into FL2's door end flush with DL's door face, from FL2's inner face "
     "to the kick strip's back line (the PM's ruling of 2026-11-01 on the door's hinge side, as D-150)"),
    ("fep_pad_t", "8 mm", "mm", "assumption",
     "the strike pad on FL2's door-end plate for the drop seal's release button (HOLD): 11 - the button's standout + its "
     "stroke from athmer's button drawing; at most 8, so 3 stays clear of the kick strip's end (FRONT, 2026-11-01)"),
    ("fep_pad_w", "12 mm", "mm", "source", "the button's window across the glass line, Y -705 to -693 (FRONT, 2026-11-01)"),
    ("fep_pad_h", "65 mm", "mm", "source",
     "the button's window from the kick strip's bottom line (glide_h, Z 10) up to Z 75 (FRONT, 2026-11-01)"),
    ("gl_fl2", "145 mm", "mm", "calculation",
     "FL2's glide along its centre line from the knee face's centre: the support under DL and the door's hinges "
     "(about 650 N, DL 12.3 kg and the 48.6 kg door, FRONT's lists), 60 from DL's slot spigot rivnut (40 needed) "
     "and its load block 7 clear of the door-end block; FL1, 112 long between two keyed ends, has none"),
    ("ch_rn_hole", "5 mm", "mm", "assumption", "hole for the flush-head M3 rivnut in the sill seat (product with the Joints Engineer, HOLD)"),
]

# the sill's members' numbers, from Control (D-120, the Lead's message of 2026-11-01): 1 of each per sill
SILL_MEMBER_PNS = {"sill_bent": "111302", "sill_plate": "111303"}

P02_PARTS = {
    "band_r": ("110102", "BASE - BAND ASSY - SIDE - RH", "Viền chân nhôm - cạnh phải (cụm)", "HS", None),
    "band_r_tube": ("111102", "BASE - BAND TUBE - SIDE - RH", "Viền chân nhôm 100x40 - cạnh phải", "MP", "band_r"),
    "seal_r": ("118001", "BASE - BASE SEAL - LIP - ROOM FLOOR - HOLD", "Gioăng môi sát sàn", "PI", "band_r"),
    "seal_fr1": ("118001", "BASE - BASE SEAL - LIP - ROOM FLOOR - HOLD", "Gioăng môi sát sàn", "PI", "front_r"),
    "seal_se": ("118001", "BASE - BASE SEAL - LIP - ROOM FLOOR - HOLD", "Gioăng môi sát sàn", "PI", "front_r"),
    "front_l": ("110104", "BASE - BAND ASSY - FRONT - LH", "Viền chân trước - trái (cụm)", "HS", None),
    "fl1": ("111104", "BASE - BAND TUBE - FRONT - FACET 1 - LH", "Viền chân trước - mặt vát 1", "MP", "front_l"),
    "fl2": ("111105", "BASE - BAND TUBE - FRONT - FACET 2 - LH", "Viền chân trước - mặt vát 2", "MP", "front_l"),
    "seal_fl1": ("118001", "BASE - BASE SEAL - LIP - ROOM FLOOR - HOLD", "Gioăng môi sát sàn", "PI", "front_l"),
    "seal_fl2": ("118001", "BASE - BASE SEAL - LIP - ROOM FLOOR - HOLD", "Gioăng môi sát sàn", "PI", "front_l"),
    "seal_fe": ("118001", "BASE - BASE SEAL - LIP - ROOM FLOOR - HOLD", "Gioăng môi sát sàn", "PI", "front_l"),
    # the Joints Engineer's keys (J-BASE-02), imported from their STEPs and placed by reference (D-95)
    "key_f": ("111212", "BASE - CORNER KEY - FRONT - LH", "Ke góc đế trước - trái", "MP", None),
    "key_k": ("111214", "BASE - CORNER KEY - KNEE - LH", "Ke góc đế - gối trái", "MP", None),
    "front_r": ("110106", "BASE - BAND ASSY - FRONT - FIXED GLASS", "Viền chân trước - dưới kính cố định (cụm)", "HS", None),
    "fr1": ("111106", "BASE - BAND TUBE - FRONT - FIXED GLASS", "Viền chân trước - dưới kính cố định", "MP", "front_r"),
    "intake": ("110107", "BASE - INTAKE ASSY - DR", "Cụm cửa gió dưới khối phải", "HS", None),
    "mesh": ("111107", "BASE - INTAKE MESH - DR", "Lưới cửa gió", "MP", "intake"),
    "rail": ("111108", "BASE - INTAKE SUPPORT RAIL - DR", "Thanh đỡ khối phải", "MP", "intake"),
    "cplate": ("111109", "BASE - INTAKE CLOSING PLATE - DR", "Tấm ngăn cửa gió", "MP", "intake"),
    "sill": ("111301", "BASE - SILL - FIXED GLASS", "Bậu đỡ kính cố định", "HS", "front_r"),
    # its members (D-120, the Lead's ruling of 2026-11-01): their own components, STEPs and DXFs, so the bent sill
    # goes to the generator's bent-sheet mode on its own and the welded sill to its weldment sheet
    "sill_bent": (SILL_MEMBER_PNS["sill_bent"], "BASE - SILL - FIXED GLASS - BENT PROFILE", "Bậu đỡ kính cố định - thanh gấp",
                  "MP", "sill"),
    "sill_plate": (SILL_MEMBER_PNS["sill_plate"], "BASE - SILL - FIXED GLASS - DOOR-END PLATE",
                   "Bậu đỡ kính cố định - tấm bịt đầu phía cửa", "MP", "sill"),
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
# FL2's door-end plate (the PM's hinge-side ruling, 2026-11-01): its pod-side face X_FEP, FL2's inner line there, and
# the kick strip's back line it runs to
X_FEP = "(%s + dl_w - fep_t)" % XL_
Y_FEP_IN = "(%s - (%s - %s) * %s / %s)" % (IL2_Y, X_FEP, IL2_X, B2, A2)
Y_KICK_BACK = "(-glass_y + kick_d / 2)"
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


BATCH1 = ("band_r", "band_r_tube", "front_r", "fr1", "sill", "sill_bent", "sill_plate", "seal_r", "seal_fr1", "seal_se")   # F2, its foam and spigots, the threshold went (D-132)


# batch 2: the front-left pieces under DL (with --arg batch2=1; its method sample first: --arg part=fl1)
BATCH2 = ("front_l", "fl1", "fl2", "seal_fl1", "seal_fl2", "seal_fe", "key_f", "key_k")

P02_BATCH_KEYS = BATCH1 + (BATCH2 if ARGS.get("batch2") == "1" else ())


def p02_setup(keys=P02_BATCH_KEYS):
    """Adds the P02 parameters and the parts of this batch (keys) to base_build's tables."""
    global SUB_DESIGNS, WITH_ASSEMBLY, HOLDING_KEYS
    BASE_PARAMS.extend(front_glass_params())    # FRONT's glass lines: the sill's channel and its holes (linked)
    BASE_PARAMS.extend(P02_PARAMS)
    if "fl1" in keys or "fl2" in keys:
        BASE_PARAMS.extend(front_dl_params())     # DL's spigot points, FRONT's named values (J-FRONT-02)
    PARTS.update({k: P02_PARTS[k] for k in keys})
    if None in SILL_MEMBER_PNS.values():
        raise RuntimeError("the sill's member numbers (D-120) aren't allocated yet: ask Control, then fill SILL_MEMBER_PNS")
    mats = {k: ("Aluminum", None, None) for k in ("band_r_tube", "fl1", "fl2", "fr1", "rail", "cplate", "sill_bent", "sill_plate",
                                                    "key_f", "key_k")}
    mats.update({"mesh": ("Aluminum", "Expanded mesh 80% free, 540 kg/m3 (ASSUMPTION)", 540.0),
                 "seal_r": MATERIALS["seal_l"], "seal_fr1": MATERIALS["seal_l"], "seal_se": MATERIALS["seal_l"],
                 "seal_fl1": MATERIALS["seal_l"], "seal_fl2": MATERIALS["seal_l"], "seal_fe": MATERIALS["seal_l"]})
    MATERIALS.update({k: m for k, m in mats.items() if k in keys})
    SUB_DESIGNS = tuple(SUB_DESIGNS) + tuple(k for k in ("band_r", "front_r", "front_l") if k in keys)
    if "fl1" in keys:             # batch 2: the front keys come from their owner's STEPs (D-95), held at the root and copied
        OWNER_STEP.update({"key_f": "v2/03-Manufacturing/joints/111212_P01_BASE-CORNER-KEY-FRONT-LH_STEP.step",
                           "key_k": "v2/03-Manufacturing/joints/111214_P01_BASE-CORNER-KEY-KNEE-LH_STEP.step"})
        HOLDING_KEYS = tuple(HOLDING_KEYS) + ("key_f", "key_k")
        EXPECTED_OWN.extend([
            ("838001", "111212", "hook stud threads in the front corner key's tapped holes (J-BASE-02)"),
            ("838010", "111212", "fixing screw threads in the front corner key's tapped holes (J-BASE-02)"),
            ("838001", "111214", "hook stud threads in the knee key's tapped holes (J-BASE-02)"),
            ("838010", "111214", "fixing screw threads in the knee key's tapped holes (J-BASE-02)")])
        WITH_ASSEMBLY = tuple(WITH_ASSEMBLY) + ("fl1", "fl2")
    if "band_r_tube" in keys:     # its back end carries a corner key (D-129): its part design follows each assembly save, as 111101's
        WITH_ASSEMBLY = tuple(WITH_ASSEMBLY) + ("band_r_tube",)
    PART_BUILDS.update({k: fns for k, fns in (
        ("band_r_tube", ("step_p02_band_r",)), ("fr1", ("step_p02_fr1",)), ("sill_bent", ("step_p02_sill_bent",)), ("sill_plate", ("step_p02_sill_plate",)),
        ("fl1", ("step_p02_fl1",)), ("fl2", ("step_p02_fl2",)))
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


def step_p02_fl2(design):
    """FL2 (111105): DL's second facet, from the knee mitre with FL1 to its square end at X -pod_w/2 + dl_x3, with
    the door-end block welded on out to DL's door face (X -pod_w/2 + dl_w): one part, ground flush and anodised
    after welding. Its knee end is closed by its band_wall end plate with the keyholes for FL1's knee key 111214
    (FL2 is the keyhole piece: on along the studs, then down kh_drop); its top wall has the rivnut hole for DL's
    slot spigot at FRONT's named point (J-FRONT-02); one glide with its load block, gl_fl2 from the knee face's
    centre along FL2. Checked against corner-keys.csv."""
    v = lambda e: ev(design, e)  # noqa: E731
    fl2 = [P(design, "%s + dl_x2" % XL_, "-dl_y2"), P(design, "%s + dl_x3" % XL_, "-dl_y3"),
           P(design, "%s + dl_x3" % XL_, Y_FL2_IN_END), P(design, IL2_X, IL2_Y)]
    knee = (v(FC_KX), v(FC_KY))
    plan_tube(design, "fl2", "FRONT FACET 2 LH", fl2, "", closed_near=knee)
    n_k = unit_xy(v(D1X) + v(D2X), v(D1Y) + v(D2Y))
    n_out = (-n_k[0], -n_k[1])                        # FL2's knee face looks back at FL1
    keyholes_on_face(design, "fl2", knee, n_out, W_KNEE, "FL2 KNEE (111214)")
    c = find_comp(design, "fl2")
    body = c.bRepBodies.item(0)
    bot = [p for p in c.constructionPlanes if p.name == "PLANE - BAND BOTTOM Z = glide_h"][0]
    # the door-end block, welded on: joined to the tube, it closes FL2's open end. The door-end plate (fep_t, the PM's
    # ruling of 2026-11-01 on the hinge side, as D-150) is welded into it, flush with DL's door face: it carries the
    # face on inward from FL2's inner face to the kick strip's back line, from the band's bottom line up, so the space
    # under DL in front of the door plane is closed and FRONT's brush on the kick strip's hinge end closes on it.
    # One profile, one extrude: the block and the plate are one weldment with the tube.
    sk = c.sketches.add(bot)
    sk.name = "PLAN - FL2 DOOR-END BLOCK AND PLATE (WELDED ON) - TO DL'S DOOR FACE, THE PLATE TO THE KICK STRIP'S BACK LINE"
    polygon(design, sk, [P(design, "%s + dl_x3" % XL_, "-dl_y3"), P(design, "%s + dl_w" % XL_, "-dl_y3"),
                         P(design, "%s + dl_w" % XL_, Y_KICK_BACK), P(design, X_FEP, Y_KICK_BACK),
                         P(design, X_FEP, Y_FEP_IN), P(design, "%s + dl_x3" % XL_, Y_FL2_IN_END)], X, Y)
    check_sketch(sk)
    ei = c.features.extrudeFeatures.createInput(one_profile(sk), adsk.fusion.FeatureOperations.JoinFeatureOperation)
    ei.setDistanceExtent(False, vi("band_h"))
    ei.participantBodies = [body]
    f = c.features.extrudeFeatures.add(ei)
    f.name = "EXTRUDE - FL2 DOOR-END BLOCK AND PLATE band_h, JOINED (WELDED)"
    if c.bRepBodies.count != 1:
        raise RuntimeError("FL2: the door-end block didn't join the tube (%d bodies)" % c.bRepBodies.count)
    # the door-end plate's back edge, on the kick strip's back line: a full round across its fep_t (the Lead's ruling of
    # 2026-11-01), so the hinge-side brush's back tips stay on the plate's face through the door's swing; its apex stays
    # on the kick strip's back line
    yb, xm = v(Y_KICK_BACK), v("%s + fep_t / 2" % X_FEP)
    ends = [fc for fc in c.bRepBodies.item(0).faces
            if fc.geometry.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType
            and abs(abs(adsk.core.Plane.cast(fc.geometry).normal.y) - 1.0) < 1e-6
            and abs(mm(fc.pointOnFace.y) - yb) < 0.01 and abs(mm(fc.pointOnFace.x) - xm) < v("fep_t") / 2 + 0.01]
    if len(ends) != 1:
        raise RuntimeError("FL2: the door-end plate's back end face: found %d, want 1" % len(ends))
    # the two side faces, each touching the end face along one of its edges: the door face (X = DL's door face) and the
    # plate's pod-side face (X_FEP); Fusion wants one of each (2026-11-01 dry run: empty lists are refused)
    xs = {}
    for e in ends[0].edges:
        for fc in e.faces:
            if fc == ends[0] or fc.geometry.surfaceType != adsk.core.SurfaceTypes.PlaneSurfaceType:
                continue
            if abs(abs(adsk.core.Plane.cast(fc.geometry).normal.x) - 1.0) < 1e-6:
                xs[round(mm(fc.pointOnFace.x), 2)] = fc
    if len(xs) != 2:
        raise RuntimeError("FL2: the plate's back end has %d side faces square to X, want 2" % len(xs))
    side_door, side_pod = xs[max(xs)], xs[min(xs)]
    fr = c.features.filletFeatures.createFullRoundFilletInput()
    fr.faceSets.add(ends[0], [side_door], [side_pod], True)
    ff = c.features.filletFeatures.addFullRoundFillet(fr)
    ff.name = "FULL ROUND - FL2 DOOR-END PLATE'S BACK EDGE (ON THE KICK STRIP'S BACK LINE)"
    if c.bRepBodies.count != 1:
        raise RuntimeError("FL2: %d bodies after the plate's full round" % c.bRepBodies.count)
    # the strike pad for the drop seal's release button (the Lead and FRONT, 2026-11-01): on the plate's door face in the
    # button's window, fep_pad_t proud (HOLD until athmer's button drawing). It starts 0.5 inside the plate, so the
    # join overlaps a volume and stays one body
    x_in = "%s + dl_w - 0.5 mm" % XL_
    pl = offset_plane(c, "yz", x_in, v(x_in), "PLANE - FL2 STRIKE PAD - 0.5 INSIDE THE DOOR-END PLATE")
    ya, yb2 = "-glass_y - fep_pad_w / 2", "-glass_y + fep_pad_w / 2"
    za, zb = "glide_h", "glide_h + fep_pad_h"
    xv = v(x_in)
    skp = c.sketches.add(pl)
    skp.name = "SECTION - FL2 STRIKE PAD (HOLD) - THE DROP SEAL BUTTON'S WINDOW"
    polygon(design, skp, [(ey, ez, (xv, v(ey), v(ez))) for ey, ez in ((ya, za), (yb2, za), (yb2, zb), (ya, zb))], Y, Z)
    check_sketch(skp)
    ep = c.features.extrudeFeatures.createInput(one_profile(skp), adsk.fusion.FeatureOperations.JoinFeatureOperation)
    dirp = adsk.fusion.ExtentDirections.PositiveExtentDirection if pl.geometry.normal.x > 0 else \
        adsk.fusion.ExtentDirections.NegativeExtentDirection
    ep.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(vi("fep_pad_t + 0.5 mm")), dirp)
    ep.participantBodies = [c.bRepBodies.item(0)]
    c.features.extrudeFeatures.add(ep).name = "EXTRUDE - FL2 STRIKE PAD fep_pad_t (HOLD), JOINED (WELDED)"
    if c.bRepBodies.count != 1:
        raise RuntimeError("FL2: %d bodies after the strike pad" % c.bRepBodies.count)
    top = offset_plane(c, "xy", "wall_z0", v("wall_z0"), "PLANE - BAND TOP Z = wall_z0")
    down = Z.copy()
    down.scaleBy(-1)
    hole_that_cuts(design, "fl2", top, "DL SPIGOT RIVNUT - SLOT (J-FRONT-02)", (v("dlf_sp_bx"), v("dlf_sp_by"), v("wall_z0")),
                   [(X, "dlf_sp_bx"), (Y, "dlf_sp_by")], "rn_hole", "band_wall", down)
    xg, yg = "%s + gl_fl2 * %s" % (FC_KX, D2X), "%s + gl_fl2 * %s" % (FC_KY, D2Y)
    hole_that_cuts(design, "fl2", bot, "GLIDE NUT - FL2", (v(xg), v(yg), v("glide_h")), [(X, xg), (Y, yg)],
                   "gl_nut_hole", "band_wall", Z)
    hole_that_cuts(design, "fl2", top, "GLIDE KEY - FL2", (v(xg), v(yg), v("wall_z0")), [(X, xg), (Y, yg)],
                   "gl_key_hole", "band_wall", down)
    off = keyhole_check(design, "fl2", "111214", "front left knee", knee, n_out)
    print("  111105 holes (centre across the axis, diameter; axis): %s" % holes_of_all(c.bRepBodies.item(0)))
    if off:
        raise RuntimeError("FL2: off against corner-keys.csv")
    print("P02: FL2 %s" % fmt_box(bbox_mm(single_body(c))))


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
    # the bore: shell the prism's side faces (2 long faces and open ends). The top and bottom faces are told by
    # their normals (along Z), not by their heights: every side face reaches the same top and bottom, and on a
    # short piece (FL1, 4469 mm2 in plan) the top and bottom were as small as an end face and were shelled
    # away too, leaving no bottom wall for the knee key's screws (FL1 sample, 2026-11-01)
    faces = adsk.core.ObjectCollection.create()

    def flat(fc):
        g = fc.geometry
        if g.surfaceType != adsk.core.SurfaceTypes.PlaneSurfaceType:
            return False
        return abs(abs(adsk.core.Plane.cast(g).normal.z) - 1.0) < 1e-6
    ends = [fc for fc in body.faces if not flat(fc) and
            fc.area * 100.0 < (ev(design, "band_t") + 1.0) * ev(design, "band_h") * 1.2]   # the short faces
    if len(ends) != 2:
        raise RuntimeError("%s: expected 2 end faces, found %d" % (label, len(ends)))
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


def sill_section_lines(design):
    """The sill's section lines on the plane X = X_FR0, as expressions (the bent profile's and the plate's)."""
    return {"y_fr": "-pod_d / 2 + band_t", "y_fl": "-pod_d / 2 + band_t + sl_t",
            "y_dw": "-glass_y - ch_w / 2 - sl_t", "y_c0": "-glass_y - ch_w / 2",
            "y_c1": "-glass_y + ch_w / 2", "y_kb": "-glass_y + ch_w / 2 + sl_t",
            "z_top": "wall_z0", "z_lb": "wall_z0 - sl_t", "z_st": "wall_z0 - ch_h", "z_sb": "wall_z0 - ch_h - sl_t",
            "z_fl": "wall_z0 - sl_flange", "z_kb": "glide_h"}


def sill_plane(design, comp, label):
    """The plane X = X_FR0 (the sill's door end) in comp, and the extrude direction into the sill (+X)."""
    v = lambda e: ev(design, e)  # noqa: E731
    pl = offset_plane(comp, "yz", X_FR0, v(X_FR0), "PLANE - %s - DOOR END X = X_FR0" % label)
    direc = adsk.fusion.ExtentDirections.PositiveExtentDirection if pl.geometry.normal.x > 0 else \
        adsk.fusion.ExtentDirections.NegativeExtentDirection
    return pl, direc


def step_p02_sill_bent(design):
    """The fixed glass's sill, its bent profile (member of the welded sill 111301, D-120): a bent 2 mm profile,
    black AA20, from the door opening's right edge to sl_x1. A flange down FR1's inner face (riveted, HOLD), a ledge
    flush with the band top over to the channel, a drop wall, the seat under FRONT's U-channel (Z 93 to 95, 4 flush M3
    rivnuts take the channel's screws, set after anodising), and a kerb down to the band's bottom line (D-132: no floor
    under it, so the glass's load, about 280 N, goes into FR1). The channel is screwed on at the factory and ships on
    the sill with FR1 (PM ruling)."""
    v = lambda e: ev(design, e)  # noqa: E731
    comp = find_comp(design, "sill_bent")
    L = sill_section_lines(design)
    pl, direc = sill_plane(design, comp, "SILL BENT PROFILE")
    xv = v(X_FR0)

    def pt(ey, ez):
        return (L[ey], L[ez], (xv, v(L[ey]), v(L[ez])))
    sk = comp.sketches.add(pl)
    sk.name = "SECTION - SILL (FLANGE, LEDGE, DROP, SEAT, KERB)"
    polygon(design, sk, [pt("y_fr", "z_top"), pt("y_c0", "z_top"), pt("y_c0", "z_st"), pt("y_kb", "z_st"),
                         pt("y_kb", "z_kb"), pt("y_c1", "z_kb"), pt("y_c1", "z_sb"), pt("y_dw", "z_sb"),
                         pt("y_dw", "z_lb"), pt("y_fl", "z_lb"), pt("y_fl", "z_fl"), pt("y_fr", "z_fl")], Y, Z)
    check_sketch(sk)
    ei = comp.features.extrudeFeatures.createInput(one_profile(sk), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(vi("sl_x1 - %s" % X_FR0)), direc)
    f = comp.features.extrudeFeatures.add(ei)
    f.name = "EXTRUDE - SILL - LENGTH sl_x1 - X_FR0"
    single_body(comp, PARTS["sill_bent"][1])
    z_st = L["z_st"]
    seat = offset_plane(comp, "xy", z_st, v(z_st), "PLANE - SILL SEAT TOP Z = wall_z0 - ch_h")
    down = Z.copy()
    down.scaleBy(-1)
    hole(design, "sill_bent", seat, "CHANNEL SCREW RIVNUT - M3 FLUSH (HOLD) - 1 TO 3",
         (v("ch_screw_x1"), v("-glass_y"), v(z_st)), [(X, "ch_screw_x1"), (Y, "-glass_y")], "ch_rn_hole", "sl_t", down,
         ("xConstructionAxis", "3", "2 * ch_screw_p"))
    seat4 = offset_plane(comp, "xy", z_st, v(z_st), "PLANE - SILL SEAT TOP (LAST SCREW)")
    hole(design, "sill_bent", seat4, "CHANNEL SCREW RIVNUT - M3 FLUSH (HOLD) - 4", (v("ch_screw_x4"), v("-glass_y"), v(z_st)),
         [(X, "ch_screw_x4"), (Y, "-glass_y")], "ch_rn_hole", "sl_t", down)
    print("P02: sill's bent profile %s" % fmt_box(bbox_mm(single_body(comp))))


def step_p02_sill_plate(design):
    """The sill's door-end plate (member of the welded sill 111301, D-120; D-150): welded into the bent profile's door
    end, it closes the space under the ledge and seat, from FR1's inner face to the kerb and down to the band's bottom
    line, so the seal line turns this corner: FR1's lip, this plate's lip along its bottom edge to the floor, then
    FRONT's brush at the kick strip's end. Its outline is the profile's inner faces (sill_end_plate_pts): it only
    touches the bent profile, which the weld joins; its own component, not a joined body."""
    v = lambda e: ev(design, e)  # noqa: E731
    comp = find_comp(design, "sill_plate")
    pl, direc = sill_plane(design, comp, "SILL DOOR-END PLATE")
    xv = v(X_FR0)
    sk = comp.sketches.add(pl)
    sk.name = "SECTION - SILL DOOR-END PLATE (WELDED IN): FR1'S INNER FACE TO THE KERB, DOWN TO glide_h"
    polygon(design, sk, [(ey, ez, (xv, v(ey), v(ez))) for ey, ez in sill_end_plate_pts()], Y, Z)
    check_sketch(sk)
    ei = comp.features.extrudeFeatures.createInput(one_profile(sk), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(vi("sl_t")), direc)
    comp.features.extrudeFeatures.add(ei).name = "EXTRUDE - SILL DOOR-END PLATE sl_t"
    print("P02: sill's door-end plate %s" % fmt_box(bbox_mm(single_body(comp, PARTS["sill_plate"][1]))))


P02_STEPS = [step_p02_band_r, step_p02_fr1, step_p02_sill_bent, step_p02_sill_plate]   # batch 1 (F2 and the threshold went, D-132)

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
    if "fl1" in PARTS:
        out += p02_hardware_front_l(design)
    return out


def p02_hardware_front_l(design):
    """Batch 2 (J-BASE-02, J-FRONT-02): the front corner key 111212 in the left side band's front end (its carrier)
    and the knee key 111214 in FL1's knee end, each with 2 flanged button head fixing screws from below and 2 hook
    stud bolts in its stud face, heads st_gap off it; DL's 2 spigots in rivnuts on FL1 and FL2 (no stop washer);
    FL2's glide with its load block. Positions from the same expressions as the holes; the keys' come from their
    stud faces (the mitres' centres) and their carriers' directions, as corner-keys.csv has them."""
    v = lambda e: ev(design, e)  # noqa: E731
    out = []
    d1, d2 = (v(D1X), v(D1Y)), (v(D2X), v(D2Y))
    n_c = unit_xy(d1[0], d1[1] - 1.0)                # the corner mitre's normal, out of the side band
    n_k = unit_xy(d1[0] + d2[0], d1[1] + d2[1])      # the knee mitre's normal, out of FL1
    deg = lambda u: math.degrees(math.atan2(u[1], u[0]))  # noqa: E731
    zk, zs = v("glide_h + band_wall"), v("glide_h")
    for host, key, face, carrier, n in (("band_l", "key_f", (v(FC_CX), v(FC_CY)), (0.0, -1.0), n_c),
                                        ("front_l", "key_k", (v(FC_KX), v(FC_KY)), d1, n_k)):
        lx, ly = -carrier[1], carrier[0]             # the key's +y, left of its +x (joints README)
        bx, by = face[0] - v("ck_x") * carrier[0], face[1] - v("ck_x") * carrier[1]   # its back face's centre
        out.append((host, key, (bx, by, zk), ("z", deg(carrier))))
        for sy in (1, -1):
            out.append((host, "bscrew", (bx + v("ck_e") * carrier[0] + sy * v("ck_y / 2 - ck_e") * lx,
                                         by + v("ck_e") * carrier[1] + sy * v("ck_y / 2 - ck_e") * ly, zs), "z-"))
        for zz in ("st_z1", "st_z2"):
            out.append((host, "bolt", (face[0] + v("st_gap") * n[0], face[1] + v("st_gap") * n[1], zk + v(zz)),
                        ("hz", deg(n))))
    z_top, head = v("wall_z0"), v("rn_head_t")
    for x, y in ((v("dlf_sp_ax"), v("dlf_sp_ay")), (v("dlf_sp_bx"), v("dlf_sp_by"))):
        out.append(("front_l", "rivnut", (x, y, z_top), None))
        out.append(("front_l", "pin", (x, y, z_top + head), None))
    xg, yg = v("%s + gl_fl2 * %s" % (FC_KX, D2X)), v("%s + gl_fl2 * %s" % (FC_KY, D2Y))
    out.append(("front_l", "glide", (xg, yg, 0.0), None))
    out.append(("front_l", "doubler", (xg, yg, zk), ("z", deg(d2) - 90.0)))     # its 54 along FL2
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
    if "fl1" in PARTS:
        # FL1's inner face from the inner corner to the inner knee, FL2's from there to DL's door face (along the
        # welded block's inner edge). The envelopes meet without overlapping: FL1's starts where it clears the side
        # band's (its far corner on X = -pod_w/2 + band_t + seal_t), the two meet at the knee's offset point (the
        # inner knee's own formula with seal_t), and FL2's ends on the door face's line.
        xc, yc = "(%s + band_t)" % XL_, Y_MITRE_IN
        p1x, p1y = "(%s / %s)" % (B1, L1), "(%s / %s)" % (A1, L1)          # FL1's left normal, into the pod
        p2x, p2y = "(%s / %s)" % (B2, L2), "(%s / %s)" % (A2, L2)          # FL2's
        t0 = "(seal_t * (1 - %s) / %s)" % (p1x, D1X)
        s0x, s0y = "(%s + %s * %s)" % (xc, t0, D1X), "(%s + %s * %s)" % (yc, t0, D1Y)
        qx = "(%s + seal_t * (%s + %s) / (1 + %s))" % (IL2_X, p1x, p2x, DOT)
        qy = "(%s + seal_t * (%s + %s) / (1 + %s))" % (IL2_Y, p1y, p2y, DOT)
        xe, ye = X_FEP, Y_FEP_IN          # FL2's lip stops at its door-end plate's pod side (the hinge-side ruling)
        l1 = "sqrt((%s - %s) ^ 2 + (%s - %s) ^ 2)" % (IL2_X, xc, IL2_Y, yc)
        l2 = "sqrt((%s - %s) ^ 2 + (%s - %s) ^ 2)" % (xe, IL2_X, ye, IL2_Y)
        # FL1's envelope starts at the inner corner and wraps round the side band envelope's front corner
        # (X -pod_w/2 + band_t + seal_t, Y_MITRE_IN): the two only touch along edges
        runs.append(("seal_fl1", "front_l", "FL1, inner face", "0 mm", l1,
                     [(xc, yc), (IL2_X, IL2_Y), (qx, qy), ("(%s + seal_t * %s)" % (s0x, p1x), "(%s + seal_t * %s)" % (s0y, p1y)),
                      ("(%s + seal_t)" % xc, yc)]))
        runs.append(("seal_fl2", "front_l", "FL2, inner face, to its door-end plate", "0 mm", l2,
                     [(IL2_X, IL2_Y), (xe, ye), (xe, "(%s + seal_t / %s)" % (ye, p2y)), (qx, qy)]))
        # FL2's door-end plate's lip (the PM's hinge-side ruling, as D-150): along the plate's bottom edge from FL2's
        # inner face to the kick strip's back line. Its fin sits under the plate, flush with DL's door face, and meets
        # FL2's lip's end; its leg is on the plate's pod side, starting where FL2's lip envelope leaves room for it
        # (FL2 runs at an angle). p02_seal_cuts takes the envelope's top off where the plate stands on the fin.
        xo, xl = "(%s + dl_w)" % XL_, "(%s - seal_t)" % X_FEP
        yl0 = "(%s - (%s - %s) * %s / %s + seal_t / %s)" % (IL2_Y, xl, IL2_X, B2, A2, p2y)
        runs.append(("seal_fe", "front_l", "X = %.2f (FL2's door-end plate, its bottom edge)" % v(xo), Y_FEP_IN, Y_KICK_BACK,
                     [(xo, Y_FEP_IN), (xo, Y_KICK_BACK), (xl, Y_KICK_BACK), (xl, yl0), (X_FEP, yl0), (X_FEP, Y_FEP_IN)]))
    if "sill" in PARTS:
        # the sill's door-end plate (D-150, Reviewer 8's P1 on #303): its lip runs the plate's bottom edge from FR1's
        # lip (Y -pod_d/2 + band_t + seal_t, where FR1's lip envelope ends: the two only touch) to the kerb. Its leg is
        # bonded on the plate's pod side and its fin sits under the plate, flush with the plate's outer face
        # (p02_seal_sections), so FRONT's brush on the kick strip's end closes on a flat face from the floor up.
        y0, y1 = "(-pod_d / 2 + band_t + seal_t)", "(-glass_y + ch_w / 2)"
        xe = "(%s + sl_t + seal_t)" % X_FR0
        runs.append(("seal_se", "front_r", "X = %.2f (the sill's door-end plate, its bottom edge)" % v(X_FR0), y0, y1,
                     [(X_FR0, y0), (xe, y0), (xe, y1), (X_FR0, y1)]))
    if "fr1" in PARTS:
        # with the sill's door-end plate, FR1's lip starts at the plate's pod side (the plate's lip turns the corner)
        yf, x0 = "-pod_d / 2 + band_t", ("(%s + sl_t)" % X_FR0 if "sill" in PARTS else X_FR0)
        runs.append(("seal_fr1", "front_r", "Y = %.2f (FR1, inner face)" % v(yf), x0, X_FR_JOINT,
                     [(x0, yf), (X_FR_JOINT, yf), (X_FR_JOINT, "%s + seal_t" % yf), (x0, "%s + seal_t" % yf)]))
    return runs


def p02_seal_cuts(design):
    """Where a plate stands on a lip's fin: {run key: (plan rectangle, z from)}; the run's envelope is cut there from
    z from up through its top. FL2's door-end plate stands on its lip's fin (X_FEP to DL's door face), from glide_h."""
    if "fl2" not in PARTS:
        return {}
    xo = "(%s + dl_w + 1 mm)" % XL_
    return {"seal_fe": ([(X_FEP, "(%s - 1 mm)" % Y_FEP_IN), (xo, "(%s - 1 mm)" % Y_FEP_IN), (xo, "(%s + 1 mm)" % Y_KICK_BACK),
                         (X_FEP, "(%s + 1 mm)" % Y_KICK_BACK)], "glide_h")}


def p02_seal_sections(design):
    """Lips whose envelope is a section across the run, not a plan rectangle: {run key: (start y, end y, [(x, z)])},
    built as one extrude along +Y. The sill's door-end plate's lip: its leg on the plate's pod side (X_FR0 + sl_t to
    + seal_t, up to seal_leg above the band's bottom) and its fin under the 2 mm plate, flush with the plate's outer
    face X_FR0, from the room floor to the band's bottom line (an L). One extrude: a fin joined to the leg as a second
    body stayed a second body in Fusion (2026-11-01)."""
    if "sill" not in PARTS:
        return {}
    xo, xp, xe = X_FR0, "(%s + sl_t)" % X_FR0, "(%s + sl_t + seal_t)" % X_FR0
    sec = [(xo, "0 mm"), (xe, "0 mm"), (xe, "glide_h + seal_leg"), (xp, "glide_h + seal_leg"), (xp, "glide_h"),
           (xo, "glide_h")]
    return {"seal_se": ("(-pod_d / 2 + band_t + seal_t)", "(-glass_y + ch_w / 2)", sec)}

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
    if "fl1" in keys:
        d1, d2 = (v(D1X), v(D1Y)), (v(D2X), v(D2Y))
        n_c = unit_xy(d1[0], d1[1] - 1.0)
        n_k = unit_xy(d1[0] + d2[0], d1[1] + d2[1])
        ang = lambda a, b: math.degrees(math.acos(min(1.0, abs(a[0] * b[0] + a[1] * b[1]))))  # noqa: E731
        dist = lambda a, b: round(math.hypot(v(a[0]) - v(b[0]), v(a[1]) - v(b[1])), 2)     # noqa: E731
        oc, ok_, ik, ic = (XL_, "-dl_y1"), ("%s + dl_x2" % XL_, "-dl_y2"), (IL2_X, IL2_Y), ("%s + band_t" % XL_, Y_MITRE_IN)
        od, idd = ("%s + dl_x3" % XL_, "-dl_y3"), ("%s + dl_x3" % XL_, Y_FL2_IN_END)
        out["tubes"][PARTS["fl1"][0]] = {
            "section": "100 x 40 x %.1f" % v("band_wall"), "axis": "DL facet 1",
            "outer_face_length": dist(oc, ok_), "inner_face_length": dist(ic, ik),
            "front_end": "mitre to the left side band, %.2f deg from square, closed by a welded 1.5 end plate with 2 "
                         "keyholes for the front corner key 111212's studs" % ang(d1, n_c),
            "back_end": "mitre to FL2, %.2f deg from square, open: the knee key 111214 inside" % ang(d1, n_k)}
        out["tubes"][PARTS["fl2"][0]] = {
            "section": "100 x 40 x %.1f" % v("band_wall"), "axis": "DL facet 2",
            "outer_face_length": dist(ok_, od), "inner_face_length": dist(ik, idd),
            "front_end": "mitre to FL1, %.2f deg from square, closed by a welded 1.5 end plate with 2 keyholes for the "
                         "knee key 111214's studs" % ang(d2, n_k),
            "back_end": "cut square to X (%.2f deg from square), the door-end block welded on, %.1f to DL's door face, "
                        "and the 2 mm door-end plate welded into it, flush with that face, %.1f wide to the kick strip's "
                        "back line" % (ang(d2, (1.0, 0.0)), v("dl_w - dl_x3"), v("%s - %s" % (Y_KICK_BACK, Y_FEP_IN)))}
    if "sill" in keys:
        out["sill"] = {"t": v("sl_t"), "length": round(v("sl_x1 - %s" % X_FR0), 2), "x0": v(X_FR0),
                       "pn": PARTS["sill"][0], "pn_bent": PARTS["sill_bent"][0], "pn_plate": PARTS["sill_plate"][0],
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


FRONT_LIB = "v2/01-CAD-Native/front/front_lib.py"
FRONT_GLASS_WANT = ("fg_vis_zb", "gu_prof_w", "gu_prof_d", "fg_gap", "fg_lc", "fg_lnx", "fg_lnz", "fg_rc", "fg_rnx", "fg_rnz")


def front_dl_params(prefix="dlf_"):
    """FRONT's named values for DL's two spigots on the band (J-FRONT-02: sp_ax, sp_ay on FL1, sp_bx, sp_by on
    FL2), read from FRONT's DL model with every value they need, so one source drives both models (linked, not
    copied). FRONT's own names get the prefix, as some clash with BASE's (sp_e); skeleton names stay. A name that
    is neither FRONT's nor the skeleton's stops the build."""
    return front_params(FRONT_DL, "OWN", FRONT_DL_WANT, prefix, "DL spigot values")


def front_glass_params(prefix="fgl_"):
    """FRONT's glass lines shared by the fixed pane, DR and DT (front_lib.py GLASS_PARAMS), linked as for DL's
    spigots: the sill's channel holes follow FRONT's channel (Reviewer 8's P3 on #303)."""
    return front_params(FRONT_LIB, "GLASS_PARAMS", FRONT_GLASS_WANT, prefix, "glass lines")


def front_params(rel, list_name, want, prefix, what):
    """FRONT's rows named in want, from the list list_name in FRONT's file rel, with every FRONT row they need
    (prefixed); skeleton names stay. A name that is neither FRONT's nor the skeleton's stops the build."""
    import re
    path = os.path.join(REPO, rel)
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
            if tgt.id == list_name and isinstance(node.value, ast.List):
                own = []
                for el in node.value.elts:
                    try:
                        own.append(ast.literal_eval(el))
                    except ValueError:
                        own.append(eval(compile(ast.Expression(el), path, "eval"), {"__builtins__": {}}, dict(consts)))
    if own is None:
        raise RuntimeError("no %s list in %s" % (list_name, rel))
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
    for n in want:
        visit(n)
    out = []
    for n in order:
        name, expr, unit, status, desc = rows[n][:5]
        expr2 = ident.sub(lambda m: prefix + m.group(0) if m.group(0) in rows else m.group(0), expr)
        out.append((prefix + name, expr2, unit, status, "FRONT's %s in %s: %s" % (n, rel, desc)))
    print("  FRONT's %s linked: %s" % (what, ", ".join(r[0] for r in out)))
    return out


# FL1's corner mitre with the left side band and its knee mitre with FL2, in plan (expressions)
D1X, D1Y = "(dl_x2 / %s)" % L1, "(-(dl_y2 - dl_y1) / %s)" % L1          # FL1's direction, corner to knee
D2X, D2Y = "(%s / %s)" % (A2, L2), "(-%s / %s)" % (B2, L2)                  # FL2's direction, knee to door end
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


if "fl1" in P02_BATCH_KEYS:      # batch 2: DL's two facets (their steps are defined above)
    P02_STEPS = P02_STEPS + [step_p02_fl1, step_p02_fl2]
