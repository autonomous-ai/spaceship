#!/usr/bin/env python3
"""C05 drawing completeness.

Every part we make (part numbers xx1000 to xx7999) has a drawing, and every
assembly (xx0001 to xx0999) has an assembly drawing, named
PARTNO_REV_NAME_DWG.pdf (conventions section 7) with the same revision as its
CAD and STEP. In each part drawing's text: units, material, finish, a
tolerance rule, the projection, and the holes (tags H01..., a hole table, or
diameter callouts) against the holes the STEP of that part has.

Reads PDF text with PyMuPDF when it is installed, else with pdftotext. The
text test can't see symbols drawn as lines (the first-angle symbol); those
are noted, not failed.
"""

import os
import re
import shutil
import subprocess

from common import Finding, owner_for, rel, walk_files, parse_file_name, pn_class


def pdf_text(path):
    try:
        import fitz  # PyMuPDF
        with fitz.open(path) as doc:
            return "\n".join(page.get_text() for page in doc)
    except ImportError:
        pass
    exe = shutil.which("pdftotext")
    if exe:
        out = subprocess.run([exe, "-layout", path, "-"], capture_output=True, text=True, timeout=60)
        return out.stdout
    return None


def index_files(root):
    """pn -> {doctype: [(rev, path)]} for every conventions-named file."""
    idx = {}
    for top in ("v2/01-CAD-Native", "v2/02-Drawings", "v2/03-Manufacturing"):
        for p in walk_files(root, top):
            m = parse_file_name(p)
            if not m:
                continue
            idx.setdefault(m["pn"], {}).setdefault(m["doc"], []).append((m["rev"], p))
    return idx


def hole_axes(step_holes):
    """Distinct hole axes (holes on one axis through two tube walls count once)."""
    axes = []
    for h in step_holes:
        for a in axes:
            if abs(abs(sum(x * y for x, y in zip(a.axis, h.axis))) - 1.0) < 1e-4:
                d = [h.center[k] - a.center[k] for k in range(3)]
                t = sum(d[k] * a.axis[k] for k in range(3))
                lat = (sum(x * x for x in d) - t * t) ** 0.5
                if lat < 0.05:
                    break
        else:
            axes.append(h)
    return axes


def _in_cut_list(root, pn):
    for p in walk_files(root, "v2/03-Manufacturing", exts=(".csv",)):
        if "cut" in os.path.basename(p).lower():
            with open(p, encoding="utf-8", errors="replace") as fh:
                if re.search(r"\b%s\b" % pn, fh.read()):
                    return True
    return False


def check_drawings(root, part_numbers, holes_by_pn, names=None):
    """part_numbers: the made parts and assemblies to check (from the parts
    lists and the STEP products). holes_by_pn: pn -> list of holes."""
    names = names or {}
    fs = []
    idx = index_files(root)
    for pn in sorted(part_numbers):
        cls = pn_class(pn)
        if cls not in ("part", "assembly"):
            continue
        files = idx.get(pn, {})
        dwgs = files.get("DWG", [])
        pdfs = [(rv, p) for rv, p in dwgs if p.lower().endswith(".pdf")]
        where = (files.get("STEP") or files.get("CAD") or [("", "")])[0][1]
        r_where = rel(root, where) if where else ""
        owner = owner_for(r_where, pn)
        label = ("%s %s" % (pn, names.get(pn, ""))).strip()
        soft = re.search(r"FILL|FELT|GASKET|SEAL|TAPE|FOAM", names.get(pn, ""), re.I)
        if not pdfs and soft and (files.get("DXF") or _in_cut_list(root, pn)):
            continue        # soft goods may be defined by a DXF or a cut list line instead of a drawing
        if not pdfs:
            fs.append(Finding("C05", "no-drawing", pn, "severe" if cls == "part" and not soft else "major",
                              "%s has no drawing PDF (%s_REV_NAME_DWG.pdf under v2/02-Drawings)%s." % (
                                  label, pn, " though its CAD is in %s" % r_where if r_where else ""),
                              "Make the ISO first-angle drawing, export it through the name strip, and commit it.",
                              r_where, owner))
            continue
        revs = {rv for rv, _p in pdfs}
        cad_revs = {rv for rv, _p in files.get("CAD", []) + files.get("STEP", [])}
        rv, pdf = sorted(pdfs)[-1]
        rp = rel(root, pdf)
        if cad_revs and not (revs & cad_revs):
            fs.append(Finding("C05", "rev-mismatch", pn, "major",
                              "%s: drawing revision %s but CAD/STEP revision %s." % (
                                  label, "/".join(sorted(revs)), "/".join(sorted(cad_revs))),
                              "Export the drawing, CAD and STEP from the same revision (guideline section 4.2).",
                              rp, owner))
        text = pdf_text(pdf)
        if text is None:
            continue
        up = text.upper()
        lacks = []
        if not re.search(r"UNITS?\s*:?\s*MM|\bMM\b", up):
            lacks.append("units (mm)")
        if cls == "part":
            if not re.search(r"MATERIAL", up) or re.search(r"MATERIAL\s*:?\s*(SEE PARTS LIST)?\s*$", up, re.M) and \
                    not re.search(r"EN AW|\d{4}|DX51|A2|A4|STEEL|ALUMIN|ACP|PET", up):
                lacks.append("material")
            if not re.search(r"FINISH|ANODI|POWDER|ZINC|GALV|PAINT|MILL FINISH", up):
                lacks.append("finish")
        if not re.search(r"ISO\s*2768|ISO\s*22081|GENERAL TOLERANCE|TOLERANCE|±|\+/-", up):
            lacks.append("tolerances (a general rule or values on the dimensions)")
        if lacks:
            fs.append(Finding("C05", "drawing-content", pn, "major",
                              "%s drawing %s doesn't state: %s." % (label, os.path.basename(rp), ", ".join(lacks)),
                              "Add them to the title block or the notes (guideline sections 3.1, 6.3, 9).", rp, owner))
        n_axes = len(hole_axes(holes_by_pn.get(pn, [])))
        if cls == "part" and n_axes:
            tags = set(re.findall(r"\bH\d{2}\b", up))
            table = bool(re.search(r"X\s*\(MM\)", up) and re.search(r"Y\s*\(MM\)", up))
            dia = len(re.findall(r"[Ø⌀]\s*\d", text))
            if not tags and not table and not dia:
                fs.append(Finding("C05", "holes-not-dimensioned", pn, "severe",
                                  "%s has %d hole axes in its STEP, but drawing %s has no hole tags, no hole table "
                                  "and no diameter callouts." % (label, n_axes, os.path.basename(rp)),
                                  "Tag every hole (H01...), dimension it to its centre from the datums or put it in "
                                  "a hole table with X (mm) and Y (mm) (guideline section 6.2).", rp, owner))
            elif tags and len(tags) < n_axes and not table:
                fs.append(Finding("C05", "holes-untagged", pn, "major",
                                  "%s has %d hole axes in its STEP but %d hole tags on drawing %s and no hole "
                                  "table." % (label, n_axes, len(tags), os.path.basename(rp)),
                                  "Tag the rest, or show they share a tag through a pattern note.", rp, owner))
    return fs
