# v2/00-Control: the Spaceship control pack

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-CTL-000 | P01 | DRAFT | 2026-10-31 | Control pack |

Spaceship is the working name for FocusPod v2. This folder is its single source of truth before CAD: what we're building, how it splits, what's still open, and the rules every file follows. It covers Milestone 1 of the engineering guideline (§11).

The PM (the Swarm Lead) decides and logs each decision in [`decision-log.md`](decision-log.md). Nothing waits for outside approval, and there are no human hardware leads on this project (D-32). The factory's wall-and-door sample is the physical check.
- **DECIDED** means the PM has ruled.
- **PROPOSED** means our working answer until the PM rules.

Nothing here is released for production.

**Headline today (D-27, D-37, D-49 to D-53, D-59 to D-88):**
- A 4+4 laminated front of toughened, heat-soaked panes, frameless as in v1, over a black anodised kick strip; the door unit is about 49.1 kg, so its hinges, on HOLD, must be rated for 60 kg or more and hold it closed, and a 35 N magnetic catch in DT keeps it shut, with no load on the fixed glass (D-46, D-56, D-67, D-68, D-83). Both panes stay 4+4 (D-82). There is no threshold and no step: the pod has no floor, and the drop seal closes on the room floor (D-132).
- Walls and ceiling on one 84 mm stack on welded galvanized steel frames with the same outside sections (D-131), joined by captive ISO 4762 M6 × 16 bolts with one 5 mm key at 2.26 mm metal-stop seams, every cross-team bolt pattern from one skeleton rule (D-63 to D-66, D-75). The pod is 409.0 kg as shipped on the merged count, which still has the aluminium frames and the floor; D-131's steel frames add about 40 to 65 kg and D-132's no floor takes off about 21 (assumption: the PM's estimates), under a cap of 460 kg as shipped, provisional until the sample panel's recount (D-131; it was 420), with the voice kit's 4.0 kg reserve outside the cap (calculation, the layout study's live count with AIR's parts from CAD (PR #91) and D-130's intake boot and gaskets (PR #254), after FRONT's decor blocks (PR #105), WALL's B1 and B2 back panels and their cassettes (PR #205), D-121's and D-124's fan boxes (PR #199) and D-117's frame cleats (PR #195); D-116's thinner casings are withdrawn (D-121)). About 19.3 dB calculated (range 14.6–21.7, about 24 dB at best); the wall sample, measured down to 100 Hz, decides (D-53).
- Fresh air driven by CO2 and heat, holding 800 ppm in a 600 ppm office and at most 4 K over the room: never below 26 l/s with someone inside, about 33 l/s for one person, 53 l/s for two and a 65 l/s boost (D-50, D-52). The air runs inside the pod: in through a flush mesh in the base band under the right decor block, up to the supply fans high in that block, down a felt-covered air column; out through a soffit above the door and a roof slot behind the block. 25.2 dB(A) at 53 l/s and 29.6 at 65 l/s, the boost reaching 66.2 l/s at 30 dB(A), with D-130's sealed intake boot and gaskets (calculation, the air report, PR #254; DR as built without them, 33.3 and 37.8): 0.4 dB(A) under the limit, a risk until the fan sample measures it (ISS-090). Two people put about 249 W into the air: 3.9 K over the room at 53 l/s (calculation, PR #72). The voice kit gets 40 W on average, on two separate 12 V Class 2 feeds of 48 W or less each (D-136); with it fitted, the fans boost to hold 4 K at 30 dB(A) or less (D-88).
- Decor blocks 205 mm deep and side walls 1495 deep, as v1 measures (D-49). Inside: an empty floor, a light shelf, and a 1000 mm ledge with a screen on the right wall (D-70).

## Read first

1. `AGENTS.md`: the repo rules.
2. `docs/engineering-guideline.md`: the hardware team's guideline (Vietnamese), mandatory for every version.
3. `v2/PLAN.md`: the approved plan and targets. Where it disagrees, the decision log wins.
4. `v2-build-plan.pdf` (this folder): the v2 build plan, with pictures. It's in Vietnamese; `requirements.md` §G translates every line.
5. [`decision-log.md`](decision-log.md): the PM's decisions D-01 to D-136, with reasons.
6. [`requirements.md`](requirements.md): what v2 must meet, with a status and a source for each line.
7. [`conventions.md`](conventions.md): units, the ISO list, axes (with a [diagram](pod-coordinate-system.svg)), names, part numbers (with the reserved old numbers), file names, revisions and status values.
8. [`assembly-tree.md`](assembly-tree.md): how the pod splits, where every plan code goes, the interfaces, and the v1 counterparts.
9. [`open-questions.md`](open-questions.md): answers for door and glass, lights, door hand and the thin floor.
10. [`issue-register.csv`](issue-register.csv): 90 issues (42 open, 9 proposed, 27 decided, 12 closed). Each closes on the PM's logged decision plus evidence.
11. [`document-register.csv`](document-register.csv): every file in `sources/v1`, `docs` and `v2`, with code, revision, status, date, source and relation.
12. [`release-checklist.md`](release-checklist.md): what stands between the design and a manufacturing release, part by part, with the totals per team. `build_release_checklist.py` writes it from the master BOM, the CAD, drawing and manufacturing folders, and the draft FAI plan ([`v2/06-Verification/fai-plan.md`](../06-Verification/fai-plan.md)); re-run it when parts merge.
13. Background: `v2/research/market-study.md` and `sources/v1/README.md`.

## Status of each scope

| Scope | Where it stands | Status | Next | Key issues |
|---|---|---|---|---|
| BASE | No floor (D-132): people stand on the room floor, with no step at the door. The aluminium base band stays, black anodised and following v1's faceted front; its piece under the right block is the flush mesh intake (D-62, D-66, D-67), and its base seal is a soft lip on its inner face that presses on the room floor (D-132). Walls stand on it at a 2.26 mm stop, on one skeleton bolt rule (D-64, D-75). | DECIDED | BASE CAD (M3); the next skeleton update (ISS-086) | ISS-040, ISS-053, ISS-054, ISS-084, ISS-085 |
| WALL | 84 mm: a 46 mm outer panel (ACP 3 on a 3 mm bond line to a welded galvanized steel 20 × 40 frame with members about 300 apart: pre-galvanized steel (Z100, pending the Joints check) of 280 MPa yield or more, 1.0 mm for the perimeters and fixing members and 0.8 mm for the studs (D-131, D-135, the Joints check), 40 mm PET, 40 × 40 corner tubes) plus a floating lining cassette (0.5 mm steel tray with 12 mm lips, 25 mm gap, 9 mm felt). No plywood (D-16, D-17, D-37, D-54, D-63, D-66, D-69). Side walls 1495 deep (D-49); in skeleton P04 the side panels are 1492.74 × 1142.74 and the back panels 1200.61 × 1118.61, reaching the ceiling frame (D-66). Captive ISO 4762 M6 × 16 bolts with one 5 mm key at 2.26 mm metal-stop seams; the back's centre seam is the slotted closing seam (D-63 to D-65). | DECIDED stack and joints | Rivnut torque on HOLD (D-48); WALL CAD (M3) | ISS-011, ISS-016, ISS-034, ISS-050, ISS-086 |
| FRONT | Decor in Dark Yellow (D-12), 205 mm deep as v1 measures (D-49), not split (D-04), hollow; DR stands on the band at Z 110 and holds the intake riser and the supply fan pair (D-61, D-66). 4+4 laminated glass, frameless (D-27): the door glass runs 25 mm into a black anodised kick strip holding the drop seal; the fixed glass sits 11.5 mm deep in hidden U-channels, 4 mm from the door's edge (D-67, D-68, D-74). Left-hinged in a 160 mm pocket in DL (D-19, D-30); the door unit is about 49.1 kg, so the hinges, on HOLD, must be rated for 60 kg or more and hold it closed; a 35 N magnetic catch in DT and a magnetic seal pair keep it shut, with no load on the fixed glass (D-46, D-56, D-68, D-83). | DECIDED; handle and seals PROPOSED (Q1) | Door-load check; FRONT CAD (PRs #27, #28) | ISS-002, ISS-012, ISS-014, ISS-045, ISS-059, ISS-074 |
| CEILING | The wall stack, 84 mm (D-42, D-66): welded galvanized steel 20 × 40 frames (D-131) spanning frame to frame, 1200.61 per half (D-55, D-66), closing at a slotted centre seam by assembly order (D-64, D-65), and the floating steel-and-felt cassette with its 25 mm gap. The soffit above the door takes the front strip, so the cassettes stop at its back face: 1160 × 1045 in the 1051 mm space behind it; the roof slot goes through the right outer panel (D-61, D-69, D-77). Light and sensor cables run in the cassette gap, entering at the back-wall top corner (D-41). | DECIDED stack and cable route | CEILING CAD (PR #32); sprinkler strategy in the US rules phase | ISS-052, ISS-071, ISS-082 |
| LINING | Floating cassettes, made at the factory and hung on captive clips with a rated load, plus a safety catch on the ceiling ones; hook-and-loop only lines them up (D-47). Trays have 34 mm returns and 12 mm lips that hold the felt; the ceiling ones add 2 ribs (D-69). The factory's 9 mm felt is tested first (D-08, D-17, D-31). | DECIDED build; clip part and felt certificate on HOLD (D-56) | Clip and catch; the wall sample's push test (ribs) | ISS-015, ISS-064, ISS-075, ISS-076 |
| AIR | Inside the pod (D-60 to D-62): room air in through a flush black mesh in the base band under the right decor block, up a 1 mm steel riser to the supply fan pair high in the block, then down a 217 × 360 mm felt-covered air column through its cartridge to a kick grille; exhaust in at the far end of a 360 × 220 mm felt-covered soffit above the door, along its cartridge to the exhaust fans and out a roof slot behind the block, about 2.3 m above the intake. One cartridge part per path, 173 × 314 × 1750 mm; four 12 V fans on two balanced signals; serviced from inside (D-59, D-61). CO2 and heat drive them (D-43, D-44, D-50, D-52): never below 26 l/s while someone is inside, about 33 l/s for one person, 53 l/s for two, a boost to 65 l/s; 25.2 dB(A) at 53 l/s and 29.6 at 65 l/s with D-130's sealed intake boot and gaskets (calculation, the air report, PR #254; D-62, D-121, D-124, D-130; 0.4 under the limit). | DECIDED; fan octave test and CAD fit on HOLD (D-56) | Fan-sample test; cartridge mock-up; CAD fit of the column, soffit and intake | ISS-010, ISS-049, ISS-073, ISS-077, ISS-078, ISS-089, ISS-090 |
| ELECTRICAL | 12 V DC bus, with mains only to the outlets: US 120 V, 60 Hz on the prototype too, on UL-listed parts, tamper-resistant NEMA 5-15R sockets and a 120 V cord and inlet (D-133); the four fans are 12 V too, on two signals (D-10, D-51, D-61). Sensor hub in the air column (D-70). Lights: a light shelf on the wall tops lighting the felt ceiling, with scenes including a 'call' scene; no front face light (D-70). Voice cockpit hooks: two separate 12 V Class 2 feeds of 48 W or less each, each from its own 60 W supply, so ELECTRICAL adds a 4th (D-136), data, mounts and a cable path (D-11); the kit's budget is 40 W on average (D-88). Cables clip only to the cassette (D-26). | DECIDED architecture; design OPEN | Load table and wiring diagram | ISS-005, ISS-060, ISS-061, ISS-062, ISS-071 |
| INTERIOR | An empty floor: no table (D-06). The marketing lead's interior spec is adopted as principles: the walls do the work, clear glass, a neutral inside; a 1000 mm ledge and a screen up to about 900 mm on the right wall, the light shelf, the hub in the air column, and the air column and soffit casings (D-60, D-70). | DECIDED | INTERIOR and AIR CAD (CEILING group) | ISS-006 |
| PACKAGING | 48 × 40 in pallets plus one standard long pallet (D-04). | DECIDED pallets; layout OPEN | Layout study | ISS-048, ISS-057 |
| Control pack | This folder, the master BOM (`v2/04-BOM/`) and the draft FAI plan (`v2/06-Verification/`). | DRAFT P01 | Re-run the release checklist as parts merge | — |

## Still PROPOSED (the PM to rule)

- The door swing (outward; ISS-055).
- The 30 W lighting budget, and the voice cockpit zones other than the screen (REQ-VCK-02).
- What "one hand tool" and "part" mean (ISS-047), and the doorway check rule (ISS-048).
- The plan code readings (ISS-007, ISS-008, ISS-032, ISS-033) and whether VT05 stays (ISS-037).
- The pod axes, file names and revision codes in `conventions.md` (part numbers are decided: D-22, D-28).

## Top findings

- **v1 is marketed at about 30 dB, but the calculation gives about 15 dB as built** (ISS-065). Don't use 30 dB as a baseline until v1 is tested in a lab.
- **The v1 door is a trapezoid** with a slanted leading edge, 2.08 m², not the BOM's 2.36 m² rectangle. In 4+4 laminated glass it weighs about 43 kg (ISS-023, calculation C5).
- **The v1 BOM understates plywood:** it says 9 mm, while the drawings and CAD say 15 mm. Any v1 weight taken from the BOM is low (ISS-018, ISS-021).
- **The v1 CAD duplicates some parts:** its 8 leveling feet sit in only 6 places and its 3 hinges in only 2. Both are closed with no v2 impact (ISS-017, ISS-024).
- **Next physical checks:** the silencer absorption needs a mock-up (ISS-073), and the wall-and-door sample decides the sound (D-32).

## How to check this pack

```
python3 v2/00-Control/check_control_pack.py
python3 v2/00-Control/build_release_checklist.py --open-prs   # main plus the open PRs; no flag: this working tree
python3 v2/00-Control/test_build_release_checklist.py
```

It re-runs the acceptance checks:
- every file in `sources/v1`, `docs` and `v2` is in the register;
- every plan code and plan item is mapped, with its interfaces;
- every issue has an owner, a confirmer and a close condition, none of them a placeholder;
- the conventions define the axes and the part numbers, and no reserved old number is used;
- every requirement has a real status and a source, with no duplicate IDs;
- every decision cited anywhere in the pack exists in the log, with a date, a reason and what it affects.

## Who owns what

This folder belongs to the control pack; the decision log records the PM's decisions. `v2-build-plan.pdf` is an input and is never edited. Other groups write in their own folders. The control pack owns `document-register.csv` and adds the folder rows for every group's folders, so other PRs don't edit it (D-78). It also owns the master BOM in `v2/04-BOM/`, rebuilt by `build_master_bom.py` from the teams' parts lists and the joints register. ELECTRICAL and the Packing and Assembly team have their own folders (D-80). `tools/fusion/` sits outside the register's scope (`sources/v1`, `docs`, `v2`).
