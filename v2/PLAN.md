# Spaceship plan (FocusPod v2)

Status: approved by Dee on 2026-10-31. Work has started. Decisions made since then are in `v2/00-Control/decision-log.md`, which wins wherever this plan disagrees.

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
| Installing it | Pro-install leaders: Room S/M take 12–20 person-hours, Framery uses trained crews quoting 4–6 hours, and Air3 needs certified installers. The best DIY is Room's 1-person booth at 2 person-hours and BuzziNest Pod at 4. | 2 people in about 1 hour with one hand tool (2 person-hours). Stretch: 1 person-hour. | 10x against the pro-install leaders, 2–4x against the best DIY |
| Getting it delivered and inside | Framery ships one crate of 310–430 kg that needs a pallet jack. Room's heaviest box is 73–81 kg. | Standard pallets to the door, then every piece carried by hand. Every part is 20 kg or less except the glass and fits an 81 cm door and a normal elevator. | 3–20x lighter pieces, and no pallet jack inside |
| Moving it inside the office | Room S/M need a pro teardown and rebuild, and Framery needs a kit and partial disassembly | Under study: castors, or a quick unbolt of the light panels | Up to 10x |
| Weight | The lightest are about 88–91 kg/m² of floor with no lab sound rating (Bay, Zenbooth Quad). Lab-rated Class A pods are 151–171 (Framery Four). | about 90 kg/m² (385 kg), with every part 20 kg or less | As light as the lightest unrated pods, and about half the weight of lab-rated ones |
| Fresh air | Best is about 25 l/s per person. Nobody publishes CO2 readings or fan noise. | About 35 l/s per person (70 l/s for 2), with a CO2 sensor that drives the fans and shows the reading. Fan noise at or under 25 dB(A) at full flow, published. | Best in class, and first to publish CO2 and fan noise |
| Quiet | 30–30.3 dB speech reduction is the best lab result (hushFree XS, Framery) | About 24 dB (calculated range 22–27), roughly 9 dB quieter than v1 as built (about 15 dB), with a published lab report. Decided (D-02): 30 dB would need about 520 kg. | Clearly quieter than v1 at under half the weight per m² of lab-rated pods |
| Price | Zenbooth $5,245 per seat (2 seats). Big-brand pods run $13k–30k. | At or below v1's $9,900 for 2 people ($4,950 per seat) | Best per seat |

Ten times better is real on installing, handling, lead time and moving the pod. It isn't physically possible on sound (10x quieter means +10 dB), on weight, or on price; the honest margin there is 1.2–3x. Dee sets the price; the rest are design targets.

## Targets

Agents work to these from day one. The hardware engineering lead and the indoor pod lead can change any of them at any time, and we fold their changes in.

| # | Goal | Target | How we prove it |
|---|---|---|---|
| 1 | Light | About 385 kg (cap 400 kg) for the quiet build. v1 is about 480 kg by its BOM. 300 kg is the light build without the sound package, and the kg-vs-dB curve set the trade (decision D-02). Every part 20 kg or less, so one person can carry it, except the glass. No maker claims 20 kg parts. | Weights from the CAD and BOM, then the prototype on a scale |
| 2 | Easy to assemble | 2 people in about 1 hour with one hand tool, and never more than 4 hours. One bolt size (M6), joints that find their own place, no glue or welding on site. Every part fits through a 914 × 2032 mm (36 × 80 in) doorway. | Step-by-step assembly sequence with fastener count, then a timed trial on the prototype |
| 3 | Easy to ship | Fits standard 48 × 40 in (1219 × 1016 mm) pallets, about 6 ft loaded height or less. Anything longer goes on a standard long pallet (such as 48 × 96 in), never a custom size. Nobody on the market ships pods on 48 × 40. | Pallet layout from the CAD |
| 4 | Fresh air | Users' top complaint about pods, so a full requirement: CO2 at or under 800 ppm with 2 people all day, which needs at least 26 l/s; we aim for about 70 l/s, a full air change every 2 minutes, which keeps CO2 near 550 ppm. A CO2 sensor drives the fans, and the reading is shown inside. The fans start by themselves, have boost, and are wired in so nobody unplugs them. Fan noise inside is at or under 25 dB(A) at full flow through silenced vents, and we publish it. Lights stay low-heat. | Calculation, then a CO2 and noise check on the prototype |
| 5 | Quiet (guardrail) | At least as quiet as v1, with 30 dB as the aim. v1 and v2 get tested in the same lab to ISO 23351-1. | Calculation, then the lab test |
| 6 | Healthy materials | Low-emission certified felt, boards and glue | Supplier certificates |
| 7 | Done right | Built to the guideline: native Fusion CAD with editable sketches and parameters, drawings that go GA then assemblies then parts, one master BOM, joint and feature registers, and a status on every number | A Reviewer runs the guideline's checklist (§13) on every pull request |

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
7. **Engineers see it early.** One part and its drawing go to the hardware leads on day 2. We tune the template to their taste while the rest keeps going.

All Engineers run Opus 5.5 at max effort on this Mac.

## Design for the pallet

Shipping sets the panel sizes, so we decide the split before the CAD. A panel ships best standing upright on a standard 48 × 40 in pallet, which allows up to about 1200 mm wide and 1700 mm tall. Here's how the build plan's parts measure up:

- **They fit:** the side wall frames (about 1500 × 1150 mm), the back wall frames (about 1200 × 1150 mm if split 2 × 2) and the floor boards (about 1185 × 1430 mm).
- **Just over:** the ceiling halves are about 1240 mm wide, roughly 20 mm too wide.
- **Too long:** the glass door (2011 mm), the fixed glass (2139 mm), the side decor blocks (2300 mm) and the plan's floor rails (2500 mm). A thin floor removes the floor rails entirely.

The likely answer is one 48 × 40 pallet for the panels, plus one standard long pallet for the glass and long pieces. The other option is to split the decor blocks so only the glass needs the long pallet. No custom pallet sizes either way. Milestone 1 picks whichever layout is lightest, cheapest to ship and quickest to assemble, and the CAD follows it.

## Same look, lighter bones

FocusPod lives indoors: in a cool, air-conditioned room, on a flat, level floor. There's no rain, sun, snow, wind or uneven ground, so the structure only has to handle indoor loads (people leaning on it, shipping, and being put together more than once). The weight comes out of what nobody sees:

| Where | Change | Rough saving |
|---|---|---|
| Floor | A thin floor: 2 to 3 cm panels lying on the room floor, with the walls fixed around them, instead of the raised 50×100 steel frame. The outside base band stays as trim, so the look doesn't change. The step into the pod drops from about 13 cm to about 2 cm, and the room inside gets about 10 cm taller. | about 50 kg |
| Wall, ceiling and decor frames | Aluminum instead of steel | about 40 kg |
| Skins | No plywood behind the ACP where sound doesn't need it. Also study sandwich walls: a foam-core or honeycomb panel with the same yellow ACP face on an aluminum frame. That's how the lightest pods are built (Mamava XL at 318 kg, hushMeet's honeycomb). | up to 58 kg |
| Glass | 8 mm instead of 10 mm saves about 20 kg. Smoked acrylic, which Room uses for its booth door to cut shipping weight, saves about 60 kg on the door and fixed panel together. Same smoked look and same shape either way. Acrylic scratches more and feels less premium, so the sound check and a sample decide. | about 20–60 kg |
| Table | Removed. Customers put whatever they like in the pod. | about 20 kg |

That takes v2 from about 460 kg as planned to a little under 300 kg. The outside looks identical. These are material changes to the build plan, so they go in marked PROPOSED for the hardware engineering lead while we keep building.

## Quiet without the weight

The walls are both the heaviest part and what stops sound. Mass is the cheap way to block sound. The light way is two thin skins with sound-absorbing fill between them, kept from touching where possible.

The market says seals matter more than mass:
- Spacestor lifted a pod from 22.7 to 24–28 dB with cavity absorber, a base seal, door drop seals and gaskets on panel joints.
- Floorless pods post the weakest numbers.

So v2 adds:
- a gasket on every panel joint
- a drop seal on the door
- fill in the cavities
- the glass seated in sealed profiles
- a seal under the thin floor

We also compare three front options: 8 mm tempered glass; 4+4 laminated acoustic glass, which weighs about the same and is quieter; and smoked acrylic, less than half the weight. Room still claims about 30 dB with an acrylic door.

The sound check designs the lightest wall that's still at least as quiet as v1, then shows what each extra dB toward 30 dB costs in kg. If the light wall can't match v1, Dee gets the trade-off before we add weight. Because 300 kg is beyond anything rated on the market, the team should build one wall sample and the door early and test them.

## What we keep, add and leave out

**Kept from the v2 build plan:**
- The look: the faceted front, proportions, colors and glass layout, unchanged.
- The frame layout. The material may go from steel to aluminum (see above).
- 3 mm ACP outside and 9 mm PET felt inside on Velcro. The plywood backing stays only where sound needs it.
- M6 bolts throughout.
- Small wall frames: 2 per side, 4 at the back and 2 in the ceiling, adjusted to fit the pallet.
- A 3-block decor frame.
- Ceiling fans, one blowing in and one out.
- The plan's switches on the back wall, which is fine for the prototype.
- The modeling order: base, left wall, right wall, back wall, ceiling, decor frame, then the floor finish.

**Added because of what v1 taught us:**
- Seals and quiet vents. v1 had none, and they're light and do a lot for sound.
- One source of truth. v1's CAD, BOM and drawings disagree, and none of them can be edited.
- A thin floor instead of a raised one, marked PROPOSED. v1's welded 2500 × 1703 mm floor frame was its biggest, heaviest piece and put a 13 cm step at the door. A raised floor is for uneven ground and running cables underneath. Indoors, the floor is flat and the cable can run inside the back wall. The thin floor still closes the box for sound and keeps the walls square.
- The parts the build plan doesn't cover yet: glass door and fixed glass, hinges, handle, seals, lights, power inlet and wiring.

**Removed:** the table. The pod ships empty, and customers furnish it however they like.

**Left out of v2:** the one-cable dock, room mic and agent status light I pitched earlier.

## How we build it

There are no gates. Work runs straight through, and phases overlap where they can.

- **Reviews run alongside the work.** The hardware engineering lead and the indoor pod lead get a short review packet after each milestone. Their notes go into the next pass, and nothing waits on them.
- **Choices the guideline reserves for the hardware engineering lead go ahead anyway.** That means changes to the look, overall size, architecture, main materials or key joints. Each one is marked PROPOSED until he signs off.
- **Agents never** order parts, contact suppliers or release anything for production.
- **Every pull request gets a Reviewer.**

### Phase 0: Fusion access (half a day, 1 Engineer on this Mac)

Fusion's built-in MCP server already works on this Mac. I ran a test script through it, and it's now registered with Claude Code and Codex. It only answers locally, so all Engineers run on this Mac (Mac 1, already in the Swarm).
- Prove the guideline's edit test (§4.4). Build one part from a fully constrained sketch with named parameters, save it as .f3d, export it to STEP, then change a parameter and confirm it rebuilds cleanly.
- Drawing proof: produce one ISO drawing sheet through Fusion's drawing API. This Fusion version has the API we need: drawings in ISO first-angle; base, projected, section and detail views; dimensions and auto-dimensions; hole tables; datum and tolerance symbols; title blocks and revision tables; and PDF, DXF and DWG export. So agents script native drawings that update when the model changes, which is what the guideline prefers (§6.1). Every sheet is exported, rendered and checked by eye. Anything the API can't do goes on a short list for a person to finish in Fusion.

### Milestone 1: decide the layout (about 1 day, 3 Engineers, starting alongside Phase 0)

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
- A native Fusion skeleton of the whole pod, driven by named parameters: overall size, wall depth 1500, decor depth 200, tube sizes and panel splits. It's built in the plan's order, as components, not bodies.
- Sample drawings:
  - GA with sections.
  - The floor (BASE) assembly and 2 of its parts.
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

1. **Drawings.** The API covers what we need, but readable dimension placement is where the last attempt fell short. Each part gets a dimension plan, every rendered sheet gets checked by eye, and the hardware leads tune the template on day 2.
2. **Claude allowance.** This Mac's weekly Claude allowance is 70% used until Nov 3, and Opus at max effort uses it fast. If it runs low, the non-Fusion Engineers can move to another Swarm machine with a Claude account, if Dee agrees.
3. **Light vs quiet.** At 300 kg the walls lose most of their mass. The two-skin wall with fill is the light answer, and light fixes come first. Any heavy fix goes to Dee with its cost in kg.
4. **Late feedback.** With no gates, a late "no" can mean rework. Parametric CAD and small review packets after each milestone keep that cheap.
5. **One Fusion.** A single Fusion on this Mac is the bottleneck for CAD and drawings. Fusion runs scripts one at a time from a queue. If that's too slow, we add a second Fusion seat on another machine.

## Decisions for Dee

1. Approve the goals and this plan. Everything else is ready: Fusion's MCP is registered, and this Mac can run the Engineers.
2. Send last attempt's output and the engineers' top complaints about it. That's the fastest way not to repeat them.
3. Ask the team to build one wall sample and the door as soon as Milestone 1 picks the wall build, so we can measure sound early instead of trusting a calculation.

Rulings that need no answer: documents are in English with the team's Vietnamese part names alongside, and v2 files follow the guideline's folder layout (§12) under `v2/`.
