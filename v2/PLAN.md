# FocusPod v2 plan

Status: draft for Dee's approval. Nothing has started.

Sources: the v2 build plan from the indoor pod lead engineer (`v2/00-Control/v2-build-plan.pdf`), the engineering guideline from the hardware engineering lead (`docs/engineering-guideline.md`), and v1 (`sources/v1/` plus the [product page](https://www.autonomous.ai/focus-pod)).

## Goal

Get the v2 prototype design right. It keeps the same size (2500 × 1700 × 2400 mm) and the same faceted yellow front, but it is:

1. **Lighter**, which saves on shipping and makes it easier to handle.
2. **Easy to assemble**: two people put it up in a few hours.
3. **Easy to ship**: it fits on standard LTL pallets. An oversize pallet is OK if needed, but standard is preferred.

It's built from a complete, editable design package, so the prototype matches the drawings.

**Later, not in the v2 prototype:** US rules (electrical listing, fire ratings, sprinklers), US 120 V electrics, and updates to the product page.

## Targets

Agents work to these from day one. The hardware engineering lead and the indoor pod lead can change any of them at any time, and we fold their changes in.

| # | Goal | Target | How we prove it |
|---|---|---|---|
| 1 | Light | 450 kg or less, and as light as we can make it (v1 comes to about 550 kg from its BOM). Every part one person can carry (25 kg or less), except the glass. | Weights from the CAD and BOM, then the prototype on a scale |
| 2 | Easy to assemble | 2 people in 4 hours or less, hand tools only, one bolt size (M6), no glue or welding on site. Every part fits through a 914 × 2032 mm (36 × 80 in) doorway. | Step-by-step assembly sequence with fastener count, then a timed trial on the prototype |
| 3 | Easy to ship | Fits standard 48 × 40 in (1219 × 1016 mm) pallets, about 6 ft loaded height or less. One oversize pallet only if needed, likely for the 2 m glass door. | Pallet layout from the CAD |
| 4 | Guardrails: quiet and fresh air | At least as quiet as v1, with 30 dB as the aim. CO2 at or under 1,000 ppm with 2 people inside (about 62 m³/h). Fan noise inside at or under 30 dB(A). | Calculation, then a check on the prototype |
| 5 | Done right | Built to the guideline: native Fusion CAD with editable sketches and parameters, drawings that go GA then assemblies then parts, one master BOM, joint and feature registers, and a status on every number | A Reviewer runs the guideline's checklist (§13) on every pull request |

## Design for the pallet

Shipping sets the panel sizes, so we decide the split before the CAD. A panel ships best standing upright on a standard 48 × 40 in pallet, which allows up to about 1200 mm wide and 1700 mm tall. Here's how the build plan's parts measure up:

- **They fit:** the side wall frames (about 1500 × 1150 mm), the back wall frames (about 1200 × 1150 mm if split 2 × 2) and the floor boards (about 1185 × 1430 mm).
- **Just over:** the ceiling halves are about 1240 mm wide, roughly 20 mm too wide.
- **Too long:** the glass door (2011 mm), the fixed glass (2139 mm), the side decor blocks (2300 mm) and the floor rails (2500 mm).

The likely answer is one standard pallet for the panels plus one long pallet for the glass and long pieces. The other option is to split the decor blocks and floor rails so only the glass rides oversize. Milestone 1 picks whichever layout is lightest, cheapest to ship and quickest to assemble, and the CAD follows it.

## Quiet without the weight

Mass stops sound, and the plan's wall has about half of v1's sound-blocking mass: about 7.6 kg/m² against 14.4. We won't add heavy layers silently. Milestone 1 lists the light fixes first: seals, quiet vents and where the felt goes. It also shows what reaching 30 dB would cost in kg. If it costs real weight, Dee gets the trade-off before we add it.

## What we keep, add and leave out

**Kept from the v2 build plan:**
- Steel frames: 50×100 and 30×60 tube for the floor, 20×20 tube for the walls, ceiling and decor.
- 3 mm ACP glued to 6 mm plywood, and 9 mm PET felt fixed with Velcro.
- M6 bolts throughout.
- Small wall frames: 2 per side, 4 at the back and 2 in the ceiling, adjusted to fit the pallet.
- A 3-block decor frame.
- Ceiling fans, one blowing in and one out.
- The plan's switches on the back wall, which is fine for the prototype.
- The modeling order: floor frame, left wall, right wall, back wall, ceiling, decor frame, floor.

**Added because of what v1 taught us:**
- Seals and quiet vents. v1 had none, and they're light and do a lot for sound.
- One source of truth. v1's CAD, BOM and drawings disagree, and none of them can be edited.
- A bolt-together floor frame. v1's welded 2500 × 1703 mm frame was its biggest, heaviest piece.
- The parts the build plan doesn't cover yet: glass door and fixed glass, hinges, handle, seals, lights, power inlet and wiring, and the table.

**Left out of v2:** the one-cable dock, room mic and agent status light I pitched earlier.

## How we build it

There are no gates. Work runs straight through, and phases overlap where they can.

- **Reviews run alongside the work.** The hardware engineering lead and the indoor pod lead get a short review packet after each milestone. Their notes go into the next pass, and nothing waits on them.
- **Choices the guideline reserves for the hardware engineering lead go ahead anyway.** That means changes to the look, overall size, architecture, main materials or key joints. Each one is marked PROPOSED until he signs off.
- **Agents never** order parts, contact suppliers or release anything for production.
- **Every pull request gets a Reviewer.**

### Phase 0: Fusion access (half a day, 1 Engineer on this Mac)

Fusion's built-in MCP server already works on this Mac. I ran a test script through it, and it's now registered with Claude Code and Codex. It only answers locally, so all Engineers run on this Mac, which needs to join the Swarm.
- Prove the guideline's edit test (§4.4). Build one part from a fully constrained sketch with named parameters, save it as .f3d, export it to STEP, then change a parameter and confirm it rebuilds cleanly.
- Drawing spike: produce one ISO drawing sheet. Fusion's API has little drawing support, so we also try computer use and a scripted fallback, which the guideline allows if it is accurate and updatable (§6.1).

### Milestone 1: decide the layout (about 1 day, 3 Engineers, starting alongside Phase 0)

1. **Weight, pallet and assembly study.** This is the heart of v2.
   - A weight budget by assembly, comparing v1 with v2 as planned.
   - Panel split options that fit standard pallets.
   - A pallet layout for each option.
   - Part weights, with every part at 25 kg or less.
   - A 2-person assembly sequence with step count, fastener count and estimated time.
   - A recommendation for the layout the CAD should follow.
2. **Control pack.** Covers:
   - Requirements and targets, each with a status.
   - The assembly tree: POD splits into BASE, WALL, FRONT, CEILING, LINING, AIR, ELECTRICAL and INTERIOR, with PACKAGING as the delivery setup.
   - Interfaces between the assemblies.
   - A file register and an issue register.
   - Conventions: units, axes, naming, part numbers, file names and revisions.
   - A proposed answer to each open question: door and glass, lights, table, door hand and floor board thickness.
3. **Bought parts, hardware, and a sound and air check.**
   - Real part numbers and fit data for every bought item, lightest options first.
   - The parts the plan doesn't cover yet: glass door hinges, handle, seals, glass clamps, latch, lights and power inlet.
   - Fasteners for the 20×20 tube.
   - A quick sound and air check: the light fixes, and what 30 dB would cost in kg.

### Milestone 2: sample set (about 2 days, 2 to 3 Engineers, starting once Phase 0 passes)

The skeleton starts from the plan's fixed dimensions while Milestone 1 finishes, then takes the chosen panel layout.
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
  - A master BOM generated from the CAD, with weights.

### Milestone 3: full set (about 1 week, 4 to 5 Engineers, starting right after the sample set)

- Every part and drawing.
- DXF flat patterns for the ACP and sheet metal, and tube cut lists.
- The master BOM.
- A 2-person assembly guide with pictures.
- The pallet and packing plan, and an FAI plan.

The Engineers split by assembly so they never share files: BASE and WALL; FRONT (door and glass); CEILING, AIR and ELECTRICAL; LINING and INTERIOR; PACKAGING and the assembly guide.

There is only one Fusion, and the MCP works on whichever document is active. So the Engineers write and review their CAD scripts in parallel, and Fusion runs them one at a time.

It ends with the hand-off: a package ready for prototype. Every scope is marked as one of: done, waiting on a supplier, or needs a test sample.

### Phase 4: prototype (the team in Vietnam)

The team builds one pod from the package. We fold what they find back into the CAD, drawings and BOM. The prototype gets weighed, packed onto pallets and timed while two people assemble it.

## Timeline

About 1.5 weeks to a prototype-ready package, with no waiting on reviews. The critical path is Phase 0, then Milestone 2, then Milestone 3; Milestone 1 runs alongside. The prototype's timing depends on the team.

## Risks

1. **Drawings.** Fusion's API can barely make drawings. The Phase 0 spike tests this first. The fallback is computer use or scripted drawings.
2. **Light vs quiet.** Light fixes come first, and any heavy fix goes to Dee with its cost in kg.
3. **Late feedback.** With no gates, a late "no" can mean rework. Parametric CAD and small review packets after each milestone keep that cheap.
4. **One Fusion.** A single Fusion on this Mac is the bottleneck for CAD and drawings. Fusion runs scripts one at a time from a queue. If that's too slow, we add a second Fusion seat on another machine.

## Decisions for Dee

1. Approve the goals and this plan.
2. Add this Mac to the Swarm. Fusion's MCP is already registered for Claude Code and Codex.

Rulings that need no answer: documents are in English with the team's Vietnamese part names alongside, and v2 files follow the guideline's folder layout (§12) under `v2/`.
