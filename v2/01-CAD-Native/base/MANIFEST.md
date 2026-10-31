# Manifest: BASE native CAD, sample P01

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-BASE-MAN | P01 | DRAFT | 2026-11-01 | BASE Engineer |

Where each part BASE designs lives in the native files and what drives it (guideline §4.5). One native design holds the whole sample: `110000_P01_BASE_CAD.f3d` here, and the same design in the cloud at Default Project / FocusPod v2 / `110000_P01_BASE_CAD`. The build script `base_build.py` makes it from nothing; it reads skeleton P04's parameter list (`v2/01-CAD-Native/skeleton/pod_skeleton.py`, `PARAMS`, v4 since #94) at run time and adds those parameters under the same names, then BASE's own (`BASE_PARAMS`, each with its status and source). A BASE name the skeleton also defines is skipped, so the skeleton's value wins. The .f3d has no external links: it opens on its own.

Every part is its own component, built in place in pod coordinates (`conventions.md` §4). Every sketch is fully constrained by dimensions driven by parameter expressions; the build fails if one isn't (`check_sketch`).

The same run also saves each part we make as its own design (`<PN>_P01_<NAME>_CAD`, with its .f3d here and its STEP in `v2/03-Manufacturing/base/`), and each subassembly as its own design (Save Copy As of its component), for the drawings.

| Part / Rev | Component | Body | Sketches and features (timeline names) | Key parameters | STEP / DXF / drawing | Edit test |
|---|---|---|---|---|---|---|
| 111101 / P01 | `111101 BASE - BAND TUBE - SIDE - LH` (in 110101) | `... - TUBE` | `PLAN - SIDE LH - OUTLINE` → `EXTRUDE - SIDE LH - TUBE OUTSIDE`; `PLAN - SIDE LH - BORE` → `CUT - SIDE LH - BORE, WALL band_wall`; `KEYHOLE - BL - ENTRY, SLOT, SEAT` → `CUT - KEYHOLE - BL` → `PATTERN - KEYHOLES - BL`; `HOLE`/`PATTERN - J-BASE-01 RIVNUT - L1`, `- SPIGOT RIVNUT - L1`, `- GLIDE KEY ACCESS - SIDE LH`, `- GLIDE NUT - SIDE LH` | `band_t`, `band_h`, `band_wall`, `glide_h`, `dl_x2`, `dl_y1`, `dl_y2`, `cap_t`, `jb_x`, `jb_e`, `jb_n`, `sp_e`, `side_l`, `base_side_y0`, `rn_hole`, `gl_*`, `kh_*`, `st_z1`, `st_z2` | own design and STEP; cut list row; drawing | see EDIT-TEST-RECORD.md |
| 111103 / P01 | `111103 BASE - BAND TUBE - BACK` (in 110103) | `... - TUBE` | `PLAN - BACK - OUTLINE` → `EXTRUDE - BACK - TUBE OUTSIDE`; `PLAN - BACK - BORE` → `CUT - BACK - BORE, WALL band_wall`; `HOLE`/`PATTERN - J-BASE-01 RIVNUT - B1`, `- B2`, `- SPIGOT RIVNUT - B1`, `- B2`, `- GLIDE KEY ACCESS - BACK`, `- CORNER KEY FIXING - BL`, `- BR`, `- GLIDE NUT - BACK` | as 111101, plus `base_back_x0`, `half_fw`, `outer_t`, `gl_e_bb`, `gl_n_back`, `ck_e`, `ck_y`, `ck_fix_hole` | own design and STEP; cut list row; drawing | see record |
| 111211 / P01 | `111211 BASE - CORNER KEY - BACK - COMMON` (2 copies in 110103) | `CORNER KEY - BACK` | `PLAN - CORNER KEY - BACK` → `EXTRUDE - CORNER KEY - BLOCK ck_z`; `HOLE`/`PATTERN - KEY FIXING - M6 TAP DRILL FROM BELOW`, `- HOOK STUD - M6 TAP DRILL THROUGH THE END FACE` | `ck_x`, `ck_y`, `ck_z`, `ck_e`, `ck_tap`, `ck_thr_b`, `ck_tap_d`, `st_z1`, `st_z2` (joints register J-BASE-02, sizes of 2026-11-01) | placed by reference: the Joints Engineer owns its model, STEP and tabulated drawing (111211 to 111214, PM ruling 2026-11-01) | dims by expression |
| 111601 / P01 | `111601 BASE - GLIDE DOUBLER - COMMON` (copies in 110101, 110103) | `GLIDE DOUBLER` | `PLAN - GLIDE DOUBLER` (outline + hole) → `EXTRUDE - GLIDE DOUBLER - PLATE gd_t` | `gd_w`, `gd_l` (52), `gd_t`, `gl_nut_hole`, `gl_dx` (0: hole centred) | own design and STEP; `v2/03-Manufacturing/base/111601_P01_BASE-GLIDE-DOUBLER-COMMON_DXF.dxf`; no drawing (D-89 part 4: DXF and parts-list row) | dims by expression |
| 111401 / P01 | `111401 BASE - FLOOR PANEL - F1` (in 110401) | `... - PANEL` | `PLAN - FLOOR PANEL F1 (WITH THE SEAM LAP)` → `EXTRUDE - FLOOR PANEL F1 - PLYWOOD fl_t`; `PLAN - F1 SEAM LAP ZONE` → `CUT - F1 SEAM HALF-LAP - UPPER HALF` | `fl_t` (= `floor_t`), `mat_t` (skeleton), `fl_gap`, `fl_seam`, `lap_w`, `band_t`, `wall_depth` | own design and STEP; `v2/03-Manufacturing/base/111401_P01_BASE-FLOOR-PANEL-F1_DXF.dxf`; drawing | see record |
| 111501 / P01 | `111501 BASE - FLOOR MAT - F1 - CLOSED-CELL 3 MM FOAM` (in 110401) | `... - SHEET` | `PLAN - SEAL MAT F1` → `EXTRUDE - SEAL MAT F1` | `mat_t` (skeleton v4), F1's outline with the lap | STEP (assembly); `111501_P01_..._DXF.dxf` and its cut-list row; no drawing (D-89 part 3) | see record |
| 831001 / P01 | `831001 HARDWARE - LOCATING SPIGOT - M6 X Ø8 - STAINLESS` (copies) | `LOCATING SPIGOT D8` | `HALF SECTION - LOCATING SPIGOT D8` → `REVOLVE - ...` | `sp_dia`, `sp_proud`, `sp_ch`, `sp_stud`, `rn_head_t` | joints register H-05 (its drawing is the Joints Engineer's) | dims by expression |
| 831002 / P01 | `831002 HARDWARE - STOP WASHER - Ø10.5 X Ø20 X 1.5 - AL` (copies) | `STOP WASHER ...` | `HALF SECTION - STOP WASHER ...` → `REVOLVE - ...` | `sw_hole`, `sw_d`, `sw_t` | joints register H-08 | dims by expression |
| 838003, 838001, 838010, 118002 | rivnut, hook stud bolt, the keys' button head screw and glide (bought) | envelopes | one revolve each, from the maker's or the standard's sizes (rivnut, bolt, screw) or HOLD sizes (glide) | `rn_*`, `gl_*` | bought: no drawing | — |
| 110101, 110103, 110401 | the band assemblies and F1's bonded assembly | — | hardware copies placed by the script at the hole positions (`hardware_points`), from the same expressions as the holes; each saved as its own design `<PN>_P01_<NAME>_CAD` for its assembly drawing | — | assembly drawings (D-89: every assembly keeps one) | copies are re-placed by a rebuild, not by a parameter edit |

Outputs made from the same build: `v2/03-Manufacturing/base/110000_P01_BASE_STEP.step` (cm, declared in the file, D-13), the parts' own STEP files, `110000_P01_BASE_DATA.json` (the CAD's facts) and, from it, `make_outputs.py` → `110000_P01_BASE_BOM.csv`, `110000_P01_BASE-TUBE-CUT-LIST_SPEC.csv` and the DXFs of F1, its mat and the doubler.

Rebuild (one Fusion run: assembly, part designs, subassembly designs, edit test; the loader reads the scripts only when the shared lock is granted):

```
python3 tools/fusion/run_script.py v2/01-CAD-Native/base/late_base.py --timeout 2700 \
  --arg targets=v2/01-CAD-Native/base/base_build.py,v2/01-CAD-Native/base/base_edit_test.py \
  --arg save=1 --arg replace=1 --arg export=1 \
  --arg also_parts=band_l_tube,band_b_tube,doubler,floor_f1,key --arg sub_assys=band_l,band_b,floor_assy
python3 v2/03-Manufacturing/base/make_outputs.py --dxf      # needs ezdxf for the DXFs
```
