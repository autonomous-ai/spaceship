"""PDF sheet for the drawing generator (PyMuPDF): ISO sheet, lines, true arcs, hatching, dimensions, tables,
title block, first-angle symbol.

Sheet coordinates are mm from the sheet's lower-left corner, Y up. Arcs and circles are written as cubic
Bezier pieces of at most 90 degrees each (how PDF draws every circle), computed from the true centre and
radius, so a reader recovers the centre and radius exactly. Text is real text in an embedded font, one string
per item, so the checks can read it.
"""

import math
import os

import fitz

MM = 72.0 / 25.4
# Text sizes are given as ISO 3098 letter height h (the capital height), as a reviewer measures them on the print;
# the font size is h over the face's cap height (Helvetica 718/1000, Arial Unicode about the same).
CAP = 0.718
H_TEXT = 2.5        # dimensions, tags, tables, notes: never less (A1/A2 sheets)
H_HEAD = 3.5        # view titles, table titles
H_LABEL = 2.0       # the title block's small field names only

SIZES = {"A3": (420.0, 297.0), "A2": (594.0, 420.0), "A1": (841.0, 594.0), "A0": (1189.0, 841.0)}

# ISO 128-20 line widths for an A1/A2 sheet (group 0.5): visible 0.5, thin 0.25
W_VIS = 0.5
W_THIN = 0.25
W_HID = 0.35
DASH_HID = (3.0, 1.5)              # ISO 128-20 type 02 at 0.35
DASH_CTR = (12.0, 1.5, 1.0, 1.5)   # type 04, long dash dot
BLACK = (0, 0, 0)

FONT_DIRS = ["/System/Library/Fonts/Supplemental", "/Library/Fonts", "/usr/share/fonts/truetype/dejavu"]
# For text outside Windows-1252 (the Vietnamese names). Arial Unicode reads back as typed; Arial, Verdana and
# Times map the space and the hyphen to U+00A0 and U+00AD in the PDF's text layer, which breaks text search.
FONTS = {"reg": ["Arial Unicode.ttf", "DejaVuSans.ttf"], "bold": ["Arial Unicode.ttf", "DejaVuSans-Bold.ttf"]}


def _font_file(kind):
    for d in FONT_DIRS:
        for f in FONTS[kind]:
            p = os.path.join(d, f)
            if os.path.exists(p):
                return p
    return None


# The owner's rule (2026-11-01): every drawing names "Autonomous" as its creator, never a person: in the title
# block's "created by" field and as the PDF's author. The PDF's Creator stays "drawgen", the program that made it
# (the mechanical check and the overwrite guard read it).
AUTHOR = "Autonomous"


class _SegGrid:
    """Segments bucketed in square cells, so 'does any line cross this box' asks only the lines nearby."""

    def __init__(self, cell=10.0):
        self.cell = cell
        self.cells = {}

    def add(self, p, q):
        c = self.cell
        seg = (tuple(p), tuple(q))
        for i in range(int(math.floor(min(p[0], q[0]) / c)), int(math.floor(max(p[0], q[0]) / c)) + 1):
            for j in range(int(math.floor(min(p[1], q[1]) / c)), int(math.floor(max(p[1], q[1]) / c)) + 1):
                self.cells.setdefault((i, j), []).append(seg)

    def near(self, box, gap):
        c = self.cell
        seen = set()
        for i in range(int(math.floor((box[0] - gap) / c)), int(math.floor((box[2] + gap) / c)) + 1):
            for j in range(int(math.floor((box[1] - gap) / c)), int(math.floor((box[3] + gap) / c)) + 1):
                for sg in self.cells.get((i, j), ()):
                    if id(sg) not in seen:
                        seen.add(id(sg))
                        yield sg


class Sheet:
    def __init__(self, size="A1", creator="drawgen", title="", subject="", keywords=""):
        self.size = size
        self.W, self.H = SIZES[size]
        self.doc = fitz.open()
        self.meta = {"creator": creator, "producer": "drawgen (tools/drawgen, PyMuPDF %s)" % fitz.VersionBind,
                     "title": title, "subject": subject, "keywords": keywords, "author": AUTHOR}
        self.pages = []
        self.fonts = {}
        for k in ("reg", "bold"):
            f = _font_file(k)
            self.fonts[k] = f
        self.new_page()

    # ------------------------------------------------------------ pages and coordinates
    def new_page(self):
        self.page = self.doc.new_page(width=self.W * MM, height=self.H * MM)
        self.pages.append(self.page)
        self.shape = self.page.new_shape()
        self._registered = set()
        self.boxes = []         # ink boxes of the text written on this page (x0, y0, x1, y1)
        self.obstacles = []     # part outlines on this page, as segments, for placing labels clear of them
        self.grid = _SegGrid()  # every line drawn on this page (outlines included), for the same
        self.reserved = []      # areas kept for what is drawn later (the table column): no label goes there
        return self.page

    # ------------------------------------------------------------ keeping labels clear (the read-back checks it)
    def add_obstacles(self, segs):
        self.obstacles.extend(segs)
        for p, q in segs:
            self.grid.add(p, q)

    def _rec(self, pts, close=False):
        """Remember a drawn stroke's segments (labels placed later keep clear of them)."""
        for k in range(len(pts) - 1):
            self.grid.add(pts[k], pts[k + 1])
        if close and len(pts) > 2:
            self.grid.add(pts[-1], pts[0])

    @staticmethod
    def _bez_pts(p0, c1, c2, p1, n=8):
        out = []
        for k in range(n + 1):
            t = k / float(n)
            a, b, c, d = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3
            out.append((a * p0[0] + b * c1[0] + c * c2[0] + d * p1[0], a * p0[1] + b * c1[1] + c * c2[1] + d * p1[1]))
        return out

    @staticmethod
    def _boxes_touch(a, b, gap=0.4):
        return a[0] - gap < b[2] and b[0] - gap < a[2] and a[1] - gap < b[3] and b[1] - gap < a[3]

    @staticmethod
    def _seg_box(p, q, box, gap=0.4):
        x0, y0, x1, y1 = box[0] - gap, box[1] - gap, box[2] + gap, box[3] + gap
        dx, dy = q[0] - p[0], q[1] - p[1]
        t0, t1 = 0.0, 1.0
        for pp, qq in ((-dx, p[0] - x0), (dx, x1 - p[0]), (-dy, p[1] - y0), (dy, y1 - p[1])):
            if abs(pp) < 1e-12:
                if qq < 0:
                    return False
            else:
                r = qq / pp
                if pp < 0:
                    t0 = max(t0, r)
                else:
                    t1 = min(t1, r)
                if t0 > t1:
                    return False
        return True

    def is_free(self, box):
        if box[0] < 22 or box[2] > self.W - 12 or box[1] < 12 or box[3] > self.H - 12:
            return False
        if any(self._boxes_touch(box, b) for b in self.boxes + self.reserved):
            return False
        return not any(self._seg_box(p, q, box) for p, q in self.grid.near(box, 0.4))

    def text_box(self, x, y, s, size=2.5, anchor="left", rotate=0, bold=False, valign="base"):
        """The ink box text() would cover, without writing."""
        w = self.text_width(str(s), size, bold)
        dx = {"left": 0.0, "center": -w / 2, "right": -w}[anchor]
        dy = -0.5 * size if valign == "mid" else 0.0
        if rotate == 0:
            return (x + dx, y + dy, x + dx + w, y + dy + size)
        bx, by = x - dy, y + dx
        return (bx - size, by, bx, by + w)

    def P(self, x, y):
        return fitz.Point(x * MM, (self.H - y) * MM)

    def flush(self):
        self.shape.commit()
        self.shape = self.page.new_shape()

    # ------------------------------------------------------------ strokes
    def _finish(self, width, dashes=None, fill=None, close=False, color=BLACK):
        d = None
        if dashes:
            d = "[%s] 0" % " ".join("%.3f" % (v * MM) for v in dashes)
        self.shape.finish(width=width * MM, color=color, fill=fill, dashes=d, closePath=close, lineCap=0,
                          lineJoin=1)

    def line(self, p, q, w=W_VIS, dashes=None, color=BLACK):
        self.shape.draw_line(self.P(*p), self.P(*q))
        self._finish(w, dashes, color=color)
        self._rec([p, q])

    def polyline(self, pts, w=W_THIN, close=False, fill=None, dashes=None):
        self.shape.draw_polyline([self.P(*p) for p in pts])
        self._finish(w, dashes, fill=fill, close=close)
        self._rec(list(pts), close or fill is not None)

    def _arc_pieces(self, c, r, a0, a1):
        """Bezier pieces (p0, c1, c2, p1) in sheet mm for the arc a0..a1 (radians, counter-clockwise)."""
        span = a1 - a0
        n = max(1, int(math.ceil(abs(span) / (math.pi / 2) - 1e-9)))
        d = span / n
        k = 4.0 / 3.0 * math.tan(d / 4.0) * r
        out = []
        for i in range(n):
            s, e = a0 + i * d, a0 + (i + 1) * d
            p0 = (c[0] + r * math.cos(s), c[1] + r * math.sin(s))
            p1 = (c[0] + r * math.cos(e), c[1] + r * math.sin(e))
            c1 = (p0[0] - k * math.sin(s), p0[1] + k * math.cos(s))
            c2 = (p1[0] + k * math.sin(e), p1[1] - k * math.cos(e))
            out.append((p0, c1, c2, p1))
        return out

    def arc(self, c, r, a0, a1, w=W_VIS, dashes=None, fill=None):
        for p0, c1, c2, p1 in self._arc_pieces(c, r, a0, a1):
            self.shape.draw_bezier(self.P(*p0), self.P(*c1), self.P(*c2), self.P(*p1))
            self._rec(self._bez_pts(p0, c1, c2, p1))
        self._finish(w, dashes, fill=fill, close=False)

    def circle(self, c, r, w=W_VIS, dashes=None, fill=None):
        self.arc(c, r, 0.0, 2 * math.pi, w, dashes, fill)

    def bezier(self, pts, w=W_VIS, dashes=None):
        for i in range(0, len(pts) - 1, 3):
            self.shape.draw_bezier(self.P(*pts[i]), self.P(*pts[i + 1]), self.P(*pts[i + 2]), self.P(*pts[i + 3]))
            self._rec(self._bez_pts(pts[i], pts[i + 1], pts[i + 2], pts[i + 3]))
        self._finish(w, dashes)

    def rect(self, x, y, w, h, lw=W_THIN, fill=None):
        self.shape.draw_rect(fitz.Rect(self.P(x, y + h), self.P(x + w, y)))
        self._finish(lw, fill=fill, close=True)
        self._rec([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], close=True)

    def arrow(self, tip, direction, length=3.0, width=1.0):
        """Filled ISO arrowhead (closed, 15 degrees half angle)."""
        dx, dy = direction
        L = math.hypot(dx, dy)
        dx, dy = dx / L, dy / L
        bx, by = tip[0] - dx * length, tip[1] - dy * length
        nx, ny = -dy * width / 2, dx * width / 2
        self.polyline([tip, (bx + nx, by + ny), (bx - nx, by - ny)], w=0.1, close=True, fill=BLACK)

    # ------------------------------------------------------------ text
    @staticmethod
    def _latin(s):
        try:
            s.encode("cp1252")
            return True
        except UnicodeEncodeError:
            return False

    def text_width(self, s, size, bold=False):
        fs = size / CAP
        if self._latin(s) or not self.fonts["bold" if bold else "reg"]:
            return fitz.get_text_length(s, fontname="hebo" if bold else "helv", fontsize=fs * MM) / MM
        return self._font_obj(bold).text_length(s, fontsize=fs * MM) / MM

    def _font_obj(self, bold):
        key = "fobj_bold" if bold else "fobj_reg"
        if key not in self.__dict__:
            self.__dict__[key] = fitz.Font(fontfile=self.fonts["bold" if bold else "reg"])
        return self.__dict__[key]

    def text(self, x, y, s, size=2.5, anchor="left", rotate=0, bold=False, valign="base"):
        """Write s with its baseline at (x, y); anchor left/center/right along the text direction. rotate: 0 or
        90 (reading upward). valign 'mid' centres the text's cap height on y. Text that fits Windows-1252 uses
        the PDF's built-in Helvetica (spaces and hyphens read back as plain ASCII); other text (the Vietnamese
        names) uses an embedded Unicode font."""
        if s is None or s == "":
            return
        s = str(s)
        w = self.text_width(s, size, bold)
        dx = {"left": 0.0, "center": -w / 2, "right": -w}[anchor]
        dy = -0.5 * size if valign == "mid" else 0.0
        if self._latin(s) or not self.fonts["bold" if bold else "reg"]:
            fname, ffile = ("hebo" if bold else "helv"), None
        else:
            kind = "bold" if bold else "reg"
            fname, ffile = "F" + kind, self.fonts[kind]
        if rotate == 0:
            pt = self.P(x + dx, y + dy)
        else:       # reading upward: the text runs along +y
            pt = self.P(x - dy, y + dx)
        self.page.insert_text(pt, s, fontsize=size / CAP * MM, fontname=fname, fontfile=ffile, rotate=rotate,
                              color=BLACK)
        self.boxes.append(self.text_box(x, y, s, size, anchor, rotate, bold, valign))
        return w

    def wrap(self, s, size, width, bold=False):
        words, lines, cur = s.split(" "), [], ""
        for wd in words:
            t = (cur + " " + wd).strip()
            if cur and self.text_width(t, size, bold) > width:
                lines.append(cur)
                cur = wd
            else:
                cur = t
        if cur:
            lines.append(cur)
        return lines

    def paragraph(self, x, y, s, size, width, lead=1.45, bold=False):
        """Wrapped text from the top line's baseline at y down; returns the y below the last line."""
        for ln in self.wrap(s, size, width, bold):
            self.text(x, y, ln, size, bold=bold)
            y -= size * lead
        return y

    # ------------------------------------------------------------ hatching (ISO 128-50)
    def hatch(self, loops, spacing=1.0, angle=45.0, w=0.18, solid_below=None):
        """Hatch the region bounded by loops (lists of sheet prims: ('line', p, q) or ('arc', c, r, a0, a1)),
        even-odd. solid_below: fill solid instead when the region is narrower than this (mm on paper)."""
        segs = []
        for loop in loops:
            segs.extend(loop)
        if solid_below is not None:
            pass
        th = math.radians(angle)
        ca, sa = math.cos(th), math.sin(th)
        # rotate so hatch lines are horizontal in (u, v): v = -x sin + y cos
        def rot(p):
            return (p[0] * ca + p[1] * sa, -p[0] * sa + p[1] * ca)

        def unrot(u, v):
            return (u * ca - v * sa, u * sa + v * ca)
        vs = []
        for sg in segs:
            if sg[0] == "line":
                vs += [rot(sg[1])[1], rot(sg[2])[1]]
            else:
                c, r = sg[1], sg[2]
                vc = rot(c)[1]
                vs += [vc - r, vc + r]
        if not vs:
            return
        v0, v1 = min(vs), max(vs)
        k0 = math.floor(v0 / spacing) + 1
        out = []
        k = k0
        while k * spacing < v1:
            v = k * spacing
            xs = []
            for sg in segs:
                if sg[0] == "line":
                    (u1, w1), (u2, w2) = rot(sg[1]), rot(sg[2])
                    if (w1 - v) * (w2 - v) < 0:
                        t = (v - w1) / (w2 - w1)
                        xs.append(u1 + t * (u2 - u1))
                else:
                    _, c, r, a0, a1 = sg
                    uc, vc = rot(c)
                    d = v - vc
                    if abs(d) >= r:
                        continue
                    h = math.sqrt(r * r - d * d)
                    for uu in (uc - h, uc + h):
                        # angle of this point in the sheet frame
                        px, py = unrot(uu, v)
                        a = math.atan2(py - c[1], px - c[0])
                        aa = a0 + ((a - a0) % (2 * math.pi))
                        if aa <= a1 + 1e-9:
                            xs.append(uu)
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                out.append((unrot(xs[i], v), unrot(xs[i + 1], v)))
            k += 1
        for p, q in out:
            self.shape.draw_line(self.P(*p), self.P(*q))
            self._rec([p, q])
        if out:
            self._finish(w)

    @staticmethod
    def _ends(sg):
        if sg[0] == "line":
            return sg[1], sg[2]
        c, r, a0, a1 = sg[1], sg[2], sg[3], sg[4]
        return (c[0] + r * math.cos(a0), c[1] + r * math.sin(a0)), (c[0] + r * math.cos(a1), c[1] + r * math.sin(a1))

    def _chain(self, segs, tol=1e-3):
        """Order segments into closed chains: [(seg, reversed)] lists."""
        left = list(segs)
        chains = []
        while left:
            cur = [(left.pop(0), False)]
            start = self._ends(cur[0][0])[0]
            end = self._ends(cur[0][0])[1]
            grown = True
            while grown and math.dist(start, end) > tol:
                grown = False
                for i, sg in enumerate(left):
                    a, b = self._ends(sg)
                    if math.dist(a, end) < tol:
                        cur.append((sg, False))
                        end = b
                    elif math.dist(b, end) < tol:
                        cur.append((sg, True))
                        end = a
                    else:
                        continue
                    left.pop(i)
                    grown = True
                    break
            chains.append(cur)
        return chains

    def _path(self, chain):
        """One closed subpath: each piece starts exactly where the last one ended (PDF needs that to join
        them; edge ends from the kernel differ in the last digits)."""
        cur = None
        for sg, rev in chain:
            if sg[0] == "line":
                a, b = (sg[2], sg[1]) if rev else (sg[1], sg[2])
                start = cur if cur is not None else self.P(*a)
                end = self.P(*b)
                self.shape.draw_line(start, end)
                self._rec([a, b])
                cur = end
            else:
                pieces = self._arc_pieces(sg[1], sg[2], sg[3], sg[4])
                if rev:
                    pieces = [(p1, c2, c1, p0) for p0, c1, c2, p1 in reversed(pieces)]
                for p0, c1, c2, p1 in pieces:
                    start = cur if cur is not None else self.P(*p0)
                    end = self.P(*p1)
                    self.shape.draw_bezier(start, self.P(*c1), self.P(*c2), end)
                    self._rec(self._bez_pts(p0, c1, c2, p1))
                    cur = end

    def fill_loops(self, loops):
        """Solid fill (ISO 128-50 for thin sections), even-odd over the loops' outlines chained into paths."""
        for loop in loops:
            for chain in self._chain(loop):
                self._path(chain)
        self.shape.finish(width=0.1 * MM, color=BLACK, fill=BLACK, even_odd=True, closePath=True)

    # ------------------------------------------------------------ dimensions (ISO 129-1)
    def dim_linear(self, p1, p2, side, gap, text, size=2.5, ext_gap=1.0, ext_over=1.5, slide=False):
        """A linear dimension between sheet points p1 and p2, measured horizontally (side 'up'/'down') or
        vertically ('left'/'right'); the dimension line sits gap mm beyond the farther point on that side. The
        value sits on the far side of the line from the part, centred, or beside the line when it doesn't fit
        between the arrows (ISO 129-1). slide: a value beside the line moves out along it, the line extended, until
        it touches no other text and no line."""
        tw = self.text_width(text, size)
        if side in ("up", "down"):
            sgn = 1 if side == "up" else -1
            yl = (max(p1[1], p2[1]) + gap) if sgn > 0 else (min(p1[1], p2[1]) - gap)
            for p in (p1, p2):
                self.line((p[0], p[1] + sgn * ext_gap), (p[0], yl + sgn * ext_over), W_THIN)
            a, b = (min(p1[0], p2[0]), yl), (max(p1[0], p2[0]), yl)
            span = b[0] - a[0]
            ty = yl + 0.8 if sgn > 0 else yl - 0.8 - size
            if span > 8:
                self.line(a, b, W_THIN)
                self.arrow(a, (-1, 0))
                self.arrow(b, (1, 0))
            else:       # arrows from outside
                self.line((a[0] - 4, yl), (b[0] + 4, yl), W_THIN)
                self.arrow(a, (1, 0))
                self.arrow(b, (-1, 0))
            if tw + 2 <= span:
                self.text((a[0] + b[0]) / 2, ty, text, size, "center")
            else:
                off = 6.0
                if slide:
                    off = next((o for o in [6.0 + 1.0 * k for k in range(40)]
                                if self.is_free(self.text_box(b[0] + o, yl - 0.35 * size, text, size, "left"))), 6.0)
                self.line(b, (b[0] + off - 1.0, yl), W_THIN)
                self.text(b[0] + off, yl - 0.35 * size, text, size, "left")
        else:
            sgn = 1 if side == "right" else -1
            xl = (max(p1[0], p2[0]) + gap) if sgn > 0 else (min(p1[0], p2[0]) - gap)
            for p in (p1, p2):
                self.line((p[0] + sgn * ext_gap, p[1]), (xl + sgn * ext_over, p[1]), W_THIN)
            a, b = (xl, min(p1[1], p2[1])), (xl, max(p1[1], p2[1]))
            span = b[1] - a[1]
            if span > 8:
                self.line(a, b, W_THIN)
                self.arrow(a, (0, -1))
                self.arrow(b, (0, 1))
            else:
                self.line((xl, a[1] - 4), (xl, b[1] + 4), W_THIN)
                self.arrow(a, (0, 1))
                self.arrow(b, (0, -1))
            tx = xl - 0.8 if sgn < 0 else xl + 0.8 + size
            if tw + 2 <= span:
                self.text(tx, (a[1] + b[1]) / 2, text, size, "center", rotate=90)
            else:
                self.text(tx, b[1] + 6, text, size, "left", rotate=90)

    def ordinate(self, origin, pts, axis, level, values, size=2.2, ext_gap=1.0, min_step=3.2):
        """Ordinate dimensions (ISO 129-1 9.3): from each sheet point an extension line to `level` (a y for
        axis 'x', an x for axis 'y'), the value written along it; values of points sharing a position once.
        origin: the sheet point of 0, marked '0'. Labels are spread so they don't overlap."""
        items = sorted(set((round(p[0 if axis == "x" else 1], 3), v) for p, v in zip(pts, values)))
        items = [(origin[0 if axis == "x" else 1], "0")] + [it for it in items
                                                         if abs(it[0] - origin[0 if axis == "x" else 1]) > 1e-6]
        # spread label positions
        pos = [it[0] for it in items]
        lab = list(pos)
        for i in range(1, len(lab)):
            if lab[i] - lab[i - 1] < min_step:
                lab[i] = lab[i - 1] + min_step
        for (c, v), lp in zip(items, lab):
            if axis == "x":
                src = [p for p in pts if abs(p[0] - c) < 1e-3]
                y0 = (max(p[1] for p in src) if src and level > src[0][1] else
                      min(p[1] for p in src)) if src else origin[1]
                sgn = 1 if level > y0 else -1
                y1 = level - sgn * 2.0
                self.line((c, y0 + sgn * ext_gap), (c, y1), W_THIN)
                if abs(lp - c) > 1e-6:
                    self.line((c, y1), (lp, level), W_THIN)
                else:
                    self.line((c, y1), (c, level), W_THIN)
                self.text(lp + 0.75, level + sgn * 0.6 if sgn > 0 else level - 0.6, v, size,
                          "left" if sgn > 0 else "right", rotate=90)
            else:
                src = [p for p in pts if abs(p[1] - c) < 1e-3]
                x0 = (max(p[0] for p in src) if src and level > src[0][0] else
                      min(p[0] for p in src)) if src else origin[0]
                sgn = 1 if level > x0 else -1
                x1 = level - sgn * 2.0
                self.line((x0 + sgn * ext_gap, c), (x1, c), W_THIN)
                if abs(lp - c) > 1e-6:
                    self.line((x1, c), (level, lp), W_THIN)
                else:
                    self.line((x1, c), (level, c), W_THIN)
                self.text(level + sgn * 0.6, lp - 0.75 if False else lp, v, size,
                          "left" if sgn > 0 else "right", valign="mid")

    # ------------------------------------------------------------ marks
    def centre_mark(self, c, r, w=W_THIN, ext=2.0):
        """Centre lines of a hole: two short chain lines crossing at the centre, extending ext past the hole."""
        L = r + ext
        dash = DASH_CTR if 2 * L > 14 else None
        self.line((c[0] - L, c[1]), (c[0] + L, c[1]), w, dash)
        self.line((c[0], c[1] - L), (c[0], c[1] + L), w, dash)

    def centre_line(self, p, q, w=W_THIN):
        self.line(p, q, w, DASH_CTR)

    def origin_mark(self, o, name, xdir=(1, 0), ydir=(0, 1), size=2.5, away=(-1.0, -1.0), label_y=None):
        """The 2D origin of a view's X/Y: a small circle with its name and the +X, +Y arrows."""
        self.circle(o, 1.2, W_THIN)
        L = 9.0
        for d, lab in ((xdir, "+X"), (ydir, "+Y")):
            tip = (o[0] + d[0] * L, o[1] + d[1] * L)
            self.line((o[0] + d[0] * 1.2, o[1] + d[1] * 1.2), tip, W_THIN)
            self.arrow(tip, d, 2.2, 0.9)
            # beside the arrow's tip, on whichever side is clear
            if d[1] == 0:
                cands = [(tip[0] + d[0] * 1.2, tip[1] - size / 2, "left" if d[0] >= 0 else "right"),
                         (tip[0] - d[0] * 1.5, tip[1] + 1.0, "right" if d[0] >= 0 else "left"),
                         (tip[0] - d[0] * 1.5, tip[1] - size - 1.0, "right" if d[0] >= 0 else "left"),
                         (tip[0] + d[0] * 1.2, tip[1] + 1.5, "left" if d[0] >= 0 else "right"),
                         (tip[0] + d[0] * 1.2, tip[1] - size - 1.5, "left" if d[0] >= 0 else "right")]
            else:
                cands = [(tip[0] + 1.0, tip[1] + d[1] * 1.2 - (size if d[1] < 0 else 0), "left"),
                         (tip[0] - 1.0, tip[1] - d[1] * 2.0, "right"),
                         (tip[0] + 1.0, tip[1] - d[1] * 2.0 - (size if d[1] > 0 else 0), "left"),
                         (tip[0] - 1.5, tip[1] + d[1] * 1.2 - (size if d[1] < 0 else 0), "right"),
                         (tip[0], tip[1] + d[1] * (2.5 + (size if d[1] > 0 else 0)) - (0 if d[1] > 0 else size), "center"),
                         (tip[0] + 4.0, tip[1] - d[1] * 4.0, "left"), (tip[0] - 4.0, tip[1] - d[1] * 4.0, "right")]
            pick = next((c_ for c_ in cands if self.is_free(self.text_box(c_[0], c_[1], lab, size, c_[2]))), cands[0])
            self.text(pick[0], pick[1], lab, size, pick[2])
        # the name outside the part's outline, on the corner's outer side (or at label_y, off the outline)
        if label_y is not None:
            self.line((o[0], o[1] - 1.2 if label_y < o[1] else o[1] + 1.2), (o[0], label_y + (size + 0.6 if label_y < o[1] else -0.6)), 0.18)
            cands = [(o[0], label_y, "center"), (o[0] - 2.0, label_y, "right"), (o[0] + 2.0, label_y, "left")]
        else:
            cands = [(o[0] + away[0] * 2.2, o[1] + (away[1] * 2.2 if away[1] > 0 else away[1] * 2.2 - size),
                      "right" if away[0] < 0 else "left"),
                     (o[0] + away[0] * 2.2, o[1] - (away[1] * 2.2 if away[1] > 0 else away[1] * 2.2 - size) - size,
                      "right" if away[0] < 0 else "left"),
                     (o[0] - away[0] * 3.5, o[1] + (away[1] * 2.2 if away[1] > 0 else away[1] * 2.2 - size),
                      "left" if away[0] < 0 else "right")]
        pick = next((c_ for c_ in cands if self.is_free(self.text_box(c_[0], c_[1], name, size, c_[2], bold=True))),
                    cands[0])
        self.text(pick[0], pick[1], name, size, pick[2], bold=True)

    @staticmethod
    def _datum_parts(at, direction, size=2.5, leader=7.0):
        dx, dy = direction
        L = math.hypot(dx, dy)
        dx, dy = dx / L, dy / L
        nx, ny = -dy, dx
        t = 1.6
        tri = [(at[0] + nx * t, at[1] + ny * t), (at[0] - nx * t, at[1] - ny * t),
               (at[0] + dx * t * 1.6, at[1] + dy * t * 1.6)]
        end = (at[0] + dx * leader, at[1] + dy * leader)
        b = size * 2.4
        bx, by = end[0] + dx * b / 2 - b / 2, end[1] + dy * b / 2 - b / 2
        return tri, (tri[2], end), (bx, by, bx + b, by + b)

    def datum_free(self, at, direction, size=2.5, leader=7.0):
        """True when the datum symbol there would touch no text and its frame no line."""
        tri, (s, e), box = self._datum_parts(at, direction, size, leader)
        if not self.is_free(box):
            return False
        tb = (min(p[0] for p in tri), min(p[1] for p in tri), max(p[0] for p in tri), max(p[1] for p in tri))
        return not any(self._boxes_touch(tb, b, 0.3) or self._seg_box(s, e, b, 0.3) for b in self.boxes)

    def datum(self, at, direction, letter, size=2.5, leader=7.0):
        """ISO 5459 datum feature symbol: a filled triangle on the feature, a leader and the framed letter."""
        tri, (s, e), box = self._datum_parts(at, direction, size, leader)
        self.polyline(tri, w=0.1, close=True, fill=BLACK)
        self.line(s, e, W_THIN)
        b = box[2] - box[0]
        self.rect(box[0], box[1], b, b, W_THIN)
        self.text(box[0] + b / 2, box[1] + b / 2, letter, size, "center", valign="mid", bold=True)

    def tag(self, c, r, label, direction=(1, 1), size=H_TEXT, leader=5.0):
        """A hole tag: a thin leader from the hole's edge to the label, which goes where it touches no other text
        and no part outline (the preferred direction first, then the others, then longer leaders)."""
        def place(d, lead):
            dx, dy = d
            L = math.hypot(dx, dy)
            dx, dy = dx / L, dy / L
            p0 = (c[0] + dx * r, c[1] + dy * r)
            p1 = (c[0] + dx * (r + lead), c[1] + dy * (r + lead))
            if dx >= 0:
                tx, ty, an = p1[0] + 0.5, p1[1] + (0.4 if dy >= 0 else -size - 0.4), "left"
            else:
                tx, ty, an = p1[0] - 0.5, p1[1] + (0.4 if dy >= 0 else -size - 0.4), "right"
            return p0, p1, (tx, ty, an), self.text_box(tx, ty, label, size, an, bold=True)
        dirs = [direction, (direction[0], -direction[1]), (-direction[0], direction[1]), (-direction[0], -direction[1]),
                (1, 0.2), (-1, 0.2), (1, -0.2), (-1, -0.2), (0.25, 1), (0.25, -1)]
        choice = None
        for lead in (leader, leader + 3, leader + 7, leader + 12, leader + 18):
            for d in dirs:
                p0, p1, t, box = place(d, lead)
                lead_box = (min(p0[0], p1[0]), min(p0[1], p1[1]), max(p0[0], p1[0]), max(p0[1], p1[1]))
                if self.is_free(box) and not any(self._boxes_touch(lead_box, b, 0.0) for b in self.boxes):
                    choice = (p0, p1, t)
                    break
            if choice:
                break
        if choice is None:
            p0, p1, t, _b = place(direction, leader)
            choice = (p0, p1, t)
        p0, p1, (tx, ty, an) = choice
        self.line(p0, p1, 0.18)
        self.text(tx, ty, label, size, an, bold=True)

    def section_arrows(self, p, q, letter, look, size=3.5):
        """A cutting-plane line (thick at the ends, ISO 128-40) from p to q with arrows showing the viewing
        direction `look` (a unit 2D vector) and the letter at each end."""
        self.line(p, q, 0.18, DASH_CTR)
        dx, dy = q[0] - p[0], q[1] - p[1]
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        for e, s in ((p, 1), (q, -1)):
            e2 = (e[0] + s * ux * 6, e[1] + s * uy * 6)
            self.line(e, e2, 0.7)
            tail = (e[0] - look[0] * 0.0, e[1] - look[1] * 0.0)
            tip = (e[0] + look[0] * 7, e[1] + look[1] * 7)
            self.line(tail, tip, W_THIN)
            self.arrow(tip, look, 3.0, 1.1)
            self.text(tip[0] + look[0] * 1.5 - s * ux * 2.5, tip[1] + look[1] * 1.5 + (1.0 if look[1] >= 0 else -4.0),
                      letter, size, "center", bold=True)

    def first_angle_symbol(self, x, y, h=6.0):
        """ISO 5456-2 first-angle symbol: a truncated cone's side view (left) and its end view (right)."""
        d1, d2, L = h, h / 2, h * 1.2
        # side view: trapezoid, the large end on the right
        cx = x + L / 2
        self.polyline([(x, y + h / 2 - d2 / 2), (x + L, y), (x + L, y + h), (x, y + h / 2 + d2 / 2)], W_THIN,
                      close=True)
        self.centre_line((x - 1.5, y + h / 2), (x + L + 1.5, y + h / 2))
        ex = x + L + 4.0 + d1 / 2
        self.circle((ex, y + h / 2), d1 / 2, W_THIN)
        self.circle((ex, y + h / 2), d2 / 2, W_THIN)
        self.centre_line((ex - d1 / 2 - 1.5, y + h / 2), (ex + d1 / 2 + 1.5, y + h / 2))
        self.centre_line((ex, y - 1.5), (ex, y + h + 1.5))
        return ex + d1 / 2 - x

    # ------------------------------------------------------------ frame and table helpers
    def border(self, margin_left=20.0, margin=10.0):
        W, H = self.W, self.H
        self.rect(margin_left, margin, W - margin_left - margin, H - 2 * margin, 0.7)
        # centring marks
        for x, y, x2, y2 in ((W / 2, margin, W / 2, 0), (W / 2, H - margin, W / 2, H), (margin_left, H / 2, 0, H / 2),
                             (W - margin, H / 2, W, H / 2)):
            self.line((x, y), (x2, y2), 0.7)
        # grid reference letters and numbers (ISO 5457): an even number of fields each way, about 50 mm long
        nx = max(2, 2 * int(round((W - margin_left - margin) / 100.0)))
        ny = max(2, 2 * int(round((H - 2 * margin) / 100.0)))
        fx = (W - margin_left - margin) / nx
        fy = (H - 2 * margin) / ny
        for i in range(nx):
            cx = margin_left + (i + 0.5) * fx
            self.text(cx, H - margin + 1.2, str(i + 1), 3.0, "center")
            self.text(cx, margin - 4.2, str(i + 1), 3.0, "center")
            if i:
                xx = margin_left + i * fx
                self.line((xx, H - margin), (xx, H - margin + 5), W_THIN)
                self.line((xx, margin), (xx, margin - 5), W_THIN)
        letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"
        for j in range(ny):
            cy = H - margin - (j + 0.5) * fy
            self.text(margin_left - 2.5, cy, letters[j], 3.0, "center", valign="mid")
            self.text(W - margin + 2.5, cy, letters[j], 3.0, "center", valign="mid")
            if j:
                yy = H - margin - j * fy
                self.line((margin_left, yy), (margin_left - 5, yy), W_THIN)
                self.line((W - margin, yy), (W - margin + 5, yy), W_THIN)
        self.rect(margin_left - 5, margin - 5, W - margin_left - margin + 10, H - 2 * margin + 10, W_THIN)

    def table_height(self, cols, rows, size=H_TEXT, row_h=None, head_size=None, title=None, title_size=None):
        """The height table() would draw, without drawing (same wrapping)."""
        head_size = head_size or size
        title_size = title_size or size
        row_h = max(row_h or 0.0, size * 2.6)
        lead = size * 1.65
        total_w = sum(c[1] for c in cols)
        hgt = 0.0
        if title:
            lines = title if isinstance(title, (list, tuple)) else [title]
            n = sum(len(self.wrap(ln, title_size, total_w - 3.0, bold=(i == 0))) for i, ln in enumerate(lines))
            hgt += n * title_size * 1.65 + 2.2
        hl = [self.wrap(h, head_size, w - 1.6, bold=True) for h, w, al in cols]
        hgt += max(row_h, max(len(x_) for x_ in hl) * head_size * 1.6 + (row_h - head_size * 1.6))
        for r in rows:
            nlines = max([1] + [len(self.wrap(str(v), size, w - 2.0)) for (h, w, al), v in zip(cols, r)
                                if v not in (None, "")])
            hgt += row_h + (nlines - 1) * lead
        return hgt

    def table(self, x, y_top, cols, rows, size=H_TEXT, row_h=None, head_size=None, title=None, title_size=None):
        """A ruled table from its top-left corner down. cols: [(header, width mm, align)]; rows: lists of cell
        strings, wrapped to their column (never cut). Sizes are letter heights. Returns the y of its bottom."""
        head_size = head_size or size
        title_size = title_size or size
        row_h = max(row_h or 0.0, size * 2.6)
        lead = size * 1.65
        y = y_top
        total_w = sum(c[1] for c in cols)
        th = 0.0
        if title:
            lines = title if isinstance(title, (list, tuple)) else [title]
            wrapped = []
            for i, ln in enumerate(lines):
                for part in self.wrap(ln, title_size, total_w - 3.0, bold=(i == 0)):
                    wrapped.append((part, i == 0))
            th = len(wrapped) * title_size * 1.65 + 2.2
            self.rect(x, y - th, total_w, th, W_THIN)
            ty = y - 1.2 - title_size
            for ln, bold in wrapped:
                self.text(x + 1.5, ty, ln, title_size, bold=bold)
                ty -= title_size * 1.65
            y -= th
        # header (may wrap)
        hl = [self.wrap(h, head_size, w - 1.6, bold=True) for h, w, al in cols]
        hh = max(row_h, max(len(x_) for x_ in hl) * head_size * 1.6 + (row_h - head_size * 1.6))
        self.rect(x, y - hh, total_w, hh, W_THIN)
        cx = x
        for (h, w, al), ls in zip(cols, hl):
            y0 = y - hh / 2 + (len(ls) - 1) * head_size * 0.8
            for k, ln in enumerate(ls):
                self.text(cx + w / 2, y0 - k * head_size * 1.6, ln, head_size, "center", valign="mid", bold=True)
            cx += w
        y -= hh
        for r in rows:
            cells = []
            nlines = 1
            for (h, w, al), v in zip(cols, r):
                ls = self.wrap(str(v), size, w - 2.0) if v not in (None, "") else [""]
                cells.append(ls)
                nlines = max(nlines, len(ls))
            hgt = row_h + (nlines - 1) * lead
            self.rect(x, y - hgt, total_w, hgt, W_THIN)
            cx = x
            for (h, w, al), ls in zip(cols, cells):
                for k, ln in enumerate(ls):
                    yy = y - row_h / 2 - k * lead
                    if al == "c":
                        self.text(cx + w / 2, yy, ln, size, "center", valign="mid")
                    elif al == "r":
                        self.text(cx + w - 1.0, yy, ln, size, "right", valign="mid")
                    else:
                        self.text(cx + 1.0, yy, ln, size, "left", valign="mid")
                cx += w
            y -= hgt
        cx = x
        top = y_top - th
        for h, w, al in cols[:-1]:
            cx += w
            self.line((cx, top), (cx, y), W_THIN)
        return y

    def save(self, path):
        self.flush()
        self.doc.subset_fonts()
        self.doc.set_metadata(self.meta)
        if getattr(self, "data", None) is not None:
            import json
            txt = json.dumps(self.data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
            esc = txt.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            self.doc.xref_set_key(self.doc.pdf_catalog(), "DrawgenData", "(%s)" % esc)
        self.doc.save(path, garbage=4, deflate=True, no_new_id=True)
        self.doc.close()
