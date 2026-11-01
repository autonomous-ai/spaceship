# WALL rework plan: every part a component (D-120), with mitred corners (D-117)

Status: PLAN (2026-11-01). Built in one Fusion pass per design **after the owner answers the materials question**, so each frame is reworked once (D-120). Method proved on one sample first (D-118).

Source: the build plan's rule 2, "model each part as a component, never a body" (`v2/00-Control/v2-build-plan.pdf`, now the main guide), as the PM's ruling D-120.

## What changes in the 16 WALL designs

| Item | Today | After the rework |
|---|---|---|
| Frame 2111xx / 2112xx | one component, 7 tube bodies (rails, stiles, studs) | an assembly: one component per member type, each with its part number; the repeated studs are copies (occurrences) of one component |
| Frame corners | butt-cut members, rails full length (D-115 cleats noted, not modelled) | the 4 perimeter corners mitred at 45° (D-117); studs butt-cut with T cleats; the Joints Engineer's cleats placed by reference when they land |
| Fill 2115xx / 2116xx | one component, one body per bay | one component per bay piece, each with its part number (identical pieces share a number and are copies) |
| Joint hardware (838003, 831002, 831001, 838002 ...) | one component per part number holding N bodies | one component per part number with one body, placed N times as copies, patterned with the holes so an edit moves them |
| Skin, tray, felt | one body per component already | no change |
| Clip zones (H03) | a reserved-space component, 4 bodies | no change: a reserved space, not a part (`config/reserved-spaces.csv`) |

The outside look, the frame envelope, every hole position and the joints stay as they are; only the member split at the 4 corners changes (no hole is within 100 of a corner).

## Part numbers needed first (the master BOM assigns them, D-28)

- **Frame assemblies:** a frame is now an assembly, so its number belongs in the 0001–0999 band (conventions §6). Either keep 2111xx/2112xx (no ripple through drawings and lists) or move them; the PM's call.
- **Members:** about 5 member types per frame (side: bottom rail, top rail or 40 × 40 top member, front stile, 40 × 40 back stile, mid stud; back: bottom rail, top rail, outer stile, centre stile, mid stud). LH and RH get separate numbers where their holes mirror (conventions §5). Members identical in form, fit and function across positions share a number. Expected: under 40 numbers, counted from the model.
- **Fill pieces:** one number per distinct piece (the bays differ by their bolt pockets and B2's ELECTRICAL cut-outs).

## Code changes (all in WALL's own files)

- `wall_side_panel.py`, `wall_back_panel.py`: a member builder (one component per member type, occurrences for repeats, names `PARTNO NAME`); mitred ends by a 45° cut on each perimeter member; one component per fill piece; hardware as occurrences of one component per part, patterned like their holes.
- `report_wall_doc.py`: counts occurrences, so masses and quantities follow the copies.
- `make_parts_list.py`: the frame as an assembly row with its member rows (cut length outer to outer, "both ends 45°" or "square"); fill piece rows; hardware quantities from the occurrence count.
- `edit_test_wall.py`: checks per occurrence (members, pieces, hardware follow the skeleton edit); clash check over occurrence bodies.
- Drawings: the frame assembly drawing stays in Fusion; the members, plain tube cut parts, go to the drawing generator (D-112).

## Order and checks (D-118)

1. Sample: L1 frame, L1 fill and L1 hardware. Pass = every component has a part number; repeats are copies; quantities and masses follow the copies; 0 clashes; every sketch fully constrained; edit test passes; the STEP opens with the assembly tree; parts list and master BOM check clean. A Reviewer looks at it before step 2.
2. The other 15 designs in batches of six, each with the same checks.
3. Parts lists, cut files, rationale and drawings regenerated; one PR.

## Waits on

- The owner's materials answer. If the build plan's materials come back (20 × 20 steel box tube frames VT10, 6 mm plywood VT02 behind the ACP, felt on hook-and-loop), WALL is redesigned on those, and this plan's structure (members, pieces and hardware as components) carries over.
- D-117's text (mitre at the 4 perimeter corners; studs T-cleated, as assumed above).
- The part numbers above.
- The Joints Engineer's cleat components (D-115).
