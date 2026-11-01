# Spaceship plan (FocusPod v2)

Status: approved by the product owner on 2026-10-31. Work has started. Decisions made since then are in `v2/00-Control/decision-log.md`, which wins wherever this plan disagrees. This plan was last brought up to the log on 2026-11-01, through D-126.

**Spaceship** is the working name for v2. The pod looks like a spaceship, and inside it should feel like one: you command your agents by voice. The prototype stays focused on the structure goals below, but the design reserves the hooks for that cockpit: mounting points, cable paths and power for a mic array, speakers, a screen and a status light. The cockpit kit can then bolt in later without a redesign.

Sources: the v2 build plan from the indoor pod lead engineer (`v2/00-Control/v2-build-plan.pdf`), the engineering guideline from the hardware engineering lead (`docs/engineering-guideline.md`), v1 (`sources/v1/` plus the [product page](https://www.autonomous.ai/focus-pod)), and the market study (`v2/research/market-study.md`).

## Goal

Get the v2 prototype design right. **The look stays exactly the same.** That means the team's iconic faceted front, the same size (2500 × 1700 × 2400 mm), the same proportions, colors and glass layout. Underneath, it is:

1. **Much lighter**, which saves on shipping and makes it easier to handle.
2. **Easy to assemble**: two people put it up in a few hours.
3. **Easy to ship**: it fits on standard 48 × 40 in LTL pallets. Long parts can go on standard long pallets, but never on odd sizes.

It's built from a complete, editable design package, so the prototype matches the drawings.

**Later, not in the v2 prototype:** US rules (electrical listing, fire ratings, sprinklers), US 120 V electrics, and updates to the product page. We don't design them out, though. The roof should be able to take a sprinkler head or open on alarm, and the threshold stays low, the door wide and the door pull light.

## 10x better than the big guys

We benchmark against the leaders: Framery, Room, Herman Miller, Steelcase (Orangebox), Haworth (hushoffice), Zenbooth and Silen. The numbers come from the big-brand scorecard in `v2/research/market-study.md`.

| What buyers feel | Best of the big guys today | Spaceship target | Better by |
|---|---|---|---|
| Installing it | Pro-install leaders: Room S/M take 12–20 person-hours, Framery uses trained crews quoting 4–6 hours, and Air3 needs certified installers. The best DIY is Room's 1-person booth at 2 person-hours and BuzziNest Pod at 4. | 2 people in about 1 hour with one hand tool (2 person-hours). Stretch: 1 person-hour. The guide counts about 126 minutes today (calculated, D-87). | 10x against the pro-install leaders at 1 hour, about 3–5x at today's 126 minutes; 2–4x against the best DIY at 1 hour |
| Getting it delivered and inside | Framery ships one crate of 310–430 kg that needs a pallet jack. Room's heaviest box is 73–81 kg. | Standard pallets to the door, then every piece carried by hand. Every part is 20 kg or less except the glass and fits an 81 cm door and a normal elevator. | 3–20x lighter pieces, and no pallet jack inside |
| Moving it inside the office | Room S/M need a pro teardown and rebuild, and Framery needs a kit and partial disassembly | Under study: castors, or a quick unbolt of the light panels | Up to 10x |
| Weight | The lightest are about 88–91 kg/m² of floor with no lab sound rating (Bay, Zenbooth Quad). Lab-rated Class A pods are 151–171 (Framery Four). | about 96 kg/m² (410.0 kg as shipped, calculated; cap 420, target 410), with every part 20 kg or less except the glass | As light as the lightest unrated pods, and well under lab-rated ones |
| Fresh air | Best is about 25 l/s per person. Nobody publishes CO2 readings or fan noise. | CO2 and heat drive the fans: about 33 l/s for one person, 53 l/s for two at 26 dB(A) or less, and a boost to 65 l/s at 30 dB(A) (calculated with D-130's sealed intake boot and gaskets: 25.0 and 29.5 dB(A), and 66.7 l/s at 30 dB(A), 0.5 under the limit until the fan sample measures it). The CO2 reading is shown inside. Fan noise is published. | Best in class, and first to publish CO2 and fan noise |
| Quiet | 30–30.3 dB speech reduction is the best lab result (hushFree XS, Framery) | About 19 dB calculated (range 14.6–21.7), and up to 24 dB if the felt does better on its air gap. That's quieter than v1 as built (about 15 dB). The wall sample, measured down to 100 Hz, settles it before a lab report. 30 dB would need about 520 kg. | Quieter than v1, at about half the weight per m² of lab-rated pods |
| Price | Zenbooth $5,245 per seat (2 seats). Big-brand pods run $13k–30k. | At or below v1's $9,900 for 2 people ($4,950 per seat) | Best per seat |

Ten times better is real on handling, lead time and moving the pod, and on installing once the trial reaches the 1 hour aim. It isn't physically possible on sound (10x quieter means +10 dB), on weight, or on price; the honest margin there is 1.2–3x. The product owner sets the price; the rest are design targets.

## Targets

Agents work to these from day one. The PM can change any of them, with the reason logged in the decision log (D-32).

| # | Goal | Target | How we prove it |
|---|---|---|---|
| 1 | Light | 300 kg stays the goal. The cap is 420 kg as shipped, and the target is 410 kg (decided, D-37, D-81). The layout study's live count is 410.0 kg as shipped: 10.0 kg under the cap and 0.0 kg under the target (calculated, with FRONT's decor blocks from CAD, PR #105; 407.6 kg before them). The voice kit's 4.0 kg reserve sits outside the cap, because the kit ships later (D-81). How it got there (calculated): 422.8 kg with D-81's savings, the clip-only lining fixing, the 24 kg/m³ fill and the 1.5 mm base band (PR #42); 412.2 kg with D-85's five savings, budgets for the light shelf and ledge, 1.0 mm inner studs in the wall panels (the ceiling's cross members stay 1.2 mm), 2 studs in the back panels, a hollow kick strip and poplar-core floor ply (PR #50); then D-86's glide load blocks, D-87's joined air pieces and ELECTRICAL's parts at 4.94 kg (PRs #61, #66, #68). Both glass panes stay 4+4 (D-82). v1 is about 480 kg by its BOM. Every part 20 kg or less, so one person can carry it, except the glass. No maker claims 20 kg parts. | Weights from the CAD and the master BOM, then the prototype on a scale |
| 2 | Easy to assemble | 2 people in about 1 hour with one hand tool as the aim, and never more than 4 hours. The guide's honest count is about 127 minutes (calculated, PR #59; D-87's target is about 126), with film peeling inside the clock, after D-87's factory pre-fitting: the exhaust fan box in the soffit, the riser on the supply fan box, preset glides with hook-in corner keys, bonded floor foam and a factory-tested harness (calculated). One bolt: an M6 × 16 socket head, captive, turned with one 5 mm key (decided, D-63). Panels find their place on spigots and meet at 2.26 mm metal-stop seams, and every bolt pattern between teams comes from one skeleton rule (decided, D-64, D-75). No glue or welding on site. Every part fits through a 914 × 2032 mm (36 × 80 in) doorway. | Step-by-step assembly sequence with fastener count, then a timed trial on the prototype |
| 3 | Easy to ship | Fits standard 48 × 40 in (1219 × 1016 mm) pallets, about 6 ft loaded height or less. Anything longer goes on a standard long pallet (such as 48 × 96 in), never a custom size. Nobody on the market ships pods on 48 × 40. | Pallet layout from the CAD |
| 4 | Fresh air | Users' top complaint about pods, so a full requirement: CO2 at or under 800 ppm with 2 people all day in a 600 ppm office. CO2 and heat drive the fans, keeping the inside within 4 K of the room and never going below 26 l/s with someone inside. One person runs at about 33 l/s. Two need 53 l/s at 26 dB(A) or less, and often the 65 l/s boost at 30 dB(A). The air runs inside the pod (decided, D-60 to D-62): room air comes in through a flush black mesh in the base band under the right decor block, rises to the supply fans high in that block, and runs down a felt-covered air column in the front-right corner; the exhaust leaves through a felt-covered soffit above the door and a roof slot behind the block. Four 12 V fans on two balanced signals start by themselves. Calculated with D-130's sealed intake boot and gaskets: 25.0 dB(A) at 53 l/s and 29.5 at 65 l/s, the boost reaching 66.7 l/s at 30 dB(A), 0.5 under the limit until the fan sample measures it (the Air Engineer, D-130; DR as built without them, 33.3 and 37.8; the air report's 25.1 and 29.6 came before DR's cavity, PR #199; D-121, D-124, ISS-090); before that correction PR #115 gave 28.5 dB(A) at the voice kit's 62 l/s. The lights are a low-heat light shelf (D-70). Two people put about 249 W into the air: 3.9 K over the room at 53 l/s (calculated, PR #72). The voice kit gets 40 W on average and 60 W at peak; with it fitted, the fans boost to hold 4 K at 30 dB(A) or less (decided, D-88). | Calculation, then a CO2 and noise check on the prototype |
| 5 | Quiet (guardrail) | At least as quiet as v1. The decided build calculates at about 19 dB (range 14.6–21.7, about 24 at best), against about 15 dB for v1 as built (calculated, D-53). The wall sample, measured down to 100 Hz, and then the lab test, with v1 and v2 in the same lab to ISO 23351-1, give the real figure; until then we quote only the calculation. | Calculation, then the lab test |
| 6 | Healthy materials | Low-emission certified felt, boards and glue | Supplier certificates |
| 7 | Done right | Built to the guideline: native Fusion CAD with editable sketches and parameters, drawings that go GA then assemblies then parts, one master BOM (`v2/04-BOM/`, checked on every run), joint and feature registers, and a status on every number | A Reviewer runs the guideline's checklist (§13) on every pull request |

## Where it stands (2026-10-31)

| | What |
|---|---|
| Done, on main | The control pack and decision log (D-01 to D-126); Milestone 1: bought parts, sound and air check, layout study (PRs #10, #11, #18, #20); skeleton P04 (PR #24), updated in place with the floor, threshold, glass edge and bolt rules (PR #58); the D-60 air path (PRs #26, #30); the wall and door sample package for the factory (PRs #21, #29, #34); the P04 weight roll-up (PR #38); the shared Fusion lock and the no-click drawing start (PRs #22, #33); the mechanical checks (PRs #25, #39, #40, #45, #49, #51, #53, #56, #71); the master BOM and its check (PRs #36, #44, #48, #54, #57); the release checklist and the draft FAI plan (PR #73); the joints register and bond spec, with FRONT's hardware and BASE's corner keys (PRs #23, #46, #47, #69); the live weight count and the D-85 savings, 410.0 kg as shipped (PRs #42, #50, #61, #63, #66, #68, #124, #126, #141, #154, #158, #161, #164, #180, #185, #188, #195, #199, #205, #105); the air report with ELECTRICAL's heat and D-88's voice kit (PRs #66, #68, #72); the packing plan on two pallets and the 2-person assembly guide, 127 min, every site fixing from the joints register (PRs #52, #59, #62, #65, #70) |
| In review | FRONT door unit and fixed glass (PRs #27, #28); CEILING sample (PR #32); WALL sample L1 (PR #41); BASE sample (PR #55); ELECTRICAL P01 (PR #64) |
| In progress | The CAD of every assembly, one team each (D-80): WALL, FRONT, BASE, CEILING (also AIR and INTERIOR), ELECTRICAL, and Packing and Assembly (pallets and the assembly guide) |
| Open checks | The factory's wall and door sample (sound down to 100 Hz, real cassette weights, the lighter fill), the fan sample, and the HOLDs: door hinges and catch, the glass product, the cassette clips, the felt certificate, the rivnut torque and the floor foam |

## What changes from the last attempt

The team already tried Fusion's Python API with an AI model, and the engineers weren't happy with the output. The guideline reads like a list of what went wrong:
- part sheets made before the assembly drawings
- imported solids with decorative sketches
- sizes taken from bounding boxes instead of hole centres
- hardware invented to fit
- one tolerance on everything
- hole positions with no reason behind them
- PASS with no evidence

Python wasn't the problem. Scripts written blind, in one shot and shipped without checks were. This time:

1. **Engineering first.** The pallet layout, real hardware part numbers and joint choices are settled before CAD (§4.3, §8).
2. **Real design intent.** Each part gets named parameters, fully constrained sketches, named features, and its own component. The edit test runs on every part family (§4.4).
3. **Small steps, checked.** Each feature is built, then measured (dimensions, clearances, mass) and screenshotted against the spec before the next one starts. No big blind scripts.
4. **Drawings dimensioned on purpose.** Each part gets a dimension plan first:
   - datums from how the part is held and fitted
   - tagged hole centres
   - tolerances set by function
   - the right sheet size

   Auto-dimension is only a draft (§6). Every sheet is rendered and looked at before review.
5. **Automatic checks on every revision.** Units, names, BOM against CAD by part number, every hole a true circle, every dimension on a centre, and the title block filled.
6. **A separate Reviewer.** A different agent from the one that built the work checks every sheet against the guideline's checklist (§13).
7. **Checked as it lands.** A Reviewer checks every pull request, the Mechanical Checker runs on every merge, and the factory's wall and door sample is the physical check (D-32).

All Engineers run Opus 5.5 at max effort on this Mac.

## Design for the pallet

Shipping sets the panel sizes. Decided (D-04): standard 48 × 40 in pallets plus one standard long pallet, with the decor blocks not split. Skeleton P04 gives the panels (D-66): side panels 1492.74 × 1142.74 mm, back panels 1200.61 × 1118.61 mm and ceiling halves 1200.61 × 1495 mm; the glass door, the fixed glass and the side decor blocks ride the long pallet. The pallet layout on P04 is still open (ISS-081), with the Packing and Assembly team (D-80).

## Same look, lighter bones

FocusPod lives indoors: in a cool, air-conditioned room, on a flat, level floor. There's no rain, sun, snow, wind or uneven ground, so the structure only has to handle indoor loads (people leaning on it, shipping, and being put together more than once). The weight comes out of what nobody sees:

| Where | Change | Rough saving |
|---|---|---|
| Floor | A thin floor inside the base band: 9 mm poplar-core plywood with a hard face veneer on a 3 mm firm closed-cell foam mat (D-86), instead of the raised 50×100 steel frame (decided, D-05, D-72, D-76). The base band stays as trim, so the look doesn't change. The step into the pod is a 13 mm threshold with a 1:2 bevel, which meets the US accessibility rule (D-72), and the room inside is about 8 cm taller than v1 (calculated). | about 50 kg (first estimate) |
| Wall, ceiling and decor frames | Aluminium instead of steel; the hidden tubes are 6063-T6, mill finish (decided, D-16, D-79) | about 40 kg (first estimate) |
| Skins | No plywood behind the ACP (decided, D-17). The sound mass sits in a floating lining cassette instead: a 0.5 mm steel tray with 9 mm felt on a 25 mm gap, hung on clips only (D-17, D-37, D-69, D-81). | up to 58 kg (first estimate) |
| Glass | 4+4 laminated glass of toughened, heat-soaked panes, frameless as in v1 (decided, D-27, D-46). Acrylic would have needed an opaque stile down the door, which breaks the look. Both panes stay 4+4: a 3+3 fixed pane would bend 58 mm when a person leans on it, over the 25 mm limit (D-82). | none: the look and the sound come first |
| Table | Removed. The floor stays empty, and the work wall gets a ledge (D-06, D-70). | about 20 kg (first estimate) |

Those were the first estimates. The sound package (felt cassettes, laminated glass, seals) puts weight back, so the decided build is 410.0 kg as shipped (Target 1; calculated, PR #105). The outside looks identical. The PM decides each change and logs it in the decision log (D-32).

## Quiet without the weight

The walls are both the heaviest part and what stops sound. Mass is the cheap way to block sound. The light way is two thin skins with sound-absorbing fill between them, kept from touching where possible.

The market says seals matter more than mass:
- Spacestor lifted a pod from 22.7 to 24–28 dB with cavity absorber, a base seal, door drop seals and gaskets on panel joints.
- Floorless pods post the weakest numbers.

So v2 adds:
- a gasket on every panel joint, running beside the bolts so none is cut (D-64)
- a drop seal on the door
- fill in the cavities
- the glass seated in sealed profiles
- a seal under the thin floor

The front is 4+4 laminated glass (D-27).

The sound check found the lightest wall that's still quieter than v1. The decided build calculates at about 19 dB (range 14.6–21.7), against about 15 dB for v1 as built (D-53). No weight goes back in until the factory's wall and door sample is measured down to 100 Hz.

## What we keep, add and leave out

**Kept from the v2 build plan:**
- The look: the faceted front, proportions, colors and glass layout, unchanged.
- The frame layout, in aluminium (D-16).
- 3 mm ACP outside and 9 mm PET felt inside, on lining cassettes held by mechanical clips only (D-47, D-81). No plywood backing (D-17).
- M6 bolts throughout: one M6 × 16 socket-head bolt and one 5 mm key (D-63).
- Small wall frames: 2 per side, 4 at the back and 2 in the ceiling, adjusted to fit the pallet.
- A 3-block decor frame.
- Fans, one path blowing in and one out. They now sit inside the pod, in an air column and a soffit, instead of the ceiling (D-60 to D-62).
- The plan's switches on the back wall, which is fine for the prototype.
- The modeling order: base, left wall, right wall, back wall, ceiling, decor frame, then the floor finish.

**Added because of what v1 taught us:**
- Seals and quiet vents. v1 had none, and they're light and do a lot for sound.
- One source of truth. v1's CAD, BOM and drawings disagree, and none of them can be edited.
- A thin floor instead of a raised one (decided, D-05, D-72). v1's welded 2500 × 1703 mm floor frame was its biggest, heaviest piece and put a 13 cm step at the door. A raised floor is for uneven ground and running cables underneath. Indoors, the floor is flat and the cable can run inside the back wall. The thin floor still closes the box for sound and keeps the walls square.
- The parts the build plan doesn't cover yet: glass door and fixed glass, hinges, handle, seals, lights, power inlet and wiring.

**Removed:** the table. The floor stays empty, and the work wall gets a 1000 mm ledge and a screen mount (D-06, D-70).

**Left out of v2:** the one-cable dock, room mic and agent status light I pitched earlier.

## How we build it

There are no gates. Work runs straight through, and phases overlap where they can.

- **The PM decides and logs.** There are no human hardware leads on the project (D-32). Choices the guideline reserves for a lead (the look, overall size, architecture, main materials, key joints) are ruled by the PM and logged with the reason; the look rule never moves.
- **Reviews run alongside the work.** A Reviewer checks every pull request, and the Mechanical Checker runs on every merge.
- **Agents never** order parts, contact suppliers or release anything for production.
- **Every pull request gets a Reviewer.**

### Phase 0: Fusion access (half a day, 1 Engineer on this Mac)

Fusion's built-in MCP server already works on this Mac. I ran a test script through it, and it's now registered with Claude Code and Codex. It only answers locally, so all Engineers run on this Mac (Mac 1, already in the Swarm).
- Prove the guideline's edit test (§4.4). Build one part from a fully constrained sketch with named parameters, save it as .f3d, export it to STEP, then change a parameter and confirm it rebuilds cleanly.
- Drawing proof, done (PR #6). By script, the drawing API places base views, dimensions and hole tables; it can't add projected or section views or fill the title block, so those go on a short list for a person or the shared tools. A no-click drawing start merged in PR #33. Every sheet is exported, rendered and checked by eye.

### Milestone 1: decide the layout (done: PRs #8, #10, #11, #18, #19)

1. **Weight, pallet and assembly study.** This is the heart of v2.
   - A weight budget by assembly, comparing v1 with v2 as planned.
   - Panel split options that fit standard pallets, including wall bands about 1.2 m long that stand on 48 × 40 pallets. Orangebox Air3 stacks 5 bands per wall.
   - A pallet layout for each option.
   - Part weights, with every part at 20 kg or less, plus the lighter indoor options against the 300 kg target: aluminum frames, no plywood backing, sandwich walls, and 8 mm glass, 4+4 laminated glass or smoked acrylic for the front.
   - Floor options compared on weight, step height, sound, stiffness and assembly time: the plan's raised floor, a thin floor, and no floor.
   - A 2-person assembly sequence with step count, fastener count and estimated time.
   - A recommendation for the layout the CAD should follow.
2. **Control pack.** Covers:
   - Requirements and targets, each with a status.
   - The assembly tree: POD splits into BASE, WALL, FRONT, CEILING, LINING, AIR, ELECTRICAL and INTERIOR, with PACKAGING as the delivery setup.
   - Interfaces between the assemblies.
   - A file register and an issue register.
   - Conventions: units, axes, naming, part numbers, file names and revisions.
   - A proposed answer to each open question: door and glass, lights (including a soft front light for video calls), door hand, and the thin floor's build.
3. **Bought parts, hardware, and a sound and air check.**
   - Real part numbers and fit data for every bought item, lightest options first.
   - The parts the plan doesn't cover yet: glass door hinges, handle, seals, glass clamps, latch, lights and power inlet.
   - Fasteners for the 20×20 tube.
   - A sound check: the lightest wall that's at least as quiet as v1, comparing two skins with fill against sandwich panels; seals and gaskets; 8 mm tempered glass, 4+4 laminated glass and smoked acrylic for the door and fixed panel; and what 30 dB would cost in kg.
   - An air design that meets the fresh-air requirement: airflow with a 2-person load, self-starting fans with boost, silenced vents, and noise inside.
   - Low-emission certified options for the felt, boards and glue.

### Milestone 2: sample set (about 2 days, 2 to 3 Engineers, starting once Phase 0 passes)

The skeleton starts from the plan's fixed dimensions while Milestone 1 finishes, then takes the chosen panel layout.
- A native Fusion skeleton of the whole pod, driven by named parameters: overall size, wall depth 1495, decor depth 205 (both measured from v1), tube sizes and panel splits. It's built in the plan's order, as components, not bodies.
- Sample drawings:
  - GA with sections.
  - The floor (BASE) assembly and 2 of its parts.
  - One wall assembly and its panel.
  - One decor detail.
- Sample registers:
  - Joints: wall to wall, wall to floor and the decor bracket.
  - One bond spec (ACP to aluminium, PR #23).
  - Feature rationale for the sample parts.
  - A master BOM generated from the CAD, with weights.

### Milestone 3: full set (about 1 week, 4 to 5 Engineers, starting right after the sample set)

- Every part and drawing.
- DXF flat patterns for the ACP and sheet metal, and tube cut lists.
- The master BOM.
- A 2-person assembly guide with pictures.
- The pallet and packing plan, and an FAI plan.

The Engineers split by assembly so they never share files, one team each (D-80): WALL (with its linings); FRONT; BASE; CEILING, which also builds AIR and INTERIOR; ELECTRICAL; and Packing and Assembly (the pallets and the assembly guide).

There is only one Fusion, and the MCP works on whichever document is active. So the Engineers write and review their CAD scripts in parallel, and Fusion runs them one at a time.

It ends with the hand-off: a package ready for prototype. Every scope is marked as one of: done, waiting on a supplier, or needs a test sample.

### Phase 4: prototype (the team in Vietnam)

The team builds one pod from the package. We fold what they find back into the CAD, drawings and BOM. The prototype gets weighed, packed onto pallets and timed while two people assemble it.

## Timeline

About 1.5 weeks to a prototype-ready package, with no waiting on reviews. The critical path is Phase 0, then Milestone 2, then Milestone 3; Milestone 1 runs alongside. The prototype's timing depends on the team.

## Risks

1. **Drawings.** The API places base views and dimensions, and the shared drawing start now works (PR #33), but readable dimension placement is where the last attempt fell short. Each part gets a dimension plan, and every rendered sheet gets checked by eye.
2. **Claude allowance.** This Mac's weekly Claude allowance is 70% used until Nov 3, and Opus at max effort uses it fast. If it runs low, the non-Fusion Engineers can move to another Swarm machine with a Claude account, if the product owner agrees.
3. **Light vs quiet.** At 300 kg the walls lose most of their mass. The two-skin wall with fill is the light answer, and light fixes come first. Any heavy fix goes to the product owner with its cost in kg.
4. **Late feedback.** With no gates, a late "no" can mean rework. Parametric CAD and small review packets after each milestone keep that cheap.
5. **One Fusion.** A single Fusion on this Mac is the bottleneck for CAD and drawings. Fusion runs scripts one at a time from a queue. If that's too slow, we add a second Fusion seat on another machine.

## Decisions for the product owner

The plan was approved on 2026-10-31. Since then the PM makes the design decisions and logs them (D-32); only spending, credentials and releases go to the product owner.

Rulings that need no answer: documents are in English with the team's Vietnamese part names alongside, and v2 files follow the guideline's folder layout (§12) under `v2/`.
