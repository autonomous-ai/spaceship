#!/usr/bin/env python3
"""Export a Fusion drawing for the repo: PDF without the account name, plus PNGs.

    python3 tools/fusion/export_drawing.py DRAWING_NAME OUT_DIR [--sheets 1-2] [--dpi 110]

One shared step for every drawing, under the Fusion lock:

1. open DRAWING_NAME from --folder (or activate it), export its PDF to a
   private temporary folder (outside the repo), and close it again if this
   command opened it;
2. remove the "Created by" value that Fusion prints from the account
   (pdf_clear_field.py: the text is removed, not covered);
3. check the PDF: no word of the Fusion account's user name or display name
   may be left anywhere in its text (the names are read from Fusion and never
   printed or written to the repo);
4. write OUT_DIR/DRAWING_NAME.pdf and one PNG per page,
   OUT_DIR/DRAWING_NAME-render.png (page 1) and -render-p2.png ... to check by
   eye before review.

Exit 0 = written and clean, 1 = export or check failed (nothing written to
OUT_DIR), 2 = Fusion not reachable, 3 = the Fusion lock was busy.
Needs PyMuPDF (fitz).
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_script as rs  # noqa: E402

EXPORT_SCRIPT = '''import adsk.core, adsk.drawing, json
def run(_c):
    app = adsk.core.Application.get()
    doc = app.activeDocument
    if doc.name != %(name)r or doc.objectType != adsk.drawing.DrawingDocument.classType():
        raise RuntimeError("the active document is %%r, not the drawing %%r" %% (doc.name, %(name)r))
    dwg = adsk.drawing.DrawingDocument.cast(doc).drawing
    opts = dwg.exportManager.createPDFExportOptions(%(raw)r)
    if %(sheets)r:
        opts.sheetsToExport = adsk.drawing.PDFSheetsExport.RangePDFSheetsExport
        opts.sheetRange = %(sheets)r
    opts.openPDF = False
    opts.useLineWeights = True
    if not dwg.exportManager.execute(opts):
        raise RuntimeError("PDF export failed")
    u = app.currentUser
    with open(%(names)r, "w") as fh:       # private temp file; the CLI deletes it
        json.dump([getattr(u, "userName", "") or "", getattr(u, "displayName", "") or ""], fh)
    print("exported %%d sheet(s) of %%s" %% (dwg.sheets.count, doc.name))
'''


def account_words(path):
    with open(path) as fh:
        names = json.load(fh)
    words = set()
    for n in names:
        for w in n.replace("@", " ").replace(".", " ").replace("_", " ").split():
            if len(w) >= 2:          # checked as whole words, so short ones are safe too
                words.add(w.lower())
    return words


def check_and_render(raw_pdf, words, out_dir, name, dpi):
    import fitz  # PyMuPDF
    clean = os.path.join(os.path.dirname(raw_pdf), "clean.pdf")
    p = subprocess.run([sys.executable, os.path.join(HERE, "pdf_clear_field.py"), raw_pdf, clean],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("pdf_clear_field failed: %s" % (p.stderr or p.stdout).strip()[:300])
    doc = fitz.open(clean)
    text = " ".join(page.get_text() for page in doc).lower()
    found = sorted(w for w in words if re.search(r"(?<![a-z0-9])%s(?![a-z0-9])" % re.escape(w), text))
    if found:
        doc.close()
        raise RuntimeError("%d account name word(s) still in the PDF text; not written" % len(found))
    os.makedirs(out_dir, exist_ok=True)
    out_pdf = os.path.join(out_dir, name + ".pdf")
    shutil.copyfile(clean, out_pdf)
    pngs = []
    for i, page in enumerate(doc):
        png = os.path.join(out_dir, "%s-render%s.png" % (name, "" if i == 0 else "-p%d" % (i + 1)))
        page.get_pixmap(dpi=dpi).save(png)
        pngs.append(png)
    pages = doc.page_count
    doc.close()
    return out_pdf, pngs, pages


def main(argv=None):
    ap = argparse.ArgumentParser(description="Export a Fusion drawing for the repo: PDF "
                                             "without the account name, plus PNGs.")
    ap.add_argument("drawing", help="the drawing's name in --folder")
    ap.add_argument("out_dir", help="repo folder for DRAWING.pdf and its PNGs")
    ap.add_argument("--sheets", default="", help="sheet range such as 1 or 1-3 (default all)")
    ap.add_argument("--dpi", type=int, default=110)
    ap.add_argument("--folder", default=rs.DEFAULT_FOLDER)
    ap.add_argument("--url", default=rs.DEFAULT_URL)
    ap.add_argument("--timeout", type=float, default=300.0)
    ap.add_argument("--lock", default=None)
    ap.add_argument("--lock-wait", type=float, default=1200.0)
    ap.add_argument("--label", default=os.environ.get(rs.LABEL_ENV, ""))
    opts = ap.parse_args(argv)

    tmp = tempfile.mkdtemp(prefix="fusion-export-")
    raw = os.path.join(tmp, "raw.pdf")
    names = os.path.join(tmp, "names.json")
    lock = rs.FusionLock(opts.lock or rs.default_lock_path(opts.url),
                         label=opts.label or "export_drawing", hold_s=3 * opts.timeout + 300,
                         script="export_drawing.py %s" % opts.drawing)
    try:
        try:
            lock.acquire(opts.lock_wait, token=os.environ.get(rs.TOKEN_ENV) or None)   # also inside a held lock
        except (rs.LockTimeout, KeyboardInterrupt) as e:
            print("export_drawing: %s" % (e or "stopped while waiting"), file=sys.stderr)
            return 3
        try:
            mcp = rs.FusionMcp(opts.url, opts.timeout)
            mcp.initialize()
            ok, out = rs.run_in_fusion(mcp, rs.doc_script("open", opts.drawing, opts.folder))
            if not ok:
                print("export_drawing: couldn't open %s: %s" % (opts.drawing, out), file=sys.stderr)
                return 1
            opened_here = any(line.startswith("run_script: opened") for line in (out or "").splitlines())   # the runner may warn first
            ok, out = rs.run_in_fusion(mcp, EXPORT_SCRIPT % {
                "name": opts.drawing, "raw": raw, "sheets": opts.sheets, "names": names})
            print("export_drawing: %s" % (out or "").strip())
            if opened_here:
                rs.run_in_fusion(mcp, rs.doc_script("close", opts.drawing, opts.folder))
            if not ok:
                return 1
        except rs.McpError as e:
            print("export_drawing: %s" % e, file=sys.stderr)
            return 2
        finally:
            lock.release()
        try:
            out_pdf, pngs, pages = check_and_render(raw, account_words(names), opts.out_dir,
                                                    opts.drawing, opts.dpi)
        except RuntimeError as e:
            print("export_drawing: %s" % e, file=sys.stderr)
            return 1
        print("export_drawing: %s (%d page(s), \"Created by\" cleared, no account name in the text)"
              % (out_pdf, pages))
        for png in pngs:
            print("export_drawing: render %s" % png)
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
