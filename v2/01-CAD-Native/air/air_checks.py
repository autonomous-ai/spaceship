"""AIR checks inside Fusion (edit test and STEP re-read): every layout body where the layout
says for the design's current values."""

import air_model as A

TOL = 0.05


def values(design):
    out = {}
    for i in range(design.userParameters.count):
        p = design.userParameters.item(i)
        out[p.name] = p.value * 10.0 if p.unit == "mm" else p.value
    return out


def check(design, adsk_fusion):
    v = values(design)
    got = {}
    for occ in design.rootComponent.allOccurrences:
        for b in occ.bRepBodies:
            bb = b.boundingBox
            got.setdefault(b.name, []).append([bb.minPoint.x * 10, bb.maxPoint.x * 10, bb.minPoint.y * 10,
                                                bb.maxPoint.y * 10, bb.minPoint.z * 10, bb.maxPoint.z * 10])
    worst, bad = 0.0, []
    for _k, name, bx in A.layout():
        want = [A.ev(v, e) for e in bx]
        have = got.get(name)
        if not have:
            bad.append((name, "missing"))
            continue
        d = min(max(abs(p - q) for p, q in zip(h, want)) for h in have)
        worst = max(worst, d)
        if d > TOL:
            bad.append((name, round(d, 3)))
    tl = design.timeline
    unhealthy = [tl.item(i).name for i in range(tl.count)
                 if tl.item(i).healthState != adsk_fusion.FeatureHealthStates.HealthyFeatureHealthState]
    return {"checked": len(A.layout()), "worst": round(worst, 3), "bad": bad, "unhealthy": unhealthy}


def union_box(v=None):
    v = v if v is not None else A.evaluate()
    bs = [[A.ev(v, e) for e in bx] for _k, _n, bx in A.layout()]
    return [min(b[0] for b in bs), min(b[2] for b in bs), min(b[4] for b in bs),
            max(b[1] for b in bs), max(b[3] for b in bs), max(b[5] for b in bs)]
