"""Finish CEILING, AIR and INTERIOR drawing PDFs (offline): name strip, then a PNG to check by eye.

    python3 v2/02-Drawings/ceiling/finish_drawings.py ceiling [frame_c1 tray ...]
    python3 v2/02-Drawings/ceiling/finish_drawings.py air
    python3 v2/02-Drawings/ceiling/finish_drawings.py interior

For each drawing of the team's specs (all of them, or the keys given): takes the raw export
the annotate run wrote to <team folder>/.raw/<drawing>.pdf, removes the account holder's name
under "Created by" with tools/fusion/pdf_clear_field.py (the repo is public), saves the repo
copy as <team folder>/<drawing>.pdf and renders <drawing without _DWG>_IMG.png next to it (110 dpi,
as BASE's drawings). Skips a drawing whose raw PDF isn't there. Needs PyMuPDF.
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
    return os.path.dirname(path), mod.SPECS, mod.ORDER


def finish(folder, drawing):
    raw = os.path.join(folder, ".raw", drawing + ".pdf")
    if not os.path.exists(raw):
        return "no raw PDF"
    out = os.path.join(folder, drawing + ".pdf")
    subprocess.run([sys.executable, CLEAR, raw, out], check=True)
    png = os.path.join(folder, (drawing[:-4] if drawing.endswith("_DWG") else drawing) + "_IMG.png")
    with fitz.open(out) as doc:
        doc[0].get_pixmap(dpi=110).save(png)
        pages = doc.page_count
    return "%s (%d page%s), %s" % (os.path.basename(out), pages, "" if pages == 1 else "s", os.path.basename(png))


def main(argv):
    team, keys = argv[0], argv[1:]
    folder, sp, order = specs(team)
    for k in keys or order:
        print("%s: %s" % (k, finish(folder, sp[k]["drawing"])))


if __name__ == "__main__":
    main(sys.argv[1:])
