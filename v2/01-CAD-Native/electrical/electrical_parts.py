"""ELECTRICAL (710000) P01: the parts, the harnesses, the loads.

Shared by `../../05-Engineering/electrical/electrical_docs.py` (CSV files,
calculations, wiring diagram) and `test_electrical_offline.py`. Lengths come
from the route model (`electrical_model.py`) wherever a route is modelled.

Every bought part stays on HOLD: no order, no supplier contact (guideline
4.3, AGENTS.md). Every number carries a status (conventions section 9).
The in-house Desk Pro AI sensor hub is cited by name only (D-09, D-11,
REQ-ELE-02): nothing about its insides goes in this public repo.
"""

import electrical_model as M

DATE = "2026-10-31"

# ------------------------------------------------------------------ supplies (DECIDED: three 60 W Class 2 units)
# id, part key, output, rated W, rated A, feeds, why
SUPPLIES = [
    ("PS1", "ps_cv", "12 V DC", 60.0, 5.0, "voice kit feed A, fused 5 A (REQ-VCK-04)",
     "the kit's 60 W peak on two Class 2 sources, so each runs at 80 % or less (PM ruling 2026-11-01): one 12 V Class 2 "
     "source gives at most 60 VA (NEC Chapter 9 Table 11(B): 5.0 x Vmax VA, 5.0 A)"),
    ("PS2", "ps_cv", "12 V DC", 60.0, 5.0, "all lights: uplight, down-light and call light, through the 3-channel light controller",
     "lights on their own source, so a light fault can't stall the fresh air; the hub holds the lights at about 22 W"),
    ("PS3", "ps_cv", "12 V DC", 60.0, 5.0, "four fans and the sensor hub (column fuse block)",
     "air and hub on their own source, so a lighting or kit fault can't stop the fresh air"),
    ("PS4", "ps_cv", "12 V DC", 60.0, 5.0, "voice kit feed B, fused 5 A (REQ-VCK-04)",
     "the kit's second feed, kept apart from feed A: two Class 2 sources are never joined (NEC 725)"),
]

# ------------------------------------------------------------------ loads (the load table)
# id, load, supply, branch fuse, qty, W each max, W each typical, status of W, source, note
FAN_W_MAX = 6.6        # Noctua's maximum input power, 0.55 A at 12 V (maker page via retailer copies, 2026-10-31: unverified)
LIGHT_BUDGET_W = 22.0  # DECIDED (PM 2026-11-01): uplight, down-light and call light together, the hub balancing them
KIT_PEAK_W = 60.0      # DECIDED (D-11, REQ-VCK-04): the voice kit's peak, all feeds together
KIT_FEED_W = 48.0      # DECIDED (PM 2026-11-01): the most the kit draws from one feed, 80 % of its 60 W supply
UP_M = 4.434                        # m: the uplight strip along the shelf (calculation, from the shelf's length)
UP_W = round(UP_M * 6.0, 1)       # 26.6 W, the uplight strip at full (calculation)
DOWN_ROW = 0.975                    # m: one down-light row, 39 sections of 25 mm, the longest that fits the 991 mm LED profile 718101 with room for the feed (D-126)
DOWN_W = round(2 * DOWN_ROW * 6.0, 1)  # 11.7 W, two rows of the down strip at full (calculation)
CALL_W = 2.7
UP_TYP = round(LIGHT_BUDGET_W - DOWN_W, 1)   # 10.3 W: the work scene, down-light full, the uplight takes the rest
FAN_W_53 = 2.6         # at about 73 % speed for 53 l/s (air report §7d): cube law 0.73^3 x 6.6 (calculation)
LOADS = [
    ("LD01", "Supply fan pair (2 x Noctua NF-A14 industrialPPC-3000 PWM), high in DR", "PS3", "F3a 2 A", 2,
     FAN_W_MAX, FAN_W_53, "unverified (max: maker figure read from retailer copies); calculation (typical, cube law at 73 % speed)",
     "selection F1; air report §7d", "PWM 1 from the hub; the fans run at full speed if the PWM line opens (fail-safe)"),
    ("LD02", "Exhaust fan pair (2 x the same fan), soffit right end", "PS3", "F3b 2 A", 2,
     FAN_W_MAX, 0.65 ** 3 * FAN_W_MAX, "unverified (max); calculation (typical, 65 % speed)",
     "selection F1; air report §7d", "PWM 2 from the hub (two signals, balanced flow, D-61)"),
    ("LD03", "Desk Pro AI sensor hub (in-house), air column zone", "PS3", "F3c 1 A", 1,
     5.0, 3.0, "assumption (ISS-060: in-house data still to collect)", "REQ-ELE-03, C8",
     "12 V input assumed; if the hub takes 5 V, a 12-to-5 V converter sits in the hub zone (HOLD H-ELE-08)"),
    ("LD04", "Call light, 900 mm bar of Häfele Loox5 2165 strip (3.0 W/m, about 155 lm/W)", "PS2", "light controller CH3", 1,
     CALL_W, 0.0, "calculation (0.9 m x 3.0 W/m, maker data)", "REQ-AIR-06, D-70; Häfele 25L1-18",
     "about 420 lm; on in the call scene, when the hub trims the down-light to stay inside the 22 W"),
    ("LD05", "Uplight on the light shelf, 4.434 m of Häfele Loox5 2168 (6.0 W/m, 970 lm/m at 3000 K: 162 lm/W)", "PS2",
     "light controller CH1", 1, UP_W, UP_TYP, "calculation (strip length from the model x 6.0 W/m; maker data)",
     "REQ-AIR-06, D-70; Häfele 25L1-18",
     "26.6 W and 4300 lm at full; in the work scene the hub runs it at 9.7 W, about 1570 lm"),
    ("LD08", "Down-light under the right-wall shelf, 2 rows x 0.975 m of Loox5 2168 side by side in the shelf's LED profile 718101 behind its satin cover, aimed at the ledge", "PS2",
     "light controller CH2", 1, DOWN_W, DOWN_W, "calculation (2 x 0.975 m x 6.0 W/m; maker data)",
     "PM ruling 2026-11-01 (down-light, about 22 W in all, about 300 lx on the ledge); Häfele 25L1-18",
     "about 1890 lm; about 333 lx on the ledge at full with no cover, about 286 to 300 lx through the satin cover at 86 to 90 % (D-127; calculation, Lambertian strip 1.2 m above it, no reflections)"),
    ("LD06", "Voice cockpit hook, feed A: 12 V, up to 48 W", "PS1", "F1 5 A", 1,
     KIT_FEED_W, 0.0, "DECIDED (D-11 peak; PM 2026-11-01: 80 % per feed)", "REQ-VCK-04; D-88",
     "the kit splits its 60 W peak (40 W average, D-88) over feeds A and B, at most 48 W on one; kit not fitted in v2, "
     "so 0 W typical"),
    ("LD09", "Voice cockpit hook, feed B: 12 V, up to 48 W", "PS4", "F4 5 A", 1,
     KIT_FEED_W, 0.0, "DECIDED (as LD06)", "REQ-VCK-04; D-88", "as LD06; the two feeds are never joined"),
    ("LD07", "Supply fan inlet temperature sensor", "PS3", "via the hub", 1,
     0.05, 0.05, "assumption", "REQ-ELE-04, D-50", "powered from the hub's sensor port"),
]

# ------------------------------------------------------------------ parts list
# key: part number, name, name_vi, kind (HS assembly, MP made, PI bought, HOLD),
# parent part number, qty per parent, material, finish, mass each kg, mass status,
# maker, sku, size, process, status, source, note
P = {}


def part(key, pn, name, vi, kind, parent, qty, material, finish, mass, mass_status, maker="", sku="",
         size="", process="", status="DRAFT", source="", note=""):
    if key in P:
        raise ValueError("part key used twice: " + key)
    P[key] = dict(part_number=pn, name=name, name_vi=vi, kind=kind, parent=parent, qty_per_parent=qty,
                  material=material, finish=finish, mass_each_kg=mass, mass_status=mass_status, maker=maker,
                  sku=sku, size=size, process=process, status=status, source=source, note=note)


HOLD_BUY = "HOLD (bought part: no order, no supplier contact; guideline 4.3)"

# ---- assemblies
part("ele", "710000", "ELECTRICAL", "Điện", "HS", "", 1, "", "", None, "calculation (sum of its parts)",
     source="assembly tree node 710000; D-10, D-11")
part("pu", "710001", "ELECTRICAL - POWER UNIT - B2", "Điện - hộp nguồn - vách sau B2", "HS", "710000", 1,
     "", "", None, "calculation (sum of its parts)", process="factory wired and tested in B2 (IF-12)",
     source="PM ruling 2026-10-31 (one earthed power unit in B2, factory wired)")
part("w_light", "710011", "ELECTRICAL - HARNESS - LIGHT FEED - B2/B4", "Điện - bó dây cấp đèn", "HS", "710000", 1,
     "", "", None, "calculation (sum of its parts)", process="harness assembly; segments clipped into B2-CASS and B4-CASS in the factory")
part("w_trunk", "710021", "ELECTRICAL - HARNESS - TRUNK - B2/R1", "Điện - bó dây chính", "HS", "710000", 1,
     "", "", None, "calculation (sum of its parts)", process="harness assembly; segments clipped into B2-CASS and R1-CASS in the factory")
part("w_col", "710023", "ELECTRICAL - HARNESS - AIR COLUMN", "Điện - bó dây cột gió", "HS", "710000", 1,
     "", "", None, "calculation (sum of its parts)", process="harness assembly; fitted in the column's chase in the factory")
part("w_call", "710024", "ELECTRICAL - HARNESS - CALL LIGHT - R2", "Điện - bó dây đèn gọi video", "HS", "710000", 1,
     "", "", None, "calculation (sum of its parts)", process="harness assembly; clipped into R2-CASS in the factory")
part("w_draw", "710031", "ELECTRICAL - DRAW WIRE - CEILING ROUTE", "Điện - dây mồi - đường trần", "HS", "710000", 1,
     "", "", None, "calculation (sum of its parts)",
     process="draw cords tied off at each hole (REQ-VCK-03): the ceiling route W33 and the column route W32")
part("hubzone", "710041", "ELECTRICAL - HUB AND CONTROLS ZONE", "Điện - vùng cảm biến và nút bấm", "HS", "710000", 1,
     "", "", None, "calculation (sum of its parts)", process="fitted in the air column's 180 x 180 zone (D-61, D-70)")
part("cord", "719001", "ELECTRICAL - CORD SET - 120 V US - 3 M (KIT)", "Điện - bộ dây nguồn 120 V (Mỹ) - 3 m", "HS", "710000", 1,
     "", "", None, "calculation (sum of its parts)", process="ships loose in the installation kit; US 120 V 60 Hz, 15 A (D-133): a NEMA 5-15P plug, SJOOW 14/3 cord and the powerCON TRUE1 cord connector, UL listed as a set (UL 817, HOLD)")


# ------------------------------------------------------------------ harness list
# Every joint between parts that are put up separately on site has a plug pair
# (D-26 rule, PM ruling: keyed plugs at every joint). Supply side = receptacle
# with female contacts; load side = plug with male contacts. Lengths: the
# modelled route (calculation) plus the pocket loops and tails (assumption).
PU_IN = 150.0          # mm of lead inside the power unit to its terminal (assumption)
TAIL = 150.0           # mm of tail beyond a grommet or slot, to mate the plugs before hanging (assumption)
LOOP = 150.0           # mm of slack loop in a pocket (= pk_l, assumption)
KIT_LOOP = 500.0       # mm service loop at the voice kit drop (assumption)
# LED strip feed leads (718053) at the harness ends: the back uplight fed both ways, the left jumper's two ends, the right
# jumper's back end, right uplight and the two down-light rows, the call bar (Reviewer 7: they had no parts line)
STRIP_FEEDS = {"W11a": 2, "W11b": 2, "W11c": 4, "W12": 1}

AWG16, AWG18, AWG20, AWG22, AWG24 = 1.31, 0.823, 0.519, 0.326, 0.205   # mm2 (source: AWG table)


def _len(v, *codes):
    tot = 0.0
    for c in codes:
        b = [x for x in M.BODIES if x["code"] == c][0]
        x0, y0, z0, x1, y1, z1 = M.body_box(b, v)
        tot += max(x1 - x0, y1 - y0, z1 - z0)
    return tot


LIGHT_A = LIGHT_BUDGET_W / 12.0   # the lights' 22 W, held by the hub (calculation); hardware max 41.6 W in the note
PS3_A = (4 * 6.6 + 5.0) / 12.0   # PS3's maximum: four fans and the hub (LD01-LD03), calculation


def harnesses(v):
    """Harness segments, in order along each circuit."""
    L = lambda *c: _len(v, *c)  # noqa: E731
    cross_top = v["cut_z1"] + v["tray_t"] - v["pu_z1"]
    cross_side = v["cut_x1"] + v["tray_t"] - v["pu_x1"]
    hub_rise = v["hub_zc"] - (v["trunk_z"] - v["grm_d"])
    up_chase = M.evaluate("col_z1", v) - v["hub_zc"]
    rows = []

    def add(**kw):
        kw.setdefault("parallel", 1)
        kw.setdefault("length_status", "calculation (route model) + assumption (loops and tails)")
        kw["length_mm"] = int(round(kw["length_mm"] / 10.0) * 10)
        rows.append(kw)

    # ---- mains and LAN, inside B2 and the power unit (factory wired, never touched on site)
    add(id="W01", harness_pn="710001", segment="PU", function="mains feed", frm="inlet (outside B2, v1 position)",
        to="breaker in the power unit", route="SLEEVE in B2's frame bay", circuit="mains 120 V",
        conductors="L, N, PE", cable="UL 1015 14 AWG single cores (black, white, green) in the sleeve", area_mm2=2.08,
        length_mm=L("SLEEVE") + 150 + 200, end_a="inlet terminals (powerCON TRUE1 TOP)", end_b="breaker, PE terminal",
        grommets="sleeve end bushes", amps_max=15.0,
        note="mains only inside B2 and the unit (D-10, IF-12); US 120 V 60 Hz, 15 A (D-133)")
    add(id="W02", harness_pn="710001", segment="PU", function="mains inside the unit",
        frm="breaker", to="GFCI receptacle; PS1, PS2, PS3 inputs", route="inside the power unit", circuit="mains 120 V",
        conductors="L, N (+ PE to the receptacle)", cable="UL 1015 14 AWG (black, white; green to the receptacle)",
        area_mm2=2.08, length_mm=1500,
        length_status="assumption (layout inside the unit)", end_a="breaker",
        end_b="GFCI receptacle LINE terminals; supply input leads in UL 486C lever connectors",
        grommets="", amps_max=15.0,
        note="supply inputs on the breaker side, not the GFCI's load side, so a trip leaves the 12 V side on; kept apart from the 12 V wiring")
    add(id="W03", harness_pn="710001", segment="PU", function="protective bond", frm="PE terminal",
        to="B2 frame (under a unit mounting bolt, serrated washer)", route="inside B2", circuit="PE",
        conductors="PE", cable="UL 1015 14 AWG green", area_mm2=2.08, length_mm=300,
        length_status="assumption", end_a="M6 ring lug, 16-14 AWG", end_b="M6 ring lug, 16-14 AWG", grommets="", amps_max=None,
        note="B2 is the only panel a mains part touches (compliance note 3)")
    add(id="W04", harness_pn="710001", segment="PU", function="LAN in", frm="etherCON feed-through (outside B2)",
        to="LAN keystone jack 1 (unit face)", route="SLEEVE in B2's frame bay", circuit="LAN",
        conductors="4 pairs", cable="Cat6 U/UTP patch cord", area_mm2=None, length_mm=L("SLEEVE") + 300,
        end_a="RJ45 plug into the feed-through", end_b="punched down at keystone jack 1", grommets="sleeve end bushes",
        amps_max=None, note="plan VT09; the building LAN comes in at v1's position")
    # ---- light feed (PS2) to the light shelf: PU -> B2-CASS -> B4-CASS -> shelf
    add(id="W10a", harness_pn="710001", segment="PU", function="light feed", frm="light controller outputs (PS2) via F2 5 A",
        to="pocket P5 in B2-CASS", route="out of the unit's top (bushed hole H03) straight up into B2-CASS's cable gap: the cut-out is plain, no steel on the path", circuit="PS2 lights",
        conductors="+12 V x 2, UP-, DOWN-, CALL-, spare", cable="6 x 18 AWG, Class 2 (CL2 or equivalent)", area_mm2=AWG18,
        length_mm=PU_IN + cross_top + LOOP, end_a="light controller terminals", end_b="Mini-Fit Jr 6-way receptacle",
        grommets="the unit's H03", amps_max=LIGHT_A,
        note="through the shelf's current sense (self-test, D-87); slack to the first clip: it crosses the 4 mm floating gap")
    add(id="W10b", harness_pn="710011", segment="B2-CASS", function="light feed", frm="P5", to="B2/B4 joint",
        route="P5, L1-B2, G-B2-B4", circuit="PS2 lights", conductors="+12 V x 2, UP-, DOWN-, CALL-, spare",
        cable="6 x 18 AWG, Class 2", area_mm2=AWG18, length_mm=80 + L("L1-B2", "G-B2-B4") + TAIL,
        end_a="Mini-Fit Jr 6-way plug (mates W10a)", end_b="Mini-Fit Jr 6-way receptacle (tail out of the top grommet)",
        grommets="G-B2-B4", amps_max=LIGHT_A, note="clipped to the cassette tray only (D-26)")
    add(id="W10c", harness_pn="710011", segment="B4-CASS", function="light feed", frm="P4 (above the joint)",
        to="P6 (shelf feed)", route="P4, L1-B4, P6, FX-SHELF", circuit="PS2 lights",
        conductors="+12 V x 2, UP-, DOWN-, CALL-, spare", cable="6 x 18 AWG, Class 2", area_mm2=AWG18,
        length_mm=LOOP + L("L1-B4") + 100 + 300,
        end_a="Mini-Fit Jr 6-way plug (mates W10b in P4)", end_b="Mini-Fit Jr 6-way receptacle, tail into the shelf",
        grommets="G-B2-B4, FX-SHELF", amps_max=LIGHT_A, note="")
    up_side_a = 1.051 * 6.0 / 12.0        # one side-wall uplight run at full (calculation)
    right_a = (DOWN_W + CALL_W) / 12.0 + up_side_a   # the right-wall jumper: down-light, call light, right uplight
    add(id="W11a", harness_pn="710011", segment="SHELF", function="light shelf feed lead",
        frm="P6 felt exit (X %.0f, Z %.0f)" % (v["lt_x"], v["shelf_z"]), to="back uplight feed point", route="FX-SHELF, the shelf's channel",
        circuit="PS2 lights", conductors="+12 V x 2, UP-, DOWN-, CALL-, spare", cable="6 x 18 AWG, Class 2", area_mm2=AWG18,
        length_mm=300, length_status="assumption", end_a="Mini-Fit Jr 6-way plug (mates W10c)",
        end_b="strip feeds: back uplight both ways; jumpers W11b, W11c", grommets="FX-SHELF", amps_max=LIGHT_A, note="")
    add(id="W11b", harness_pn="710011", segment="SHELF", function="jumper to the left wall uplight",
        frm="back feed point", to="left wall uplight, back end", route="the shelf's channel",
        circuit="PS2 lights", conductors="+12 V, UP-", cable="2 x 18 AWG, Class 2", area_mm2=AWG18,
        length_mm=v["lt_x"] + v["x_rf"] + 100, length_status="calculation (X %.0f to X -%.0f) + assumption (100)" % (v["lt_x"], v["x_rf"]),
        end_a="strip feed connector", end_b="strip feed connector", grommets="", amps_max=up_side_a, note="")
    add(id="W11c", harness_pn="710011", segment="SHELF", function="jumper to the right wall: uplight, down-light, call drop",
        frm="back feed point", to="right wall shelf: uplight, down-light rows, call drop at Y -209.5", route="the shelf's channel",
        circuit="PS2 lights", conductors="+12 V, UP-, DOWN-, CALL-", cable="4 x 18 AWG, Class 2", area_mm2=AWG18,
        length_mm=v["x_rf"] - v["lt_x"] + 100 + 300, length_status="calculation (X %.0f to X %.0f and along the right wall) + assumption" % (v["lt_x"], v["x_rf"]),
        end_a="strip feed connector", end_b="strip feed connectors; Mini-Fit Jr 2-way receptacle for the call drop (X6)",
        grommets="", amps_max=right_a,
        note="every strip run is 1.5 m or less, inside the maker's 3.5 m per feed; down-light rows fed in parallel")
    # ---- trunk: air feed (PS3), cockpit (PS1), dimming signal, Cat6: PU -> B2-CASS -> R1-CASS
    for wid, fn, circ, cond, cable, area, par, amps, endb in (
            ("W20", "air feed", "PS3 air", "+12 V x 2, 0 V x 2", "4 x 18 AWG (2 per pole), Class 2", AWG18, 2, PS3_A, "column fuse block"),
            ("W30", "voice kit feeds A and B", "PS1 and PS4 kit", "+12 V A, 0 V A, +12 V B, 0 V B",
             "4 x 16 AWG (one pair per feed), Class 2", AWG16, 1, KIT_FEED_W / 12.0, "kit drop"),
            ("W24", "hub link to the power unit", "hub I/O", "RS-485 A, B (to the light controller), 0 V, light current, PS1 and PS2 rail senses",
             "6 x 24 AWG screened, Class 2", AWG24, 1, 0.01, "hub I/O"),
            ("W31", "voice kit data", "LAN", "4 pairs", "Cat6 U/UTP", None, 1, None, "kit drop")):
        def end(kind):
            if wid == "W24":
                return "shares W20's 10-way %s" % kind
            if wid == "W31":
                return "RJ45 inline coupler"
            return "%s %s%s" % ({"W20": "Mini-Fit Jr 10-way", "W30": "Mini-Fit Jr 4-way"}[wid], kind,
                                " (with W24)" if wid == "W20" else "")
        add(id=wid + "a", harness_pn="710001", segment="PU", function=fn, frm="power unit",
            to="pocket P1 in B2-CASS", route="out of the unit's right side (bushed holes H01, H02) straight into B2-CASS's cable gap: the cut-out is plain", circuit=circ,
            conductors=cond, cable=cable, area_mm2=area, parallel=par, length_mm=PU_IN + cross_side + LOOP,
            end_a={"W20": "PS3 output", "W30": "F1 and F4, 5 A each (feeds A and B)", "W24": "light controller link, PS2 current sense, PS1 and PS2 rail taps",
                   "W31": "punched down at keystone jack 2 (unit face)"}[wid],
            end_b=end("receptacle"), grommets="the unit's H01/H02", amps_max=amps,
            note="slack to the first clip: it crosses the 4 mm floating gap, so no clip within 150 mm of the cut-out")
        add(id=wid + "b", harness_pn="710021", segment="B2-CASS", function=fn, frm="P1", to="back-right corner",
            route="P1, T1-B2, S-CNR", circuit=circ, conductors=cond, cable=cable, area_mm2=area, parallel=par,
            length_mm=LOOP + L("T1-B2") + TAIL, end_a=end("plug"),
            end_b=end("receptacle") + ", tail through the corner slot S-CNR",
            grommets="S-CNR (edge-protected slot)", amps_max=amps,
            note="the four cables pass the corner slot side by side")
        tail_c = {"W20": L("T1-R1A", "P3-KIT", "T1-R1B", "FX-COL") + TAIL,
                  "W24": L("T1-R1A", "P3-KIT", "T1-R1B", "FX-COL") + TAIL,
                  "W30": L("T1-R1A") + 75 + KIT_LOOP, "W31": L("T1-R1A") + 75 + KIT_LOOP}[wid]
        add(id=wid + "c", harness_pn="710021", segment="R1-CASS", function=fn, frm="P2 (corner, in R1-CASS)",
            to={"W20": "air column chase", "W24": "air column chase", "W30": "kit drop P3-KIT",
                "W31": "kit drop P3-KIT"}[wid],
            route={"W20": "P2, T1-R1A, T1-R1B, FX-COL", "W24": "P2, T1-R1A, T1-R1B, FX-COL",
                   "W30": "P2, T1-R1A, P3-KIT", "W31": "P2, T1-R1A, P3-KIT"}[wid],
            circuit=circ, conductors=cond, cable=cable, area_mm2=area, parallel=par, length_mm=LOOP + tail_c,
            end_a=end("plug") + (" (mated in P2 through the felt slot FS-CNR)" if wid != "W31" else " (in P2)"),
            end_b={"W20": "Mini-Fit Jr 10-way receptacle (with W24), tail into the column",
                   "W24": "shares W20's 10-way receptacle",
                   "W30": "Mini-Fit Jr 4-way receptacle, capped with an empty plug housing (the kit outlet: two 12 V feeds, 5 A fuse and up to 48 W each, never joined)",
                   "W31": "RJ45 keystone jack, capped (the kit's data link)"}[wid],
            grommets={"W20": "FS-CNR, FX-COL", "W24": "FS-CNR, FX-COL", "W30": "FS-CNR", "W31": "FS-CNR"}[wid],
            amps_max=amps, note={"W30": "REQ-VCK-04: fused 12 V 5 A outlet; reached through the felt plug FA-KIT",
                                 "W31": "REQ-VCK-05: data link to the kit zone"}.get(wid, ""))
    # ---- air column (factory fitted in the column's chase)
    add(id="W20d", harness_pn="710023", segment="COLUMN", function="air feed", frm="chase entry",
        to="column fuse block (behind the hub zone cover)", route="CHASE", circuit="PS3 air",
        conductors="+12 V x 2, 0 V x 2", cable="4 x 18 AWG (2 per pole), Class 2", area_mm2=AWG18, parallel=2,
        length_mm=LOOP + hub_rise + 150, end_a="Mini-Fit Jr 10-way plug (with W24d), mates W20c behind the column",
        end_b="fuse block input", grommets="", amps_max=PS3_A, note="F3a 2 A, F3b 2 A, F3c 1 A, F3d 1 A in the column")
    add(id="W24d", harness_pn="710023", segment="COLUMN", function="hub link to the power unit", frm="chase entry",
        to="hub I/O (hub zone)", route="CHASE", circuit="hub I/O",
        conductors="RS-485 A, B, 0 V, light current, PS1 and PS2 rail senses", cable="6 x 24 AWG screened",
        area_mm2=AWG24, length_mm=LOOP + hub_rise + 150, end_a="shares W20d's 10-way plug",
        end_b="hub I/O (HOLD H-ELE-05)", grommets="", amps_max=0.01,
        note="the hub sets the three light channels over RS-485, reads PS2's current and every 12 V rail for the self-test (D-87)")
    add(id="W40", harness_pn="710023", segment="COLUMN", function="supply fan pair", frm="F3a 2 A + hub PWM 1, tach 1",
        to="supply fan box, high in DR", route="CHASE, TO-DR", circuit="PS3 fan S",
        conductors="+12 V, 0 V, PWM, tach", cable="4 x 20 AWG", area_mm2=AWG20,
        length_mm=up_chase + L("TO-DR") + 300, end_a="fuse block and hub terminals",
        end_b="4-way PWM fan connector into a Y-cable at the fan pair (housing HOLD H-ELE-07)",
        grommets="G-DR", amps_max=2 * FAN_W_MAX / 12.0,
        note="PWM fail-safe: an open PWM line runs the fans at full speed")
    add(id="W41", harness_pn="710023", segment="COLUMN", function="exhaust fan pair", frm="F3b 2 A + hub PWM 2, tach 2",
        to="exhaust fan box, soffit right end", route="CHASE, TO-SOFFIT", circuit="PS3 fan E",
        conductors="+12 V, 0 V, PWM, tach", cable="4 x 20 AWG", area_mm2=AWG20,
        length_mm=up_chase + L("TO-SOFFIT") + 300, end_a="fuse block and hub terminals",
        end_b="4-way PWM fan connector into a Y-cable (housing HOLD H-ELE-07)", grommets="G-SOFFIT",
        amps_max=2 * FAN_W_MAX / 12.0, note="two signals, balanced flow (D-61)")
    add(id="W42", harness_pn="710023", segment="COLUMN", function="inlet temperature sensor",
        frm="hub sensor port", to="supply fan box inlet (DR)", route="CHASE, TO-DR", circuit="hub sensor",
        conductors="4 cores (sensor supply, ground, two signal)", cable="4 x 24 AWG screened", area_mm2=AWG24,
        length_mm=up_chase + L("TO-DR") + 500, end_a="hub sensor connector (HOLD, ISS-060)",
        end_b="sensor probe (HOLD H-ELE-06)", grommets="G-DR", amps_max=None,
        note="the 4 K limit's room reading (D-50, REQ-ELE-04)")
    add(id="W43", harness_pn="710023", segment="COLUMN", function="hub supply", frm="F3c 1 A", to="sensor hub",
        route="hub zone", circuit="PS3 hub", conductors="+12 V, 0 V", cable="2 x 18 AWG, Class 2", area_mm2=AWG18,
        length_mm=300, length_status="assumption", end_a="fuse block", end_b="hub power connector (HOLD, ISS-060)",
        grommets="", amps_max=5.0 / 12.0, note="")
    add(id="W44", harness_pn="710023", segment="COLUMN", function="controls loom", frm="BOOST, TEST, CALL buttons and the LIGHT knob",
        to="hub inputs", route="hub zone", circuit="hub I/O", conductors="BOOST, TEST, CALL, common, knob wiper, knob reference",
        cable="6 x 24 AWG screened", area_mm2=AWG24, length_mm=300, length_status="assumption", end_a="button and knob tags",
        end_b="hub inputs (HOLD H-ELE-05)", grommets="", amps_max=None,
        note="boost by hand (D-33); TEST runs the self-test (D-87)")
    add(id="W12", harness_pn="710024", segment="R2-CASS", function="call light drop",
        frm="the shelf's call branch at FX-CALL0 (behind the shelf, Y -209.5)", to="call light bar (Y -209.5, Z 1450)",
        route="FX-CALL0, P7, CALL-R2, FX-CALL2", circuit="PS2 lights", conductors="+12 V, CALL-",
        cable="2 x 18 AWG, Class 2", area_mm2=AWG18, length_mm=TAIL + LOOP + L("CALL-R2", "FX-CALL2") + 300,
        end_a="Mini-Fit Jr 2-way plug (mates W11c's call branch in P7)", end_b="strip feed of the call bar",
        grommets="FX-CALL0, FX-CALL2 (felt only)", amps_max=CALL_W / 12.0, note="")
    # ---- draw wires (REQ-VCK-03): a cord in each cassette or column segment, tied off at its holes
    add(id="W32", harness_pn="710031", segment="R1-CASS + COLUMN", function="draw wire: kit zone to the soffit (mic, status light)",
        frm="kit drop P3-KIT", to="soffit right end", route="T1-R1B, FX-COL, CHASE, TO-SOFFIT", circuit="reserve",
        conductors="cord", cable="nylon draw cord 3 mm", area_mm2=None,
        length_mm=L("T1-R1B", "FX-COL", "CHASE", "TO-SOFFIT") + 2 * TAIL, end_a="tied at P3-KIT",
        end_b="tied at the soffit entry", grommets="FX-COL, G-SOFFIT", amps_max=None, note="REQ-VCK-02, -03")
    add(id="W33", harness_pn="710031", segment="B4-CASS + CEILING", function="draw wire: ceiling route (D-41)",
        frm="shelf feed pocket P6", to="soffit back face, top", route="C1-UP, C1-JOG, C1-RISE, FX-CEIL, G-CEIL-B, C1-CEIL, G-CEIL-F",
        circuit="reserve", conductors="cord", cable="nylon draw cord 3 mm", area_mm2=None,
        length_mm=L("C1-UP", "C1-JOG", "C1-RISE", "FX-CEIL", "G-CEIL-B", "C1-CEIL", "G-CEIL-F") + 2 * TAIL,
        end_a="tied at P6", end_b="tied at the ceiling cassette's front hole", grommets="FX-CEIL, G-CEIL-B, G-CEIL-F",
        amps_max=None, note="also the wiring point reserved for a sprinkler or alarm signal (ISS-052)")
    for r in rows:
        r["from"] = r.pop("frm")
    return rows


# ------------------------------------------------------------------ data the calculations use
PARTS_DATA = {
    "ps_eff": 0.83,          # source: Mean Well LPV-60 datasheet (PWM-60: 0.86); the lower one, for heat and input current
    "ps_noload_w": 0.5,      # assumption: PWM-60 standby under 0.5 W (source); LPV-60 not stated
    "b2_outer_kg": 9.1,      # calculation: CEILING P01's frame 1.829 and skin 3.500 kg/m2 (PR #32) x B2's 1.343 m2,
                             # + 40 mm fill at 25 kg/m3 (D-81) 1.34 + bond 0.34 + joint hardware 0.3 (assumptions)
}

LKP = "maker page or datasheet, read 2026-10-31"
MW_LPV = "https://www.meanwellusa.com/upload/pdf/LPV-60/LPV-60-spec.pdf (rev 2026-09-07)"
MW_PWM = "Mean Well PWM-60 datasheet rev 2026-02-04 (copy: https://www.simpex.ch/wp-content/uploads/2025/02/PWM-60-spec-SI.pdf)"
MOLEX = "Molex PS-5556-001 rev E8 and Digi-Key part pages"
NEUTRIK = "https://www.neutrik.com/en/product/nac3mpx-top ; https://www.neutrik.com/en/product/ne8fdp"
HEYCO = "https://www.heyco.com/products/bushings-grommets-heycaps-plugs/tubing-caps-and-plugs/heyco-shorty-bushings"
HAFELE = "https://files.hafele.co.uk/CatalogFiles/www/25L1-18.pdf"
SE = "https://www.se.com/vn/en/product/A9D32610/"
EATON_FAZ = "Eaton FAZ-NA UL 489 brochure (https://www.multiwaycontrol.com/multiway/FAZ_circuit_breaker_UL489_Eaton.pdf): 17.7 mm per pole, 70.5 mm deep; retailer listing FAZ-C15/1-NA-L-SP, read 2026-11-01"
GFCI_SRC = "Pass & Seymour 1595TR series brochure (USESI 103691: 1.72 x 4.20 in, 1.13 in deep), Legrand 1597 pages, read 2026-11-01"
SEL = "v2/05-Engineering/hardware/selection.md"
JNT = "v2/05-Engineering/joints/joints-register.md 2.1"
AL = "aluminium 5052-H32"

# ---- power unit 710001: made parts
part("pu_body", "711001", "ELECTRICAL - POWER UNIT - ENCLOSURE BODY", "Điện - hộp nguồn - thân hộp", "MP", "710001", 1,
     AL + " 1.0 mm", "mill finish (hidden, D-79)", 0.465, "CAD (Fusion volume 173,340 mm3 x 2.68 g/cm3, 711001 P01 design)",
     size="296 x 260 x 72, 25 mm side flanges", process="sheet metal: laser cut, folded",
     status="DRAFT; HOLD features: the fixing to B2's frame (WALL, IF-12) and the earth stud hole (PEM data)",
     source="711001_P01_ELECTRICAL-POWER-UNIT-ENCLOSURE-BODY_CAD (electrical_parts_cad.py)",
     note="folded tray 296 x 260 x 72 with 22 mm front lips; two Ø19.1 lead exits (right), Ø19.1 light feed exit (top), "
          "Ø25 sleeve entry (bottom), 4 M4 clinch nut holes in the lips")
part("pu_front", "711002", "ELECTRICAL - POWER UNIT - FRONT PLATE", "Điện - hộp nguồn - mặt trước", "MP", "710001", 1,
     AL + " 1.5 mm", "black anodised AA20 (visible aluminium, D-67)", 0.344,
     "CAD (Fusion volume 128,264 mm3 x 2.68 g/cm3, 711002 P01 design, D-133 rebuild)", size="320 x 284",
     process="laser cut from 1.5 mm sheet as a flat plate; anodised", status="DRAFT; HOLD features: the GFCI receptacle's decorator opening and the two keystone openings, set by the picked parts' drawings (D-133)",
     source="711002_P01_ELECTRICAL-POWER-UNIT-FRONT-PLATE_CAD; DXF 711002_P01_ELECTRICAL-POWER-UNIT-FRONT-PLATE_DXF.dxf (no drawing, D-89 part 4)",
     note="flat plate, its DXF gives the full outline and every hole (D-89 part 4); thickness 1.5 mm; general tolerance "
          "ISO 2768-m; covers B2-CASS's cut felt edge 8 mm all round and stands 2 mm off the felt on 4 spacers (718049); critical holes: "
          "the 4 x Ø4.5 M4 holes on the body's clinch nuts (42 and 23 mm from the plate's edges, true "
          "position Ø0.3), the breaker window 19 x 45 +0.5/0; HOLD: the GFCI receptacle's decorator opening 33.6 x 67 "
          "with its two 6-32 plate screw holes 96.8 apart, and the two keystone openings 14.9 x 19.4 (D-133)")
# ---- power unit 710001: bought parts
part("ps_cv", "718001", "ELECTRICAL - 12 V SUPPLY - 60 W CLASS 2", "Điện - nguồn 12 V 60 W", "PI", "710001", 4,
     "potted plastic case, IP67", "", 0.40, "source", maker="Mean Well", sku="LPV-60-12",
     size="162.5 x 42.5 x 32", status=HOLD_BUY, source=MW_LPV,
     note="PS1 and PS4 (the kit's feeds A and B), PS2 (lights, through the light controller) and PS3 (air, hub). 12 V 0-5 A; 90-264 VAC; 83 %; 'Class 2 power unit', UL1310, Class II; "
          "inrush 60 A 525 us at 230 VAC. The maker says not for LED luminaires in the EU or China: check PS2 before an EU version")
part("lightctl", "718002", "ELECTRICAL - LED CONTROLLER - 3 CHANNEL 12 V PWM - RS-485", "Điện - bộ điều khiển đèn 3 kênh",
     "PI", "710001", 1, "", "", 0.10, "assumption", sku="maker HOLD (H-ELE-14)", status=HOLD_BUY,
     source="PM ruling 2026-11-01 (the hub balances uplight, down-light and call light at about 22 W)",
     note="constant-voltage PWM dimmer for 12 V strips, 3 channels (uplight, down-light, call), at least 3 A per channel, "
          "common +12 V, set by the hub over RS-485 (DMX or Modbus); on a lost link it holds its level or goes dark, never brighter")
part("rcbo", "718003", "ELECTRICAL - CIRCUIT BREAKER - 1P 15 A C - UL 489", "Điện - CB 1 cực 15 A (UL 489)", "PI", "710001", 1,
     "", "", 0.12, "assumption", maker="Eaton", sku="FAZ-C15/1-NA-L (UL 489, 1 pole, 15 A, C curve; or equal)",
     size="17.7 W x 70.5 D, DIN rail", status=HOLD_BUY, source=EATON_FAZ,
     note="D-133: US 120 V 60 Hz. UL 489 branch circuit breaker (interrupting rating at 120 V to confirm on the listing); "
          "protects the 14 AWG mains wiring at 15 A (NEC 240.4(D)); C curve for the three supplies' inrush. "
          "The GFCI receptacle 718007 gives the user outlets the personnel protection the RCBO gave")
part("inlet", "718004", "ELECTRICAL - APPLIANCE INLET - POWERCON TRUE1 TOP", "Điện - ổ cắm nguồn vào", "PI", "710001", 1,
     "", "", 0.05, "assumption", maker="Neutrik", sku="NAC3MPX-TOP", size="flange 26 x 31 x 4.5; 31.2 behind",
     status=HOLD_BUY, source=NEUTRIK + "; " + SEL,
     note="UL 498 certified (Neutrik's page names UL file E343813); 20 A in the US (retailer listings give 20 A at 120 VAC; the UL rating to "
          "confirm on the certificate, H-ELE-03); used at 120 V 60 Hz, 15 A (D-133); plug or unplug under load; UL94 V-0; IP65 mated or capped. "
          "In B2's skin at X 120, Z 313 (v1's spot moved off the closing seam); panel range to confirm (H-ELE-03)")
part("inlet_cap", "718005", "ELECTRICAL - INLET SEALING CAP", "Điện - nắp che ổ nguồn vào", "PI", "710001", 1,
     "", "", 0.01, "assumption", maker="Neutrik", sku="SCNAC-01 (as named in selection E; confirm)", status=HOLD_BUY,
     source=SEL, note="keeps IP65 while unplugged")
part("lan_ft", "718006", "ELECTRICAL - LAN FEED-THROUGH - ETHERCON", "Điện - ổ mạng xuyên vách", "PI", "710001", 1,
     "", "", 0.04, "assumption", maker="Neutrik", sku="NE8FDP", size="flange 26 x 31; 34.55 behind",
     status=HOLD_BUY, source=NEUTRIK + "; " + SEL, note="CAT5e coupler (so the link is CAT5e); panel up to 4 mm")
part("socket", "718007", "ELECTRICAL - RECEPTACLE - GFCI TR DUPLEX 15 A - NEMA 5-15R", "Điện - ổ cắm đôi chống giật GFCI NEMA 5-15R",
     "PI", "710001", 1, "", "", 0.25, "assumption", maker="Pass & Seymour (Legrand)",
     sku="1595TRW (15 A 125 V, tamper-resistant, self-test, UL 943 Class A; or equal: Eaton TRSGF15W, Leviton GFTR1)",
     size="decorator face 33.3 x 66.7; strap 43.7 x 106.7; 28.7 behind the strap", status=HOLD_BUY, source=GFCI_SRC,
     note="D-133: the pod's user outlets, two NEMA 5-15R, tamper-resistant (NEC 406.12), GFCI trips at 4 to 6 mA (UL 943 Class A). "
          "On the unit face: its strap behind the front plate, held by two 6-32 plate screws (718054), the earthed enclosure as its box; "
          "fed from the breaker's side; replaces the UTEN S300 socket (plan VT07)")
# 718008 (UTEN two-port LAN socket) and 718009 (86 back box) are retired by D-133: the keystone jacks snap into the
# front plate, and the GFCI receptacle needs no box. A retired number is never used again.
RETIRED = {"718008": "D-133: LAN keystone jacks in the front plate", "718009": "D-133: no 86 back box"}
part("dinrail", "718010", "ELECTRICAL - DIN RAIL - TS35 X 7.5 - 100 MM", "Điện - thanh ray DIN", "PI", "710001", 1,
     "steel", "zinc plated", 0.03, "assumption", maker="Phoenix Contact", sku="NS 35/7,5 PERF 2000MM, 0801733, cut to 100 (unverified)",
     status=HOLD_BUY, source="EN 60715 TS35", note="carries the breaker")
part("fuseholder", "718011", "ELECTRICAL - FUSE HOLDER - ATO BLADE - INLINE", "Điện - đế cầu chì lưỡi", "PI", "710001", 3,
     "", "", 0.01, "assumption", sku="HOLD (H-ELE-11)", status=HOLD_BUY, source="ISO 8820-3 blade fuses",
     note="F1, F2 and F4")
part("fuse5", "718012", "ELECTRICAL - FUSE - ATO 5 A 32 V", "Điện - cầu chì 5 A", "PI", "710001", 2, "", "", 0.002,
     "assumption", maker="Littelfuse", sku="0287005 (ATO 287 series; unverified)", status=HOLD_BUY,
     source="ISO 8820-3", note="F1 and F4, the voice kit outlet's feeds A and B (REQ-VCK-04)")
part("fuse3", "718013", "ELECTRICAL - FUSE - ATO 5 A 32 V - LIGHTS", "Điện - cầu chì 5 A đèn", "PI", "710001", 1, "", "", 0.002,
     "assumption", maker="Littelfuse", sku="0287005 (unverified)", status=HOLD_BUY, source="ISO 8820-3",
     note="F2, the light controller's feed (hardware max 41.6 W)")
part("m4screw", "718019", "ELECTRICAL - SCREW - M4 X 8 - ISO 7045 A2 PAN HEAD", "Điện - vít M4 x 8 inox", "PI", "710001", 4,
     "stainless steel", "plain (A2 stainless)", 0.0015, "assumption", maker="HOLD: standard part",
     sku="ISO 7045 M4 x 8 H, A2-70", size="M4", status=HOLD_BUY, source="this design (README section 3)",
     note="the front plate onto the body's lips")
P["m4screw"].update(length_mm="8", grade="A2-70", torque_nm="HOLD (set on the first unit: A2 M4 into a clinch nut in 1.0 mm aluminium)")
part("m4spacer", "718049", "ELECTRICAL - SPACER - M4 X 2 MM - NYLON, BLACK", "Điện - vòng đệm cách M4 x 2", "PI", "710001", 4,
     "nylon 6/6", "black, as supplied", 0.0002, "assumption", maker="HOLD: standard part",
     sku="M4 round spacer 4.3 ID x 8 OD x 2 mm", size="M4 x 2", status=HOLD_BUY, source="this design (README section 3)",
     note="under the front plate at its 4 screws: the plate stands 2 mm off the felt, so the floating lining never touches the unit (D-17)")
P["m4spacer"].update(length_mm="2")
part("plate_screw", "718054", "ELECTRICAL - SCREW - 6-32 X 1/2 - OVAL HEAD, BLACK", "Điện - vít 6-32 x 1/2 đầu dù, đen", "PI",
     "710001", 2, "steel", "black oxide", 0.001, "assumption", maker="HOLD: standard part",
     sku="6-32 UNC x 1/2 in oval head slotted (a decorator wallplate screw)", size="6-32", status=HOLD_BUY,
     source="decorator wallplates: two 6-32 screws 3-13/16 in (96.8 mm) apart into the device strap",
     note="D-133: the GFCI receptacle's strap to the front plate, the plate acting as its wallplate")
P["plate_screw"].update(length_mm="12.7")
part("m4nut", "718047", "ELECTRICAL - CLINCH NUT - M4 - FOR 1.0 MM ALUMINIUM", "Điện - đai ốc ép M4", "PI", "710001", 4,
     "aluminium", "plain, as supplied", 0.0008, "assumption", maker="PennEngineering",
     sku="CLA-M4-1 (unverified: the aluminium clinch nut for 1.0 mm sheet)", size="M4", status=HOLD_BUY,
     source="PEM catalogue", note="pressed into the body's lips")
P["m4nut"].update(grade="aluminium", torque_nm="HOLD (as the screw)")
part("pestud", "718014", "ELECTRICAL - EARTH STUD - M5 SELF-CLINCHING", "Điện - vít tiếp địa M5", "PI", "710001", 1,
     "aluminium", "plain, as supplied", 0.005, "assumption", maker="PennEngineering", sku="FHA-M5-12 (unverified)", status=HOLD_BUY,
     source="PEM catalogue", note="the enclosure's PE point: inlet, socket and bond lugs")
part("serrated", "718015", "ELECTRICAL - BONDING WASHER - SERRATED M6 A2", "Điện - long đen răng tiếp địa", "PI", "710001", 1,
     "stainless A2", "", 0.001, "assumption", sku="DIN 6798 A 6.4 A2, maker HOLD", status=HOLD_BUY, source="DIN 6798",
     note="under the bond lead's lug on one mounting bolt, so the lug bites through to bare aluminium")
part("lug", "718016", "ELECTRICAL - RING TERMINAL - INSULATED 16-14 AWG", "Điện - đầu cos tròn 16-14 AWG", "PI", "710001", 5,
     "tinned copper", "", 0.001, "assumption", sku="16-14 AWG, #10 (M5) x 4, 1/4 in (M6) x 1, UL 486A-486B listed; maker HOLD",
     status=HOLD_BUY, source="", note="PE lugs (D-133: 14 AWG)")
part("sleeve", "718017", "ELECTRICAL - CONDUIT - FLEXIBLE NONMETALLIC 1/2 IN", "Điện - ống luồn dây mềm 1/2 in", "PI", "710001", 0.6,
     "PVC, UL 1660 liquidtight flexible nonmetallic (LFNC-B)", "", 0.08, "assumption (kg per m)",
     sku="trade size 1/2 (21.3 OD); maker HOLD", status=HOLD_BUY, source="",
     note="the sleeve in B2's bay, inlet to unit, 0.57 m (route model); its end bushes in the inlet and the unit's Ø25 entry H04 HOLD "
          "(H-ELE-03); qty in m")
part("bolt", "838001", "HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC", "Bulong lục giác chìm M6 × 16", "PI",
     "710001", 4, "steel", "zinc plated", 0.0055, "assumption", maker="HOLD: standard part, maker picked with the joints register",
     sku="ISO 4762 M6 x 16, 8.8, zinc plated", size="M6", status=HOLD_BUY, source=JNT,
     note="the unit's 4 fixings into B2's members: the pod's one bolt, one 5 mm key (D-63)")
P["bolt"].update(length_mm="16", grade="8.8", torque_nm="HOLD (D-48: set by the rivnut spin-out test T06)")
part("washer", "838004", "HARDWARE - WASHER - M6 LARGE - ISO 7093-1 6.4 X 18 A2", "Long đen to M6 inox", "PI", "710001", 4,
     "stainless steel", "plain (A2 stainless)", 0.0028, "assumption",
     maker="HOLD: standard part, maker picked with the joints register", sku="ISO 7093-1 6.4 x 18 x 1.6, A2", size="M6",
     status=HOLD_BUY, source=JNT)
P["washer"].update(grade="A2")
part("rivnut", "838003", "HARDWARE - RIVET NUT - M6 - SHEREX CAH3-610-4.2", "Tán rút M6", "PI", "710001", 4,
     "aluminium", "plain, as supplied", 0.003, "assumption", maker="Sherex", sku="CAH3-610-4.2", size="M6",
     status=HOLD_BUY, source=JNT,
     note="set in B2's vertical members by the factory before the unit goes in (WALL's frame drawing shows the holes)")
P["rivnut"].update(grade="5056", torque_nm="HOLD (D-48: spin-out test T06)", length_mm="14.86")

# ---- wire and cable by length (unit: m; mass each = kg per m)
def cable(key, pn, name, vi, parent, metres, kgm, sku, note):
    part(key, pn, name, vi, "PI", parent, round(metres, 2), "", "", kgm, "assumption (kg per m, typical catalogue value)",
         sku=sku, status=HOLD_BUY, note=note + "; qty in m")


def _m(ids):
    import electrical_model as _M
    v = _M.values()
    rows = {h["id"]: h for h in harnesses(v)}
    return sum(rows[i]["length_mm"] for i in ids) / 1000.0


cable("w15", "718020", "ELECTRICAL - WIRE - UL 1015 14 AWG (BLACK, WHITE, GREEN)", "Điện - dây đơn UL 1015 14 AWG (đen, trắng, xanh lá)",
      "710001", 3 * _m(["W01"]), 0.025, "maker HOLD: UL 1015 AWM, 600 V, 105 °C, stranded copper",
      "W01: L, N, PE in the sleeve (D-133: sized for 15 A)")
cable("w10", "718021", "ELECTRICAL - WIRE - UL 1015 14 AWG (BLACK, WHITE)", "Điện - dây đơn UL 1015 14 AWG (đen, trắng)", "710001",
      1.5, 0.025, "maker HOLD: as 718020", "W02 inside the unit (assumption; D-133: sized for 15 A)")
cable("w25", "718022", "ELECTRICAL - WIRE - UL 1015 14 AWG GREEN", "Điện - dây tiếp địa UL 1015 14 AWG", "710001", 0.3, 0.025,
      "maker HOLD: as 718020", "W03 bond lead (D-133: 14 AWG, the equipment ground for a 15 A circuit, NEC 250.122)")
cable("c218", "718023", "ELECTRICAL - CABLE - 2 X 18 AWG - CLASS 2", "Điện - cáp 2 x 18 AWG", "710000",
      _m(["W11b", "W12", "W43"]), 0.025,  # W43's row said 2 x 22 AWG, which had no line (Reviewer 7): it is this cable
      "maker HOLD: 300 V PVC, CL2 or CL3 listed for the US phase", "12 V feeds")
cable("c418", "718024", "ELECTRICAL - CABLE - 4 X 18 AWG - CLASS 2", "Điện - cáp 4 x 18 AWG", "710000",
      _m(["W20a", "W20b", "W20c", "W20d", "W11c"]), 0.045, "maker HOLD: as 718023",
      "the air feed (2 cores per pole), the right-wall light jumper")
cable("c416", "718055", "ELECTRICAL - CABLE - 4 X 16 AWG - CLASS 2", "Điện - cáp 4 x 16 AWG", "710000",
      _m(["W30a", "W30b", "W30c"]), 0.065, "maker HOLD: 300 V PVC, CL2 or CL3 listed",
      "the voice kit's feeds A and B, one pair each: 16 AWG keeps the drop at a feed's 4 A within 3 % (calc-results)")
cable("c618", "718029", "ELECTRICAL - CABLE - 6 X 18 AWG - CLASS 2", "Điện - cáp 6 x 18 AWG", "710000",
      _m(["W10a", "W10b", "W10c", "W11a"]), 0.065, "maker HOLD: as 718023", "the light feed: +12 V x 2 and the three channel returns")
cable("c624", "718025", "ELECTRICAL - CABLE - 6 X 24 AWG SCREENED - CLASS 2", "Điện - cáp tín hiệu 6 x 24 AWG", "710000",
      _m(["W24a", "W24b", "W24c", "W24d", "W44"]), 0.035, "maker HOLD", "the hub's link to the power unit, and the controls loom")
cable("c420", "718026", "ELECTRICAL - CABLE - 4 X 20 AWG", "Điện - cáp quạt 4 x 20 AWG", "710023",
      _m(["W40", "W41"]), 0.035, "maker HOLD", "fan leads: 12 V, 0 V, PWM, tach")
cable("c424", "718027", "ELECTRICAL - CABLE - 4 X 24 AWG SCREENED", "Điện - cáp cảm biến 4 x 24 AWG", "710023",
      _m(["W42"]), 0.030, "maker HOLD", "inlet temperature sensor")
cable("cat6", "718028", "ELECTRICAL - CABLE - CAT6 U/UTP", "Điện - cáp mạng Cat6", "710000",
      _m(["W04", "W31a", "W31b", "W31c"]), 0.040, "maker HOLD", "LAN in and the kit tie line")

# ---- plugs, terminals and RJ45 parts, counted joint by joint (harness list ends)
for key, pn, name, vi, parent, qty, sku, mass, note in (
        ("rec2", "718030", "ELECTRICAL - CONNECTOR - MINI-FIT JR RECEPTACLE 2 WAY V-0", "Điện - giắc cái 2 chân", "710000", 1,
         "39-01-2025", 0.0015, "supply side of X6, the call light drop"),
        ("plug2", "718031", "ELECTRICAL - CONNECTOR - MINI-FIT JR PLUG 2 WAY V-0", "Điện - giắc đực 2 chân", "710000", 1,
         "39-01-3029", 0.0015, "load side of X6"),
        ("rec6", "718045", "ELECTRICAL - CONNECTOR - MINI-FIT JR RECEPTACLE 6 WAY V-0", "Điện - giắc cái 6 chân", "710000", 3,
         "39-01-2065", 0.0035, "the light feed at X1 (unit top), X4 (B2/B4) and X5 (shelf)"),
        ("plug6", "718046", "ELECTRICAL - CONNECTOR - MINI-FIT JR PLUG 6 WAY V-0", "Điện - giắc đực 6 chân", "710000", 3,
         "39-01-3069", 0.0035, "the same joints"),
        ("rec4", "718032", "ELECTRICAL - CONNECTOR - MINI-FIT JR RECEPTACLE 4 WAY V-0", "Điện - giắc cái 4 chân", "710000", 3,
         "39-01-2045", 0.0025, "the voice kit's feeds A and B at X1 and X2, and the kit outlet X7 (16 AWG terminals 718056)"),
        ("plug4", "718033", "ELECTRICAL - CONNECTOR - MINI-FIT JR PLUG 4 WAY V-0", "Điện - giắc đực 4 chân", "710000", 3,
         "39-01-3049", 0.0025, "X1, X2, and one empty housing as the kit outlet's cap"),
        ("rec10", "718034", "ELECTRICAL - CONNECTOR - MINI-FIT JR RECEPTACLE 10 WAY V-0", "Điện - giắc cái 10 chân", "710000", 3,
         "39-01-2105", 0.005,
         "air feed (2 + 2) and the hub link (6) in one housing at X1, X2, X3"),
        ("plug10", "718035", "ELECTRICAL - CONNECTOR - MINI-FIT JR PLUG 10 WAY V-0", "Điện - giắc đực 10 chân", "710000", 3,
         "39-01-3109", 0.005, "the same joints"),
        ("term_f", "718036", "ELECTRICAL - TERMINAL - MINI-FIT JR FEMALE 18-24 AWG TIN", "Điện - chân giắc cái", "710000", 32,
         "39-00-0039", 0.0003, "1 x 2 + 3 x 6 + 3 x 4, the 18 AWG cores (the 4-way housings take 718056, the hub link's "
         "24 AWG cores 718077)"),
        ("term_m", "718037", "ELECTRICAL - TERMINAL - MINI-FIT JR MALE 18-24 AWG TIN", "Điện - chân giắc đực", "710000", 32,
         "39-00-0041", 0.0003, "1 x 2 + 3 x 6 + 3 x 4, the 18 AWG cores (the 4-way housings take 718057, the hub link's "
         "24 AWG cores 718078)")):
    part(key, pn, name, vi, "PI", parent, qty, "nylon UL94 V-0" if "term" not in key else "tin-plated brass", "", mass,
         "assumption", maker="Molex", sku=sku, status=HOLD_BUY, source=MOLEX,
         note=note + "; 18 AWG: 9 A (2 way), 8 A (4 and 6 way) per circuit, 600 V; UL E29179 (10 way: rating to confirm)")
for key, pn, name, vi, qty, note in (
        ("rj45", "718038", "ELECTRICAL - RJ45 PLUG - CAT6", "Điện - đầu RJ45", 5, "W04 1, W31a 1, W31b 2, W31c 1"),
        ("coupler", "718039", "ELECTRICAL - RJ45 INLINE COUPLER - CAT6", "Điện - đầu nối RJ45", 2, "X1 and X2"),
        ("keystone", "718040", "ELECTRICAL - RJ45 KEYSTONE JACK - CAT6 - WITH DUST CAP", "Điện - nhân mạng RJ45", 3,
         "2 snapped into the front plate (jack 1 the building LAN, W04; jack 2 the tie line W31a; D-133) and 1 at the kit's "
         "data end at X7, capped")):
    part(key, pn, name, vi, "PI", "710000", qty, "", "", 0.005, "assumption", sku="maker HOLD (H-ELE-12)",
         status=HOLD_BUY, source="", note=note)

part("term_f16", "718056", "ELECTRICAL - TERMINAL - MINI-FIT JR FEMALE 16 AWG TIN", "Điện - chân giắc cái 16 AWG", "PI",
     "710000", 12, "tin-plated brass", "", 0.0003, "assumption", maker="Molex", sku="39-00-0078 (16 AWG, bag; 39-00-0077 on reel)",
     status=HOLD_BUY, source=MOLEX + "; RS listing of 39-00-0078 (16 AWG min and max), read 2026-11-01",
     note="3 x 4: the voice kit feeds' receptacles at X1, X2 and the kit outlet X7 (4 x 16 AWG, 718055)")
part("term_m16", "718057", "ELECTRICAL - TERMINAL - MINI-FIT JR MALE 16 AWG TIN", "Điện - chân giắc đực 16 AWG", "PI",
     "710000", 8, "tin-plated brass", "", 0.0003, "assumption", maker="Molex", sku="5558 series, 16 AWG: part number to confirm",
     status=HOLD_BUY, source=MOLEX, note="2 x 4: the voice kit feeds' plugs at X1 and X2 (the cap housing has none)")
part("term_f24", "718077", "ELECTRICAL - TERMINAL - MINI-FIT JR FEMALE 22-28 AWG TIN", "Điện - chân giắc cái 22-28 AWG", "PI",
     "710000", 18, "tin-plated brass", "", 0.0003, "assumption", status=HOLD_BUY,
     note="3 x 6: the hub link's 24 AWG cores in the 10-way receptacles at X1, X2, X3 (their 1.1 mm insulation is under "
          "718036's 1.30 mm grip)")
part("term_m24", "718078", "ELECTRICAL - TERMINAL - MINI-FIT JR MALE 22-28 AWG TIN", "Điện - chân giắc đực 22-28 AWG", "PI",
     "710000", 18, "tin-plated brass", "", 0.0003, "assumption", status=HOLD_BUY,
     note="3 x 6: the hub link's 24 AWG cores in the 10-way plugs at X1, X2, X3")

# ---- protection where cables pass steel, clips, draw cord
part("bushing", "718041", "ELECTRICAL - BUSHING - SHORTY 19.1 HOLE - NYLON", "Điện - vòng đệm luồn dây", "PI", "710000", 9,
     "nylon 6/6 UL94 V-2", "black, as supplied", 0.001, "assumption", maker="Heyco", sku="2836 (SB 750-625, black)",
     status=HOLD_BUY, source=HEYCO,
     note="the panel hole is Ø19.1 (WALL and CEILING cut 19.1 for it; PM 2026-10-31). Every hole through a sheet: the power unit "
          "body's H01-H03 (two lead exits, the light feed exit; 1.0 mm aluminium), G-B2-B4 x 2, G-CEIL-B, G-CEIL-F "
          "(0.5 mm steel), G-DR (DR's back plate, 1.0-2.7 mm, FRONT HOLD-10), G-SOFFIT (the soffit's casing): 9 (B2-CASS's cut-out "
          "is plain, WALL, so its top return and its bushing are gone). Panels to 1.6 mm, "
          "passes 15.9: the 0.5 mm fit and "
          "a thicker-panel bushing for G-DR or G-SOFFIT if over 1.6 mm are HOLD H-ELE-01. Felt-only holes take none: no steel edge")
part("edge", "718042", "ELECTRICAL - EDGE PROTECTION STRIP - 0.5 MM SHEET", "Điện - nẹp bảo vệ mép tôn", "PI", "710000", 0.2,
     "PVC or nylon", "", 0.02, "assumption (kg per m)", sku="maker HOLD (H-ELE-01)", status=HOLD_BUY, source="",
     note="the slot S-CNR (182 mm edge); qty in m (B2-CASS's cut-out is plain, WALL, so its slot is gone)")
part("clip", "718043", "ELECTRICAL - CABLE CLIP - FOR 0.5 MM STEEL TRAY", "Điện - kẹp giữ cáp", "PI", "710000", 24,
     "", "", 0.002, "assumption", sku="maker HOLD (H-ELE-10)", status=HOLD_BUY, source="",
     note="one per 300 mm of route and two per pocket (calculation from the route model); clips to the tray only (D-26)")
part("drawcord", "718044", "ELECTRICAL - DRAW CORD - NYLON 3 MM", "Điện - dây mồi", "PI", "710031",
     round(_m(["W32", "W33"]), 2), "nylon", "", 0.006, "assumption (kg per m)", sku="maker HOLD", status=HOLD_BUY,
     source="", note="W32 and W33; qty in m")

# ---- lights
part("strip_shelf", "718050", "ELECTRICAL - LED STRIP - LOOX5 2168 - 12 V 6.0 W/M - 3000 K", "Điện - LED dây kệ đèn",
     "PI", "710000", 6.384, "", "", 0.02, "assumption (kg per m)", maker="Häfele", sku="833.74.176 (3000 K: confirm the article order 175-178)",
     size="8 mm wide", status=HOLD_BUY, source=HAFELE,
     note="uplight 4.434 m and down-light 2 x 0.975 m (it cuts every 25 mm: section length 25 mm, maker page); 970 lm/m, Ra > 90, R9 > 50; max 3.5 m per feed (every run here is 1.5 m or less); qty in m")
# ---- D-126: the light shelf's down-light profile, under INTERIOR's light shelf 810201 (CEILING places it; ELECTRICAL lists it)
TECHLIGHT = "Tech-Light P13-2 profile and C15 cover: public retailer listings (BLT Direct, P13-2 1 m x 23 x 12.5; C15 fits P13-2, 19 inside) and the maker's catalogue (P13-2 for strips up to 2 x 8 mm; opal covers 70 %), read 2026-11-01"
part("led_prof", "718101", "ELECTRICAL - LED PROFILE - LIGHT SHELF - SURFACE 23 X 12.5", "Điện - thanh nhôm LED nổi 23 x 12.5 - kệ đèn",
     "PI", "810201", 1, "aluminium", "anodised as supplied; colour to match the shelf (HOLD)", 0.16,
     "assumption (about 0.16 kg/m for a 23 x 12.5 surface profile; maker figure HOLD)", maker="Tech-Light (type)",
     sku="P13-2 type, cut to 991 mm", size="23 x 12.5 outside, 20 inside at the strip base, 991 long", status=HOLD_BUY, source=TECHLIGHT,
     note="takes the down-light's two 8 mm strips side by side (2 x 0.975 m) with 4 mm to spare; heat 12 W/m at full: about 20 K above the room (calculation, 9 W/m2K on about 66 mm of outer surface), maker's rating HOLD; replaces CEILING's channel 811204 (D-126)")
part("led_cover", "718102", "ELECTRICAL - LED PROFILE COVER - SATIN - CLIP-IN", "Điện - nắp mờ nhẹ (satin) gài cho thanh LED",
     "PI", "810201", 1, "polycarbonate, satin (grade HOLD)", "satin, as supplied: at least 86 % light transmission (ASTM D1003)", 0.04,
     "assumption (about 0.04 kg/m)", maker="HOLD (no supplier contact)",
     sku="satin clip-in cover for the P13-2 type profile, cut to 991 mm; no public product verified yet (HOLD)", size="20 wide, 991 long",
     status=HOLD_BUY, source=TECHLIGHT + "; D-127: a satin cover passing at least 86 %, no clear cover",
     note="D-127 (PM, 2026-11-01): satin, at least 86 % light transmission, so the ledge gets 350 to 364 lx when new at the "
          "same 22 W (calculation); no clear cover, because the shelves are open underneath and the LED dots would show from "
          "the seat. Tech-Light lists only 98 / 70 / 63 % covers for the P13-2; satin or frosted polycarbonate covers of "
          "85 to 90 % are offered by diffuser makers, but none is verified for this profile yet (HOLD). Clip-in, held along its "
          "whole length, unclipped to change a strip; replaces the cut diffuser 811205 (D-126).")
part("led_cap", "718103", "ELECTRICAL - LED PROFILE END CAP", "Điện - nắp bịt đầu thanh LED", "PI", "810201", 2,
     "plastic, as supplied", "as supplied", 0.002, "assumption", maker="Tech-Light (type)", sku="P13-2 end cap type, one with a cable hole",
     size="for 23 x 12.5", status=HOLD_BUY, source=TECHLIGHT, note="one at each end; the feed lead enters through one (HOLD with the profile)")
part("led_clip", "718104", "ELECTRICAL - LED PROFILE MOUNTING CLIP", "Điện - kẹp gắn thanh LED", "PI", "810201", 3,
     "steel, as supplied", "as supplied", 0.002, "assumption", maker="Tech-Light (type)", sku="P13-2 mounting clip type",
     size="for 23 x 12.5", status=HOLD_BUY, source=TECHLIGHT,
     note="3 on the 991 mm profile, about every 400 mm (assumption); the count follows the product's clip spacing (HOLD with the profile)")
part("strip_call", "718051", "ELECTRICAL - LED STRIP - LOOX5 2165 - 12 V 3.0 W/M - 3000 K", "Điện - LED dây đèn gọi video",
     "PI", "710024", 0.9, "", "", 0.02, "assumption (kg per m)", maker="Häfele", sku="833.74.156 (3000 K: confirm)",
     size="8 mm wide", status=HOLD_BUY, source=HAFELE, note="about 420 lm for the 0.9 m bar (465 lm/m at 3000 K); qty in m")
part("call_profile", "718052", "ELECTRICAL - CALL LIGHT PROFILE AND DIFFUSER - 0.9 M", "Điện - thanh nhôm tán quang đèn gọi",
     "PI", "710024", 1, "aluminium + opal PMMA", "anodised, maker's standard (colour with INTERIOR)", 0.15, "assumption", maker="Häfele", sku="Loox5 profile, article HOLD (H-ELE-09)",
     status=HOLD_BUY, source=HAFELE, note="the maker recommends a diffuser profile for even light")

part("strip_lead", "718053", "ELECTRICAL - LED STRIP FEED LEAD - LOOX5 8 MM", "Điện - dây nối nguồn LED dây Loox5 8 mm",
     "PI", "710000", sum(STRIP_FEEDS.values()), "", "", 0.01, "assumption", maker="Häfele",
     sku="Loox5 lead for 8 mm monochrome 12 V strip, article HOLD (H-ELE-09)", status=HOLD_BUY, source=HAFELE,
     note="clip-on feed leads at the strip ends: " + ", ".join("%s %d" % kv for kv in STRIP_FEEDS.items()) +
          " (the back uplight both ways; the left jumper's ends; the right jumper's back end, right uplight and down-light rows 1 "
          "and 2; the call bar)")

# ---- hub and controls zone 710041
part("m4hub", "718048", "ELECTRICAL - SCREW - M4 X 12 - ISO 7045 A2 PAN HEAD, BLACK", "Điện - vít M4 x 12 đen", "PI", "710041", 4,
     "stainless steel", "black oxide (visible)", 0.0018, "assumption", maker="HOLD: standard part",
     sku="ISO 7045 M4 x 12 H, A2-70, black", size="M4", status=HOLD_BUY, source="this design (README section 7)",
     note="the hub zone plate into the column; what it screws into is CEILING's (HOLD)")
P["m4hub"].update(length_mm="12", grade="A2-70", torque_nm="HOLD (with CEILING's column fixing)")
part("hub", "718060", "ELECTRICAL - SENSOR HUB - DESK PRO AI (IN-HOUSE)", "Điện - bộ cảm biến Desk Pro AI", "PI", "710041", 1,
     "", "", 0.15, "assumption", maker="Autonomous (in-house)", sku="Desk Pro AI sensor hub",
     status="HOLD (in-house module: interface data ISS-060)", source="REQ-ELE-02, D-09; cited by name only")
part("hub_plate", "711005", "ELECTRICAL - HUB ZONE COVER PLATE", "Điện - mặt che vùng cảm biến", "MP", "710041", 1,
     AL + " 1.5 mm", "black anodised AA20 (D-67)", 0.094, "CAD (Fusion volume 34,911 mm3 x 2.68 g/cm3, 711005 P01 design)",
     size="180 x 180", process="laser cut from 1.5 mm sheet as a flat plate; anodised",
     status="DRAFT; HOLD features: the hub window, button and knob holes (ISS-060) and the fixing holes (CEILING's column)",
     source="711005_P01_ELECTRICAL-HUB-ZONE-COVER-PLATE_CAD; DXF 711005_P01_ELECTRICAL-HUB-ZONE-COVER-PLATE_DXF.dxf (no drawing, D-89 part 4)",
     note="flat plate, its DXF gives the full outline and every hole (D-89 part 4); thickness 1.5 mm; general tolerance "
          "ISO 2768-m; HOLD: the hub window, the 3 button holes, the knob hole (ISS-060) and the 4 fixing holes (CEILING's column)")
for key, pn, name, vi, qty, note in (
        ("btn_boost", "718061", "ELECTRICAL - PUSH BUTTON - MOMENTARY - BOOST", "Điện - nút nhấn tăng gió", 1, "hub input (D-33)"),
        ("btn_call", "718062", "ELECTRICAL - PUSH BUTTON - MOMENTARY - CALL", "Điện - nút nhấn đèn gọi", 1,
         "hub input; the hub switches the call light (D-87 self-test can run it)"),
        ("pot", "718063", "ELECTRICAL - LIGHT KNOB - POTENTIOMETER WITH KNOB", "Điện - núm chỉnh sáng", 1,
         "hub analog input; the hub sets PS2's 0-10 V dimming (value set by the hub's input, H-ELE-05)"),
        ("btn_test", "718069", "ELECTRICAL - PUSH BUTTON - MOMENTARY - SELF-TEST", "Điện - nút tự kiểm tra", 1,
         "hub input: runs the fans, lights and sensors and shows pass or fail (D-87)"),
        ("fh_col", "718064", "ELECTRICAL - FUSE HOLDER - ATO BLADE - INLINE - COLUMN", "Điện - đế cầu chì cột gió", 3,
         "F3a to F3c behind the cover"),
        ("sensor", "718065", "ELECTRICAL - INLET TEMPERATURE SENSOR", "Điện - cảm biến nhiệt cửa gió vào", 1,
         "type set by the hub's sensor port (H-ELE-06, D-50)")):
    part(key, pn, name, vi, "PI", "710041", qty, "", "", 0.01, "assumption", sku="maker HOLD", status=HOLD_BUY, source="",
         note=note)
part("fuse2", "718066", "ELECTRICAL - FUSE - ATO 2 A 32 V", "Điện - cầu chì 2 A", "PI", "710041", 2, "", "", 0.002,
     "assumption", maker="Littelfuse", sku="0287002 (unverified)", status=HOLD_BUY, source="ISO 8820-3", note="F3a, F3b fans")
part("fuse1", "718067", "ELECTRICAL - FUSE - ATO 1 A 32 V", "Điện - cầu chì 1 A", "PI", "710041", 1, "", "", 0.002,
     "assumption", maker="Littelfuse", sku="0287001 (unverified)", status=HOLD_BUY, source="ISO 8820-3", note="F3c hub")
part("isense", "718073", "ELECTRICAL - CURRENT SENSE MODULE - 12 V 0-5 A", "Điện - mô-đun đo dòng", "PI", "710001", 1,
     "", "", 0.01, "assumption", sku="maker HOLD (H-ELE-13)", status=HOLD_BUY, source="",
     note="on PS2's output in the power unit: the self-test steps each light channel and reads the current change (D-87)")
part("ycable", "718068", "ELECTRICAL - FAN Y-CABLE - 4-PIN PWM", "Điện - cáp chia quạt", "PI", "710041", 2, "", "", 0.01,
     "assumption", maker="Noctua", sku="NA-SYC1 (unverified; harness end housing H-ELE-07)", status=HOLD_BUY,
     source="", note="one per fan pair, at the fan box")

# ---- cord set kit 719001 (ships loose; the US version changes only this, the inlet side and the socket)
part("cord_conn", "718070", "ELECTRICAL - CORD CONNECTOR - POWERCON TRUE1 TOP", "Điện - giắc dây nguồn", "PI", "719001", 1,
     "", "", 0.08, "assumption", maker="Neutrik", sku="mate of NAC3MPX-TOP, as selection E (NAC3F-TRUE1-S / NAC3FX-W-TOP): confirm",
     status=HOLD_BUY, source=SEL, note="locking; UL 498 (as the inlet), for SJOOW 14/3 (cable OD 6-12 mm)")
part("cord_wire", "718071", "ELECTRICAL - CORD - SJOOW 14/3", "Điện - dây nguồn SJOOW 14/3", "PI", "719001", 3.0,
     "Carolprene (CPE) jacket, EPDM insulation, UL 62 type SJOOW, 300 V, 3 x 14 AWG", "black", 0.149,
     "calculation (kg per m: 100 lb per 1000 ft, maker sheet)", sku="maker HOLD", status=HOLD_BUY,
     source="", note="3 m, 15 A (D-133); qty in m")
part("plug_us", "718072", "ELECTRICAL - MAINS PLUG - NEMA 5-15P", "Điện - phích cắm NEMA 5-15P", "PI", "719001", 1, "", "", 0.06,
     "assumption", sku="15 A 125 V straight blade, industrial grade, UL 498; maker HOLD", status=HOLD_BUY, source="",
     note="D-133: US 120 V. The prototype is tested in Vietnam through a 220-to-110 V step-down transformer (the test set's, "
          "not a pod part)")

# ---- lines the named products added (2026-11-01): the inlet's tab terminals, the conduit's connector, the call
# light profile's end caps
part("qd", "718074", "ELECTRICAL - FEMALE DISCONNECT - 0.250 IN - 16-14 AWG - INSULATED", "Điện - đầu cos cái 6,3 mm",
     "PI", "710001", 3, "tin-plated brass, nylon insulation", "", 0.001, "assumption", status=HOLD_BUY,
     note="the inlet NAC3MPX-TOP's three 1/4 in tabs (L, N, PE), on W01's 14 AWG")
part("sleeve_fit", "718075", "ELECTRICAL - CONDUIT CONNECTOR - LFNC 1/2 IN - STRAIGHT", "Điện - đầu nối ống luồn dây 1/2 in",
     "PI", "710001", 1, "nylon 6, as supplied", "as supplied", 0.01, "assumption", maker="Electri-Flex",
     sku="NMLT-11 (UL and cUL E197675; 1/2 in trade-size knockout)", status=HOLD_BUY,
     source="https://www.electriflex.com/wp-content/uploads/2016/07/Type-NMLT-NMSC-Nonmetallic-Type-B-Connectors-_-Electri-Flex-2.pdf",
     note="the conduit 718017 into the unit's H04")
part("call_caps", "718076", "ELECTRICAL - CALL LIGHT PROFILE END CAP (PAIR)", "Điện - nắp bịt thanh nhôm đèn gọi (cặp)",
     "PI", "710024", 1, "plastic, silver", "as supplied", 0.004, "assumption", status=HOLD_BUY,
     note="the 0.9 m call light bar's two ends")


# D-89 part 4: flat sheet parts carry thickness and the general tolerance in their row
P["pu_front"].update(thickness_mm="1.5", tolerance="ISO 2768-m; M4 holes true position Ø0.3; breaker window +0.5/0")
P["hub_plate"].update(thickness_mm="1.5", tolerance="ISO 2768-m")
P["pu_body"].update(thickness_mm="1.0", tolerance="ISO 2768-m (drawing 711001)")


# ------------------------------------------------------------------ the bought products (named 2026-11-01)
# Each bought line's product, named from its own datasheet or the maker's own page (the Lead's task of 2026-11-01:
# US 120 V and UL listed on the mains side, D-133; Class 2 on the 12 V side, D-136; the light shelf plugs in, D-148).
# The table sets the line's maker, part number (with the ratings and listing that matter), status and source, and adds
# the maker and number to its name; a line that truly waits on a supplier's answer or another team's data stays HOLD
# with its reason. Nothing is ordered and no supplier is contacted (guideline 4.3).
NAMED_BUY = "source (datasheet); not ordered (guideline 4.3)"


def held(reason):
    return "HOLD (%s; no order, no supplier contact)" % reason


PRODUCTS = {'718077': ('MOLEX 39-00-0047',
            'Molex',
            '39-00-0047: Mini-Fit female crimp terminal, 22-28 AWG, insulation 0.90-1.80 mm, tin-plated brass, bag',
            'https://www.molex.com/en-us/products/part-detail/39000047 ; https://tools.molex.com/pdm_docs/ps/PS-5556-001.pdf',
            '3 A per circuit at 24 AWG in a 7-10 way housing (PS-5556-001)'),
 '718078': ('MOLEX 39-00-0049',
            'Molex',
            '39-00-0049: Mini-Fit male crimp terminal, 22-28 AWG, tin-plated brass, bag',
            'https://www.molex.com/en-us/products/part-detail/39000049 ; https://tools.molex.com/pdm_docs/ps/PS-5556-001.pdf',
            ''),
 '718001': ('MEAN WELL LPV-60-12',
            'Mean Well',
            "LPV-60-12: 12 V 0-5 A, 60 W, 90-264 VAC; 'Class 2 power unit', UL1310, Class II",
            'https://www.meanwellusa.com/upload/pdf/LPV-60/LPV-60-spec.pdf (rev 2026-09-07)',
            'leads 600 mm: AC UL1015 18 AWG, DC UL1007 16 AWG (sheet)'),
 '718002': ('ENTTEC CVC4 73926',
            'ENTTEC',
            '73926 (CVC4): 4-channel constant-voltage PWM LED dimmer, 12-24 V DC, 5 A per channel, common VCC, '
            'DMX512 (RS-485) and RDM; 88 x 117.5 x 31.5 mm',
            'https://cdn.enttec.com/pdf/assets/73926/73926_CVC4_DATASHEET.pdf',
            "holds the last DMX frame when the data stops; channel 4 spare; its fit in the unit's controller space "
            'to check in the layout'),
 '718004': ('NEUTRIK NAC3MPX-TOP',
            'Neutrik',
            'NAC3MPX-TOP: UL 498 20 A 250 V AC (Recognized, file E343813); 1/4 in flat tabs',
            'https://www.neutrik.com/en/product/nac3mpx-top',
            'its 1/4 in tabs take the three disconnects 718074'),
 '718005': ('NEUTRIK SCNAC-01',
            'Neutrik',
            'SCNAC-01: D-size sealing cover for NAC3MPX*, IP 65 closed',
            'https://www.neutrik.com/en/product/scnac-01',
            ''),
 '718006': ('NEUTRIK NE8FDP',
            'Neutrik',
            'NE8FDP: etherCON CAT5e RJ45 feedthrough, D-size metal flange, panel up to 4 mm',
            'https://www.neutrik.com/en/product/ne8fdp',
            ''),
 '718007': ('P&S 1597TRW',
            'Pass & Seymour (Legrand)',
            '1597TRW: radiant tamper-resistant 15 A 125 V self-test duplex GFCI, white; cULus listed E42190; 1.73 x '
            '4.2 x 1.13 in',
            'https://www.legrand.us/p/print/1597TRW.pdf (read 2026-11-01)',
            "1595TRW is no longer listed (Legrand's search sends it to 1597TRW); the same 1.73 x 4.2 x 1.13 in body "
            "and decorator face, so the front plate's opening stays"),
 '718010': ('PHOENIX CONTACT NS 35/7,5 PERF 2000MM',
            'Phoenix Contact',
            '0843103: NS 35/7,5 PERF 2000MM, pack of 10, EN 60715 steel; one rail cut to 100 mm',
            'https://www.phoenixcontact.com/pc/products/0843103 (sheet copy '
            'https://docs.rs-online.com/6e9f/A700000016059116.pdf)',
            ''),
 '718011': ('LITTELFUSE FHAC0001ZXJ',
            'Littelfuse',
            'FHAC0001ZXJ: inline ATO fuse holder with cover, 16 AWG leads, 20 A at 32 V DC',
            'Littelfuse catalog p.132 (copy https://static.chipdip.ru/lib/468/DOC012468626.pdf)',
            ''),
 '718012': ('LITTELFUSE 0287005.PXCN',
            'Littelfuse',
            '0287005.PXCN: ATOF 5 A 32 V DC, 1000 A interrupting; UL listed AU1410',
            'Littelfuse ATOF 287 sheet (copy '
            'https://datasheet.lcsc.com/datasheet/pdf/67d4e77c30c689b2c6a06a59b85b9e09.pdf)',
            'the .PXCN pack is 2000; .L is 50'),
 '718013': ('LITTELFUSE 0287005.PXCN',
            'Littelfuse',
            '0287005.PXCN: ATOF 5 A 32 V DC, 1000 A interrupting; UL listed AU1410',
            'Littelfuse ATOF 287 sheet (copy '
            'https://datasheet.lcsc.com/datasheet/pdf/67d4e77c30c689b2c6a06a59b85b9e09.pdf)',
            ''),
 '718014': ('PEM FHA-M5-12',
            'PennEngineering (PEM)',
            'FHA-M5-12: aluminium self-clinching flush-head stud M5 x 12, sheet 1.0 mm min., hole 5.0 +0.08',
            'https://www.pemnet.com/products/product-finder/fha-m5-12/',
            'nut torque 1.5 N m in aluminium (sheet)'),
 '718015': ('FABORY 51460.060.001 DIN 6798 A',
            'Fabory',
            '51460.060.001: serrated lock washer, external teeth, DIN 6798 A, M6 (6.4), stainless A2',
            'https://www.fabory.com/en/p/51460060001/generatePdf',
            ''),
 '718016': ('PANDUIT PV14-10R-C/PV14-14R-C',
            'Panduit',
            'PV14-10R-C (#10 stud, 4) and PV14-14R-C (1/4 in, 1): vinyl-insulated rings, 16-14 AWG; cULus 587H '
            'E52164',
            'https://www.panduit.com/en/products/wire-termination/electrical-terminals/ring-terminals/p204344.html#pn=PV14-10R-C',
            ''),
 '718017': ('ELECTRI-FLEX LIQUATITE NM-11',
            'Electri-Flex',
            'Liquatite Type NM 1/2 in (catalog 81011, 100 ft): LFNC-B, UL 1660 Type B, file E79308',
            'https://www.electriflex.com/products/type-nm/',
            ''),
 '718019': ('FABORY 51340.040.008 DIN 7985-H',
            'Fabory',
            '51340.040.008: M4 x 8 Phillips raised cheese head, DIN 7985-H (ISO 7045 head 8 x 3.1), A2-70',
            'https://www.fabory.com/en/p/51340040008/generatePdf',
            ''),
 '718020': ('ALPHA WIRE 461419 BK005/WH005/GR005',
            'Alpha Wire',
            '461419 BK005, WH005, GR005: UL 1015 AWM 105 C 600 V, 14 AWG 19/.0147 copper, 100 ft spools',
            'https://www.alphawire.com/disteAPI/SpecPDF/DownloadProductSpecPdf?productPartNumber=461419',
            ''),
 '718021': ('ALPHA WIRE 461419 BK005/WH005',
            'Alpha Wire',
            '461419 BK005, WH005: UL 1015 AWM 105 C 600 V, 14 AWG, 100 ft spools',
            'https://www.alphawire.com/disteAPI/SpecPDF/DownloadProductSpecPdf?productPartNumber=461419',
            ''),
 '718022': ('ALPHA WIRE 461419 GR005',
            'Alpha Wire',
            '461419 GR005: UL 1015 AWM 105 C 600 V, 14 AWG, green, 100 ft spool',
            'https://www.alphawire.com/disteAPI/SpecPDF/DownloadProductSpecPdf?productPartNumber=461419',
            ''),
 '718023': ('SOUTHWIRE R40018-1',
            'Southwire',
            'R40018-1 (spec 13060): 2 x 18 AWG stranded, PVC, CL3R (also CMR, FPLR, CMG), 300 V, 60 C, OD 3.66 mm',
            'https://cabletechsupport.southwire.com/en/tile/39/spec/13060/?country=US',
            "cores about 1.3-1.45 mm (calculation), low in the terminal's 1.30-3.10 grip: prove a crimp sample"),
 '718024': ('SOUTHWIRE R40049-1',
            'Southwire',
            'R40049-1 (spec 13060): 4 x 18 AWG stranded, PVC, CL3R, 300 V, 60 C, OD 4.22 mm',
            'https://cabletechsupport.southwire.com/en/tile/39/spec/13060/?country=US',
            'prove a crimp sample (as 718023)'),
 '718025': ('BELDEN 9536',
            'Belden',
            '9536 060100: 6 x 24 AWG stranded, overall foil and drain, PVC, CMG, 300 V (UL AWM 2464)',
            'https://catalog.belden.com/techdata/EN/9536_techdata.pdf',
            "CMG stands in for CL2/CL3 by the NEC's cable substitution table (to confirm in the US rules phase, "
            'ISS-083)'),
 '718026': ('SOUTHWIRE R30042-1',
            'Southwire',
            'R30042-1 (spec 13066): 4 x 20 AWG stranded, foil shield and drain, PVC, CL3R, 300 V, OD 4.04 mm',
            'https://cabletechsupport.southwire.com/en/tile/39/spec/13066/?country=US',
            'no unshielded 20/4 in the CL3R range; the foil does no harm on PWM and tach'),
 '718027': ('BELDEN 9534',
            'Belden',
            '9534 060100: 4 x 24 AWG stranded, overall foil and drain, PVC, CMG, 300 V (UL AWM 2464)',
            'https://catalog.belden.com/techdata/EN/9534_techdata.pdf',
            'CMG stands in for CL2/CL3 (as 718025)'),
 '718028': ('BELDEN 3612',
            'Belden',
            '3612 0081000: Cat 6 U/UTP, 4 pair, 23 AWG solid, CMR (UL 1666), OD 5.87 mm',
            'https://catalog.belden.com/techdata/EN/3612_techdata.pdf',
            ''),
 '718029': ('SOUTHWIRE R40015-1',
            'Southwire',
            'R40015-1 (spec 13060): 6 x 18 AWG stranded, PVC, CL3R, 300 V, 60 C, OD 5.38 mm',
            'https://cabletechsupport.southwire.com/en/tile/39/spec/13060/?country=US',
            ''),
 '718030': ('MOLEX 39-01-2025 (5557-02R)',
            'Molex',
            '39-01-2025 (5557-02R-210): Mini-Fit Jr receptacle housing, dual row, 2 circuits, UL 94V-0; 9 A per '
            'circuit at 18 AWG, 600 V; UL E29179',
            'https://www.molex.com/en-us/products/part-detail/39012025 ; '
            'https://tools.molex.com/pdm_docs/ps/PS-5556-001.pdf',
            ''),
 '718031': ('MOLEX 39-01-3029 (5559-02P1)',
            'Molex',
            '39-01-3029 (5559-02P1-210): Mini-Fit Jr plug housing, dual row, 2 circuits, without panel mounting '
            'ears, UL 94V-0; UL E29179',
            'https://www.molex.com/en-us/products/part-detail/39013029 ; '
            'https://tools.molex.com/pdm_docs/ps/PS-5556-001.pdf',
            '39-01-2026 was the panel-mount plug with ears: this free-hanging twin suits a cable-to-cable joint'),
 '718032': ('MOLEX 39-01-2045 (5557-04R)',
            'Molex',
            '39-01-2045 (5557-04R-210): Mini-Fit Jr receptacle housing, 4 circuits, UL 94V-0; 8 A per circuit at '
            '16-18 AWG, 600 V; UL E29179',
            'https://www.molex.com/en-us/products/part-detail/39012045 ; '
            'https://tools.molex.com/pdm_docs/ps/PS-5556-001.pdf',
            ''),
 '718033': ('MOLEX 39-01-3049 (5559-04P1)',
            'Molex',
            '39-01-3049 (5559-04P1-210): Mini-Fit Jr plug housing, 4 circuits, without panel mounting ears, UL '
            '94V-0; UL E29179',
            'https://www.molex.com/en-us/products/part-detail/39013049 ; '
            'https://tools.molex.com/pdm_docs/ps/PS-5556-001.pdf',
            '39-01-2046 was the panel-mount plug with ears'),
 '718034': ('MOLEX 39-01-2105 (5557-10R)',
            'Molex',
            '39-01-2105 (5557-10R-210): Mini-Fit Jr receptacle housing, 10 circuits, UL 94V-0; 7 A per circuit at 18 '
            'AWG, 3 A at 24 AWG, 600 V; UL E29179',
            'https://www.molex.com/en-us/products/part-detail/39012105 ; '
            'https://tools.molex.com/pdm_docs/ps/PS-5556-001.pdf',
            ''),
 '718035': ('MOLEX 39-01-3109 (5559-10P1)',
            'Molex',
            '39-01-3109 (5559-10P1-210): Mini-Fit Jr plug housing, 10 circuits, without panel mounting ears, UL '
            '94V-0; UL E29179',
            'https://www.molex.com/en-us/products/part-detail/39013109 ; '
            'https://tools.molex.com/pdm_docs/ps/PS-5556-001.pdf',
            '39-01-2106 was the panel-mount plug with ears'),
 '718036': ('MOLEX 39-00-0039',
            'Molex',
            '39-00-0039: Mini-Fit female crimp terminal, 18-24 AWG, tin over copper on brass, insulation 1.30-3.10 '
            'mm, bag',
            'https://www.molex.com/en-us/products/part-detail/39000039 ; '
            'https://tools.molex.com/pdm_docs/ps/PS-5556-001.pdf',
            "for the 18 AWG cores; the hub link's 24 AWG cores (1.1 mm) take the 22-28 AWG terminal"),
 '718037': ('MOLEX 39-00-0041',
            'Molex',
            '39-00-0041: Mini-Fit male crimp terminal, 24-18 AWG, matte tin on brass, bag',
            'https://www.molex.com/en-us/products/part-detail/39000041 ; '
            'https://tools.molex.com/pdm_docs/ps/PS-5556-001.pdf',
            "for the 18 AWG cores; the hub link's 24 AWG cores take the 22-28 AWG terminal"),
 '718038': ('PANDUIT SP688E-C',
            'Panduit',
            'SP688E-C: Cat 6 UTP RJ45 modular plug, 23-24 AWG, pack of 100; cULus, UL 1863 (E129886)',
            'https://www.panduit.com/en/products/copper-systems/copper-connectors/copper-modular-plugs/p202336.html#pn=SP688E-C',
            'suits the Belden 3612 cable (23 AWG solid, 5.87 mm)'),
 '718039': ('PANDUIT CC688IW',
            'Panduit',
            'CC688IW: Mini-Com Cat 6 UTP RJ45 coupler module; UL 1863, UL 2043',
            'https://www.panduit.com/en/products/copper-systems/connectors/jack-modules/cc688iw.html',
            'Panduit allows up to two couplers per channel: X1 and X2 use both'),
 '718040': ('PANDUIT NK688MWH',
            'Panduit',
            'NK688MWH: NetKey Cat 6 UTP RJ45 punchdown keystone jack, 22-26 AWG; UL 1863, UL 2043; dust cap PSL-DCJB '
            'for the capped jack at X7',
            'https://www.panduit.com/en/products/copper-systems/connectors/jack-modules/nk688mwh.html',
            'the 14.9 x 19.4 cut-out in 1.5 mm plate to prove on a sample'),
 '718041': ('HEYCO 2836N',
            'Heyco',
            '2836N (B 750-625N, black): thin panel snap bushing for a 19.1 mm hole, panels 0.5 to 1.6 mm, bore 15.9 '
            'mm; UL Recognized E15331, 94V-2',
            'https://www.heyco.com/wp-content/uploads/2024/09/Thin-Panel-Snap-Bushings.pdf',
            '2836 locks only in 1.6 mm sheet; 2836N locks in the 1.0 mm body and the 0.5 mm trays'),
 '718042': ('HEYCO 12431 DS-125',
            'Heyco',
            '12431 (DS-125-48 in, 1.2 m): push-on nylon grommet channel for panels 0.5 to 3.2 mm, 94HB',
            'https://www.heyco.com/wp-content/uploads/2024/09/Grommet-Channels.pdf',
            '0.5 mm is the bottom of its range: prove the grip on a sample'),
 '718043': ('HEYCO 3904 PMT 150',
            'Heyco',
            '3904 (PMT 150): push-mount cable tie with wings, nylon 6/6, bundle to 44.5 mm, panels 0 to 3.2 mm, Ø6.4 '
            'mm hole',
            'https://www.heyco.com/wp-content/uploads/2024/09/Nytye-Push-Mount-Cable-Ties.pdf',
            'needs a Ø6.4 mm hole at each clip point in the cassette trays (an interface with WALL and CEILING)'),
 '718044': ('ERIN ROPE SBN041000',
            'Erin Rope',
            'SBN041000: #4 (1/8 in, 3.2 mm) solid braid nylon cord, 575 lb break, 1000 ft',
            'https://erinrope.com/solid-braid-nylon/',
            ''),
 '718045': ('MOLEX 39-01-2065 (5557-06R)',
            'Molex',
            '39-01-2065 (5557-06R-210): Mini-Fit Jr receptacle housing, 6 circuits, UL 94V-0; 8 A per circuit at 18 '
            'AWG, 600 V; UL E29179',
            'https://www.molex.com/en-us/products/part-detail/39012065 ; '
            'https://tools.molex.com/pdm_docs/ps/PS-5556-001.pdf',
            "X5 is the light shelf's plug-in joint on site (D-148)"),
 '718046': ('MOLEX 39-01-3069 (5559-06P1)',
            'Molex',
            '39-01-3069 (5559-06P1-210): Mini-Fit Jr plug housing, 6 circuits, without panel mounting ears, UL '
            '94V-0; UL E29179',
            'https://www.molex.com/en-us/products/part-detail/39013069 ; '
            'https://tools.molex.com/pdm_docs/ps/PS-5556-001.pdf',
            "39-01-2066 was the panel-mount plug with ears; X5 is the light shelf's plug-in joint on site (D-148)"),
 '718047': ('PEM CLA-M4-1',
            'PennEngineering (PEM)',
            'CLA-M4-1: aluminium self-clinching nut M4, shank code 1 (sheet 1.0 mm min.), hole 5.94 +0.08',
            'https://www.pemnet.com/products/product-finder/cla-m4-1/',
            "the body's H05-H08 are Ø5.4 today: the clinch hole is 5.94 +0.08 (follow-up with the body's next "
            'rebuild)'),
 '718050': ('HÄFELE 833.74.176',
            'Häfele',
            '833.74.176: Loox5 LED 2168, 12 V, 6.0 W/m, 3000 K, 970 lm/m, Ra 92, R9 > 50; 5 m roll; cULus mark, '
            'class III',
            'https://files.hafele.co.uk/CatalogFiles/www/25L1-18.pdf',
            '3000 K comes in 5 m rolls only: 6.384 m per pod takes 2 rolls'),
 '718051': ('HÄFELE 833.74.156',
            'Häfele',
            '833.74.156: Loox5 LED 2165, 12 V, 3.0 W/m, 3000 K, 465 lm/m, Ra 92; cULus mark, class III',
            'https://files.hafele.co.uk/CatalogFiles/www/25L1-18.pdf',
            '0.9 m gives about 420 lm at 3000 K (465 lm/m, catalogue)'),
 '718052': ('HÄFELE LOOX5 2191 833.72.982',
            'Häfele',
            '833.72.982: Loox5 profile 2191 for surface mounting, 2500 x 18 x 14 mm, silver anodised, opal white '
            'diffuser; cut to 0.9 m',
            'https://files.hafele.co.uk/CatalogFiles/www/25L1-56.pdf',
            'dots not seen with strips of 120 LEDs/m or more (the 2165 has 160); end caps 718076'),
 '718053': ('HÄFELE 833.74.695',
            'Häfele',
            '833.74.695: Loox5 5 A driver-to-light lead for 8 mm monochrome strip, 500 mm, clip-on',
            'https://files.hafele.co.uk/CatalogFiles/www/25L1-18.pdf',
            'its far end is a Loox5 12 V plug: each harness end mates or splices it'),
 '718055': ('SOUTHWIRE 94664',
            'Southwire',
            '94664 (spec 13090): 4 x 16 AWG stranded, PVC, CL3 (ETL), 300 V, 75 C, OD 5.84 mm',
            'https://cabletechsupport.southwire.com/en/tile/39/spec/13090/?country=US',
            "cores about 1.9-2.0 mm (calculation) suit the 16 AWG terminal's 1.80 mm minimum"),
 '718056': ('MOLEX 39-00-0078',
            'Molex',
            '39-00-0078: Mini-Fit female crimp terminal, 16 AWG, tin over copper on brass, bag',
            'https://www.molex.com/en-us/products/part-detail/39000078 ; '
            'https://tools.molex.com/pdm_docs/ps/PS-5556-001.pdf',
            ''),
 '718057': ('MOLEX 39-00-0082',
            'Molex',
            '39-00-0082: Mini-Fit male crimp terminal, 16 AWG, insulation 1.80-3.10 mm, matte tin on brass, bag',
            'https://www.molex.com/en-us/products/part-detail/39000082 ; '
            'https://tools.molex.com/pdm_docs/ps/PS-5556-001.pdf',
            ''),
 '718061': ('E-SWITCH PV16F2B0SS',
            'E-Switch',
            'PV16F2B0SS: 16 mm anti-vandal momentary push button, stainless, SPDT, 2 A 24 V DC, IP67',
            'https://configured-product-images.s3.amazonaws.com/2D/specs/PV16F2B0SS.pdf',
            "panel hole Ø16.0 +0.2/0, 36.6 mm deep behind: 711005's button holes follow (its HOLD features)"),
 '718062': ('E-SWITCH PV16F2B0SS',
            'E-Switch',
            'PV16F2B0SS: 16 mm anti-vandal momentary push button, stainless, SPDT, 2 A 24 V DC, IP67',
            'https://configured-product-images.s3.amazonaws.com/2D/specs/PV16F2B0SS.pdf',
            ''),
 '718064': ('LITTELFUSE FHAC0001ZXJ',
            'Littelfuse',
            'FHAC0001ZXJ: inline ATO fuse holder with cover, 16 AWG leads, 20 A at 32 V DC',
            'Littelfuse catalog p.132 (copy https://static.chipdip.ru/lib/468/DOC012468626.pdf)',
            ''),
 '718066': ('LITTELFUSE 0287002.PXCN',
            'Littelfuse',
            '0287002.PXCN: ATOF 2 A 32 V DC, 1000 A interrupting; UL listed AU1410',
            'Littelfuse ATOF 287 sheet (copy '
            'https://datasheet.lcsc.com/datasheet/pdf/67d4e77c30c689b2c6a06a59b85b9e09.pdf)',
            ''),
 '718067': ('LITTELFUSE 0287001.PXCN',
            'Littelfuse',
            '0287001.PXCN: ATOF 1 A 32 V DC, 1000 A interrupting; UL listed AU1410',
            'Littelfuse ATOF 287 sheet (copy '
            'https://datasheet.lcsc.com/datasheet/pdf/67d4e77c30c689b2c6a06a59b85b9e09.pdf)',
            ''),
 '718069': ('E-SWITCH PV16F2B0SS',
            'E-Switch',
            'PV16F2B0SS: 16 mm anti-vandal momentary push button, stainless, SPDT, 2 A 24 V DC, IP67',
            'https://configured-product-images.s3.amazonaws.com/2D/specs/PV16F2B0SS.pdf',
            ''),
 '718070': ('NEUTRIK NAC3F-TRUE1-S',
            'Neutrik',
            'NAC3F-TRUE1-S: UL 498 20 A 250 V AC; cable OD 6-12 mm; 14 AWG; certified with SJOOW 14/3',
            'https://www.neutrik.com/en/product/nac3f-true1-s',
            'the cord 718071 is SJOOW 14/3, the US cable Neutrik certifies with it (not SJT)'),
 '718071': ('CAROL 01360',
            'Prysmian (Carol)',
            '01360: type SJOOW 14/3, 300 V, 90 C, black Carolprene jacket, OD 9.27 mm; UL 62 flexible cord',
            'https://na.prysmian.com/sites/na.prysmian.com/files/media/products/Carolprene%C2%AE%20Jacketed%20Type%20SJOOW.pdf',
            '100 lb per 1000 ft: 0.149 kg/m (calculation)'),
 '718072': ('LEVITON 5266-C',
            'Leviton',
            '5266-C: NEMA 5-15P industrial grade, 15 A 125 V; cord range 0.230-0.685 in; UL 498 file E13399',
            'https://www.leviton.com/en/products/5266-c',
            ''),
 '718074': ('PANDUIT DNF14-250FIB-C',
            'Panduit',
            'DNF14-250FIB-C: fully insulated female disconnect, 0.250 x 0.032 in tab, 16-14 AWG; UL 310, CSA 22.2 '
            'No.153',
            'https://www.panduit.com/en/products/wire-termination/electrical-terminals/disconnects/p204674.html#pn=DNF14-250FIB-C',
            ''),
 '718076': ('HÄFELE 833.72.853',
            'Häfele',
            '833.72.853: end caps for Loox5 profile 2191, plastic, silver, pack of 2',
            'https://files.hafele.co.uk/CatalogFiles/www/25L1-56.pdf',
            '')}

HOLDS = {'718003': "the breaker's own sheet (Eaton FAZ-C15/1-NA-L) can't be read: eaton.com and the distributors block "
           "automated reads; Eaton's family catalog gives UL 489 at 240 Vac, C curve, 14 kA at 15-25 A",
 '718048': "its length waits on what it screws into (CEILING's column), and no maker sheet was found for a black A2 "
           'M4 pan head (plain A2: Fabory 51340.040.012)',
 '718049': 'no maker sheet found for a black nylon 6/6 spacer 4.3 x 8 x 2 mm (the closest, RAF M0591-4-N, states no '
           'colour or grade)',
 '718054': 'no maker sheet found for a black 6-32 x 1/2 in oval head wallplate screw (packs are stainless or brown); '
           'black matters on the black front plate',
 '718063': "the pot's value, taper and supply are set by the hub's analog input (H-ELE-05, ISS-060)",
 '718065': "the sensor type is set by the hub's sensor port (H-ELE-06, ISS-060): NTC, 1-Wire or I2C",
 '718068': "Noctua's NA-SYC1 page can't be read automatically, so it isn't quoted from the maker; the harness end "
           'waits on H-ELE-07',
 '718073': "its output must suit the in-house hub's input (H-ELE-13, ISS-060): analog or I2C not known yet",
 '718075': "the connector's knockout: NMLT-11 takes a 1/2 in trade-size knockout (7/8 in, 22.2 mm, by common "
           'practice; its sheet gives only the trade size) and H04 is Ø25 (assumption): the hole and the connector '
           "are settled together in the body's next rebuild",
 '718101': 'no maker sheet read gives a surface profile about 23 x 12.5 mm (20 mm base) with a satin cover of 86 % '
           "or more; the one 86 % cover found (KLUS G-22S) fits a 24.5 mm high profile, which changes the shelf's "
           'look (a PM call, D-126, D-127)',
 '718102': 'follows the shelf profile 718101 (no satin cover of 86 % or more found for it)',
 '718103': 'follows the shelf profile 718101',
 '718104': 'follows the shelf profile 718101 (the count follows its clip spacing)'}


def _name_products():
    for p in P.values():
        pn = p["part_number"]
        if pn.startswith("83") and p["status"] == HOLD_BUY:     # the joints register names its hardware (D-63)
            p["status"] = "source (joints register, D-63); not ordered (guideline 4.3)"
            continue
        if pn in PRODUCTS:
            tag, maker, sku, src, add = PRODUCTS[pn]
            p.update(maker=maker, sku=sku, status=NAMED_BUY, source=src)
            p["name"] = "%s - %s" % (p["name"], tag)
            if add:
                p["note"] = "%s; %s" % (p["note"], add) if p["note"] else add
        elif pn in HOLDS:
            p["status"] = held(HOLDS[pn])


_name_products()


def _fill_sources():
    """Every row names where its numbers come from (C06)."""
    for k, p in P.items():
        if p["source"]:
            continue
        if p["kind"] == "HS":
            p["source"] = "this design: README (sections 3 to 8) and the harness list"
        elif "qty in m" in p["note"]:
            p["source"] = "harness list lengths (route model); mass: typical catalogue value (assumption)"
        else:
            p["source"] = "function and HOLD per README section 10; mass: assumption"


_fill_sources()


def unit_of(key):
    """'m' for parts bought by length, else 'pc'."""
    return "m" if "qty in m" in P[key]["note"] else "pc"


# ------------------------------------------------------------------ voltage-drop paths (supply to the farthest load)
CIRCUIT_PATHS = [
    ("PS1 (and PS4) to the voice kit outlet, one feed", ["W30a", "W30b", "W30c"]),
    ("PS2 to the left wall uplight", ["W10a", "W10b", "W10c", "W11a", "W11b"]),
    ("PS2 to the call light", ["W10a", "W10b", "W10c", "W11a", "W11c", "W12"]),
    ("PS3 to the supply fans", ["W20a", "W20b", "W20c", "W20d", "W40"]),
    ("PS3 to the exhaust fans", ["W20a", "W20b", "W20c", "W20d", "W41"]),
    ("PS3 to the sensor hub", ["W20a", "W20b", "W20c", "W20d", "W43"]),
]
