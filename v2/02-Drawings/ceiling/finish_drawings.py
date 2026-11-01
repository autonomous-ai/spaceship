"""Finish CEILING, AIR and INTERIOR drawing PDFs (offline): name strip, then a PNG to check by eye.

    python3 v2/02-Drawings/ceiling/finish_drawings.py ceiling [frame_c1 tray ...] [--log ANNOTATE_LOG]
    python3 v2/02-Drawings/ceiling/finish_drawings.py air
    python3 v2/02-Drawings/ceiling/finish_drawings.py interior

For each drawing of the team's specs (all of them, or the keys given): takes the raw export
the annotate run wrote to <team folder>/.raw/<drawing>.pdf, writes "Autonomous" under "Created by"
and fills the title block with tools/fusion/pdf_clear_field.py (the repo is public; the owner's
rule), replaces the notes and title data pictures with the same words as text
(pdf_notes_text.py, so the mechanical checks can read them), saves the repo copy as
<team folder>/<drawing>.pdf and renders <drawing without _DWG>_IMG.png next to it (110 dpi,
as BASE's drawings). Then, for the ceiling's drawings, reads the PDF back with
check_drawing_pdf.py (symbol, image sizes and places, hidden lines, text heights, names; the
annotate run's log gives the view extents) and fails if a check fails. Skips a drawing whose
raw PDF isn't there. Needs PyMuPDF.
"""

import importlib.util
import os
import subprocess
import sys

import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CLEAR = os.path.join(REPO, "tools", "fusion", "pdf_clear_field.py")
TEAMS = {"ceiling": ("ceiling", "drawing_specs.py"), "air": ("air", "drawing_specs_air.py"),
         "interior": ("interior", "drawing_specs_interior.py")}


def specs(team):
    folder, fname = TEAMS[team]
    path = os.path.join(REPO, "v2", "02-Drawings", folder, fname)
    spec = importlib.util.spec_from_file_location("specs_" + team, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return os.path.dirname(path), mod.SPECS, mod.ORDER, getattr(mod, "IMG_W", 170.0)


def finish(folder, drawing, sp=None, img_w=None):
    raw = os.path.join(folder, ".raw", drawing + ".pdf")
    if not os.path.exists(raw):
        return "no raw PDF"
    out = os.path.join(folder, drawing + ".pdf")
    subprocess.run([sys.executable, CLEAR, raw, out], check=True)
    if sp is not None and sp.get("images"):
        # the notes and title data as text in place of their pictures (pdf_notes_text.py: C05 reads the text)
        sys.path.insert(0, HERE)
        import pdf_notes_text as T
        for what, pic_h, txt_h in T.replace_pictures(out, sp, img_w):
            print("  %s: picture %.1f mm tall replaced by text %.1f mm tall" % (what, pic_h, txt_h))
    png = os.path.join(folder, (drawing[:-4] if drawing.endswith("_DWG") else drawing) + "_IMG.png")
    with fitz.open(out) as doc:
        doc[0].get_pixmap(dpi=110).save(png)
        pages = doc.page_count
    return "%s (%d page%s), %s" % (os.path.basename(out), pages, "" if pages == 1 else "s", os.path.basename(png))


def main(argv):
    log_text = None
    if "--log" in argv:
        i = argv.index("--log")
        with open(argv[i + 1], encoding="utf-8", errors="replace") as fh:
            log_text = fh.read()
        argv = argv[:i] + argv[i + 2:]
    team, keys = argv[0], argv[1:]
    folder, sp, order, img_w = specs(team)
    failed = []
    for k in keys or order:
        done = finish(folder, sp[k]["drawing"], sp[k], img_w)
        print("%s: %s" % (k, done))
        if team != "ceiling" or done == "no raw PDF":
            continue
        sys.path.insert(0, HERE)
        import check_drawing_pdf as C
        bad, warn, info = C.check(k, log_text=log_text)
        for line in info + ["WARNING: " + w for w in warn] + bad:
            print("  " + line)
        print("CHECK PDF %s: %s" % (sp[k]["drawing"], "FAIL (%d)" % len(bad) if bad else "PASS"))
        if bad:
            failed.append(k)
    if failed:
        sys.exit("drawings that fail the PDF check: %s" % failed)


if __name__ == "__main__":
    main(sys.argv[1:])
