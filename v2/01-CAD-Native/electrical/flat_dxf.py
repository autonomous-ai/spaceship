"""A flat part's DXF, written from its outline sketch: plain ASCII DXF (R12), in mm ($INSUNITS 4), every
line and circle on the CUT layer and nothing else, so it meets D-89 part 4 (a flat sheet part's DXF draws
only on the CUT and MARK layers) and the shop's laser software reads it as cut lines.

Standard library only; the Fusion build (electrical_parts_cad.py) and the offline test both use it.
"""

LAYER = "CUT"


def _pairs(code_values):
    return "".join("%s\n%s\n" % (c, v) for c, v in code_values)


def dxf_text(lines, circles, layer=LAYER):
    """lines: [((x1, y1), (x2, y2))], circles: [((cx, cy), r)], all in mm."""
    if not lines and not circles:
        raise ValueError("nothing to write")
    out = [_pairs([(0, "SECTION"), (2, "HEADER"), (9, "$ACADVER"), (1, "AC1009"),
                   (9, "$INSUNITS"), (70, 4), (0, "ENDSEC")])]
    out.append(_pairs([(0, "SECTION"), (2, "TABLES"),
                       (0, "TABLE"), (2, "LTYPE"), (70, 1),
                       (0, "LTYPE"), (2, "CONTINUOUS"), (70, 0), (3, "Solid line"), (72, 65), (73, 0), (40, "0.0"),
                       (0, "ENDTAB"),
                       (0, "TABLE"), (2, "LAYER"), (70, 2),
                       (0, "LAYER"), (2, "0"), (70, 0), (62, 7), (6, "CONTINUOUS"),
                       (0, "LAYER"), (2, layer), (70, 0), (62, 1), (6, "CONTINUOUS"),
                       (0, "ENDTAB"), (0, "ENDSEC")]))
    ents = [(0, "SECTION"), (2, "ENTITIES")]
    for (x1, y1), (x2, y2) in lines:
        ents += [(0, "LINE"), (8, layer), (10, "%.4f" % x1), (20, "%.4f" % y1), (30, "0.0"),
                 (11, "%.4f" % x2), (21, "%.4f" % y2), (31, "0.0")]
    for (cx, cy), r in circles:
        if r <= 0:
            raise ValueError("circle radius must be positive")
        ents += [(0, "CIRCLE"), (8, layer), (10, "%.4f" % cx), (20, "%.4f" % cy), (30, "0.0"), (40, "%.4f" % r)]
    ents += [(0, "ENDSEC"), (0, "EOF")]
    out.append(_pairs(ents))
    return "".join(out)


def write(path, lines, circles, layer=LAYER):
    text = dxf_text(lines, circles, layer)
    with open(path, "w", encoding="ascii", newline="\n") as fh:
        fh.write(text)
    return len(lines), len(circles)
