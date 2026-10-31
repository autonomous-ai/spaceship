# Drawing record: V2-SWL-00 proof panel (frame V2-SWL-10 + skin V2-SWL-20)

Phase 0 proof. **DRAFT P01, not for manufacture.**

- PDF: `V2-SWL-00_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_DWG.pdf` (A2, cleaned: see "Personal data")
- Render checked by eye: `V2-SWL-00_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_DWG-render.png` (150 dpi)
- Native drawing: Fusion cloud, Default Project / FocusPod v2 / `V2-SWL-00_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_DWG`, made from the design's version 1
- Made 2026-10-31 on Mac 1, Fusion 2706.1.17, by `make_drawing.py` (steps below)

## How it was made

| Step | How | Result |
|---|---|---|
| Start the drawing | Fusion's Create Drawing command, started by script with the Data Panel on Default Project; **one OK click and one Cancel click** (Base View dialog) by the Lead through macOS accessibility. These two clicks are the only steps outside the API | ISO, mm, first-angle drawing |
| Sheet | `step=save`: sheet set to A2, saved into FocusPod v2 | A2 landscape 594 x 420 mm |
| Front view | `step=front`: base view "Front" (looks along +Y: the frame from inside the pod), 1:5, centred at (330, 255) mm | 180..480 x 140..370 mm |
| View from above | `step=top`: base view "Top", 1:5, aligned below the front view (first angle). The API can't make projected views; the PM ruled aligned base views are fine | 180..480 x 77.7..82.3 mm, 4 hole circles |
| View from the right | `step=right`: base view "Right" (from +X, the back of the pod), 1:5, aligned left of the front view (first angle) | 107.7..112.3 x 140..370 mm, 4 hole circles |
| Dimensions | `dims_front`, `dims_top`, `dims_right`: linear dimensions from view geometry: datum corners (line ends) to hole centres (circle centre points), baseline style | 14 dimensions: 1470, 30, 1150, 565; holes 60 / 510 / 960 / 1410 from datum C and 10 from datum A; holes 60 / 403.33 / 746.67 / 1090 from datum B and 10 from datum A |
| Hole tables | Fusion hole tables on the two side views, origins on the datum corners | View from the right: 4 rows, tags A1-A4 on the view. View from above: table came out empty |
| Projection symbol | Sheet sketch, lines and circles: truncated cone, narrow end left, end view circles on the right (ISO first angle) | Drawn above the title block |
| Export | `step=export`: PDF to `.raw/` (git-ignored), then `tools/fusion/pdf_clear_field.py` | Repo PDF without the account holder's name |

## Checks (CAD and render checks; nothing here is a physical test)

| Check | Result |
|---|---|
| ISO, first-angle, projection symbol | Pass: ISO drawing standard (first-angle); symbol drawn. Its layout follows the sources below |
| Holes dimensioned to centres from datums | Pass: every hole dimension starts on a datum corner of the view and ends on the circle's centre point; values match the model |
| Holes are true circles | Pass: the view curves are circles (type Circle), and they render round at 150 dpi |
| Hole table tags match the view | Partial: tags A1-A4 match the view from the right. The view-from-above table is empty, and tags can't be set to H01... by API. The H01-H12 list is in `FEATURE-RATIONALE.md` |
| Title block filled | Fail by API: values come from document properties the API can't set. Title, sheet and date are filled; part no., rev, status, scale and material are not |
| No overlaps | Fail: the two stock hole tables and one blank table sit at the top right, over the front view's top-right corner. The API can't move, fill or delete them |
| Readable at A2 | Pass for views and dimensions (render checked); tables as above |
| Personal data | Pass after cleaning: "Created by" value removed from the text layer; checked by re-reading the PDF |

## For the Lead to click (the API can't)

1. Delete the two stock hole tables and the blank table at the top right.
2. Fill the title block: DWG No. V2-SWL-00, Rev P01, Document status DRAFT, Document type ASSEMBLY DRAWING; clear "Created by".
3. Optional: add the general notes (units, datums and 2D axis mapping per view, scoped tolerance proposal: see `make_drawing.py` NOTES).
4. Save, then save the cleaned sheet as our drawing template (Fusion's "New Drawing Template" / "Output Drawing Template" commands), so later drawings can start from it.
5. Sections A-A (through H01) and B-B (through H09) at 2:1: the API can't create section views.

Then re-export: `make_drawing.py --arg step=export` and `pdf_clear_field.py`.

## Sources for the projection symbol

- RMIT Learning Lab, mechanical drawings, views: first-angle symbol has the view from the left drawn to the right of the front view. https://learninglab.rmit.edu.au/dlsweb/Toolbox/electrotech/toolbox1204/resources/03workshop/02drawings/03views.htm
- ISO 128-3:2020 preview (clause 4.7, first-angle symbol). https://webstore.ansi.org/preview-pages/ISO/preview_ISO+128-3-2020.pdf
