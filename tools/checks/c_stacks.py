#!/usr/bin/env python3
"""C02 tolerance stack-ups, worst case first (guideline section 6.3: RSS only
with a statistical basis and process data, so RSS is shown for information).

Stacks live in v2/04-Checks/stacks/:
- stacks.csv: stack_id, joint, owner, what, min_mm, max_mm, severity,
  status_source
- contributors.csv: stack_id, name, sign (+1 or -1), nominal_mm, plus_mm,
  minus_mm, status, source

The stack result is sum(sign x value). Worst-case minimum takes each
contributor at the end that makes the result smallest, maximum the other
way. A stack with a contributor whose nominal or tolerance is still empty is
OPEN: it is listed in the report with what is missing, and becomes a finding
only when it can be computed and fails.
"""

import math
import os

from common import Finding, read_csv, num

DIR = "v2/04-Checks/stacks"


def load(root):
    sp = os.path.join(root, DIR, "stacks.csv")
    cp = os.path.join(root, DIR, "contributors.csv")
    if not (os.path.exists(sp) and os.path.exists(cp)):
        return [], {}
    stacks = read_csv(sp)
    contrib = {}
    for c in read_csv(cp):
        contrib.setdefault(c["stack_id"], []).append(c)
    return stacks, contrib


def evaluate(contribs):
    """Return dict: nominal, wc_min, wc_max, rss_min, rss_max, missing."""
    nominal = wc_min = wc_max = 0.0
    var = 0.0
    shift = 0.0
    missing = []
    for c in contribs:
        s = 1.0 if num(c.get("sign")) is None or num(c.get("sign")) >= 0 else -1.0
        n, p, m = num(c.get("nominal_mm")), num(c.get("plus_mm")), num(c.get("minus_mm"))
        if n is None or p is None or m is None:
            missing.append(c["name"])
            n = n or 0.0
            p = p or 0.0
            m = m or 0.0
        p, m = abs(p), abs(m)
        nominal += s * n
        lo, hi = (n - m, n + p)
        wc_min += min(s * lo, s * hi)
        wc_max += max(s * lo, s * hi)
        mid = (lo + hi) / 2.0
        shift += s * (mid - n)
        var += ((p + m) / 2.0) ** 2
    rss = math.sqrt(var)
    return {"nominal": nominal, "wc_min": wc_min, "wc_max": wc_max, "rss_min": nominal + shift - rss,
            "rss_max": nominal + shift + rss, "missing": missing}


def check_stacks(root):
    stacks, contrib = load(root)
    fs, report = [], []
    for st in stacks:
        sid = st["stack_id"]
        res = evaluate(contrib.get(sid, []))
        lo, hi = num(st.get("min_mm")), num(st.get("max_mm"))
        res.update({"stack_id": sid, "joint": st.get("joint", ""), "what": st.get("what", ""),
                    "min": lo, "max": hi, "owner": st.get("owner", "")})
        if res["missing"]:
            res["state"] = "OPEN"
        elif (lo is not None and res["wc_min"] < lo - 1e-9) or (hi is not None and res["wc_max"] > hi + 1e-9):
            res["state"] = "FAIL"
            fs.append(Finding(
                "C02", "stack-" + sid, sid, st.get("severity") or "major",
                "%s (%s): worst case %.2f to %.2f mm (nominal %.2f; RSS %.2f to %.2f, for information), the joint "
                "needs %s. Source of the limit: %s." % (
                    st.get("what", sid), st.get("joint", ""), res["wc_min"], res["wc_max"], res["nominal"],
                    res["rss_min"], res["rss_max"], _rng(lo, hi), st.get("status_source", "")),
                st.get("fix", "") or "Tighten the tolerances that dominate, add adjustment, or change the nominal.",
                "%s/contributors.csv" % DIR, st.get("owner", ""), {"model": "stacks", "result": res}))
        else:
            res["state"] = "PASS"
        report.append(res)
    return fs, report


def _rng(lo, hi):
    if lo is not None and hi is not None:
        return "%g to %g mm" % (lo, hi)
    return ("at least %g mm" % lo) if lo is not None else ("at most %g mm" % hi)
