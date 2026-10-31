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


def cut_list_lacks(root, pn, thickness=False):
    """D-89: None when no list has a row for pn (a cell that is exactly the number), else (what the most
    complete row lacks of size, thickness when asked (soft goods other than felt and fill), material and
    tolerance, its file, the features the row names: pockets, notches, holes). A cut list is a .csv with "cut"
    in its name, and a parts-list row that gives the same serves as one (PM ruling 2026-11-01, as the release
    checklist reads it): every .csv under v2/03-Manufacturing and v2/02-Drawings counts."""
    from common import read_csv
    best = None
    for top in ("v2/03-Manufacturing", "v2/02-Drawings"):
        for p in walk_files(root, top, exts=(".csv",)):
            for row in read_csv(p):
                if not any((v or "").strip() == pn for v in row.values() if isinstance(v, str)):
                    continue
                lacks = []
                sizes = _cell(row, r"size|dimension|length|width|thick|^[lwt]_?mm$")
                if not any(re.search(r"\d", v) for _k, v in sizes):
                    lacks.append("size")
                thick = any(re.search(r"\d", v) for _k, v in _cell(row, r"thick|^t_?mm$")) or any(
                    len(re.findall(r"\d+(?:\.\d+)?", v)) >= 3 and re.search(r"[x×]", v, re.I) for _k, v in sizes)
                if thickness and not thick:
                    lacks.append("thickness")
                if not _cell(row, r"material|grade"):
                    lacks.append("material")
                if not _cell(row, r"tol") and not any(re.search(r"±|\+/-", v or "") for v in row.values()
                                                      if isinstance(v, str)):
                    lacks.append("tolerance")
                feats = sorted({m.group(0).lower() for v in row.values() if isinstance(v, str)
                                for m in FEATURE_WORDS.finditer(v)})
                if best is None or len(lacks) + len(feats) < len(best[0]) + len(best[2]):
                    best = (lacks, rel(root, p), feats)
    return best


def soft_kind(name):
    """'felt or fill', 'soft' (foam, gasket, seal, tape) or '' by the name's head noun (D-89)."""
    if not is_soft(name):
        return ""
    return "felt or fill" if is_soft(name, kinds=("FELT", "FILL")) else "soft"


# D-89 part 4 (PM rule, 2026-11-01): a flat part cut from sheet (laser, waterjet or CNC router) with no bends
# and no machined features needs no drawing when its DXF gives the full outline and every hole, and its
# parts-list row gives material, thickness, finish, a general tolerance (ISO 2768-m) and any critical hole note.
# The row is read exactly as the release checklist reads it (v2/00-Control/build_release_checklist.py,
# flat_lacks; same patterns); the check adds what only the files show: a line on the DXF's BEND layer means
# folded (Reviewer 6's hardening), the STEP shows no bends, pockets or blind holes, and the DXF has every hole.
SHEET_CUT = re.compile(r"laser|water\s*-?\s*jet|router|routed", re.I)
NOT_FLAT = re.compile(r"bend|bent|fold|brake|groove|\blap\b|half-lap|rebate|pocket|machin|\bmill(?:ed|ing)?\b|drill|"
                      r"\btap(?:ped|ping)?\b|thread|countersink|counterbore|ream|\bturn(?:ed|ing)?\b|lathe|chamfer|weld|"
                      r"bond", re.I)
BEND_LAYER = re.compile(r"\b(?:BEND|FOLD)", re.I)


DXF_LAYERS_ALLOWED = ("CUT", "MARK")          # D-89 part 4: a flat part's DXF holds only these (guideline 9)
DXF_STRUCTURE = ("BLOCK", "ENDBLK", "SEQEND", "VERTEX", "ENDSEC", "EOF")   # records, not lines


def dxf_summary(path):
    """A DXF read without a library: {'units': $INSUNITS, 'layers': {layer: count of drawing entities in the
    ENTITIES and BLOCKS sections}, 'circles': [diameters of CIRCLE entities]}; None when the file can't be read
    as ASCII DXF (empty or binary). Block records (BLOCK, ENDBLK) and a polyline's VERTEX and SEQEND are records,
    not lines, so a block header on layer 0 doesn't count."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError:
        return None
    if not text.strip() or text.startswith("AutoCAD Binary DXF"):
        return None
    lines = text.splitlines()
    pairs = [(lines[i].strip(), lines[i + 1].strip()) for i in range(0, len(lines) - 1, 2)]
    out = {"units": None, "layers": {}, "circles": []}
    sec, cur = None, None
    for k, (code, val) in enumerate(pairs):
        if code == "2" and k and pairs[k - 1] == ("0", "SECTION"):
            sec, cur = val.upper(), None
        elif code == "0" and val == "ENDSEC":
            sec, cur = None, None
        elif code == "9" and val == "$INSUNITS" and k + 1 < len(pairs):
            out["units"] = pairs[k + 1][1]
        elif sec in ("ENTITIES", "BLOCKS") and code == "0":
            cur = None if val.upper() in DXF_STRUCTURE else val.upper()
        elif sec in ("ENTITIES", "BLOCKS") and cur and code == "8":
            out["layers"][val] = out["layers"].get(val, 0) + 1
        elif sec == "ENTITIES" and cur == "CIRCLE" and code == "40":
            try:
                out["circles"].append(round(2.0 * float(val), 2))
            except ValueError:
                pass
    return out


def _rows_naming(root, pn):
    """Every row of a .csv under v2/03-Manufacturing or v2/02-Drawings with a cell that is exactly pn, as
    ({column: value}, file): the rows a D-89 reading may use (the checklist reads the same files)."""
    from common import read_csv
    for top in ("v2/03-Manufacturing", "v2/02-Drawings"):
        for p in walk_files(root, top, exts=(".csv",)):
            for row in read_csv(p):
                cells = {(k or "").strip(): (v or "").strip() for k, v in row.items()
                         if isinstance(k, str) and isinstance(v, str)}
                if pn in cells.values():
                    yield cells, rel(root, p)


def flat_row_lacks(root, pn):
    """D-89 (4), as the checklist's flat_lacks: what the best row lacks for a flat part cut from sheet to go
    without a drawing; None when no row has the number."""
    best = None
    for cells, _p in _rows_naming(root, pn):
        def has(pattern):
            return [v for k, v in cells.items() if re.search(pattern, k, re.I) and v]
        process = " ".join(has(r"process"))
        material = " ".join(has(r"material|grade"))
        sizes = has(r"size|dimension|length|width|thick|^[lwt]_?mm$")
        thick = any(re.search(r"\d", v) for v in has(r"thick|^t_?mm$")) or any(
            len(re.findall(r"\d+(?:\.\d+)?", v)) >= 3 and re.search(r"[x×]", v, re.I) for v in sizes) or bool(
            re.search(r"\d+(?:\.\d+)?\s*mm\b", material))
        not_flat = sorted({m.group(0).lower() for m in NOT_FLAT.finditer(process)})
        lacks = [n for n, ok in (
            ("a cut by laser, waterjet or router in its process", bool(SHEET_CUT.search(process))),
            ("no bends or machined features (its process names %s)" % ", ".join(not_flat), not not_flat),
            ("material", bool(material)), ("thickness", thick), ("finish", bool(has(r"finish"))),
            ("an ISO 2768 general tolerance", any("2768" in v for v in cells.values()))) if not ok]
        if best is None or len(lacks) < len(best):
            best = lacks
    return best


def flat_cut_lacks(root, pn, files, holes, flat):
    """D-89 part 4: what keeps this part from going without a drawing (empty when it may). flat: the STEP's
    (ok, thickness, why), or None when no STEP holds the part."""
    why = []
    dxfs = sorted(files.get("DXF", []))
    if not dxfs:
        return ["it has no DXF of its own"]
    rv, dxf = dxfs[-1]
    d = dxf_summary(dxf)
    if d is None:
        return ["its DXF can't be read as ASCII DXF, so it can't be shown flat"]
    other = sorted(l for l in d["layers"] if l.upper() not in DXF_LAYERS_ALLOWED)
    if other:
        bend = [l for l in other if BEND_LAYER.search(l)]
        why.append("its DXF has lines on the %s layer%s; only CUT and MARK are allowed%s" % (
            ", ".join(other), "s" if len(other) > 1 else "", ", so it is folded" if bend else ""))
    if d["units"] not in (None, "4"):
        why.append("its DXF isn't in mm ($INSUNITS %s)" % d["units"])
    cad_revs = {r for r, _p in files.get("CAD", []) + files.get("STEP", [])}
    if cad_revs and rv not in cad_revs:
        why.append("its DXF is revision %s but its CAD/STEP is %s" % (rv, "/".join(sorted(cad_revs))))
    if flat is not None and not flat[0]:
        why.append(flat[2])
    want = {}
    for h in hole_axes(holes or []):          # every hole in the STEP must be in the DXF, by diameter
        k = round(h.diameter, 1)
        want[k] = want.get(k, 0) + 1
    for dia, n in sorted(want.items()):
        got = sum(1 for c in d["circles"] if abs(c - dia) <= 0.1)
        if got < n:
            why.append("its DXF has %d of the %d Ø%g holes in its STEP" % (got, n, dia))
    lacks = flat_row_lacks(root, pn)
    worked = [l for l in (lacks or []) if l.startswith("no bends or machined features")]
    # a folded or machined part keeps its drawing: say why, and leave out the row's other gaps
    not_flat = [w for w in why if "only CUT and MARK" in w or w == (flat[2] if flat is not None and not flat[0] else None)]
    if not_flat or worked:
        return not_flat + ["its row's process names %s" % l.split("names ", 1)[-1].rstrip(")") for l in worked]
    if lacks is None:
        why.append("no parts list or cut list has a row for it")
    elif lacks:
        why.append("its row lacks %s" % "; ".join(lacks))
    return why


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


def check_drawings(root, part_numbers, holes_by_pn, names=None, faces_by_pn=None, src_by_pn=None, flat_by_pn=None):
    """part_numbers: the made parts and assemblies to check (from the parts
    lists and the STEP products). holes_by_pn: pn -> list of holes.
    faces_by_pn: pn -> face count of each of its bodies (a plain rectangle has 6).
    src_by_pn: pn -> the STEP or parts list it comes from, for the owner of a part without files of its own."""
    names = names or {}
    faces_by_pn = faces_by_pn or {}
    src_by_pn = src_by_pn or {}
    flat_by_pn = flat_by_pn or {}      # pn -> (ok, thickness, why) from the STEP (D-89 part 4)
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
        kind = soft_kind(names.get(pn, ""))
        if not pdfs and kind == "soft" and files.get("DXF"):
            continue        # D-89 (3): a DXF gives the outline of a foam, gasket, seal or tape, any shape
        if not pdfs and kind:
            # D-89 (2) felt or fill, (3) other soft goods: a plain knife-cut rectangle or strip needs no drawing
            # when its cut-list or parts-list row gives size (thickness too, for (3)), material, tolerance and
            # part number; a piece with pockets, notches or holes keeps its drawing (or, for (3), a DXF)
            row = cut_list_lacks(root, pn, thickness=(kind == "soft"))
            n_holes = len(hole_axes(holes_by_pn.get(pn, [])))
            n_faces = max(faces_by_pn.get(pn) or [0])
            if row is not None and not row[0] and not row[2] and not n_holes and n_faces <= 6:
                continue
            why = []
            if row is not None and row[2]:
                why.append("its row names %s, so it isn't a plain rectangle" % " and ".join(row[2]))
            elif n_holes:
                why.append("it isn't a plain rectangle (its STEP has %d hole axes)" % n_holes)
            elif n_faces > 6:
                why.append("it isn't a plain rectangle (a body in its STEP has %d faces, a block has 6: pockets "
                           "or notches)" % n_faces)
            if row is None:
                why.append("no cut list or parts list has a row for it")
            elif row[0]:
                why.append("its row in %s doesn't give %s" % (row[1], ", ".join(row[0])))
            need = ("a drawing" if kind == "felt or fill" else "a DXF of its outline or a drawing")
            fs.append(Finding("C05", "no-drawing", pn, "major",
                              "%s has no drawing, and D-89's cut-list route doesn't apply: %s." % (
                                  label, "; ".join(why)),
                              "For a plain knife-cut rectangle or strip, give part number, size%s, material and "
                              "tolerance in its parts-list or cut-list row (D-89); otherwise make %s." % (
                                  ", thickness" if kind == "soft" else "", need),
                              r_where, owner))
            continue
        if not pdfs and cls == "part" and files.get("DXF"):
            # D-89 part 4: a flat sheet part goes on its DXF and its parts-list row
            lacks = flat_cut_lacks(root, pn, files, holes_by_pn.get(pn), flat_by_pn.get(pn))
            if not lacks:
                continue
            fs.append(Finding("C05", "no-drawing", pn, missing_sev,
                              "%s has no drawing, and D-89 part 4 (flat sheet part on its DXF) doesn't apply: %s." % (
                                  label, "; ".join(lacks)),
                              "Make its drawing; or, for a flat part cut from sheet with no bends and no machined "
                              "features, give the full outline and every hole in its DXF and material, thickness, "
                              "finish, ISO 2768-m and any critical hole note in its parts-list row (D-89 part 4).",
                              r_where, owner))
            continue
        if not pdfs:
            fs.append(Finding("C05", "no-drawing", pn, missing_sev if cls == "part" else "major",
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
