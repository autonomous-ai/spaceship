#!/usr/bin/env python3
"""Put a block of notes on a drawing sheet, as an image rendered from text.

    python3 tools/fusion/sheet_notes.py DRAWING_NAME NOTES.txt --sheet 1 --x 600 --y 250 --width 200

Fusion's drawing API can't write text on a sheet (no text in sheet sketches,
custom table cells stay blank), but it can insert an image
(Sheet.images.insert). So (PM ruling 2026-10-31, from the WALL Engineer's
find):

1. the note's SOURCE TEXT lives in the repo next to its drawing, so it stays
   searchable and editable (plain text; a blank line starts a new paragraph,
   a line starting with "# " is a heading);
2. this renders it to a PNG at 300 dpi in Arial Unicode (Vietnamese names
   render), at an ISO text height (--text-mm, default 2.5 mm capitals) and
   exactly --width mm wide;
3. under the Fusion lock it opens the drawing, inserts the image on --sheet
   with its LOWER-LEFT corner at (--x, --y) sheet mm, scaled to --width mm,
   saves a new version and closes the drawing (if this command opened it).

Exit 0 = inserted and saved, 1 = failed (nothing saved), 2 = Fusion not
reachable, 3 = the lock was busy. --render-only writes the PNG and stops.
Images can't be moved or deleted by the API, so place notes once, on a sheet
whose layout is settled; to change a note, make the sheet again.
"""

import argparse
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_script as rs  # noqa: E402

FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
DPI = 300
PT_PER_MM = 72.0 / 25.4
CAP_RATIO = 0.716            # Arial capital height / font size (ISO 3098 text height = capitals)

# Measured on Mac 1, Fusion 2706.1.17, 2026-10-31 (MEASURED below): how
# Images.insert maps a PNG onto the sheet. Filled in from the live test.
MM_PER_PX_AT_SCALE_1 = None   # sheet mm per image pixel at scale 1.0
ANCHOR = None                 # which point of the image `position` sets

INSERT_SCRIPT = '''import adsk.core, adsk.drawing
A = %(args)r
def run(_c):
    app = adsk.core.Application.get()
    doc = adsk.drawing.DrawingDocument.cast(app.activeDocument)
    if doc is None or doc.name != A["name"]:
        raise RuntimeError("the active document is not the drawing %%r" %% A["name"])
    dwg = doc.drawing
    if not 1 <= A["sheet"] <= dwg.sheets.count:
        raise RuntimeError("the drawing has %%d sheet(s), not %%d" %% (dwg.sheets.count, A["sheet"]))
    sh = dwg.sheets.item(A["sheet"] - 1)
    ii = sh.images.createInput()
    ii.imageFilePath = A["png"]
    ii.position = adsk.core.Point2D.create(A["px"], A["py"])
    ii.scale = A["scale"]
    if not sh.images.insert(ii):
        raise RuntimeError("Images.insert returned False")
    print("inserted %%s on sheet %%d (%%s) at %%s, scale %%.5f" %% (A["label"], A["sheet"], sh.name,
                                                                     (A["px"], A["py"]), A["scale"]))
'''


def paragraphs(text):
    out, cur = [], []
    for line in text.splitlines():
        if not line.strip():
            if cur:
                out.append(" ".join(cur))
                cur = []
            continue
        if line.startswith("# "):
            if cur:
                out.append(" ".join(cur))
                cur = []
            out.append(("H", line[2:].strip()))
            continue
        cur.append(line.strip())
    if cur:
        out.append(" ".join(cur))
    return out


def render(text, width_mm, text_mm, png_path):
    """Render the notes to a PNG exactly width_mm wide; returns (png, w_px, h_px, h_mm)."""
    import fitz
    size = text_mm / CAP_RATIO * PT_PER_MM          # font size in points
    w_pt = width_mm * PT_PER_MM
    pad = 1.5 * PT_PER_MM
    blocks = paragraphs(text)

    def lay(page):
        y = pad
        for b in blocks:
            head = isinstance(b, tuple)
            s = b[1] if head else b
            fs = size * (1.25 if head else 1.0)
            r = fitz.Rect(pad, y, w_pt - pad, 10 ** 5)
            left = page.insert_textbox(r, s, fontsize=fs, fontname="AU", fontfile=FONT)
            used = (10 ** 5 - y) - left
            y += used + size * 0.6
        return y + pad

    probe = fitz.open()
    h_pt = lay(probe.new_page(width=w_pt, height=10 ** 5 + 10))
    probe.close()
    doc = fitz.open()
    page = doc.new_page(width=w_pt, height=h_pt)
    lay(page)
    pix = page.get_pixmap(dpi=DPI)
    pix.set_dpi(DPI, DPI)
    pix.save(png_path)
    w_px, h_px = pix.width, pix.height
    doc.close()
    return png_path, w_px, h_px, h_pt / PT_PER_MM


def placement(x, y, width_mm, w_px, h_px):
    """(position x, position y, scale) for Images.insert, from the measured mapping,
    so that the image's lower-left corner lands at (x, y) and it is width_mm wide."""
    if MM_PER_PX_AT_SCALE_1 is None or ANCHOR is None:
        raise RuntimeError("Images.insert's mapping hasn't been measured yet")
    scale = width_mm / (w_px * MM_PER_PX_AT_SCALE_1)
    w, h = width_mm, h_px * MM_PER_PX_AT_SCALE_1 * scale
    dx, dy = {"lower-left": (0, 0), "upper-left": (0, h), "center": (w / 2, h / 2)}[ANCHOR]
    return x + dx, y + dy, scale


def main(argv=None):
    ap = argparse.ArgumentParser(description="Put a block of notes on a drawing sheet, "
                                             "as an image rendered from text.")
    ap.add_argument("drawing")
    ap.add_argument("notes", help="the note's source text, kept in the repo next to its drawing")
    ap.add_argument("--sheet", type=int, default=1)
    ap.add_argument("--x", type=float, required=True, help="lower-left corner, sheet mm")
    ap.add_argument("--y", type=float, required=True, help="lower-left corner, sheet mm")
    ap.add_argument("--width", type=float, required=True, help="width on the sheet, mm")
    ap.add_argument("--text-mm", type=float, default=2.5, help="capital height, mm (ISO 3098)")
    ap.add_argument("--render-only", metavar="PNG", help="write the PNG here and stop")
    ap.add_argument("--folder", default=rs.DEFAULT_FOLDER)
    ap.add_argument("--url", default=rs.DEFAULT_URL)
    ap.add_argument("--timeout", type=float, default=300.0)
    ap.add_argument("--lock", default=None)
    ap.add_argument("--lock-wait", type=float, default=1200.0)
    ap.add_argument("--label", default=os.environ.get(rs.LABEL_ENV, ""))
    opts = ap.parse_args(argv)

    with open(opts.notes, encoding="utf-8") as fh:
        text = fh.read()
    png = opts.render_only or os.path.join(tempfile.mkdtemp(prefix="sheet-notes-"), "notes.png")
    png, w_px, h_px, h_mm = render(text, opts.width, opts.text_mm, png)
    print("sheet_notes: rendered %s: %d x %d px, %.1f x %.1f mm" % (
        os.path.basename(opts.notes), w_px, h_px, opts.width, h_mm))
    if opts.render_only:
        return 0
    px, py, scale = placement(opts.x, opts.y, opts.width, w_px, h_px)

    lock = rs.FusionLock(opts.lock or rs.default_lock_path(opts.url),
                         label=opts.label or "sheet_notes", hold_s=3 * opts.timeout + 300,
                         script="sheet_notes.py %s %s" % (opts.drawing, os.path.basename(opts.notes)))
    try:
        lock.acquire(opts.lock_wait, token=os.environ.get(rs.TOKEN_ENV) or None)   # also inside a held lock
    except (rs.LockTimeout, KeyboardInterrupt) as e:
        print("sheet_notes: %s" % (e or "stopped while waiting"), file=sys.stderr)
        return 3
    try:
        mcp = rs.FusionMcp(opts.url, opts.timeout)
        mcp.initialize()
        ok, out = rs.run_in_fusion(mcp, rs.doc_script("open", opts.drawing, opts.folder))
        if not ok:
            print("sheet_notes: couldn't open %s: %s" % (opts.drawing, out), file=sys.stderr)
            return 1
        opened_here = any(line.startswith("run_script: opened") for line in (out or "").splitlines())   # the runner may warn first
        ok, out = rs.run_in_fusion(mcp, INSERT_SCRIPT % {"args": {
            "name": opts.drawing, "sheet": opts.sheet, "png": png, "px": px, "py": py,
            "scale": scale, "label": os.path.basename(opts.notes)}})
        print("sheet_notes: %s" % (out or "").strip())
        if not ok:
            return 1
        ok, out = rs.run_in_fusion(mcp, rs.doc_script(
            "save", opts.drawing, opts.folder,
            description="notes %s" % os.path.basename(opts.notes)))
        print("sheet_notes: %s" % (out or "").strip())
        if ok and opened_here:
            rs.run_in_fusion(mcp, rs.doc_script("close", opts.drawing, opts.folder))
        return 0 if ok else 1
    except rs.McpError as e:
        print("sheet_notes: %s" % e, file=sys.stderr)
        return 2
    finally:
        lock.release()


if __name__ == "__main__":
    sys.exit(main())
