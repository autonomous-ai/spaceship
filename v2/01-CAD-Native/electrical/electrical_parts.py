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
    ("PS1", "ps_cv", "12 V DC", 60.0, 5.0, "voice cockpit hook, fused 5 A (REQ-VCK-04)",
     "the kit's 12 V 5 A is exactly one Class 2 source at 12 V (NEC Chapter 9 Table 11(B): 5.0 x Vmax VA, 5.0 A)"),
    ("PS2", "ps_cv", "12 V DC", 60.0, 5.0, "all lights: uplight, down-light and call light, through the 3-channel light controller",
     "lights on their own source, so a light fault can't stall the fresh air; the hub holds the lights at about 22 W"),
    ("PS3", "ps_cv", "12 V DC", 60.0, 5.0, "four fans and the sensor hub (column fuse block)",
     "air and hub on their own source, so a lighting or kit fault can't stop the fresh air"),
]

# ------------------------------------------------------------------ loads (the load table)
# id, load, supply, branch fuse, qty, W each max, W each typical, status of W, source, note
FAN_W_MAX = 6.6        # Noctua's maximum input power, 0.55 A at 12 V (maker page via retailer copies, 2026-10-31: unverified)
LIGHT_BUDGET_W = 22.0  # DECIDED (PM 2026-11-01): uplight, down-light and call light together, the hub balancing them
UP_W = round(4.434 * 6.0, 1)      # 26.6 W, the uplight strip at full (calculation)
DOWN_W = round(2 * 1.026 * 6.0, 1)  # 12.3 W, two rows of the down strip at full (calculation)
CALL_W = 2.7
UP_TYP = round(LIGHT_BUDGET_W - DOWN_W, 1)   # 9.7 W: the work scene, down-light full, the uplight takes the rest
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
    ("LD08", "Down-light under the right-wall shelf, 2 rows x 1.026 m of Loox5 2168, aimed at the ledge", "PS2",
     "light controller CH2", 1, DOWN_W, DOWN_W, "calculation (2.052 m x 6.0 W/m; maker data)",
     "PM ruling 2026-11-01 (down-light, about 22 W in all, about 300 lx on the ledge); Häfele 25L1-18",
     "about 1990 lm; about 350 lx on the ledge at full (calculation, Lambertian strip 1.2 m above it, no reflections)"),
    ("LD06", "Voice cockpit hook, 12 V 5 A reserved outlet", "PS1", "F1 5 A", 1,
     60.0, 0.0, "DECIDED (D-11 peak; D-88 average)", "REQ-VCK-04; D-88",
     "60 W peak on the hook, 40 W average budget (D-88); kit not fitted in v2, so 0 W typical"),
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
part("cord", "719001", "ELECTRICAL - CORD SET - 220 V VN - 3 M (KIT)", "Điện - bộ dây nguồn 220 V - 3 m", "HS", "710000", 1,
     "", "", None, "calculation (sum of its parts)", process="ships loose in the installation kit; the US version changes only this cord, the inlet side and the socket (REQ-ELE-01)")


# ------------------------------------------------------------------ harness list
# Every joint between parts that are put up separately on site has a plug pair
# (D-26 rule, PM ruling: keyed plugs at every joint). Supply side = receptacle
# with female contacts; load side = plug with male contacts. Lengths: the
# modelled route (calculation) plus the pocket loops and tails (assumption).
PU_IN = 150.0          # mm of lead inside the power unit to its terminal (assumption)
TAIL = 150.0           # mm of tail beyond a grommet or slot, to mate the plugs before hanging (assumption)
LOOP = 150.0           # mm of slack loop in a pocket (= pk_l, assumption)
KIT_LOOP = 500.0       # mm service loop at the voice kit drop (assumption)

AWG18, AWG20, AWG22, AWG24 = 0.823, 0.519, 0.326, 0.205   # mm2 (source: AWG table)


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
        to="RCBO in the power unit", route="SLEEVE in B2's frame bay", circuit="mains 220 V",
        conductors="L, N, PE", cable="H07V-K 1.5 mm2 single cores in the sleeve", area_mm2=1.5,
        length_mm=L("SLEEVE") + 150 + 200, end_a="inlet terminals (powerCON TRUE1 TOP)", end_b="RCBO, PE terminal",
        grommets="sleeve end bushes", amps_max=10.0, note="mains only inside B2 and the unit (D-10, IF-12)")
    add(id="W02", harness_pn="710001", segment="PU", function="mains inside the unit",
        frm="RCBO", to="user socket; PS1, PS2, PS3 inputs", route="inside the power unit", circuit="mains 220 V",
        conductors="L, N (+ PE to the socket)", cable="H05V-K 1.0 mm2", area_mm2=1.0, length_mm=1500,
        length_status="assumption (layout inside the unit)", end_a="RCBO", end_b="socket, supply input leads",
        grommets="", amps_max=10.0, note="supply inputs on their own leads, kept apart from the 12 V side")
    add(id="W03", harness_pn="710001", segment="PU", function="protective bond", frm="PE terminal",
        to="B2 frame (under a unit mounting bolt, serrated washer)", route="inside B2", circuit="PE",
        conductors="PE", cable="H07V-K 2.5 mm2 green-yellow", area_mm2=2.5, length_mm=300,
        length_status="assumption", end_a="M6 ring lug", end_b="M6 ring lug", grommets="", amps_max=None,
        note="B2 is the only panel a mains part touches (compliance note 3)")
    add(id="W04", harness_pn="710001", segment="PU", function="LAN in", frm="etherCON feed-through (outside B2)",
        to="LAN socket port 1 (unit face)", route="SLEEVE in B2's frame bay", circuit="LAN",
        conductors="4 pairs", cable="Cat6 U/UTP patch cord", area_mm2=None, length_mm=L("SLEEVE") + 300,
        end_a="RJ45 plug into the feed-through", end_b="punched down at the socket", grommets="sleeve end bushes",
        amps_max=None, note="plan VT09; the building LAN comes in at v1's position")
    # ---- light feed (PS2) to the light shelf: PU -> B2-CASS -> B4-CASS -> shelf
    add(id="W10a", harness_pn="710001", segment="PU", function="light feed", frm="light controller outputs (PS2) via F2 5 A",
        to="pocket P5 in B2-CASS", route="out of the unit's top, G-PU-TOP", circuit="PS2 lights",
        conductors="+12 V x 2, UP-, DOWN-, CALL-, spare", cable="6 x 18 AWG, Class 2 (CL2 or equivalent)", area_mm2=AWG18,
        length_mm=PU_IN + cross_top + LOOP, end_a="light controller terminals", end_b="Mini-Fit Jr 6-way receptacle",
        grommets="G-PU-TOP", amps_max=LIGHT_A,
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
            ("W30", "voice kit feed", "PS1 kit", "+12 V x 2, 0 V x 2", "4 x 18 AWG (2 per pole), Class 2", AWG18, 2, 5.0, "kit drop"),
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
            to="pocket P1 in B2-CASS", route="out of the unit's right side, S-PU-X", circuit=circ,
            conductors=cond, cable=cable, area_mm2=area, parallel=par, length_mm=PU_IN + cross_side + LOOP,
            end_a={"W20": "PS3 output", "W30": "F1 5 A", "W24": "light controller link, PS2 current sense, PS1 and PS2 rail taps",
                   "W31": "LAN socket port 2"}[wid],
            end_b=end("receptacle"), grommets="S-PU-X", amps_max=amps,
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
                   "W30": "Mini-Fit Jr 4-way receptacle, capped with an empty plug housing (the kit outlet, 12 V 5 A)",
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
        conductors="4 cores (sensor supply, ground, two signal)", cable="4 x 24 AWG shielded", area_mm2=AWG24,
        length_mm=up_chase + L("TO-DR") + 500, end_a="hub sensor connector (HOLD, ISS-060)",
        end_b="sensor probe (HOLD H-ELE-06)", grommets="G-DR", amps_max=None,
        note="the 4 K limit's room reading (D-50, REQ-ELE-04)")
    add(id="W43", harness_pn="710023", segment="COLUMN", function="hub supply", frm="F3c 1 A", to="sensor hub",
        route="hub zone", circuit="PS3 hub", conductors="+12 V, 0 V", cable="2 x 22 AWG", area_mm2=AWG22,
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
SEL = "v2/05-Engineering/hardware/selection.md"
JNT = "v2/05-Engineering/joints/joints-register.md 2.1"
AL = "aluminium 5052-H32"

# ---- power unit 710001: made parts
part("pu_body", "711001", "ELECTRICAL - POWER UNIT - ENCLOSURE BODY", "Điện - hộp nguồn - thân hộp", "MP", "710001", 1,
     AL + " 1.0 mm", "mill finish (hidden, D-79)", 0.469, "CAD (Fusion volume 175,106 mm3 x 2.68 g/cm3, 711001 P01 design)",
     size="296 x 260 x 72, 25 mm side flanges", process="sheet metal: laser cut, folded",
     status="DRAFT; HOLD features: the fixing to B2's frame (WALL, IF-12) and the earth stud hole (PEM data)",
     source="711001_P01_ELECTRICAL-POWER-UNIT-ENCLOSURE-BODY_CAD (electrical_parts_cad.py)",
     note="folded tray 296 x 260 x 72 with 22 mm front lips; two Ø19.1 lead exits (right), Ø19.1 light feed exit (top), "
          "Ø25 sleeve entry (bottom), 4 M4 clinch nut holes in the lips")
part("pu_front", "711002", "ELECTRICAL - POWER UNIT - FRONT PLATE", "Điện - hộp nguồn - mặt trước", "MP", "710001", 1,
     AL + " 1.5 mm", "black anodised AA20 (visible aluminium, D-67)", 0.257,
     "CAD (Fusion volume 96,020 mm3 x 2.68 g/cm3, 711002 P01 design)", size="296 x 260",
     process="laser cut from 1.5 mm sheet as a flat plate; anodised", status="DRAFT; HOLD features: the two 86-plate openings (UTEN codes, H-ELE-04)",
     source="711002_P01_ELECTRICAL-POWER-UNIT-FRONT-PLATE_CAD; DXF 711002_P01_ELECTRICAL-POWER-UNIT-FRONT-PLATE_DXF.dxf (no drawing, D-89 part 4)",
     note="flat plate, its DXF gives the full outline and every hole (D-89 part 4); thickness 1.5 mm; general tolerance "
          "ISO 2768-m; critical holes: the 4 x Ø4.5 M4 holes on the body's clinch nuts (30 and 11 mm from the edges, true "
          "position Ø0.3), the RCBO window 37 x 45 +0.5/0; HOLD: the two 86-plate openings (UTEN codes)")
# ---- power unit 710001: bought parts
part("ps_cv", "718001", "ELECTRICAL - 12 V SUPPLY - 60 W CLASS 2", "Điện - nguồn 12 V 60 W", "PI", "710001", 3,
     "potted plastic case, IP67", "", 0.40, "source", maker="Mean Well", sku="LPV-60-12",
     size="162.5 x 42.5 x 32", status=HOLD_BUY, source=MW_LPV,
     note="PS1 (kit), PS2 (lights, through the light controller) and PS3 (air, hub). 12 V 0-5 A; 90-264 VAC; 83 %; 'Class 2 power unit', UL1310, Class II; "
          "inrush 60 A 525 us at 230 VAC. The maker says not for LED luminaires in the EU or China: check PS2 before an EU version")
part("lightctl", "718002", "ELECTRICAL - LED CONTROLLER - 3 CHANNEL 12 V PWM - RS-485", "Điện - bộ điều khiển đèn 3 kênh",
     "PI", "710001", 1, "", "", 0.10, "assumption", sku="maker HOLD (H-ELE-14)", status=HOLD_BUY,
     source="PM ruling 2026-11-01 (the hub balances uplight, down-light and call light at about 22 W)",
     note="constant-voltage PWM dimmer for 12 V strips, 3 channels (uplight, down-light, call), at least 3 A per channel, "
          "common +12 V, set by the hub over RS-485 (DMX or Modbus); on a lost link it holds its level or goes dark, never brighter")
part("rcbo", "718003", "ELECTRICAL - RCBO - 1P+N C10 30 MA TYPE A", "Điện - CB chống giật 1P+N 10 A 30 mA", "PI", "710001", 1,
     "", "", 0.20, "assumption", maker="Schneider Electric", sku="A9D32610 (Acti9 iDPN Vigi)", size="36 W x 73 D",
     status=HOLD_BUY, source=SE + " (Vietnam datasheet)",
     note="6 kA; type A suits the supplies' electronic inputs. Inrush: Mean Well allows 6 LPV-60 or 16 PWM-60 per C16; "
          "2 + 1 on a C10 uses about 63 % of that (calculation)")
part("inlet", "718004", "ELECTRICAL - APPLIANCE INLET - POWERCON TRUE1 TOP", "Điện - ổ cắm nguồn vào", "PI", "710001", 1,
     "", "", 0.05, "assumption", maker="Neutrik", sku="NAC3MPX-TOP", size="flange 26 x 31 x 4.5; 31.2 behind",
     status=HOLD_BUY, source=NEUTRIK + "; " + SEL,
     note="16 A 250 VAC (EN 60320-1), 20 A 250 VAC (UL 498); plug or unplug under load; UL94 V-0; IP65 mated or capped. "
          "In B2's skin at X 120, Z 313 (v1's spot moved off the closing seam); panel range to confirm (H-ELE-03)")
part("inlet_cap", "718005", "ELECTRICAL - INLET SEALING CAP", "Điện - nắp che ổ nguồn vào", "PI", "710001", 1,
     "", "", 0.01, "assumption", maker="Neutrik", sku="SCNAC-01 (as named in selection E; confirm)", status=HOLD_BUY,
     source=SEL, note="keeps IP65 while unplugged")
part("lan_ft", "718006", "ELECTRICAL - LAN FEED-THROUGH - ETHERCON", "Điện - ổ mạng xuyên vách", "PI", "710001", 1,
     "", "", 0.04, "assumption", maker="Neutrik", sku="NE8FDP", size="flange 26 x 31; 34.55 behind",
     status=HOLD_BUY, source=NEUTRIK + "; " + SEL, note="CAT5e coupler (so the link is CAT5e); panel up to 4 mm")
part("socket", "718007", "ELECTRICAL - USER SOCKET - UTEN S300 UNIVERSAL", "Điện - ổ cắm 5 chấu UTEN S300", "PI", "710001", 1,
     "", "", 0.10, "assumption", maker="UTEN", sku="S300 socket, code HOLD (H-ELE-04)", size="86 x 86",
     status=HOLD_BUY, source=SEL + " (plan VT07)", note="the plan's VT07 set adds a switch P01 doesn't need (ISS-061)")
part("lan_socket", "718008", "ELECTRICAL - LAN SOCKET - UTEN S300 TWO PORT", "Điện - ổ mạng đôi UTEN S300", "PI", "710001", 1,
     "", "", 0.05, "assumption", maker="UTEN", sku="S300 two-port LAN, code HOLD (H-ELE-04; S300G-1PC is the one-port)",
     size="86 x 86", status=HOLD_BUY, source=SEL + " (plan VT09)",
     note="port 1: the building LAN; port 2: the tie line W31 to the voice kit (REQ-VCK-05)")
part("backbox", "718009", "ELECTRICAL - BACK BOX - 86 PLATE", "Điện - đế âm cho mặt 86", "PI", "710001", 2,
     "PC", "", 0.05, "assumption", maker="UTEN", sku="UBBOX/A", size="85 x 85 x 50", status=HOLD_BUY, source=SEL)
part("dinrail", "718010", "ELECTRICAL - DIN RAIL - TS35 X 7.5 - 100 MM", "Điện - thanh ray DIN", "PI", "710001", 1,
     "steel", "zinc plated", 0.03, "assumption", maker="Phoenix Contact", sku="NS 35/7,5 PERF 2000MM, 0801733, cut to 100 (unverified)",
     status=HOLD_BUY, source="EN 60715 TS35", note="carries the RCBO")
part("fuseholder", "718011", "ELECTRICAL - FUSE HOLDER - ATO BLADE - INLINE", "Điện - đế cầu chì lưỡi", "PI", "710001", 2,
     "", "", 0.01, "assumption", sku="HOLD (H-ELE-11)", status=HOLD_BUY, source="ISO 8820-3 blade fuses",
     note="F1 and F2")
part("fuse5", "718012", "ELECTRICAL - FUSE - ATO 5 A 32 V", "Điện - cầu chì 5 A", "PI", "710001", 1, "", "", 0.002,
     "assumption", maker="Littelfuse", sku="0287005 (ATO 287 series; unverified)", status=HOLD_BUY,
     source="ISO 8820-3", note="F1, the voice kit outlet (REQ-VCK-04)")
part("fuse3", "718013", "ELECTRICAL - FUSE - ATO 5 A 32 V - LIGHTS", "Điện - cầu chì 5 A đèn", "PI", "710001", 1, "", "", 0.002,
     "assumption", maker="Littelfuse", sku="0287005 (unverified)", status=HOLD_BUY, source="ISO 8820-3",
     note="F2, the light controller's feed (hardware max 41.6 W)")
part("m4screw", "718019", "ELECTRICAL - SCREW - M4 X 8 - ISO 7045 A2 PAN HEAD", "Điện - vít M4 x 8 inox", "PI", "710001", 4,
     "stainless steel", "plain (A2 stainless)", 0.0015, "assumption", maker="HOLD: standard part",
     sku="ISO 7045 M4 x 8 H, A2-70", size="M4", status=HOLD_BUY, source="this design (README section 3)",
     note="the front plate onto the body's lips")
P["m4screw"].update(length_mm="8", grade="A2-70", torque_nm="HOLD (set on the first unit: A2 M4 into a clinch nut in 1.0 mm aluminium)")
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
part("lug", "718016", "ELECTRICAL - RING TERMINAL - INSULATED 1.5-2.5 MM2", "Điện - đầu cos tròn", "PI", "710001", 5,
     "tinned copper", "", 0.001, "assumption", sku="M5 x 4, M6 x 1; maker HOLD", status=HOLD_BUY, source="",
     note="PE lugs")
part("sleeve", "718017", "ELECTRICAL - CONDUIT - PVC FLEXIBLE - 20 MM", "Điện - ống luồn dây mềm 20", "PI", "710001", 0.6,
     "PVC", "", 0.08, "assumption (kg per m)", sku="maker HOLD", status=HOLD_BUY, source="",
     note="the sleeve in B2's bay, inlet to unit, 0.57 m (route model); qty in m")
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


cable("w15", "718020", "ELECTRICAL - WIRE - H07V-K 1.5 MM2 (BROWN, BLUE, GREEN-YELLOW)", "Điện - dây đơn mềm 1.5", "710001",
      3 * _m(["W01"]), 0.020, "maker HOLD (e.g. a VN 450/750 V flexible core)", "W01: L, N, PE in the sleeve")
cable("w10", "718021", "ELECTRICAL - WIRE - H05V-K 1.0 MM2", "Điện - dây đơn mềm 1.0", "710001", 1.5, 0.014,
      "maker HOLD", "W02 inside the unit (assumption)")
cable("w25", "718022", "ELECTRICAL - WIRE - H07V-K 2.5 MM2 GREEN-YELLOW", "Điện - dây tiếp địa 2.5", "710001", 0.3, 0.032,
      "maker HOLD", "W03 bond lead")
cable("c218", "718023", "ELECTRICAL - CABLE - 2 X 18 AWG - CLASS 2", "Điện - cáp 2 x 18 AWG", "710000",
      _m(["W11b", "W12", "W43"]), 0.025,
      "maker HOLD: 300 V PVC, CL2 or CL3 listed for the US phase", "12 V feeds")
cable("c418", "718024", "ELECTRICAL - CABLE - 4 X 18 AWG - CLASS 2", "Điện - cáp 4 x 18 AWG", "710000",
      _m(["W30a", "W30b", "W30c", "W20a", "W20b", "W20c", "W20d", "W11c"]), 0.045, "maker HOLD: as 718023",
      "voice kit feed and the air feed (2 cores per pole), the right-wall light jumper")
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
         "39-01-2026", 0.0015, "load side of X6"),
        ("rec6", "718045", "ELECTRICAL - CONNECTOR - MINI-FIT JR RECEPTACLE 6 WAY V-0", "Điện - giắc cái 6 chân", "710000", 3,
         "39-01-2065", 0.0035, "the light feed at X1 (unit top), X4 (B2/B4) and X5 (shelf)"),
        ("plug6", "718046", "ELECTRICAL - CONNECTOR - MINI-FIT JR PLUG 6 WAY V-0", "Điện - giắc đực 6 chân", "710000", 3,
         "39-01-2066", 0.0035, "the same joints"),
        ("rec4", "718032", "ELECTRICAL - CONNECTOR - MINI-FIT JR RECEPTACLE 4 WAY V-0", "Điện - giắc cái 4 chân", "710000", 3,
         "39-01-2045", 0.0025, "voice kit feed at X1 and X2, and the kit outlet X7"),
        ("plug4", "718033", "ELECTRICAL - CONNECTOR - MINI-FIT JR PLUG 4 WAY V-0", "Điện - giắc đực 4 chân", "710000", 3,
         "39-01-2046", 0.0025, "X1, X2, and one empty housing as the kit outlet's cap"),
        ("rec10", "718034", "ELECTRICAL - CONNECTOR - MINI-FIT JR RECEPTACLE 10 WAY V-0", "Điện - giắc cái 10 chân", "710000", 3,
         "39-01-2105 (unverified: the pattern of the 2, 4 and 6 way numbers)", 0.005,
         "air feed (2 + 2) and the hub link (6) in one housing at X1, X2, X3"),
        ("plug10", "718035", "ELECTRICAL - CONNECTOR - MINI-FIT JR PLUG 10 WAY V-0", "Điện - giắc đực 10 chân", "710000", 3,
         "39-01-2106 (unverified: as above)", 0.005, "the same joints"),
        ("term_f", "718036", "ELECTRICAL - TERMINAL - MINI-FIT JR FEMALE 18-24 AWG TIN", "Điện - chân giắc cái", "710000", 62,
         "39-00-0039", 0.0003, "1 x 2 + 3 x 6 + 3 x 4 + 3 x 10"),
        ("term_m", "718037", "ELECTRICAL - TERMINAL - MINI-FIT JR MALE 18-24 AWG TIN", "Điện - chân giắc đực", "710000", 58,
         "39-00-0041", 0.0003, "1 x 2 + 3 x 6 + 2 x 4 + 3 x 10 (the cap housing has none)")):
    part(key, pn, name, vi, "PI", parent, qty, "nylon UL94 V-0" if "term" not in key else "tin-plated brass", "", mass,
         "assumption", maker="Molex", sku=sku, status=HOLD_BUY, source=MOLEX,
         note=note + "; 18 AWG: 9 A (2 way), 8 A (4 and 6 way) per circuit, 600 V; UL E29179 (10 way: rating to confirm)")
for key, pn, name, vi, qty, note in (
        ("rj45", "718038", "ELECTRICAL - RJ45 PLUG - CAT6", "Điện - đầu RJ45", 5, "W04 1, W31a 1, W31b 2, W31c 1"),
        ("coupler", "718039", "ELECTRICAL - RJ45 INLINE COUPLER - CAT6", "Điện - đầu nối RJ45", 2, "X1 and X2"),
        ("keystone", "718040", "ELECTRICAL - RJ45 KEYSTONE JACK - CAT6 - WITH DUST CAP", "Điện - nhân mạng RJ45", 1,
         "the kit's data end at X7, capped")):
    part(key, pn, name, vi, "PI", "710000", qty, "", "", 0.005, "assumption", sku="maker HOLD (H-ELE-12)",
         status=HOLD_BUY, source="", note=note)

# ---- protection where cables pass steel, clips, draw cord
part("bushing", "718041", "ELECTRICAL - BUSHING - SHORTY 19.1 HOLE - NYLON", "Điện - vòng đệm luồn dây", "PI", "710000", 8,
     "nylon 6/6 UL94 V-2", "black, as supplied", 0.001, "assumption", maker="Heyco", sku="2836 (SB 750-625, black)",
     status=HOLD_BUY, source=HEYCO,
     note="every hole through a sheet: G-PU-TOP, G-B2-B4 x 2, FX-CEIL, G-CEIL-B, G-CEIL-F (0.5 mm steel), G-DR (DR's back "
          "plate, 1.0-2.7 mm, FRONT HOLD-10), G-SOFFIT (the soffit's casing). Panels to 1.6 mm, passes 15.9: the 0.5 mm fit and "
          "a thicker-panel bushing for G-DR or G-SOFFIT if over 1.6 mm are HOLD H-ELE-01. Felt-only holes take none: no steel edge")
part("edge", "718042", "ELECTRICAL - EDGE PROTECTION STRIP - 0.5 MM SHEET", "Điện - nẹp bảo vệ mép tôn", "PI", "710000", 0.32,
     "PVC or nylon", "", 0.02, "assumption (kg per m)", sku="maker HOLD (H-ELE-01)", status=HOLD_BUY, source="",
     note="the two slots S-PU-X (120 mm edge) and S-CNR (182 mm); qty in m")
part("clip", "718043", "ELECTRICAL - CABLE CLIP - FOR 0.5 MM STEEL TRAY", "Điện - kẹp giữ cáp", "PI", "710000", 24,
     "", "", 0.002, "assumption", sku="maker HOLD (H-ELE-10)", status=HOLD_BUY, source="",
     note="one per 300 mm of route and two per pocket (calculation from the route model); clips to the tray only (D-26)")
part("drawcord", "718044", "ELECTRICAL - DRAW CORD - NYLON 3 MM", "Điện - dây mồi", "PI", "710031",
     round(_m(["W32", "W33"]), 2), "nylon", "", 0.006, "assumption (kg per m)", sku="maker HOLD", status=HOLD_BUY,
     source="", note="W32 and W33; qty in m")

# ---- lights
part("strip_shelf", "718050", "ELECTRICAL - LED STRIP - LOOX5 2168 - 12 V 6.0 W/M - 3000 K", "Điện - LED dây kệ đèn",
     "PI", "710000", 6.486, "", "", 0.02, "assumption (kg per m)", maker="Häfele", sku="833.74.176 (3000 K: confirm the article order 175-178)",
     size="8 mm wide", status=HOLD_BUY, source=HAFELE,
     note="uplight 4.434 m and down-light 2 x 1.026 m; 970 lm/m, Ra > 90, R9 > 50; max 3.5 m per feed (every run here is 1.5 m or less); qty in m")
part("strip_call", "718051", "ELECTRICAL - LED STRIP - LOOX5 2165 - 12 V 3.0 W/M - 3000 K", "Điện - LED dây đèn gọi video",
     "PI", "710024", 0.9, "", "", 0.02, "assumption (kg per m)", maker="Häfele", sku="833.74.156 (3000 K: confirm)",
     size="8 mm wide", status=HOLD_BUY, source=HAFELE, note="about 440 lm for the 0.9 m bar; qty in m")
part("call_profile", "718052", "ELECTRICAL - CALL LIGHT PROFILE AND DIFFUSER - 0.9 M", "Điện - thanh nhôm tán quang đèn gọi",
     "PI", "710024", 1, "aluminium + opal PMMA", "anodised, maker's standard (colour with INTERIOR)", 0.15, "assumption", maker="Häfele", sku="Loox5 profile, article HOLD (H-ELE-09)",
     status=HOLD_BUY, source=HAFELE, note="the maker recommends a diffuser profile for even light")

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
     status=HOLD_BUY, source=SEL, note="locking")
part("cord_wire", "718071", "ELECTRICAL - CORD - H05VV-F 3G1.5", "Điện - dây nguồn mềm 3 x 1.5", "PI", "719001", 3.0, "PVC", "",
     0.12, "assumption (kg per m)", sku="maker HOLD", status=HOLD_BUY, source="", note="3 m; qty in m")
part("plug_vn", "718072", "ELECTRICAL - MAINS PLUG - VN OFFICE SOCKET", "Điện - phích cắm", "PI", "719001", 1, "", "", 0.06,
     "assumption", sku="HOLD: plug type checked with the factory's office sockets", status=HOLD_BUY, source="")


# D-89 part 4: flat sheet parts carry thickness and the general tolerance in their row
P["pu_front"].update(thickness_mm="1.5", tolerance="ISO 2768-m; M4 holes true position Ø0.3; RCBO window +0.5/0")
P["hub_plate"].update(thickness_mm="1.5", tolerance="ISO 2768-m")
P["pu_body"].update(thickness_mm="1.0", tolerance="ISO 2768-m (drawing 711001)")


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
    ("PS1 to the voice kit outlet", ["W30a", "W30b", "W30c"]),
    ("PS2 to the left wall uplight", ["W10a", "W10b", "W10c", "W11a", "W11b"]),
    ("PS2 to the call light", ["W10a", "W10b", "W10c", "W11a", "W11c", "W12"]),
    ("PS3 to the supply fans", ["W20a", "W20b", "W20c", "W20d", "W40"]),
    ("PS3 to the exhaust fans", ["W20a", "W20b", "W20c", "W20d", "W41"]),
    ("PS3 to the sensor hub", ["W20a", "W20b", "W20c", "W20d", "W43"]),
]
