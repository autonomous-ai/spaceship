# v2/00-Control: the Spaceship control pack

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-CTL-000 | P01 | DRAFT | 2026-10-31 | Control pack |

Spaceship is the working name for FocusPod v2. This folder is its single source of truth before CAD: what we're building, how it splits, what's still open, and the rules every file follows. It covers Milestone 1 of the engineering guideline (§11).

The PM (the Swarm Lead) decides and logs each decision in [`decision-log.md`](decision-log.md). Nothing waits for outside approval, and there are no human hardware leads on this project (D-32). The factory's wall-and-door sample is the physical check.
- **DECIDED** means the PM has ruled.
- **PROPOSED** means our working answer until the PM rules.

Nothing here is released for production.

**Headline today (D-27, D-37, D-42, D-46 to D-59):**
- A 4+4 laminated front of toughened, heat-soaked panes, frameless as in v1, with an 85 mm dark kick strip at the bottom; the door hardware and the glass product are on HOLD until rated parts are named (D-46, D-56).
- Walls and ceiling on one 81 mm stack. The pod is estimated at about 427 kg, open against the 420 kg cap until the wall sample settles it (D-54). About 19.3 dB calculated (range 14.6–21.7, about 24 dB at best); the wall sample, measured down to 100 Hz, decides (D-53).
- Fresh air driven by CO2 and heat, holding 800 ppm in a 600 ppm office and at most 4 K over the room: never below 26 l/s with someone inside, about 33 l/s for one person, 53 l/s for two at 26 dB(A) or less, and a boost to 65 l/s at 30 dB(A) (D-50, D-52). Four 12 V fans in two boxed cartridges in the right decor block, supply low and exhaust high (D-51).
- Decor blocks 205 mm deep and side walls 1495 deep, as v1 measures (D-49).

## Read first

1. `AGENTS.md`: the repo rules.
2. `docs/engineering-guideline.md`: the hardware team's guideline (Vietnamese), mandatory for every version.
3. `v2/PLAN.md`: the approved plan and targets. Where it disagrees, the decision log wins.
4. `v2-build-plan.pdf` (this folder): the v2 build plan, with pictures. It's in Vietnamese; `requirements.md` §G translates every line.
5. [`decision-log.md`](decision-log.md): the PM's decisions D-01 to D-60, with reasons.
6. [`requirements.md`](requirements.md): what v2 must meet, with a status and a source for each line.
7. [`conventions.md`](conventions.md): units, the ISO list, axes (with a [diagram](pod-coordinate-system.svg)), names, part numbers (with the reserved old numbers), file names, revisions and status values.
8. [`assembly-tree.md`](assembly-tree.md): how the pod splits, where every plan code goes, the interfaces, and the v1 counterparts.
9. [`open-questions.md`](open-questions.md): answers for door and glass, lights, door hand and the thin floor.
10. [`issue-register.csv`](issue-register.csv): 73 issues (30 open, 9 proposed, 22 decided, 12 closed). Each closes on the PM's logged decision plus evidence.
11. [`document-register.csv`](document-register.csv): every file in `sources/v1`, `docs` and `v2`, with code, revision, status, date, source and relation.
12. Background: `v2/research/market-study.md` and `sources/v1/README.md`.

## Status of each scope

| Scope | Where it stands | Status | Next | Key issues |
|---|---|---|---|---|
| BASE | Thin floor inside the aluminium base band, in a dark finish, with a 20 mm threshold (D-05, D-18, D-40). PROPOSED layer build: about 20 mm, walls standing around it on a base rail, packers for leveling (Q4). | DECIDED type; layers PROPOSED | Layout study; BASE CAD in Milestone 2 | ISS-040, ISS-050, ISS-054 |
| WALL | 81 mm: ACP 3 on an aluminium 20 × 40 × 1.2 frame at 400 with 40 mm PET, plus a floating lining cassette with a 0.5 mm steel tray, 25 mm gap and 9 mm felt. No plywood (D-16, D-17, D-37, D-54). Side walls 1495 deep (D-49). 2 sheets per side wall, 4 at the back, aligned reveals (D-23); the back frames span frame to frame, about 1207 per half, with 1169 linings (D-55). | DECIDED stack | Rivnut torque on HOLD (D-48); M6 anchor; ACP-to-frame joint | ISS-011, ISS-016, ISS-034, ISS-050 |
| FRONT | Decor in Dark Yellow (D-12), 205 mm deep as v1 measures (D-49), not split (D-04), hollow; the right block holds the fans and the two cartridges (D-51). 4+4 laminated glass, frameless (D-27), with an 85 mm kick strip holding the drop seal (D-40, D-57). Left-hinged in a 160 mm pocket in DL (D-19, D-30); the hinges, the lock and the glass product are on HOLD (D-46, D-56). | DECIDED; handle and seals PROPOSED (Q1) | Door-load check for the 47.5 kg door unit; depth chain on the GA | ISS-002, ISS-012, ISS-014, ISS-045, ISS-059, ISS-074 |
| CEILING | The wall stack, 81 mm: 20 × 40 × 1.2 aluminium frames spanning frame to frame, about 1207 per half (D-55), and the floating steel-and-felt cassette with its 25 mm gap (D-42). Light and sensor cables run in that gap, entering at the back-wall top corner (D-41). | DECIDED stack and cable route | Sprinkler zone | ISS-052, ISS-071 |
| LINING | Floating cassettes, made at the factory and hung on captive clips with a rated load, plus a safety catch on the ceiling ones; hook-and-loop only lines them up (D-47). The factory's 9 mm felt is tested first (D-08, D-17, D-31). | DECIDED build; clip part and felt certificate on HOLD (D-56) | Felt-to-steel fixing, clips, joint detail | ISS-015, ISS-064, ISS-075, ISS-076 |
| AIR | Four 12 V fans in two boxed cartridges side by side in the right decor block: room air drawn in low, exhaust out through a 150 mm riser to the top slot at least 1 m above (D-51, D-58); both grilles sit on the block's removable, felt-covered inner face, and the cartridges slide out into the pod for service (D-59). CO2 and heat drive them: 800 ppm or less in a 600 ppm office, at most 4 K over the room, never below 26 l/s while someone is inside, about 33 l/s for one person, 53 l/s for two at 26 dB(A) or less, and a boost to 65 l/s at 30 dB(A), also by hand (D-43, D-44, D-50, D-52). | DECIDED; fan octave test and riser fit on HOLD (D-56) | Fan-sample test; cartridge mock-up; riser fit in CAD | ISS-010, ISS-039, ISS-049, ISS-073, ISS-077, ISS-078 |
| ELECTRICAL | 12 V DC bus, with mains only to the outlets; the four fans are 12 V too (D-10, D-51). Sensor hub. One dimmable 12 V LED ceiling light plus a front face light (D-20). Voice cockpit hooks of 12 V 5 A, data, mounts and a cable path (D-11). Cables clip only to the cassette (D-26). | DECIDED architecture; design OPEN | Load table and wiring diagram | ISS-005, ISS-060, ISS-061, ISS-062, ISS-071 |
| INTERIOR | Empty: no table (D-06). | DECIDED | — | ISS-006 |
| PACKAGING | 48 × 40 in pallets plus one standard long pallet (D-04). | DECIDED pallets; layout OPEN | Layout study | ISS-048, ISS-057 |
| Control pack | This folder. | DRAFT P01 | Re-review | — |

## Still PROPOSED (the PM to rule)

- The thin floor's layer build (Q4) and the door swing (outward; ISS-055).
- The 30 W lighting budget, and where the front face light and the voice cockpit zones go.
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
```

It re-runs the acceptance checks:
- every file in `sources/v1`, `docs` and `v2` is in the register;
- every plan code and plan item is mapped, with its interfaces;
- every issue has an owner, a confirmer and a close condition, none of them a placeholder;
- the conventions define the axes and the part numbers, and no reserved old number is used;
- every requirement has a real status and a source, with no duplicate IDs;
- every decision cited anywhere in the pack exists in the log, with a date, a reason and what it affects.

## Who owns what

This folder belongs to the control pack; the decision log records the PM's decisions. `v2-build-plan.pdf` is an input and is never edited. Other groups write in their own folders (the PLANNED rows in `document-register.csv`), and each adds file rows to the register when it releases files. `tools/fusion/` sits outside the register's scope (`sources/v1`, `docs`, `v2`).
