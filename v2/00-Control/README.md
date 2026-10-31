# v2/00-Control: the Spaceship control pack

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-CTL-000 | P01 | DRAFT | 2026-10-31 | Control pack |

Spaceship is the working name for FocusPod v2. This folder is its single source of truth before CAD: what we're building, how it splits, what's still open, and the rules every file follows. It covers Milestone 1 of the engineering guideline (§11).

The PM (the Swarm Lead) decides and logs each decision in [`decision-log.md`](decision-log.md). Nothing waits for outside approval, and there are no human hardware leads on this project (D-32). The factory's wall-and-door sample is the physical check.
- **DECIDED** means the PM has ruled.
- **PROPOSED** means our working answer until the PM rules.

Nothing here is released for production.

**Headline today (D-27, D-33, D-37 to D-48):**
- A 4+4 laminated front of toughened, heat-soaked panes, frameless as in v1, with a 90 mm dark kick strip at the bottom; door hardware on HOLD until a rated set is named.
- Walls and ceiling on one 81 mm stack; the pod at about 418 kg against a 420 kg cap, and about 24 dB calculated.
- Fresh air set by the CO2 control to hold 800 ppm in a 600 ppm office: at least 26 l/s with one person, 53 l/s for two at 25 dB(A) or less, boost at 30 dB(A) or less aiming for 70 l/s.
- Decor blocks 230–235 mm deep, as in v1.

## Read first

1. `AGENTS.md`: the repo rules.
2. `docs/engineering-guideline.md`: the hardware team's guideline (Vietnamese), mandatory for every version.
3. `v2/PLAN.md`: the approved plan and targets. Where it disagrees, the decision log wins.
4. `v2-build-plan.pdf` (this folder): the v2 build plan, with pictures. It's in Vietnamese; `requirements.md` §G translates every line.
5. [`decision-log.md`](decision-log.md): the PM's decisions D-01 to D-48, with reasons.
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
| WALL | 81 mm: ACP 3 on an aluminium 20 × 40 × 1.2 frame at 400 with 40 mm PET, plus a floating lining cassette with a 0.5 mm steel tray, 25 mm gap and 9 mm felt. No plywood (D-16, D-17, D-34, D-37). 2 sheets per side wall, 4 at the back, aligned reveals (D-23). | DECIDED stack | Rivnut grip and fill checks (D-34); M6 anchor; ACP-to-frame joint | ISS-011, ISS-016, ISS-034, ISS-050 |
| FRONT | Decor in Dark Yellow (D-12), 230–235 mm deep as in v1 (D-39), not split (D-04), hollow, holding the fans and silencers (D-29, D-33, D-36). 4+4 laminated glass, frameless (D-27), with a 90 mm kick strip holding the drop seal (D-40). Left-hinged on dormakaba OFFICE 11.233 in a 160 mm pocket (D-19, D-30). | DECIDED; handle and seals PROPOSED (Q1) | Door-load check; depth chain on the GA; decor rebuilt from the v1 STEP | ISS-002, ISS-012, ISS-014, ISS-045, ISS-059 |
| CEILING | The wall stack, 81 mm: 20 × 40 × 1.2 aluminium frames and the floating steel-and-felt cassette with its 25 mm gap (D-42). Light and sensor cables run in that gap, entering at the back-wall top corner (D-41). | DECIDED stack and cable route | Sprinkler zone | ISS-052, ISS-071 |
| LINING | Floating cassettes, made at the factory and hung with tool-free clips. The factory's 9 mm felt is tested first (D-08, D-17, D-31). | DECIDED build; clips OPEN | Felt-to-steel fixing, clips, joint detail | ISS-015, ISS-064 |
| AIR | Fans inside the front decor blocks. The CO2 control holds 800 ppm in a 600 ppm office: at least 26 l/s while someone is inside, 53 l/s for two at 25 dB(A) or less, boost at 30 dB(A) or less aiming for 70 l/s, also by hand (D-43 to D-45). Splitter silencers in the right and top decor blocks: 37.5 mm linings, 212 mm cartridge, sliding in behind a felt-covered panel (D-29, D-33, D-36, D-38). | DECIDED; fan choice and mock-up OPEN | Pick the fan; silencer mock-up | ISS-010, ISS-039, ISS-049, ISS-072, ISS-073 |
| ELECTRICAL | 12 V DC bus, with mains only to the outlets, except for the mains EC fan fallback (D-10, D-29). Sensor hub. One dimmable 12 V LED ceiling light plus a front face light (D-20). Voice cockpit hooks of 12 V 5 A, data, mounts and a cable path (D-11). Cables clip only to the cassette (D-26). | DECIDED architecture; design OPEN | Load table and wiring diagram | ISS-005, ISS-060, ISS-061, ISS-062, ISS-071 |
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
