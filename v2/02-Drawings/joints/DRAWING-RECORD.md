# Drawing record: joint hardware we make (P01)

Two drawings, as the PM approved (2026-10-31): the corner key family on one TABULATED sheet (D-89 part 1), and the spigot. The stop washer 831002 has no drawing: it is flat and cut from sheet, on its DXF and its full row (D-89 part 4; the mechanical check accepts it).

| Drawing (Default Project / FocusPod v2 / joints, and the PDF here) | Covers | Sheet | Views (base views, first-angle, one scale) | Dimensions |
|---|---|---|---|---|
| `831001_P01_HARDWARE-LOCATING-SPIGOT_DWG` | 831001 | A3 | front (elevation, hidden lines) and from above, 5:1 | 6 |
| `111211_P01_BASE-CORNER-KEY-TABULATED_DWG` | **TABULATED** 111211, 111212, 111213, 111214, drawn as the square 111211 | A3 | front (hidden lines), from the right (the stud face) and from above (hidden lines), 2:1 | 11 |

## How they are made

1. `tools/fusion/start_drawing.py DESIGN DWG --folder "Default Project/FocusPod v2/joints" --sheet A3`: the empty drawing, saved and closed.
2. `tools/fusion/run_script.py v2/02-Drawings/joints/joints_drawing.py --arg part=spigot,keys`: one run for both drawings. It checks the screen is unlocked (an open drawing on a locked screen has hung Fusion), opens each drawing itself, updates it to the design's newest version, adds the base views and the dimensions planned by `plan_dims` (tested offline in `test_joints_drawing.py`), draws the first-angle symbol, exports the raw PDF to `.raw/` (git-ignored), saves and closes it.
3. `python3 v2/02-Drawings/joints/joints_drawing.py finish spigot|keys`, locally: the shared `tools/fusion/pdf_clear_field.py` removes the "Created by" name and fills the title block (DWG No., Rev., Document status and Title, `pdf_title_block.py`; the key sheet's title names the family); the notes go in as PDF text in the sheet's free top-right area at 2.5 mm capitals, the tabulated sizes as a table; on the key sheet the hole tags and thread callouts go at the holes and view B (111212 from above) is drawn; then a PNG render is made.

**Why the notes are PDF text:** the drawing API can't write free text on a sheet (custom table cells come out blank, `tools/fusion/README.md`). So units, material, finish, ISO 2768-m, the hole notes (H01 to H04) and the tabulated table (cut angle, hand, long and short side, count per pod, for each part number) are added to the PDF from the notes in `joints_drawing.py`. Every dimension is native.

**Sizes shown at their thread sizes:** Fusion draws a cosmetic thread at its standard size. The key's tapped holes show as Ø5.04 (6H mean minor; tap drill Ø5.0), and the spigot's stud as 5.88 (6g mean major of M6). The notes say so.

## What went wrong and was fixed

- The first key sheet had a dimension between the two hidden fixing-hole circles that showed the sheet distance (28 for 14). Its two points had no link to the model, and the API can't delete or edit a dimension. That drawing (minutes old, our own) was deleted and drawn again in one held session, with the dimension taken from the view's corner instead (24.5), as the other hole dimensions are.

## The key sheet, drawn again (2026-11-01)

- **One held Fusion session**, 01:56 to 01:59 UTC: the first drawing deleted, a new one started on the design's version 2, then annotated: 3 views and 11 dimensions, all native and linked to the model.
- **Read back from the PDF:** front 30 and 75; from the right 35, 17.5, 26, 60 and Ø5.04 (the stud holes); from above 30, 10.5, 10.5 and 24.5 (the fixing holes, 14 apart) and Ø5.04. No dimension shows a sheet distance.
- **"Created by" cleared** with the fix in #214 to `tools/fusion/pdf_clear_field.py`: Fusion wrote today's date with a one-digit day (1/11/26), which the tool took as part of the name; with the fix the name goes and the date stays.
- **Checked:** `test_joints_drawing.py` 0 failures; the PDF carries UNITS MM, the material, finish, ISO 2768-m, H01 to H04, TABULATED and all four part numbers (the mechanical check's drawing rules, C05). A Reviewer's visual pass follows (D-114).

## Reviewer 5's D-114 pass on the key sheet, and the fixes (2026-11-01)

The sheet matched the STEP (block 30 x 35 x 75, holes at 26 and 60, the bottom holes 10.5 from the back face and 7 either side, first-angle views). Four fixes, all in the local finish step, so no new Fusion run:

1. **Title block:** DWG No., Rev. and Document status were blank and Title showed the design's file name. The shared finish step now fills them for every team (`tools/fusion/pdf_title_block.py`, run by `pdf_clear_field.py`): 111211, P01, DRAFT and "BASE - CORNER KEY - TABULATED: 111211, 111212, 111213, 111214"; the spigot's sheet takes 831001, P01, DRAFT and its name from the master BOM.
2. **Hole tags at the holes** (guideline 6.2): H01 and H02 "M6x1-6H THRU" at the stud face's holes, H03 and H04 "M6x1-6H 15 DEEP" at the bottom holes, each with a leader to its circle. The finish step finds the circles in the PDF itself (solid ones as curves, hidden ones from their dashes, which must go all round) and refuses if two tags would pick one hole.
3. **111212 drawn** as view B, 2:1, from above: the cut face at A = 24.14° to the square position, measured at the long end, the long side 37.84 and the short side 22.16, the stud holes square to the cut face (hidden) with their axis, and the bottom holes. It is drawn in the PDF from the model's sizes, because the drawing's design is saved as 111211 and Fusion can't show a second cut on one sheet; it was checked against `111212_P01_..._STEP.step` (the stud holes' axis is (-0.9125, -0.409, 0), the long side on -Y). Note 3 says 111213 is 111212's opposite hand.
4. **Notes at 2.5 mm capitals** (Helvetica, was 2.05), wrapped inside the box, the table with real columns.

The Lead's drawing check from CEILING's sample, on these two sheets: no inserted pictures; the first-angle symbol draws right; two views made as visible-only show hidden lines anyway (the key's stud-face view shows the bottom holes, the spigot's top view the stud), which Fusion does when the style is set at creation, and both add information, so they stay; no dimension is placed twice.

Offline: `test_joints_drawing.py` now also checks the notes' letter height and box, finding a solid and a hidden circle but not a hidden cone's dashes, and view B's sizes (0 failures).
