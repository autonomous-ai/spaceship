# Edit test record: FRONT

Engineering guideline section 4.4. Each test opens the exported .f3d as a new unsaved copy, changes skeleton parameters, checks every anchor in the anchors file (a body side against the parameter expression it must follow), puts the values back, checks again and closes the copy without saving. The saved design is never touched.

## 360001 FRONT - DOOR UNIT, P01

Run 2026-10-31 on Mac 1, Fusion 2706.1.17:

```sh
python3 tools/fusion/run_script.py v2/01-CAD-Native/front/edit_test_front.py \
    --arg anchors=v2/01-CAD-Native/front/360001_P01_FRONT-DOOR-UNIT_ANCHORS.json \
    --arg "edits=pod_w=2600 mm;fr_dz=12 mm;door_xbr=1474 mm"
```

The three edits are skeleton parameters: the pod 100 mm wider, the front 5 mm higher (door bottom Z 110, so the strip grows to 83 mm), and the door 10 mm wider at the bottom.

Copy of `v2/01-CAD-Native/front/360001_P01_FRONT-DOOR-UNIT_CAD.f3d`, opened as a new unsaved document and closed without saving; 29 anchors.

| State | Box X x Y x Z (mm) | Unhealthy items | Loose sketches | Anchors off their expressions | Worst (mm) |
|---|---|---|---|---|---|
| Before | 1346.0 x 148.8 x 2089.0 | 0 | 0 | none | 0.020 |
| pod_w 2600 mm; fr_dz 12 mm; door_xbr 1474 mm | 1356.0 x 148.8 x 2094.0 | 0 | 0 | none | 0.020 |
| Reverted | 1346.0 x 148.8 x 2089.0 | 0 | 0 | none | 0.020 |

**RESULT: PASS (CAD check on a copy)**

The first run of this test failed, and that is why the sketches now measure from a reference point: the lock space's left side was dimensioned from the pod's centre line with abs(), and the edit moved it from X +3.2 to X -41.2, across the centre line, so the corner flipped to +41.2. Every FRONT sketch now dimensions its corners from a point at -`sk_ref` (5000 mm) on both axes, so a distance can't change sign.

## 360002 FRONT - FIXED GLASS UNIT, P01

```sh
python3 tools/fusion/run_script.py v2/01-CAD-Native/front/edit_test_front.py \
    --arg anchors=v2/01-CAD-Native/front/360002_P01_FRONT-FIXED-GLASS-UNIT_ANCHORS.json \
    --arg "edits=pod_w=2600 mm;fr_dz=12 mm;fix_xk=511 mm;door_xtr=1192 mm"
```

Four skeleton edits at once: the pod 100 mm wider, the front 5 mm higher, the pane's knee 10 mm further left, and the door's top-right corner 10 mm further right (so the free edge, which follows the door edge, tilts).

| State | Box X x Y x Z (mm) | Unhealthy items | Loose sketches | Anchors off their expressions | Worst (mm) |
|---|---|---|---|---|---|
| Before | 1032.7 x 15.0 x 2040.0 | 0 | 0 | none | 0.010 |
| pod_w 2600 mm; fr_dz 12 mm; fix_xk 511 mm; door_xtr 1192 mm | 1123.5 x 15.0 x 2045.0 | 0 | 0 | none | 0.010 |
| Reverted | 1032.7 x 15.0 x 2040.0 | 0 | 0 | none | 0.010 |

**RESULT: PASS (CAD check on a copy)**, 16 anchors.
