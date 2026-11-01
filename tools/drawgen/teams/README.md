# Team entries: which parts drawgen draws (D-139)

Every part drawing comes from drawgen (D-139). Each team lists its own parts in its own file here,
`tools/drawgen/teams/<team>.py`. The file name is the team's folder name under `v2/03-Manufacturing/` and
`v2/02-Drawings/`. Each team edits its own file in its own PRs, so teams don't collide. Its first entries, and any
change to drawgen's code, are reviewed by drawgen's owner, and every drawing gets a reviewer's visual pass (D-114)
before it counts. `tools/drawgen/specs.py` gathers the files. The mechanical check (C05) and the release checklist
read the same list.

A file holds two dicts of plain data:

- `PARTS = {"111101": {...}}`: the parts drawgen draws, each with its entry (below).
- `NO_DRAWING = {"211501": "D-128: ..."}`: parts that need no drawing, each with the decision that says so.
  `generate` prints the reason instead of drawing them.

A number listed twice (in two files, or in both dicts) stops drawgen with an error.

## What an entry holds

Only what a STEP can't give. drawgen reads everything else each time it draws: views, sections, holes, sizes,
names, material, finish and revision come from the part's STEP, its parts-list row and the feature registers.

| Key | What it says | Example |
|---|---|---|
| `datums` | `"spigot"`: A the seat face, B a round spigot hole, C a face that stops the turn about B (joints register R-J6, R-J13). Leave it out for the corner scheme below. | `"spigot"` |
| `spigot_dia`, `spigot_pick` or `spigot_near`, `spigot_slot` | Which hole is B: its size, which one (`"-Y"`: nearest the front; `{"X": -102.75}`: nearest that pod coordinate), and whether the part also has the slot | `9.53`, `"-Y"`, `False` |
| `c_face`, `a_words`, `c_words` | Datum C's face, and the words naming A and C on the sheet | `"-X"`, `"top face (the wall seat, Z 110)"` |
| `corner`, `datum_words`, `datum_faces` | The corner scheme: origin at a corner of the part's faces, and the datum letters on given faces | `"-X-Y-Z"`, `{"A": "-Z"}` |
| `notes` | Notes for this part, each one sentence or two, with their source (a decision, a register line) | `["Both ends square (BASE tube cut list)."]` |
| `tolerance` | The tolerance note: the project's own values with their source, never a blanket ISO 2768 (guideline 3.2) | see `base.py` |
| `key_notes` | `True`: a note at each end that carries a key from Joints' `corner-keys.csv`, saying which way round it fits | `True` |
| `material_has`, `material_why` | The entry is written for this material: drawgen refuses to draw while the parts list says another (so welded-steel notes never go over an aluminium list) | `"steel"`, `"D-131's welded, galvanized steel frame"` |
| `principal`, `scale`, `sheet` | Only when the default choice is wrong: the principal view, the ISO scale, the sheet size | `"right"`, `0.2`, `"A1"` |

## Adding a part

1. Add its entry to your team's file. Start from a similar part's entry.
2. Draw it: `tools/drawgen/run.sh generate <pn>`. The read-back runs on it and must pass: every hole in a table
   within 0.05 mm of the STEP, true circles, no text touching text or an outline, no line through a text.
3. Look at the PDF at print size. Then open a PR with the entry and the PDF, and ask for the visual pass.

When drawgen refuses a part (bent or folded, a fillet, a countersink, holes square to a face no view looks at
straight), the refusal says why. The part goes to Fusion for now, with that reason, and the gap goes to drawgen's
owner.
