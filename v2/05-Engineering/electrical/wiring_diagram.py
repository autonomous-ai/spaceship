"""The ELECTRICAL P01 wiring diagram: two A3 sheets drawn with PyMuPDF.

Sheet 1: the schematic: mains in the power unit, the three Class 2 supplies,
every 12 V circuit to its loads, and every plug-in joint (X1 to X7).
Sheet 2: the harness list and two route views drawn to scale from the route
model (`electrical_model.py`): the back wall and the right wall, seen from
inside the pod, with the lining cassettes, pockets, grommets and routes.

Called by electrical_docs.py. Every coordinate on sheet 2 is computed from
the model's parameters, so the views follow the CAD.
"""

import fitz  # PyMuPDF

import electrical_model as M

MMPT = 72.0 / 25.4
W, H = 420.0, 297.0            # A3 landscape, mm
INK = (0.1, 0.1, 0.1)
MAINS = (0.75, 0.1, 0.1)       # mains in red
SELV = (0.05, 0.25, 0.6)       # Class 2 12 V in blue
SIG = (0.2, 0.45, 0.2)         # signals and data in green
GREY = (0.55, 0.55, 0.55)
LIGHT = (0.92, 0.92, 0.92)


class Sheet:
    def __init__(self, doc):
        self.p = doc.new_page(width=W * MMPT, height=H * MMPT)

    def pt(self, x, y):
        return fitz.Point(x * MMPT, y * MMPT)

    def line(self, x0, y0, x1, y1, color=INK, w=0.25, dashes=None):
        self.p.draw_line(self.pt(x0, y0), self.pt(x1, y1), color=color, width=w * MMPT, dashes=dashes)

    def poly(self, pts, color=INK, w=0.35):
        for (a, b), (c, d) in zip(pts, pts[1:]):
            self.line(a, b, c, d, color, w)

    def rect(self, x0, y0, x1, y1, color=INK, w=0.25, fill=None, dashes=None):
        self.p.draw_rect(fitz.Rect(x0 * MMPT, y0 * MMPT, x1 * MMPT, y1 * MMPT), color=color, fill=fill,
                         width=w * MMPT, dashes=dashes)

    def text(self, x, y, s, size=2.2, color=INK, bold=False):
        self.p.insert_text(self.pt(x, y), s, fontsize=size * MMPT, fontname="hebo" if bold else "helv", color=color)

    def box(self, x0, y0, x1, y1, title, lines=(), color=INK, size=1.9, fill=None):
        self.rect(x0, y0, x1, y1, color, 0.3, fill=fill)
        self.text(x0 + 1.2, y0 + 3.0, title, 2.1, color, bold=True)
        for i, s in enumerate(lines):
            self.text(x0 + 1.2, y0 + 6.2 + i * 2.75, s, max(size, 1.8), INK)

    def plug(self, x, y, label, color=INK):
        """A plug pair: a socket bracket and a pin bracket, the joint label above."""
        self.line(x - 1.6, y - 1.4, x - 0.4, y - 1.4, color, 0.3)
        self.line(x - 0.4, y - 1.4, x - 0.4, y + 1.4, color, 0.3)
        self.line(x - 1.6, y + 1.4, x - 0.4, y + 1.4, color, 0.3)
        self.line(x + 0.4, y - 1.0, x + 0.4, y + 1.0, color, 0.5)
        self.text(x - 2.0, y - 2.4, label, 1.8, color, bold=True)

    def fuse(self, x, y, label, color=SELV):
        self.rect(x - 2.2, y - 0.9, x + 2.2, y + 0.9, color, 0.3)
        self.line(x - 2.2, y, x + 2.2, y, color, 0.2)
        self.text(x - 2.6, y - 1.6, label, 1.6, color)

    def frame_and_title(self, title, sheet, scale, notes):
        self.rect(10, 10, W - 10, H - 10, INK, 0.5)
        x0, y0 = W - 10 - 185, H - 10 - 38
        self.rect(x0, y0, W - 10, H - 10, INK, 0.5)
        rows = [("PROJECT", "FocusPod v2 - Spaceship"), ("TITLE", title),
                ("DWG / PART NO.", "710000  ELECTRICAL"), ("REV / STATUS", "%s / DRAFT - not for production" % M.REV),
                ("UNITS / SCALE", "mm / %s" % scale), ("SHEET", "%d of 3" % sheet),
                ("DATE / BY", "2026-10-31 / ELECTRICAL Engineer"), ("SOURCE", "electrical_model.py, electrical_parts.py")]
        for i, (k, v) in enumerate(rows):
            yy = y0 + 4.2 + i * 4.3
            self.text(x0 + 2, yy, k, 1.8, GREY, bold=True)
            self.text(x0 + 36, yy, v, 2.2 if k == "TITLE" else 2.0, INK, bold=(k == "TITLE"))
            if i:
                self.line(x0, yy - 3.1, W - 10, yy - 3.1, GREY, 0.15)
        nx, ny = 12, H - 10 - 38
        self.rect(10, ny, x0 - 2, H - 10, INK, 0.3)
        self.text(nx, ny + 3.5, "NOTES", 2.0, INK, bold=True)
        for i, s in enumerate(notes):
            self.text(nx, ny + 7.0 + i * 2.75, s, 1.8, INK)


def sheet1(doc, rows, harness):
    s = Sheet(doc)
    # ---------------- power unit
    s.rect(14, 16, 150, 240, INK, 0.45, dashes="[2 1] 0")
    s.text(16, 20, "710001 POWER UNIT - in panel B2 (factory wired and tested; earthed aluminium enclosure)", 2.1,
           INK, bold=True)
    s.box(18, 26, 52, 46, "INLET  (outside B2)", ["powerCON TRUE1 TOP", "16 A 250 V, locking", "v1 position, X 120 Z 313"],
          MAINS)
    s.box(62, 26, 96, 46, "RCBO 1P+N", ["C10, 30 mA", "the only mains", "protection"], MAINS)
    s.box(106, 26, 146, 46, "USER SOCKET", ["UTEN S300 (plan VT07)", "on the unit face,", "Z 1000 (PM ruling)"], MAINS)
    s.line(52, 32, 62, 32, MAINS, 0.5)
    s.text(53, 31, "L N PE", 1.8, MAINS)
    s.line(96, 32, 106, 32, MAINS, 0.5)
    s.text(55, 44.5, "W01 3x1.5", 1.8, MAINS)
    for i, (ps, ttl, sub) in enumerate((("PS1", "PS1  60 W", "12 V 5 A, Class 2"),
                                        ("PS2", "PS2  60 W + LIGHT CTRL", "3 ch PWM, RS-485, Class 2"),
                                        ("PS3", "PS3  60 W", "12 V 5 A, Class 2"))):
        y = 60 + i * 42
        s.box(62, y, 104, y + 26, ttl, [sub, "input 100-240 V", "Class II (no PE)"], SELV)
        s.line(79, 46, 79, y, MAINS, 0.4) if i == 0 else s.line(79, y - 16, 79, y, MAINS, 0.4)
        s.text(80.5, y - 2, "W02 L N", 1.8, MAINS)
    s.box(18, 60, 52, 82, "PE TERMINAL", ["inlet PE, socket PE,", "enclosure stud,", "B2 frame bond W03"], MAINS)
    s.line(18, 88, 52, 88, MAINS, 0.3)
    s.text(18, 92, "W03 2.5 mm2 G/Y to B2's frame", 1.7, MAINS)
    s.text(18, 95, "(only B2 carries a mains part)", 1.7, MAINS)
    s.box(18, 104, 52, 126, "LAN", ["etherCON NE8FDP in B2,", "W04 Cat6 to port 1", "port 2: W31 to the kit"], SIG)
    # 12 V outputs leave the unit on the right side (slot S-PU-X) and the top (G-PU-TOP)
    s.fuse(116, 73, "F1 5 A")
    s.line(104, 73, 113.8, 73, SELV, 0.5)
    s.line(118.2, 73, 150, 73, SELV, 0.5)
    s.fuse(116, 115, "F2 5 A")
    s.line(104, 115, 113.8, 115, SELV, 0.5)
    s.line(118.2, 115, 150, 115, SELV, 0.5)
    s.line(104, 157, 150, 157, SELV, 0.5)
    s.text(106, 112, "PS2 out", 1.8, SELV)
    s.line(104, 124, 112, 124, SIG, 0.3)
    s.line(112, 124, 112, 190, SIG, 0.3)
    s.line(112, 190, 150, 190, SIG, 0.3)
    s.text(105, 128, "RS-485", 1.8, SIG)
    s.line(52, 115, 60, 115, SIG, 0.3)
    s.line(60, 115, 60, 210, SIG, 0.3)
    s.line(60, 210, 150, 210, SIG, 0.3)
    s.text(61, 208, "port 2", 1.8, SIG)
    # ---------------- joints and routes
    xs = (150, 200, 250, 300)
    s.text(152, 20, "JOINTS AND HARNESS SEGMENTS (plug pair at every joint; cables clip to the cassettes only, D-26)",
           2.0, INK, bold=True)
    for x, lab in ((150, "X1 unit / B2-CASS"), (200, "X2 corner, in R1-CASS"), (250, "X3 into the air column")):
        s.text(x + 1, 24.5, lab, 1.8, GREY, bold=True)
        s.line(x, 26, x, 236, GREY, 0.15, dashes="[1 1] 0")
    # kit feed (PS1)
    for x in (150, 200):
        s.plug(x, 73, "", SELV)
    s.text(152, 71.5, "W30b 4x18 AWG  B2-CASS", 1.8, SELV)
    s.text(202, 71.5, "W30c  R1-CASS", 1.8, SELV)
    s.line(200.4, 73, 240, 73, SELV, 0.5)
    s.box(240, 64, 300, 84, "X7 VOICE KIT DROP (R1, behind the screen)",
          ["12 V 5 A outlet: Mini-Fit Jr 4-way, capped", "Cat6 keystone, capped; draw wire W32", "reached through felt plug FA-KIT"],
          SELV, 1.8)
    # light feed (PS2) up the back wall
    s.plug(150, 115, "", SELV)
    s.text(152, 113.5, "W10b B2-CASS", 1.8, SELV)
    s.plug(176, 115, "X4", SELV)
    s.text(178, 113.5, "W10c B4-CASS", 1.8, SELV)
    s.plug(222, 115, "X5", SELV)
    s.line(176.4, 115, 221.6, 115, SELV, 0.5)
    s.line(150.4, 115, 175.6, 115, SELV, 0.5)
    s.line(222.4, 115, 300, 115, SELV, 0.5)
    s.text(224, 113.5, "W11 in the shelf (6 x 18 AWG feed)", 1.8, SELV)
    s.box(300, 104, 405, 128, "LIGHT SHELF  (back and side wall tops, D-70)",
          ["uplight 4.43 m and down-light 2 x 1.03 m (Loox5 2168),", "call drop at Y -209.5 (X6) down R2-CASS to the bar;",
           "hub keeps up + down + call at about 22 W"], SELV, 1.8)
    # air feed (PS3) + dimming signal to the column
    for x in (150, 200, 250):
        s.plug(x, 157, "", SELV)
        s.plug(x, 190, "", SIG)
    s.text(152, 155.5, "W20b air feed 4x18 AWG (2 per pole)", 1.8, SELV)
    s.text(202, 155.5, "W20c R1-CASS", 1.8, SELV)
    s.text(252, 155.5, "W20d column", 1.8, SELV)
    s.line(150.4, 157, 199.6, 157, SELV, 0.5)
    s.line(200.4, 157, 249.6, 157, SELV, 0.5)
    s.line(250.4, 157, 262, 157, SELV, 0.5)
    s.text(152, 188.5, "W24b hub link 6x24 AWG: RS-485, light current, rails", 1.8, SIG)
    s.text(152, 166.5, "W20 and W24 share one 10-way plug at X1, X2 and X3", 1.8, GREY)
    s.text(202, 188.5, "W24c", 1.8, SIG)
    s.text(252, 188.5, "W24d", 1.8, SIG)
    s.line(150.4, 190, 199.6, 190, SIG, 0.3)
    s.line(200.4, 190, 249.6, 190, SIG, 0.3)
    s.line(250.4, 190, 262, 190, SIG, 0.3)
    # Cat6 to the kit
    for x in (150, 200):
        s.plug(x, 210, "", SIG)
    s.line(150.4, 210, 199.6, 210, SIG, 0.3)
    s.line(200.4, 210, 240, 210, SIG, 0.3)
    s.line(240, 210, 240, 84, SIG, 0.3)
    s.text(152, 208.5, "W31b Cat6 (RJ45 couplers)", 1.8, SIG)
    s.text(202, 208.5, "W31c to the kit drop X7", 1.8, SIG)
    # ---------------- air column
    s.rect(262, 136, 405, 236, INK, 0.45, dashes="[2 1] 0")
    s.text(264, 140, "AIR COLUMN  (front-right inside corner; hub zone 180 x 180 at Z 1200, D-61, D-70)", 1.9, INK, bold=True)
    s.box(264, 146, 300, 176, "FUSE BLOCK", ["behind the hub zone cover", "F3a 2 A  supply fans", "F3b 2 A  exhaust fans",
                                             "F3c 1 A  hub"], SELV, 1.8)
    s.box(306, 146, 352, 176, "DESK PRO AI SENSOR HUB", ["in-house, cited by name; CO2, presence",
                                                       "out: PWM 1, 2; RS-485 to the lights", "in: tach 1, 2; inlet sensor; buttons;",
                                                       "light current; PS1-PS3 rails (H-ELE-05)"],
          SIG, 1.8)
    s.box(358, 146, 403, 160, "SUPPLY FANS S1 S2", ["high in DR; W40 4 x 20 AWG"], SELV, 1.8)
    s.box(358, 163, 403, 177, "EXHAUST FANS E1 E2", ["soffit right end; W41"], SELV, 1.8)
    s.box(358, 180, 403, 194, "INLET TEMP SENSOR", ["supply fan box inlet; W42"], SIG, 1.8)
    s.box(264, 182, 300, 200, "CONTROLS (hub zone)", ["BOOST, TEST, CALL buttons", "LIGHT knob: all hub inputs",
                                                      "(W44); TEST = self-test D-87"], SIG, 1.8)
    s.box(306, 182, 352, 200, "CALL LIGHT  (R2, above the screen)", ["900 mm bar, 2.7 W, on light controller CH3;",
                                                                    "fed down from the shelf (X6, W12)", "see the light shelf box"], SELV, 1.8)
    s.line(262, 157, 264, 157, SELV, 0.5)
    s.line(300, 152, 306, 152, SELV, 0.4)
    s.line(352, 153, 358, 153, SELV, 0.4)
    s.line(352, 170, 358, 170, SELV, 0.4)
    s.line(352, 187, 358, 187, SIG, 0.3)
    s.line(262, 190, 264, 190, SIG, 0.3)
    s.box(264, 205, 403, 232, "SAFETY AND RESERVES",
          ["SELF-TEST (D-87): TEST checks the 3 rails, runs both fan pairs (tach), steps each light channel (current), reads",
           "the sensors and shows PASS or the failing item. PWM fail-safe: an open PWM line runs the fans at full speed.",
           "Draw wires: W32 kit drop -> column -> soffit (mic, status light); W33 back wall top -> ceiling cassette (D-41,",
           "and the sprinkler or alarm wiring point, ISS-052). Nothing is cut on site later (REQ-VCK-03)."], INK, 1.8)
    notes = [
        "1. Mains (red) exists only inside B2 and the power unit (D-10, IF-12). Nothing mains is connected on site.",
        "2. Every 12 V circuit (blue) is Class 2: each supply is 60 W, the Class 2 limit at 12 V (compliance note).",
        "3. Plug pairs: supply side receptacle (female), load side plug (male); Molex Mini-Fit Jr, keyed by way count.",
        "4. Every cable through sheet steel runs in a grommet; cables clip to the cassette tray only (D-26).",
        "5. Wire sizes and lengths: harness list (sheet 2 and the _SPEC.csv). Voltage drop under 3 %: calc-results.md.",
        "6. Bought parts are on HOLD: no order, no supplier contact. The in-house hub is cited by name only.",
        "7. US version: change the cord set, the inlet side and the socket only; supplies take 100-240 V.",
        "8. Joints: X1 unit/B2-CASS  X2 corner (R1-CASS)  X3 column entry  X4 B2/B4  X5 shelf  X6 call  X7 kit.",
    ]
    s.frame_and_title("ELECTRICAL - WIRING DIAGRAM", 1, "not to scale (schematic)", notes)
    return s


def sheet2(doc, rows, harness, v):
    s = Sheet(doc)
    cols = [("ID", 12), ("SEGMENT", 22), ("FUNCTION", 44), ("CABLE", 56), ("L mm", 12), ("END A", 116), ("END B", 128)]
    x, y = 13, 17
    s.text(x, y, "HARNESS LIST  (every field, with conductors, routes, bushings and voltage drop: "
                 "710000_P01_ELECTRICAL-HARNESS-LIST_SPEC.csv)", 2.4, INK, bold=True)
    y += 5.5
    cx = x
    for name, wdt in cols:
        s.text(cx, y, name, 2.0, GREY, bold=True)
        cx += wdt
    s.line(x, y + 1.2, W - 13, y + 1.2, GREY, 0.2)
    for h in harness:
        y += 6.0
        cx = x
        vals = [h["id"], h["segment"], h["function"], h["cable"], str(h["length_mm"]), h["end_a"], h["end_b"]]
        for (name, wdt), val in zip(cols, vals):
            maxc = int(wdt / 0.98)
            val = val if len(val) <= maxc else val[:maxc - 2] + ".."
            s.text(cx, y, val, 1.9, INK)
            cx += wdt
        s.line(x, y + 1.6, W - 13, y + 1.6, LIGHT, 0.15)
    notes = [
        "1. Lengths: route model (calculation) + 150 mm loops and tails (assumption). The kit drop has a 500 mm service loop.",
        "2. Plug pairs: supply side receptacle (female), load side plug (male). W20 and W24 share one 10-way at X1, X2, X3.",
        "3. Every segment is tested in the factory before it ships (D-87): continuity, polarity, no shorts, latch pull.",
        "4. Cables: Class 2 circuits on 300 V PVC cable (CL2 or CL3 listed for the US phase); mains only inside B2 and the unit.",
        "5. W32 and W33 are draw cords, tied off at each hole, for the voice kit's later cables (REQ-VCK-03).",
    ]
    s.frame_and_title("ELECTRICAL - HARNESS LIST", 2, "table, not to scale", notes)
    return s


def sheet3(doc, rows, harness, v):
    s = Sheet(doc)
    k = 1.0 / 20.0
    sk = M.skeleton_boxes(v)
    ox_a, ox_b, oy = 18.0, 165.0, 150.0

    def lab(x, y, t, col=INK, size=1.9, bold=False):
        s.text(x, y, t, size, col, bold)
    # ---- view A: back wall from inside, looking toward +Y
    X = lambda x: ox_a + (x + 1250) * k  # noqa: E731
    Z = lambda z: oy - z * k  # noqa: E731
    lab(ox_a, oy - 2400 * k - 9, "VIEW A - BACK WALL FROM INSIDE, looking toward +Y   (1:20)", INK, 2.3, True)
    lab(ox_a, oy - 2400 * k - 5, "X view = +X, Y view = +Z; origin O on the room floor at the pod centre", GREY, 1.9)
    s.rect(X(-1250), Z(2400), X(1250), Z(0), GREY, 0.2)
    for code in ("B1-CASS", "B2-CASS", "B3-CASS", "B4-CASS"):
        b = sk[code]
        s.rect(X(b[0]), Z(b[5]), X(b[3]), Z(b[2]), GREY, 0.2, fill=LIGHT)
        lab(X(b[0]) + 1.5, Z(b[5]) + 3.5, code, GREY, 1.9)
    for b in M.BODIES:
        bx = M.body_box(b, v)
        c = b["code"]
        if c == "PU":
            s.rect(X(bx[0]), Z(bx[5]), X(bx[3]), Z(bx[2]), MAINS, 0.4)
            lab(X(bx[0]), Z(bx[2]) + 3.2, "power unit X 95-395, Z 870-1130", MAINS)
        elif c in ("INLET", "LAN-FT"):
            s.p.draw_circle(s.pt(X((bx[0] + bx[3]) / 2), Z((bx[2] + bx[5]) / 2)), (bx[3] - bx[0]) / 2 * k * MMPT,
                            color=MAINS if c == "INLET" else SIG, width=0.3 * MMPT)
        elif c == "SLEEVE":
            s.rect(X(bx[0]), Z(bx[5]), X(bx[3]), Z(bx[2]), MAINS, 0.25, dashes="[1 1] 0")
        elif c in ("P1", "P4", "P5", "P6", "T1-B2", "L1-B2", "L1-B4", "S-PU-X", "G-PU-TOP", "G-B2-B4", "S-CNR"):
            s.rect(X(bx[0]), Z(bx[5]), X(bx[3]), Z(bx[2]), SELV, 0.3)
        elif c.startswith("C1") or c in ("FX-CEIL", "FX-SHELF"):
            s.rect(X(bx[0]), Z(bx[5]), X(bx[3]), Z(bx[2]), GREY, 0.3)
    lab(X(-1240), Z(313) + 0.8, "inlet X 120 Z 313, LAN Z 375 (v1's spot, off the X 0 closing seam)", MAINS)
    lab(X(400), Z(1100) - 2.0, "trunk Z 1100 to the corner", SELV)
    lab(X(370), Z(1800), "light feed up B2, B4 (X 355)", SELV)
    lab(X(370), Z(2290) + 3.0, "shelf feed X 355 Z 2250", SELV)
    # ---- view B: right wall from inside, looking toward +X (front to the right)
    Yv = lambda y: ox_b + (850 - y) * k  # noqa: E731
    lab(ox_b, oy - 2400 * k - 9, "VIEW B - RIGHT WALL FROM INSIDE, looking toward +X   (1:20)", INK, 2.3, True)
    lab(ox_b, oy - 2400 * k - 5, "X view = -Y (front to the right), Y view = +Z", GREY, 1.9)
    s.rect(Yv(850), Z(2400), Yv(-850), Z(0), GREY, 0.2)
    for code in ("R1-CASS", "R2-CASS"):
        b = sk[code]
        s.rect(Yv(b[4]), Z(b[5]), Yv(b[1]), Z(b[2]), GREY, 0.2, fill=LIGHT)
        lab(Yv(b[4]) + 1.5, Z(b[5]) + 3.5, code, GREY, 1.9)
    s.rect(Yv(v["col_y1"]), Z(M.evaluate("col_z1", v)), Yv(v["col_y0"]), Z(15), INK, 0.35, dashes="[1.5 1] 0")
    lab(Yv(v["col_y1"]) + 1, Z(M.evaluate("col_z1", v)) + 3.5, "air column", INK)
    for b in M.BODIES:
        bx = M.body_box(b, v)
        c = b["code"]
        if c in ("P2", "P3-KIT", "T1-R1A", "T1-R1B", "CALL-R2", "FS-CNR", "FA-KIT", "FX-COL", "FX-CALL1", "FX-CALL2"):
            s.rect(Yv(bx[4]), Z(bx[5]), Yv(bx[1]), Z(bx[2]), SELV, 0.3)
        elif c in ("CHASE", "TO-SOFFIT", "TO-DR", "HUB"):
            s.rect(Yv(bx[4]), Z(bx[5]), Yv(bx[1]), Z(bx[2]), SIG, 0.35)
    lab(Yv(v["y_kit"]) - 6, Z(v["trunk_z"] + 260), "X7 kit drop", SELV)
    lab(Yv(780), Z(v["trunk_z"]) + 5.0, "P2 corner", SELV)
    lab(Yv(v["call_y"]) - 3, Z(v["call_z"] + 90), "call light feed", SELV)
    lab(Yv(-300) + 2, Z(v["hub_zc"]), "hub zone", SIG)
    # ---- text column
    tx = 262
    lines = [
        ("RESERVED SPACES IN THE CAD", True),
        ("Routes, pockets, bushings and slots are reserved spaces in the", False),
        ("cassettes' 24 mm gap, in 710000_P01_ELECTRICAL_CAD, derived", False),
        ("from skeleton P04. Pockets: P1 at the unit, P2 in R1-CASS behind", False),
        ("the felt slot FS-CNR (hidden by B2-CASS's end), P4 above the", False),
        ("B2/B4 joint, P5 and P6 the light feed, P3 the voice kit drop.", False),
        ("", False),
        ("SITE ORDER  (two people, one 5 mm key, no electrician)", True),
        ("1  Hang R1-CASS and R2-CASS; their tails stay out.", False),
        ("2  Hold B2-CASS near: plug its leads to the unit (X1) and to", False),
        ("   R1's corner tails (X2), push the pairs into P1 and P2, hang it.", False),
        ("3  B4-CASS: plug X4, push the pair into P4, hang it.", False),
        ("4  Plug the light shelf at X5 when the shelf goes up.", False),
        ("5  Before the air column goes in, plug X3 and X6 behind it.", False),
        ("6  Plug the fans at their boxes (DR inner face; soffit underside).", False),
        ("7  Room cord into the inlet, RCBO on, press TEST: PASS (D-87).", False),
        ("", False),
        ("KEEP-OUTS FOR OTHER TEAMS", True),
        ("WALL: B2 bay X 95-395, Z 870-1130 for the unit; sleeve X 136-156,", False),
        ("Z 301-870; the holes and slots in B2-CASS, B4-CASS, R1-CASS, R2-CASS.", False),
        ("INTERIOR: ledge and screen fixings 15 mm off the trunk band Z 1085-1115.", False),
        ("CEILING: column chase 24 x 24 (X 1140-1164, Y -310 to -286), hub zone,", False),
        ("soffit entry; the ceiling cassette's holes at X 583 (D-41 route).", False),
        ("FRONT: a 19.1 mm bushed hole in DR's back plate, X 1152, Z 2108 (G-DR).", False),
    ]
    yy = 22
    for t, bold in lines:
        lab(tx, yy, t, INK, 1.9, bold)
        yy += 4.1
    notes = [
        "1. Every coordinate in these views is computed from electrical_model.py (skeleton P04 parameters), so they follow the CAD.",
        "2. Bushings (Heyco 2836, 19.1 hole): G-PU-TOP, G-B2-B4 x2, FX-CEIL, G-CEIL-B/F, G-DR (DR back plate), G-SOFFIT; slots get an edge strip.",
        "3. Felt-only holes (FX-*, FS-CNR, FA-KIT) pass felt on the lips with the 24 mm gap behind: no steel edge, no bushing.",
        "4. The Fusion drawing of the route model replaces these views when the drawing start is allowed (screen unlocked).",
    ]
    s.frame_and_title("ELECTRICAL - ROUTES AND JOINTS", 3, "1:20 (views)", notes)
    return s


def write(pdf_path, png_pattern, v, rows, harness):
    doc = fitz.open()
    sheet1(doc, rows, harness)
    sheet2(doc, rows, harness, v)
    sheet3(doc, rows, harness, v)
    doc.set_metadata({"title": "710000 P01 ELECTRICAL - WIRING DIAGRAM", "author": "ELECTRICAL Engineer",
                      "subject": "FocusPod v2 (Spaceship)", "creator": "electrical_docs.py", "producer": "PyMuPDF",
                      "creationDate": "D:20261031000000", "modDate": "D:20261031000000"})
    doc.save(pdf_path, deflate=True, garbage=4)
    for i, page in enumerate(doc, start=1):
        page.get_pixmap(dpi=110).save(png_pattern % i)
    doc.close()
