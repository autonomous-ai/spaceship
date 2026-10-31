"""Pack each option onto standard pallets only: 48 x 40 in (upright panels) and 96 x 48 in (long pieces, glass).

Rules (from the plan): panels stand upright on 48 x 40 with their length along the 48 in side;
loaded height at most about 6 ft; long pieces and glass lie flat on a 96 x 48 pallet; no custom sizes.
"""
import math
import os

from inputs import p

LB_PER_KG = 2.20462
IN_PER_MM = 1 / 25.4


def upright_limits():
    return p("pal_std_l"), p("max_load_h") - p("pal_std_h") - p("pack_cap_h")   # along, up


def orient_upright(dims):
    """(along, up, thick) for a part standing on edge on a 48x40, or None if it cannot."""
    t = min(dims)
    a, b = sorted(dims)[1:]
    max_along, max_up = upright_limits()
    options = [(x, y) for x, y in ((a, b), (b, a)) if x <= max_along and y <= max_up]
    if not options:
        return None
    along, up = min(options, key=lambda o: (o[0], o[1]))   # shortest along-length first, so parts can share a slot
    return along, up, t


def units(parts):
    out = []
    for pt in parts:
        if pt.ship == "none":
            continue
        for i in range(pt.qty):
            out.append(pt)
    return out


def carton_for(boxes):
    """One kit carton holding the bought parts and fixings, standing in the 48x40 stack."""
    vol = sum(b.dims[0] * b.dims[1] * b.dims[2] for b in boxes) * 1e-9
    along, up = 1200.0, 600.0
    depth = math.ceil(1.3 * vol / (along * up * 1e-6) * 1000 / 10) * 10   # 30 % void, rounded up to 10 mm
    return dict(pid="KIT-CARTON", label="kit carton: " + ", ".join(sorted({b.pid for b in boxes})),
                along=along, up=up, t=float(depth), kg=sum(b.kg for b in boxes) + 1.5)


def pack(parts):
    """Returns a list of pallets. Each pallet: kind, slots or layers, gross kg, loaded height mm."""
    upright, longs, glass, boxes = [], [], [], []
    for u in units(parts):
        if u.ship == "box":
            boxes.append(u)
        elif u.ship == "glass":
            glass.append(u)
        elif u.ship == "upright" and orient_upright(u.dims):
            along, up, t = orient_upright(u.dims)
            upright.append(dict(pid=u.pid, label=u.name, along=along, up=up, t=t, kg=u.kg))
        else:
            longs.append(u)
    long_pallet = bool(longs or glass)
    if boxes and not long_pallet:
        upright.append(carton_for(boxes))

    # ---- 48 x 40: slots across the 40 in depth, items side by side along the 48 in length
    usable = p("pal_std_w") - 2 * p("edge_board")
    upright.sort(key=lambda d: (-d["t"], -d["up"], d["pid"]))
    pallets, cur = [], None
    for it in upright:
        need = it["t"] + p("pack_gap")
        placed = False
        if cur:
            for s in cur["slots"]:
                if s["t"] == it["t"] and s["used"] + it["along"] <= p("pal_std_l"):
                    s["items"].append(it); s["used"] += it["along"]; placed = True
                    break
        if not placed:
            if cur is None or cur["depth"] + need > usable:
                cur = dict(kind="48x40", slots=[], depth=0.0)
                pallets.append(cur)
            cur["slots"].append(dict(t=it["t"], used=it["along"], items=[it]))
            cur["depth"] += need
    for pal in pallets:
        items = [i for s in pal["slots"] for i in s["items"]]
        pal["net"] = sum(i["kg"] for i in items)
        pal["gross"] = pal["net"] + p("pal_std_kg") + p("pack_kg_std")
        pal["height"] = p("pal_std_h") + max(i["up"] for i in items) + p("pack_cap_h")
        pal["L"], pal["W"] = p("pal_std_l"), p("pal_std_w")

    # ---- 96 x 48: long pieces flat in layers across the 48 in width, glass on top in its own frame
    if longs or glass:
        pal = dict(kind="96x48", layers=[], L=p("pal_long_l"), W=p("pal_long_w"))
        flat = []
        for u in longs:
            a, b, c = sorted(u.dims, reverse=True)     # length, width, height when lying flat
            if a > p("pal_long_l"):
                raise ValueError(f"{u.pid} is {a} mm long: too long for a 96 in pallet")
            flat.append(dict(pid=u.pid, label=u.name, l=a, w=b, h=c, kg=u.kg))
        flat.sort(key=lambda d: (-d["w"], -d["l"], d["pid"]))
        for it in flat:
            for lay in pal["layers"]:
                if lay["used"] + it["w"] <= p("pal_long_w") and not lay.get("glass"):
                    lay["items"].append(it); lay["used"] += it["w"]; lay["h"] = max(lay["h"], it["h"])
                    break
            else:
                pal["layers"].append(dict(items=[it], used=it["w"], h=it["h"]))
        if boxes:
            # one long flat kit carton in the non-glass layer with the most free width, or a new layer
            vol = 1.3 * sum(b.dims[0] * b.dims[1] * b.dims[2] for b in boxes) * 1e-9
            L = 2400.0
            best = max(pal["layers"], key=lambda lay: p("pal_long_w") - lay["used"], default=None)
            free = p("pal_long_w") - best["used"] if best else 0.0
            h_need = math.ceil(vol / (L * free * 1e-6) * 1000 / 10) * 10 if free > 200 else None
            kit = dict(pid="KIT-CARTON", label="kit carton: " + ", ".join(sorted({b.pid for b in boxes})),
                       l=L, kg=sum(b.kg for b in boxes) + 1.5)
            if h_need is not None and h_need <= best["h"]:
                kit.update(w=free, h=h_need)
                best["items"].append(kit); best["used"] += free
            else:
                kit.update(w=600.0, h=float(math.ceil(vol / (L * 1e-3 * 0.6) * 1000 / 10) * 10))
                pal["layers"].append(dict(items=[kit], used=600.0, h=kit["h"]))
        if glass:
            g = [dict(pid=u.pid, label=u.name, l=max(u.dims), w=sorted(u.dims)[1], h=min(u.dims), kg=u.kg) for u in glass]
            pal["layers"].append(dict(items=g, used=max(x["w"] for x in g), h=p("glass_pack_h"), glass=True,
                                      under=p("sheet_under_glass") if pal["layers"] else 0.0))
        net = sum(i["kg"] for lay in pal["layers"] for i in lay["items"])
        extra = p("glass_frame_kg") if glass else 0.0
        pal["net"] = net
        pal["gross"] = net + extra + p("pal_long_kg") + p("pack_kg_long")
        pal["height"] = p("pal_long_h") + sum(lay["h"] + lay.get("under", 0.0) for lay in pal["layers"]) + p("pack_cap_h")
        pallets.append(pal)
    for pal in pallets:
        cuft = (pal["L"] * pal["W"] * pal["height"]) * IN_PER_MM ** 3 / 1728
        pal["cuft"] = cuft
        pal["lb"] = pal["gross"] * LB_PER_KG
        pal["pcf"] = pal["lb"] / cuft
    return pallets


def summary(pallets):
    lb = sum(x["lb"] for x in pallets)
    cuft = sum(x["cuft"] for x in pallets)
    return dict(n=len(pallets), n_std=sum(1 for x in pallets if x["kind"] == "48x40"),
                n_long=sum(1 for x in pallets if x["kind"] == "96x48"),
                kg=sum(x["gross"] for x in pallets), lb=lb, cuft=cuft, pcf=lb / cuft,
                max_h=max(x["height"] for x in pallets))


# ---------------------------------------------------------------- diagrams
def _svg_text(x, y, s, size=11, anchor="start", weight="normal"):
    s = str(s).replace("&", "&amp;").replace("<", "&lt;")
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" font-family="Helvetica, Arial, sans-serif">{s}</text>'


def svg(pal, title):
    """Plan view and elevation of one pallet, with a numbered legend. Scale 1:20 at 96 dpi-ish."""
    k = 0.2   # px per mm
    out = []
    W_px = 1000
    legend = []
    if pal["kind"] == "48x40":
        plan_w, plan_h = pal["L"] * k, pal["W"] * k
        ox, oy = 30, 70
        out.append(_svg_text(ox, oy - 10, "Plan view (48 in along X, 40 in along Y)", 11, weight="bold"))
        out.append(f'<rect x="{ox}" y="{oy}" width="{plan_w:.1f}" height="{plan_h:.1f}" fill="#f3e9d2" stroke="#7a5c2e"/>')
        y = p("edge_board")
        n = 0
        for s in pal["slots"]:
            x = (pal["L"] - s["used"]) / 2
            for it in s["items"]:
                n += 1
                out.append(f'<rect x="{ox + x * k:.1f}" y="{oy + y * k:.1f}" width="{it["along"] * k:.1f}" height="{max(s["t"] * k, 1.0):.1f}" fill="#c9d6ea" stroke="#1f3b63" stroke-width="0.6"/>')
                legend.append((n, it, s["t"]))
                x += it["along"]
            y += s["t"] + p("pack_gap")
        ex, ey = ox + plan_w + 60, 70
        H = pal["height"]
        out.append(_svg_text(ex, ey - 10, "End view (40 in across, height up)", 11, weight="bold"))
        base = ey + H * k
        out.append(f'<rect x="{ex}" y="{base - p("pal_std_h") * k:.1f}" width="{pal["W"] * k:.1f}" height="{p("pal_std_h") * k:.1f}" fill="#b08a55" stroke="#7a5c2e"/>')
        y = p("edge_board")
        n = 0
        for s in pal["slots"]:
            up = max(it["up"] for it in s["items"])
            n += len(s["items"])
            out.append(f'<rect x="{ex + y * k:.1f}" y="{base - (p("pal_std_h") + up) * k:.1f}" width="{max(s["t"] * k, 1.0):.1f}" height="{up * k:.1f}" fill="#c9d6ea" stroke="#1f3b63" stroke-width="0.6"/>')
            y += s["t"] + p("pack_gap")
        out.append(f'<line x1="{ex - 10}" y1="{base - H * k:.1f}" x2="{ex + pal["W"] * k + 10:.1f}" y2="{base - H * k:.1f}" stroke="#b00" stroke-dasharray="4 3"/>')
        out.append(_svg_text(ex + pal["W"] * k + 14, base - H * k + 4, f"{H:.0f} mm loaded", 10))
        lim = p("max_load_h")
        out.append(f'<line x1="{ex - 10}" y1="{base - lim * k:.1f}" x2="{ex + pal["W"] * k + 10:.1f}" y2="{base - lim * k:.1f}" stroke="#555" stroke-dasharray="1 3"/>')
        out.append(_svg_text(ex + pal["W"] * k + 14, base - lim * k + 4, f"{lim:.0f} mm limit", 10))
        top = max(oy + plan_h, base) + 30
    else:
        plan_w, plan_h = pal["L"] * k, pal["W"] * k
        ox, oy = 30, 70
        out.append(_svg_text(ox, oy - 10, "Plan view (96 in along X, 48 in along Y); layers drawn bottom to top", 11, weight="bold"))
        out.append(f'<rect x="{ox}" y="{oy}" width="{plan_w:.1f}" height="{plan_h:.1f}" fill="#f3e9d2" stroke="#7a5c2e"/>')
        colors = ["#c9d6ea", "#d9ead3", "#fde2c8", "#e6d3f0", "#f4cccc"]
        n = 0
        for li, lay in enumerate(pal["layers"]):
            y = 0.0
            for it in lay["items"]:
                n += 1
                x = (pal["L"] - it["l"]) / 2
                if lay.get("glass"):
                    y = 0.0
                out.append(f'<rect x="{ox + x * k:.1f}" y="{oy + y * k:.1f}" width="{it["l"] * k:.1f}" height="{it["w"] * k:.1f}" fill="{colors[li % 5]}" fill-opacity="0.55" stroke="#1f3b63" stroke-width="0.8"/>')
                out.append(_svg_text(ox + x * k + 4, oy + y * k + 12, str(n), 10, weight="bold"))
                legend.append((n, it, it["h"], li + 1))
                if not lay.get("glass"):
                    y += it["w"]
        ex, ey = ox, oy + plan_h + 50
        out.append(_svg_text(ex, ey - 8, "Side view (96 in along X, height up)", 11, weight="bold"))
        H = pal["height"]
        base = ey + H * k
        out.append(f'<rect x="{ex}" y="{base - p("pal_long_h") * k:.1f}" width="{pal["L"] * k:.1f}" height="{p("pal_long_h") * k:.1f}" fill="#b08a55" stroke="#7a5c2e"/>')
        z = p("pal_long_h")
        for li, lay in enumerate(pal["layers"]):
            z += lay.get("under", 0.0)
            Lmax = max(it["l"] for it in lay["items"])
            x = (pal["L"] - Lmax) / 2
            out.append(f'<rect x="{ex + x * k:.1f}" y="{base - (z + lay["h"]) * k:.1f}" width="{Lmax * k:.1f}" height="{lay["h"] * k:.1f}" fill="{colors[li % 5]}" stroke="#1f3b63" stroke-width="0.8"/>')
            out.append(_svg_text(ex + x * k + 4, base - (z + lay["h"] / 2) * k + 4, f"layer {li + 1}" + (" (glass)" if lay.get("glass") else ""), 9))
            z += lay["h"]
        out.append(f'<line x1="{ex - 5}" y1="{base - H * k:.1f}" x2="{ex + pal["L"] * k + 5:.1f}" y2="{base - H * k:.1f}" stroke="#b00" stroke-dasharray="4 3"/>')
        out.append(_svg_text(ex + pal["L"] * k + 8, base - H * k + 4, f"{H:.0f} mm loaded", 10))
        top = base + 30
        W_px = max(W_px, int(ox + plan_w + 120))
    # legend
    ly = top
    out.append(_svg_text(30, ly, "Legend (part id, size as stacked, kg each)", 11, weight="bold"))
    ly += 16
    for row in legend:
        n, it = row[0], row[1]
        if pal["kind"] == "48x40":
            txt = f'{n}. {it["pid"]}: {it["along"]:.0f} along x {it["up"]:.0f} up x {row[2]:.0f} thick, {it["kg"]:.1f} kg'
        else:
            txt = f'{n}. {it["pid"]} (layer {row[3]}): {it["l"]:.0f} x {it["w"]:.0f} x {row[2]:.0f}, {it["kg"]:.1f} kg'
        out.append(_svg_text(30, ly, txt, 10))
        ly += 14
    head = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W_px}" height="{ly + 20:.0f}" viewBox="0 0 {W_px} {ly + 20:.0f}">',
            '<rect width="100%" height="100%" fill="white"/>',
            _svg_text(30, 24, title, 14, weight="bold"),
            _svg_text(30, 42, f'{pal["kind"]} in pallet · gross {pal["gross"]:.0f} kg ({pal["lb"]:.0f} lb) · loaded height {pal["height"]:.0f} mm ({pal["height"] * IN_PER_MM:.1f} in) · {pal["pcf"]:.1f} lb/ft3', 11)]
    return "\n".join(head + out + ["</svg>", ""])


def write_svgs(pallets, option_key, outdir):
    names = []
    for i, pal in enumerate(pallets, 1):
        fn = f"pallets-{option_key}-{i}-{pal['kind']}.svg"
        with open(os.path.join(outdir, fn), "w") as f:
            f.write(svg(pal, f"Option {option_key}, pallet {i} of {len(pallets)}"))
        names.append(fn)
    return names
