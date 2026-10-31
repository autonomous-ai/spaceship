# INTERIOR P01 (810000): native Fusion design

The light shelf along the side and back wall tops, the 1000 mm work wall ledge and the screen rail (D-70, D-85, ELECTRICAL's points via the PM), built by script from the skeleton's parameter list, the ceiling's parameters (the soffit depth sets where the side walls' free length starts) and INTERIOR's own (`interior_model.py`, each with its status and source).

| File | What |
|---|---|
| `interior_model.py` | parameters, the folded sections (sketches extruded along the walls), boxes for the HOLD envelopes, the cable holes, masses against the D-85 budgets |
| `interior_build.py` | the Fusion build with its checks, save and export; `parts=...` builds several part-only designs for the drawings in one run |
| `interior_exports.py` | parts list (size, tolerance, maker and SKU or HOLD) and the flat blanks of the folded parts as DXF |
| `test_interior_offline.py` | 9 checks without Fusion: shelf place and budget, cable points, ledge size, place, stand-off and brackets on WALL's stiles, ledge budget, no overlaps, clear of the column, part numbers |

Run:

    python3 tools/fusion/run_script.py v2/01-CAD-Native/interior/interior_build.py --doc 810000_P01_INTERIOR_CAD \
        --arg into_active=1 --arg save=1 --arg export=1 --close --discard --label "CEILING Engineer (INTERIOR)"
    python3 v2/01-CAD-Native/interior/interior_exports.py BUILD_LOG
