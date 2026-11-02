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


def number_of(key):
    """The part number a layout key's bodies carry: a part's (PARTS), or a hardware item's (HARDWARE: the soffit's
    lock screws are 838002, built with that number); BODY_KEY first, for a box whose body is another part's."""
    k = A.BODY_KEY.get(key, key)
    if k in A.PARTS:
        return A.PARTS[k][0]
    if k in A.HARDWARE:
        return A.HARDWARE[k][0]
    raise KeyError("layout key %r has no part or hardware number" % key)


def place_check(got, v):
    """Each unit of the layout (A.units: a copy of a part, a joined head and shank as one) against the bodies of its
    part number, paired by nearest fit (copies carry one body name, D-120). got: {part number: [x0, x1, y0, y1, z0,
    z1] per body}. Returns (worst mm, [(unit, problem)])."""
    worst, bad = 0.0, []
    by_key = {}
    for k, name, bx in A.units():
        by_key.setdefault(k, []).append((name, [A.ev(v, e) for e in bx]))
    for k, items in by_key.items():
        pool = list(got.get(number_of(k), []))
        for name, want in items:
            if not pool:
                bad.append((name, "missing"))
                continue
            best = min(pool, key=lambda h: max(abs(p - q) for p, q in zip(h, want)))
            d = max(abs(p - q) for p, q in zip(best, want))
            pool.remove(best)
            worst = max(worst, d)
            if d > TOL:
                bad.append((name, round(d, 3)))
    return worst, bad


def bodies_by_number(root):
    got = {}
    for occ in root.allOccurrences:
        for b in occ.bRepBodies:
            bb = b.boundingBox
            got.setdefault(occ.component.partNumber, []).append(
                [bb.minPoint.x * 10, bb.maxPoint.x * 10, bb.minPoint.y * 10, bb.maxPoint.y * 10,
                 bb.minPoint.z * 10, bb.maxPoint.z * 10])
    return got


def check(design, adsk_fusion):
    v = values(design)
    worst, bad = place_check(bodies_by_number(design.rootComponent), v)
    tl = design.timeline
    unhealthy = [tl.item(i).name for i in range(tl.count)
                 if tl.item(i).healthState != adsk_fusion.FeatureHealthStates.HealthyFeatureHealthState]
    return {"checked": len(A.units()), "worst": round(worst, 3), "bad": bad, "unhealthy": unhealthy}


def union_box(v=None):
    v = v if v is not None else A.evaluate()
    bs = [[A.ev(v, e) for e in bx] for _k, _n, bx in A.layout()]
    return [min(b[0] for b in bs), min(b[2] for b in bs), min(b[4] for b in bs),
            max(b[1] for b in bs), max(b[3] for b in bs), max(b[5] for b in bs)]
