# Build record: 610000 AIR P01 (air column, soffit, cartridges, fan boxes, riser, roof sleeve)

Run 2026-10-31 20:33 UTC on Mac 1 (Fusion 2706.1.17), through the Fusion lock:
`python3 tools/fusion/run_script.py v2/01-CAD-Native/air/air_build.py --arg own_doc=1 --arg create=1 --arg new_name=1 --arg save=1 --arg export=1`.
**DRAFT P01.** Cloud copy: Default Project / FocusPod v2 / `610000_P01_AIR_CAD` (made by the first run, a name never used before; PM ruling 2026-11-01). Parameters: skeleton P04 v4 (PR #94), the ceiling's (the roof slot is CEILING's) and AIR's own (`air_model.py`).

## Result

- timeline 324 items, unhealthy 0, loose sketches 0, user parameters 222, bodies 63
- clash pairs over 1 mm³: 0 (the first run found 6 of 0.5 mm, square stud envelopes in the rails' round fork ends; the shanks are round now)
- position check: all 53 layout bodies on their boxes, worst 0.000 mm
- saved: True; exports: `610000_P01_AIR_CAD.f3d`, `v2/03-Manufacturing/air/610000_P01_AIR_STEP.step` (cm, declared, D-13)
- no personal names in the STEP, the DXF and CSV files or any of the 91 entries of the `.f3d`
- master BOM check (`v2/04-BOM/build_master_bom.py --ref HEAD`): no part without a number or a mass, no duplicate number, no unregistered hardware

## Shipping pieces (D-87: 20 kg or less; masses from Fusion, HOLD items at their parts-list figures)

| Piece | Mass |
|---|---:|
| 610201 soffit with the exhaust fan box and its 2 fans fitted | 14.70 kg |
| 610101 column (without its cartridge) | 8.35 kg |
| 610301 cartridge (each of 2) | 10.90 kg |
| 610401 supply fan box with the riser and transitions (its 2 fans are in FRONT's list) | 8.79 kg |

The soffit is 0.8 kg over the assembly guide's 13.9 kg: the 2 mm door-side plate that carries the door-side rail on the D-90 stud heads weighs 2.59 kg. A 1 mm plate would bring it to about 13.4 kg.

## Exports (`air_exports.py` on this run's log)

- `610000_P01_AIR-PARTS-LIST_BOM.csv` (39 rows) and `610000_P01_AIR-FLAT-CUT-LIST_BOM.csv` (fills and layers)
- DXF cut files of the flat parts (D-89 part 4): foot plate (spigot hole and slot), plenum plates, top rails (forks, lock holes), end plate, door-side plate, the ACP faces with their openings, the grilles (pattern HOLD)

## Not in this build yet

- STEP re-read in Fusion (`step_reimport_check_air.py`; `step_check.py`'s box puts the four placed fans at the origin) and the edit test (`edit_test_air.py`): queued.
- Drawings (D-89 parts 1 to 4, 18 sheets): specs ready in `../../02-Drawings/air/`, waiting for drawing starts.
- HOLD: hanger studs (D-90 sizes; number from the joints register), hinges, latches, the lock screws' captive retainer, the transitions, the hub zone, grille patterns.
