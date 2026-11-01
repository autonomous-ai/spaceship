# WALL rework plan: every part a component (D-120), with mitred corners (D-117)

Status: IN PROGRESS (2026-11-01). The owner kept v2's lighter construction and D-117 is confirmed, so the rework runs: the L1 sample (frame and panel) first, then the other designs in batches (D-118). Numbers: D-123.

Source: the build plan's rule 2, "model each part as a component, never a body" (`v2/00-Control/v2-build-plan.pdf`, now the main guide), as the PM's ruling D-120.

## What changes in the 16 WALL designs

| Item | Today | After the rework |
|---|---|---|
| Frame 2111xx / 2112xx | one component, 7 tube bodies (rails, stiles, studs) | an assembly: one component per member type, each with its part number; the repeated studs are copies (occurrences) of one component |
| Frame corners | butt-cut members, rails full length (D-115 cleats noted, not modelled) | the 4 perimeter corners mitred at 45° (D-117); studs butt-cut with T cleats; the Joints Engineer's cleats placed by reference when they land |
| Fill 2115xx / 2116xx | one component, one body per bay | one component per bay piece, straight in the panel assembly, each with its part number (identical pieces share a number and are copies); the panels' fill numbers 211501-211504 and 211601-211604 are cancelled (D-123); each piece form is cut from its own DXF, no drawing (D-128, FILL-PIECES.md, check_fill_dxfs.py) |
| Joint hardware (838003, 831002, 831001, 838002 ...) | one component per part number holding N bodies | one component per part number with one body, placed N times as copies, patterned with the holes so an edit moves them |
| Skin, tray, felt | one body per component already | no change |
| Clip zones (H03) | a reserved-space component, 4 bodies | no change: a reserved space, not a part (`config/reserved-spaces.csv`) |

The outside look, the frame envelope, every hole position and the joints stay as they are; only the member split at the 4 corners changes (no hole is within 100 of a corner).

## Part numbers needed first (the master BOM assigns them, D-28)

- **Frame assemblies:** a frame is now an assembly, so its number belongs in the 0001–0999 band (conventions §6). Either keep 2111xx/2112xx (no ripple through drawings and lists) or move them; the PM's call.
- **Members:** allocated per position for L1, R1, L2, R2, B1 and B2 (2121xx-2126xx); B3 and B4 get theirs when their lists exist (D-123). PM rule (2026-11-01): members share a number only when one solid matches the other moved or turned, never mirrored, with the same section, length, both end cuts (mitres, cleat slots) and holes. `v2/03-Manufacturing/wall/check_member_identity.py` finds them from the STEPs; on the pre-rework STEPs it finds 18 distinct parts in 6 positions (about 19 in all 8). It is run on the rebuilt STEPs and the list goes to Control, which marks the freed numbers CANCELLED.
- **Fill pieces:** one number per distinct form (15, allocated, #198).

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

## Log (2026-11-01, UTC)

- 03:01 L1 sample (frame, then panel): both stopped at the first mitre sketch, nothing saved: `VCS_SKETCH_OVER_CONSTRAINTS`. Fusion gives a straight side its own vertical or horizontal constraint, so dimensioning both its corners repeated it. Fixed by one polygon helper for both walls (`poly_plan`, tested offline; `poly_on`).
- F-189 (the Checker's copy check): WALL's spigot copy had an assumed 10 mm thread against Joints' 8 mm. WALL now places Joints' own STEPs of the spigot 831001 and the stop washer 831002 (one source, as D-95 for the keys).
- B3 and B4 (Lead, option a): one new number for the upper top rail, one part for both turned end for end; B1's and B2's numbers for the other members, with B3's and B4's frames added as their parents by Control. Confirmed with `check_member_identity.py` once built.
- B4's bay 3 takes F13 turned over: a copy of bay 1's part, turned half round by a rigid joint to the bottom rail's vertex at the bay's corner (`place_turned_copy`).
- Next Fusion run: L1 frame and panel with the B2 frame and panel (the back sample), one queue place.
- D-131 (PM): the frames turn to welded, galvanized steel in the same sections; L1 is the sample, the other panels wait for its review (wall_batch.py holds them). The Joints Engineer's details: 1.2 mm side rails and front stiles, 1.0 for the 40 x 40 members and back perimeters, 0.8 studs; yield 280 MPa or more (S280GD+Z or SGC400), pre-galvanized, zinc-painted welds, no hot-dip; mitred corners with a 2 mm plate welded in (831007 to 831009, register H-40 to H-42), each member cut back for it; rivnut 838003 now the steel CAH2-610-4.2 (same head and grip).
- D-135 (PM): the skin flexes 2 mm or less under a 100 N push at a bay's centre, so members about 300 apart: 5 studs on a side panel, set from the bolts so each bolt stays 30 or more clear (R-J14), 3 on a back panel; B2 keeps its 373 mm first bay at ELECTRICAL's unit, framed with welded cross members (waits for D-133's unit). New fill list (14 forms) sent to Control for numbers.
- 05:32 the L1 steel run (old stud spacing) built the reworked structure end to end (members, mitres, studs, fill pieces, 18 hardware copies from Joints' STEPs, 0 clashes) and failed only on the frame's stud occurrence pattern and two STEP-import timeline groups. Studs are now copies held by joints on both walls, and every unhealthy item prints Fusion's message.
- A dry run in unsaved documents (wall_dry_run.py: L1 and B1 panels and cassettes) is queued to prove the new pieces before the L1 sample, which waits for the fill numbers.
- Dry runs 1 to 4 (unsaved): plates first had no turn (a point joint takes the part's own axes, and a joint made inside the frame doesn't move it) and are now placed by joint origins with axes and joints in the root; the studs' sketch over-constrained and moved to offset joint origins; a turned fill copy came out mirrored (a joint origin's own angle turns its offsets too) and is now turned by the joint's angle.
- #294 (Joints' plate STEPs) merged: the builder imports them in place of its boxes; the boxes' overlap allowance is gone (Lead): any overlap left is a real clash. Lead (2026-11-01): the plates stay square laser-cut blanks, made a little shorter at each end so their square edges sit about 0.5 inside the frame's outer faces; the builder reads each plate's size from its STEP, so the shorter blanks drop in.
- Dry run 5 (L1, B1) and 6 (R1, L2, B3, B4): every plate, stud and fill copy placed, notches open, 0 loose sketches. Two faults, both fixed: the back panels' closing-seam lead-in (R-J9, FR-13) lies wholly in the corner weld under D-131 (the members stop 1.41 short of the corner for the plate), so it is ground into the weld after welding, a step in the frame's process, not a cut; and each STEP import's timeline group reports "unknown" (a group has no health of its own; its occurrence and base feature are healthy, the import probe showed), so groups are judged by their own items. The only clash left is the full-size plate's square end against the side skin's back return at the side panels' two back corners (about 10 mm3 each), which the shorter blanks clear.
- Dry run 7 (the import probe and B1): B1 builds clean (0 unhealthy items, 0 loose sketches, 0 clashes).
- The L1 sample is queued behind a gate: it builds only once the shorter plates are in the worktree with the README origin kept at the frame's outer corner.
