# CEILING drawing register

Drawings of the ceiling's parts and assemblies, where they are made, and their state. Under D-139 every part drawing
comes from the drawing generator (`tools/drawgen`, from the part's STEP); bent sheet too since its bent sheet mode
(#335, the Lead's ruling 2026-11-01), and the assembly sheets from its assembly mode. Fusion makes only what the
generator can't draw yet, said first with why. Every drawing needs the reviewer's D-114 visual pass before it counts.
Fusion cloud files live in Default Project / FocusPod v2.

| Drawing | Part | Made in | State (2026-11-01, 13:00 UTC) |
|---|---|---|---|
| `513102_P01_LINING-RIB-CEILING_DWG` | 513102 rib | the generator's bent sheet mode | Fusion's sheet is out of this PR (D-147: Reviewer 5's Hold stood). The generator draws it in #348, which carries the rib's DXF fix (the blank was 1 mm short) and its real folds; it reads back PASS on a scratch run. It waits for the generator's count check to take a part placed in two cassettes. |
| `513101_P01_LINING-TRAY-CEILING_DWG` | 513101 tray | the generator's bent sheet mode | Waits for the generator to take a second fold on a flange: each return turns in again as the 12 mm lip (8 folds), in the Drawing Generator Engineer's queue. |
| `510301_P01_LINING-CASSETTE-CEILING-COMMON_DWG` | 510301 cassette | the generator's assembly mode | A sub-assembly sheet needs its parts table with balloons, fixings and order (guideline 5.2), which Fusion's API can't draw (the Lead's ruling on Reviewer 5's D-114 pass); the cassette's entry facts went to the Air Engineer. |
| `410101` | the C1 panel assembly | the generator's assembly mode | In #348, on its build v10 STEP: read-back PASS. |
| `411101`, `411102` | the two frames, welded (D-131), with their cut lists | the generator's weldment sheet | Each member's drawing is its row in its frame's cut list, and the holes made after welding go on the frame's sheet (D-162); no member has a sheet of its own, since none has a before-weld feature. These wait for the generator's weldment hooks. |

## Superseded cloud files

Kept, renamed `NAME_SUPERSEDED-<date>` by `ceiling_cleanup.py supersede=` (the PM's rule, 2026-11-01 06:55 UTC: no
cloud file is ever deleted). Read back from the folder at 11:49 UTC (a read-only listing).

| Renamed (UTC) | Now named | What it was |
|---|---|---|
| 10:22 | `513102_P01_LINING-RIB-CEILING_DWG_SUPERSEDED-2026-11-01` | the rib's Fusion sheet of 06:54 |
| 10:24 | `513101_P01_LINING-TRAY-CEILING_DWG_SUPERSEDED-2026-11-01` | the tray's Fusion sheet of 07:40 (its hole table printed empty) |
| 11:21 | `513102_P01_LINING-RIB-CEILING_DWG_SUPERSEDED-2026-11-01-2` | the rib's Fusion sheet of 10:24 (its thickness printed ".5") |

Not renamed: `513101_P01_LINING-TRAY-CEILING_DWG` (version 2, 11:23 UTC), the tray's last Fusion sheet, made before
the Lead moved the tray to the generator. Its PDF was never committed; the cloud file stays as it is.

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
