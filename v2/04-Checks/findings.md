# Mechanical check findings: Spaceship (FocusPod v2)

| Doc code | Revision | Status | Owner |
|---|---|---|---|
| V2-CHK-001 | P01 | Live register, rendered from `findings.json` by `tools/checks/register.py` | Mechanical Checker |

Every finding has an owner group and a status. **Severe findings block the owner's merge until they're fixed** (PM rule). The checks in `tools/checks/` re-run on main after every merge; a finding the checks no longer see on main closes with that revision as evidence. Findings written by hand close by hand, with evidence. ACCEPTED means the PM ruled it intended (D-number given).

Severity: **severe** = can't be made, assembled or used as drawn; **major** = will cause rework or a wrong part; **minor** = record keeping. Check codes: C01 clash and minimum gaps (Fusion); C02 tolerance stack-ups; C03 fastener and tool access; C04 weight, doorway and pallet fit; C05 drawing completeness; C06 BOM completeness; C07 fastener schedule and thread engagement; C08 hole-to-hole alignment; C09 edge distance, bend radius, hole-to-bend; C10 mixed metals; C11 material grade and finish.

## Open: 7 (4 severe, 2 major, 1 minor)

By owner group:

- BASE: F-006
- FRONT; Fusion Engineer 2: F-002
- Fusion Engineer 2: F-003
- Fusion Engineer 2; WALL; CEILING: F-004
- Joints Engineer; Fusion Engineer 2: F-001, F-005
- Layout Engineer: F-007

| ID | Severity | Check | Part | Finding | File | Fix | Owner group | Found | Posted |
|---|---|---|---|---|---|---|---|---|---|
| F-001 | severe | C02 | skeleton SEAM-GAPS | SEAM-BACK-CENTRE: B1 ENVELOPE to B2 ENVELOPE is 0.0 mm, needs at least 1 mm; SEAM-BACK-CORNER-L: L1 ENVELOPE to B1 ENVELOPE is 0.0 mm, needs at least 1 mm; SEAM-BACK-CORNER-R: R1 ENVELOPE to B2 ENVELOPE is 0.0 mm, needs at least 1 mm; SEAM-CEILING-CENTRE: C1 ENVELOPE to C2 ENVELOPE is 0.0 mm, needs at least 1 mm; SEAM-CEILING-SIDE: C1 ENVELOPE to L2 ENVELOPE is 0.0 mm, needs at least 1 mm. Rule source: assumption: 1.0 mm stands in until the joints register gives the compressed gasket thickness. Why: IF-04 asks for a seam gasket between B1 and B2 (and B3, B4); a gasket needs a gap of at least its compressed thickness, and frames cut to plus tolerance must still fit | `v2/03-Manufacturing/skeleton/100000_P03_POD-SKELETON_STEP.step` | Joints Engineer: set the compressed gasket thickness per seam. Fusion Engineer 2: add a seam_gap parameter and shrink the panels by it | Joints Engineer; Fusion Engineer 2 | 2026-10-31 1eec888 | Joints, Fusion Engineer 2, WALL, CEILING groups 2026-10-31 |
| F-002 | severe | C02 | skeleton KICK-OVER-THRESHOLD | KICK-OVER-THRESHOLD: KICK ENVELOPE to THRESHOLD ENVELOPE is 0.0 mm, needs at least 7 mm. Rule source: confirmed: FRONT's 7 mm floor gap for the drop seal, approved by the PM in the FRONT group on 2026-10-31. Why: The door swings over the threshold; with no running gap it rubs, and the drop seal needs the gap to close | `v2/03-Manufacturing/skeleton/100000_P03_POD-SKELETON_STEP.step` | Kick strip bottom at the threshold top plus 7 mm (Z 27 with a 20 mm threshold), carried as a skeleton parameter | FRONT; Fusion Engineer 2 | 2026-10-31 1eec888 | FRONT, Fusion Engineer 2 groups 2026-10-31 |
| F-004 | severe | C01 | skeleton shell back X -1207..1207 Z 2319..2357 | The outer shell is open on the back face of the skeleton: nothing covers X -1207 to 1207, Z 2319 to 2357 (a slot 2414 x 38 mm). Bordered by: B3 ENVELOPE, B4 ENVELOPE, C1 ENVELOPE, C2 ENVELOPE, L2 ENVELOPE, R2 ENVELOPE. Checked 1 mm inside the face on a 5 mm grid, bodies as their boxes. | `v2/03-Manufacturing/skeleton/100000_P03_POD-SKELETON_STEP.step` | Close it: extend the bordering panels to meet, or add the part that belongs there. | Fusion Engineer 2; WALL; CEILING | 2026-10-31 1eec888 | Fusion Engineer 2, WALL, CEILING groups 2026-10-31 |
| F-006 | severe | C01 | skeleton DR x BAND-R | DR's bottom follows the fixed glass bottom (Z 102), 8 mm into the right base band's front end (Z 10 to 110): 14394 mm3 of overlap, on the skeleton's own list of expected clashes as a HOLD for the base design (skeleton P03 BUILD-RECORD, clash check). | `v2/01-CAD-Native/skeleton/BUILD-RECORD.md` | BASE: notch the band or stop it short of DR in the base design; the Fusion clash check confirms it on the assembled CAD. | BASE | 2026-10-31 1eec888 | already in the BASE brief (not re-posted) |
| F-005 | major | C02 | skeleton SEAM-GAPS-HORIZONTAL | SEAM-SIDE-HORIZONTAL: L1 ENVELOPE to L2 ENVELOPE is 0.0 mm, needs at least 1 mm; SEAM-BACK-HORIZONTAL: B1 ENVELOPE to B3 ENVELOPE is 0.0 mm, needs at least 1 mm. Rule source: assumption: as SEAM-BACK-CENTRE. Why: IF-04 asks for a seam gasket between the lower and upper side panels; under the upper panel's weight it needs its compressed thickness or a groove | `v2/03-Manufacturing/skeleton/100000_P03_POD-SKELETON_STEP.step` | Joints Engineer: say whether the horizontal seams take a gasket in the gap (then a seam_gap) or in a groove (then no gap) | Joints Engineer; Fusion Engineer 2 | 2026-10-31 1eec888 | Joints, Fusion Engineer 2, WALL groups 2026-10-31 |
| F-007 | major | C04 | F-HW | F-HW FRONT - SEALED GLAZING PROFILES FOR THE FIXED GLASS (2200 x 120 x 60 mm) doesn't fit the 48x40 pallet it ships on (1219 x 1016, at most 1679 tall loaded above a 150 mm deck); it fits the 48x96 pallet. | `v2/05-Engineering/layout-study/out/parts-option-B1-final-stack.csv` | Move it to the right pallet in the layout study, or change the piece. | Layout Engineer | 2026-10-31 1eec888 |  |
| F-003 | minor | C02 | skeleton door_z0 | Skeleton P03 parameter door_z0 = 109 (pod_h - dt_h - door_h) is used by nothing and disagrees with door_zb = 105, where the door bottom really is (BUILD-RECORD). | `v2/01-CAD-Native/skeleton/pod_skeleton.py` | Remove door_z0, or derive it from door_zb so the two can't disagree. | Fusion Engineer 2 | 2026-10-31 1eec888 | Fusion Engineer 2 group 2026-10-31 |

## Closed and accepted: 0

| ID | Status | Severity | Check | Part | Finding | Owner group | Found | Closed or accepted |
|---|---|---|---|---|---|---|---|---|

