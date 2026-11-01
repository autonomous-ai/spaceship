#!/usr/bin/env python3
"""Run the Fusion half of the mechanical checks through the locked runner
and turn its results into findings.

  python3 tools/checks/run_fusion_checks.py                 # assembled design on this checkout
  python3 tools/checks/run_fusion_checks.py --model skeleton
  python3 tools/checks/run_fusion_checks.py --root <tree> --rev <sha> --update
  python3 tools/checks/run_fusion_checks.py --from-json result.json --update   # convert only, no Fusion

Fusion runs only through tools/fusion/run_script.py, which takes the
machine-wide lock and waits its turn (PM rule). The Fusion script makes its
own document, imports the STEP files, measures, writes JSON and closes the
document without saving.

Findings: C01 unlisted clashes (severe), C02 gap rules on true distances,
C03 tool envelope blocked (severe), C07 bolt tip running into a part or
too little thread engagement (severe), C10 touching parts for the
mixed-metal check.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (REPO_ROOT, CHECKS_DIR, Finding, owner_for, rel, walk_files, pn_class,  # noqa: E402
                    reserved_spaces, reserved_label)
import register  # noqa: E402
import c_parts  # noqa: E402
import stepfile as sf  # noqa: E402

PN_IN_LABEL = re.compile(r"\b(\d{6})\b")


def pick_steps(root, model):
    steps = walk_files(root, "v2/03-Manufacturing", exts=(".step", ".stp"))
    if model == "skeleton":
        return [p for p in steps if "/skeleton/" in rel(root, p)]
    out = []
    for p in steps:
        if "/skeleton/" in rel(root, p):
            continue
        s = sf.StepFile(p)
        _c, tops = s.usage_counts()
        if any(pn_class(t) == "assembly" for t in tops):
            out.append(p)
    return out


def run_fusion(root, steps, out_json, cfg_root):
    runner = os.path.join(cfg_root, "tools/fusion/run_script.py")
    script = os.path.join(cfg_root, "tools/checks/fusion/whole_pod_check.py")
    cfg = os.path.join(cfg_root, CHECKS_DIR, "config")
    cmd = [sys.executable, runner, script, "--lock-wait", os.environ.get("CHECKS_LOCK_WAIT", "7200"),
           "--arg", "steps=" + ",".join(os.path.abspath(p) for p in steps),
           "--arg", "out=" + out_json, "--arg", "rules=" + os.path.join(cfg, "gap-rules.csv"),
           "--arg", "allow=" + os.path.join(cfg, "clash-allow.csv"), "--arg", "tools=" + os.path.join(cfg, "tools.csv"),
           "--arg", "swing=" + os.path.join(cfg, "door-swing.csv")]
    env = dict(os.environ, FUSION_MCP_LABEL=os.environ.get("FUSION_MCP_LABEL", "Mechanical Checker"))
    p = subprocess.run(cmd, env=env, capture_output=True, text=True)
    return p.returncode, p.stdout[-4000:], p.stderr[-4000:]


def _relative(res, root):
    """A copy of a Fusion result with file paths relative to the repo (or bare names), never absolute."""
    out = dict(res)

    def rp(p):
        p = os.path.abspath(p)
        for base in (root, REPO_ROOT):
            if p.startswith(os.path.abspath(base) + os.sep):
                return os.path.relpath(p, base).replace(os.sep, "/")
        return os.path.basename(p)
    out["steps"] = [rp(p) for p in res.get("steps", [])]
    out["imports"] = [dict(i, file=rp(i["file"])) for i in res.get("imports", [])]
    return out


def _short(label):
    return label.split(" / ")[-2] if " / " in label else label


def _pn(label):
    m = PN_IN_LABEL.findall(label or "")
    return m[-1] if m else ""


def _allowed(c, allow_rows):
    for r in allow_rows or []:
        ra, rb = re.compile(r["a"], re.I), re.compile(r["b"], re.I)
        vmax = float(r.get("max_mm3") or 0)
        same = c["a"].split(" / ")[0] == c["b"].split(" / ")[0]     # scope same-file: one assembly file (D-104)
        if ((ra.search(c["a"]) and rb.search(c["b"])) or (ra.search(c["b"]) and rb.search(c["a"]))) and \
                (vmax <= 0 or c["mm3"] <= vmax) and ((r.get("scope") or "").strip() != "same-file" or same):
            return r["id"]
    return None


# a door may touch or wipe a seal as it swings (the seal is modelled rigid); more overlap than this means it
# crushes the seal's body, not its fin (assumption, about a 2 mm deep bite along 25 mm of a 2 mm fin)
SOFT_SWING_MM3 = 100.0


# D-92: ELECTRICAL's route bodies (routes, pockets, grommets: its 7100xx components) are reserved spaces, not panels:
# the gap and seam rules skip them (a clash with one still counts: a cable can't pass through a wall without a hole)
ROUTE_BODY = re.compile(r"(?<!\d)7100\d\d(?!\d)")


def _file_of(label, steps):
    """The repo-relative STEP file a body comes from: the file whose name starts with the number of the label's top
    component ('410000_P01_CEILING_CAD:1 / ...' is CEILING's 410000_P01_CEILING_STEP.step); '' when none does."""
    m = re.match(r"(\d{6})_", (label or "").split(" / ")[0])
    for s in (steps or []) if m else []:
        s = s.replace("\\", "/")
        i = s.find("v2/03-Manufacturing/")
        if i >= 0 and os.path.basename(s).startswith(m.group(1) + "_"):
            return s[i:]
    return ""


def _team_of(label, steps):
    """The team whose STEP file a body comes from."""
    f = _file_of(label, steps)
    return owner_for(f, f.split("/")[-1][:6]) if f else owner_for("", _pn(label))


def _folder_of(label, steps):
    """The team folder of a body's STEP file ('air' for v2/03-Manufacturing/air/...)."""
    parts = _file_of(label, steps).split("/")
    return parts[2] if len(parts) > 3 else ""


def _reserved_owner(label, reserved):
    """The owner (lower case) of the reserved space a body's label names, or None."""
    for pn in reserved or {}:
        if re.search(r"(?<!\d)%s(?!\d)" % pn, label or ""):
            row = reserved[pn] if isinstance(reserved, dict) else {}
            return (row.get("owner") or "").strip().lower()
    return None


# ISO head heights k as a share of the thread size d: k = d for ISO 4762 socket heads; 0.55 d for the ISO 7380
# button heads (3.3 at M6, 2.75 at M5, 4.4 at M8); 0 for countersunk heads, whose length is the whole screw
# (source: the standards' k max). The bolt walk measures a bolt with its head.
HEAD_K = (("ISO 4762", 1.0), ("ISO 7380", 0.55), ("ISO 10642", 0.0), ("ISO 7046", 0.0), ("ISO 14581", 0.0))
SIZE_X_LEN = re.compile(r"\bM(\d+(?:\.\d+)?)\s*X\s*(\d+(?:\.\d+)?)\b", re.I)


def nominal_length(name):
    """(d, length under the head, whole length with the head) from a fastener's name, or None when its name gives
    no size and length or no head standard this knows."""
    m = SIZE_X_LEN.search(name or "")
    if not m:
        return None
    for std, k in HEAD_K:
        if std in (name or "").upper():
            d, length = float(m.group(1)), float(m.group(2))
            return d, length, length + k * d
    return None


def _thread_rule(bolt, body, allow_rows):
    """The clash-allow rule that makes `body` the bolt's own thread, or None: the rules whose id says THREAD or
    TAPPED (BOLT-IN-THREAD for nuts and rivnuts, SCREW-IN-TAPPED-KEY for the base keys' tapped holes)."""
    for r in allow_rows or []:
        if not re.search(r"THREAD|TAPPED", r.get("id") or "", re.I):
            continue
        ra, rb = re.compile(r["a"], re.I), re.compile(r["b"], re.I)
        if (ra.search(bolt) and rb.search(body)) or (ra.search(body) and rb.search(bolt)):
            return r["id"]
    return None


def stale_swing(d, door_rows):
    """A saved door swing whose moving bodies today's config/door-swing.csv no longer picks (a pattern that caught
    a part outside the door) can't be read again: only a new run can swing the right bodies."""
    for row in door_rows or []:
        if (row.get("direction") or "").strip() != (d.get("direction") or "").strip():
            continue
        mv = re.compile(row["moving"], re.I)
        ex = re.compile(row["fixed_exclude"], re.I) if row.get("fixed_exclude") else None
        return [l for l in d.get("moving", []) if not mv.search(l) or (ex and ex.search(l))]
    return []


def findings_from(res, model, file_hint="", allow_rows=None, reserved=None, factory=None, tapped_min_d=1.5,
                  door_rows=None, notes=None):
    """Findings carry the scope '<model>/fusion', so only a Fusion run can
    close them (an offline run can't see an exact clash); the door swing's carry '<model>/fusion-swing'. With
    allow_rows, the allow-list is applied again, so a saved run reads with today's list.
    factory: config/factory-fitted.csv rows (pattern, why): fasteners set before their sub-assembly meets the others,
    so only that sub-assembly's parts can be in the tool's way. tapped_min_d: the least engagement in a tapped hole,
    in thread diameters (config/policy.csv). door_rows: config/door-swing.csv, to set aside a stale saved swing.
    notes: a list that gets what was set aside, and why."""
    fs = []
    scope = model + "/fusion"
    steps = res.get("steps")
    notes = notes if notes is not None else []
    clashes = {}
    for c in res.get("clashes", []):
        # today's allow list decides when it's given, both ways: a rule made narrower brings a hidden clash back
        if (_allowed(c, allow_rows) if allow_rows is not None else c.get("allowed")):
            continue
        if reserved:
            # D-105: a reserved space holds the place of a part its owner designs (FRONT's DR spaces for AIR's air
            # path); the owner's own parts may fill it, anyone else's part in it is a clash
            oa, ob = _reserved_owner(c["a"], reserved), _reserved_owner(c["b"], reserved)
            if (oa and _folder_of(c["b"], steps) == oa) or (ob and _folder_of(c["a"], steps) == ob):
                continue
        clashes.setdefault("%s %s x %s" % (model, _short(c["a"]), _short(c["b"])), []).append(c)
    for subject, cs in clashes.items():
        # one finding per pair of parts, with its largest overlap (a part's bodies can meet the other's several times)
        c = max(cs, key=lambda x: x["mm3"])
        more = " (the largest of %d body pairs, %.1f mm3 in all)" % (len(cs), sum(x["mm3"] for x in cs)) \
            if len(cs) > 1 else ""
        fs.append(Finding(
            "C01", "clash", subject, "severe",
            "%s and %s overlap by %.1f mm3%s in the %s (Fusion, exact intersection)." % (
                c["a"], c["b"], c["mm3"], more, model),
            "Fix the geometry so they meet or clear; if the overlap is intended, add it to "
            "v2/04-Checks/config/clash-allow.csv with its reason.", file_hint,
            owner_for(file_hint, _pn(c["a"])) if file_hint else
            "; ".join(sorted({_team_of(c["a"], res.get("steps")), _team_of(c["b"], res.get("steps"))})),
            {"model": scope, "mm3": c["mm3"], "a": c["a"], "b": c["b"], "pairs": len(cs)}))
    groups = {}
    for g in res.get("gaps", []):
        if reserved and (reserved_label(g.get("a", ""), reserved) or reserved_label(g.get("b", ""), reserved)):
            continue                    # a reserved space has no seams until it's designed
        if ROUTE_BODY.search(g.get("a", "")) or ROUTE_BODY.search(g.get("b", "")):
            continue                    # D-92: ELECTRICAL's route bodies have no seams
        lo, hi = g.get("min_mm"), g.get("max_mm")
        if (lo is not None and g["gap_mm"] < lo - 1e-6) or (hi is not None and g["gap_mm"] > hi + 1e-6):
            groups.setdefault(g.get("group") or g["id"], []).append(g)
    for grp, items in groups.items():
        sev = "severe" if any(g.get("severity") == "severe" for g in items) else "major"
        if model == "skeleton" and all(g.get("method") == "exact" for g in items):
            sev = "major"           # reference geometry only: the made parts are checked in the assembly model
        fs.append(Finding(
            "C02", "gap-" + grp, "%s %s" % (model, grp), sev,
            "; ".join("%s: %s to %s is %.2f mm (true minimum distance, Fusion), needs %s" % (
                g["id"], _short(g["a"]), _short(g["b"]), g["gap_mm"],
                ("%g to %g" % (g["min_mm"], g["max_mm"])) if g.get("max_mm") is not None else ">= %g" % g["min_mm"])
                      for g in items),
            items[0].get("fix") or "See the rule's fix in v2/04-Checks/config/gap-rules.csv.", file_hint,
            items[0].get("owner") or owner_for(file_hint), {"model": scope, "rules": items}))
    for d in res.get("door_swing", []):
        stale = stale_swing(d, door_rows)
        if stale:
            notes.append("door swing %s set aside: it swung %s, which config/door-swing.csv no longer moves with "
                         "the door; the next Fusion run swings the right bodies" % (
                             d.get("direction"), ", ".join(_short(l) for l in stale[:3])))
            continue
        h = d.get("first_hit")          # the first rigid part it hits (a seal it only touches is soft)
        deep = [x for x in d.get("hits", []) if x.get("soft") and x.get("max_mm3", 0) > SOFT_SWING_MM3]
        if not h and deep:               # a seal the door doesn't just touch but crushes
            x = deep[0]
            h = {"hits": x["hits"], "angle_deg": x["first_deg"], "moving": x["moving"], "mm3": x["max_mm3"]}
        if h:
            fs.append(Finding(
                "C01", "door-swing", "%s door swing %s" % (model, d.get("direction")), "severe",
                "Opening %s, the door hits %s at %g degrees (%s, %.1f mm3 overlap); it must open to %g degrees "
                "freely. Swing assumptions: %s" % (d.get("direction"), _short(h["hits"]), h["angle_deg"],
                                                   _short(h["moving"]), h["mm3"], d["max_deg"], d["rule"]),
                "Move the hinge axis, trim the part it hits, or add a door stop before that angle if the "
                "clear width at the stop still meets REQ-US-03.", file_hint, owner_for(file_hint, "35"),
                {"model": scope + "-swing", "swing": d}))
    for b in res.get("fasteners", []):
        if b.get("error"):
            continue
        name = _short(b["bolt"])
        subject = "%s %s at %s" % (model, name, b["head"])
        owner = owner_for(file_hint, _pn(b["bolt"])) if file_hint else _team_of(b["bolt"], steps)
        nom = nominal_length(name)
        if nom and abs(nom[2] - b["length_mm"]) > 1.0:
            # a bolt modelled short (a stub, or split into bodies) can't be followed to its thread or its tool
            fs.append(Finding(
                "C07", "fastener-model", subject, "major",
                "%s is modelled %.1f mm long with its head, but its name gives M%g x %g, %.1f mm with the head: the "
                "check can't follow it to its thread or its tool, so it leaves the rest of it out." % (
                    b["bolt"], b["length_mm"], nom[0], nom[1], nom[2]),
                "Model the bolt at its full size, one body and one component per bolt (the bolt STEP the joints "
                "register names), and export the STEP again.", file_hint, owner, {"model": scope, "bolt": b}))
            continue
        reach = b["length_mm"]
        nut = [x for x in b["layers"] if x["is_nut"] and x["from_head_mm"] <= reach]       # threads the bolt enters
        tapped = [x for x in b["layers"] if not x["is_nut"] and x["from_head_mm"] <= reach
                  and _thread_rule(b["bolt"], x["body"], allow_rows)]
        solid = [x for x in b["layers"] if not x["is_nut"] and x not in tapped and x["from_head_mm"] <= reach]
        # the tool: never blocked by the bolt's own bodies; a factory-fitted one only by its own sub-assembly
        own = b["bolt"].rsplit(" / ", 1)[0] + " / "
        blocked = [x for x in b.get("tool_blocked_by") or [] if not x["body"].startswith(own)]
        fac = next((r for r in factory or [] if re.search(r["pattern"], b["bolt"], re.I)), None)
        if fac:
            sub = b["bolt"].rsplit(" / ", 2)[0] + " / "
            blocked = [x for x in blocked if x["body"].startswith(sub)]
        if blocked:
            fs.append(Finding(
                "C03", "tool-blocked", subject, "severe",
                "The tool can't reach %s at %s: a %s envelope along its axis hits %s." % (
                    b["bolt"], b["head"], b["tool"], ", ".join("%s (%.0f mm3)" % (x["body"], x["mm3"])
                                                               for x in blocked[:4])),
                "Move the bolt, add an access hole, or change the assembly order so the tool goes in first.",
                file_hint, owner, {"model": scope, "bolt": b}))
        if b.get("collisions"):
            fs.append(Finding(
                "C07", "bolt-collides", subject, "severe",
                "%s (%.1f mm long) runs into material with no hole for it: %s. If that is past the nut, the bolt is "
                "too long and bottoms out before it clamps." % (
                    b["bolt"], b["length_mm"], ", ".join("%s from %.1f mm" % (x["body"], x["from_head_mm"])
                                                         for x in b["collisions"][:3])),
                "Shorten the bolt or add the hole; the tip must stop at least 1 mm short of the next part.", file_hint,
                owner, {"model": scope, "bolt": b}))
        tc = b.get("tip_clearance")
        if tc and tc["mm"] < 1.0 and not b.get("collisions"):
            fs.append(Finding(
                "C07", "tip-clearance", subject, "major",
                "%s's tip is %.2f mm from %s: under the 1 mm minimum, so tolerances can make it bottom out." % (
                    b["bolt"], tc["mm"], tc["body"]),
                "Shorten the bolt or move the part behind it.", file_hint, owner, {"model": scope, "bolt": b}))
        if nut:
            n = nut[-1]
            engaged = min(b["length_mm"], n["to_mm"]) - n["from_head_mm"]
            full = n["to_mm"] - n["from_head_mm"]
            protrude = b["length_mm"] - n["to_mm"]
            through_nut = re.search(r"\bNUT\b", n["body"], re.I) and not re.search(r"RIVNUT|RIVET NUT", n["body"], re.I)
            if through_nut and engaged + 0.5 >= full and protrude < 1.0:
                fs.append(Finding(
                    "C07", "no-protrusion", subject, "major",
                    "%s ends %.1f mm past %s: at least one thread (1 mm for M6) should show past a nut." % (
                        b["bolt"], protrude, n["body"]),
                    "Lengthen the bolt by one size.", file_hint, owner, {"model": scope, "bolt": b}))
            if engaged + 0.5 < full:
                fs.append(Finding(
                    "C07", "short-engagement", subject, "severe",
                    "%s engages %.1f mm of the %.1f mm thread in %s: not full engagement." % (
                        b["bolt"], max(engaged, 0.0), full, n["body"]),
                    "Lengthen the bolt to pass through the whole thread (plus at least 1 pitch for a through nut).",
                    file_hint, owner, {"model": scope, "bolt": b}))
        elif tapped:
            # a tapped hole: the bolt needs enough thread in it, not the whole part (the walk samples every 0.25 to
            # 0.5 mm, so 0.25 mm is given back)
            t = tapped[-1]
            d = nom[0] if nom else b.get("dia_mm") or 0.0
            engaged = min(b["length_mm"], t["to_mm"]) - t["from_head_mm"]
            need = tapped_min_d * d
            if engaged + 0.25 < need:
                fs.append(Finding(
                    "C07", "short-engagement", subject, "severe",
                    "%s engages %.1f mm of thread in the tapped hole in %s; a tapped hole needs at least %.1f x d = "
                    "%.1f mm (config/policy.csv)." % (b["bolt"], max(engaged, 0.0), t["body"], tapped_min_d, need),
                    "Lengthen the screw or deepen the thread.", file_hint, owner, {"model": scope, "bolt": b}))
        elif solid:
            fs.append(Finding(
                "C07", "no-thread-found", subject, "major",
                "No nut, rivnut, insert or tapped hole found along %s; it passes %s." % (
                    b["bolt"], ", ".join(x["body"] for x in solid[:4])),
                "Model the nut or rivnut it threads into, or name it so the check can find it (a tapped part needs "
                "its rule in v2/04-Checks/config/clash-allow.csv).", file_hint, owner, {"model": scope, "bolt": b}))
    return fs


def contacts_from(res):
    return [(_pn(t["a"]), _pn(t["b"]), "") for t in res.get("touching", []) if _pn(t["a"]) and _pn(t["b"])]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=REPO_ROOT)
    ap.add_argument("--ref", default="", help="check this git ref (e.g. origin/main) in a fresh export instead of --root")
    ap.add_argument("--register-root", default=REPO_ROOT)
    ap.add_argument("--model", default="assembly", help="assembly, skeleton, or a label for --steps")
    ap.add_argument("--steps", default="", help="comma-separated STEP files to check instead of picking them")
    ap.add_argument("--save-json", default="", help="also copy the raw Fusion result here")
    ap.add_argument("--rev", default="")
    ap.add_argument("--update", action="store_true")
    ap.add_argument("--from-json", default="")
    a = ap.parse_args(argv)
    root = os.path.abspath(a.root)
    export_dir = None
    if a.ref:
        from common import export_ref
        root, sha = export_ref(a.ref)
        export_dir = root
        a.rev = a.rev or sha
    try:
        return _main(a, root)
    finally:
        if export_dir:                      # the export is about 22 MB: never leave it behind
            import shutil
            shutil.rmtree(export_dir, ignore_errors=True)


def _main(a, root):
    if a.from_json:
        with open(a.from_json, encoding="utf-8") as fh:
            res = json.load(fh)
    else:
        steps = [os.path.abspath(p) for p in a.steps.split(",") if p] if a.steps else pick_steps(root, a.model)
        if not steps:
            print("no %s STEP files to check" % a.model)
            return 0
        out_json = os.path.join(tempfile.mkdtemp(prefix="fusion-check-"), "result.json")
        code, out, err = run_fusion(root, steps, out_json, REPO_ROOT)
        print(out)
        if code != 0 or not os.path.exists(out_json):
            print(err, file=sys.stderr)
            print("Fusion run failed (exit %d)" % code, file=sys.stderr)
            return 2
        with open(out_json, encoding="utf-8") as fh:
            res = json.load(fh)
        import shutil
        if a.save_json:
            with open(a.save_json, "w", encoding="utf-8") as fh:
                json.dump(_relative(res, root), fh, indent=1)
                fh.write("\n")
        shutil.rmtree(os.path.dirname(out_json), ignore_errors=True)
        res["rev"] = a.rev
        res["model"] = a.model
    model = res.get("model", a.model)
    hint = rel(root, res["steps"][0]) if res.get("steps") and len(res["steps"]) == 1 and \
        os.path.abspath(res["steps"][0]).startswith(root) else ""
    cfg = os.path.join(a.register_root, CHECKS_DIR, "config")

    def rows(name):
        p = os.path.join(cfg, name)
        return c_parts.read_csv(p) if os.path.exists(p) else []
    allow_rows = rows("clash-allow.csv")
    import c_drawings
    tapped_min_d = float(c_drawings.policy(a.register_root, "tapped_engagement_min_d", "1.5"))
    notes = []
    fs = findings_from(res, model, hint, allow_rows, reserved_spaces(root), factory=rows("factory-fitted.csv"),
                       tapped_min_d=tapped_min_d, door_rows=rows("door-swing.csv"), notes=notes)
    for n in notes:
        print("note: " + n)
    plists = c_parts.find_parts_lists(root)
    if plists:
        fs += c_parts.check_mixed_metals(root, plists, contacts_from(res))
    print("fusion %s: %d bodies, %d clashes (%d unlisted), %d fasteners, %d findings, %.0f s" % (
        model, len(res.get("bodies", [])), len(res.get("clashes", [])),
        sum(1 for c in res.get("clashes", []) if not c.get("allowed")), len(res.get("fasteners", [])), len(fs),
        res.get("seconds", 0)))
    for f in fs:
        print("  %-6s %s | %s" % (f.severity, f.check, f.subject))
    if a.update:
        out = os.path.join(a.register_root, CHECKS_DIR, "results")
        os.makedirs(out, exist_ok=True)
        slim = _relative(res, root)
        with open(os.path.join(out, "fusion-%s-latest.json" % model), "w", encoding="utf-8") as fh:
            json.dump(slim, fh, indent=1)
            fh.write("\n")
        reg = register.load(a.register_root)
        ran = ["%s:%s/fusion" % (c, model) for c in ("C01", "C02", "C03", "C07")]
        if res.get("door_swing") and not any(n.startswith("door swing") for n in notes):
            ran.append("C01:%s/fusion-swing" % model)        # a swing set aside keeps its findings open
        new, reopened, closed = register.merge(reg, [f.to_dict() for f in fs], a.rev or "unknown", None, ran)
        register.save(reg, a.register_root)
        print("register: new %s, reopened %s, closed %s" % (new or "-", reopened or "-", closed or "-"))
    return 1 if any(f.severity == "severe" for f in fs) else 0


if __name__ == "__main__":
    sys.exit(main())
