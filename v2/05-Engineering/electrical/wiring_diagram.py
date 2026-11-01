"""The ELECTRICAL P01 wiring diagram: three A1 sheets drawn with PyMuPDF.

Sheet 1: the schematic: mains in the power unit, the three Class 2 supplies,
every 12 V circuit to its loads, and every plug-in joint (X1 to X7).
Sheet 2: the harness list.
Sheet 3: two route views drawn to scale from the route model
(`electrical_model.py`): the back wall and the right wall, seen from inside the
pod, with the lining cassettes, pockets, grommets and routes; the site order and
the keep-outs for other teams.

Sheets 1 and 3 were laid out on A3; they are drawn at twice the size on A1, so
the schematic keeps its overview and every letter is at least 2.5 mm high
(sheet_kit.py: ISO 3098 capital heights, the guideline's "never shrink the font
to fit a page"). Every sheet is checked for overlapping text before it's saved.

Called by electrical_docs.py. Every coordinate on sheet 3 is computed from
the model's parameters, so the views follow the CAD.
"""

import electrical_model as M
import electrical_parts as EP
import fitz  # PyMuPDF
import sheet_kit as K
from sheet_kit import GREY, INK, LIGHT, MAINS, SELV, SIG  # noqa: F401  (colours used below)

DATE = "2026-11-01"
SOURCE = "electrical_model.py, electrical_parts.py"
SHEETS = 3


class Sheet(K.Sheet):
    """An A3 layout drawn at twice the size on A1. textf() takes the font size as laid out on A3 (mm); on paper
    it doubles, and nothing comes out under 2.5 mm capital height."""

    def __init__(self, doc):
        super().__init__(doc, "A1", 2.0)

    def textf(self, x, y, s, size=2.2, color=INK, bold=False):
        self.text(x, y, s, size * K.CAP * self.zoom, color, bold)

    def boxf(self, x0, y0, x1, y1, title, lines=(), color=INK, size=1.9, fill=None):
        self.rect(x0, y0, x1, y1, color, 0.3, fill=fill)
        self.textf(x0 + 1.2, y0 + 3.0, title, 2.1, color, bold=True)
        for i, t in enumerate(lines):
            self.textf(x0 + 1.2, y0 + 6.2 + i * 2.75, t, max(size, 1.8), INK)

    def riser_hops(self, x, y0, y1, hops, color=INK, w=0.3, r=1.2):
        """A vertical wire from y0 to y1 that hops (a half circle to the right) over the wires crossing it at `hops`."""
        import math
        ys = sorted(hops, reverse=(y0 > y1))
        step = -1 if y0 > y1 else 1
        y = y0
        for h in ys:
            self.line(x, y, x, h - step * r, color, w)
            pts = [(x + r * math.sin(math.pi * i / 8), h - step * r * math.cos(math.pi * i / 8)) for i in range(9)]
            self.poly(pts, color, w)
            y = h + step * r
        self.line(x, y, x, y1, color, w)

    def plug(self, x, y, label, color=INK):
        """A plug pair: a socket bracket and a pin bracket, the joint label above."""
        self.line(x - 1.6, y - 1.4, x - 0.4, y - 1.4, color, 0.3)
        self.line(x - 0.4, y - 1.4, x - 0.4, y + 1.4, color, 0.3)
        self.line(x - 1.6, y + 1.4, x - 0.4, y + 1.4, color, 0.3)
        self.line(x + 0.4, y - 1.0, x + 0.4, y + 1.0, color, 0.5)
        self.textf(x - 2.0, y - 2.4, label, 1.8, color, bold=True)

    def fuse(self, x, y, label, color=SELV):
        self.rect(x - 2.2, y - 0.9, x + 2.2, y + 0.9, color, 0.3)
        self.line(x - 2.2, y, x + 2.2, y, color, 0.2)
        self.textf(x - 2.6, y - 1.6, label, 1.6, color)

    def frame(self, title, sheet, scale, notes):
        notes = ["UNITS: mm. GENERAL TOLERANCE: harness lengths +20/-0 mm per segment; route positions +/-5 mm."] + list(notes)
        return self.frame_and_title(title, "710000  ELECTRICAL", sheet, SHEETS, scale, DATE, SOURCE, notes)


def sheet1(doc, rows, harness, v):
    s = Sheet(doc)
    # ---------------- power unit
    s.rect(14, 16, 150, 240, INK, 0.45, dashes="[2 1] 0")
    s.textf(16, 20, "710001 POWER UNIT - in panel B2 (factory wired and tested; earthed aluminium enclosure)", 2.1,
           INK, bold=True)
    s.boxf(18, 26, 52, 46, "INLET  (outside B2)", ["powerCON TRUE1 TOP", "UL 498, 20 A, locking", "v1 position, X 120 Z 313"],
          MAINS)
    s.boxf(62, 26, 96, 46, "BREAKER 1P 15 A", ["UL 489, C curve;", "protects the 14 AWG", "mains wiring"], MAINS)
    s.boxf(106, 26, 146, 46, "GFCI RECEPTACLE", ["TR duplex NEMA 5-15R,", "UL 943 Class A; unit", "face, Z 1050 (D-70)"], MAINS)
    s.line(52, 32, 62, 32, MAINS, 0.5)
    s.textf(53, 31, "L N PE", 1.8, MAINS)
    s.line(96, 32, 106, 32, MAINS, 0.5)
    s.textf(53, 35.6, "W01", 1.8, MAINS)
    s.textf(53, 38.4, "3 x 14", 1.8, MAINS)
    s.textf(53, 41.2, "AWG", 1.8, MAINS)
    for i, (ps, ttl, sub) in enumerate((("PS1", "PS1 + PS4  2 x 60 W", "kit feeds A, B: 12 V each"),
                                        ("PS2", "PS2  60 W + LIGHT CTRL", "3 ch PWM, RS-485, Class 2"),
                                        ("PS3", "PS3  60 W", "12 V 5 A, Class 2"))):
        y = 60 + i * 42
        s.boxf(62, y, 104, y + 26, ttl, [sub, "input 100-240 V", "Class II (no PE)"], SELV)
        s.line(79, 46, 79, y, MAINS, 0.4) if i == 0 else s.line(79, y - 16, 79, y, MAINS, 0.4)
        s.textf(80.5, y - 2, "W02 L N", 1.8, MAINS)
    s.boxf(18, 60, 52, 82, "PE TERMINAL", ["inlet PE, receptacle", "ground, enclosure stud,", "B2 frame bond W03"], MAINS)
    s.line(24, 82, 24, 87, MAINS, 0.3)                    # W03 from the PE terminal to B2's frame (Reviewer 7: it was loose)
    for i, half in enumerate((3.0, 2.0, 1.0)):            # frame (chassis) ground symbol
        s.line(24 - half, 87 + i, 24 + half, 87 + i, MAINS, 0.3)
    s.textf(29, 88.2, "W03 14 AWG green to B2's frame", 1.7, MAINS)
    s.textf(29, 91.2, "(only B2 carries a mains part)", 1.7, MAINS)
    s.boxf(18, 104, 52, 126, "LAN", ["etherCON NE8FDP in B2,", "W04 Cat6 to keystone 1,", "keystone 2: W31 to the kit"], SIG)
    # 12 V outputs leave the unit on the right side (H01, H02) and the top (H03), straight into the cable gap (plain cut-out)
    for yk, fl in ((71, "F1 5 A"), (77, "F4 5 A")):          # the kit's feeds A (PS1) and B (PS4), never joined
        s.fuse(116, yk, fl)
        s.line(104, yk, 113.8, yk, SELV, 0.5)
        s.line(118.2, yk, 150, yk, SELV, 0.5)
    s.fuse(116, 115, "F2 5 A")
    s.line(104, 115, 113.8, 115, SELV, 0.5)
    s.line(118.2, 115, 150, 115, SELV, 0.5)
    s.line(104, 157, 150, 157, SELV, 0.5)
    s.textf(106, 112, "PS2 out", 1.8, SELV)
    s.line(104, 124, 112, 124, SIG, 0.3)
    s.line(112, 124, 112, 190, SIG, 0.3)
    s.line(112, 190, 150, 190, SIG, 0.3)
    s.textf(105, 128, "RS-485", 1.8, SIG)
    s.line(52, 115, 60, 115, SIG, 0.3)
    s.line(60, 115, 60, 210, SIG, 0.3)
    s.line(60, 210, 150, 210, SIG, 0.3)
    s.textf(61, 208, "port 2", 1.8, SIG)
    # ---------------- joints and routes
    xs = (150, 200, 250, 300)
    s.textf(152, 20, "JOINTS AND HARNESS SEGMENTS (plug pair at every joint; cables clip to the cassettes only, D-26)",
           2.0, INK, bold=True)
    for x, lab, y0 in ((150, "X1 unit / B2-CASS", 26), (200, "X2 corner, in R1-CASS", 26), (250, "X3 into the air column", 136)):
        s.textf(x + 1, y0 - 1.5, lab, 1.8, GREY, bold=True)
        s.line(x, y0, x, 236, GREY, 0.15, dashes="[1 1] 0")
    # the kit's two feeds (PS1, PS4), one cable: plug pairs at X1 and X2
    for yk in (71, 77):
        for x in (150, 200):
            s.plug(x, yk, "", SELV)
        s.line(150.4, yk, 199.6, yk, SELV, 0.5)
        s.line(200.4, yk, 240, yk, SELV, 0.5)
    s.textf(152, 69.5, "W30b 4x16 AWG, feeds A, B  B2-CASS", 1.8, SELV)
    s.textf(202, 69.5, "W30c  R1-CASS", 1.8, SELV)
    s.boxf(240, 64, 300, 84, "X7 VOICE KIT DROP (R1, behind the screen)",
          ["two 12 V feeds, 5 A fuse each: Mini-Fit Jr 4-way, capped", "Cat6 keystone, capped; draw wire W32", "reached through felt plug FA-KIT"],
          SELV, 1.8)
    # light feed (PS2) up the back wall
    s.plug(150, 115, "", SELV)
    s.textf(152, 113.5, "W10b B2-CASS", 1.8, SELV)
    s.plug(176, 115, "X4", SELV)
    s.textf(178, 113.5, "W10c B4-CASS", 1.8, SELV)
    s.plug(222, 115, "X5", SELV)
    s.line(176.4, 115, 221.6, 115, SELV, 0.5)
    s.line(150.4, 115, 175.6, 115, SELV, 0.5)
    s.line(222.4, 115, 300, 115, SELV, 0.5)
    s.textf(242, 113.5, "W11 in the shelf (6 x 18 AWG feed)", 1.8, SELV)   # right of the Cat6 riser at X 240
    s.boxf(300, 104, 405, 128, "LIGHT SHELF  (back and side wall tops, D-70)",
           ["uplight %.2f m and down-light 2 x %.3f m (Loox5 2168)," % (EP.UP_M, EP.DOWN_ROW),
            "call drop at Y %.1f (X6) down R2-CASS to the bar;" % v["call_y"],
            "hub keeps up + down + call at about 22 W"], SELV, 1.8)
    # air feed (PS3) + dimming signal to the column
    for x in (150, 200, 250):
        s.plug(x, 157, "", SELV)
        s.plug(x, 190, "", SIG)
    s.textf(152, 155.5, "W20b air feed 4x18 AWG (2 per pole)", 1.8, SELV)
    s.textf(202, 155.5, "W20c R1-CASS", 1.8, SELV)
    s.textf(252, 155.5, "W20d", 1.8, SELV)
    s.line(150.4, 157, 199.6, 157, SELV, 0.5)
    s.line(200.4, 157, 249.6, 157, SELV, 0.5)
    s.line(250.4, 157, 262, 157, SELV, 0.5)
    s.textf(152, 188.5, "W24b hub link 6x24 AWG: RS-485, light current, rails", 1.8, SIG)
    s.textf(152, 166.5, "W20 and W24 share one 10-way plug at X1, X2 and X3", 1.8, GREY)
    s.textf(202, 188.5, "W24c", 1.8, SIG)
    s.textf(252, 188.5, "W24d", 1.8, SIG)
    s.line(150.4, 190, 199.6, 190, SIG, 0.3)
    s.line(200.4, 190, 249.6, 190, SIG, 0.3)
    s.line(250.4, 190, 262, 190, SIG, 0.3)
    # Cat6 to the kit
    for x in (150, 200):
        s.plug(x, 210, "", SIG)
    s.line(150.4, 210, 199.6, 210, SIG, 0.3)
    s.line(200.4, 210, 240, 210, SIG, 0.3)
    s.riser_hops(240, 210, 84, (190, 157, 115), SIG, 0.3)    # W31c's riser hops over W24c, W20c and the light feed
    s.textf(152, 208.5, "W31b Cat6 (RJ45 couplers)", 1.8, SIG)
    s.textf(202, 208.5, "W31c to the kit drop X7", 1.8, SIG)
    # ---------------- air column
    s.rect(262, 136, 405, 236, INK, 0.45, dashes="[2 1] 0")
    s.textf(264, 140, "AIR COLUMN  (front-right inside corner; hub zone 180 x 180 at Z 1200, D-61, D-70)", 1.9, INK, bold=True)
    s.boxf(264, 146, 300, 176, "FUSE BLOCK", ["behind the hub zone cover", "F3a 2 A  supply fans", "F3b 2 A  exhaust fans",
                                             "F3c 1 A  hub"], SELV, 1.8)
    s.boxf(306, 146, 352, 176, "DESK PRO AI SENSOR HUB", ["in-house, cited by name; CO2, presence",
                                                       "out: PWM 1, 2; RS-485 to the lights", "in: tach 1, 2; inlet sensor; buttons;",
                                                       "light current; PS1-PS3 rails (H-ELE-05)"],
          SIG, 1.8)
    s.boxf(358, 146, 403, 160, "SUPPLY FANS S1 S2", ["high in DR; W40 4 x 20 AWG"], SELV, 1.8)
    s.boxf(358, 163, 403, 177, "EXHAUST FANS E1 E2", ["soffit right end; W41"], SELV, 1.8)
    s.boxf(358, 180, 403, 194, "INLET TEMP SENSOR", ["supply fan box inlet; W42"], SIG, 1.8)
    s.boxf(264, 182, 300, 200, "CONTROLS (hub zone)", ["BOOST, TEST, CALL buttons", "LIGHT knob: all hub inputs",
                                                      "(W44); TEST = self-test D-87"], SIG, 1.8)
    s.boxf(306, 182, 352, 200, "CALL LIGHT  (R2, above the screen)", ["900 mm bar, 2.7 W, on light controller CH3;",
                                                                    "fed down from the shelf (X6, W12)", "see the light shelf box"], SELV, 1.8)
    s.line(262, 157, 264, 157, SELV, 0.5)
    s.line(300, 152, 306, 152, SELV, 0.4)
    s.line(352, 153, 358, 153, SELV, 0.4)
    s.line(352, 170, 358, 170, SELV, 0.4)
    s.poly([(352, 174), (355.5, 174), (355.5, 187), (358, 187)], SIG, 0.3)   # the sensor's link starts on the hub
    s.line(262, 190, 264, 190, SIG, 0.3)
    s.boxf(264, 205, 403, 232, "SAFETY AND RESERVES",
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
        "7. Mains: US 120 V 60 Hz, 15 A, UL-listed parts (D-133); the prototype is tested in Vietnam through a 220-to-110 V step-down transformer.",
        "8. Joints: X1 unit/B2-CASS  X2 corner (R1-CASS)  X3 column entry  X4 B2/B4  X5 shelf  X6 call  X7 kit.",
    ]
    s.frame("ELECTRICAL - WIRING DIAGRAM", 1, "not to scale (schematic)", notes)
    return s


def sheet2(doc, rows, harness, v):
    s = K.Sheet(doc, "A1")
    x, y = 16.0, 22.0
    s.text(x, y, "HARNESS LIST  (every field, with conductors, routes, bushings and voltage drop: "
                 "710000_P01_ELECTRICAL-HARNESS-LIST_SPEC.csv)", K.TITLE, INK, True)
    notes = [
        "1. Lengths: route model (calculation) + 150 mm loops and tails (assumption). The kit drop has a 500 mm service loop.",
        "2. Plug pairs: supply side receptacle (female), load side plug (male). W20 and W24 share one 10-way at X1, X2, X3.",
        "3. Every segment is tested in the factory before it ships (D-87): continuity, polarity, no shorts, latch pull.",
        "4. Cables: Class 2 circuits on 300 V PVC cable (CL2 or CL3 listed for the US phase); mains only inside B2 and the unit.",
        "5. W32 and W33 are draw cords, tied off at each hole, for the voice kit's later cables (REQ-VCK-03).",
    ]
    bottom = s.frame_and_title("ELECTRICAL - HARNESS LIST", "710000  ELECTRICAL", 2, SHEETS, "table, not to scale", DATE,
                               SOURCE, ["UNITS: mm. GENERAL TOLERANCE: harness lengths +20/-0 mm per segment; route "
                                        "positions +/-5 mm."] + notes)
    cols = [("ID", 20), ("SEGMENT", 34), ("FUNCTION", 120), ("CABLE", 120), ("L mm", 18), ("END A", 248), ("END B", 248)]
    vals = [[h["id"], h["segment"], h["function"], h["cable"], str(h["length_mm"]), h["end_a"], h["end_b"]] for h in harness]
    _y, left = s.table(x, y + 6.0, cols, vals, bottom - 2.0)
    if left:
        raise ValueError("the harness list needs another sheet: %d rows left" % len(left))
    return s


def sheet3(doc, rows, harness, v):
    s = Sheet(doc)
    k = 1.0 / 20.0
    sk = M.skeleton_boxes(v)
    ox_a, ox_b, oy = 18.0, 165.0, 150.0

    later = []                                            # view labels, placed once every line is drawn

    def lab(x, y, t, col=INK, size=1.9, bold=False):
        s.textf(x, y, t, size, col, bold)

    def vlab(x, y, t, col=INK, size=1.9):
        later.append((x, y, t, col, size, None))
    scale = "1:%g" % round(1.0 / (k * s.zoom))           # on paper: the A3 layout's 1:20 drawn twice the size
    # ---- view A: back wall from inside, looking toward +Y
    X = lambda x: ox_a + (x + 1250) * k  # noqa: E731
    Z = lambda z: oy - z * k  # noqa: E731
    lab(ox_a, oy - 2400 * k - 9, "VIEW A - BACK WALL FROM INSIDE, looking toward +Y   (%s)" % scale, INK, 2.3, True)
    lab(ox_a, oy - 2400 * k - 5, "X view = +X, Y view = +Z; origin O on the room floor at the pod centre", GREY, 1.9)
    s.rect(X(-1250), Z(2400), X(1250), Z(0), GREY, 0.2)
    for code in ("B1-CASS", "B2-CASS", "B3-CASS", "B4-CASS"):
        b = sk[code]
        s.rect(X(b[0]), Z(b[5]), X(b[3]), Z(b[2]), GREY, 0.2, fill=LIGHT)
        vlab(X(b[0]) + 1.5, Z(b[5]) + 3.5, code, GREY, 1.9)
    for b in M.BODIES:
        bx = M.body_box(b, v)
        c = b["code"]
        if c == "PU":
            s.rect(X(bx[0]), Z(bx[5]), X(bx[3]), Z(bx[2]), MAINS, 0.4)
            vlab(X(bx[3]) + 2.0, Z(bx[2]) - 2.0, "power unit X %.0f-%.0f, Z %.0f-%.0f" % (v["pu_x0"], v["pu_x1"], v["pu_z0"], v["pu_z1"]), MAINS)
        elif c in ("INLET", "LAN-FT"):
            s.circle(X((bx[0] + bx[3]) / 2), Z((bx[2] + bx[5]) / 2), (bx[3] - bx[0]) / 2 * k,
                     MAINS if c == "INLET" else SIG, 0.3)
        elif c == "SLEEVE":
            s.rect(X(bx[0]), Z(bx[5]), X(bx[3]), Z(bx[2]), MAINS, 0.25, dashes="[1 1] 0")
        elif c in ("P1", "P4", "P5", "P6", "T1-B2", "L1-B2", "L1-B4", "G-B2-B4", "S-CNR"):
            s.rect(X(bx[0]), Z(bx[5]), X(bx[3]), Z(bx[2]), SELV, 0.3)
        elif c.startswith("C1") or c in ("FX-CEIL", "FX-SHELF", "PU-PLATE"):
            s.rect(X(bx[0]), Z(bx[5]), X(bx[3]), Z(bx[2]), GREY, 0.3)
    vlab(X(200), Z(313) + 1.0, ["inlet X 120 Z 313, LAN Z 375", "(v1's spot, off the X 0 closing seam)"], MAINS)
    vlab(X(400), Z(1100) - 2.0, "trunk Z 1100 to the corner", SELV)
    vlab(X(370), Z(1800), "light feed up B2, B4 (X %.0f)" % v["lt_x"], SELV)
    vlab(X(370), Z(2290) + 3.0, "shelf feed X %.0f Z %.0f" % (v["lt_x"], v["shelf_z"]), SELV)
    # ---- view B: right wall from inside, looking toward +X (front to the right)
    Yv = lambda y: ox_b + (850 - y) * k  # noqa: E731
    lab(ox_b, oy - 2400 * k - 9, "VIEW B - RIGHT WALL FROM INSIDE, looking toward +X   (%s)" % scale, INK, 2.3, True)
    lab(ox_b, oy - 2400 * k - 5, "X view = -Y (front to the right), Y view = +Z", GREY, 1.9)
    s.rect(Yv(850), Z(2400), Yv(-850), Z(0), GREY, 0.2)
    for code in ("R1-CASS", "R2-CASS"):
        b = sk[code]
        s.rect(Yv(b[4]), Z(b[5]), Yv(b[1]), Z(b[2]), GREY, 0.2, fill=LIGHT)
        vlab(Yv(b[4]) + 1.5, Z(b[5]) + 3.5, code, GREY, 1.9)
    s.rect(Yv(v["col_y1"]), Z(M.evaluate("col_z1", v)), Yv(v["col_y0"]), Z(15), INK, 0.35, dashes="[1.5 1] 0")
    vlab(Yv(v["col_y1"]) + 1, Z(M.evaluate("col_z1", v)) + 3.5, "air column", INK)
    for b in M.BODIES:
        bx = M.body_box(b, v)
        c = b["code"]
        if c in ("P2", "P3-KIT", "T1-R1A", "T1-R1B", "CALL-R2", "FS-CNR", "FA-KIT", "FX-COL", "FX-CALL1", "FX-CALL2"):
            s.rect(Yv(bx[4]), Z(bx[5]), Yv(bx[1]), Z(bx[2]), SELV, 0.3)
        elif c in ("CHASE", "TO-SOFFIT", "TO-DR", "HUB"):
            s.rect(Yv(bx[4]), Z(bx[5]), Yv(bx[1]), Z(bx[2]), SIG, 0.35)
    vlab(Yv(v["y_kit"]) - 6, Z(v["trunk_z"] + 260), "X7 kit drop", SELV)
    vlab(Yv(780), Z(v["trunk_z"]) + 5.0, "P2 corner", SELV)
    call = next(M.body_box(b, v) for b in M.BODIES if b["code"] == "CALL-R2")
    call_left = min(Yv(call[1]), Yv(call[4]))                # Reviewer 7: beside its blue bar, outside the column's outline
    later.append((call_left - 1.5 - s.text_w("call light feed", 1.9 * K.CAP * s.zoom), Z(v["call_z"] + 90),
                  "call light feed", SELV, 1.9, [(0, dy) for dy in (0, -3, 3, -6, 6, -9, 9, -12, 12)]))
    vlab(Yv(-300) + 2, Z(v["hub_zc"]), "hub zone", SIG)
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
        ("7  Room cord into the inlet, breaker on, press TEST: PASS (D-87).", False),
        ("", False),
        ("KEEP-OUTS FOR OTHER TEAMS", True),
        ("WALL: B2 bay X %.0f-%.0f, Z %.0f-%.0f for the unit; sleeve X %.0f-%.0f," % (v["pu_x0"], v["pu_x1"], v["pu_z0"], v["pu_z1"], v["sl_x"] - 10, v["sl_x"] + 10), False),
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
        "2. Bushings (Heyco 2836, 19.1 hole): the unit's H01-H03, G-B2-B4 x2, G-CEIL-B/F, G-DR (DR back plate), G-SOFFIT; the slot S-CNR gets an edge strip.",
        "3. Felt-only holes (FX-*, FS-CNR, FA-KIT) go through the felt only, clear of the 12 mm lips: no steel edge, no bushing (no hole through a lip, D-69).",
        "4. These views are the route drawing of 710000; there is no separate Fusion drawing of the route model (PM ruling 2026-11-01).",
    ]
    top = s.frame("ELECTRICAL - ROUTES AND JOINTS", 3, "%s (views)" % scale, notes)
    for x, y, t, col, size, around in later:             # every line is drawn now: each label goes where it's clear
        s.label(x, y, t, size * K.CAP * s.zoom, col, around=around)
    s.first_angle_symbol(s.W - 10 - K.TB_W + 2, top - 18)  # two orthographic views (Reviewer 7)
    return s


def write(pdf_path, png_pattern, v, rows, harness):
    doc = fitz.open()
    for sheet in (sheet1(doc, rows, harness, v), sheet2(doc, rows, harness, v), sheet3(doc, rows, harness, v)):
        sheet.check()                                     # no overlapping text, nothing outside the frame
    doc.set_metadata({"title": "710000 P01 ELECTRICAL - WIRING DIAGRAM", "author": "ELECTRICAL Engineer",
                      "subject": "FocusPod v2 (Spaceship)", "creator": "electrical_docs.py", "producer": "PyMuPDF",
                      "creationDate": "D:20261101000000", "modDate": "D:20261101000000"})
    doc.save(pdf_path, deflate=True, garbage=4, no_new_id=True)
    for i, page in enumerate(doc, start=1):
        page.get_pixmap(dpi=72).save(png_pattern % i)     # A1 at 72 dpi: about the pixels A3 had at 110
    doc.close()
