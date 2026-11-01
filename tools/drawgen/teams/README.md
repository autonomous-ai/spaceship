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
| `rivet_holes` | Hole sizes that take rivets, each with its rivet: the tapped-hole guard passes them (3.3, 4.2 and about 5.0 are tap drills' sizes too) and their table rows name the rivet. A parts-list row that says tapped or threaded is still refused | `{4.2: "blind rivet, Ø4 (D-130)"}` |
| `bent` | The part is bent or folded sheet: drawn from its STEP and its DXF (`<pn>_*_DXF.dxf` in the team's folder), with a bend table. `True` when the model has its bend radii; a model that folds sharp gives its inside radius and where it comes from | `True`, `{"radius": 1.0, "radius_why": "INTERIOR's brake tooling"}`, `{"vgroove": "90° V on the back, leaving the outer skin (ACP maker's guide)", "outside_radius": 2}` for a V-grooved and folded ACP panel: its model must have each fold's outside radius, and `outside_radius` (optional) is the one every fold must have |
| `material_has`, `material_why` | The entry is written for this material: drawgen refuses to draw while the parts list says another (so welded-steel notes never go over an aluminium list) | `"steel"`, `"D-131's welded, galvanized steel frame"` |
| `cut_list` | A welded frame whose members are their own parts (D-120, D-162): `file`, its team's cut list CSV (columns `frame`, `member_part`, `name`, `section`, `length_mm`, `qty`, `ends`, and `holes` when present); its rows for the frame become the sheet's cut list, one per member number, each named as its parts-list row names it (the file's own name only for a member with no row). Each member number's bodies under the frame must equal its quantity, both ways; a number with two lengths, two ends texts or two pairs of end angles, and a bought part under the frame, are refused. With `end_a_deg` and `end_b_deg` (FRONT's), the model check takes each end's cuts from them: a cell's steepest is the body's steepest at that end, and the cuts a cell gives ('50.9 and 0.0 (two cuts)') are that end's cut faces, both ways; an ends text that gives both angles must agree with them. End A is the end its ends text names ('left end (A)', 'lower front end (A)'), in pod axes (left -X, right +X, front -Y, back +Y, lower -Z, upper +Z), and its cuts must be that end's; a row whose two ends differ must name it. `lean` 'opposite' (the cuts lean apart: mirror images) or 'parallel' (parallel cut planes) is checked against the model too. `welded_in`: made parts welded in that aren't in the cut list (mitre plates), counted against their parts-list rows | `{"file": "410000_P01_CEILING-TUBE-CUT-LIST_BOM.csv", "welded_in": ["831007", "831008"]}` |
| `principal`, `scale`, `sheet` | Only when the default choice is wrong: the principal view, the ISO scale, the sheet size | `"right"`, `0.2`, `"A1"` |

## Adding a part

1. Add its entry to your team's file. Start from a similar part's entry.
2. Draw it: `tools/drawgen/run.sh generate <pn>`. The read-back runs on it and must pass: every hole in a table
   within 0.05 mm of the STEP, true circles, no text touching text or an outline, no line through a text.
3. Look at the PDF at print size. Then open a PR with the entry and the PDF, and ask for the visual pass.

When drawgen refuses a part (bent or folded without a `bent` entry, a fillet, a countersink, holes on an angled face the part hides, a
flat-faced feature it can't size such as a step or a pocket), the refusal says why and names the faces. The part goes to Fusion for now, with that reason, and the gap goes to drawgen's
owner.
