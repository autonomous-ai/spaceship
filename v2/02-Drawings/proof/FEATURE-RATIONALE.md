# Feature rationale: proof frame V2-SWL-10 (PROPOSED)

Engineering guideline section 7, for the 12 joint holes of the proof part. Phase 0 proof only: **DRAFT, not for manufacture.** Hole tags match the drawing and the hole tables. Coordinates are in the part system (see `v2/01-CAD-Native/proof/MANIFEST.md`): datum A = frame outer face (Y = 0), B = bottom face (Z = 0), C = front face (X = 0).

## Hole groups

| Tags | Part + rev | View | Function | Mates with | Size | Position | Source and status |
|---|---|---|---|---|---|---|---|
| H01-H04 | V2-SWL-14 rail top, P01 | Top view; hole table 1 | M6 bolt joint to the upper side frame (build plan II: the side wall is two frames joined with M6x60 bolts) | Bottom rail of the upper side frame, same pattern | Ø6.6 through both tube walls, axis vertical, entry from the top face | X = 60, 510, 960, 1410 from C (pitch 450); Y = 10 from A (tube centre line) | Ø6.6: SOURCE ISO 273 medium clearance for M6. Edge distance 60 and pitch ≤ 500: ASSUMPTION until J-WALL-01 |
| H05-H08 | V2-SWL-13 rail bottom, P01 | Top view (hidden below H01-H04); hole table 1 | M6 bolt joint to the base (build plan rule 6: walls bolt to the floor frame with M6) | Base or thin-floor edge member, not designed | As H01-H04 | Same X and Y as H01-H04 | HOLD: the base joint depends on the floor choice (thin floor PROPOSED) |
| H09-H12 | V2-SWL-11 stile rear, P01 | View from the back; hole table 2 | M6 bolt joint to the back wall frame (build plan joint detail: side and back walls bolted) | End stile of the back wall frame; nut or rivnut there, not designed | Ø6.6 through both tube walls, axis along X, entry from the bay side (X = 1450) | Z = 60, 403.33, 746.67, 1090 from B (pitch 343.33); Y = 10 from A | Edge distance and pitch ≤ 400: ASSUMPTION until J-WALL-02 |

## Why these values

- **Ø6.6 clearance**: ISO 273 medium series for M6 (SOURCE). It lets an M6 bolt (Ø6.0 max) pass both frames with room for position error.
- **Hole on the tube centre line (Y = 10)**: the bolt then bears on both tube walls evenly and stays clear of the skin bond face (datum A) and the felt face. CALCULATION: tube_size / 2.
- **Edge distance 60**: the first hole must clear the stile (20), the weld bead (about 3), the washer (ISO 7089 M6, outside Ø12, radius 6) and leave swing for an open-end wrench inside the bay (about 25). 20 + 3 + 6 + 25 = 54, rounded up to 60. ASSUMPTION: to be confirmed by the tool access check in the joint register.
- **Equal pitch, count from a maximum pitch**: the count is `ceil((L - 2 x 60) / pitch_max) + 1`, so a longer or shorter frame keeps the same edge distance and never exceeds the maximum pitch. The maximum pitch (500 rails, 400 stile) is an ASSUMPTION: the joint register must set it from gasket compression and frame stiffness (the guideline warns that a rule like "every 300 mm" is not a reason by itself).
- **Mid rail clearance**: no rear stile hole may sit within tube_size / 2 + 12 of the mid rail centre line, so the bolt head and the wrench clear the mid rail weld. The build script checks it (`mid rail zone check: OK`).

## Tolerance

Floating-fastener rule: position tolerance (diameter, at maximum material) T = H - F = 6.6 - 6.0 = 0.6 for each frame (CALCULATION). If both frames hold Ø0.6 position to A, B and C, M6 bolts always pass. HOLD: whether a welded 20x20 frame holds Ø0.6 after welding is for the shop to confirm; the fallbacks are drilling after welding in a jig, or slots in one of the two frames. The drawing shows this as a proposal, not a released tolerance.

## Stack still to draw (HOLD)

The M6x60 bolt from the build plan fits the frame-to-frame joint (two 20 mm tubes = 40 mm grip, two washers, nut, about 12 mm left over inside the bay). For the rear stile joint it is too long if the back wall takes a rivnut: 60 mm from the bay side would run through the back wall's tube and reach its skin. The joint register (J-WALL-02) has to draw the real stack and pick the length.
