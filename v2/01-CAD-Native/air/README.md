# AIR P01 (610000): native Fusion design

The air column, the soffit, the two splitter cartridges, the fan boxes, the intake riser, the supply box's two transitions, its rest in DR (the lip angle 611408 on two rubber pads 618402 on DR's shelf tube F08, the riser buffer 618501 against DR's cross tube F07), and the roof sleeve with its top flange and the grille on it (D-60 to D-62, D-87, D-130, PM rulings of 2026-11-01), built by script from the skeleton's parameter list, the ceiling's parameters (the roof slot is CEILING's) and AIR's own (`air_model.py`, each with its status and source).

| File | What |
|---|---|
| `air_model.py` | parameters, the layout (every body as a box of expressions; the shapes that aren't boxes as outlines: the lip's L, the upper transition's facet-cut plan, the lower transition's trapezoid, the sleeve's flange), cut features (keyholes, spigot hole and slot, rail forks, lock holes, the rivnut holes, the door plate's pockets and B08 reliefs, the fill's B08 pockets), the BOM tree's part numbers; DR's frame values where the supply box meets it, from FRONT's DR STEP; DR's panel face read from FRONT's DR model at load (no copy); FRONT's panel screws that stand into AIR's space (D-142) |
| `air_build.py` | the Fusion build: components per part, checks (timeline, sketches, clashes, every body on its layout box, masses), save and export; `parts=...` builds several part-only designs for the drawings in one run |
| `air_exports.py` | parts list (D-87 shipping pieces), DXF cut files of the flat parts, flat cut list, from a build log |
| `test_air_offline.py` | 52 checks without Fusion (they pass on DR's face at Y −643.5 and −641.14, and on D-132's floor top Z 0), among them FRONT's panel screws kept clear or relieved, the door plate's pockets, the cartridge 4 over B01's washers, the position check fed the layout,  the supply box's rest on F08 and F07, the transition's clearance to DR's facet tube, the trapezoid's to DR's diagonal tube, and the sleeve flange's rivnut edge rule and bulges; D-61 sizes, no overlaps, clearances, the soffit against the ceiling, the sleeve clear of C2's members, fans in their boxes, D-87 rulings (5 mm off the linings, foot on the floor top, studs and locks on the ceiling's rivnuts, forks, hub zone, keyholes), part numbers |

Run (through the shared lock, one design per run):

    python3 tools/fusion/run_script.py v2/01-CAD-Native/air/air_build.py --doc 610000_P01_AIR_CAD \
        --arg into_active=1 --arg save=1 --arg export=1 --close --discard --label "CEILING Engineer (AIR)"
    python3 v2/01-CAD-Native/air/air_exports.py BUILD_LOG
    python3 tools/fusion/run_script.py v2/01-CAD-Native/air/air_build.py --arg parts=column,soffit,cart --arg save=1

New designs need `--doc-new` (or `create=1` for `parts=`) only once the PM allows it again.
