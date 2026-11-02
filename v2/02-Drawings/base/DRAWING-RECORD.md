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
| 110000, 110101, 110102, 110103, 110106 | assembly | sections through the hidden keys, glides and spigots |
| 110104 (DL's band assembly) | assembly | its entry is in; the sheet is out until the generator's curve fix (#412): with main's generator its balloon 6 ends 0.1 mm off the stud head's ellipse in section D, so its read-back fails, and a sheet that fails its read-back doesn't ship (the Lead's ruling of 2026-11-01) |
| 111301 (the welded sill) | assembly (weldment) | its two members and the weld note |
| 111302 (the sill's bent profile) | bent sheet | follows in its own PR (the Lead's ruling of 2026-11-01). Since #371 the generator draws it, with the inside radius 2 as its DXF and the Ø5.1 seat holes as rivnut holes, but its read-back fails on two layouts in the generator: the 19's extension line through the 17 in the section (Generator Engineer 2), and bend tags B2 to B4 crowded at 1:5 (the Drawing Generator Engineer) |

## No drawing (D-89 part 4: a flat part cut from sheet; its DXF and its full parts-list row)

111601 (the load block), 111111 (the tube end cap, D-165), 111303 (the sill's door-end plate).

## In Fusion, said first (the Lead's ruling of 2026-11-01)

| Part | Why the generator can't draw it yet | Sheet |
|---|---|---|
| 111105 (FL2) | The full round on its hinge-side plate's back edge (the PM's hinge-side ruling): the generator can't size a round edge | one Fusion sheet, in one short run after rebuild F, from FL2's part design in its own axes (CS-111105) |
| 111602 (the levelling glide, D-164) | A turned part with a hex socket: the generator has no mode for turned parts | one Fusion sheet, in the same run |
| 111104 (FL1) | Its datums can't be placed: all its side faces lie off the pod's axes | one Fusion sheet, in the same run, from FL1's part design in its own axes (CS-111104) |

The Joints Engineer's parts (the corner keys 111211 to 111215, the spigot 831001) are on Joints' own sheets.

## How the Fusion sheets are made

Each sheet in one held queue place (`zsh v2/02-Drawings/base/run_drawings.sh PN`): `tools/fusion/start_drawing.py` makes the empty A3 drawing from the part's own design (FL1 and FL2 in their own axes, CS-111104 and CS-111105, so their views run along the tube); `base_drawings.py` adds the base views (first angle), the overall and hole-centre dimensions, the hole table and the projection symbol, and exports the raw PDF; `finish_pdfs.py` adds the notes as text on the right (the views take the left half), fills the title block, and makes the creator and the PDF's author Autonomous, with no maker line (D-140, D-147).

| Sheet | Views | Dimensions |
|---|---|---|
| 111104 FL1 | front, from above (hidden lines: the knee key's fixing holes), from the left (the corner end plate's 2 keyholes), iso; 1:1 | 123.24 and 100 (front), 40 (end), the keyhole seats 27.5 then 34 (end); the end cuts 65.86° and 82.75° to the outer face; hole table A1, A2 (Ø7) |
| 111105 FL2 | front, from above (the hinge-side plate and pad in plan; the glide's holes), from the left (the knee end plate's 2 keyholes), iso; 1:2 | 207.48 and 100 (front), 141.16 (end), the keyhole seats 27.5 then 34 (end); the end cuts 82.75° (the knee) and 62.8° (the door end) to the outer face; hole table A1 (Ø8), B1 (Ø13.5) |
| 111602 glide | front (hidden lines: the socket), from above; 2:1 | 60 overall, 7.61 base, 6 socket depth; Ø40, Ø10, 5 across flats |

## What went wrong and was fixed

- The first sheets (16:00 UTC) put the views from above on the notes, and the glide's front view got no heights: Fusion reports a turned part's edges seen edge-on not as horizontal lines, so the heights now come from the outline's vertical lines. The notes moved to the right, the views to the left half. The first versions are renamed `_SUPERSEDED-2026-11-01` (never deleted, D-141) and drawn again (16:33 to 16:39).
- FL2's end-view height ran into the notes; its views moved 10 left and it was drawn again (the earlier version renamed).
- FL1 and FL2 again (17:37 to 17:45 UTC, the Lead's two flags): each size is now printed once and each end cut carries its angle. Drawn as kind "facet" (`base_drawings.py`): the length and the height on the front view; the width and the keyhole seats on the end view, as one chain (27.5, then 34: a stack of two didn't fit beside these views, and the seats' heights come from the slots' straight sides, which end at the seats' centres, since the keyholes on a turned plate are ellipses with no centre); each end cut's angle to the outer face in the view from above, between the outer edge and the cut's line (Fusion's angle runs between two lines of one view, so it gives 82.75° to the outer face for the knee's 7.25° off square; the notes give both); the holes' positions in the hole table only. Before, the end views' keyhole dimensions measured to arc centres Fusion approximates (20.61 and 20, 121.35 and 121.16), FL2's 100 and 1.9 came twice from its door-end plate's full round, and FL1's corner angle text sat on a hole dimension. Checked offline first against both parts' STEPs projected with the same hidden-line removal (the same corner points as Fusion's to 0.01). FL2's knee angle was drawn again nearer its corner (at 20 its text crossed the inner edge). The versions before are renamed `_SUPERSEDED-2026-11-01-2` to `-4`, never deleted.
- FL2's two coaxial holes (A1 Ø8 in the top wall over B1 Ø13.5 in the bottom wall) got their tags on top of each other: `finish_pdfs.py` writes such tags side by side on the first one's line; nothing else on the sheet moves.
- The PDF trap check (C05) on the three Fusion sheets: no dimension printed twice; hidden lines in the views from above (FL1, FL2: the bottom wall's holes for the hole table) and the glide's front view (its socket), on purpose.
