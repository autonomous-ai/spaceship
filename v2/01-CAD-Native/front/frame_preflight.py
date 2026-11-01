"""Offline preflight for FRONT's three decor frames, before a Fusion run (no Fusion needed):

    python3 v2/01-CAD-Native/front/frame_preflight.py
    python3 v2/01-CAD-Native/front/frame_preflight.py --cut-lists [dl_block.py ...]   # write the cut lists

For each block (DL, DT, DR), at the nominal parameters and at its edit test's values (the edits in
EDIT-TEST-RECORD.md):
- every tube outline is a simple polygon (no edge crossing another) with no edge under MIN_EDGE: a folded outline
  builds at one size and turns unhealthy at another (DL's door-side ring tubes on 2026-11-01, where the 7 mm front face
  had no width left at the bond line's depth);
- every edit-test anchor on a frame tube equals that tube's box (DR's frame anchors went stale when the tubes moved to
  the bond line, 2026-11-01);
- repeats are copies (frame_lib.check_copies), and DL's door-side post's corner bead meets the bond spec (post_bead).
Exits 1 on any failure.
"""
import math
import os
import re
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MIN_EDGE = 0.5    # mm
# the edit tests' values (EDIT-TEST-RECORD.md)
EDITS = {"dl_block.py": {"decor_d": "215 mm", "dl_w": "283 mm", "dl_y3": "848 mm"},
         "dt_block.py": {"decor_d": "215 mm", "dt_xr": "1690 mm", "dl_w": "283 mm"},
         "dr_block.py": {"decor_d": "215 mm", "fix_xk": "511 mm", "fix_zk": "1531 mm"}}


def load(script, edits=None):
    """The block script's namespace and its parameters in mm (skeleton, library, own), with edits applied."""
    for m in ("adsk", "adsk.core", "adsk.fusion"):
        sys.modules.setdefault(m, types.ModuleType(m))
    sys.modules["adsk"].core = sys.modules["adsk.core"]
    sys.modules["adsk"].fusion = sys.modules["adsk.fusion"]
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    path = os.path.join(HERE, script)
    g = {"SCRIPT_ARGS": {"repo_root": REPO}, "__file__": path, "__name__": "front_preflight"}
    src = open(path, encoding="utf-8").read()
    exec(compile(src, path, "exec"), g)
    lib = g["L"]
    params, _p, _r = lib.load_skeleton_params(REPO)
    lists = [params, lib.LIB_PARAMS, lib.GLASS_PARAMS] + ([lib.JF_PARAMS] if "JF_PARAMS" in src else []) + [g["OWN"]]
    env = {"abs": abs, "sqrt": math.sqrt}
    for lst in lists:
        for name, expr, *_ in lst:
            e = (edits or {}).get(name, expr)
            env[name] = eval(re.sub(r"(\d)\s*mm\b", r"\1", e).replace("^", "**"), {"__builtins__": {}}, env)
    return g, env


def _crosses(p):
    def o(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    n = len(p)
    for i in range(n):
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            a, b, c, d = p[i], p[(i + 1) % n], p[j], p[(j + 1) % n]
            if o(a, b, c) * o(a, b, d) < -1e-9 and o(c, d, a) * o(c, d, b) < -1e-9:
                return True
    return False


def check(script, edits=None):
    g, env = load(script, edits)
    FL = g["FL"]
    ev = FL.evaluator(env)
    bad, boxes = [], {}
    members = g["frame_members"]()
    for m in members:
        pts = [(ev(u), ev(v)) for u, v in m["pts"]]
        short = min(math.dist(pts[i - 1], pts[i]) for i in range(len(pts)))
        if _crosses(pts):
            bad.append("%s's outline crosses itself" % m["key"])
        if short < MIN_EDGE:
            bad.append("%s's outline has a %.3f mm edge" % (m["key"], short))
        ax = m["axes"]
        r = {ax[0]: (min(p[0] for p in pts), max(p[0] for p in pts)), ax[1]: (min(p[1] for p in pts), max(p[1] for p in pts))}
        a, b = ev(m["a"]), ev(m["b"])
        r[m["along"]] = (min(a, b), max(a, b))
        boxes[m["key"]] = [r["x"][0], r["y"][0], r["z"][0], r["x"][1], r["y"][1], r["z"][1]]
    for key, i, expr in g["ANCHORS"]:
        if key in boxes and abs(ev(expr) - boxes[key][i]) > 0.01:
            bad.append("anchor %s[%d]: the tube at %.3f, its expression %.3f" % (key, i, boxes[key][i], ev(expr)))
    frame_pn, member_pn = {"dl_block.py": ("DL_FRAME", "DL_MEMBERS"), "dt_block.py": ("DT_FRAME", "DT_MEMBERS"),
                           "dr_block.py": ("DR_FRAME", "DR_MEMBERS")}[script]
    MP = g["MP"]
    try:
        FL.check_copies(members, FL.member_parts(REPO, getattr(MP, frame_pn), getattr(MP, member_pn)), ev)
    except RuntimeError as e:
        bad.append("copies: %s" % e)
    if "post_bead" in g:
        try:
            g["post_bead"](ev)
        except RuntimeError as e:
            bad.append(str(e))
    return len(members), bad


CUT_REL = {"dl_block.py": "351104_P01_FRONT-DECOR-FRAME-DL-TUBE-CUT-LIST.csv",
           "dt_block.py": "351204_P01_FRONT-DECOR-FRAME-DT-TUBE-CUT-LIST.csv",
           "dr_block.py": "351306_P01_FRONT-DECOR-FRAME-DR-TUBE-CUT-LIST.csv"}


def write_cut_lists(scripts=None):
    """Write the frames' tube cut lists (D-162) from the same frame data the builds use: the build writes the very same
    file (frame_lib.write_cut_list), so a cut list can be brought up to date without a Fusion run."""
    for script in scripts or CUT_REL:
        g, env = load(script)
        FL, MP = g["FL"], g["MP"]
        frame_pn, member_pn = {"dl_block.py": ("DL_FRAME", "DL_MEMBERS"), "dt_block.py": ("DT_FRAME", "DT_MEMBERS"),
                               "dr_block.py": ("DR_FRAME", "DR_MEMBERS")}[script]
        mparts = FL.member_parts(REPO, getattr(MP, frame_pn), getattr(MP, member_pn))
        path = os.path.join(REPO, "v2", "03-Manufacturing", "front", CUT_REL[script])
        FL.write_cut_list(path, g["frame_members"](), FL.evaluator(env), getattr(MP, frame_pn), mparts,
                          "aluminium EN AW-6063-T6")
        print("wrote %s" % os.path.relpath(path, REPO))


def main():
    if "--cut-lists" in sys.argv[1:]:
        write_cut_lists([a for a in sys.argv[1:] if a.endswith(".py")] or None)
        return 0
    failed = 0
    for script in ("dl_block.py", "dt_block.py", "dr_block.py"):
        for label, edits in (("nominal", None), ("edit test", EDITS[script])):
            n, bad = check(script, edits)
            print("%s %s: %d tubes, %s" % (script, label, n, "OK" if not bad else "; ".join(bad)))
            failed += bool(bad)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
