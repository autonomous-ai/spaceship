#!/usr/bin/env python3
"""Write the ELECTRICAL P01 documents from the model and parts data.

    python3 v2/05-Engineering/electrical/electrical_docs.py          # write everything
    python3 v2/05-Engineering/electrical/electrical_docs.py --check  # write nothing; fail if a file is stale

Reads `v2/01-CAD-Native/electrical/electrical_model.py` (routes) and
`electrical_parts.py` (parts, harnesses, loads). Writes:

- v2/03-Manufacturing/electrical/710000_P01_ELECTRICAL-PARTS-LIST_BOM.csv
- v2/03-Manufacturing/electrical/710000_P01_ELECTRICAL-HARNESS-LIST_SPEC.csv
- v2/05-Engineering/electrical/710000_P01_ELECTRICAL-LOAD-TABLE_CALC.csv
- v2/05-Engineering/electrical/calc-results.md (voltage drop, supply loading, heat, mass)
- v2/02-Drawings/electrical/710000_P01_ELECTRICAL-WIRING-DIAGRAM_DWG.pdf (2 sheets, A3)
  and a PNG of each sheet (_IMG) for review and for the Fusion drawing's sheet image.

Standard library plus PyMuPDF (already used by tools/fusion/pdf_clear_field.py).
"""

import argparse
import csv
import io
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CAD = os.path.join(REPO, "v2", "01-CAD-Native", "electrical")
sys.path.insert(0, CAD)
import electrical_model as M  # noqa: E402
import electrical_parts as EP  # noqa: E402

OUT_BOM = "v2/03-Manufacturing/electrical/710000_P01_ELECTRICAL-PARTS-LIST_BOM.csv"
OUT_HARNESS = "v2/03-Manufacturing/electrical/710000_P01_ELECTRICAL-HARNESS-LIST_SPEC.csv"
OUT_LOAD = "v2/05-Engineering/electrical/710000_P01_ELECTRICAL-LOAD-TABLE_CALC.csv"
OUT_CALC = "v2/05-Engineering/electrical/calc-results.md"
OUT_PDF = "v2/02-Drawings/electrical/710000_P01_ELECTRICAL-WIRING-DIAGRAM_DWG.pdf"
OUT_PNG = "v2/02-Drawings/electrical/710000_P01_ELECTRICAL-WIRING-DIAGRAM-SHEET%d_IMG.png"

RHO_CU = 0.0178        # ohm mm2 / m, copper at 20 C (source: standard value)
RHO_CU_60 = RHO_CU * (1 + 0.00393 * 40)   # at 60 C conductor temperature (calculation)
V_BUS = 12.0


def csv_text(header, rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    for r in rows:
        w.writerow([("" if r.get(h) is None else r.get(h)) for h in header])
    return buf.getvalue()


def fmt(x, nd=3):
    if x is None or x == "":
        return ""
    if isinstance(x, (int,)) and not isinstance(x, bool):
        return str(x)
    s = ("%." + str(nd) + "f") % x
    return s.rstrip("0").rstrip(".") if "." in s else s


# ------------------------------------------------------------------ parts list
def parts_rows():
    """Parts list rows with qty per pod and assembly masses rolled up."""
    parts = EP.P
    by_pn = {}
    for key, p in parts.items():
        by_pn.setdefault(p["part_number"], []).append(key)
    dup = [pn for pn, ks in by_pn.items() if len(ks) > 1]
    if dup:
        raise SystemExit("duplicate part numbers in electrical_parts.py: %s" % dup)
    children = {}
    for key, p in parts.items():
        children.setdefault(p["parent"], []).append(key)
    qty_pod = {}

    def walk(pn, mult):
        for k in children.get(pn, []):
            q = parts[k]["qty_per_parent"] * mult
            qty_pod[k] = qty_pod.get(k, 0) + q
            walk(parts[k]["part_number"], q)
    top = [k for k, p in parts.items() if p["parent"] == ""]
    for k in top:
        qty_pod[k] = 1
        walk(parts[k]["part_number"], 1)
    mass = {}

    def m(k):
        if k in mass:
            return mass[k]
        p = parts[k]
        if p["kind"] == "HS":
            tot = 0.0
            for c in children.get(p["part_number"], []):
                tot += parts[c]["qty_per_parent"] * m(c)
            mass[k] = tot
        else:
            mass[k] = p["mass_each_kg"] or 0.0
        return mass[k]
    rows = []
    order = []

    def walk_order(pn):
        for k in children.get(pn, []):
            order.append(k)
            walk_order(parts[k]["part_number"])
    for k in top:
        order.append(k)
        walk_order(parts[k]["part_number"])
    for k in order:
        p = parts[k]
        r = dict(p)
        r["qty_per_pod"] = fmt(qty_pod.get(k, 0), 3)
        r["qty_per_parent"] = fmt(p["qty_per_parent"], 3)
        r["mass_each_kg"] = fmt(m(k), 4)
        r["unit"] = EP.unit_of(k)
        r["revision"] = M.REV
        rows.append(r)
    return rows, m, qty_pod


BOM_HEADER = ["part_number", "name", "name_vi", "kind", "parent", "qty_per_parent", "qty_per_pod", "unit",
              "material", "grade", "finish", "mass_each_kg", "mass_status", "maker", "sku", "size", "length_mm",
              "torque_nm", "process", "revision", "status", "source", "note"]


# ------------------------------------------------------------------ routes and harness lengths
def route_lengths(v):
    """Centre-line lengths of the modelled route segments, mm (calculation from the model)."""
    out = {}
    for b in M.BODIES:
        x0, y0, z0, x1, y1, z1 = M.body_box(b, v)
        out[b["code"]] = max(x1 - x0, y1 - y0, z1 - z0)
    return out


def harness_rows(v):
    rows = []
    for h in EP.harnesses(v):
        r = dict(h)
        L = h["length_mm"]
        a = h.get("amps_max")
        area = h.get("area_mm2")
        if a and area and h["circuit"] not in ("mains 220 V", "PE", "LAN"):
            loop = 2 * L / 1000.0 * RHO_CU_60 / area / h.get("parallel", 1)
            r["drop_v"] = fmt(a * loop, 3)
            r["drop_pct"] = fmt(100 * a * loop / V_BUS, 2)
        rows.append(r)
    return rows


HARNESS_HEADER = ["id", "harness_pn", "segment", "function", "from", "to", "route", "circuit", "conductors",
                  "cable", "area_mm2", "parallel", "length_mm", "length_status", "end_a", "end_b",
                  "grommets", "amps_max", "drop_v", "drop_pct", "note"]


# ------------------------------------------------------------------ load table
LOAD_HEADER = ["id", "load", "supply", "fuse", "qty", "w_each_max", "w_total_max", "w_each_typical",
               "w_total_typical", "a_total_max_12v", "w_status", "source", "note"]


def load_rows():
    rows = []
    for (lid, name, sup, fuse, qty, wmax, wtyp, st, src, note) in EP.LOADS:
        rows.append(dict(id=lid, load=name, supply=sup, fuse=fuse, qty=qty, w_each_max=fmt(wmax, 2),
                         w_total_max=fmt(qty * wmax, 2), w_each_typical=fmt(wtyp, 2),
                         w_total_typical=fmt(qty * wtyp, 2), a_total_max_12v=fmt(qty * wmax / V_BUS, 3),
                         w_status=st, source=src, note=note))
    return rows


def supply_summary():
    out = []
    for sid, _key, _o, rated, _amps, feeds, _why in EP.SUPPLIES:
        wmax = sum(q * w for (_i, _n, s, _f, q, w, _t, _st, _src, _no) in EP.LOADS if s == sid)
        wtyp = sum(q * t for (_i, _n, s, _f, q, _w, t, _st, _src, _no) in EP.LOADS if s == sid)
        out.append((sid, rated, wmax, wtyp, 100.0 * wmax / rated, feeds))
    return out


def calc_md(v, mass_of, harness):
    sup = supply_summary()
    tot_max = sum(s[2] for s in sup)
    tot_typ = sum(s[3] for s in sup)
    rated = sum(s[1] for s in sup)
    eff = EP.PARTS_DATA["ps_eff"]
    noload = EP.PARTS_DATA["ps_noload_w"]
    loss_typ = sum(s[3] / eff - s[3] for s in sup) + noload * len(sup)
    loss_max = sum(s[2] / eff - s[2] for s in sup) + noload * len(sup)
    ac_in_max = tot_max / eff + noload * len(sup)
    lines = []
    A = lines.append
    A("# ELECTRICAL P01: calculation results")
    A("")
    A("| Doc code | Revision | Status | Date | Owner |")
    A("|---|---|---|---|---|")
    A("| V2-ENG-ELE-03 | P01 | DRAFT, written by `electrical_docs.py` | %s | ELECTRICAL Engineer |" % EP.DATE)
    A("")
    A("Every number here is a **calculation** from the load table (`710000_P01_ELECTRICAL-LOAD-TABLE_CALC.csv`), "
      "the harness list and the route model, unless marked. Inputs carry their own status in those files.")
    A("")
    A("## 1. Supply loading (12 V)")
    A("")
    A("| Supply | Rated W | Load max W | Load typical W | Max load / rating | Feeds |")
    A("|---|---:|---:|---:|---:|---|")
    for sid, r, wm, wt, pct, feeds in sup:
        A("| %s | %.0f | %.1f | %.1f | %.0f %% | %s |" % (sid, r, wm, wt, pct, feeds))
    A("| **All** | **%.0f** | **%.1f** | **%.1f** | %.0f %% | REQ-ELE-03: about 125 W load, supply at least 150 W |" % (
        rated, tot_max, tot_typ, 100 * tot_max / rated))
    A("")
    A("Typical = one or two people, lights full, fans near the 53 l/s normal flow, no voice kit fitted. "
      "Max = every load at its maximum at once, which the control never asks for (the fans reach full speed only "
      "above the 65 l/s boost).")
    A("")
    A("## 2. Mains side")
    A("")
    A("- Supplies' input at maximum load: %.0f W at %.0f %% efficiency (assumption from the maker's typical "
      "figure, parts list) plus %.1f W no-load each: about **%.2f A at 220 V**." % (
          ac_in_max, eff * 100, noload, ac_in_max / 220.0))
    A("- The RCBO is C10, 30 mA: 10 A x 220 V = 2.2 kW for the user socket and the supplies together. "
      "A laptop charger takes about 0.3 A; a 2 kW heater would still hold (9.1 A), which is the worst case a user "
      "might plug in (assumption).")
    A("- Mains conductors 1.5 mm² (H07V-K in the sleeve, 0.82 m): rated well above 10 A in free air "
      "(IEC 60364-5-52, to confirm by the factory's electrician); the RCBO protects them.")
    A("")
    A("## 3. Voltage drop on the 12 V circuits (copper at 60 °C, %.4f Ω mm²/m)" % RHO_CU_60)
    A("")
    A("Loop resistance = 2 x length x ρ / area, divided by the number of parallel pairs. Each segment carries its own "
      "maximum current (the loads beyond it at full power). Limit used: 3 % of 12 V from the supply to the farthest "
      "load (assumption; the fans start at 7 V and run to 13.2 V, and the strips are specified at 12 V).")
    A("")
    A("| Segment | Circuit | Length mm | Area mm² x pairs | Max A | Drop V |")
    A("|---|---|---:|---:|---:|---:|")
    by_id = {h["id"]: h for h in harness}
    for h in harness:
        if h.get("drop_v"):
            A("| %s %s | %s | %s | %s x %s | %s | %s |" % (h["id"], h["segment"], h["circuit"], h["length_mm"],
                                                        h["area_mm2"], h.get("parallel", 1), fmt(h["amps_max"], 2),
                                                        h["drop_v"]))
    A("")
    A("| Path, supply to the farthest load | Drop V | Drop % | 3 % limit |")
    A("|---|---:|---:|---|")
    for name, ids in EP.CIRCUIT_PATHS:
        d = sum(float(by_id[i]["drop_v"]) for i in ids)
        A("| %s (%s) | %.2f | %.1f | %s |" % (name, " + ".join(ids), d, 100 * d / V_BUS,
                                            "within" if d / V_BUS <= 0.03 else "**over**"))
    A("")
    A("Mains conductors are left out: 0.92 m of 1.5 mm² at the RCBO's full 10 A drops about 0.25 V of 220 V (0.1 %).")
    A("")
    A("## 4. Heat the electrical parts add inside the pod")
    A("")
    A("The supplies sit inside the pod (in the power unit), so their losses heat the pod air; the lights' and the "
      "hub's power is heat inside too, and so is the supply fans' power (it ends up in the supply air). The "
      "exhaust fans' power leaves with the exhaust.")
    A("")
    lights = sum(q * t for (_i, _n, s, _f, q, _w, t, _st, _src, _no) in EP.LOADS if _i in ("LD04", "LD05"))
    hub = sum(q * t for (_i, _n, s, _f, q, _w, t, _st, _src, _no) in EP.LOADS if _i == "LD03")
    fan_s = sum(q * t for (_i, _n, s, _f, q, _w, t, _st, _src, _no) in EP.LOADS if _i == "LD01")
    extra = loss_typ + hub + fan_s
    dT = extra / (1.2 * 1005 * 0.053)
    A("| Heat source, typical | W |")
    A("|---|---:|")
    A("| Lights (already in C4's 30 W) | %.1f |" % lights)
    A("| Supply losses, 3 units | %.1f |" % loss_typ)
    A("| Sensor hub | %.1f |" % hub)
    A("| Supply fan pair at 53 l/s | %.1f |" % fan_s)
    A("| **Not yet in C4's 240 W** (losses + hub + supply fans) | **%.1f** |" % extra)
    A("")
    A("At the 53 l/s normal flow that adds **%.2f K** to C4's 3.8 K (ΔT = P / (1.2 × 1005 × 0.053), calculation). "
      "The lights are %.1f W: the shelf capped at 71.5 %% (PM heat request) and the call light. With the voice kit at "
      "its 40 W average (D-88), the kit adds 40 W and its supply's loss about %.1f W more (calculation). For the Air "
      "Engineer's 4 K check (D-50)." % (dT, lights, 40 / eff - 40))
    A("")
    A("## 5. Mass")
    A("")
    pu = mass_of("pu")
    tot = mass_of("ele")
    groups = [("710001 power unit (with its mains wiring and fixings)", ["pu"]),
              ("710041 hub and controls zone", ["hubzone"]),
              ("710051 cord set (ships loose; counts in the pod as shipped)", ["cord"]),
              ("lights: shelf strip, call strip and profile", ["strip_shelf", "w_call"]),
              ("harness parts: cables, plugs, terminals, RJ45 parts, bushings, edge strip, clips, senses",
               [k for k, p in EP.P.items() if p["parent"] == "710000" and p["kind"] != "HS" and k != "strip_shelf"]
               + ["w_light", "w_trunk", "w_col", "w_draw"])]
    A("| Group | kg | Status |")
    A("|---|---:|---|")
    seen = 0.0
    for label, keys in groups:
        m = sum(mass_of(k) * (EP.P[k]["qty_per_parent"] if EP.P[k]["kind"] != "HS" else 1) for k in keys)
        seen += m
        A("| %s | %.2f | calculation (parts list: quantity x mass each, each mass with its own status) |" % (label, m))
    A("| **710000 ELECTRICAL** | **%.2f** | calculation; the layout study's roll-up carries 3.05 kg for switches, lights and harness (assumption) |" % tot)
    A("")
    if abs(seen - tot) > 0.005:
        raise SystemExit("mass groups %.3f don't add up to the total %.3f" % (seen, tot))
    b2 = EP.PARTS_DATA["b2_outer_kg"]
    A("**B2 with the power unit inside (D-03, at most 20 kg):** B2's outer panel about %.1f kg (calculation from "
      "CEILING's measured frame and skin masses per m², PR #32, scaled to B2's 1.343 m², plus 40 mm fill at "
      "25 kg/m³, D-81) + the power unit %.2f kg = **%.1f kg**, under 20 kg. WALL's own B2 mass replaces the first "
      "figure when B2 is modelled." % (b2, pu, b2 + pu))
    A("")
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------ main
def outputs():
    v = M.values()
    rows, mass_of, _q = parts_rows()
    harness = harness_rows(v)
    files = {
        OUT_BOM: csv_text(BOM_HEADER, rows),
        OUT_HARNESS: csv_text(HARNESS_HEADER, harness),
        OUT_LOAD: csv_text(LOAD_HEADER, load_rows()),
        OUT_CALC: calc_md(v, mass_of, harness),
    }
    return files, v, rows, harness


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="write nothing; exit 1 if a file differs")
    ap.add_argument("--no-pdf", action="store_true", help="skip the wiring diagram")
    opts = ap.parse_args()
    files, v, rows, harness = outputs()
    stale = []
    for rel, text in files.items():
        path = os.path.join(REPO, rel)
        old = open(path, encoding="utf-8").read() if os.path.exists(path) else None
        if old != text:
            stale.append(rel)
            if not opts.check:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8", newline="") as fh:
                    fh.write(text)
    if not opts.no_pdf and not opts.check:
        import wiring_diagram as WD
        WD.write(os.path.join(REPO, OUT_PDF), os.path.join(REPO, OUT_PNG), v, rows, harness)
        print("wrote %s and its sheet images" % OUT_PDF)
    for rel in stale:
        print(("stale: " if opts.check else "wrote: ") + rel)
    if opts.check and stale:
        sys.exit(1)


if __name__ == "__main__":
    main()
