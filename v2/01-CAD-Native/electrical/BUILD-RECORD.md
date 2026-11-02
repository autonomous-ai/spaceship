# Build record: 710000 ELECTRICAL P01 (route model)

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-CAD-ELE-01 | P01 | DRAFT | 2026-11-01 | ELECTRICAL Engineer |

Run 2026-10-31 at about 21:38 UTC on Mac 1, Fusion 2706.1.17, inside one held Fusion session (route rebuild with its edit test, then the front plate, then the body's drawing): the rebuild with tonight's last three changes from WALL's fit checks: the ceiling route's crossing out of B4-CASS moved below its 12 mm top lip (a felt-only Ø12 hole at X 583, Z 2330; the ceiling cassette's back-return bushing level with it), B2-CASS's cut-out plain with no returns (so the slot S-PU-X and the bushing G-PU-TOP are gone), and the front plate as a reserved space (320 x 284, 2 mm off the felt). Before it changed anything, the build read the saved skeleton (version 4) and found skin_t and the 17 favourites it derives.

```
python3 tools/fusion/run_script.py v2/01-CAD-Native/electrical/electrical_build.py --label "ELECTRICAL Engineer" \
    --doc 710000_P01_ELECTRICAL_CAD --arg rebuild=1 --arg save=1 --arg export=1 --close --discard
```

(queued through a loader that reads the script when the lock is granted, with the edit test as a second step in the same run: PASS, `EDIT-TEST-RECORD.md`). The cloud copy is Default Project / FocusPod v2 / `710000_P01_ELECTRICAL_CAD`, opened at version 5 and saved as the next version. It is linked to skeleton P04 by Derive and keeps that link. The repo's `.f3d` and STEP were exported from the same saved version, with the link broken in memory only (shared rule for repo exports), so the `.f3d` opens on its own.

## Result

| Check | Result |
|---|---|
| Bodies, components | 40 bodies in 7 components (710001, 710011, 710021, 710023, 710024, 710031, 710041) |
| Timeline | 90 items, 0 unhealthy |
| Sketches | 0 not fully constrained |
| User parameters | 91: 17 from the skeleton (`<name>` = `<name>_Ref`; `dt_zb` and `inner_w` added) and 74 electrical, each with its status and source |
| Skeleton values | live derived values equal the repo's P04 CSV (version 4) for all 17 used (none differ) |
| Body boxes against the offline model | 0 mismatches over 0.01 mm |
| Overlap between its own bodies | none over 0.1 mm³ |
| Overlap with skeleton P04's 36 bodies | 36 pairs, all on the intended list, each with its reason (routes and pockets in the cassettes' cable gap, the unit and the inlet in B2, the run into DR); 0 unexpected; every listed pair occurs |
| Design box | X 82.98 … 1195.53, Y −665.03 … 850.02, Z 300.98 … 2347.08 mm (the front plate reaches X 83) |
| Saved | yes (new version of the cloud design) |
| `.f3d` export | `710000_P01_ELECTRICAL_CAD.f3d`, 39 entries (25 zstd, 14 stored), every entry read decompressed: no personal names |
| STEP export | `../../03-Manufacturing/electrical/710000_P01_ELECTRICAL_STEP.step`: AP214, length unit cm declared in the file (D-13), 8 products (710000 and the 7 components), 40 solids (`tools/fusion/step_check.py`; its box reads vertices only, so it misses the cylinders' round extents by up to 5.6 mm: the Fusion re-read below is the exact check); no personal names |
| STEP re-read in Fusion | 40 bodies, box equal to the design's, max difference 0.000 mm |

## B2 interface: 711001 rebuilt and redrawn, 710000 rebuilt (2026-11-02)

On Mac 1 in the shared lock, from a checkout with main's runner files in its working tree only:

- 02:32 UTC: `electrical_parts_cad.py --arg parts=body --arg export=1` opened `711001_P01_ELECTRICAL-POWER-UNIT-ENCLOSURE-BODY_CAD` at version 6 and saved version 7: the B2 interface's holes. In the bottom H04 Ø15.9 at X 32 (the mains cord, Heyco SB 625-7; it was the conduit's Ø22.2), H10 Ø11.1 at X 112 (the LAN cable, SB 437-5), H11 and H12 Ø6.6 at X 65 and 281 (fixing), all 14 from the back (Y 824); in the top H13 and H14 Ø6.6 at X 15 and 281; the earth stud H09 moved to X 90; H15 Ø5.0 in the back at X 47, Y 45 (the cord clamp's PEM FHA-M5-12 stud). Box 296 x 260 x 72, volume 173,340 mm3, 0.465 kg; timeline 45, 0 unhealthy, 0 loose sketches, 30 parameters; f3d, STEP (cm, D-13) and DXF exported. The STEP holds the 15 holes exactly (the hole table's check reads every one in its own wall). An earlier 18:22 build (version 6) is the same geometry; version 7 only corrects one parameter's source text (the cord is SJEOOW, 9.22 mm).
- The drawing: renamed `..._DWG_SUPERSEDED-2026-11-01-5` and `..._DWG_SUPERSEDED-2026-11-02` (kept, D-141) and started fresh from design version 7. The first two opens of a freshly started drawing hung (2026-11-01 18:23 and 2026-11-02 02:34: Fusion's upload of the new file was put off, Fusion Engineer 2) and the runner flagged Fusion; after the Lead's safe restart, a hold with only the open and a 30 s wait first worked at 03:41. `make_body_drawing.py` placed the 6 views, matched every view's circles to the STEP's 15 holes (the back's H15 seen through the open front), and added the pitch, the overall sizes, datums and centre marks; `body_drawing_text.py` finished the PDF (0.12 MB): Autonomous in Created by, author and creator; the 15-row hole table; tags H01-H15; read back clean.
- 03:59 UTC: the route model through the late-binding loader with the edit test (PASS, `EDIT-TEST-RECORD.md`): `710000_P01_ELECTRICAL_CAD` opened at version 7 and saved as the next version (the skeleton link kept).

| Check | Result |
|---|---|
| Bodies, components | 57 bodies in 7 components (B2's SLEEVE gone; MN-UP, MN-JOG, MN-MBR, LN-BAND, LN-UP, LN-MBR new) |
| Timeline | 122 items, 0 unhealthy, 0 loose sketches |
| User parameters | 143 |
| Body boxes against the offline model | 0 mismatches over 0.01 mm |
| Overlap between its own bodies | none over 0.1 mm3 |
| Overlap with skeleton P04 | only the intended pairs, each listed with its reason; every listed pair occurs |
| Design box | X 74.98 ... 1195.53, Y -640.67 ... 850.02, Z 300.98 ... 2347.08 mm (the cord's channel reaches X 75) |
| `.f3d` exports | 710000 and 711001 read decompressed, as text and UTF-16: no personal name (one 3-letter match inside 710000's binary geometry stream, not text) |
| STEP re-read in Fusion | 57 bodies, box equal to the design's, max difference 0.000 mm |

## Route rebuild for the column route agreed with CEILING (2026-11-01)

Run 2026-11-01 at about 17:34 UTC on Mac 1, Fusion 2706.1.17, through the late-binding loader with the edit test as the second step (PASS, `EDIT-TEST-RECORD.md`), from a checkout with main's runner files (#386, #402) in its working tree:

```
python3 tools/fusion/run_script.py late_ele.py --doc 710000_P01_ELECTRICAL_CAD \
    --arg targets=v2/01-CAD-Native/electrical/electrical_build.py,v2/01-CAD-Native/electrical/edit_test_electrical.py \
    --arg rebuild=1 --arg save=1 --arg export=1 --close --discard
```

Opened Default Project / FocusPod v2 / `710000_P01_ELECTRICAL_CAD` at version 6 and saved it as the next version (the link to the skeleton kept). The column's route now follows AIR's points as CEILING built them on its combined AIR branch: the hub zone in AIR's zone, two bushed entries in the FR angle, the fill channel, the run along the high plenum plate to DR's opening, the exhaust lead up the FR angle through two cordgrips into the fan box, and the trunk's joint in pocket P8 behind the column; the chase, the run into DR and DR's bushed hole are gone.

| Check | Result |
|---|---|
| Bodies, components | 52 bodies in 7 components |
| Timeline | 112 items, 0 unhealthy |
| Sketches | 0 not fully constrained |
| User parameters | 128 |
| Skeleton values | live derived values equal the repo's P04 CSV for all used (none differ) |
| Body boxes against the offline model | 0 mismatches over 0.01 mm |
| Overlap between its own bodies | none over 0.1 mm3 |
| Overlap with skeleton P04's 31 bodies | only the intended pairs, each listed with its reason; none with DR now; every listed pair occurs |
| Design box | X 82.98 ... 1195.53, Y -640.67 ... 850.02, Z 300.98 ... 2347.08 mm |
| Saved | yes (new version of the cloud design) |
| `.f3d` export | 64 entries read decompressed (zstd) as bytes and as UTF-16: no personal name (the design's own text found as the control) |
| STEP export | `../../03-Manufacturing/electrical/710000_P01_ELECTRICAL_STEP.step`: AP214, cm declared (D-13), 52 solids (`tools/fusion/step_check.py`) |
| STEP re-read in Fusion | 52 bodies, box equal to the design's, max difference 0.000 mm |
| Against AIR's model (offline, CEILING's combined branch) | 0 overlaps over 0.1 mm3 with AIR's cut-outs and holes taken out; the points test passes against it |

## Front plate 711002 rebuilt for the vents and the heat check (2026-11-01)

Run 2026-11-01 at about 16:33 UTC on Mac 1, Fusion 2706.1.17, from a checkout with main's runner (#386: it waited 4.8 s after another team's save before reading the folder): only the front plate, with the devices on the left (the GFCI receptacle at 50 and the breaker window at 95 from the unit's left side, all bare mains parts left of 105), the two keystone openings in the middle (150), and the vent grille on the right only, 8 rows of 3 slots 44 x 4 (4 rows low, 4 high), so no slot lies within 15 mm of a bare mains part or above one (UL 62368-1: side openings in a PIS's 5 degree drop zone; foreign objects) and 4 mm keeps every probe out (the Lead's two conditions; the heat check in calc-results section 6).

```
python3 tools/fusion/run_script.py v2/01-CAD-Native/electrical/electrical_parts_cad.py --label "ELECTRICAL: front plate 711002 rebuild (vents and layout, about 3 min)" \
    --arg parts=front --arg export=1 --timeout 1500
```

Opened Default Project / FocusPod v2 / `711002_P01_ELECTRICAL-POWER-UNIT-FRONT-PLATE_CAD` at version 6 and saved it as the next version. Box 320 x 284 x 1.5 mm; volume 124,328 mm3, 0.333 kg at 2.68 g/cm3 (the parts list's mass); timeline 3 features, 0 unhealthy, 0 loose sketches; 36 parameters. Exports: the `.f3d`, the STEP (1 solid, box 320 x 284 x 1.5, `tools/fusion/step_check.py`) and the DXF (116 lines and 6 circles on layer CUT, mm). The `.f3d`'s 52 entries, read decompressed (zstd) as bytes and as UTF-16, hold no personal name (a planted name is found; the part's own name is found as the control).

## Front plate 711002 rebuilt for D-133 (US devices)

Run 2026-11-01 at about 06:11 UTC on Mac 1, Fusion 2706.1.17: only the front plate, for the US devices' openings (the GFCI receptacle's decorator opening 33.6 × 67 with its two Ø3.8 plate-screw holes 96.8 apart, two keystone openings 14.9 × 19.4, the breaker window 19 × 45, the devices' row at 180 above the unit's bottom and the top vents at 120). The body 711001 and the hub plate 711005 didn't change and weren't rebuilt.

```
python3 tools/fusion/run_script.py v2/01-CAD-Native/electrical/electrical_parts_cad.py --label "ELECTRICAL Engineer" \
    --arg parts=front --arg export=1
```

Opened Default Project / FocusPod v2 / `711002_P01_ELECTRICAL-POWER-UNIT-FRONT-PLATE_CAD` at version 4 and saved it as the next version. Box 320 × 284 × 1.5 mm; volume 128,264 mm³, 0.344 kg at 2.68 g/cm³ (the parts list's mass); timeline 3 features, 0 unhealthy, 0 loose sketches; 31 parameters. Exports from the same version: the `.f3d`, the STEP (Fusion's cm, declared, D-13) and the DXF in mm, 60 lines and 6 circles, all on layer CUT (D-89 part 4).

## Earlier runs (kept for the record)

- 2026-10-31 20:55: the rebuild with every skeleton-linked value, the 296 mm unit and the moved exits passed the same checks with 41 bodies (the slot S-PU-X and the bushing G-PU-TOP still in) and the crossing at Z 2337.5; its edit test passed.

- 2026-10-31 19:17: the rebuild on skeleton P04 version 4 passed the same checks with 16 skeleton values, the 300 mm unit and the ceiling values as CEILING's numbers; its edit test (the run's second step) stopped before any edit (it looked for a part number an imported copy doesn't keep), and the next edit test showed two edits the model couldn't follow (`EDIT-TEST-RECORD.md`).

- 2026-10-31 17:58–18:01: the rebuild on skeleton P04 before version 4 passed the same checks (15 skeleton parameters, the column top as its own 2120).

- 2026-10-31 16:40: the first build of the 40-body model passed the same checks. The corner grommets and the call-light route then changed, so the model was rebuilt.
- 2026-10-31 17:2x: a rebuild failed while listing the cloud folder (an entry changed while it was being read). `find_file` now takes a snapshot and skips unreadable entries (runner PR #86).
- 2026-10-31 17:4x: a rebuild failed re-adding parameters, because the old features still used them. The rebuild now freezes the parameter values, clears the timeline and components, and updates the parameters in place.

## Not in this run

- The Fusion drawing of the folded enclosure body 711001 is on its own branch (D-91, PR #173). Drawn 2026-11-01 at about 06:32 UTC in one held Fusion session: the first drawing (started 2026-10-31) was renamed `711001_P01_ELECTRICAL-POWER-UNIT-ENCLOSURE-BODY_DWG_SUPERSEDED-2026-11-01`, kept, not deleted (`retire_dwg.py`; PM ruling: no promote, no delete); `tools/fusion/start_drawing.py` started a fresh A2 drawing of the body's design version 3; `make_body_drawing.py` added 6 views (visible edges only), 3 dimensions and datums A, B, C, all as expected; `body_drawing_text.py` finished the PDF (text block, the account name cleared). Read back: no hidden lines, a 4-corner first-angle symbol, each size printed once, letters 2.5 mm or more (C05's check: clear). The route model has no separate Fusion drawing: sheet 3 of the wiring diagram is its drawing (PM ruling 2026-11-01).
- 711001's drawing redrawn 2026-11-01 for Reviewer 7's Hold on #173, in two held Fusion sessions on Mac 1:
  - 10:06 UTC, a probe. The body's design got version 4, which only adds a named view, "711001 VIEW FROM BELOW" (a camera; no geometry change, so the repo's f3d and STEP, version 3's, hold the same part). The current drawing was opened, tried and closed unsaved: the drawing API refused every orientation value past the standard ones ("invalid argument value" for 10 to 16), so a base view can't use the named view, and it can't turn or project one; centre marks set on the made view for round cuts printed (Fusion's "Smart Centers" layer), those set in the view's input didn't; a dimension between two hole centres worked; the API lists hidden holes' circles too, which the PDF doesn't print. The named view stays in version 4, unused.
  - 10:52 UTC, the redraw. `retire_dwg.py` renamed the drawing `711001_P01_ELECTRICAL-POWER-UNIT-ENCLOSURE-BODY_DWG_SUPERSEDED-2026-11-01-2`, kept, not deleted (D-141); `tools/fusion/start_drawing.py` started a fresh A2 drawing of design version 4; `make_body_drawing.py` placed the 6 views at their expected sizes (the bottom as view D: Fusion's Bottom, which is the view from below turned 180 degrees, placed apart at the top right), checked every view's circles against the STEP's 8 holes (hidden ones allowed), and added the H05-H08 pitch (236, 238) from the holes' centres, the three overall sizes, datums A, B, C and the centre marks; saved and closed. `body_drawing_text.py` finished the PDF (0.11 MB): Autonomous in Created by, author and creator; the hole table; tags H01-H08; the pitch printed as (236) and (238), for reference; "D (turned 180°)" and arrow D; read back clean.

- 2026-11-01, the holes the named parts set (follow-up to #173 and #337), on Mac 1 in the lock:
  - 12:06 UTC: `electrical_parts_cad.py --arg parts=front,body --arg export=1` rebuilt 711002 (version 6; the four M4 screw holes 22 from the plate's top and bottom, were 23) and 711001 (version 5: the clinch holes H05-H08 Ø5.94 at 10 from the top and bottom, H04 Ø22.2, the new earth stud hole H09 Ø5.0 at X 110 in the bottom, 36 from the back); 0 unhealthy features, 0 loose sketches; f3d, STEP (cm, D-13) and DXF exported. The new STEP holds the 9 holes exactly (read back).
  - 12:08 UTC: the drawing renamed `..._DWG_SUPERSEDED-2026-11-01-3` (kept, D-141) and started fresh from design version 5; every view's circles matched the STEP's 9 holes. Its finish showed the width's line running through the pitch's text (also on #173's sheet), so the width and the vertical pitch were set further out and the drawing redrawn: renamed `..._DWG_SUPERSEDED-2026-11-01-4` (kept) and started fresh again at 12:37 UTC from design version 5: every view's circles matched the STEP's 9 holes; the width now 18 above the front view and the vertical pitch 12 to its right; the PDF (0.11 MB) reads back clean, with no line through a dimension's value.