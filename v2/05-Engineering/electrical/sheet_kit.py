"""Shared sheet helpers for ELECTRICAL's generated drawings (wiring diagram, assembly sheets), drawn with PyMuPDF.

Letter sizes are capital heights (ISO 3098), the way the reviewers measure them (font size x 0.716, the
PM's ruling on #235's review): 2.5 mm for every text on a sheet, 3.5 mm for sheet and view titles, 1.8 mm
only for the labels of the title block (ISO 7200, the PM's ruling). The guideline says not to shrink a font to
fit a page (section 6), so text that is too long wraps to its width, a table wraps its cells (it never cuts a
value short), and a sheet that can't hold its content raises an error instead of drawing over itself.

Every text drawn is recorded with its ink box (capital top to descender, its measured width), and check()
fails on any two texts that overlap or any text outside the frame, so a sheet is checked before it's saved.
The offline test reads the saved PDFs back and checks the same rules independently.
"""

import fitz  # PyMuPDF

MMPT = 72.0 / 25.4
CAP = 0.716                      # capital height / font size: the reviewers' figure (PM ruling on #235's review, 2026-11-01)
DESC = 0.21                      # Helvetica's descender / font size (p, g, y), for the ink box
BODY, TITLE, LABEL = 2.5, 3.5, 1.8   # capital heights, mm
PITCH = 1.7                      # baseline to baseline, in capital heights
SIZES = {"A1": (841.0, 594.0), "A2": (594.0, 420.0), "A3": (420.0, 297.0)}
TB_W, TB_ROW = 185.0, 6.4        # title block width and row pitch, mm
TB_H = 8 * TB_ROW                # 8 rows

INK = (0.1, 0.1, 0.1)
MAINS = (0.75, 0.1, 0.1)         # mains in red
SELV = (0.05, 0.25, 0.6)         # Class 2 12 V in blue
SIG = (0.2, 0.45, 0.2)           # signals and data in green
GREY = (0.45, 0.45, 0.45)        # text in grey stays dark enough to print
LIGHT = (0.92, 0.92, 0.92)


def font_size(h):
    """Font size (mm) for a capital height h (mm)."""
    return h / CAP


def text_width(s, h, bold=False):
    """Width (mm) of a text at capital height h."""
    return fitz.get_text_length(s, fontname="hebo" if bold else "helv", fontsize=font_size(h))


def _pieces(word):
    """A word too long for its line breaks after _ - / , (a file name), never inside a part number."""
    out, cur = [], ""
    for ch in word:
        cur += ch
        if ch in "_-/,":
            out.append(cur)
            cur = ""
    if cur:
        out.append(cur)
    return out


def wrap(s, width, h=BODY, bold=False, indent="   "):
    """The lines of `s` that fit `width` mm at capital height h; follow-on lines are indented."""
    if text_width(s, h, bold) <= width:
        return [s]
    lines, cur = [], ""
    for wd in s.split(" "):
        trial = (cur + " " + wd) if cur.strip() else (cur + wd)
        if text_width(trial, h, bold) <= width:
            cur = trial
            continue
        if cur.strip():                                  # close the line; the word starts the next one
            lines.append(cur)
            cur = indent + wd
            if text_width(cur, h, bold) <= width:
                continue
        else:
            cur = trial
        parts, cur = _pieces(cur), ""                    # the word alone is too long: break it after _ - / ,
        for pc in parts:
            if cur.strip() and text_width(cur + pc, h, bold) > width:
                lines.append(cur)
                cur = indent + pc
            else:
                cur += pc
        if text_width(cur, h, bold) > width:
            raise ValueError("can't wrap %r into %.1f mm" % (cur, width))
    if cur.strip():
        lines.append(cur)
    return lines


class Sheet:
    """One page. Content coordinates are in mm from the top left, times `zoom` (a schematic laid out for A3 drawn
    at twice the size on A1 keeps its overview and doubles every letter). The frame, title block and notes are
    drawn in page mm, never zoomed."""

    def __init__(self, doc, size="A3", zoom=1.0):
        self.W, self.H = SIZES[size]
        self.size, self.zoom = size, zoom
        self.p = doc.new_page(width=self.W * MMPT, height=self.H * MMPT)
        self.inks = []               # (x0, y0, x1, y1, text) in page mm
        self.segs = []               # drawn line segments (x0, y0, x1, y1) in page mm, for the text-on-line check
        self.content_bottom = self.H - 10.0

    # ---- primitives (content coordinates, zoomed)
    def pt(self, x, y):
        return fitz.Point(x * self.zoom * MMPT, y * self.zoom * MMPT)

    def line(self, x0, y0, x1, y1, color=INK, w=0.25, dashes=None):
        self.p.draw_line(self.pt(x0, y0), self.pt(x1, y1), color=color, width=w * self.zoom * MMPT, dashes=dashes)
        z = self.zoom
        self.segs.append((x0 * z, y0 * z, x1 * z, y1 * z))

    def poly(self, pts, color=INK, w=0.35):
        for (a, b), (c, d) in zip(pts, pts[1:]):
            self.line(a, b, c, d, color, w)

    def rect(self, x0, y0, x1, y1, color=INK, w=0.25, fill=None, dashes=None):
        z = self.zoom * MMPT
        self.p.draw_rect(fitz.Rect(x0 * z, y0 * z, x1 * z, y1 * z), color=color, fill=fill, width=w * self.zoom * MMPT,
                         dashes=dashes)
        z = self.zoom
        self.segs += [(x0 * z, y0 * z, x1 * z, y0 * z), (x1 * z, y0 * z, x1 * z, y1 * z),
                      (x1 * z, y1 * z, x0 * z, y1 * z), (x0 * z, y1 * z, x0 * z, y0 * z)]

    def circle(self, x, y, r, color=INK, w=0.25):
        self.p.draw_circle(self.pt(x, y), r * self.zoom * MMPT, color=color, width=w * self.zoom * MMPT)

    def text(self, x, y, s, h=BODY, color=INK, bold=False):
        """Text with its baseline at content (x, y); h is its capital height on paper, at least BODY."""
        self.page_text(x * self.zoom, y * self.zoom, s, max(h, BODY), color, bold)

    def text_w(self, s, h=BODY, bold=False):
        """Width in content units of a text at capital height h on paper."""
        return text_width(s, max(h, BODY), bold) / self.zoom

    def line_pitch(self, h=BODY):
        """Baseline to baseline in content units."""
        return max(h, BODY) * PITCH / self.zoom

    def para(self, x, y, s, width, h=BODY, color=INK, bold=False):
        """Wrapped text from baseline (x, y), `width` content units wide; returns the next baseline."""
        for ln in wrap(s, width * self.zoom, max(h, BODY), bold):
            self.text(x, y, ln, h, color, bold)
            y += self.line_pitch(h)
        return y

    # ---- labels placed clear of what's drawn
    AROUND = [(dx, dy) for dy in (0, -1.5, 1.5, -3, 3, -4.5, 4.5, -6, 6, -8, 8)
              for dx in (0, 3, -3, 6, -6, 10, -10, 16, -16, 24, -24)]

    def _ink(self, x, y, s, h, bold):
        hh, z = max(h, BODY), self.zoom
        fs = font_size(hh)
        return (x * z, y * z - CAP * fs, x * z + text_width(s, hh, bold), y * z + DESC * fs, s)

    def _free(self, b, gap=0.5):
        if b[0] < 10 or b[1] < 10 or b[2] > self.W - 10 or b[3] > self.content_bottom:
            return False
        g = (b[0] - gap, b[1] - gap, b[2] + gap, b[3] + gap, b[4])
        if any(g[0] < a[2] and a[0] < g[2] and g[1] < a[3] and a[1] < g[3] for a in self.inks):
            return False
        return not any(crosses(sg, g, 0.0) for sg in self.segs)

    def label(self, x, y, lines, h=BODY, color=INK, bold=False, around=None):
        """A label of one or more lines with its first baseline at content (x, y), moved to the nearest spot where
        it overlaps no text and no drawn line runs through it (draw the lines first). Raises if there is none."""
        lines = [lines] if isinstance(lines, str) else list(lines)
        pitch = self.line_pitch(h)
        for dx, dy in (around or self.AROUND):
            boxes = [self._ink(x + dx, y + dy + i * pitch, ln, h, bold) for i, ln in enumerate(lines)]
            if all(self._free(bx) for bx in boxes):
                for i, ln in enumerate(lines):
                    self.text(x + dx, y + dy + i * pitch, ln, h, color, bold)
                return x + dx, y + dy
        raise ValueError("no clear place near (%.1f, %.1f) for the label %r" % (x, y, lines[0]))

    def first_angle_symbol(self, x, y, label=True):
        """ISO 5456-2 first-angle symbol in page mm, its left end at x, its axis at y: the truncated cone's side view
        (small end 5, large end 10, 10 long) and its end view (circles of 10 and 5), 4 apart; 'ISO first angle'
        under it. It must land clear of every text and line drawn so far (it raises otherwise)."""
        x0, y0, x1, y1 = x - 0.5, y - 5.5, x + 30.5, y + 5.5 + (BODY * PITCH + 1.0 if label else 0)
        box = (x0, y0, x1, y1, "first-angle symbol")
        if any(x0 < a[2] and a[0] < x1 and y0 < a[3] and a[1] < y1 for a in self.inks) or \
                any(crosses(sg, box, 0.0) for sg in self.segs) or y1 > self.content_bottom or x1 > self.W - 10:
            raise ValueError("no room for the first-angle symbol at (%.0f, %.0f)" % (x, y))
        pts = [(x, y - 2.5), (x + 10, y - 5), (x + 10, y + 5), (x, y + 2.5), (x, y - 2.5)]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            self.page_line(ax, ay, bx, by, INK, 0.35)
        cx = x + 10 + 4 + 5
        for r in (5.0, 2.5):
            self.p.draw_circle(fitz.Point(cx * MMPT, y * MMPT), r * MMPT, color=INK, width=0.35 * MMPT)
        self.inks.append((x0, y - 5.5, x1, y + 5.5, "first-angle symbol"))    # the drawing; its label is a text of its own
        if label:
            self.page_text(x, y + 5.5 + BODY * 1.4, "ISO first angle", BODY, INK)

    # ---- page coordinates (not zoomed)
    def page_text(self, x, y, s, h, color=INK, bold=False):
        if not s:
            return
        fs = font_size(h)
        self.p.insert_text(fitz.Point(x * MMPT, y * MMPT), s, fontsize=fs * MMPT, fontname="hebo" if bold else "helv",
                           color=color)
        self.inks.append((x, y - CAP * fs, x + text_width(s, h, bold), y + DESC * fs, s))

    def page_rect(self, x0, y0, x1, y1, color=INK, w=0.35):
        self.p.draw_rect(fitz.Rect(x0 * MMPT, y0 * MMPT, x1 * MMPT, y1 * MMPT), color=color, width=w * MMPT)

    def page_line(self, x0, y0, x1, y1, color=INK, w=0.2):
        self.p.draw_line(fitz.Point(x0 * MMPT, y0 * MMPT), fitz.Point(x1 * MMPT, y1 * MMPT), color=color, width=w * MMPT)

    def frame_and_title(self, title, dwg, sheet, of, scale, date, source, notes, notes_title="NOTES"):
        """The frame, the title block (bottom right) and the notes block beside it. Returns the top of the
        notes block: content must stay above it. Notes that don't fit their block raise."""
        W, H = self.W, self.H
        self.page_rect(10, 10, W - 10, H - 10, INK, 0.5)
        x0, y0 = W - 10 - TB_W, H - 10 - TB_H
        self.page_rect(x0, y0, W - 10, H - 10, INK, 0.5)
        rows = [("PROJECT", "FocusPod v2 - Spaceship"), ("TITLE", title), ("DWG / PART NO.", dwg),
                ("REV / STATUS", "P01 / DRAFT - not for production"), ("UNITS / SCALE", "mm / %s" % scale),
                ("SHEET", "%d of %d   (%s)" % (sheet, of, self.size)), ("DATE / BY", "%s / ELECTRICAL Engineer" % date),
                ("SOURCE", source)]
        for i, (k, v) in enumerate(rows):
            top = y0 + i * TB_ROW
            base = top + TB_ROW - 1.6                    # capital tops 1.3 (title) to 2.3 mm under the row's top
            self.page_text(x0 + 2, base, k, LABEL, GREY, True)
            vh = TITLE if k == "TITLE" else BODY
            if text_width(v, vh, k == "TITLE") > TB_W - 42:
                raise ValueError("title block %s too long: %r" % (k, v))
            self.page_text(x0 + 40, base, v, vh, INK, k == "TITLE")
            if i:
                self.page_line(x0, top, W - 10, top, GREY, 0.15)
        nx1 = x0 - 2
        self.page_rect(10, y0, nx1, H - 10, INK, 0.35)
        y = y0 + 1.5 + BODY * 1.4
        self.page_text(12, y, notes_title, BODY, INK, True)
        y += BODY * PITCH
        for n in notes:
            for ln in wrap(n, nx1 - 14, BODY):
                if y + DESC * font_size(BODY) > H - 11:
                    raise ValueError("the notes don't fit their block; move some to a notes sheet")
                self.page_text(12, y, ln, BODY, INK)
                y += BODY * PITCH
        self.content_bottom = y0 - 2.0
        return y0

    # ---- blocks in content coordinates
    def box(self, x0, y0, x1, title, lines=(), color=INK, h=BODY, fill=None, min_y1=None):
        """A box from (x0, y0) to x1, as tall as its wrapped title and lines (or min_y1). Returns its bottom y."""
        z, hh = self.zoom, max(h, BODY)
        pad = 1.4 / z
        width = (x1 - x0 - 2 * pad) * z                  # on paper
        rows = [(ln, True) for ln in wrap(title, width, hh, True)] + \
               [(ln, False) for t in lines for ln in wrap(t, width, hh)]
        base = y0 + pad + hh * CAP / z
        y1 = max(base + (len(rows) - 1) * self.line_pitch(h) + DESC * font_size(hh) / z + pad, min_y1 or 0)
        self.rect(x0, y0, x1, y1, color, 0.3, fill=fill)
        for i, (ln, bold) in enumerate(rows):
            self.text(x0 + pad, base + i * self.line_pitch(h), ln, h, color if bold else INK, bold)
        return y1

    def table(self, x, y, cols, rows, bottom, h=BODY, head_color=GREY):
        """Columns [(name, width)] in content units; rows of strings. Cells wrap, never cut. Draws the rows that
        fit above `bottom` and returns (next y, the rows left over for the next sheet)."""
        pad = 1.2 / self.zoom
        pitch = self.line_pitch(h)
        cap = max(h, BODY) * CAP / self.zoom
        y += cap
        cx = x
        for name, wd in cols:
            self.text(cx, y, name, h, head_color, True)
            cx += wd
        total = sum(wd for _n, wd in cols)
        y += DESC * font_size(max(h, BODY)) / self.zoom + pad
        self.line(x, y, x + total, y, GREY, 0.2)
        for i, row in enumerate(rows):
            cells = [wrap(str(v), (wd - 2 * pad) * self.zoom, max(h, BODY), indent="") for (_n, wd), v in zip(cols, row)]
            n = max(len(c) for c in cells)
            need = pad + cap + (n - 1) * pitch + DESC * font_size(max(h, BODY)) / self.zoom + pad
            if y + need > bottom:
                return y, rows[i:]
            cx = x
            for (_n, wd), lines in zip(cols, cells):
                for j, ln in enumerate(lines):
                    self.text(cx, y + pad + cap + j * pitch, ln, h)
                cx += wd
            y += need
            self.line(x, y, x + total, y, LIGHT, 0.15)
        return y, []

    def check(self):
        """Fails on two texts that overlap, a text that a drawn line runs through, or a text outside the frame."""
        bad = []
        for i, a in enumerate(self.inks):
            if a[0] < 10 or a[1] < 10 or a[2] > self.W - 10 or a[3] > self.H - 10:
                bad.append("outside the frame: %r" % a[4])
            for sg in self.segs:
                if crosses(sg, a):
                    bad.append("a line runs through %r" % a[4])
                    break
            for b in self.inks[i + 1:]:
                if a[0] < b[2] - 0.05 and b[0] < a[2] - 0.05 and a[1] < b[3] - 0.05 and b[1] < a[3] - 0.05:
                    bad.append("%r overlaps %r" % (a[4], b[4]))
        if bad:
            raise ValueError("sheet check: " + "; ".join(bad[:8]) + (" (+%d more)" % (len(bad) - 8) if len(bad) > 8 else ""))
        return True


def crosses(seg, box, tol=0.1):
    """True when the segment passes through the box shrunk by tol (Liang-Barsky clipping)."""
    x0, y0, x1, y1 = seg
    bx0, by0, bx1, by1 = box[0] + tol, box[1] + tol, box[2] - tol, box[3] - tol
    if bx0 >= bx1 or by0 >= by1:
        return False
    dx, dy = x1 - x0, y1 - y0
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x0 - bx0), (dx, bx1 - x0), (-dy, y0 - by0), (dy, by1 - y0)):
        if p == 0:
            if q < 0:
                return False
        else:
            r = q / p
            if p < 0:
                t0 = max(t0, r)
            else:
                t1 = min(t1, r)
            if t0 > t1:
                return False
    return True


def ink_boxes(page):
    """Every text span on a saved PDF page as (x0, y0, x1, y1, capital height mm, text) in page mm, ink box from
    the capital top to the descender: the offline test's independent reading."""
    out = []
    for blk in page.get_text("dict")["blocks"]:
        for ln in blk.get("lines", []):
            for sp in ln["spans"]:
                t = sp["text"]
                if not t.strip():
                    continue
                fs = sp["size"] / MMPT
                ox, oy = sp["origin"][0] / MMPT, sp["origin"][1] / MMPT
                out.append((ox, oy - CAP * fs, sp["bbox"][2] / MMPT, oy + DESC * fs, CAP * fs, t))
    return out


def overlaps(boxes, tol=0.05):
    """Pairs of ink boxes that overlap."""
    bad = []
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            if a[0] < b[2] - tol and b[0] < a[2] - tol and a[1] < b[3] - tol and b[1] < a[3] - tol:
                bad.append((a[5], b[5]))
    return bad
