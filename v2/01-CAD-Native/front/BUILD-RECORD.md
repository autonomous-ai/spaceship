# Build record: FRONT

## 360001 FRONT - DOOR UNIT, P01 (DRAFT)

Run 2026-10-31 on Mac 1, Fusion 2706.1.17, through the shared lock (`tools/fusion/run_script.py`, PR #22), on main at 753fa2a plus this branch:

```sh
python3 tools/fusion/run_script.py v2/01-CAD-Native/front/door_unit.py --doc 360001_P01_FRONT-DOOR-UNIT_CAD --doc-new --save "P01 build"
python3 tools/fusion/run_script.py v2/01-CAD-Native/front/door_unit.py --doc 360001_P01_FRONT-DOOR-UNIT_CAD --arg step=export
python3 tools/fusion/step_check.py v2/03-Manufacturing/front/360001_P01_FRONT-DOOR-UNIT_STEP.step --expect=-1132,-773.38,27,214,-624.62,2116
```

Cloud copy: Default Project / FocusPod v2 / `360001_P01_FRONT-DOOR-UNIT_CAD`, version 3 (the exports come from it).

### Result

- skeleton parameters: `100000_P03_POD-SKELETON-PARAMETERS.csv` (P03), 60 loaded
- bodies 10, timeline 29 items, unhealthy 0, loose sketches 0, parameters 96
- clash pairs 4, expected 4, unexpected 0; every listed pair clashes
- unit box X -1132..214, Y -773.38..-624.62, Z 27..2116 (it includes the HOLD spaces)
- STEP: length unit cm, declared in the file (D-13); 10 products, 10 solids; `step_check.py` box MATCH (largest difference 0.0000 mm); re-read in Fusion, box equal to the model's (0.000 mm); no names in the header
- f3d 205,808 bytes; STEP 101,687 bytes
- edit test PASS (`EDIT-TEST-RECORD.md`)
- renders checked by eye: `360001_P01_FRONT-DOOR-UNIT-FRONT_IMG.png` (front, from outside), `...-ISO_IMG.png`

| Body | Size X × Y × Z (mm) | Box (mm) |
|---|---|---|
| DOOR LEAF GLASS 4+4 | 1175 × 8.76 × 2036 | -961, -703.38, 80 → 214, -694.62, 2116 |
| KICK STRIP | 1175 × 20 × 78 | -961, -709, 27 → 214, -689, 105 |
| GLAZING U-SEAL | 1175 × 12 × 27 | -961, -705, 78 → 214, -693, 105 |
| DROP SEAL ENVELOPE | 1175 × 11.6 × 40 | -961, -704.6, 27 → 214, -693, 67 |
| HOLD HINGE SPACE H1, H2, H3 | 271 × 40 × 120 each | X -1132 → -861; Z centres 355, 1110.5, 1866 |
| HOLD LOCK SPACE | 65 × 40 × 159 | 3.23, -719, 985.5 → 68.23, -679, 1144.5 |
| HOLD PULL SPACE, outside and pod side | 40 × 70 × 360 each | X -65.86 → -25.86, Z 885 → 1245 |

Listed overlaps (the HOLD spaces wrap the glass where the named hardware will clamp it): H1, H2, H3 with the leaf, 105,120 mm³ each; the lock with the leaf, 90,535 mm³.

### Mass (calculation)

| Item | kg | Status |
|---|---|---|
| 361001 leaf, 2.1087 m² × 8.76 mm × 2376 kg/m³ | 43.89 | calculation (CAD); laminate density from 8 mm glass at 2500 and 0.76 mm PVB at 1070 kg/m³ |
| 361002 kick strip, 660 mm² × 1175 mm × 2700 kg/m³ | 2.09 | calculation (CAD) |
| 368002 U-seal | 0.15 | calculation (CAD, 1200 kg/m³ assumption) |
| 368001 drop seal | 0.60 | assumption (D-56) |
| 368101 hinges, 3 × 0.6 | 1.80 | assumption (D-56) |
| 368102 lock | 0.84 | source (HOLD candidate, selection C7) |
| 368103 pull pair | 0.80 | assumption (D-56) |
| **Door unit** | **50.17** | calculation |

**This is 2.7 kg over D-56's 47.5 kg**, which REQ-BLD-05 uses as the rating for the hinges and lock: +0.61 kg for the 25 mm of glass inside the strip, +1.09 kg because the strip is machined from 20 × 80 flat bar (4 mm walls, 2.09 kg) where D-56 assumed 1.0 kg, +0.15 kg for the U-seal, and +0.84 kg for a lock, which D-56 doesn't count. DECIDED by the PM on 2026-10-31: the door unit is 50.2 kg, and the hinge and lock set must be rated for at least 60 kg (50.2 kg plus a margin); the HOLD rows in the parts list say so. An extruded strip with 2.5 mm walls would weigh about 1.35 kg (calculation), for a later production die.

### Interfaces to other assemblies

| With | What | Status |
|---|---|---|
| BASE (threshold) | The drop seal closes on the threshold top (`thresh_h`, Z 20) across `kick_len`; the strip runs 7 mm above it | decided gap; threshold detail is BASE's |
| BASE (base band at the hinge side) | The drop seal's release button sits at the strip's hinge end (X -961) and needs a strike on the jamb below DL (DL stops at Z 110) | HOLD: athmer's button drawing; strike position for BASE |
| BASE (base band under the fixed glass) | The strip's latch end is square at X 214, 4 mm from where the fixed glass starts (X 218); the band piece under the fixed glass should end about 4 mm clear of it, like the glass-to-glass gap | for BASE and the fixed glass unit |
| DL | The hinge spaces reach 160 mm into DL (to X -1132) at three heights, and the frame-stop seal and stop come with DL and DT | next FRONT PRs; HOLD H01 |
| Fixed glass unit | The 180° glass-to-glass seal sits on the fixed pane's edge | next FRONT PR |

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
