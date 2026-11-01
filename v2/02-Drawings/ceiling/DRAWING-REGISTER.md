# CEILING drawing register

Drawings of the ceiling's parts and assemblies, where they are made, and their state. Under D-139 a part drawing
comes from the drawing generator (`tools/drawgen`, from the part's STEP); Fusion makes only the assembly sheets and
the parts the generator can't draw yet (bent parts). Every drawing needs the reviewer's D-114 visual pass before it
counts. Fusion cloud files live in Default Project / FocusPod v2.

| Drawing | Part | Made in | Why there | State (2026-11-01) |
|---|---|---|---|---|
| `513102_P01_LINING-RIB-CEILING_DWG` | 513102 rib | Fusion | bent hat section (the generator refuses bends) | PDF read-back check PASS; waits for the D-114 visual pass |
| `513101_P01_LINING-TRAY-CEILING_DWG` | 513101 tray | Fusion | bent tray | the 07:40 UTC drawing printed Fusion's hole table empty (check FAIL); to be renamed `_SUPERSEDED-2026-11-01` and drawn again without the table, its two holes dimensioned, once the drawing start's timeout fix merges |
| `510301_P01_LINING-CASSETTE-CEILING-COMMON_DWG` | 510301 cassette | the drawing generator's assembly mode | a sub-assembly sheet needs its parts table with balloons, fixings and order (guideline 5.2), which Fusion's API can't draw | the 10:27 UTC Fusion sheet failed Reviewer 5's D-114 pass on those; the Lead's ruling: the generator draws it, with WALL's six cassette assemblies (the Air Engineer); its entry facts posted. The Fusion sheet stays in the cloud, unused |

## Superseded cloud files

Kept, renamed `NAME_SUPERSEDED-<date>` by `ceiling_cleanup.py supersede=` (the PM's rule, 2026-11-01 06:55 UTC: no
cloud file is ever deleted). None yet.

## Deleted before the rule

Before 06:55 UTC on 2026-11-01 the cleanup deleted failed sample drawings of the ceiling's own, so they could be
started again under their names (each was version 2 or less, never released, and its PDF never committed):

| UTC | Drawings |
|---|---|
| 03:00 | `513102_P01_LINING-RIB-CEILING_DWG` |
| 05:41 | `513102_P01_LINING-RIB-CEILING_DWG` |
| 06:13 to 06:17 | `513102_P01_LINING-RIB-CEILING_DWG`, `513101_P01_LINING-TRAY-CEILING_DWG`, `510301_P01_LINING-CASSETTE-CEILING-COMMON_DWG` |
| 06:51 to 06:54 | the same three; the tray's and the cassette's new starts then failed on the dialog timing (fixed in #295) |

Each redo followed a method fix found on the sample (the drawing commits on this branch say which).
