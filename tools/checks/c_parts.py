#!/usr/bin/env python3
"""Checks on the parts lists (the engineers' parts-list CSVs for the BOM),
the shipping list, and their match with the CAD.

- C04: every shipping piece 20 kg or less except glass; through a 914 x 2032
  doorway (and the 810 mm rule of REQ-ASM-06, PROPOSED, as a note); fits its
  pallet (48 x 40 in, or the standard long 48 x 96 in) standing or lying.
- C06: BOM completeness: every row complete and valid; part numbers unique;
  every CAD product in a parts list and every made part in the CAD.
- C07: fastener schedule: every screw, bolt, nut, washer and rivnut with
  size, length, grade, finish, torque, quantity, maker and SKU; written to
  v2/04-Checks/fastener-schedule.csv with its CAD locations. Thread
  engagement and bottoming need the geometry along each bolt: the Fusion
  check measures them (tools/checks/fusion/).
- C10: mixed metals: bare steel touching aluminium (from the assembled
  CAD, boxes touching), and fasteners whose material or finish is unknown.
- C11: every part has a material grade and a finish.
"""

import os
import re
from collections import defaultdict

from common import (register_names, name_words, reserved_spaces, JOINTS_KEYS, Finding, owner_for, rel, walk_files, read_csv, num, pn_class, pn_problems, is_fastener,
                    parse_file_name, is_soft)

ALIASES = {
    "part_number": ("part_number", "partnumber", "part_no", "partno", "pn", "part", "item_number", "number"),
    "name": ("name", "name_en", "english_name", "description", "part_name"),
    "name_vi": ("name_vi", "vietnamese", "name_vn", "vi_name", "ten", "ten_vi"),
    "material": ("material", "materials"),
    "grade": ("grade", "material_grade", "alloy", "temper", "property_class", "alloy_temper"),
    "finish": ("finish", "coating", "surface", "surface_finish", "treatment"),
    "qty": ("qty", "quantity", "qty_per_pod", "count"),
    "mass": ("mass_kg", "mass", "kg", "kg_each", "weight_kg", "unit_mass_kg", "mass_each_kg", "weight"),
    "mass_total": ("mass_total_kg", "kg_total", "total_mass_kg", "mass_total"),
    "status": ("status", "number_status", "mass_status"),
    "source": ("source", "sources", "source_file", "source_doc"),
    "rev": ("rev", "revision"),
    "class": ("class", "part_class", "type", "kind", "row_type", "make_buy"),
    "maker": ("maker", "manufacturer", "brand", "supplier_brand"),
    "sku": ("sku", "maker_pn", "mpn", "catalog", "catalogue", "maker_part_number", "order_code"),
    "size": ("size", "thread", "thread_size", "nominal_size"),
    "length": ("length_mm", "length", "bolt_length", "len_mm"),
    "torque": ("torque_nm", "torque", "tightening_torque", "torque_n_m"),
    "parent": ("parent", "parent_pn", "assembly", "parent_part_number", "used_in"),
    "location": ("location", "position", "position_code", "where"),
}
NAME_RE = re.compile(r"^(POD|BASE|WALL|FRONT|CEILING|LINING|AIR|ELECTRICAL|INTERIOR|PACKAGING|HARDWARE|SEALS) - \S")
STATUS_WORDS = ("confirmed", "source", "calculation", "assumption", "unverified", "measured", "draft", "hold",
                "review", "decided", "proposed")
GRADE_HINT = re.compile(r"\d|\b(A2|A4|ABS|PET|PE|PVC|EPDM|PU|PUR|ACP|MDF|HPL|LVL|felt|glass|toughened|laminat)\b",
                        re.I)
FINISH_WORDS = re.compile(r"anodi[sz]|powder|paint|galvani|zinc|\bzn\b|plated|passivat|black oxide|e-?coat|mill finish|"
                          r"\braw\b|natural|lacquer|PVDF|coated|polished|brushed|as supplied|bare|self.colou?r|\bRAL\s*\d|"
                          r"\bblack\b|\bwhite\b|\bgr[ae]y\b|colou?r|\bclear\b|ground|arris|seamed|\+Z\d|Z275|Z140|Z100|"
                          r"\bEV\d{3,}\b", re.I)          # EV3038: the ACP's factory coil coating colour

VAGUE_FINISH = re.compile(r"finish (to )?match|as (the )?(base band|v1)|tbd|to be (set|decided|confirmed)", re.I)


def _norm_key(k):
    return re.sub(r"[^a-z0-9]+", "_", (k or "").strip().lower()).strip("_")


def normalise(row):
    nk = {_norm_key(k): (v or "").strip() for k, v in row.items() if k is not None}
    out = {}
    for field, names in ALIASES.items():
        for n in names:
            if n in nk and nk[n] != "":
                out[field] = nk[n]
                break
        else:
            out.setdefault(field, "")
    out["_raw"] = nk
    if not out["mass"] and out.get("mass_total"):          # a row that gives only its total mass
        q = num(out["qty"]) or 1.0
        t = num(out["mass_total"])
        if t is not None and q > 0:
            out["mass"] = "%g" % (t / q)
    return out


def is_placeholder(row):
    """A master BOM row that stands in for an item not yet in any parts list ('register only'), or one copied
    from a team's parts list, which is checked in that list itself."""
    raw = row.get("_raw", {})
    rtype = (raw.get("row_type") or "").lower()
    note = (raw.get("note") or raw.get("notes") or "").lower()
    src = (raw.get("source_file") or "").split(" @ ")[0].strip()      # 'path.csv @ working tree' since #122
    return ("register only" in rtype or "not in any parts list" in note
            or (src.startswith("v2/03-Manufacturing/") and src.endswith(".csv")))


def is_master(path):
    return "/04-BOM/" in path.replace("\\", "/") and "MASTER" in os.path.basename(path).upper()


def find_parts_lists(root):
    """CSV files under 03-Manufacturing, 04-BOM and 02-Drawings with a
    part-number column."""
    out = []
    for top in ("v2/03-Manufacturing", "v2/04-BOM", "v2/02-Drawings", "v2/01-CAD-Native"):
        for p in walk_files(root, top, exts=(".csv",)):
            if "/skeleton/" in rel(root, p):
                continue          # the skeleton parameter table is not a parts list
            if "/04-BOM/" in "/" + rel(root, p) and "MASTER" not in os.path.basename(p).upper():
                continue          # the master BOM's generated views (bought parts, made parts by process) copy it
            try:
                rows = read_csv(p)
            except (UnicodeDecodeError, OSError):
                continue
            if not rows:
                continue
            keys = {_norm_key(k) for k in rows[0].keys() if k}
            if keys & set(ALIASES["part_number"]) and keys & set(ALIASES["qty"]):
                out.append((p, [normalise(r) for r in rows]))
    return out


# ----------------------------------------------------------------- C06 / C11 / C07

def check_parts_lists(root, plists):
    fs = []
    reserved = reserved_spaces(root)    # reserved air spaces: no mass, no drawing, no BOM count (the Lead's ruling)
    seen = defaultdict(list)     # pn -> [(file, name)]
    for p, rows in plists:
        r = rel(root, p)
        for i, row in enumerate(rows, start=2):
            pn = row["part_number"]
            if pn in reserved:
                continue            # only holds space; listed open under its designer by the drawing check
            name = row["name"]
            owner = owner_for(r, pn)
            subj = "%s (%s line %d)" % (pn or "no part number", os.path.basename(r), i)
            rtype = (row["_raw"].get("row_type") or "").lower()
            if not pn and rtype in ("assembly", "pod", "group", "heading", "family"):
                continue            # a master BOM heading row, not a part
            if is_master(r) and is_placeholder(row):
                if pn:
                    seen[pn].append((r, name))      # still counts for duplicate numbers
                continue            # its details live in the register or the team's own parts list
            if not pn and (row["class"] or "").lower() == "cut":
                continue            # a cut-length member of a made frame: the frame's drawing and cut list define it
            if not pn:
                fs.append(Finding("C06", "no-part-number", "%s line %d" % (r, i), "major",
                                  "Row %d of %s has no part number (%s)." % (i, r, name or "no name"),
                                  "Give it a number from conventions section 6.", r, owner))
                continue
            seen[pn].append((r, name))
            for prob in pn_problems(pn):
                fs.append(Finding("C06", "bad-part-number", pn, "severe" if "D-28" in prob else "major",
                                  "Part number %s in %s: %s." % (pn, r, prob),
                                  "Use a new number in the right family band (conventions section 6).", r, owner))
            cls = pn_class(pn)
            missing = []
            if not NAME_RE.match(name or "") and not (pn_class(pn) == "assembly" and pn[2:] == "0000"):
                fs.append(Finding("C06", "name-pattern", pn, "minor",
                                  "%s name '%s' doesn't follow [ASSEMBLY] - [FUNCTION] - [LOCATION] - [VARIANT] "
                                  "(conventions section 5)." % (pn, name), "Rename it to the pattern.", r, owner))
            if not row["name_vi"]:
                missing.append("Vietnamese name")
            if num(row["qty"]) is None or num(row["qty"]) <= 0:
                missing.append("quantity")
            summed = cls == "assembly" and re.search(r"\bsum\b", row["_raw"].get("mass_status") or "", re.I)
            if (num(row["mass"]) is None or num(row["mass"]) <= 0) and not summed:
                missing.append("mass")      # an assembly's mass may be the sum of its listed parts, 0 until listed
            if not row["status"]:
                missing.append("status")
            if not row["source"]:
                missing.append("source")
            if missing:
                sev = "major" if ("quantity" in missing or "mass" in missing) else "minor"
                if re.search(r"\bHOLD\b", row["status"] or "") or re.search(r"\bHOLD\b", name or ""):
                    sev = "minor"           # a held item's data comes with its release
                fs.append(Finding("C06", "row-incomplete", pn, sev,
                                  "%s %s in %s is missing: %s." % (pn, name, r, ", ".join(missing)),
                                  "Fill them in, each number with its status and source.", r, owner))
            # C11: material grade and finish on every part and bought item (assemblies inherit).
            # A bought item named by maker and exact SKU carries its material and finish in the SKU;
            # a HOLD item gets them when it is released.
            held = bool(re.search(r"\bHOLD\b", row["status"] or ""))       # the status column only, whole word
            sku_named = bool(row["sku"])                                     # the SKU column only
            if (cls == "part" or (cls == "bad" and pn) or (cls == "bought" and not sku_named)) and not held:
                mat = " ".join(x for x in (row["material"], row["grade"]) if x)
                fin_text = row["finish"] or row["material"] or ""
                if re.search(r"glass|laminat", mat, re.I):      # a glass part's finish is its edge work
                    fin = re.search(r"ground|polish|arris|seamed|edge", fin_text, re.I)
                elif is_soft(name, ("FILL", "FOAM", "GASKET", "SEAL", "TAPE")):   # hidden soft goods: no finish
                    fin = True
                elif is_soft(name, ("FELT",)):                    # the felt's finish is its colour
                    fin = re.search(r"gr[ae]y|black|white|colou?r|RAL|\bdark\b", fin_text, re.I)
                else:
                    fin = FINISH_WORDS.search(fin_text) and not VAGUE_FINISH.search(fin_text)
                lacks = []
                if not mat:
                    lacks.append("material")
                elif not GRADE_HINT.search(mat):
                    lacks.append("material grade (a named grade or alloy and temper, not just a family)")
                if not fin:
                    if re.search(r"glass|laminat", mat, re.I):
                        lacks.append("edge finish for the glass (ground, polished, arrised)")
                    elif is_soft(name, ("FELT",)):
                        lacks.append("felt colour (plan VT03-PET: Dark Gray)")
                    elif VAGUE_FINISH.search(fin_text):
                        lacks.append("finish (it says only '%s')" % VAGUE_FINISH.search(fin_text).group(0))
                    else:
                        lacks.append("finish")
                if lacks:
                    fs.append(Finding("C11", "material-finish", pn, "major",
                                      "%s %s in %s has no %s. Material given: '%s'." % (
                                          pn, name, r, " and no ".join(lacks), mat or "nothing"),
                                      "State the material grade (for example EN AW-6063 T6, DX51D+Z275, A2-70) and "
                                      "the finish (for example anodised 15 um, powder coat RAL ..., zinc plated, "
                                      "mill finish) in the parts list and on the drawing.", r, owner))
            if cls == "bought" and not (row["maker"] and row["sku"]) and not held:
                fs.append(Finding("C06", "bought-no-sku", pn, "major",
                                  "%s %s in %s is a bought item with no maker and exact SKU, and it isn't marked "
                                  "HOLD (guideline section 4.2)." % (pn, name, r),
                                  "Give maker and exact SKU with its source document, or mark it HOLD with the "
                                  "issue that releases it.", r, owner))
            if is_fastener(pn, name):
                fs.extend(_fastener_row(r, pn, name, row, owner))
    fs = _fold_unnumbered(_fold_minor_rows(fs))
    reg = register_names(root)
    for pn, uses in seen.items():
        # the same words in the same order are one name: 'HOOK-AND-LOOP' and 'HOOK AND LOOP' don't differ
        names = {name_words(n) for _f, n in uses}
        if len(names) > 1:
            # which name is right: the joints register's for hardware (D-99); the Joints Engineer's own list for the
            # base keys (D-95); else the name the team lists agree on. The master BOM copies the team lists, so a
            # name only it differs on means it needs a rebuild (the PM's).
            team = [(f, n) for f, n in uses if not is_master(f)]
            if pn in reg:
                ref, why = reg[pn], " The joints register names it '%s' (D-99)." % reg[pn]
            elif JOINTS_KEYS.match(pn) and any("/joints/" in f for f, _n in team):
                ref = next(n for f, n in team if "/joints/" in f)
                why = " The Joints Engineer's list names it '%s', and the teams place the keys by reference (D-95)." % ref
            elif team and len({name_words(n) for _f, n in team}) == 1:
                ref, why = team[0][1], ""
            else:
                ref, why = None, ""
            off = [(f, n) for f, n in uses if ref is not None and name_words(n) != name_words(ref)] or uses
            if ref is not None and all(is_master(f) for f, _n in off):
                owner, fix = "Control", "Rebuild the master BOM from the team lists (v2/04-BOM/build_master_bom.py)."
            elif ref is not None:
                f0 = next(f for f, _n in off if not is_master(f))
                owner = owner_for(f0, "" if JOINTS_KEYS.match(pn) else pn)
                fix = "Use '%s' in %s." % (ref, ", ".join(sorted({f for f, _n in off})))
            else:
                owner = owner_for(uses[0][0], pn)
                fix = "One number is one form, fit and function (conventions section 6)."
            fs.append(Finding("C06", "duplicate-number", pn, "major",
                              "Part number %s is used for different names: %s.%s" % (
                                  pn, "; ".join("'%s' in %s" % (n, f) for f, n in uses), why),
                              fix, off[0][0], owner))
    return fs


def _fold_unnumbered(fs):
    """One finding per file for rows with no part number yet (often bought hardware waiting for its numbers)."""
    keep, groups = [], {}
    for f in fs:
        if f.check == "C06" and f.rule == "no-part-number":
            groups.setdefault(f.file, []).append(f)
        else:
            keep.append(f)
    for file, items in groups.items():
        what = "; ".join(re.sub(r"^Row \d+ of .*? has no part number \((.*)\)\.$", r"\1", x.message) for x in items)
        keep.append(Finding("C06", "no-part-number", "%s: %d rows" % (os.path.basename(file), len(items)), "major",
                            "%d rows of %s have no part number: %s." % (len(items), file, what),
                            "Give each a number from conventions section 6 (bought hardware: family 83 or 84, from the "
                            "joints register and the master BOM).", file, items[0].owner))
    return keep


def _fold_minor_rows(fs):
    """One finding per file for minor gaps in its rows (missing Vietnamese name, status or source), so a
    generated list with the same gap on every row reads as one item to fix."""
    keep, groups = [], {}
    for f in fs:
        if f.check == "C06" and f.rule == "row-incomplete" and f.severity == "minor":
            gap = f.message.split("is missing: ", 1)[-1].rstrip(".")
            groups.setdefault((f.file, gap), []).append(f)
        else:
            keep.append(f)
    for (file, gap), items in groups.items():
        if len(items) == 1:
            keep.append(items[0])
            continue
        pns = ", ".join(x.subject for x in items)
        keep.append(Finding("C06", "rows-incomplete", "%s: %s" % (os.path.basename(file), gap), "minor",
                            "%d rows of %s are missing: %s (%s)." % (len(items), file, gap, pns),
                            "Fill them in (the assembly tree has the Vietnamese names of the families).", file,
                            items[0].owner))
    return keep


def _fastener_row(r, pn, name, row, owner):
    """What a fastener row must state depends on its kind: a bolt, screw or stud its thread, length, grade,
    finish and torque; a nut, rivnut or insert its thread, grade, finish and torque (a rivnut's torque may be
    HOLD with its test, D-48); a washer or retainer its grade and finish; all of them maker and SKU."""
    lacks = []
    up = (name or "").upper()
    threaded = re.search(r"\b(BOLT|SCREW|STUD)\b", up)
    nutlike = re.search(r"\b(NUT|RIVNUT|RIVET NUT|INSERT|CLINCH)\b", up)
    if not (threaded or nutlike):
        # washers, retainers, spigots and the like: grade, finish, maker and SKU only
        lacks = []
        if not (row["grade"] or GRADE_HINT.search(row["material"] or "")):
            lacks.append("grade")
        if not (row["finish"] or FINISH_WORDS.search((row["material"] or "") + " " + (name or ""))):
            lacks.append("finish")
        if pn_class(pn) == "bought" and not (row["maker"] and row["sku"]):
            lacks.append("maker and SKU")          # a part we make has a drawing instead
        return [] if not lacks else [Finding("C07", "fastener-spec", pn, "major",
                                             "Hardware item %s %s in %s has no %s." % (pn, name, r, ", no ".join(lacks)),
                                             "Complete the row (guideline section 4.2).", r, owner)]
    if not (row["size"] or re.search(r"\bM\d+(\.\d+)?\b", name or "")):
        lacks.append("thread size")
    if threaded and not (row["length"] or re.search(r"\bM\d+\s*[x×]\s*\d+", name or "", re.I)):
        lacks.append("length")
    if not (row["grade"] or re.search(r"\b(4\.6|5\.6|8\.8|10\.9|12\.9|A2|A4|A2-70|A4-70|A4-80|steel|stainless|"
                                       r"alumin)", (row["material"] or "") + " " + (name or ""), re.I)):
        lacks.append("grade or property class")
    if not (row["finish"] or FINISH_WORDS.search((row["material"] or "") + " " + (name or ""))):
        lacks.append("finish")
    tq = row["torque"]
    if not tq:
        lacks.append("torque (or HOLD with its test, as D-48 does for the rivnuts)")
    if pn_class(pn) == "bought" and not (row["maker"] and row["sku"]):
        lacks.append("maker and SKU")
    if not lacks:
        return []
    return [Finding("C07", "fastener-spec", pn, "major",
                    "Fastener %s %s in %s has no %s." % (pn, name, r, ", no ".join(lacks)),
                    "Complete the row: size, length, grade, finish, torque with its basis, maker and SKU "
                    "(guideline sections 4.2 and 8.1).", r, owner)]


def fastener_schedule(root, plists, step_usage):
    """Rows for v2/04-Checks/fastener-schedule.csv. step_usage: pn ->
    [(file, count, [paths])]."""
    rows = []
    for p, plrows in plists:
        r = rel(root, p)
        for row in plrows:
            if not is_fastener(row["part_number"], row["name"]):
                continue
            pn = row["part_number"]
            cad = step_usage.get(pn, [])
            rows.append({
                "part_number": pn, "name": row["name"], "size": row["size"], "length_mm": row["length"],
                "grade": row["grade"] or row["material"], "finish": row["finish"], "torque_nm": row["torque"],
                "qty_parts_list": row["qty"], "qty_cad": sum(c for _f, c, _p in cad) if cad else "",
                "where_cad": "; ".join(sorted({x for _f, _c, ps in cad for x in ps}))[:500],
                "maker": row["maker"], "sku": row["sku"], "status": row["status"], "parts_list": r,
                "engagement": "not measured yet (Fusion check)"})
    return rows


# ----------------------------------------------------------------- CAD match (C06)

def _group(path):
    """The team folder a file sits in: 'v2/03-Manufacturing/wall/x.step' gives 'wall'."""
    parts = (path or "").replace("\\", "/").split("/")
    return parts[2] if len(parts) > 3 and parts[0] == "v2" else ""


def check_cad_match(root, plists, step_products):
    """step_products: pn -> {"files": set, "count": int, "name": str}."""
    fs = []
    listed = {row["part_number"] for _p, rows in plists for row in rows if row["part_number"]}
    for pn, info in sorted(step_products.items()):
        if not re.match(r"^\d{6}$", pn):
            continue
        if pn not in listed:
            f = sorted(info["files"])[0]
            fs.append(Finding("C06", "cad-not-in-bom", pn, "major",
                              "%s %s is in the CAD (%s) but in no parts list." % (pn, info["name"], f),
                              "Add it to the parts list, or remove it from the CAD.", f, owner_for(f, pn)))
    names = {}
    for p, rows in plists:
        for row in rows:
            if row["part_number"]:
                names.setdefault(row["part_number"], (row["name"], rel(root, p)))
    norm = name_words
    reg = register_names(root)          # D-99: hardware names come from the joints register
    for pn, info in sorted(step_products.items()):
        if (pn not in names and pn not in reg) or not re.match(r"^\d{6}$", pn):
            continue
        cad = re.sub(r"^%s\s+" % pn, "", info["name"] or "")
        cad = re.sub(r"\s*\(\d+\)$", "", cad)            # Fusion's '(1)' copy suffix
        if not cad or re.match(r"^\d{6}_[PR]\d{2}_", cad):
            continue
        f = sorted(info["files"])[0]
        if pn in reg:
            ref = reg[pn]
            # the CAD may add a position code to the register's name (368101 '... - HOLD - H1 BOTTOM')
            wrong = ["the CAD"] if not (norm(cad) == norm(ref) or norm(cad).startswith(norm(ref) + " ")) else []
            if pn in names and norm(names[pn][0]) != norm(ref):
                wrong.append("the parts list (%s)" % names[pn][1])
            if wrong:
                fs.append(Finding("C06", "name-mismatch", pn, "minor",
                                  "%s is named '%s' in the CAD%s; the joints register names it '%s', and hardware names "
                                  "come from the register (D-99)." % (
                                      pn, cad, " and '%s' in %s" % (names[pn][0], names[pn][1]) if pn in names else "", ref),
                                  "Use the register's name in %s." % " and ".join(wrong), f, owner_for(f, pn)))
            continue
        same = norm(cad) == norm(names[pn][0]) or norm(cad).startswith(norm(names[pn][0]) + " ")  # + a position code
        if not same:
            fs.append(Finding("C06", "name-mismatch", pn, "minor",
                              "%s is named '%s' in the CAD (%s) but '%s' in the parts list (%s); the guideline wants one "
                              "name everywhere (section 4.2)." % (pn, cad, f, names[pn][0], names[pn][1]),
                              "Use the same name in the CAD component and the parts list.", f, owner_for(f, pn)))
    # A team's parts list is matched against the CAD once that team has exported STEP files (its folder,
    # e.g. v2/03-Manufacturing/wall). The master BOM lists every team's parts, so it isn't matched itself:
    # each row is checked in its team's own list.
    step_groups = {_group(f) for info in step_products.values() for f in info["files"]}
    for p, rows in plists:
        r = rel(root, p)
        if is_master(r) or _group(r) not in step_groups:
            continue
        for row in rows:
            pn = row["part_number"]
            if pn_class(pn) in ("part", "assembly") and pn not in step_products:
                fs.append(Finding("C06", "bom-not-in-cad", pn, "major",
                                  "%s %s is in %s but in no STEP file in v2/03-Manufacturing." % (pn, row["name"], r),
                                  "Export its STEP from the native CAD (same revision), or take it off the list.", r,
                                  owner_for(r, pn)))
    return fs


# ----------------------------------------------------------------- C04 shipping

PALLETS = {
    # name: (length, width, max piece height) mm; height = 1829 loaded - 150 deck (REQ-SHP-01, REQ-SHP-03)
    "48x40": (1219.0, 1016.0, 1679.0),
    "48x96": (2438.0, 1219.0, 1679.0),
    # the layout study's packer puts every 'box' piece in one kit carton, 2400 long, on the long pallet
    # whenever the build has one (layout-study scripts/pallets.py: carton_for; the long flat kit carton);
    # its cross-section is the free width of a layer (600 when it gets its own layer) by the layer height
    "kit-carton": (2400.0, 600.0, 1679.0),
}


def _fits(dims, pallet):
    L, W, H = PALLETS[pallet]
    a, b, c = dims
    for x, y, z in ((a, b, c), (a, c, b), (b, a, c), (b, c, a), (c, a, b), (c, b, a)):
        if x <= L + 1e-6 and y <= W + 1e-6 and z <= H + 1e-6:
            return True
    return False


def load_shipping_list(root):
    """The pieces that ship on their own: the packing list in v2/07-Packaging when it exists (each row with
    its pallet, size and mass), else the layout study's list of the decided build. Rows are normalised to
    id, name, size_mm, kg_each, ships_as, status."""
    pk = sorted(walk_files(root, "v2/07-Packaging", exts=(".csv",)))
    pk = [p for p in pk if "PACKING-LIST" in os.path.basename(p).upper()]
    if pk:
        types = {}
        for f in walk_files(root, "v2/07-Packaging", exts=(".svg", ".md", ".pdf")):
            m = re.search(r"PALLET-(\d+)-(48X40|96X48|48X96)", os.path.basename(f).upper())
            if m:
                types[m.group(1)] = "48x40" if m.group(2) == "48X40" else "48x96"
        rows = []
        for r in read_csv(pk[0]):
            glass = (r.get("glass") or "").strip().lower() in ("yes", "y", "true", "1")
            pal = types.get((r.get("pallet") or "").strip(), "")
            rows.append({"id": r.get("label") or r.get("part_number", ""), "name": r.get("name", ""),
                         "size_mm": r.get("size_mm", ""), "kg_each": r.get("kg", ""),
                         "ships_as": "glass" if glass else ("long" if pal == "48x96" else "upright"),
                         "pallet": pal, "status": r.get("kg_status", ""), "assembly": (r.get("name") or "").split(" - ")[0]})
        return rel(root, pk[0]), rows
    p = os.path.join(root, "v2/05-Engineering/layout-study/out/parts-option-B1-final-stack.csv")
    if not os.path.exists(p):
        return None, []
    return rel(root, p), read_csv(p)


MASS_LISTS = ("v2/05-Engineering/layout-study/out/parts-decided-P04.csv",          # newest first
              "v2/05-Engineering/layout-study/out/parts-option-B1-final-stack.csv")


def load_mass_list(root):
    """The layout study's newest decided part list with masses: (repo path, rows)."""
    for r in MASS_LISTS:
        p = os.path.join(root, r)
        if os.path.exists(p):
            return r, read_csv(p)
    return None, []


def load_adjustments(root, list_path=None):
    """Owners' weight changes not yet in the given part list (column applies_to names the list)."""
    p = os.path.join(root, "v2/04-Checks/config/mass-adjustments.csv")
    rows = read_csv(p) if os.path.exists(p) else []
    if list_path:
        rows = [a for a in rows if not a.get("applies_to") or os.path.basename(list_path) == a["applies_to"]]
    return rows


def check_pod_mass(root, rows, src, cap_kg=420.0):
    """The pod total from the layout study's part list (every row, as it sums
    them) plus the owners' weight changes not yet in that list, against the
    cap (D-37, D-54)."""
    if not rows:
        return [], None
    # the PM's weight ruling of 2026-10-31: the voice cockpit kit (4.0 kg, shipped later) sits outside the cap
    outside = [r for r in rows if re.search(r"outside the cap|voice cockpit kit reserve",
                                            " ".join(str(r.get(k) or "") for k in ("item", "name", "status", "note")), re.I)]
    rows = [r for r in rows if r not in outside]
    base = sum(num(r.get("kg_total")) or 0.0 for r in rows)
    adj = load_adjustments(root, src)
    extra = sum(num(a.get("kg")) or 0.0 for a in adj)
    total = base + extra
    outside_kg = sum(num(r.get("kg_total")) or 0.0 for r in outside)
    info = {"list_kg": round(base, 2), "adjustments": adj, "total_kg": round(total, 2), "cap_kg": cap_kg,
            "outside_cap_kg": round(outside_kg, 2)}
    if total <= cap_kg + 1e-6:
        return [], info
    parts = "; ".join("%+.1f kg %s (%s, %s)" % (num(a["kg"]), a["id"], a["status"], a["source"]) for a in adj)
    return [Finding("C04", "pod-mass-over-cap", "POD total mass", "major",
                    "The pod is about %.1f kg against the %.0f kg cap (D-37, D-54): %.1f kg over. The layout study's "
                    "list gives %.1f kg (%s)%s%s. Open against the cap until the wall sample settles it (ISS-080)." % (
                        total, cap_kg, total - cap_kg, base, src, "; adjustments since: " + parts if parts else "",
                        "; %.1f kg of voice cockpit kit is outside the cap (PM weight ruling)" % outside_kg
                        if outside_kg else ""),
                    "Find the weight, or the PM rules on the cap after the wall sample (D-54: the 25 kg/m3 fill "
                    "would save 4.3 kg).", src, "PM (Lead)", {"total_kg": round(total, 2), "cap_kg": cap_kg})], info


def check_shipping(root, door=(914.0, 2032.0), door_req=(810.0, 2032.0), limit_kg=20.0):
    fs = []
    src, rows = load_shipping_list(root)
    report = []
    for row in rows:
        sid = row.get("id", "")
        name = row.get("name", "")
        ships = (row.get("ships_as") or "").strip().lower()
        if ships == "none":
            continue
        dims = [num(x) for x in re.split(r"\s*[x×]\s*", row.get("size_mm") or "") if num(x) is not None]
        kg = num(row.get("kg_each"))
        status = row.get("status", "")
        glass = ships == "glass" or "GLASS" in name.upper()
        line = {"id": sid, "name": name, "kg": kg, "dims": dims, "ships_as": ships, "status": status}
        report.append(line)
        owner = owner_for(src)          # the shipping list is the layout study's
        if kg is not None and kg > limit_kg + 1e-6 and not glass:
            fs.append(Finding("C04", "mass-over-20kg", sid, "severe",
                              "%s %s weighs %.2f kg (%s, %s), over the 20 kg rule (D-03)." % (sid, name, kg, status,
                                                                                            src),
                              "Split the piece or take weight out so one person can carry it.", src, owner))
        if len(dims) == 3:
            a, b, c = sorted(dims)
            if a > door[0] + 1e-6 or b > door[1] + 1e-6:
                fs.append(Finding("C04", "doorway", sid, "severe",
                                  "%s %s (%s mm) doesn't pass a %g x %g mm doorway: its two smallest sizes are "
                                  "%g and %g (PLAN Target 2)." % (sid, name, row.get("size_mm"), door[0], door[1], a, b),
                                  "Split it or change its shape.", src, owner))
            elif a > door_req[0] + 1e-6:
                fs.append(Finding("C04", "doorway-810", sid, "minor",
                                  "%s %s passes 914 x 2032 but not the 810 mm door of REQ-ASM-06 (PROPOSED): its "
                                  "smallest size is %g." % (sid, name, a), "PM to confirm which door rule holds.",
                                  src, owner))
            has_long = any((r.get("ships_as") or "").strip().lower() in ("long", "glass") for r in rows)
            want = row.get("pallet") or ("48x96" if ships in ("long", "glass") else
                                         ("kit-carton" if ships == "box" and has_long else "48x40"))
            if not _fits(dims, want):
                other = "48x40" if want != "48x40" else "48x96"
                fs.append(Finding("C04", "pallet-fit", sid, "major" if _fits(dims, other) else "severe",
                                  "%s %s (%s mm) doesn't fit the %s pallet it ships on (%g x %g, at most %g tall "
                                  "loaded above a 150 mm deck)%s." % (
                                      sid, name, row.get("size_mm"), want, *PALLETS[want],
                                      "; it fits the %s pallet" % other if _fits(dims, other) else
                                      "; it fits no standard pallet"),
                                  "Move it to the right pallet in the layout study, or change the piece.", src, owner))
    msrc, mrows = load_mass_list(root)
    mass_fs, _info = check_pod_mass(root, mrows, msrc)
    # the 20 kg rule also on the newest list, which has no sizes (glass exempt, D-03)
    if msrc and msrc != src:
        for row in mrows:
            kg = num(row.get("kg_each"))
            item = row.get("item") or row.get("name") or ""
            if kg is not None and kg > limit_kg + 1e-6 and not re.search(r"glass|door unit", item, re.I):
                fs.append(Finding("C04", "mass-over-20kg", item[:60], "severe",
                                  "%s weighs %.2f kg (%s, %s), over the 20 kg rule (D-03)." % (
                                      item, kg, row.get("status", ""), msrc),
                                  "Split the piece or take weight out so one person can carry it.", msrc,
                                  owner_for(msrc)))
    return fs + mass_fs, report, src


def _family_of(row):
    a = (row.get("assembly") or "").upper()
    return {"BASE": "11", "WALL": "21", "FRONT": "35", "CEILING": "41", "LINING": "51", "AIR": "61",
            "ELECTRICAL": "71"}.get(a, "")


# ----------------------------------------------------------------- C10 mixed metals

def metal_class(text):
    t = (text or "").lower()
    if not t:
        return "unknown"
    if re.search(r"stainless|\ba2\b|\ba4\b|a2-|a4-|304|316", t):
        return "stainless"
    if re.search(r"alumin|\bal\b|en aw|6063|6061|6082|5052|5754|5083|3003|acp", t):
        return "aluminium"
    if re.search(r"steel|\bst\b|dx51|sgcc|dc01|spcc|s235|s275|8\.8|10\.9|12\.9|4\.6|5\.6|iron", t):
        if re.search(r"galv|zinc|\bzn\b|plated|powder|paint|e-?coat|coated|z275|z140|z100|geomet|dacromet|"
                     r"black oxide", t):
            return "steel-coated"
        return "steel-bare"
    return "other"


def check_mixed_metals(root, plists, contacts):
    """contacts: list of (pn_a, pn_b, file) for parts whose boxes touch in
    the assembled CAD."""
    fs = []
    mat = {}
    for _p, rows in plists:
        for row in rows:
            if row["part_number"]:
                mat[row["part_number"]] = " ".join(x for x in (row["material"], row["grade"], row["finish"]) if x)
    for p, rows in plists:
        r = rel(root, p)
        for row in rows:
            pn = row["part_number"]
            if is_master(r) and is_placeholder(row):
                continue            # checked in the register or the team's own parts list
            own = " ".join(x for x in (row["material"], row["grade"], row["finish"]) if x)
            if not pn:
                mat[""] = own
            if metal_class(mat.get(pn, "")) == "unknown" and metal_class(row["name"]) != "unknown":
                mat[pn] = row["name"]           # e.g. 'ISO 4762 8.8 ZINC' in the name
            if is_fastener(pn, row["name"]) and metal_class(mat.get(pn, "")) == "unknown":
                fs.append(Finding("C10", "fastener-metal-unknown", pn, "major",
                                  "Fastener %s %s in %s has no material or finish, so it can't be checked against "
                                  "the aluminium it touches." % (pn, row["name"], r),
                                  "Give material and finish (stainless A2, or zinc-plated steel).", r,
                                  owner_for(r, pn)))
            elif is_fastener(pn, row["name"]) and metal_class(mat.get(pn, "")) == "steel-bare":
                fs.append(Finding("C10", "fastener-bare-steel", pn, "severe",
                                  "Fastener %s %s in %s is bare steel ('%s'); the frames are aluminium." % (
                                      pn, row["name"], r, mat.get(pn, "")),
                                  "Use stainless or coated steel, with an isolating washer where the joint stays "
                                  "wet.", r, owner_for(r, pn)))
    seen = set()
    for a, b, f in contacts:
        ca, cb = metal_class(mat.get(a, "")), metal_class(mat.get(b, ""))
        pair = tuple(sorted((a, b)))
        if pair in seen:
            continue
        seen.add(pair)
        if {ca, cb} == {"steel-bare", "aluminium"}:
            fs.append(Finding("C10", "bare-steel-on-aluminium", "%s x %s" % pair, "major",
                              "%s (%s) and %s (%s) touch in the assembled CAD (boxes touch; the Fusion check "
                              "confirms contact): bare steel against aluminium corrodes." % (
                                  a, mat.get(a, ""), b, mat.get(b, "")),
                              "Coat the steel part (zinc, powder) or separate them with an isolating layer.", f,
                              owner_for(f, a)))
    return fs
