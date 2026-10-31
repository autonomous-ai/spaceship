# Build record: FRONT

## 360001 FRONT - DOOR UNIT, P01 (DRAFT)

Run 2026-10-31 18:5x UTC on Mac 1, Fusion 2706.1.17, through the shared lock, one run per design (PM fair-share rule): build, save, export, pictures and the edit test in one run, on skeleton P04 updated in place (v4, #94):

```sh
python3 tools/fusion/run_script.py v2/01-CAD-Native/front/door_unit.py --doc 360001_P01_FRONT-DOOR-UNIT_CAD \
    --arg step=all --arg "desc=P01 on skeleton v4 (#94): pull height on the floor mat" \
    --arg "edits=pod_w=2600 mm;fr_dz=12 mm;door_xbr=1474 mm" --close
python3 tools/fusion/step_check.py v2/03-Manufacturing/front/360001_P01_FRONT-DOOR-UNIT_STEP.step \
    --expect=-1132,-773.38,20,216.0196,-624.62,2115.5
```

Cloud copy: Default Project / FocusPod v2 / `360001_P01_FRONT-DOOR-UNIT_CAD`, the version this run saved (the exports come from it).

### Result

- skeleton parameters: `100000_P04_POD-SKELETON-PARAMETERS.csv` (P04 v4), 89 loaded
- bodies 11, timeline 36 items, unhealthy 0, loose sketches 0, parameters 152
- clash pairs 4, all listed (the HOLD hinge spaces and the strike wrap the glass where the hardware clamps it): H1, H2, H3 with the leaf, 105,120 mm³ each; the strike with the leaf, 11,949 mm³
- unit box X -1132 to 216.02, Y -773.38 to -624.62, Z 20 to 2115.5 (it includes the HOLD spaces)
- STEP: length unit cm, declared in the file (D-13); `step_check.py` box MATCH against the box computed from the parameters (largest difference 0.0000 mm); re-read in Fusion, box equal to the model's (0.000 mm)
- f3d 245,735 bytes; STEP 121,456 bytes; no names in the exports (f3d entries, STEP, CSV, DXF, pictures scanned)
- edit test PASS (`EDIT-TEST-RECORD.md`)
- pictures checked by eye: `360001_P01_FRONT-DOOR-UNIT-FRONT_IMG.png` (front, from outside), `...-ISO_IMG.png`: leaf, black kick strip, three hinge spaces on the hinge edge, the strike at the top latch corner, the pull spaces, the seal half along the latch edge
- parts list: after the run, its bought rows were re-written under the joints register's names with maker and SKU columns (the door script now does this itself); every other field is the run's, checked field by field

DXF: leaf (front view, X from the hinge edge, Y from the leaf's bottom) (0, 0), (1175, 0), (1175, 25), (893.28, 2034), (0, 2034); kick strip section 20 × 85 with the 12 × 27 pocket over the 12 × 55 cavity and its two 2 mm chambers (D-85).

| Body | Size X × Y × Z (mm) | Box (mm) |
|---|---|---|
| DOOR LEAF GLASS 4+4 | 1175 × 8.76 × 2034 | -961, -703.38, 80 → 214, -694.62, 2114 |
| KICK STRIP (hollow, D-85) | 1175 × 20 × 85 | -961, -709, 20 → 214, -689, 105 |
| GLAZING U-SEAL | 1175 × 12 × 27 | -961, -705, 78 → 214, -693, 105 |
| DROP SEAL ENVELOPE | 1175 × 11.6 × 40 | -961, -704.6, 20 → 214, -693, 60 |
| HOLD HINGE SPACE H1, H2, H3 | 271 × 40 × 120 each | X -1132 → -861; Z centres 355, 1109.5, 1864 |
| CATCH STRIKE HT-MSG62-U10 | 62 × 14.1 × 23.5 | -154.72, -706.05, 2092 → -92.72, -691.95, 2115.5 |
| 180 MAGNETIC SEAL - DOOR HALF | 283.74 × 11.76 × 2009 | -67.72, -704.88, 105 → 216.02, -693.12, 2114 |
| HOLD PULL SPACE, outside and pod side | 40 × 70 × 360 each | X -65.02 → -25.02, Z 879 → 1239 |

### Mass (calculation)

| Item | kg | Status |
|---|---|---|
| 361001 leaf, 8.76 mm × 2376 kg/m³ | 43.85 | calculation (CAD); laminate density from 8 mm glass at 2500 and 0.76 mm PVB at 1070 kg/m³ |
| 361002 kick strip, hollow (D-85) | 1.22 | calculation (CAD, 2700 kg/m³) |
| 368002 U-seal | 0.15 | calculation (CAD, 1200 kg/m³ assumption) |
| 368001 drop seal | 0.60 | assumption (D-56) |
| 368101 hinges, 3 × 0.6 | 1.80 | assumption (D-56) |
| 368102 strike | 0.02 | source (Sugatsune datasheet, 22.9 g) |
| 368006 magnetic seal, the door's half | 0.15 | assumption, HOLD product |
| 368103 pull pair | 0.80 | assumption (D-56) |
| **Door unit** | **48.59** | calculation |

The hinge set's rating stays at least 60 kg (PM ruling 2026-10-31: the unit plus a margin).

### Interfaces to other assemblies

| With | What | Status |
|---|---|---|
| BASE (threshold) | The drop seal closes on the threshold top (`thresh_h`, Z 13); the strip's bottom runs 7 above it (Z 20) | decided gap; threshold detail is BASE's |
| BASE (band at the hinge side) | The drop seal's release button sits at the strip's hinge end (X -961) and needs a strike on the jamb below DL | HOLD: athmer's button drawing; position for BASE |
| BASE (sill under the fixed glass) | The strip's latch end is square at X 214, about 4 mm from the fixed glass's bottom channel | BASE's sill ends clear of it |
| DL | The hinge spaces reach 160 mm into DL's pockets (to X -1132), at the three heights; the hinges' frame halves ship fitted in DL | HOLD H01 |
| DT | The strike faces DT's 35 N magnetic catch across the 6 mm gap; the top stop and seal are DT's | decided (PM ruling) |
| Fixed glass unit | The magnetic seal pair: 368006 on this leaf, 368003 on the pane | HOLD product |

## 360002 FRONT - FIXED GLASS UNIT, P01 (DRAFT)

Run 2026-10-31 18:3x UTC on Mac 1, Fusion 2706.1.17, through the shared lock, one run per design (PM fair-share rule): build, save, export, pictures and the edit test in one run, on skeleton P04 updated in place (v4, #94):

```sh
python3 tools/fusion/run_script.py v2/01-CAD-Native/front/fixed_glass.py --doc 360002_P01_FRONT-FIXED-GLASS-UNIT_CAD \
    --arg step=all --arg "desc=P01: bottom channel screw holes to BASE's sill (PM ruling 2026-11-01)" \
    --arg "edits=pod_w=2600 mm;fr_dz=12 mm;fix_xk=511 mm;door_xtr=1192 mm" --close
python3 tools/fusion/step_check.py v2/03-Manufacturing/front/360002_P01_FRONT-FIXED-GLASS-UNIT_STEP.step \
    --expect=-66.6252,-706.5,95,964.1285,-691.5,2135
```

Cloud copy: Default Project / FocusPod v2 / `360002_P01_FRONT-FIXED-GLASS-UNIT_CAD`, the version this run saved (the exports come from it).

### Result

- skeleton parameters: `100000_P04_POD-SKELETON-PARAMETERS.csv` (P04, v4); bodies 4, timeline 18 items, unhealthy 0, loose sketches 0, parameters 119
- clash pairs 0
- gap from the door's latch edge to the pane's free edge: 4.00 mm square to the edge at the band top, mid-height and the door top (4.04 mm horizontally)
- STEP: length unit cm, declared in the file (D-13); `step_check.py` box MATCH against the box computed from the parameters (largest difference 0.0000 mm); re-read in Fusion, box equal to the model's (0.000 mm)
- f3d 202,381 bytes; STEP 91,936 bytes; no names in the exports (f3d entries, STEP, CSV, DXF, pictures scanned)
- edit test PASS (`EDIT-TEST-RECORD.md`); pictures checked by eye: `360002_P01_FRONT-FIXED-GLASS-UNIT-FRONT_IMG.png` (front, from outside), `...-ISO_IMG.png`: the channel shows on the four held edges, none on the free edge

The U-profile's box is X -66.63 to 964.13, Y -706.5 to -691.5 (15 on the glass plane), Z 95 to 2135. Pane corners in its DXF (X from its leftmost point, Y from its bottom): (285.09, 0), (1026.24, 0), (826.05, 1427.46), (301.39, 2033), (0, 2033). U-profile cut lengths, base / mouth: bottom 744.7 / 729.5, right 1446.5 / 1424.8, diagonal 803.8 / 792.6, top 303.5 / 294.5; mitres 41.0°, 73.5°, 65.5°. Bottom piece: 4 holes 3.4, countersunk 90° to 7 inside, at X 269.4, 484.3, 699.2, 914.1 (50 from each end, 214.9 apart).

### Mass (calculation)

| Item | kg |
|---|---|
| 361003 pane, 8.76 mm at 2376 kg/m³ | 28.59 |
| 368004 U-profile, 4 pieces | 0.56 |
| 368002 U-seal | 0.24 |
| 368003 magnetic seal, the pane's half (assumption, HOLD product) | 0.15 |
| **Fixed glass unit** | **29.54** |

### Interfaces to other assemblies

| With | What |
|---|---|
| BASE | The bottom channel sits on BASE's sill seat (top Z 95), screwed down with 4 ISO 10642 M3 × 8 A2 into flush-head M3 rivnuts in the seat, at the factory; it ships on the sill (PM rulings 2026-11-01). The pane's 28.6 kg bears on it. |
| DR | The right and diagonal channels sit inside DR behind the 17 mm slot in its inner-edge skin; no DR frame tube crosses the channel's Y range. |
| DT | The top channel sits inside DT behind the 17 mm slot in its underside; DT's catch rail stands 3.5 behind it. |
| Door unit | The free edge runs 4 mm from the door's latch edge; the magnetic seal pair (368003 here, 368006 on the door) closes it. |

Fit order (PM ruling 2026-11-01): the bottom channel comes factory-fitted on BASE's sill; on site the pane drops into it, then DR slides in from the right onto the pane's right edges, then DT is lowered onto its top edge.

## 350003 FRONT - DECOR BLOCK ASSY - DR, P01 stage 2 (DRAFT)

Run 2026-10-31 20:2x UTC on Mac 1, Fusion 2706, through the shared lock, one run per design (build, save, export, pictures and the edit test), on skeleton P04 v4:

```sh
python3 tools/fusion/run_script.py v2/01-CAD-Native/front/dr_block.py --doc 350003_P01_FRONT-DECOR-BLOCK-ASSY-DR_CAD \
    --arg step=all --arg "desc=P01 stage 2: every frame tube shelled" \
    --arg "edits=decor_d=215 mm;fix_xk=511 mm;fix_zk=1531 mm" --close
python3 tools/fusion/step_check.py v2/03-Manufacturing/front/350003_P01_FRONT-DECOR-BLOCK-ASSY-DR_STEP.step
```

### Result

- bodies 38, timeline 146 items, unhealthy 0, loose sketches 0, parameters 181; clash pairs 0 (frame against skin, plates, panels, air parts and the glass channel)
- frame 351306: 26 tubes of 20 × 20 × 1.5 (80 × 20 at the bolt line, 40 and 60 × 20 at the bottom and the band), every tube shelled with its ends open (0 failed), 5.72 kg, 15.05 m of tube (cut list `351306_P01_FRONT-DECOR-FRAME-DR-TUBE-CUT-LIST.csv`)
- air intake past the frame: base opening 0.0422 m² gross, 0.0129 m² under the frame's bottom tubes, 0.0293 m² free (rule: 0.028 or more, PM ruling)
- flat parts (D-89 part 4, DXF 1:1 in mm, layer CUT): back plate 351302 798.0 × 2284.0 with 6 holes; access panel 351305 255.4 × 2042.0 with 12 holes (7.0 for M6, and the column's two hook studs at X 971, Z 1700 and 1850); inner panel 351303 715.0 × 2038.5
- felt 351304: same outline as the inner panel (stepped and slanted), so it keeps a drawing (D-89); its DXF is for the cutter
- STEP: length unit cm, declared in the file (D-13); box X 230 to 1250, Y -850 to -635, Z 110 to 2400 (`step_check.py`), equal to the model's when re-read in Fusion (0.000 mm)
- f3d 820,702 bytes; STEP 566,889 bytes; no names in the exports (f3d entries, STEP, CSV, DXF, picture metadata scanned)
- edit test PASS (`EDIT-TEST-RECORD.md`); pictures checked by eye: `350003_P01_FRONT-DECOR-BLOCK-ASSY-DR-FRONT_IMG.png`, `...-ISO_IMG.png`

### Mass (calculation)

| Item | kg |
|---|---|
| 351301 skin, ACP 3 mm at 1300 kg/m³ | 7.71 |
| 351306 frame, 26 tubes shelled, 2700 kg/m³ | 5.72 |
| 351302 back plate | 1.51 |
| 351305 access panel | 3.87 |
| 351303 inner panel | 1.67 |
| 351304 felt, 1.8 kg/m² | 0.77 |
| 350004 air supply assembly: riser 5.47, transitions 1.5 + 1.5 (assumption; reserved air spaces, detail by AIR), fan box 3.6 (D-60 table's 5.1 less the upper transition), fans 2 × 0.3 | 12.67 |
| **DR block** | **33.92** |

### Interfaces to other assemblies

| With | What |
|---|---|
| BASE | Stands on the band top (Z 110); the riser's open foot sits 140 mm over the base air opening. |
| Fixed glass | The right and diagonal channels sit behind the 17 mm slot in DR's inner-edge skin; no frame tube crosses the channel. |
| Air column | Hooks onto 2 studs on the access panel (X 971, Z 1700 and 1850, rivnut 838003), pushed back and dropped 10 mm onto BASE's floor spigots; the access panel is screwed to the frame to carry about 10 kg (PM ruling). |
| DT | Meets DT at X 449 under the top; joint HOLD (joints register). |

## 350002 FRONT - DECOR BLOCK ASSY - DT, P01 stage 2 (DRAFT)

Run 2026-10-31 20:2x UTC on Mac 1, Fusion 2706, through the shared lock, one run per design, on skeleton P04 v4:

```sh
python3 tools/fusion/run_script.py v2/01-CAD-Native/front/dt_block.py --doc 350002_P01_FRONT-DECOR-BLOCK-ASSY-DT_CAD \
    --arg step=all --arg "desc=P01 stage 2: welded tube frame 351204 (13 tubes); back plate corner on the slope" \
    --arg "edits=decor_d=215 mm;dt_xr=1690 mm;dl_w=283 mm" --close
python3 tools/fusion/step_check.py v2/03-Manufacturing/front/350002_P01_FRONT-DECOR-BLOCK-ASSY-DT_STEP.step
```

### Result

- bodies 18, timeline 62 items, unhealthy 0, loose sketches 0, parameters 148; clash pairs 0
- frame 351204: 13 tubes of 20 × 20 × 1.5, every tube shelled (0 failed), 2.51 kg, 8.52 m of tube (cut list `351204_P01_FRONT-DECOR-FRAME-DT-TUBE-CUT-LIST.csv`); its rail F02 carries the catch 368007 and the top stop 351203
- back plate 351202 (D-89 part 4): 1694.75 × 274.0, no holes; its corner sits on the slope so it clears the skin
- STEP: length unit cm, declared in the file (D-13); box X -1250 to 449, Y -850 to -645, Z 2094 to 2400 (`step_check.py`), equal to the model's when re-read in Fusion (0.000 mm)
- f3d 364,297 bytes; STEP 243,290 bytes; no names in the exports
- edit test PASS (`EDIT-TEST-RECORD.md`); pictures checked by eye: `350002_P01_FRONT-DECOR-BLOCK-ASSY-DT-FRONT_IMG.png`, `...-ISO_IMG.png`

### Mass (calculation)

| Item | kg |
|---|---|
| 351201 skin, ACP 3 mm at 1300 kg/m³ | 2.85 |
| 351204 frame, 13 tubes shelled | 2.51 |
| 351202 back plate | 1.66 |
| 351203 door top stop | 0.08 |
| 368005 frame-stop seal, top run 796 mm (assumption) | 0.05 |
| 368007 door catch (datasheet) | 0.05 |
| **DT block** | **7.20** |

### Interfaces to other assemblies

| With | What |
|---|---|
| Door unit | The top stop 351203 and the seal 368005 stop the leaf; the catch 368007 holds its strike 368102 (35 N). |
| Fixed glass | The top channel sits behind the 17 mm slot in DT's underside; the catch rail stands 3.5 behind it. |
| DR, DL, ceiling | Joints HOLD (joints register); DT goes on last, after the door hangs (fit order: glass, DR, DT). |
