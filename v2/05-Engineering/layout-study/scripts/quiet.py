"""Re-check of parts, pallets and assembly time for the quiet build (Lead's ruling, 2026-10-31).

The Hardware Engineer's sound curve puts the best value near 380 kg in total: smoked acrylic front, wall cavities
deepened to 40-60 mm and filled. This study does not size the sound build. It adds an even areal mass to the wall
(and, in one case, ceiling) panels until the pod reaches the target total, deepens the frames and the walls by
dt mm, and checks the 20 kg part limit, the pallets and the assembly time. The outside size stays the same; the
inside shrinks by 2 x dt in width and dt in depth.
"""
from assembly import sequence, timing
from inputs import override, p
from pallets import pack, summary
from v2_model import FAST, parts_for, total, variant

LAYOUTS = (("plan", False, "plan split, sound mass inside the panels"),
           ("rows3", False, "3 rows per wall, sound mass inside the panels"),
           ("plan", True, "plan split, sound mass on separate inner leaves"))


def quiet_build(x, ceiling=True, leaf=False):
    return variant(FAST, key="quiet", front="acrylic10", sound_kgm2=x, ceiling_sound=ceiling, leaf=leaf)


def solve_mass(split, target, dt, ceiling=True, leaf=False):
    """Extra areal mass (kg/m2) on the wall (and ceiling) panels that brings the pod to the target total."""
    with override(wall_t_plan=p("wall_t_plan") + dt, frame_depth=p("frame_depth") + dt):
        lo, hi = 0.0, 40.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if total(parts_for(split, quiet_build(mid, ceiling, leaf))) < target:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2


def check(split, target, dt, ceiling=True, leaf=False):
    x = solve_mass(split, target, dt, ceiling, leaf)
    with override(wall_t_plan=p("wall_t_plan") + dt, frame_depth=p("frame_depth") + dt):
        m = quiet_build(x, ceiling, leaf)
        parts = parts_for(split, m)
        pals = pack(parts)
        s = summary(pals)
        t = timing(sequence(split, m, parts, False, s["n_std"], s["n_long"]))
        heavy = sorted((pt for pt in parts if pt.ship not in ("glass", "none")), key=lambda pt: -pt.kg)
        over = [pt for pt in heavy if pt.kg > 20.0]
        return dict(split=split, leaf=leaf, dt=dt, target=target, ceiling=ceiling, x=x, total=total(parts), heaviest=heavy[0], parts=parts,
                    over=over, pallets=pals, sum=s, time=t,
                    std_gross=max((pl["gross"] for pl in pals if pl["kind"] == "48x40"), default=0.0),
                    long_gross=max((pl["gross"] for pl in pals if pl["kind"] == "96x48"), default=0.0))


def quiet_rows():
    rows = []
    for target in (p("quiet_total"), p("quiet_cap")):
        for dt in (20, 40):
            for ceiling in (True, False):
                for split, leaf, _ in LAYOUTS:
                    rows.append(check(split, target, dt, ceiling, leaf))
    return rows
