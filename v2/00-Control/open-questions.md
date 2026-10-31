# Open questions: Spaceship (FocusPod v2)

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-CTL-006 | P01 | DRAFT. Answers are PROPOSED unless the PM has DECIDED them (`decision-log.md`). | 2026-10-31 | Control pack |

Each question gets an answer and the reasons for it. Where the PM has ruled, the answer is DECIDED and logged in `decision-log.md`. Otherwise it is PROPOSED: the work follows it now, and it changes if the PM rules otherwise. Nothing waits for outside approval (`AGENTS.md`). Numbers carry their status (`conventions.md` §9). The hardware parts named below are functions, not chosen products: real part numbers come from the hardware selection (`v2/05-Engineering/hardware/`, guideline §4.3) before anything goes into CAD.

| Q | Question | Answer in one line | Status | Issues |
|---|---|---|---|---|
| Q1 | Door and glass | Keep v1's front layout and outline; 4+4 laminated glass, frameless as v1; dormakaba OFFICE 11.233 hinges in a 160 mm pocket in the left decor block; sealed all round; fixed panel in sealed profiles | DECIDED material (D-27) and hinges (D-30); rest PROPOSED | ISS-001, -002, -003, -023, -043 |
| Q2 | Lights | One dimmable, low-heat LED ceiling light plus a soft front face light for video calls, all on 12 V; the Hardware Engineer picks the parts | DECIDED (D-20); 30 W budget PROPOSED | ISS-004, -061 |
| Q3 | Door hand | Left-hinged as v1, seen from outside facing the door, with the hinge pocket in the left decor block; handle and catch on the right; opens outward | DECIDED hinge (D-19); swing PROPOSED | ISS-055 |
| Q4 | Floor type | Thin floor inside the aluminium base band, 20 mm threshold at the door, walls standing around it on a base rail, packers for leveling | DECIDED (D-05, D-18); layer build PROPOSED | ISS-040, -050, -053, -054 |

## Q1. Door and glass

The build plan has no glass at all (ISS-001). The look needs v1's glass layout (REQ-LOOK-04).

**Answer** (material DECIDED, D-27; hinges DECIDED, D-30; the rest PROPOSED)
1. **Same layout and outline as v1.** One hinged door leaf and one fixed panel in the same plane, smoked gray. The door is a trapezoid, 1175.6 wide at the bottom and 892.9 at the top, 2011.1 tall, with a slanted leading edge that meets the fixed panel's slanted edge. The fixed panel has 5 sides and follows the inner edge of the right decor block. Status: source (v1 STEP outline). The v2 cut sizes come from the v2 decor and floor once the depth chain and height are fixed (ISS-012, ISS-013).
2. **Material, DECIDED (D-27): 4+4 laminated glass (8.76 mm), frameless as in v1.** It replaces the earlier acrylic baseline (D-07): acrylic needed an aluminium stile along its hinge edge, which added an opaque band about 80 mm wide down the door and broke the look rule (D-01). Laminated glass also removes the creep, scratch, fire-class and flatness risks. Acrylic stays only as an optional experiment on the factory sample. The laminate's smoked tint is matched to v1 on the sample.
3. **Hardware, by function.** Each item gets a real part number from the hardware selection first.
   - Hinges: dormakaba OFFICE 11.233 (D-30), in a 160 mm pocket inside the left decor block DL. The door in laminated glass is about 43 kg (calculation C5 in `requirements.md`); the hinges' clamping range for 8.76 mm laminate goes on the factory's question list. v1 lists 3 hinges, but its CAD has only 2 positions (ISS-024).
   - Handle: a back-to-back pull handle, inside and outside, about 300 mm long like v1. The v1 CAD shows only the outside half (ISS-056).
   - Catch: a magnetic catch on the leading edge, with no lock or latch. It keeps the pull light (REQ-US-04).
   - Seals: a perimeter seal on the hinge side and top; a seal on the slanted joint between the door and the fixed panel; an automatic drop seal at the bottom onto the threshold, housed in a 90 mm aluminium kick strip in the base band's dark finish (D-40).
   - Fixed panel: held in sealed U profiles with gaskets, sitting on setting blocks, at the base, DT and DR. No glue, so the panel can be replaced.
4. **Handling:** two people with suction lifters. The door and fixed panel travel on the standard long pallet, because 2011 is taller than a 48 × 40 pallet takes (layout study).

**Reasons**
- Weight: the front is the heaviest single item. In 4+4 laminated glass the door is about 43.3 kg and the fixed panel about 28.0 kg (calculation C5); the BOM's rectangles overstated the door (ISS-023). D-27 frees the weight for it by moving the ceiling to 40 mm frames, so the pod stays at about 400 kg.
- Look: same outline, same smoked colour, same plane.
- Safety: a glass door must be safety glass, tempered or laminated, as is standard practice. Laminated glass holds together if it breaks.
- Sound: the front is the weak spot. Sealing every edge does more than adding thickness (PLAN.md "Quiet without the weight"), and the quiet target is about 24 dB (REQ-SND-01).

## Q2. Lights

The build plan has no lights. The v1 BOM lists 2 square 170 × 170 ceiling lights, and the v1 CAD has 1 (ISS-004, ISS-019).

**Answer: DECIDED (D-20)**
1. **One dimmable, low-heat LED ceiling light**, placed clear of the fan grilles, the silencers and the reserved sprinkler zone. The Hardware Engineer picks the part.
2. **A soft front face light for video calls**, for example a diffused strip on the inside face of the top decor block DT or the ceiling's front edge (placement PROPOSED). It lights the seated user's face from the front and above, which kills the harsh shadows users complain about (market study).
3. **All on 12 V** (D-10). Total lighting power 30 W or less (REQ-AIR-06; PROPOSED, assumption). Colour about 3500–4000 K with high colour rendering (assumption, to confirm with the fitting data). The sensor hub switches them on with presence; what the plan's switch does is open (ISS-061).
4. Lights connect with plugs, so a ceiling panel can come off without cutting wires.

**Reasons**
- Heat is the users' top complaint. Each watt of light is heat in a small box: 30 W adds about 0.36 K at 70 l/s (calculation C4 basis).
- Video calls come up again and again in user comments (market study).
- 12 V keeps mains out of the ceiling, and the later US version only changes the power supply.
- The lights are inside, so the outside look doesn't change.

## Q3. Door hand

**Answer** (hinge side DECIDED, D-19; swing PROPOSED)
- **Left-hinged, as v1** (D-19): hinges on the **left** (−X side), seen from outside facing the door, in a hinge pocket in the left decor block DL. The handle and catch are on the right, next to the fixed panel.
- **The door opens outward.** v1's files don't show the swing direction (ISS-055), so this needs confirming.
- No mirrored version for the prototype.

**Reasons**
- The look sets the hand. The fixed glass and the wide faceted right block DR sit on the right, and the door's slanted edge meets the fixed glass. Hanging the door on the right would put the hinges on glass or on the facets and change the glass layout. In the v1 STEP the hinges sit at X ≈ −972…−908, on DL.
- Opening outward leaves the small inside free for the customer's furniture (the pod ships empty), makes it quicker to get out, and the drop seal still closes onto the threshold.
- Keeping v1's hand keeps v1's hardware positions as a check.

## Q4. Floor type: thin floor (DECIDED, D-05 and D-18; the layer build below is PROPOSED)

The PM's decisions: 2–3 cm panels lying on the room floor, the walls fixed around them, in place of the plan's raised 50×100 steel floor frame (D-05); the floor sits inside the aluminium base band, with a 20 mm threshold at the door (D-18).

**PROPOSED build, from the room floor up**

| Layer | What | Thickness | Status |
|---|---|---|---|
| Underlay and base seal | Closed-cell foam or rubber underlay under the floor panels; a compressible seal strip under each wall's bottom rail | about 3 mm | assumption |
| Floor panel | 15 mm plywood or a similar low-emission board, CNC cut to size | 15 mm | assumption |
| Wear layer | Factory-applied wood-look surface, like v1's wood look | about 2 mm | assumption |
| **Total** | | **about 20 mm**, matching the 20 mm threshold | threshold DECIDED (D-18); layers PROPOSED |

**Split.** For example 3 panels across the width, about 810 × 1520 mm each and about 15 kg each (assumption: plywood 650 kg/m³ plus a 2 kg/m² wear layer). That keeps each under 20 kg and lets them stand upright on a 48 × 40 pallet. The layout study sets the final split. Panels meet with a tongue and groove so the seams stay flush, with no glue.

**Edge detail**
- At the side and back walls: an aluminium angle, the **base rail**, is screwed along the floor's outer edges at the factory. Its upstand sets where each wall stands.
- At the door: an aluminium **threshold** profile on the floor's front edge, bevelled down to the room floor, with a flat land for the door's drop seal. The threshold is 20 mm (D-18). A later US version needs about 13 mm or a ramp (ISS-053).
- Under the decor blocks DL and DR: the base rail runs to the front corners, so the decor blocks locate on it too.
- Outside: the **aluminium base band** (D-18) runs around the bottom; the thin floor lies inside it. It keeps v1's look (in v1 the band is the 106 mm floor frame plus brackets) and hides the seal and rail. Whether the band and the base rail can be one profile is for the BASE design.

**How the walls fix**
1. Lay the underlay. Lay the floor panels with their base rails, butted and squared. The CNC-cut floor sets the footprint.
2. Stand the back wall panels, then the side walls, on the room floor around the floor, with each wall's bottom tube against the base rail upstand. The joint finds its own place.
3. Fix each wall to the rail with tool-free connectors where they can hold, otherwise with captive M6 bolts from inside through the wall's bottom tube into rivet nuts in the base rail upstand, about every 400 mm (assumption; the joint calculation sets the pitch). One bolt size, one tool (D-08, ISS-064).
4. The walls carry their own weight and the roof's straight to the room floor through the base seal. The floor panels carry only people and furniture.

**Leveling**
- The room floor is flat and level by requirement (REQ-SCP-01), so there are no adjustable feet.
- Up to about ±5 mm over the footprint (assumption, ISS-054), the underlay and base seal take it, plus 1, 2 and 3 mm plastic packers from the installation kit under the wall bottom rails at the corners and at the door.
- Check that the door opening is plumb with a spirit level before the final tightening. The hinge side must be true.
- A floor worse than that needs a leveling kit (open, ISS-054).

**Reasons**
- Weight: no steel frame, joists, feet or boards. PLAN.md estimates about 50 kg saved.
- Step: 20 mm instead of about 130 mm (calculation C7). Easier to walk in, and closer to a later US threshold.
- Headroom: about 10 cm more inside than v1, at the same 2400 outside height: about 2329 mm against v1's 2223, with D-27's 53 mm ceiling (REQ-BLD-06, calculation).
- Sound: it still closes the bottom of the box, with a seal. Floorless pods post the weakest numbers (market study).
- Square and quick: the floor sets the wall positions, and the walls locate themselves on the rail.

**What it costs**
- The walls get about 100 mm taller, which changes the panel split and pallet heights (ISS-050).
- No cable space under the floor; cables run in the back wall (ISS-005).
- A damaged floor panel can't be swapped without loosening a wall. Fine for the prototype.

## Other questions and their answers

| Question | Working default | Issue |
|---|---|---|
| Decor colour: yellow or black? | DECIDED (D-12): Dark Yellow EV3038, matching the plan's material list and v1's product photos | ISS-031 |
| Quiet target and weight | DECIDED (D-27, D-37): 4+4 laminated front; the pod at about 418 kg against a 420 kg cap; 23.8 dB calculated (Class C), with the factory sample deciding. The 0.4 mm lining tray was tried and dropped because it cost 1 dB. | ISS-063, ISS-065, ISS-068 |
| Assembly method | DECIDED (D-08): tool-free connectors, captive bolts, factory-made subassemblies, felt pre-fitted at the factory | ISS-064 |
| Overall height and its datum | DECIDED (D-21): 2400 from the room floor to the top of the roof skin | ISS-013 |
| Depth chain between the walls and the decor | Back face at Y = +850, decor front at Y = −850, overlap set by the bracket joint | ISS-012 |
| Visible panel seams | DECIDED (D-23): 2 sheets per side wall and 4 on the back, with crisp, aligned reveals | ISS-044 |
| What "one hand tool" and "part" mean | One driver or key for every site fastener; a part is each piece handled on its own (PROPOSED) | ISS-047 |
