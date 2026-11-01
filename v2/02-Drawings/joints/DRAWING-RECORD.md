# Drawing record: joint hardware we make (P01)

Two drawings, as the PM approved (2026-10-31): the corner key family on one TABULATED sheet (D-89 part 1), and the spigot. The stop washer 831002 has no drawing: it is flat and cut from sheet, on its DXF and its full row (D-89 part 4; the mechanical check accepts it).

| Drawing (Default Project / FocusPod v2 / joints, and the PDF here) | Covers | Sheet | Views (base views, first-angle, one scale) | Dimensions |
|---|---|---|---|---|
| `831001_P01_HARDWARE-LOCATING-SPIGOT_DWG` | **TABULATED** 831001 and 831010 (since 2026-11-01), drawn as 831001 | A3 | front (elevation, hidden lines) and from above, 5:1 | 6 |
| `111211_P01_BASE-CORNER-KEY-TABULATED_DWG` | **TABULATED** 111211, 111212, 111213, 111214, 111215, drawn as the square 111211 with its D-144 holes | A3 | front (hidden lines), from the right (the stud face) and from above (hidden lines), 2:1 | 12 |

**The key sheet is back (D-144, 2026-11-01).** #300 took its old version out of the repo (D-147 (3)); this redraw on the key design's version 3 replaces it. How it was drawn is below.

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

## The key sheet for D-144 (2026-11-01)

D-144 stepped 111211's fixing holes ((10.5, +6) and (17.8, −6)) and added 111215 (FR1's square key, the first holes); D-147 (3) took the old sheet out until this redraw. The sheet is Fusion's under D-139 and D-143 (a five-part tabulated sheet with tapped holes, which the generator refuses until their callouts land), said to the Lead before the run.

**In Fusion:**
- **08:19 UTC, a slip:** a first D-144 redraw deleted the drawing it replaced instead of renaming it, against D-141 (ruled 06:55); the delete step was older than the rule and wasn't rechecked. Owned to the Lead. Only this sheet; its PDF is in git at 084217c.
- **09:26 UTC:** that redraw (its version 2) renamed `111211_P01_BASE-CORNER-KEY-TABULATED_DWG_SUPERSEDED-2026-11-01` (D-141), a new sheet started on the key design's version 3 and annotated: 3 views, 12 dimensions.
- **10:09 UTC, after the visual pass below:** that sheet renamed `111211_P01_BASE-CORNER-KEY-TABULATED_DWG_SUPERSEDED-2026-11-01-2`, a new one started on version 3 and annotated with the right view 8 to the right: 3 views, 12 dimensions, all native and linked to the model. Every step in one held session, with the exact-mitre STEP export (the build record).

**Layout, from D-144's bigger table and my visual pass:**
- Front and right views 6 up (sheet y 191) to widen the gap over the top view; the front view's 30 above it; the stepped hole's 10.5 above the top view, in that gap; both its y dimensions (11.5, 23.5) on the left, so the tags have the right side.
- H03 and H04 tags right of the top view, lifted so the lower one ends 3.5 above the title block (at the holes' height H03 ended 1 from it); the first-angle symbol moved right (x 252).
- The right view 8 right (x 88): its 60, stacked left of the 26, read back at x 18.7 on the frame line (19.98); now 26.7. `test_joints_drawing.py` now checks that every dimension sits inside the frame with room for its text (it fails with the view back at x 80).
- Note 3 writes (A=0) so it can't split over a line; view B's angle label starts past its face line, which crossed the A; view B drawn at the mitre's exact −24.1446° (its sizes don't change at 0.01).
- The finish finds the stepped holes' hidden circles with a 1.6 join (at 3.5 they merged with the stud holes' hidden lines).

**Read back from the PDF:** right view 17.5, 26, 60, 35, Ø5.04; front 75, 30; top 10.5 and 17.8 (the holes' x), 11.5 and 23.5 (their y), Ø5.04; view B 22.16, 37.84, A = 24.14°. Created by and the PDF's author read "Autonomous"; no maker named in the notes (D-147 (1)).

**Checks:** `test_joints_drawing.py` 0 failures; the mechanical check against main closes the key sheet's no-drawing findings for 111211 to 111215 and 111215's missing STEP (the pull request's checks). A Reviewer's D-114 visual pass follows.

## Reviewer 6's D-114 pass on the D-144 key sheet (#324), and the fixes (2026-11-01)

Reviewer 6 checked each key against its STEP (111212 to 111215 pass; 111211 matched except for the P2) and held #324 on one P2, with P3s for the redo:

- **P2, the hole names:** the top view tagged (10.5, +6) H04 and (17.8, −6) H03, against the table's H03 (10.5, +6) and H04 (17.8, −6). Anyone settling that by the table's sign would mirror 111211's stepped pattern, and a mirrored key doesn't fit. Fixed in the finish step: H03 on the upper hole, H04 on the lower; note 5 now says **+Y up in the top view**. `test_joints_drawing.py` places the top view's holes and checks that each tag picks the hole the table gives it (it fails with the old names).
- **Ø5.04 twice, and as a size tighter than 6H allows:** both diameter dimensions dropped (native, the redo below); the M6x1-6H callouts carry the size, and note 4 says the views draw the tapped holes at the thread's minor diameter. This also clears the mechanical check's "printed twice" finding.
- **Y from the side face, the note's ±0.1 from the centre line:** the drawing API can't place a centre line that a dimension attaches to (it has centre line and mark settings only), and a dimension between two hidden circles' centres once showed the sheet distance (above). So the top view keeps its dimensions from the −Y side face, and note 5 now says so: it gives Y from that face (17.5 + Y) and puts the ±0.1 on the back face and that face. With the block's width at ISO 2768-m, the holes stay within about ±0.25 of the centre line, inside the band's Ø7.0 holes' ±0.5.
- **Note 3:** 111213 is now "the opposite hand of view B's shape, at its own A" (24.02°, not 24.14°). **Note 1** gives the scale, 2:1, view B too.
- **Hidden circles for H03 and H04:** kept. In first-angle projection a view from below sits above the front view, where the A3 sheet has no room at 2:1, and each hidden circle carries its tag and the table's position.

**The redo in Fusion (D-139: the tabulated key sheet stays Fusion's):**
- **11:47 UTC:** the 10:09 sheet renamed `111211_P01_BASE-CORNER-KEY-TABULATED_DWG_SUPERSEDED-2026-11-01-3` (D-141). Fusion's Server Verification Warning was up, and Create Drawing never opened, so the run stopped there with no new sheet. Nothing from that run is used (the Lead's steer).
- **12:22 UTC:** a new sheet started on the key design's version 3 and annotated in one held session: 3 views, 10 dimensions (the two Ø5.04 gone), all native and linked to the model.
- **The finish:** one more note line had closed the 4 mm and two note lines that `finish()` keeps between the notes and view B, so it stopped. Notes 3 and 4 are shorter (same facts), and view B sits 4 lower (it still ends 5 above the title block). `test_joints_drawing.py` now checks that gap, and view B's room above the title block, from the sheet's own settings, so a longer note fails the test before a finish.

**Read back from the PDF:** right view 17.5, 26, 60, 35; front 75, 30; top 10.5 and 17.8 (x), 11.5 and 23.5 (y); view B 22.16, 37.84, A = 24.14°. No 5.04 anywhere on the sheet. H03's tag on the upper hole (10.5, +6), H04's on the lower (17.8, −6). Created by and the author read "Autonomous"; no maker named (D-147 (1)).

## The spigot sheet, tabulated (2026-11-01)

The Lead's ruling on J-FRONT-03: DT's two spigots on DR's ledge stand 11 proud, so they still engage DT's holes 5. 831010 is 831001 with the pin 3 longer, a tabulated variant. The sheet's views don't change: they show 831001, as the native drawing has them since Reviewer 5's pass. So only the finish step changed, from the same raw export: the title (HARDWARE - LOCATING SPIGOT - TABULATED: 831001, 831010), TABULATED in the notes, the scale in note 1, the pin length L in note 3 with a table (PART, L, PROUD, OVERALL, POD, WHERE: 831001 7.24, 8.00, 15.24, 28; 831010 10.24, 11.00, 18.24, 2, DR's ledge under DT), note 5's proud from the table, and note 6 naming H-05 and H-45 with one STEP per number. Read back: the views' dimensions are the same as main's sheet, word for word; Created by and the PDF's author read Autonomous. A Reviewer's D-114 pass follows. Known from the first sheet: the pin's 8 sits on its dimension line.

## Reviewer 10's D-114 pass on the spigot sheet (#346), and the fixes (2026-11-01)

Reviewer 10 held #346 on one P2: the front view printed 831001's 7.24 and 15.24, the two sizes the table varies, so for 831010 the view and the table disagreed. The Lead asked for the finish step to fix it rather than a new Fusion run (the queue was long).

- **Lettered, in the finish step (no Fusion run):** `letter_dims()` takes each value Fusion printed on the views (it must be there exactly once, left of the notes), removes its text from the page (a redaction; the dimension's lines and arrows stay) and writes the letter on the same baseline, centred where the value was, at the same size and direction: **7.24 → L** and **15.24 → L + 8**. It runs before the notes, whose table repeats the values, and re-reads the page: each letter there once in its direction, neither value left. Note 3 says L is the pin above its shoulder and L + 8 the overall length, both per part in the table.
- **The drawing test covers the spigot sheet:** TABULATED and both numbers in the notes; "L + 8" on one note line; each table row's OVERALL = L + 8 and PROUD = L + 0.76; the letters are exactly the drawn part's L and OVERALL; no floor panel in WHERE (D-132); each POD equals the parts list's count; and `letter_dims()` on a page with Fusion-like values (it keeps the other values and the dimension line, and stops on a value that isn't there).
- **WHERE, note 5 and the count (P3):** F2 is gone (D-132), so its two spigots and their 838009 inserts go: 831001 is **24** a pod (8 band, 8 seams, 4 ceiling, 2 DL, 2 DR; Reviewer 10's re-check: the count had carried 2 too many since DL's, DR's and DT's were added), and 838009 is cancelled. Note 5 now says the pin stands the table's proud above the face its rivnut is set in (not always a tube face: DR's are on BASE's closing angle). The air column's foot has no locator yet: BASE's bracket on the band isn't posted, so J-AIR-02 holds it (HOLD-26), with Joints' proposal in the register.
- **For the next annotate run (Reviewer 10, carried from main):** a centre line on the front view and a centre mark on the top view, and the pin's 8 off the shoulder line; and 831001's STEP header names the stop washer (the product is right), fixed at the next spigot export.

**Read back from the PDF:** front view L, L + 8, 8, 8 (the pin's Ø8 h9 is in note 3); 5.88; top view 4. Created by and the author read "Autonomous"; no maker named (D-147 (1)).

