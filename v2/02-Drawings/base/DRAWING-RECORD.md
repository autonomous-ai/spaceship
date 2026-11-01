# Drawing record: BASE (P01, P02)

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-BASE-DR | P02 | DRAFT | 2026-11-01 | BASE Engineer |

Where each BASE drawing comes from. D-139 and D-158: every part drawing comes from the drawing generator (`tools/drawgen`, BASE's entries in `tools/drawgen/teams/base.py`), drawn from the part's STEP of the same revision; Fusion draws only what the generator can't draw yet, and the team says which and why first. Every sheet gets a Reviewer's visual pass (D-114). Each sheet and its PDF name Autonomous as the creator, never a person (D-140).

## From the generator

| Part | Mode | Note |
|---|---|---|
| 111101, 111102 (side bands) | part | datum B the front spigot rivnut hole (Ø10.00, D-163) |
| 111103 (back band) | part | datum B the spigot rivnut hole nearest X −102.75 |
| 111106 (FR1) | part | corner datums: the bottom face, the keyed end plate, the outer face |
| 110000, 110101, 110102, 110103, 110104, 110106 | assembly | sections through the hidden keys, glides and spigots |
| 111301 (the welded sill) | assembly (weldment) | its two members and the weld note |
| 111302 (the sill's bent profile) | bent sheet | waits for the generator's countersink callout (the Lead's ruling of 2026-11-01: the Drawing Generator Engineer adds it first; until then the generator refuses the part rather than draw plain holes) |

## No drawing (D-89 part 4: a flat part cut from sheet; its DXF and its full parts-list row)

111601 (the load block), 111111 (the tube end cap, D-165), 111303 (the sill's door-end plate).

## In Fusion, said first (the Lead's ruling of 2026-11-01)

| Part | Why the generator can't draw it yet | Sheet |
|---|---|---|
| 111105 (FL2) | The full round on its hinge-side plate's back edge (the PM's hinge-side ruling): the generator can't size a round edge | one Fusion sheet, in one short run after rebuild F, from FL2's part design in its own axes (CS-111105) |
| 111602 (the levelling glide, D-164) | A turned part with a hex socket: the generator has no mode for turned parts | one Fusion sheet, in the same run |
| 111104 (FL1) | Its datums can't be placed: all its side faces lie off the pod's axes | one Fusion sheet, in the same run, from FL1's part design in its own axes (CS-111104) |

The Joints Engineer's parts (the corner keys 111211 to 111215, the spigot 831001) are on Joints' own sheets.
