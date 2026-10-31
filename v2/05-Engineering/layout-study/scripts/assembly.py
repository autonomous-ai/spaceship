"""Two-person assembly sequence, time estimate and bolt access check for each option.

Time model (all inputs are assumptions in inputs.py, to be replaced by the timed prototype trial):
a step's 2-person work (carrying long parts, setting panels on pins, glass, door) runs once with both people busy;
1-person work (bolts, connectors, felt) is shared, so it takes half the elapsed time; a hand-off and checking
allowance is added on top.
"""
import math

from inputs import p
from v2_model import CAM_JOINTS, connectors, joints

TOOL = ("one 5 mm T-handle hex key (M6 socket-head bolts into rivnuts; glides adjust from above with the same key). "
        "Handling aids, not tools: a small step stool and 2 suction lifters for the glass")


def _bolts(J, ids, frac=1.0):
    return int(round(sum(j[3] for j in J if j[0] in ids) * frac))


def sequence(split, m, parts, split_long, n_std, n_long):
    """List of steps: name, parts placed, lifts, bolts, cams, 2p seconds, 1p seconds, access note."""
    J = joints(split, m, split_long)
    t_bolt = p("t_bolt_captive_s") if m.get("captive") else p("t_bolt_s")
    t_place = p("t_place_hung_s") if m.get("cams") else p("t_place_s")

    def fix(ids, frac=1.0):
        """(bolts, cams, 1-person seconds) for a set of joints."""
        cams = _bolts(J, [i for i in ids if i in CAM_JOINTS], frac) if m.get("cams") else 0
        bolts = _bolts(J, ids, frac) - cams
        return bolts, cams, bolts * t_bolt + cams * p("t_cam_s")

    def qty(prefix):
        return sum(pt.qty for pt in parts if pt.pid.startswith(prefix))

    def carry_place(prefix, overhead=False):
        n = qty(prefix)
        two_p, one_p = 0.0, 0.0
        for pt in parts:
            if not pt.pid.startswith(prefix):
                continue
            heavy_or_long = pt.kg > 15 or max(pt.dims) > 1600
            carry = p("t_carry_s") * pt.qty
            if heavy_or_long:
                two_p += carry
            else:
                one_p += carry
            two_p += (p("t_place_overhead_s") if overhead else t_place) * pt.qty
        return n, two_p, one_p

    steps = []
    if m.get("ordered"):
        unpack = (n_std * p("t_unpack_std_ordered_min") + n_long * p("t_unpack_long_ordered_min")) * 60
    else:
        unpack = (n_std * p("t_unpack_std_min") + n_long * p("t_unpack_long_min")) * 60
    steps.append(dict(name="Unpack, check parts against the label list, stand the glass safely", lifts=0, bolts=0, cams=0,
                      two=unpack, one=0.0, access="-"))
    if m["floor"] == "raised":
        n, two, one = carry_place("B-RAIL")
        nj, tj, oj = carry_place("B-JOIST")
        b, c, tb = fix(("J-BASE-02",))
        steps.append(dict(name="Raised frame: bars, corner brackets, joists, 6 feet; level", lifts=n + nj, bolts=b, cams=c,
                          two=two + tj + p("t_level_min") * 60, one=one + oj + tb,
                          access="Corner bolts from above and inside before any wall stands on the frame."))
        n, two, one = carry_place("B-BOARD")
        screws = 2 * 8
        steps.append(dict(name="2 floor boards screwed to the joists (plan: screws, a second fastener and a driver)",
                          lifts=n, bolts=0, cams=0, two=two, one=one + screws * 20, access="From above, open."))
    else:
        n, two, one = carry_place("B-BAND")
        b, c, tb = fix(("J-BASE-02", "J-BASE-03"))
        steps.append(dict(name="Base band: 4 pieces and corner keys on 8 glides; level from above", lifts=n, bolts=b, cams=c,
                          two=two + p("t_level_min") * 60, one=one + tb,
                          access="Corner keys from above and inside; closed later by the wall panels, so bolted first."))
        if m["floor"] == "thin":
            n, two, one = carry_place("B-FLOOR")
            steps.append(dict(name="Seal mat and 2 thin floor panels dropped inside the band (no fixings)", lifts=n,
                              bolts=0, cams=0, two=two, one=one, access="-"))
    seam = "cam or clip connectors" if m.get("cams") else "bolts"
    if split in ("bands", "rows3"):
        n, two, one = carry_place("W-")
        b, c, tb = fix(("J-BASE-01", "J-WALL-01", "J-WALL-02", "J-WALL-03", "J-WALL-04"))
        rows = 5 if split == "bands" else 3
        steps.append(dict(name=f"Walls row by row from the bottom: back pair, then each side, {rows} rows", lifts=n, bolts=b, cams=c,
                          two=two, one=one + tb,
                          access="All from inside through open frame bays or the loose felt strips over the joints."))
    else:
        n, two, one = carry_place("W-BACK-LO")
        n3, two3, one3 = carry_place("W-BACK-FULL")
        n2, two2, one2 = carry_place("W-SIDE-LO")
        b, c, tb = fix(("J-BASE-01",))
        b2, c2, tb2 = fix(("J-WALL-03", "J-WALL-04"), 0.5)
        steps.append(dict(name=f"Lower walls: back pair on its pins, then the two sides; bolts to the band, {seam} at seam and corners",
                          lifts=n + n2 + n3, bolts=b + b2, cams=c + c2, two=two + two2 + two3, one=one + one2 + one3 + tb + tb2,
                          access="From inside through open frame bays, or behind the loose felt strip over each joint; hex key swings in the 1.2 m bays."))
        n, two, one = carry_place("W-BACK-UP")
        n2, two2, one2 = carry_place("W-SIDE-UP")
        b, c, tb = fix(("J-WALL-01", "J-WALL-02"))
        b2, c2, tb2 = fix(("J-WALL-03", "J-WALL-04"), 0.5)
        steps.append(dict(name=f"Upper walls: back pair, then sides; {seam} at horizontal seams, vertical seam and corners",
                          lifts=n + n2, bolts=b + b2, cams=c + c2, two=two + two2, one=one + one2 + tb + tb2,
                          access="As the lower walls; top fixings at 2.2 m need the step stool."))
    n, two, one = carry_place("C-HALF", overhead=True)
    b, c, tb = fix(("J-CEIL-01", "J-CEIL-02", "J-AIR-01"))
    fans_in_ceiling = m.get("stack") != "final"
    steps.append(dict(name="Ceiling halves lifted onto the walls from inside" + ("; fans and silenced vents from below" if fans_in_ceiling else ""),
                      lifts=n, bolts=b, cams=c, two=two, one=one + tb,
                      access="Upward from inside, ceiling felt (or its joint strips) not yet on" +
                             ("; fans mount from below through their opening." if fans_in_ceiling else ".")))
    n, two, one = carry_place("F-D")
    b, c, tb = fix(("J-FRONT-01", "J-FRONT-03", "J-AIR-02"))
    air = sum(pt.qty for pt in parts if pt.pid.startswith(("A-CART", "A-RISER")))
    steps.append(dict(name="Decor blocks (skins on, factory-made): left door post, right, then top"
                      + (f"; then {air} air parts slid into the right block from inside through its felt-covered access panel: "
                         "the supply and exhaust cartridges with their 12 V fans fitted, and the exhaust riser between them" if air else ""),
                      lifts=n + air, bolts=b, cams=c, two=two + air * 120, one=one + tb,
                      access="Through the front frame members of the side walls and ceiling from inside, behind the loose felt strips."))
    pre = m.get("prehung")
    b = 4
    lifters = " (2 people, 2 suction lifters)" if m.get("front") in ("lam44", "glass8", "glass10") else ""
    steps.append(dict(name="Fixed glass " + ("in its factory profile frame: set and fix" if pre else "into its sealed profiles") + lifters,
                      lifts=1, bolts=b, cams=0,
                      two=(p("t_fixed_preglazed_min") if pre else p("t_fixed_glass_min")) * 60 + p("t_carry_s"), one=b * t_bolt,
                      access="Profile frame bolted from inside; glass held by clip-in beads."))
    b = 6
    steps.append(dict(name="Door: " + ("hinges and pull fitted in the factory; lift onto the hinge pins, fit drop seal, adjust" if pre
                                       else "hinges on the left decor post, pull, drop seal; adjust swing") + lifters,
                      lifts=1, bolts=b, cams=0, two=(p("t_door_prehung_min") if pre else p("t_door_min")) * 60 + p("t_carry_s"),
                      one=b * t_bolt, access="Hinge bolts reachable with the door open 90 degrees."))
    nc = connectors(split)
    steps.append(dict(name=f"Electrics: {nc} plug-in connectors at panel seams, power in, test fans and lights",
                      lifts=0, bolts=0, cams=0, two=p("t_elec_min") * 60, one=nc * p("t_connector_s"),
                      access="Connectors sit in the open bays, or behind the loose strip, next to each seam."))
    if m.get("leaf"):
        n, two, one = carry_place("L-LEAF-SIDE")
        n2, two2, one2 = carry_place("L-LEAF-BACK")
        n3, two3, one3 = carry_place("L-LEAF-HALF", overhead=True)
        c1, ct1, co1 = carry_place("L-CASS-SIDE")
        c2, ct2, co2 = carry_place("L-CASS-BACK")
        c3, ct3, co3 = carry_place("L-CASS-HALF", overhead=True)
        n, two, one = n + c1 + c2, two + ct1 + ct2, one + co1 + co2
        n3, two3, one3 = n3 + c3, two3 + ct3, one3 + co3
        leaves = n + n2 + n3
        what = "lining cassettes (steel tray + felt)" if c1 + c2 + c3 else "inner leaves (sound mass + felt)"
        steps.append(dict(name=f"{leaves} {what} clipped on from inside, ceiling ones from below", lifts=leaves, bolts=0, cams=0,
                          two=two + two2 + two3, one=one + one2 + one3 + leaves * p("t_leaf_s"),
                          access="Close every bay and joint: last. Joints stay reachable until then."))
    elif m.get("prefit"):
        ns = sum(j[2] for j in J if j[0] in CAM_JOINTS or j[0] in ("J-CEIL-01",))
        steps.append(dict(name=f"Felt: {ns} loose strips over the joints (the rest came pre-fitted)", lifts=0, bolts=0, cams=0,
                          two=0.0, one=ns * p("t_felt_strip_s"), access="Closes the joints: last."))
    else:
        nf = qty("L-FELT")
        steps.append(dict(name=f"Felt lining: {nf} panels pressed onto Velcro", lifts=nf, bolts=0, cams=0, two=0.0,
                          one=nf * (p("t_felt_s") + p("t_carry_s") / 3), access="Closes every bay: last."))
    steps.append(dict(name="Threshold, final check of door swing and seals, clean", lifts=1, bolts=0, cams=0,
                      two=p("t_final_min") * 60, one=0.0, access="-"))
    for st in steps:
        st.setdefault("cams", 0)
    return steps


def timing(steps):
    two = sum(s["two"] for s in steps)
    one = sum(s["one"] for s in steps)
    elapsed = (two + one / 2) * (1 + p("inefficiency"))
    return dict(elapsed_min=elapsed / 60, person_h=2 * elapsed / 3600, bolts=sum(s["bolts"] for s in steps),
                cams=sum(s.get("cams", 0) for s in steps), lifts=sum(s["lifts"] for s in steps), steps=len(steps))


# ---------------------------------------------------------------- doorway
def corridor_turn_max(w1, w2):
    """Longest thin part that can be carried flat around a 90-degree corner between corridors w1 and w2 (mm)."""
    return (w1 ** (2 / 3) + w2 ** (2 / 3)) ** 1.5


def doorway(parts):
    rows = []
    seen = set()
    for pt in parts:
        if pt.ship == "none" or pt.pid in seen:
            continue
        seen.add(pt.pid)
        a, b, c = sorted(pt.dims)
        need_w = a + 2 * p("hand_clear")
        ok_nom = need_w <= p("door_w") and b <= p("door_h")
        ok_clear = need_w <= p("door_clear_w") and b <= p("door_h")
        rows.append(dict(pid=pt.pid, name=pt.name, dims=(c, b, a), kg=pt.kg, need_w=need_w, ok_nom=ok_nom,
                         ok_clear=ok_clear))
    return rows
