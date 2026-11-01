"""Render each ceiling drawing's notes and title data as PNG images (offline).

    python3 v2/02-Drawings/ceiling/render_notes.py

Fusion's drawing API can't put text on a sheet (custom table cells come out
blank, title block fields can't be set), but it can insert a raster image
(Sheet.images). So the notes, the title data and each view's scale label (a view drawn
at another scale than the sheet's) are drawn here, at 10 px per mm, and
make_drawing_ceiling.py inserts them at that size (Fusion's own size for an image is
fixed, so it scales each one: drawing_specs.FUSION_IMG_W). Lettering 2.5 mm, labels
3.5 mm (ISO 3098 heights), Arial Unicode for the Vietnamese names.
Output: v2/02-Drawings/ceiling/.notes/ (git-ignored; regenerate any time).
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import drawing_specs as S  # noqa: E402

PX_MM = S.PX_MM
FONT_PATHS = ["/Library/Fonts/Arial Unicode.ttf", "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"]
OUT = os.path.join(HERE, ".notes")


def font(h_mm):
    for p in FONT_PATHS:
        if os.path.exists(p):
            return ImageFont.truetype(p, int(round(h_mm * PX_MM / 0.72)))
    raise FileNotFoundError("no Arial Unicode font found")


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, s, f, width_px):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_w(draw, t, f) <= width_px:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def render_notes(sp, path):
    W = int(S.IMG_W * PX_MM)
    f, fb = font(2.5), font(3.0)
    pad = int(2 * PX_MM)
    scratch = ImageDraw.Draw(Image.new("L", (10, 10)))
    rows = [("NOTES", fb, None)]
    for i, n in enumerate(sp["notes"]):
        for j, line in enumerate(wrap(scratch, n, f, W - 2 * pad - int(6 * PX_MM))):
            rows.append((line, f, "%d." % (i + 1) if j == 0 else ""))
    lh = int(4.2 * PX_MM)
    H = pad * 2 + lh * len(rows)
    img = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W - 1, H - 1], outline=0, width=3)
    y = pad
    for text, ff, num in rows:
        if num is None:
            d.text((pad, y), text, font=ff, fill=0)
        else:
            d.text((pad, y), num, font=ff, fill=0)
            d.text((pad + int(6 * PX_MM), y), text, font=ff, fill=0)
        y += lh
    img.save(path, dpi=(PX_MM * 25.4, PX_MM * 25.4))
    return img.size


def render_title(sp, path):
    W = int(S.IMG_W * PX_MM)
    f, fb = font(2.5), font(3.0)
    lh = int(6.5 * PX_MM)
    col = int(38 * PX_MM)
    rows = sp["title"]
    H = lh * (len(rows) + 1) + 6
    img = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W - 1, H - 1], outline=0, width=4)
    d.text((int(2 * PX_MM), int(1 * PX_MM)), "TITLE DATA (the title block fields can't be set by script)", font=f, fill=0)
    y = lh
    for label, value in rows:
        d.line([0, y, W, y], fill=0, width=2)
        d.text((int(2 * PX_MM), y + int(1.6 * PX_MM)), label, font=f, fill=0)
        ff = fb if label in ("PART NO.", "NAME") else f
        d.text((col + int(2 * PX_MM), y + int(1.2 * PX_MM if ff is fb else 1.6 * PX_MM)), str(value), font=ff, fill=0)
        y += lh
    d.line([col, lh, col, H], fill=0, width=2)
    img.save(path, dpi=(PX_MM * 25.4, PX_MM * 25.4))
    return img.size


def render_label(text, path):
    """A view's label (its scale), 3.5 mm lettering, no frame."""
    f = font(3.5)
    scratch = ImageDraw.Draw(Image.new("L", (10, 10)))
    pad = int(1 * PX_MM)
    left, top, right, bottom = scratch.textbbox((0, 0), text, font=f)   # the glyphs' own box (the first label's
    W, H = (right - left) + 2 * pad, (bottom - top) + 2 * pad            # fixed height cut its foot off)
    img = Image.new("L", (W, H), 255)
    ImageDraw.Draw(img).text((pad - left, pad - top), text, font=f, fill=0)
    img.save(path, dpi=(PX_MM * 25.4, PX_MM * 25.4))
    return img.size


def render_symbol(path):
    """The ISO first-angle symbol (truncated cone: side view narrow end left, end view right), 24 x 10 mm with
    S.SYMBOL_PX_MARGIN all round, 0.35 mm lines."""
    m, lw = S.SYMBOL_PX_MARGIN, 0.35
    W, H = int(round((24.0 + 2 * m) * PX_MM)), int(round((10.0 + 2 * m) * PX_MM))
    img = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(img)

    def p(x, y):           # symbol mm (origin: the outline's narrow end's middle at x 0, y 0) -> pixels, y down
        return ((x + m) * PX_MM, (H / PX_MM - (y + 5.0 + m)) * PX_MM)
    w = max(1, int(round(lw * PX_MM)))
    outline = [p(0, -2.5), p(10, -5), p(10, 5), p(0, 2.5), p(0, -2.5)]
    d.line(outline, fill=0, width=w, joint="curve")
    for r in (5.0, 2.5):
        cx, cy = p(19.0, 0.0)
        d.ellipse([cx - r * PX_MM, cy - r * PX_MM, cx + r * PX_MM, cy + r * PX_MM], outline=0, width=w)
    img.save(path, dpi=(PX_MM * 25.4, PX_MM * 25.4))
    return img.size


def main():
    os.makedirs(OUT, exist_ok=True)
    sy = render_symbol(os.path.join(OUT, "FIRST_ANGLE_SYMBOL.png"))
    print("first-angle symbol picture %s px (%.0f x %.0f mm)" % (sy, sy[0] / PX_MM, sy[1] / PX_MM))
    for key in S.ORDER:
        sp = S.SPECS[key]
        n = render_notes(sp, os.path.join(OUT, sp["drawing"] + "_NOTES.png"))
        t = render_title(sp, os.path.join(OUT, sp["drawing"] + "_TITLE.png"))
        print("%-45s notes %s px (%.0f x %.0f mm), title %s px (%.0f x %.0f mm)" % (
            sp["drawing"], n, n[0] / PX_MM, n[1] / PX_MM, t, t[0] / PX_MM, t[1] / PX_MM))
        for view, text in S.labels(sp).items():
            lb = render_label(text, os.path.join(OUT, "%s_LABEL_%s.png" % (sp["drawing"], view.upper())))
            print("%-45s label %s view %r: %s px (%.0f x %.0f mm)" % ("", view, text, lb, lb[0] / PX_MM, lb[1] / PX_MM))


if __name__ == "__main__":
    main()
