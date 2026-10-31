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
from common import REPO_ROOT, CHECKS_DIR, Finding, owner_for, rel, walk_files, pn_class  # noqa: E402
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
    cmd = [sys.executable, runner, script, "--lock-wait", os.environ.get("CHECKS_LOCK_WAIT", "3600"),
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
        if ((ra.search(c["a"]) and rb.search(c["b"])) or (ra.search(c["b"]) and rb.search(c["a"]))) and \
                (vmax <= 0 or c["mm3"] <= vmax):
            return r["id"]
    return None


# a door may touch or wipe a seal as it swings (the seal is modelled rigid); more overlap than this means it
# crushes the seal's body, not its fin (assumption, about a 2 mm deep bite along 25 mm of a 2 mm fin)
SOFT_SWING_MM3 = 100.0


def findings_from(res, model, file_hint="", allow_rows=None):
    """Findings carry the scope '<model>/fusion', so only a Fusion run can
    close them (an offline run can't see an exact clash). With allow_rows,
    the allow-list is applied again, so a saved run reads with today's list."""
    fs = []
    scope = model + "/fusion"
    for c in res.get("clashes", []):
        if c.get("allowed") or _allowed(c, allow_rows):
            continue
        fs.append(Finding(
            "C01", "clash", "%s %s x %s" % (model, _short(c["a"]), _short(c["b"])), "severe",
            "%s and %s overlap by %.1f mm3 in the %s (Fusion, exact intersection)." % (c["a"], c["b"], c["mm3"], model),
            "Fix the geometry so they meet or clear; if the overlap is intended, add it to "
            "v2/04-Checks/config/clash-allow.csv with its reason.", file_hint, owner_for(file_hint, _pn(c["a"])),
            {"model": scope, "mm3": c["mm3"], "a": c["a"], "b": c["b"]}))
    groups = {}
    for g in res.get("gaps", []):
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
                {"model": scope, "swing": d}))
    for b in res.get("fasteners", []):
        if b.get("error"):
            continue
        name = _short(b["bolt"])
        reach = b["length_mm"]
        nut = [x for x in b["layers"] if x["is_nut"] and x["from_head_mm"] <= reach]       # threads the bolt enters
        solid = [x for x in b["layers"] if not x["is_nut"] and x["from_head_mm"] <= reach]
        if b.get("tool_blocked_by"):
            fs.append(Finding(
                "C03", "tool-blocked", "%s %s at %s" % (model, name, b["head"]), "severe",
                "The tool can't reach %s at %s: a %s envelope along its axis hits %s." % (
                    b["bolt"], b["head"], b["tool"], ", ".join("%s (%.0f mm3)" % (x["body"], x["mm3"])
                                                               for x in b["tool_blocked_by"][:4])),
                "Move the bolt, add an access hole, or change the assembly order so the tool goes in first.",
                file_hint, owner_for(file_hint, _pn(b["bolt"])), {"model": scope, "bolt": b}))
        if b.get("collisions"):
            fs.append(Finding(
                "C07", "bolt-collides", "%s %s at %s" % (model, name, b["head"]), "severe",
                "%s (%.1f mm long) runs into material with no hole for it: %s. If that is past the nut, the bolt is "
                "too long and bottoms out before it clamps." % (
                    b["bolt"], b["length_mm"], ", ".join("%s from %.1f mm" % (x["body"], x["from_head_mm"])
                                                         for x in b["collisions"][:3])),
                "Shorten the bolt or add the hole; the tip must stop at least 1 mm short of the next part.", file_hint,
                owner_for(file_hint, _pn(b["bolt"])), {"model": scope, "bolt": b}))
        tc = b.get("tip_clearance")
        if tc and tc["mm"] < 1.0 and not b.get("collisions"):
            fs.append(Finding(
                "C07", "tip-clearance", "%s %s at %s" % (model, name, b["head"]), "major",
                "%s's tip is %.2f mm from %s: under the 1 mm minimum, so tolerances can make it bottom out." % (
                    b["bolt"], tc["mm"], tc["body"]),
                "Shorten the bolt or move the part behind it.", file_hint, owner_for(file_hint, _pn(b["bolt"])),
                {"model": scope, "bolt": b}))
        if nut:
            n = nut[-1]
            engaged = min(b["length_mm"], n["to_mm"]) - n["from_head_mm"]
            full = n["to_mm"] - n["from_head_mm"]
            protrude = b["length_mm"] - n["to_mm"]
            through_nut = re.search(r"\bNUT\b", n["body"], re.I) and not re.search(r"RIVNUT|RIVET NUT", n["body"], re.I)
            if through_nut and engaged + 0.5 >= full and protrude < 1.0:
                fs.append(Finding(
                    "C07", "no-protrusion", "%s %s at %s" % (model, name, b["head"]), "major",
                    "%s ends %.1f mm past %s: at least one thread (1 mm for M6) should show past a nut." % (
                        b["bolt"], protrude, n["body"]),
                    "Lengthen the bolt by one size.", file_hint, owner_for(file_hint, _pn(b["bolt"])),
                    {"model": scope, "bolt": b}))
            if engaged + 0.5 < full:
                fs.append(Finding(
                    "C07", "short-engagement", "%s %s at %s" % (model, name, b["head"]), "severe",
                    "%s engages %.1f mm of the %.1f mm thread in %s: not full engagement." % (
                        b["bolt"], max(engaged, 0.0), full, n["body"]),
                    "Lengthen the bolt to pass through the whole thread (plus at least 1 pitch for a through nut).",
                    file_hint, owner_for(file_hint, _pn(b["bolt"])), {"model": scope, "bolt": b}))
        elif solid:
            fs.append(Finding(
                "C07", "no-thread-found", "%s %s at %s" % (model, name, b["head"]), "major",
                "No nut, rivnut or insert found along %s; it passes %s." % (b["bolt"], ", ".join(x["body"] for x in solid[:4])),
                "Model the nut or rivnut it threads into, or name it so the check can find it.", file_hint,
                owner_for(file_hint, _pn(b["bolt"])), {"model": scope, "bolt": b}))
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
    allow_p = os.path.join(a.register_root, CHECKS_DIR, "config", "clash-allow.csv")
    allow_rows = c_parts.read_csv(allow_p) if os.path.exists(allow_p) else []
    fs = findings_from(res, model, hint, allow_rows)
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
        new, reopened, closed = register.merge(reg, [f.to_dict() for f in fs], a.rev or "unknown", None, ran)
        register.save(reg, a.register_root)
        print("register: new %s, reopened %s, closed %s" % (new or "-", reopened or "-", closed or "-"))
    return 1 if any(f.severity == "severe" for f in fs) else 0


if __name__ == "__main__":
    sys.exit(main())
