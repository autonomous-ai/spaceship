# Build record: 610000 AIR P01 (air column, soffit, cartridges, fan boxes, riser, roof sleeve)

Run 2026-11-01 02:00 UTC on Mac 1 (Fusion 2706.1.17), in one held Fusion session (build, STEP re-read, edit test):
`python3 tools/fusion/run_script.py v2/01-CAD-Native/air/air_build.py --arg own_doc=1 --arg save=1 --arg export=1`.
**DRAFT P01.** Cloud copy: Default Project / FocusPod v2 / `610000_P01_AIR_CAD` (the script opens it by name and rebuilds it as a new version). Parameters: skeleton P04 v4 (PR #94), the ceiling's (the roof slot and the hanger rivnuts are CEILING's), FRONT's named value for DR's access-panel face and AIR's own (`air_model.py`).

## Result

- timeline 312 items, unhealthy 0, loose sketches 0, user parameters 225, bodies 63
- clash pairs over 1 mm³: 0
- position check: all 53 layout bodies on their boxes, worst 0.000 mm
- saved; exports: `610000_P01_AIR_CAD.f3d`, `v2/03-Manufacturing/air/610000_P01_AIR_STEP.step` (cm, declared, D-13)
- STEP re-read in Fusion (`step_reimport_check_air.py`): 63 bodies, box within 0.03 mm of the layout (**MATCH**); no solid holds a sealed void any more
- edit test: **PASS**, 6 changes (pod_w; pod_d with wall_depth; dt_zb; DR's panel dr_acc_t; col_x0; hub_z), every body followed, 0 unhealthy (`EDIT-TEST-RECORD.md`)
- no personal names in the STEP, the DXF and CSV files or any entry of the `.f3d`
- master BOM check (`v2/04-BOM/build_master_bom.py --no-write`): no part without a number or a mass, no duplicate number, no unregistered hardware

## What changed in this build (PM rulings 2026-11-01)

- **DR's access-panel face.** The column and the whole soffit start at FRONT's named value `dr_acc_face_y` (`-pod_d / 2 + decor_d - dr_back_t + dr_acc_t`, Y −643.5), not at the side walls' front end (−645), so neither overlaps DR's 3 mm access panel. AIR carries the same names, expressions and inputs as FRONT's DR model; `test_air_offline.py` (`FrontInterface.test_same_as_front`) fails if they drift, whenever FRONT's file is in the checkout. The door-side rail narrows to 22.5 so it stays 1 mm clear of the roof sleeve; the forks are 1.5 shorter. The room faces stay at Y −285.
- **DR keeps its riveted back band** behind the soffit: the soffit's door-side plate is not sealed to DR (open 4.76 under the ceiling frame and below Z 2140), so the band stays DR's sound wall.
- **The edit test's one unhealthy item at pod_w 2600** was a latch's cut in the soffit fill: at a wider pod the left section's first latch moves past the fill's end and its cut found nothing. The fill under the cartridge now stops 8 short of the front face, under the latch line, so no latch cuts it wherever the sections' quarter points fall. The edit test now also changes FRONT's panel thickness (`dr_acc_t`) and names any item that isn't healthy.
- **The fan boxes are open where the air passes** (the exhaust box on its cartridge side and top, the supply box at the bottom and top): a sealed box blocks the air, and its STEP solid held a void the mechanical checks' reader couldn't read then.
- The scripts load this worktree's modules first (Fusion keeps modules loaded between runs).

## Shipping pieces (D-87: 20 kg or less; masses from Fusion, HOLD items at their parts-list figures)

| Piece | Mass |
|---|---:|
| 610201 soffit with the exhaust fan box and its 2 fans fitted | 13.84 kg |
| 610101 column (without its cartridge) | 8.32 kg |
| 610301 cartridge (each of 2) | 10.91 kg |
| 610401 supply fan box with its 2 fans, the riser and transitions (PM ruling 2026-11-01: AIR carries all four fans) | 8.90 kg |

## Exports (`air_exports.py` on this run's log)

- `610000_P01_AIR-PARTS-LIST_BOM.csv`: each row with size, tolerance, maker and SKU, so the row is the cut list of the flat parts (D-89)
- DXF cut files of the flat parts (D-89 part 4): foot plate (spigot hole and slot), plenum plates, top rails (forks, lock holes), end plate, door-side plate, the ACP faces with their openings, the grilles (pattern HOLD)

## Open issue (PM ruling D-121)

- **Exhaust short-circuit:** with the exhaust fans 50 mm off the box floor, the upper part of the cartridge's passages opens above them, so some air can short-circuit. The AIR follow-up moves the fans to the top on a sealed bulkhead, as D-121 adopts; open until it merges.

## Open findings from the mechanical checks on this branch (main's newer rules), for the AIR follow-up

- C08, C09: the soffit's two lock-screw holes in the door-side rail (611205) are Ø6.6 where the register rules 7.0 for an M6 into a rivnut, and 8.5 from the rail's door edge where 2 diameters are asked. The rivnuts are in the ceiling frame's C1 front member, which the D-117 / D-120 frame rework rebuilds; the rail can't grow toward DR's panel, so the follow-up places the holes and the rivnuts together (a local ear on the rail at each screw, or another fixing).
- C11: the aluminium parts name no alloy and temper yet ("alloy HOLD"); the ACP and felt faces and the cartridge layers give no finish.
- C06: under D-120 the corner angles (two shapes under one number), the column fill, the kick grille and the soffit fill (two pieces each), the cartridge (casing and layers in one component, so 611301 and 611302 aren't in the STEP by their own numbers), and the lock screws (head and shank bodies) become their own components; 618101 (hub zone) has no mass line.

## Not in this build yet

- Drawings (D-89, 18 sheets; D-91: they follow): specs ready in `../../02-Drawings/air/`.
- The AIR follow-up after this merges: D-116 (cartridge layers at 32 kg/m3), D-121 (cartridge casings stay 2.0; the fan box layout and its 32 kg/m3 linings; the exhaust fans to the top), D-124 (fan box casings 3 mm), the findings above, and the transitions 618102 (upper) and 618103 (riser) designed into FRONT's reserved spaces with FRONT's named values (HOLD envelopes until then).
- HOLD: hinges, latches, the lock screws' captive retainer, the hub zone, grille patterns.
