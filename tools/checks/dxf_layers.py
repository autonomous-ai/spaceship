"""Which layers a DXF draws on: the one reader for D-89 part (4), shared by the mechanical check
(tools/checks/c_drawings.py) and the release checklist (v2/00-Control/build_release_checklist.py), so the two
tools can't drift. Change it here only, and run both tools' tests.

Standard library only; reads ASCII DXF without a DXF library.

The rule (PM rulings, 2026-11-01, logged in D-89):
- What a DXF draws is its ENTITIES section. The records BLOCK, ENDBLK, VERTEX and SEQEND are not lines.
- A stored block counts only where the drawing places it with an INSERT, nested inserts included, and its
  shapes on layer 0 take the INSERT's layer. So the arrow-head blocks a DXF library writes and never places
  don't count.
- A flat part's DXF may draw only on the CUT and MARK layers (guideline section 9); any other layer (BEND, a
  pocket, an engraving, a half-lap) keeps its drawing.
"""

ALLOWED = ("CUT", "MARK")
RECORDS = ("BLOCK", "ENDBLK", "SEQEND", "VERTEX", "ENDSEC", "EOF")


def drawn_layers(text):
    """The layers a DXF draws on, upper-cased, from its ENTITIES and the blocks they place; None when the text
    can't be read as ASCII DXF (empty or binary)."""
    if not text or not text.strip() or text.startswith("AutoCAD Binary DXF"):
        return None
    lines = text.splitlines()
    pairs = [(lines[i].strip(), lines[i + 1].strip()) for i in range(0, len(lines) - 1, 2)]
    sec, ent, block, naming, blocks, drawn = None, None, None, False, {}, []
    for k, (code, val) in enumerate(pairs + [("0", "EOF")]):
        if code == "0":
            if ent is not None and sec == "ENTITIES":
                drawn.append(tuple(ent))
            elif ent is not None and sec == "BLOCKS" and block:
                blocks.setdefault(block, []).append(tuple(ent))
            v, ent, naming = val.upper(), None, False
            if v == "ENDSEC":
                sec, block = None, None
            elif sec == "BLOCKS" and v == "BLOCK":
                block, naming = None, True
            elif sec == "BLOCKS" and v == "ENDBLK":
                block = None
            elif sec in ("ENTITIES", "BLOCKS") and v not in RECORDS:
                ent = [v, "0", ""]
        elif code == "2" and k and pairs[k - 1] == ("0", "SECTION"):
            sec = val.upper()
        elif code == "2" and naming:
            block, naming = val.upper(), False
        elif code == "2" and ent is not None and ent[0] == "INSERT":
            ent[2] = val.upper()
        elif code == "8" and ent is not None:
            ent[1] = val.upper()

    def placed(name, layer, seen):
        out = set()
        for typ, lay, ref in ([] if name in seen else blocks.get(name, [])):
            own = layer if lay == "0" else lay
            out.add(own)
            if typ == "INSERT":
                out |= placed(ref, own, seen | {name})
        return out

    layers = set()
    for typ, lay, ref in drawn:
        layers |= {lay} | (placed(ref, lay, frozenset()) if typ == "INSERT" else set())
    return layers


def other_layers(text, allowed=ALLOWED):
    """D-89 (4): the drawn layers other than CUT and MARK; None when the DXF can't be read, so the part can't be
    shown flat."""
    layers = drawn_layers(text)
    return None if layers is None else {x for x in layers if x not in allowed}
