# Drawing record: V2-SWL-00 proof panel (frame V2-SWL-10 + skin V2-SWL-20)

Phase 0 proof. **DRAFT P01, not for manufacture.** Status: waiting for the first sheet (one person action); the script part is ready and tested offline.

## How the drawing is made

1. A person starts the drawing once in Fusion: open Default Project / FocusPod v2 / `V2-SWL-00_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH`, then File > New Drawing > From Design: ISO, mm, A2 landscape. Placing a Front base view at 1:5 is optional. Save it in the same folder.
2. With that drawing active: `python3 tools/fusion/run_script.py v2/02-Drawings/proof/make_drawing.py`. The script adds the views, hole tables, dimensions, notes and the parts list, and exports the PDF next to this file.
3. The PDF is rendered to PNG and checked by eye (true circles, no overlaps, readable at A2).

Why a person: Fusion's API can't start a drawing on this install. Manual creation needs a template with view placeholders (`RuntimeError: 3 : Manual drawing creation requires a template with view placeholder information.`), none exists, and automatic creation hung. The API also can't save a drawing as a template (`DrawingDocument.saveAs` writes `.f2d`; exports are PDF, DWG and DXF only). Details: `tools/fusion/README.md`.

## Sheet content (planned; checked against the PDF after the run)

| Item | How | Guideline |
|---|---|---|
| ISO, first-angle, mm | Drawing standard ISO (first-angle by definition), units mm | 3.1, 3.2 |
| Front view from inside the pod, 1:5 | Base view, Fusion "Front" (looks along +Y: the frame from inside) | 5, 6.1 |
| View from above, below the front view | Base view "Top" at the same scale, aligned (the API can't make projected views; the PM ruled aligned base views are fine) | 3.2 |
| View from the right, left of the front view | Base view "Right" at the same scale, aligned | 3.2 |
| Hole positions | Linear dimensions from the datum corner to each hole centre (circle centre points), baseline style, no chains | 6.2 |
| Hole tables | Hole table 1 on the view from above (rail holes), hole table 2 on the view from the right (rear stile holes), origins on the datum corners | 6.2 |
| Overall sizes | Frame 1470 x 1150, skin overhang 30, mid rail at 565 | 6.1 |
| Notes | Units, projection, datums A/B/C, 2D axis mapping per view, hole list, scoped general tolerance proposal, sections left for a person | 3.3, 6.3 |
| Parts list | Built from the CAD at run time: part numbers, English and Vietnamese names, material, lengths, masses | 4.2 |
| Title block | Filled by Fusion from the design properties (part number, description). The API can only place title block tags, not set their text | 13 |

## Left for a person (no API)

- Section A-A through H01 and section B-B through H09, both 2:1, showing the Ø6.6 hole through both tube walls. The API can't create section views, and a scripted cut can't be labelled or hatched (sheet sketches have no text or hatch).

## Results

To be filled after the run: revision, PDF path, PNG check.
