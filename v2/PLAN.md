# FocusPod v2 plan

Status: draft for Dee's approval. Nothing has started.

Sources: the v2 build plan from the indoor pod lead engineer (`v2/00-Control/v2-build-plan.pdf`), the engineering guideline from the hardware engineering lead (`docs/engineering-guideline.md`), and v1 (`sources/v1/` plus the [product page](https://www.autonomous.ai/focus-pod)).

## Goal

v2 is the same FocusPod, with the same 2500 × 1700 × 2400 mm size and the same faceted yellow front. It is lighter, two people can put it up in hours, it ships in small flat boxes, and it actually delivers the quiet and fresh air we advertise.

We deliver it as a complete, editable, traceable design package that the factory can build without guessing.

## Targets

These are proposals. They become requirements once the hardware engineering lead and the indoor pod lead confirm them at Gate A.

| # | Goal | Proposed target | How we prove it |
|---|---|---|---|
| 1 | Quiet | Speech level reduction of at least 30 dB, measured to ISO 23351-1. This is the number on the v1 page. | Calculation in Milestones 1 and 2, then a test on the prototype |
| 2 | Light | 450 kg or less (v1 comes to about 550 kg from its BOM). No single part over 40 kg except the glass. Final number set at Gate A. | Weights from the CAD and BOM, then the prototype on a scale |
| 3 | Easy to assemble | 2 people in 4 hours or less, hand tools only, one bolt size (M6), no glue or welding on site. Every part fits through a 914 × 2032 mm (36 × 80 in) doorway. | Timed assembly trial on the prototype |
| 4 | Easy to ship | Flat-packed. Crate count and pods per 40 ft container are computed and kept as low as possible; the target is set at Gate A. | Packing plan from the CAD |
| 5 | Fresh, quiet air | CO2 at or under 1,000 ppm with 2 people inside (about 62 m³/h of airflow). Fan noise inside at or under 30 dB(A). Vents that don't let speech out. | Calculation, then a measurement on the prototype |
| 6 | Sellable in the US | 120 V / 60 Hz, UL-listed electrical parts, finishes rated ASTM E84 Class A, and sprinkler rules (NFPA 13) checked | Parts list with certificates, plus a code check |
| 7 | Built to the guideline | Native Fusion CAD with editable sketches and parameters. Drawings go GA, then assemblies, then parts (ISO, first-angle). One master BOM, joint and feature registers, and a status on every number. | A Reviewer runs the guideline's checklist (§13) at each gate |

## What we keep, add and leave out

**Kept from the v2 build plan:**
- Steel frames: 50×100 and 30×60 tube for the floor, 20×20 tube for the walls, ceiling and decor.
- 3 mm ACP glued to 6 mm plywood, and 9 mm PET felt fixed with Velcro.
- M6 bolts throughout.
- Small wall frames: 2 per side, 4 at the back and 2 in the ceiling.
- A 3-block decor frame.
- Ceiling fans, one blowing in and one out.
- Switches on the back wall.
- The modeling order: floor frame, left wall, right wall, back wall, ceiling, decor frame, floor.

**Added because of what v1 taught us:**
- A real sound package. v1 had no felt, no wall fill, no seals and no vent silencers, and v2 needs all four.
- One source of truth. v1's CAD, BOM and drawings disagree, and none of them can be edited.
- Electrics that match the page: 2 outlets, USB-C 100 W and Ethernet, or the page changes. v1 had 1 outlet.
- A bolt-together floor frame. v1's welded 2500 × 1703 mm frame was its biggest, heaviest piece.
- The parts the build plan doesn't cover yet: glass door and fixed glass, hinges, handle, seals, lights, power inlet and wiring, and the table.

**Left out of v2:** the one-cable dock, room mic and agent status light I pitched earlier. They're candidates for later.

## The hard trade-off: light vs quiet

Mass stops sound. The plan's wall puts about 7.6 kg/m² in the sound path (3 mm ACP and 6 mm plywood; the PET felt absorbs sound but barely blocks it). v1 had about 14.4 kg/m² in two layers. With half the mass, v2 could land 6 to 10 dB worse than v1 and miss 30 dB.

The rough weights point the same way. v2 as planned comes to about 460 kg, about 100 kg of it glass. v1 comes to about 550 kg from its BOM, although the page says 431 kg. Adding a heavy layer to reach 30 dB could wipe out the weight saving.

Milestone 1 replaces these rough numbers with calculations. It also gives a short list of fixes (a mass layer, an inner board with fill, seals, vent silencers) with the dB each one gains and the kg each one costs. Gate A picks. My leaning is that quiet wins, because it's the product's promise, and then we cut weight where it doesn't carry sound: the frames, the decor and the floor.

## How we build it

We follow the guideline's milestones, with a gate after each one. Agents never order parts, contact suppliers or release anything for production. Every pull request gets a Reviewer.

### Phase 0: Fusion access (half a day, 1 Engineer on this Mac)

Fusion's built-in MCP server already works on this Mac. I ran a test script through it, and it's now registered with Claude Code and Codex. It only answers locally, so all Engineers run on this Mac, which needs to join the Swarm.
- Prove the guideline's edit test (§4.4). Build one part from a fully constrained sketch with named parameters, save it as .f3d, export it to STEP, then change a parameter and confirm it rebuilds cleanly.
- Drawing spike: produce one ISO drawing sheet. Fusion's API has little drawing support, so we also try computer use and a scripted fallback, which the guideline allows if it is accurate and updatable (§6.1).

### Phase 1, Milestone 1: requirements and issues (about 1 day, 3 Engineers in parallel)

1. **Control pack.** Covers:
   - Requirements and targets, each with a status.
   - The assembly tree: POD splits into BASE, WALL, FRONT, CEILING, LINING, AIR, ELECTRICAL and INTERIOR, with PACKAGING as the delivery setup.
   - Interfaces between the assemblies.
   - A file register and an issue register.
   - Conventions: units, axes, naming, part numbers, file names and revisions.
2. **Bought parts and hardware.** Real part numbers and fit data for every bought item in the plan. Also the parts the plan doesn't cover yet: glass door hinges, handle, seals, glass clamps, latch, lights and power inlet. Plus US 120 V, UL-listed options for the plan's Vietnamese 220 V switches and fan.
3. **Sound, air and weight.**
   - Sound estimates for the walls, door and vents.
   - Options to reach 30 dB, each with its weight.
   - Airflow, CO2 and fan noise.
   - Vent silencer size.
   - The weight of v1 and v2, assembly by assembly.

**Gate A:** the hardware engineering lead and the indoor pod lead approve the targets, conventions and change proposals. They also settle the open questions: door and glass, lights, table, door hand and floor board thickness.

### Phase 2, Milestone 2: sample set (about 2 days, 2 to 3 Engineers)

- A native Fusion skeleton of the whole pod, driven by named parameters: overall size, wall depth 1500, decor depth 200, tube sizes and panel splits. It's built in the plan's order, as components, not bodies.
- Sample drawings:
  - GA with sections.
  - The floor frame (BASE) assembly and 2 of its parts.
  - One wall assembly and its panel.
  - One decor detail.
- Sample registers:
  - Joints: wall to wall, wall to floor and the decor bracket.
  - One bond spec (ACP to plywood).
  - Feature rationale for the sample parts.
  - A master BOM generated from the CAD.

**Gate B:** the hardware engineering lead reviews the sample before we scale it.

### Phase 3, Milestone 3: full set (about 1 week, 4 to 5 Engineers)

- Every part and drawing.
- DXF flat patterns for the ACP and sheet metal, and tube cut lists.
- The master BOM.
- A 2-person assembly guide with pictures.
- A packing plan and an FAI plan.

The Engineers split by assembly so they never share files: BASE and WALL; FRONT (door and glass); CEILING, AIR and ELECTRICAL; LINING and INTERIOR; PACKAGING and the assembly guide.

There is only one Fusion, and the MCP works on whichever document is active. So the Engineers write and review their CAD scripts in parallel, and Fusion runs them one at a time.

**Gate C:** ready for prototype. Every scope is marked as one of: done, waiting on a supplier, or needs a test sample.

### Phase 4: prototype (the team in Vietnam)

The team builds one pod from the package, and we fold what they find back into the CAD, drawings and BOM. Sound, airflow and timed assembly tests back the page's claims. Only the hardware engineering lead releases v2 for production.

## Timeline

About 2 weeks to a prototype-ready package. That assumes the drawing spike works and each gate gets a review within a day. The prototype's timing depends on the team.

## Risks

1. **Drawings.** Fusion's API can barely make drawings. The Phase 0 spike tests this first. The fallback is computer use or scripted drawings.
2. **Light vs quiet.** This may force more mass or a looser weight target. We'll have numbers in Milestone 1 and a decision at Gate A.
3. **Review speed.** Every gate waits on two engineers. We'll keep review packets small, and it's best if they join this project.
4. **US rules.** UL, ASTM E84 or sprinkler rules could change materials or electrics. We check them in Milestone 1.
5. **One Fusion.** A single Fusion on this Mac is the bottleneck for CAD and drawings. Fusion runs scripts one at a time from a queue. If that's too slow, we add a second Fusion seat on another machine.

## Decisions for Dee

1. Approve the goals and this plan.
2. Can the hardware engineering lead and the indoor pod lead join this project to approve gates directly? Otherwise, reviews go through you.
3. Add this Mac to the Swarm. Fusion's MCP is already registered for Claude Code and Codex.
4. Include US compliance (UL, ASTM E84, NFPA 13) in v2? I recommend yes.

Rulings that need no answer: documents are in English with the team's Vietnamese part names alongside, and v2 files follow the guideline's folder layout (§12) under `v2/`.
