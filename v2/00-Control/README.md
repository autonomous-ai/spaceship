# v2/00-Control: the Spaceship control pack

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-CTL-000 | P01 | DRAFT | 2026-10-31 | Control pack |

Spaceship is the working name for FocusPod v2. This folder is its single source of truth before CAD: what we're building, how it splits, what's still open, and the rules every file follows. It covers Milestone 1 of the engineering guideline (§11).

The PM (the Swarm Lead) decides and logs each decision in [`decision-log.md`](decision-log.md); nothing waits for outside approval (`AGENTS.md`).
- **DECIDED** means the PM has ruled.
- **PROPOSED** means our working answer until the PM rules.

Nothing here is released for production.

## Read first

1. `AGENTS.md`: the repo rules.
2. `docs/engineering-guideline.md`: the hardware team's guideline (Vietnamese), mandatory for every version.
3. `v2/PLAN.md`: the approved plan and targets.
4. `v2-build-plan.pdf` (this folder): the indoor pod lead engineer's build plan, with pictures. It's in Vietnamese; `requirements.md` §G translates every line.
5. [`decision-log.md`](decision-log.md): the PM's decisions D-01 to D-26, with reasons.
6. [`requirements.md`](requirements.md): what v2 must meet, with a status and a source for each line.
7. [`conventions.md`](conventions.md): units, the ISO list, axes (with a [diagram](pod-coordinate-system.svg)), names, part numbers, file names, revisions and status values.
8. [`assembly-tree.md`](assembly-tree.md): how the pod splits, where every plan code goes, the interfaces, and the v1 counterparts.
9. [`open-questions.md`](open-questions.md): answers for door and glass, lights, door hand and the thin floor.
10. [`issue-register.csv`](issue-register.csv): 69 issues (36 open, 11 proposed, 18 decided, 4 closed), each with who confirms it and when it closes.
11. [`document-register.csv`](document-register.csv): every file in `sources/v1`, `docs` and `v2`, with code, revision, status, date, source and relation.
12. Background: `v2/research/market-study.md` and `sources/v1/README.md`.

## Status of each scope

| Scope | Where it stands | Status | Next | Key issues |
|---|---|---|---|---|
| BASE | Thin floor inside the aluminium base band, with a 20 mm threshold (D-05, D-18). PROPOSED layer build: about 20 mm, walls standing around it on a base rail, packers for leveling (Q4). | DECIDED type; layers PROPOSED | Layout study; BASE CAD in Milestone 2 | ISS-040, ISS-050, ISS-054 |
| WALL | Final stack, 81 mm at 13.1 kg/m²: ACP 3 on an aluminium 20 × 40 frame at 400 with 40 mm PET, plus a floating steel-and-felt lining cassette; no plywood (D-16, D-17). 2 sheets per side wall, 4 at the back, aligned reveals (D-23). | DECIDED stack | Split and part weights from the layout study; M6 anchor and ACP-to-frame joint | ISS-011, ISS-012, ISS-016, ISS-050 |
| FRONT | Decor per plan section VI, in Dark Yellow (D-12), not split (D-04), on aluminium frames (D-16). Smoked acrylic front, laminated glass as fallback; the factory sample decides (D-07). Left-hinged, hinge pocket in DL (D-19). Hardware PROPOSED (Q1). | DECIDED material, colour, hand | Hinges and seals from the hardware selection; door-load check; decor rebuilt from the v1 STEP | ISS-002, ISS-014, ISS-045, ISS-059, ISS-068 |
| CEILING | The wall stack on a 20 × 100 aluminium frame, 141 mm at 17.4 kg/m², with the silencers inside (D-16). Slot pattern undefined; sprinkler zone to reserve. | DECIDED stack | Air design; ceiling halves under 20 kg | ISS-010, ISS-052, ISS-067 |
| LINING | Floating cassettes: 0.5 mm steel tray, 25 mm gap, 9 mm felt, made at the factory, hung with tool-free clips (D-08, D-17). | DECIDED build; clips OPEN | Felt-to-steel fixing, clips, joint detail | ISS-015, ISS-064, ISS-069 |
| AIR | 70 l/s, CO2-driven, self-starting, 25 dB(A) or less at full flow, through the in-house sensor hub, on 12 V fans (D-09, D-10). | DECIDED targets; fans OPEN | Air design and fan choice | ISS-039, ISS-049 |
| ELECTRICAL | 12 V DC bus with mains to the outlets only (D-10); sensor hub; one dimmable 12 V LED ceiling light plus a front face light (D-20); voice cockpit hooks of 12 V 5 A, data, mounts and a cable path (D-11). | DECIDED architecture; design OPEN | Load table and wiring diagram | ISS-005, ISS-060, ISS-061, ISS-062, ISS-069 |
| INTERIOR | Empty: no table (D-06). | DECIDED | — | ISS-006 |
| PACKAGING | 48 × 40 in pallets plus one standard long pallet (D-04). | DECIDED pallets; layout OPEN | Layout study | ISS-048, ISS-057 |
| Control pack | This folder. | DRAFT P01 | Review | — |

## Still PROPOSED (the PM to rule)

- The thin floor's layer build (Q4) and the door swing (outward; ISS-055).
- The 30 W lighting budget, and where the front face light and the voice cockpit zones go.
- The depth chain between walls and decor (ISS-012).
- What "one hand tool" and "part" mean (ISS-047), and the doorway check rule (ISS-048).
- The pod axes, file names and revision codes in `conventions.md` (the part-number scheme is decided, D-22).

Facts only the team can confirm (indoor pod lead engineer):
- the VT03 double code (ISS-007) and two typos in the plan (ISS-008, ISS-032);
- what VT05 is for (ISS-037);
- the v1 file conflicts (ISS-017 to ISS-030).

## Top findings

- **v1 is marketed at about 30 dB, but the calculation gives about 15 dB as built** (ISS-065). Don't use 30 dB as a baseline until v1 is tested in a lab.
- The v1 door is a **trapezoid** with a slanted leading edge, not the BOM's rectangle. In glass it would weigh about 41.6 kg at 8 mm, not 47 (ISS-023, calculated from the v1 STEP).
- The v1 CAD's 8 leveling feet sit in only **6 places** (2 duplicates), so it agrees with the BOM's 6. Its 3 hinges sit in only 2 places (ISS-017, ISS-024).
- The v1 BOM understates plywood: 9 mm against 15 mm in the drawings and CAD. Any v1 weight taken from the BOM is low (ISS-018, ISS-021).
- The plan's fan (VT06) and speed knob (VT08) are mains parts. They don't fit the 12 V bus or a CO2-driven, self-starting fan (ISS-038, ISS-039).
- The final stack raised three points, now decided:
  - The ceiling fill rides on its cassette, so each ceiling panel stays at 20 kg or less (D-24).
  - A laminated fallback front gets a 420 kg cap, with weight offsets to find (D-25).
  - Cables in the cassette gap clip only to the cassette (D-26).

## How to check this pack

```
python3 v2/00-Control/check_control_pack.py
```

It re-runs the acceptance checks:
- every file in `sources/v1`, `docs` and `v2` is in the register;
- every plan code and plan item is mapped, with its interfaces;
- every issue has an owner and a close condition;
- the conventions define the axes and the part numbers;
- every requirement has a status and a source;
- every decision has a date, a reason and what it affects.

## Who owns what

This folder belongs to the control pack; the decision log is the PM's. `v2-build-plan.pdf` is an input and is never edited. Other groups write in their own folders (the PLANNED rows in `document-register.csv`), and each adds file rows to the register when it releases files. `tools/fusion/` sits outside the register's scope (`sources/v1`, `docs`, `v2`).
