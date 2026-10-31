# Drawing record: joint hardware we make (P01)

Two drawings, as the PM approved (2026-10-31): the corner key family on one TABULATED sheet (D-89 part 1), and the spigot. The stop washer 831002 has no drawing: it is flat and cut from sheet, on its DXF and its full row (D-89 part 4; the mechanical check accepts it).

| Drawing (Default Project / FocusPod v2 / joints, and the PDF here) | Covers | Sheet | Views (base views, first-angle, one scale) | Dimensions |
|---|---|---|---|---|
| `831001_P01_HARDWARE-LOCATING-SPIGOT_DWG` | 831001 | A3 | front (elevation, hidden lines) and from above, 5:1 | 6 |
| `111211_P01_BASE-CORNER-KEY-TABULATED_DWG` | **TABULATED** 111211, 111212, 111213, 111214, drawn as the square 111211 | A3 | front (hidden lines), from the right (the stud face) and from above (hidden lines), 2:1 | 11 |

## How they are made

1. `tools/fusion/start_drawing.py DESIGN DWG --folder "Default Project/FocusPod v2/joints" --sheet A3`: the empty drawing, saved and closed.
2. `tools/fusion/run_script.py v2/02-Drawings/joints/joints_drawing.py --arg part=spigot,keys`: one run for both drawings. It checks the screen is unlocked (an open drawing on a locked screen has hung Fusion), opens each drawing itself, updates it to the design's newest version, adds the base views and the dimensions planned by `plan_dims` (tested offline in `test_joints_drawing.py`), draws the first-angle symbol, exports the raw PDF to `.raw/` (git-ignored), saves and closes it.
3. `python3 v2/02-Drawings/joints/joints_drawing.py finish spigot|keys`, locally: `tools/fusion/pdf_clear_field.py` removes the "Created by" name, the notes go in as PDF text in the sheet's free top-right area, and a PNG render is made.

**Why the notes are PDF text:** the drawing API can't write free text on a sheet (custom table cells come out blank, `tools/fusion/README.md`). So units, material, finish, ISO 2768-m, the hole notes (H01 to H04) and the tabulated table (cut angle, hand, long and short side, count per pod, for each part number) are added to the PDF from the notes in `joints_drawing.py`. Every dimension is native.

**Sizes shown at their thread sizes:** Fusion draws a cosmetic thread at its standard size. The key's tapped holes show as Ø5.04 (6H mean minor; tap drill Ø5.0), and the spigot's stud as 5.88 (6g mean major of M6). The notes say so.

## What went wrong and was fixed

- The first key sheet had a dimension between the two hidden fixing-hole circles that showed the sheet distance (28 for 14). Its two points had no link to the model, and the API can't delete or edit a dimension. That drawing (minutes old, our own) was deleted and drawn again in one held session, with the dimension taken from the view's corner instead (24.5), as the other hole dimensions are.
