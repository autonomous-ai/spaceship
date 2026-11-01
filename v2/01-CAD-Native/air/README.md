# AIR P01 (610000): native Fusion design

The air column, the soffit, the two splitter cartridges, the fan boxes, the intake riser and the roof sleeve (D-60 to D-62, D-87, PM rulings of 2026-11-01), built by script from the skeleton's parameter list, the ceiling's parameters (the roof slot is CEILING's) and AIR's own (`air_model.py`, each with its status and source).

| File | What |
|---|---|
| `air_model.py` | parameters, the layout (every body as a box of expressions), cut features (keyholes, spigot hole and slot, rail forks, lock holes), the BOM tree's part numbers |
| `air_build.py` | the Fusion build: components per part, checks (timeline, sketches, clashes, every body on its layout box, masses), save and export; `parts=...` builds several part-only designs for the drawings in one run |
| `air_exports.py` | parts list (D-87 shipping pieces), DXF cut files of the flat parts, flat cut list, from a build log |
| `test_air_offline.py` | 14 checks without Fusion: D-61 sizes, no overlaps, clearances, the soffit against the ceiling, the sleeve clear of C2's members, fans in their boxes, D-87 rulings (5 mm off the linings, foot on the mat, studs and locks on the ceiling's rivnuts, forks, hub zone, keyholes), part numbers |

Run (through the shared lock, one design per run):

    python3 tools/fusion/run_script.py v2/01-CAD-Native/air/air_build.py --doc 610000_P01_AIR_CAD \
        --arg into_active=1 --arg save=1 --arg export=1 --close --discard --label "CEILING Engineer (AIR)"
    python3 v2/01-CAD-Native/air/air_exports.py BUILD_LOG
    python3 tools/fusion/run_script.py v2/01-CAD-Native/air/air_build.py --arg parts=column,soffit,cart --arg save=1

New designs need `--doc-new` (or `create=1` for `parts=`) only once the PM allows it again.
