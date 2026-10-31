# Build record: 710000 ELECTRICAL P01 (route model)

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-CAD-ELE-01 | P01 | DRAFT | 2026-11-01 | ELECTRICAL Engineer |

Run 2026-10-31 at about 19:17 UTC on Mac 1, Fusion 2706.1.17, through the Fusion lock: the rebuild on skeleton P04 version 4 (#94, updated in place), with the air column's top now the skeleton's named value `dt_zb`. Before it changed anything, the build read the saved skeleton (version 4) and found skin_t and the 16 favourites it derives (PM heads-up of 18:53 on a lost favourite; no open copy with unsaved changes or at an older version).

```
python3 tools/fusion/run_script.py v2/01-CAD-Native/electrical/electrical_build.py --label "ELECTRICAL Engineer" \
    --doc 710000_P01_ELECTRICAL_CAD --arg rebuild=1 --arg save=1 --arg export=1 --close --discard
```

(queued through a loader that reads the script when the lock is granted, with the edit test as a second step in the same run). The cloud copy is Default Project / FocusPod v2 / `710000_P01_ELECTRICAL_CAD`, opened at version 3 and saved as the next version. It is linked to skeleton P04 by Derive and keeps that link. The repo's `.f3d` and STEP were exported from the same saved version, with the link broken in memory only (shared rule for repo exports), so the `.f3d` opens on its own.

## Result

| Check | Result |
|---|---|
| Bodies, components | 41 bodies in 7 components (710001, 710011, 710021, 710023, 710024, 710031, 710041) |
| Timeline | 90 items, 0 unhealthy |
| Sketches | 0 not fully constrained |
| User parameters | 84: 16 from the skeleton (`<name>` = `<name>_Ref`, `dt_zb` added) and 68 electrical, each with its status and source |
| Skeleton values | live derived values equal the repo's P04 CSV (version 4) for all 16 used (none differ) |
| Body boxes against the offline model | 0 mismatches over 0.01 mm |
| Overlap between its own bodies | none over 0.1 mm³ |
| Overlap with skeleton P04's 36 bodies | 38 pairs, all on the intended list, each with its reason (routes and pockets in the cassettes' cable gap, the unit and the inlet in B2, the run into DR); 0 unexpected; every listed pair occurs (the record of the 17:58 run said 39; its log shows the same 38) |
| Design box | X 94.99 … 1195.53, Y −665.03 … 850.02, Z 300.98 … 2347.08 mm |
| Saved | yes (new version of the cloud design) |
| `.f3d` export | `710000_P01_ELECTRICAL_CAD.f3d`, 39 entries (25 zstd, 14 stored), every entry read decompressed: no personal names |
| STEP export | `../../03-Manufacturing/electrical/710000_P01_ELECTRICAL_STEP.step`: AP214, length unit cm declared in the file (D-13), 8 products (710000 and the 7 components), 41 solids (`tools/fusion/step_check.py`; its box reads vertices only, so it misses the cylinders' round extents by up to 5.6 mm: the Fusion re-read below is the exact check); no personal names |
| STEP re-read in Fusion | 41 bodies, box equal to the design's, max difference 0.000 mm |

## Earlier runs (kept for the record)

- 2026-10-31 17:58–18:01: the rebuild on skeleton P04 before version 4 passed the same checks (15 skeleton parameters, the column top as its own 2120).

- 2026-10-31 16:40: the first build of the 40-body model passed the same checks. The corner grommets and the call-light route then changed, so the model was rebuilt.
- 2026-10-31 17:2x: a rebuild failed while listing the cloud folder (an entry changed while it was being read). `find_file` now takes a snapshot and skips unreadable entries (runner PR #86).
- 2026-10-31 17:4x: a rebuild failed re-adding parameters, because the old features still used them. The rebuild now freezes the parameter values, clears the timeline and components, and updates the parameters in place.

## Not in this run

- The edit test, the second step of the same run, stopped at its first line: it checked the imported copy's root part number, which an imported copy doesn't keep. It now checks the 7 components instead and runs again on its own (`EDIT-TEST-RECORD.md`). The failed step left the route design open; the next ELECTRICAL run closes it (its saved version is in the cloud).
- The enclosure body's Fusion drawing follows on its own branch after this PR merges (D-91). The route model has no separate Fusion drawing: sheet 3 of the wiring diagram is its drawing (PM ruling 2026-11-01).
- The three sheet-metal parts (711001, 711002, 711005) need new designs. That waits for the PM's all-clear on making new designs (paused after the 17:54 Fusion crash).
