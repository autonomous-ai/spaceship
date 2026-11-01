# drawgen: part drawings from STEP, outside Fusion (D-112, D-113)

`drawgen` makes the manufacturing drawing of a simple part straight from that part's STEP on main: aluminium tube
cut parts and frames of them, flat plates, and blanks with square notches. It never opens Fusion or its queue.
Fusion keeps the general arrangement, the assemblies, bent parts, the door, the glass, the decor, and any part
drawgen refuses.

## Run it

```
tools/drawgen/run.sh generate --sample          # the five sample drawings, into v2/02-Drawings/<team>/
tools/drawgen/run.sh generate 211101 111101     # registered parts (tools/drawgen/specs.py)
tools/drawgen/run.sh check v2/02-Drawings/wall/211101_P01_WALL-PANEL-FRAME-SIDE-LOWER-LH_DWG.pdf
tools/drawgen/run.sh stale                      # generated drawings whose STEP, parts list or register changed
```

`run.sh` makes drawgen's own Python environment on first use, in a per-user cache (`DRAWGEN_VENV` moves it):
OCC 7.8 through `cadquery-ocp` and PyMuPDF, pinned in `requirements.txt`. Nothing is installed system-wide.
Tests: `<venv>/bin/python tools/drawgen/tests/test_drawgen.py` (prints `N of N passed`).

## What it reads

- The part's STEP: its own file (`v2/03-Manufacturing/<team>/PN_REV_NAME_STEP.step`), or the team assembly STEP
  that holds it. Fusion writes cm and says so (D-13); OCC reads it in mm and every drawing checks one box against
  the repo's own reader (`tools/checks/stepfile.py`). A part file in its own system (BASE's tubes) is drawn where
  it sits in the pod: the placement comes from the team assembly STEP, checked hole for hole, and the sheet says
  so.
- The team parts list row: name, Vietnamese name, material, finish, process, tolerance, mass, cut list.
- The feature rationale registers (`v2/02-Drawings/<team>/FEATURE-RATIONALE*.md`, both layouts in use): each
  hole's register ID, function and mating parts, in the hole tables.
- `specs.py`: the choices a STEP can't give (datums, extra notes, the tolerance note).

## What a drawing has (guideline 3.2, 3.3, 6; D-113)

- Exact projections with hidden-line removal (OCC `HLRBRep_Algo`, never the polygonal one): lines stay lines and
  circles stay circles, written as Bezier quarter arcs on their true centre and radius. Hidden lines that would
  print on top of a visible line are left out (ISO 128 practice); the rest are dashed.
- First-angle layout: the view from above below the principal view, from below above it, from the left on its
  right, from the right on its left; a view too long to sit beside goes under the others as a lettered view with
  a reference arrow.
- A view of every drilled face. A face nothing shows (inside a frame bay) gets a section in front of it, unless
  its holes are the far-wall twins of holes a view shows: then the removed section through the pair shows them.
- Holes through two walls of one member: a removed section through their axis, hatched per ISO 128-50 (filled
  solid under 1.6 mm on paper), each wall's hole sized across its gap.
- One hole table per face: tags H01... on the views, `X (mm)` and `Y (mm)` from that view's origin (O1, O2...,
  the one 3D origin seen in each view), +X right and +Y up, size, depth, the register's feature and fits. The view
  titles give each view's mapping to the pod axes.
- Datums: WALL frames sit on a spigot hole and slot (R-J13), so A is the seat face, B the round hole, C the slot,
  and every hole position is from B (R-J6). Other parts name their datum faces in `specs.py`.
- Mitred ends: the angle from square and the true length along each face.
- Frames: member balloons, the cut list from the parts list, stile positions, the D-115 joint note.
- Scale: the largest ISO scale at which the views fit beside the hole tables; for a long part the table column
  gets narrower (its text wraps more) before the scale drops, as long as the tables still end above the title block.
- Labels: every line is drawn first (views, cutting planes, dimensions), then hole callouts, view titles, tags,
  origin names and datum symbols each go where they touch no line and no other text.
- Title block: UNITS: mm, the first-angle symbol, part number, name (English and Vietnamese), revision of the
  part's STEP (or of its parts list when it lives in an assembly STEP), DRAFT, material, finish, mass, scale,
  sheet; the tolerance note is the project's (joints register, parts lists), never a blanket ISO 2768. No
  personal names. The PDF's Creator is `drawgen`; its catalog key `/DrawgenData` lists every source with its
  hash, the views and the tagged features.
- TABULATED drawings (D-89 part 1): one sheet for parts of one family (`tabulated.py`), each piece's size and
  notches read from its own STEP.

## What it refuses (the part stays with Fusion)

A cylinder that is neither a hole, a slot nor a keyhole (a bend, a fillet, a round), a cone (a countersink), any
other curved face, holes on a face at an angle to every principal view, an outline with a curve or an angled
edge on a tabulated blank, a part that fits no ISO scale on its sheet. It also never overwrites a PDF it didn't
make: a Fusion drawing stays.

## Checks

`readback.py` reads a drawing back against its STEP, independently of how it was drawn: every hole the repo's own
STEP reader finds is in a table, each row's X and Y equal the hole's projected centre within 0.05 mm, each tagged
hole is drawn as a true circle at its place within 0.05 mm, the text has what the mechanical check reads, the
Creator is drawgen, and no text touches another text or a part outline and no line runs through a text (read from
the PDF's own text and paths). `generate` runs it on every drawing it writes. The mechanical check's drawing rule (C05) and
the release checklist count the drawings by their file names, like any other drawing.
