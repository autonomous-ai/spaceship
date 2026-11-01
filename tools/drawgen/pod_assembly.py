"""GA sheet 1: the whole pod, 100000, as one assembly sheet drawn from the teams' STEPs (D-158; the PM's rulings of
2026-11-01). Run it in drawgen's environment (tools/drawgen/run.sh makes it):

    <venv>/bin/python tools/drawgen/pod_assembly.py generate      # v2/02-Drawings/00-General-Assembly/, read back
    <venv>/bin/python tools/drawgen/pod_assembly.py check v2/02-Drawings/00-General-Assembly/100000_*_DWG.pdf

The pod has no STEP of its own. Its parts are the teams' assembly STEPs, all in pod coordinates: every STEP under
v2/03-Manufacturing, the skeleton's folder left out, whose top part has an assembly number (conventions section 6),
the set the whole-pod mechanical check reads (tools/checks/run_fusion_checks.py, pick_steps). Each file's top part is
drawn as part of its first-level assembly in the master BOM (210101 under 210000 WALL, 350001 under 350000 FRONT -
DECOR), so the items are the pod's first-level assemblies; the parts table is the master BOM's first-level rows that
have a part number, less the entry's leave_out (the packaging 910000 isn't on the pod as it stands). A first-level row
no STEP has yet gets its row with a * and no balloon, as the assembly mode does.

The sheet itself is the assembly mode's (tools/drawgen/assembly.py, the Air Engineer's): its views, sections, balloons,
table, sizes, notes and title block, through make()'s hook for an assembly built elsewhere. This file adds the reading
of the pod and its own read-back, against the same STEPs and the master BOM (assembly.check reads one STEP and one
team list). The entry is POD in tools/drawgen/teams/ga.py. The drawing takes the skeleton's revision (the pod's own
number, 100000, revised as the skeleton is) and the date of its newest STEP.
"""

import csv
import glob
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import assembly as A  # noqa: E402
import geom  # noqa: E402
import inputs  # noqa: E402
from compose import NotDrawable  # noqa: E402
from geom import vdot, vsub  # noqa: E402

POD_PN = "100000"
TEAM = "ga"                               # the GA's folder under v2/02-Drawings is 00-General-Assembly
MASTER_REL = "v2/04-BOM/100000_P01_POD-MASTER_BOM.csv"
OUT_REL = "v2/02-Drawings/00-General-Assembly"
SKELETON_DIR = "skeleton"


def _checks(name):
    """A module of the repo's own checks (tools/checks): stepfile (the STEP reader without OCC), common."""
    p = os.path.join(inputs.REPO, "tools", "checks")
    if p not in sys.path:
        sys.path.insert(0, p)
    return __import__(name)


def pod_steps(root=None):
    """The whole pod's STEPs, sorted: every STEP under v2/03-Manufacturing, the skeleton's folder left out, whose top
    part has an assembly number (conventions section 6), as the whole-pod check picks them."""
    root = root or inputs.MANUF
    stepfile, common = _checks("stepfile"), _checks("common")
    out = []
    for p in sorted(glob.glob(os.path.join(root, "*", "*.step")) + glob.glob(os.path.join(root, "*", "*.stp"))):
        if os.path.basename(os.path.dirname(p)) == SKELETON_DIR:
            continue
        _c, tops = stepfile.StepFile(p).usage_counts()
        if any(common.pn_class(t) == "assembly" for t in tops):
            out.append(p)
    return out


def master_tree(path):
    """(the pod's row, [first-level rows that have a part number], {part number: the part number of its first-level
    assembly}) from the master BOM, whose rows run in tree order with their level (0 the pod)."""
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows or rows[0].get("level") != "0" or (rows[0].get("part_number") or "").strip() != POD_PN:
        raise NotDrawable("%s: its first row is not the pod %s at level 0" % (inputs.rel(path), POD_PN))
    stack, first, up = [], [], {}
    for r in rows:
        lv = int(r["level"])
        pn = (r.get("part_number") or "").strip()
        stack = stack[:lv] + [pn]
        if lv == 1 and pn:
            first.append(r)
        if lv >= 1 and pn and len(stack) > 1 and stack[1]:
            up.setdefault(pn, stack[1])
    return rows[0], first, up


def skeleton_rev(root=None):
    """The skeleton STEP's revision (PN_REV_NAME_STEP.step under the skeleton's folder), newest when several."""
    root = root or inputs.MANUF
    revs = []
    for p in glob.glob(os.path.join(root, SKELETON_DIR, "*_STEP.step")):
        m = inputs.NAME_RE.match(os.path.basename(p))
        if m and m.group(1) == POD_PN:
            revs.append(m.group(2))
    if not revs:
        raise NotDrawable("no skeleton STEP %s_*_STEP.step under %s" % (POD_PN, inputs.rel(os.path.join(root,
                                                                                                      SKELETON_DIR))))
    return sorted(revs)[-1]


def _step_date(path):
    with open(path, encoding="latin-1") as fh:
        m = re.search(r"(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})", fh.read(4000))
    return (m.group(1), m.group(2)) if m else ("", "")


def top_parts(path):
    """[(part number, product name, solids)] for each top part of a team STEP (its free shapes), solids in the
    file's top coordinates (the pod system)."""
    from OCP.TDF import TDF_LabelSequence
    _doc, st = A._xcaf(path)
    tops = TDF_LabelSequence()
    st.GetFreeShapes(tops)
    out = []
    for i in range(1, tops.Length() + 1):
        lab = tops.Value(i)
        name = A._label_name(lab)
        out.append((geom.part_number_of(name), name, A._solids_of(st.GetShape_s(lab))))
    return out


class PodAssy(A.Assy):
    """The pod as the assembly mode's Assy: its items are the master BOM's first-level assemblies, each with the top
    parts of the team STEPs that fall under it."""

    kind = "pod"

    def __init__(self, pn, team, entry, step=None, master=None, steps=None):     # noqa: D107 (Assy's own fields)
        if pn != POD_PN:
            raise NotDrawable("%s: the pod sheet is %s" % (pn, POD_PN))
        self.pn, self.team, self.entry = pn, team, entry
        self.list_file = master or os.path.join(inputs.REPO, MASTER_REL)
        own, first, up = master_tree(self.list_file)
        leave = set(entry.get("leave_out", ()))
        self.steps = list(steps) if steps is not None else pod_steps()
        if not self.steps:
            raise NotDrawable("%s: no team STEP under v2/03-Manufacturing" % pn)
        self.row = own
        self.name = (own.get("name") or "").strip()
        self.name_vi = (own.get("name_vi") or "").strip()
        self.rev = entry.get("rev") or skeleton_rev()
        self.dwg_name = "%s_%s_%s_DWG" % (pn, self.rev, inputs.ascii_name(self.name))
        # the sheet's date is the newest STEP's (make() reads it from self.step's header)
        self.step = max(self.steps, key=lambda p: (_step_date(p), p))
        by_item, self.files = {}, {}
        for p in self.steps:
            for tpn, name, solids in top_parts(p):
                if tpn is None:
                    raise NotDrawable("%s: %s has a top part without a part number (%s)" % (pn, inputs.rel(p), name))
                item = up.get(tpn)
                if item is None:
                    raise NotDrawable("%s: %s's top part %s isn't under a first-level assembly in %s" % (
                        pn, inputs.rel(p), tpn, inputs.rel(self.list_file)))
                if item in leave:
                    raise NotDrawable("%s: %s's top part %s falls under %s, which the entry leaves out" % (
                        pn, inputs.rel(p), tpn, item))
                by_item.setdefault(item, []).append(A.Occ(item, name, solids))
                self.files.setdefault(item, []).append(inputs.rel(p))
        self.items = []
        for r in first:
            ipn = r["part_number"].strip()
            if ipn in leave:
                continue
            row = dict(r)
            row["qty_per_parent"] = row.get("qty_per_pod", "")   # the table's quantity: each per pod
            self.items.append(A.Item(ipn, row, by_item.get(ipn, [])))
        for n, it in enumerate(self.items, 1):
            it.no = n
        self.occs = [o for it in self.items for o in it.occs]
        self.count_notes = []

    def sources(self):
        """The sheet's sources: every STEP drawn, then the master BOM."""
        return ([{"role": "STEP", "path": inputs.rel(p), "sha256_12": inputs.sha12(p)} for p in self.steps] +
                [{"role": "parts list", "path": inputs.rel(self.list_file), "sha256_12": inputs.sha12(self.list_file)}])


def entry():
    """The GA's entry, POD in tools/drawgen/teams/ga.py."""
    import importlib.util as _ilu
    path = os.path.join(HERE, "teams", "ga.py")
    sp = _ilu.spec_from_file_location("drawgen_pod_entry", path)
    m = _ilu.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m.POD


def make(out_path, conf=None, today=None):
    """Draw the pod's sheet into out_path; returns the assembly mode's report."""
    conf = conf if conf is not None else entry()
    assy = PodAssy(POD_PN, TEAM, conf)
    try:
        return A.make(POD_PN, TEAM, conf, out_path, today=today, assy=assy)
    except TypeError as e:
        if "assy" in str(e):
            raise NotDrawable("assembly.make() takes no built assembly yet (its hook comes with the Air Engineer's "
                              "PR after #350)")
        raise


def generate(out_dir=None, conf=None):
    """Write the sheet as out_dir/PN_REV_NAME_DWG.pdf, never over a PDF drawgen didn't make (a Fusion drawing)."""
    out_dir = out_dir or os.path.join(inputs.REPO, OUT_REL)
    tmp = os.path.join(out_dir, ".drawgen-%s.pdf" % POD_PN)
    os.makedirs(out_dir, exist_ok=True)
    try:
        rep = make(tmp, conf)
        final = os.path.join(out_dir, rep["dwg"] + ".pdf")
        if os.path.exists(final):
            import fitz
            with fitz.open(final) as d:
                if (d.metadata or {}).get("creator") != "drawgen":
                    raise NotDrawable("%s exists and was not made by drawgen (a Fusion drawing): left as it is"
                                      % inputs.rel(final))
        os.replace(tmp, final)
        return final, rep
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


# ------------------------------------------------------------------ the read-back


def _item_parts(steps, up):
    """{first-level part number: [the solids of each team STEP top part under it]}: one list per placed part, as
    the sheet measures an interface point on a placed part's whole box (assembly._ref_point)."""
    out = {}
    for p in steps:
        for tpn, _name, solids in top_parts(p):
            item = up.get(tpn)
            if item:
                out.setdefault(item, []).append(solids)
    return out


def check(pdf_path):
    """Read the pod's sheet back against the team STEPs and the master BOM, independently of how it was drawn:
    the STEPs it names are the whole-pod set today and unchanged since (else draw it again); every table row against
    the master BOM's first-level row (item order, number, name, quantity, material, finish, word for word); every
    balloon's number against the table, its tip where its 3D point projects, an arrowhead or dot there and that point
    in or on its item's solids; every item a STEP has carries a balloon, and a * only where none has; the interface
    ordinates measured again; Creator drawgen, CREATED BY and author Autonomous, no maker line, no text touching text
    or a line. Returns (failures, stats)."""
    import fitz
    import readback
    doc = fitz.open(pdf_path)
    page = doc[0]
    data = readback.read_data(doc)
    fails = []
    stats = {"rows": 0, "balloons": 0, "interfaces": 0, "steps": 0}
    if data.get("kind") != "pod":
        return ["not the pod's sheet (no kind 'pod' in its drawing data)"], stats
    steps = [os.path.join(inputs.REPO, s["path"]) for s in data["sources"] if s["role"] == "STEP"]
    lst = os.path.join(inputs.REPO, [s for s in data["sources"] if s["role"] == "parts list"][0]["path"])
    # 0. the sources: today's whole-pod set, each file as it was drawn
    now = [inputs.rel(p) for p in pod_steps()]
    drawn = [inputs.rel(p) for p in steps]
    for p in sorted(set(now) - set(drawn)):
        fails.append("%s is in the pod's STEPs now but not on the sheet: draw it again" % p)
    for p in sorted(set(drawn) - set(now)):
        fails.append("%s is on the sheet but not in the pod's STEPs now" % p)
    for s in data["sources"]:
        stats["steps"] += s["role"] == "STEP"
        p = os.path.join(inputs.REPO, s["path"])
        if not os.path.exists(p):
            fails.append("source %s is gone" % s["path"])
        elif inputs.sha12(p) != s["sha256_12"]:
            fails.append("source %s changed since the sheet was drawn: draw it again" % s["path"])
    _own, first, up = master_tree(lst)
    leave = set(entry().get("leave_out", ()))       # the sheet's data doesn't hold it; the entry does
    rows = [r for r in first if r["part_number"].strip() not in leave]
    # 1. the table against the master BOM's first-level rows
    tab = A.table_text(page, data)
    if sorted(tab) != list(range(1, len(rows) + 1)):
        fails.append("the table's items %s are not 1 to %d (the master BOM's first-level rows)" % (sorted(tab),
                                                                                                   len(rows)))
    for n, r in enumerate(rows, 1):
        if n not in tab:
            continue
        stats["rows"] += 1
        want = [str(n), r["part_number"].strip(), (r.get("name") or "").strip(), A.qty_text(r.get("qty_per_pod")),
                (r.get("material") or "").strip() or "-", (r.get("finish") or "").strip() or "-"]
        for k, (w, g) in enumerate(zip(want, tab[n][1])):
            if k and " ".join(w.split()) != g:
                fails.append("table item %d %s: '%s' where the master BOM has '%s'" % (n, A.COLS[k][0], g[:60],
                                                                                       w[:60]))
    # 2. balloons, on their items' solids from every STEP
    parts = _item_parts(steps, up)
    solids = {k: [x for sol in v for x in sol] for k, v in parts.items()}
    views = {v["name"]: v for v in data["views"]}
    ballooned = set()
    for b in data.get("balloons", []):
        stats["balloons"] += 1
        n, bpn = b["no"], b["pn"]
        if n not in tab:
            fails.append("balloon %d: no table row %d" % (n, n))
        elif tab[n][1][1] != bpn:
            fails.append("balloon %d names %s, its table row %s" % (n, bpn, tab[n][1][1]))
        if bpn not in solids:
            fails.append("balloon %d: no STEP has a part under %s" % (n, bpn))
        v = views.get(b["view"])
        t3 = tuple(b["tip3d"])
        S = (v["off"][0] + v["scale"] * vdot(t3, v["x"]), v["off"][1] + v["scale"] * vdot(t3, v["y"]))
        if math.dist(S, b["tip"]) > A.TOL_TIP:
            fails.append("balloon %d: its tip is %.3f mm from where its point projects" % (n, math.dist(S, b["tip"])))
        if not A._arrow_or_dot_at(page, data["sheet_h"], tuple(b["tip"]), b["end"]):
            fails.append("balloon %d: no %s drawn at its tip" % (n, "arrowhead" if b["end"] == "arrow" else "dot"))
        if not A._in_or_on(solids.get(bpn, []), t3):
            fails.append("balloon %d: its point (%.2f, %.2f, %.2f) is not on %s in the STEPs" % ((n,) + t3 + (bpn,)))
        ballooned.add(bpn)
        txt = [t for t in readback.text_boxes(page, data["sheet_h"]) if t[4] == str(n) and
               math.dist(((t[0] + t[2]) / 2, (t[1] + t[3]) / 2), tuple(b["centre"])) < 1.5]
        if not txt:
            fails.append("balloon %d: its number isn't written in its circle" % n)
    for n, (mark, cells) in tab.items():
        has = cells[1] in solids
        if not mark and not has:
            fails.append("item %d %s has no * but no STEP has a part under it" % (n, cells[1]))
        if mark and has:
            fails.append("item %d %s is marked as not modelled, but a STEP has it" % (n, cells[1]))
        if not mark and cells[1] not in ballooned:
            fails.append("item %d %s is in the STEPs but has no balloon" % (n, cells[1]))
    # 3. interface ordinates, measured again from the STEPs
    for g in data.get("interfaces", []):
        v = views[g["view"]]
        ax = v["x"] if g["axis"] == "x" else v["y"]
        o3 = tuple(g["origin3d"])
        for p_ in g["points"]:
            stats["interfaces"] += 1
            c3 = tuple(p_["at3d"])
            if not any(all(bx[k] - A.TOL_ON <= c3[k] <= bx[k + 3] + A.TOL_ON for k in range(3))
                       for bx in [A.box_of(sol) for sol in parts.get(p_["pn"], [])]):
                fails.append("interface point of %s at (%.2f, %.2f, %.2f) is outside it" % ((p_["pn"],) + c3))
            want = abs(vdot(vsub(c3, o3), ax))
            if abs(abs(float(p_["value"])) - want) > A.TOL_ON:
                fails.append("interface value %s for %s, the STEPs give %.2f" % (p_["value"], p_["pn"], want))
    # 4. the sheet as a whole: what every drawgen sheet must hold
    text = "\n".join(pg.get_text() for pg in doc)
    up_text = text.upper()
    for need, pat in (("UNITS: mm", r"UNITS:\s*MM\b"), ("MATERIAL", r"MATERIAL:"), ("FINISH", r"FINISH:"),
                      ("TOLERANCE", r"TOLERANCE")):
        if not re.search(pat, up_text):
            fails.append("text lacks %s" % need)
    meta = doc.metadata or {}
    if meta.get("creator") != "drawgen":
        fails.append("PDF Creator is not drawgen")
    if meta.get("author") != "Autonomous":
        fails.append("PDF author is not Autonomous")
    if not re.search(r"CREATED BY\s+Autonomous\b", text):
        fails.append("the title block's CREATED BY is not Autonomous")
    for pg, phrase in readback.note_makers(doc):
        fails.append("sheet %d: a note names a maker ('%s')" % (pg, phrase))
    for pg, what in readback.clashes(doc):
        fails.append("sheet %d: %s" % (pg, what))
    return fails, stats


def main(argv=None):
    """generate [--out DIR]: draw the pod's sheet and read it back; check PDF...: read sheets back."""
    import argparse
    ap = argparse.ArgumentParser(description="drawgen: GA sheet 1, the whole pod")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate")
    g.add_argument("--out", default=None)
    c = sub.add_parser("check")
    c.add_argument("pdfs", nargs="+")
    a = ap.parse_args(argv)
    bad = 0
    if a.cmd == "generate":
        try:
            final, rep = generate(a.out)
        except NotDrawable as e:
            print("%s: not drawn: %s" % (POD_PN, e))
            return 1
        fails, st = check(final)
        print("%s: %s; read-back %s (%d STEPs, %d table rows, %d balloons, %d interface sizes)" % (
            POD_PN, inputs.rel(final) if final.startswith(inputs.REPO) else final, "PASS" if not fails else "FAIL",
            st["steps"], st["rows"], st["balloons"], st["interfaces"]))
        for f in fails:
            print("  - " + f)
        bad += bool(fails)
    else:
        for p in a.pdfs:
            fails, _st = check(p)
            print("%s: %s" % (os.path.basename(p), "PASS" if not fails else "FAIL"))
            for f in fails:
                print("  - " + f)
            bad += bool(fails)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
