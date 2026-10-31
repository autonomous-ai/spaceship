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

from common import Finding, owner_for, rel, walk_files, parse_file_name, pn_class, is_soft


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


# D-89 (PM rule, 2026-11-01): a part covered by a tabulated drawing that lists its part number counts
# as drawn; a plain knife-cut felt or fill rectangle needs no drawing when the cut list gives its size,
# material, tolerance and part number.
TABULATED = re.compile(r"\bTABULATED\b", re.I)


def tabulated_cover(idx):
    """pn -> [(rev, pdf, drawing pn)] for the part numbers listed in a tabulated drawing. A tabulated drawing
    says TABULATED in its text; it covers every other number of its own family and kind (parts for a part
    drawing, assemblies for an assembly drawing) that its text lists, so a mating part named in a note or an
    assembly drawing's parts list doesn't count."""
    cover = {}
    for own, files in idx.items():
        kind = pn_class(own)
        if kind not in ("part", "assembly"):
            continue
        for rv, p in files.get("DWG", []):
            if not p.lower().endswith(".pdf"):
                continue
            text = pdf_text(p)
            if not text or not TABULATED.search(text):
                continue
            for n in sorted(set(re.findall(r"(?<!\d)(\d{6})(?!\d)", text))):
                if n != own and n[:2] == own[:2] and pn_class(n) == kind:
                    cover.setdefault(n, []).append((rv, p, own))
    return cover


def _cell(row, pattern):
    return [(k, (v or "").strip()) for k, v in row.items() if k and re.search(pattern, k, re.I) and (v or "").strip()]


FEATURE_WORDS = re.compile(r"\b(?:pockets?|notch(?:es)?|holes?|slots?|cut-?outs?)\b", re.I)     # D-89: these keep the drawing


def cut_list_lacks(root, pn):
    """For a felt or fill piece (D-89): None when no cut list (a .csv with "cut" in its name, as D-89 defines
    it) has a row for pn (a cell that is exactly the number), else (what the most complete row lacks of size,
    material and tolerance, its file, the features the row names: pockets, notches, holes)."""
    from common import read_csv
    best = None
    for top in ("v2/03-Manufacturing", "v2/02-Drawings"):
        for p in walk_files(root, top, exts=(".csv",)):
            if "cut" not in os.path.basename(p).lower():
                continue
            for row in read_csv(p):
                if not any((v or "").strip() == pn for v in row.values() if isinstance(v, str)):
                    continue
                lacks = []
                sizes = _cell(row, r"size|dimension|length|width|thick|^[lwt]_?mm$")
                if not any(re.search(r"\d", v) for _k, v in sizes):
                    lacks.append("size")
                if not _cell(row, r"material|grade"):
                    lacks.append("material")
                if not _cell(row, r"tol") and not any(re.search(r"±|\+/-", v or "") for v in row.values()
                                                      if isinstance(v, str)):
                    lacks.append("tolerance")
                feats = sorted({m.group(0).lower() for v in row.values() if isinstance(v, str)
                                for m in FEATURE_WORDS.finditer(v)})
                if best is None or len(lacks) < len(best[0]):
                    best = (lacks, rel(root, p), feats)
    return best


def policy(root, key, default):
    p = os.path.join(root, "v2/04-Checks/config/policy.csv")
    if os.path.exists(p):
        import csv
        with open(p, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                if row.get("key") == key and row.get("value"):
                    return row["value"].strip()
    return default


def screen_locked():
    """True when this Mac's console session is locked (ioreg IOConsoleUsers), as tools/fusion/start_drawing.py
    reads it; None when it can't tell (not a Mac, no ioreg)."""
    import plistlib
    try:
        out = subprocess.run(["ioreg", "-n", "Root", "-d1", "-a"], capture_output=True, timeout=30).stdout
        data = plistlib.loads(out)
    except Exception:
        return None
    data = data[0] if isinstance(data, list) else data
    return any(u.get("CGSSessionScreenIsLocked") for u in data.get("IOConsoleUsers", []))


def missing_drawing_severity(root):
    """The severity of a missing drawing for a part we make, from config/policy.csv: severe or major, or
    auto-screen-lock (D-84): major while the screen is locked, severe otherwise or when it can't tell."""
    v = policy(root, "missing_drawing_severity", "severe")
    if v == "auto-screen-lock":
        return "major" if screen_locked() else "severe"
    return v


def check_drawings(root, part_numbers, holes_by_pn, names=None, faces_by_pn=None, src_by_pn=None):
    """part_numbers: the made parts and assemblies to check (from the parts
    lists and the STEP products). holes_by_pn: pn -> list of holes.
    faces_by_pn: pn -> face count of each of its bodies (a plain rectangle has 6).
    src_by_pn: pn -> the STEP or parts list it comes from, for the owner of a part without files of its own."""
    names = names or {}
    faces_by_pn = faces_by_pn or {}
    src_by_pn = src_by_pn or {}
    fs = []
    idx = index_files(root)
    missing_sev = missing_drawing_severity(root)          # PM rulings D-73, D-84: see config/policy.csv
    tab = tabulated_cover(idx)                            # D-89
    for pn in sorted(part_numbers):
        cls = pn_class(pn)
        if cls not in ("part", "assembly"):
            continue
        files = idx.get(pn, {})
        dwgs = files.get("DWG", [])
        pdfs = [(rv, p) for rv, p in dwgs if p.lower().endswith(".pdf")]
        where = (files.get("STEP") or files.get("CAD") or [("", "")])[0][1]
        r_where = rel(root, where) if where else ""
        owner = owner_for(r_where or src_by_pn.get(pn, ""), pn)
        label = ("%s %s" % (pn, names.get(pn, ""))).strip()
        soft = is_soft(names.get(pn, ""))          # by the name's head noun: SEAL HOLDER is a holder
        if not pdfs and pn in tab:                 # D-89: listed in a tabulated drawing, so drawn
            cad_revs = {rv for rv, _p in files.get("CAD", []) + files.get("STEP", [])}
            tab_revs = {rv for rv, _p, _own in tab[pn]}
            if cad_revs and not (tab_revs & cad_revs):
                rv, tp, own = sorted(tab[pn])[-1]
                fs.append(Finding("C05", "rev-mismatch", pn, "major",
                                  "%s: its tabulated drawing %s is revision %s but its CAD/STEP is revision %s." % (
                                      label, os.path.basename(tp), "/".join(sorted(tab_revs)),
                                      "/".join(sorted(cad_revs))),
                                  "Export the drawing, CAD and STEP from the same revision (guideline section 4.2).",
                                  rel(root, tp), owner))
            continue
        if not pdfs and is_soft(names.get(pn, ""), kinds=("FELT", "FILL")):
            # D-89: a plain knife-cut felt or fill rectangle needs no drawing when its cut-list row gives
            # size, material, tolerance and part number; one with holes needs a drawing
            row = cut_list_lacks(root, pn)
            n_holes = len(hole_axes(holes_by_pn.get(pn, [])))
            n_faces = max(faces_by_pn.get(pn) or [0])
            if row is not None and not row[0] and not row[2] and not n_holes and n_faces <= 6:
                continue
            why = []
            if row is not None and row[2]:
                why.append("its cut-list row names %s, so it isn't a plain rectangle and needs a drawing" %
                           " and ".join(row[2]))
            elif n_holes:
                why.append("it isn't a plain rectangle (its STEP has %d hole axes), so it needs a drawing" % n_holes)
            elif n_faces > 6:
                why.append("it isn't a plain rectangle (a body in its STEP has %d faces, a block has 6: pockets "
                           "or notches), so it needs a drawing" % n_faces)
            if row is None:
                why.append("no cut list (a .csv with CUT in its name) has a row for it")
            elif row[0]:
                why.append("its cut-list row in %s doesn't give %s" % (row[1], ", ".join(row[0])))
            fs.append(Finding("C05", "no-drawing", pn, "major",
                              "%s has no drawing, and D-89's cut-list route doesn't apply: %s." % (
                                  label, "; ".join(why)),
                              "For a plain knife-cut rectangle, give part number, size, material and tolerance in "
                              "a cut list, a .csv with CUT in its name (D-89); otherwise make its drawing.",
                              r_where, owner))
            continue
        if not pdfs and soft and (files.get("DXF") or _in_cut_list(root, pn)):
            continue        # other soft goods may be defined by a DXF or a cut list line instead of a drawing
        if not pdfs:
            fs.append(Finding("C05", "no-drawing", pn, missing_sev if cls == "part" and not soft else "major",
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
        if not re.search(r"\bUNITS?\s*[:=]?\s*MM\b", up):
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
