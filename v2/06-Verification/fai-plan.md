# First-article inspection plan: Spaceship (FocusPod v2)

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-VER-001 | P01 | DRAFT: a plan, no result yet | 2026-11-01 | Control pack |

What to inspect on the first article of each made part and assembly, the functional checks on the first pod, and the test that accepts each bought part. Guideline §10: an FAI line traces to a drawing characteristic (part and revision, characteristic ID, nominal, limits, unit, datum, method and gauge, result, conclusion, evidence). This is the plan: every result is empty and every line is **PLANNED**, not passed.

- **IDs.** Each characteristic gets an ID here (K-J01 and so on). When the part's drawing exists, its balloon carries the same ID, and the drawing's own tolerance governs.
- **Limits.** A limit is written only where a source sets it, with its status. Where none does, the line says "set on the drawing", because §10 forbids inventing numbers to fill a table.
- **Applies to.** Part numbers or number patterns in backticks (x is any digit). The release checklist (`v2/00-Control/release-checklist.md`) reads them to list each part's characteristics and each bought part's test.
- **Units.** mm, kg and N unless a line says otherwise.
- **Sample.** One of each part number, the first article, unless a line says otherwise; a joint or seam check covers every one on the first pod (assumption: first-article practice, which the guideline doesn't size; a drawing or the PM may raise it).
- **Pending.** A limit that waits on the part's drawing says "pending: set on the drawing", with HOLD and the reason in its status. It is never filled with a number the sources don't give.

## A. Site joints and frames

| ID | Applies to | Characteristic | Nominal | Limits | Datum | Method and gauge | Sample | Source and status | Result | Conclusion | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K-J01 | `2111xx` `4111xx` `1111xx` `11120x` | Bolt clearance hole diameter | Ø7.0 | pending: set on the drawing (HOLD) | — | pin gauges, go and no-go | 1 of each number (the first article) | DECIDED (D-64, joints register R-J6) |  | PLANNED |  |
| K-J02 | `2111xx` `4111xx` `1111xx` `11120x` | Bolt hole position from the spigot hole | 0 | Ø0.4 (±0.2) | the spigot hole | CMM, or the drill jig's check fixture | 1 of each number (the first article) | DECIDED (D-64, R-J6); calculation (stack ST-03: 0.05 to spare) |  | PLANNED |  |
| K-J03 | `2111xx` `4111xx` | Spigot hole and slot | Ø8.5; slot 8.5 × 14 | pending: set on the drawing (HOLD) | — | pin gauge Ø8.5; slot gauge | 1 of each number (the first article) | DECIDED (D-64) |  | PLANNED |  |
| K-J04 | `2111xx` `4111xx` `1111xx` | Rivnut hole | Ø9.53 | +0.10 / 0 | — | pin gauges | 1 of each number (the first article) | source (maker's data, joints register H-03) |  | PLANNED |  |
| K-J05 | `2111xx` `4111xx` `1111xx` | Frame flatness at a joint face | 0 | ±0.5 over a seam | the joint face | straightedge and feeler gauge | 1 of each number (the first article) | assumption (joints register; the frame drawings set it with the maker's capability) |  | PLANNED |  |
| K-J06 | `2111xx` `4111xx` | Tube wall: 20 × 40 × 1.2 perimeter members; the wall panels' inner studs 1.0; the ceiling's cross members 1.2 | 1.2 / 1.0 | to the profile standard (unverified) | — | wall-thickness micrometer on a cut sample | 1 of each number (the first article) | DECIDED (D-34, D-54, D-85) |  | PLANNED |  |
| K-J07 | `831001` | Locating spigot diameter and stand | Ø8; 8 proud | pending: set on the drawing (HOLD) | the rivnut face | micrometer; height gauge | 1 of each number (the first article) | PROPOSED sizes (joints register H-05, assumption) |  | PLANNED |  |
| K-J08 | `831002` | Stop washer thickness | 1.5 | ±0.05 | — | micrometer | 1 of each number (the first article) | PROPOSED part; assumption tolerance (joints register H-08) |  | PLANNED |  |
| K-J09 | `210xxx` `410xxx` | Seam gap at a stopped seam, assembled | 2.26 | 2.13–2.39 | — | feeler gauges | every stopped seam on the first pod | DECIDED (D-64); calculation (joints register stack: washer 1.5 + rivnut head 0.76); J-T3 accepts 2.26 ±0.15 |  | PLANNED |  |
| K-J10 | `210xxx` `410xxx` | Closing gap at B1–B2, B3–B4 and C1–C2, assembled | 5.5 | ±0.3 (5.2–5.8) | — | feeler or taper gauge | the three closing seams on the first pod | DECIDED (D-65); calculation (stacks ST-02 and ST-04) |  | PLANNED |  |
| K-J11 | `210xxx` `410xxx` | Gasket squeeze at a stopped seam: the 848001 strip, 3.97 free | 43% | 33–51% | — | micrometer on the free strip, then the seam gap | every stopped seam on the first pod | calculation (joints register: stop 2.13–2.39, gasket ±10% an assumption) |  | PLANNED |  |
| K-J12 | `210xxx` `410xxx` | Fit-up force per edge, sliding past a seal by hand, overhead included | — | ≤ 150 | — | push-pull force gauge on the panel edge | every panel edge on the first pod | DECIDED (joints register R-J17); test J-T5 |  | PLANNED |  |
| K-J13 | `210xxx` `410xxx` `110xxx` | Bolt thread past the rivnut's far end (838001, 838002) | 2.28 | ≥ 1.9 | — | depth gauge on a coupon | the T06 coupons (10, an assumption in the test plan) | calculation (joints register; bolt length tolerance js15, unverified) |  | PLANNED |  |
| K-J14 | `210xxx` `410xxx` `110xxx` | A head washer (838004) under every bolt head | 1 per bolt | — | — | visual count | every bolt on the first pod | DECIDED (D-63, R-J10) |  | PLANNED |  |
| K-J15 | `210xxx` `410xxx` | Outside faces flush across a seam | 0 | within 0.5 | — | straightedge and feeler gauge | every seam on the first pod | assumption (joints register tests J-T3, J-T5) |  | PLANNED |  |
| K-J16 | `2111xx` `4111xx` | Hidden frame tubes: 6063-T6, mill finish, with only the bond spec's surface prep | as stated | — | — | the mill certificate; visual | 1 of each number (the first article) | DECIDED (D-79) |  | PLANNED |  |

## B. Outer panels and skins

| ID | Applies to | Characteristic | Nominal | Limits | Datum | Method and gauge | Sample | Source and status | Result | Conclusion | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K-P01 | `210xxx` | Outer panel size: side panels 1492.74 × 1142.74; back panels 1200.61 × 1118.61, frames 1198.99 wide at the closing seams | as stated; 46 thick | pending: set on the drawing (HOLD) | the panel's spigot hole | steel tape and caliper; height gauge for the thickness | every one on the first pod | calculation (skeleton P04, PRs #24 and #58; D-66) |  | PLANNED |  |
| K-P02 | `410xxx` | Ceiling half size | 1200.61 × 1495 × 46 | pending: set on the drawing (HOLD) | the spigot hole | steel tape and caliper | every one on the first pod | calculation (skeleton P04; D-66) |  | PLANNED |  |
| K-P03 | `2113xx` `4113xx` | ACP skin bonded flat: bond line 3, skin flatness | 3 | flatness set with the bond spec | — | straightedge and feeler; the bond spec's T09 coupons | 1 of each number (the first article) | DECIDED (D-66); source (bond spec, sample test T09) |  | PLANNED |  |
| K-P04 | `2113xx` `4113xx` | Skin colour Dark Yellow EV3038 | EV3038 | match the approved sample | — | visual, against the sample, under daylight | 1 of each number (the first article) | DECIDED (D-12) |  | PLANNED |  |
| K-P05 | `2115xx` `5133xx` | Cavity fill density | 24 kg/m³ | the maker's data | — | weigh a cut piece and measure it | 1 cut piece from the first batch | DECIDED (D-81); the wall sample's T02 confirms it |  | PLANNED |  |

## C. Lining cassettes

| ID | Applies to | Characteristic | Nominal | Limits | Datum | Method and gauge | Sample | Source and status | Result | Conclusion | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K-L01 | `5111xx` `5131xx` | Tray: 0.5 mm galvanised steel, 34 mm returns, 12 mm lips | 0.5; 34; 12 | sheet to its standard (unverified); returns and lips set on the drawing | — | micrometer; caliper | 1 of each number (the first article) | DECIDED (D-37, D-69) |  | PLANNED |  |
| K-L02 | `5111xx` `5131xx` | Inside bend radius and flat-pattern size | from the CAD flat pattern | pending: set on the drawing (HOLD) | — | radius gauge; tape on the flat blank | 1 of each number (the first article) | source (the team's sheet-metal model; CEILING's flat pattern matches its bend calculation to 0.01, PR #32) |  | PLANNED |  |
| K-L03 | `510xxx` | Cassette size: wall cassettes per skeleton P04; ceiling cassette 1160 × 1045 | as stated; 34 thick | pending: set on the drawing (HOLD) | — | steel tape and caliper | 1 of each number (the first article) | calculation (skeleton P04; D-77) |  | PLANNED |  |
| K-L04 | `5113xx` `5132xx` | Felt: 9 mm, 1.8 kg/m², Dark Gray | 9; 1.8 | the maker's data | — | caliper; scale on a cut piece; colour against the sample | 1 of each number (the first article) | DECIDED (D-17, D-79); unverified (felt data, ISS-075) |  | PLANNED |  |
| K-L05 | `510xxx` | Clips and catches hold (518001, 518002): each wall clip 8.3 kg in shear, each ceiling clip 8.0 kg in pull-out, each catch lanyard 48 kg | as stated | ≥ | — | pull test T07; drop test T08 | T07: 5 of each clip; T08: 3 drops (test plan, assumptions) | calculation (test plan T07, T08; safety factor 3 an assumption, ISS-076); clip and catch products HOLD-08 |  | PLANNED |  |

## D. Front

| ID | Applies to | Characteristic | Nominal | Limits | Datum | Method and gauge | Sample | Source and status | Result | Conclusion | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K-F01 | `361001` `361003` | Glass: 4+4 laminate of toughened, heat-soaked panes | 8.76 | the glass standard (supplier) | — | micrometer; the toughening and heat-soak certificates | 1 of each number (the first article) | DECIDED (D-46, D-82); product HOLD (ISS-074) |  | PLANNED |  |
| K-F02 | `361001` `361003` | Glass outline against its DXF | the DXF | pending: set on the drawing (HOLD) | the bottom edge | full-size template or tape against the DXF | 1 of each number (the first article) | source (v1 STEP outline via skeleton P04) |  | PLANNED |  |
| K-F03 | `360002` | Fixed glass free edge to the door: gap, parallel | 4.0 | pending: set on the drawing (HOLD) | the door's edge | feeler gauges at the top, middle and bottom | every one on the first pod | DECIDED (D-68, D-74); PR #28 measured 4.00 in CAD |  | PLANNED |  |
| K-F04 | `360002` | Glass depth in its hidden U-channels | 11.5 | pending: set on the drawing (HOLD) | — | depth gauge before glazing | every one on the first pod | DECIDED (D-68) |  | PLANNED |  |
| K-F05 | `361002` | Kick strip running gap over the threshold | 7 | 6.5–7.5 | the threshold | feeler gauges | 1 of each number (the first article) | DECIDED (D-68, D-72); limits from the mechanical check's gap rule (`v2/04-Checks/config/gap-rules.csv`) |  | PLANNED |  |
| K-F06 | `361002` `110xxx` `1111xx` | Black anodised, matte (the kick strip and every base band piece) | ≥ 20 µm | class AA20 (EN ISO 7599) | — | eddy-current coating thickness gauge; visual against the sample | every anodised piece of the first pod | DECIDED (D-67, D-79) |  | PLANNED |  |
| K-F07 | `360001` | Door unit mass, as hung | 49.1 | weigh; the hardware is rated ≥ 60 kg | — | scale | every one on the first pod | calculation (CAD, with the hollow kick strip, D-85; the layout study's live count, PR #61); DECIDED rating (D-68) |  | PLANNED |  |
| K-F08 | `360001` | Door keep: the magnetic catch in DT holds the door | 35 N | ≥ | — | push-pull gauge at the latch corner | every one on the first pod | DECIDED (D-83); product to be named |  | PLANNED |  |

## D1. Decor block DL (FRONT, PR #105)

| ID | Applies to | Characteristic | Nominal | Limits | Datum | Method and gauge | Sample | Source and status | Result | Conclusion | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K-D18 | `350001` | DL assembled: outer shape to skeleton P04, 205 mm deep as v1 (D-49); left-hinged door side (D-19); stands on its 2 spigots on the band; ships with the hinges' frame halves fitted | 205 deep; about 12.7 kg | shape pending: set on the drawing (HOLD); mass ≤ 20 (D-03) | the 2 spigot holes | tape and caliper; trial fit on the spigots; scale | 1 of each number (the first article) | DECIDED (D-03, D-19, D-49); source (FRONT's parts list, PR #105; joints register J-FRONT-02) |  | PLANNED |  |
| K-D19 | `351101` | DL skin: flat ACP 3 mm panels, 45° mitred joints as v1, bonded to the frame, with three hinge pockets; colour Dark Yellow EV3038 | 3; EV3038 | outline per its DXF; mitres and the hinge pockets pending: set on the drawing (HOLD: the pocket sizes wait on the hinge product) | the frame | template against the DXF; visual against the approved sample; the bond spec's T09 coupons | 1 of each number (the first article) | DECIDED (D-12, D-49); source (FRONT's parts list, PR #105); hinge HOLD (D-46) |  | PLANNED |  |
| K-D20 | `351104` | DL frame: 26 welded 6063-T6 tubes, 20 × 20 × 1.5 and the 60 × 20 × 1.5 hinge members, 11.8 m in all, per its cut list; it carries the door's load (the hinges, hinge post H1 to H3, the bolt-line post B04 with 6 holes Ø14 for the J-FRONT-01 rivnut tails); mill finish (D-79) | lengths per the cut list; Ø14 | lengths, mitres and hole positions pending: set on the frame drawing (HOLD) | the hinge post | tape; protractor; wall micrometer; pin gauge Ø14 | 1 of each number (the first article) | calculation (FRONT's cut list); DECIDED finish (D-79); source (joints register HOLD-10; ISS-045) |  | PLANNED |  |
| K-D21 | `351102` | DL back plate: 5754-H22 sheet 2.0, laser cut; 6 holes Ø9.53 for the rivnuts on X −1224, 3 per side | 2.0; Ø9.53 | Ø9.53 +0.10/0 (row); its row gives no finish or general tolerance yet (HOLD: FRONT to add them if it claims D-89 part 4) | the wall's bolt line | pin gauges; CMM or the drill fixture | 1 of each number (the first article) | source (FRONT's parts list, PR #105; joints register J-FRONT-01) |  | PLANNED |  |
| K-D22 | `351103` | Door hinge-side stop: 6063-T6 aluminium angle in 4 lengths between the hinges, screwed through DL's door-side skin into the frame's door-side tubes | frame gap 2 to 6 | the gap 2 to 6 (hardware selection C3) | the door's hinge edge | feeler gauge; caliper | 1 of each number (the first article) | source (FRONT's parts list, PR #105; hardware selection C3) |  | PLANNED |  |

## D2. Decor block DR (FRONT, PR #105)

| ID | Applies to | Characteristic | Nominal | Limits | Datum | Method and gauge | Sample | Source and status | Result | Conclusion | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K-D01 | `350003` | DR assembled: outer shape to skeleton P04, 205 mm deep as v1 (D-49); stands on its 2 spigots on its support, held by the J-FRONT-01 bolts | 205 deep; skeleton P04 shape | pending: set on the drawing (HOLD) | the 2 spigot holes | tape and caliper; trial fit on the spigots | 1 of each number (the first article) | DECIDED (D-49; joints register J-FRONT-02); drawing pending |  | PLANNED |  |
| K-D02 | `350003` `350004` | Mass as each ships: DR with its fitted glass channels and without the air supply assembly; the air supply assembly joined (D-87) | DR about 18.9 as shipped with its channels (FRONT's estimate); air supply assembly about 14.9 | DR ≤ 19.0 (D-108); each piece ≤ 20 (D-03) | — | scale | 1 of each number (the first article) | DECIDED (D-03, D-87, D-106, D-108); calculation (FRONT's list; 14.9 kg, the air table, D-60); ISS-087 stays open until DR's CAD confirms it |  | PLANNED |  |
| K-D03 | `351301` | DR skin: flat ACP 3 mm panels, 45° mitred joints as v1, bonded to the frame; colour Dark Yellow EV3038 | 3; EV3038 | outline per its DXF; mitres pending: set on the drawing (HOLD) | the frame | template against the DXF; visual against the approved sample; the bond spec's T09 coupons | 1 of each number (the first article) | DECIDED (D-12, D-49); source (FRONT's parts list, PR #105) |  | PLANNED |  |
| K-D04 | `351306` | DR frame: 26 welded 6063-T6 tubes per its cut list, walls by role (D-106, the D-85 rule): the 19 skin-only tubes 1.0, the tubes that carry rivnuts 1.2, the fan-box shelf tubes 1.5; mill finish (D-79) | walls 1.0 / 1.2 / 1.5; lengths per the cut list | lengths and mitre angles pending: set on the frame drawing (HOLD) | the frame's bolt-line tube | tape; protractor; wall micrometer | 1 of each number (the first article) | calculation (lengths from the parameters, FRONT's cut list); DECIDED walls (D-106) and finish (D-79) |  | PLANNED |  |
| K-D05 | `351306` | DR frame holes: 10 rivnuts for the access panel bolts; 6 holes Ø14 in the bolt-line tube for the J-FRONT-01 rivnut tails | rivnut holes Ø9.53; Ø14 | Ø9.53 +0.10/0 (maker's data); Ø14 and positions pending: set on the drawing (HOLD) | the bolt-line tube | pin gauges; position on a check fixture | 1 of each number (the first article) | source (FRONT's parts list; joints register H-03) |  | PLANNED |  |
| K-D06 | `351302` | DR back plate: 5754-H22 sheet 1.5 (D-106, was 2.0; inside the rivnut grip), mill finish, laser cut; 6 holes Ø9.53 for the rivnuts on the X +1224 strip, on the wall's bolt line (critical) | 1.5; Ø9.53 | Ø9.53 +0.10/0 (row, critical); other sizes ISO 2768-m (row); the critical holes' position: HOLD (the row gives no position limit yet) | the wall's bolt line | pin gauges; CMM or the drill fixture for the 6 critical holes | 1 of each number (the first article) | source (FRONT's parts list; J-FRONT-01); no drawing (D-89 part 4); rivet HOLD |  | PLANNED |  |
| K-D07 | `351305` | DR access panel: 5754-H22 sheet 3.0, mill finish; opening 203 × 215; 10 bolt holes Ø6.6; 2 holes Ø9.53 at X 971, Z 1700 and 1850 for the column's hook studs | 3.0; 203 × 215; Ø6.6; Ø9.53 | Ø9.53 +0.10/0 (row); other sizes ISO 2768-m (row) | the panel's bolt holes | pin gauges; tape; trial fit of the 10 M6 × 16 bolts | 1 of each number (the first article) | source (FRONT's parts list; the air table, D-60; PM ruling 2026-11-01); gasket tape HOLD |  | PLANNED |  |
| K-D08 | `351303` | DR inner panel: ACP 3 mm, CNC routed; lifts off for the fan box; held by 4 clips | 3 | outline ISO 2768-m (row) | — | template against the DXF; trial lift-off | 1 of each number (the first article) | source (FRONT's parts list; D-59, D-60); clip HOLD |  | PLANNED |  |
| K-D09 | `351304` | DR inner panel felt: PET 9 mm, Dark Gray, laser cut, glued to 351303 at the factory | 9 | outline ±2 (row) | the inner panel's edge | tape; caliper; check the bond; the emission certificate | 1 of each number (the first article) | source (FRONT's parts list; D-31, D-79); certificate HOLD |  | PLANNED |  |
| K-D10 | `350004` | Air supply assembly: ships joined, slides into DR through its inner face, plug-in connectors; stands on the frame's shelf tubes | as stated | slides in by hand; fixing HOLD (air detail) | the shelf tubes | trial fit; visual | 1 of each number (the first article) | DECIDED (D-60, D-87); source (FRONT's parts list) |  | PLANNED |  |

## D3. Decor block DT (FRONT, PR #105)

| ID | Applies to | Characteristic | Nominal | Limits | Datum | Method and gauge | Sample | Source and status | Result | Conclusion | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K-D13 | `350002` | DT assembled: outer shape to skeleton P04, 205 mm deep as v1 (D-49); goes on after the door hangs; sits on a spigot on DL and on DR and takes 4 bolts from the ceiling's front tubes at the 220 mm rule | 205 deep; about 7.2 kg | shape pending: set on the drawing (HOLD); mass ≤ 20 (D-03) | the spigots on DL and DR | tape and caliper; trial fit; scale | 1 of each number (the first article) | DECIDED (D-03, D-49); source (FRONT's parts list, PR #105; joints register J-FRONT-03, which FRONT's list still marks HOLD) |  | PLANNED |  |
| K-D14 | `351201` | DT skin: flat ACP 3 mm panels, 45° mitred joints as v1, bonded to the frame; colour Dark Yellow EV3038 | 3; EV3038 | outline per its DXF; mitres pending: set on the drawing (HOLD) | the frame | template against the DXF; visual against the approved sample; the bond spec's T09 coupons | 1 of each number (the first article) | DECIDED (D-12, D-49); source (FRONT's parts list, PR #105) |  | PLANNED |  |
| K-D15 | `351204` | DT frame: 13 welded 6063-T6 tubes 20 × 20 × 1.5, 8.5 m in all, lengths per its cut list; mill finish (D-79; FRONT's row doesn't state it); its rail F02 carries the catch 368007 and the top stop 351203 | lengths per the cut list | lengths and mitre angles pending: set on the frame drawing (HOLD) | the rail F02 | tape; protractor; wall micrometer | 1 of each number (the first article) | calculation (lengths, FRONT's cut list); DECIDED finish (D-79) |  | PLANNED |  |
| K-D16 | `351202` | DT back plate: ACP 3 mm, CNC routed, bonded to the frame; the soffit sits behind it (D-60) | 3 | pending: set on its drawing, with the bond area and surface prep (HOLD); its row's tolerance and finish to come from FRONT | the frame | template against the DXF; the bond spec's T09 coupons | 1 of each number (the first article) | source (FRONT's parts list, PR #105); it keeps its drawing: a bonded part shows its bond area and surface prep there (D-89; PM, 2026-11-01) |  | PLANNED |  |
| K-D17 | `351203` | Door top stop: 6063-T6 aluminium angle cut to length, screwed up through DT's underside into the rail F02 | frame gap 2 to 6 | the gap 2 to 6 (hardware selection C3) | the door's top edge | feeler gauge; caliper | 1 of each number (the first article) | source (FRONT's parts list, PR #105; hardware selection C3) |  | PLANNED |  |

## E. Base

| ID | Applies to | Characteristic | Nominal | Limits | Datum | Method and gauge | Sample | Source and status | Result | Conclusion | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K-B01 | `110xxx` `1111xx` | Base band wall 1.5, with an aluminium load block at each glide | 1.5 | the profile standard (unverified) | — | caliper; check each block is in | 1 of each number (the first article) | DECIDED (D-86) |  | PLANNED |  |
| K-B02 | `1114xx` | Floor panel: 9 mm poplar-core ply with a hard face; plan size per skeleton P04, X 0 to ±1210 and Y −645 to 810 (1210 × 1455), plus its half-lap | 9; 1210 × 1455 | pending: set on the drawing (HOLD) | the band's inner face | caliper; steel tape | 1 of each number (the first article) | DECIDED (D-72, D-85, D-86); calculation (skeleton P04) |  | PLANNED |  |
| K-B03 | `1114xx` | Panel edge and half-lap seam under 1000 N on the foam | — | ≤ 1 deflection | the room floor | dial gauge under a 1000 N load; castor rolled over the edge | the first F1 and F2, at the half-lap and one free edge | assumption until tested (D-76); calculation about 0.6 (D-86) |  | PLANNED |  |
| K-B04 | `1115xx` | Floor foam: 3 mm firm closed-cell, about 200 kg/m³, bonded under the panel at the factory | 3 | the maker's data | — | caliper; check the bond | 1 of each number (the first article) | DECIDED (D-76, D-87); product HOLD (ISS-085) |  | PLANNED |  |
| K-B05 | `110000` | Door threshold (in the BASE assembly until the profile has its own number): 13 high, a 6 mm upright, then a 1:2 bevel | 13; 6; 1:2 | pending: set on the drawing (HOLD) | the room floor | height gauge; angle gauge | every one on the first pod | DECIDED (D-72) |  | PLANNED |  |
| K-B06 | `110000` | Intake mesh band piece under the right decor block (in the BASE assembly until it has its own number): free area | 0.028 m² | ≥ | — | measure the open area | every one on the first pod | DECIDED (D-62) |  | PLANNED |  |
| K-B07 | `110000` | Base seal (118001) at the floor's edge, against the band's inner face | 4 gap | sealed | — | feeler gauge; light test | every one on the first pod | DECIDED (D-86) |  | PLANNED |  |
| K-B08 | `11121x` | Corner and inline keys 111211 to 111214: one machined 6061-T6 block, mill finish, hidden, fixed in a band piece's open end at the factory; 30 mm (D-103, was 25) × 35 × 75; its fixing holes keep 2 diameters from its ends; each key's hook studs take the next piece | 30 × 35 × 75 | pending: set on the Joints Engineer's tabulated drawing (HOLD) | the band's bottom wall | caliper; trial fit in a band end | 1 of each number (the first article) | DECIDED (D-87 hook-in keys, D-95 one source, D-102 and D-103 hole distances); source (BASE's row and the joints register J-BASE-02, 25 × 35 × 75 before D-103) |  | PLANNED |  |
| K-B10 | `1111xx` | Band holes for the key screws: 2 diameters from the band piece's cut end | 14.9 to 19.5 from the cut ends | pending: set on the drawing (HOLD) | the cut end | caliper | 1 of each number (the first article) | DECIDED (D-102, D-103) |  | PLANNED |  |
| K-B09 | `111601` | Glide doubler: 5754-H22 sheet 3 mm, mill finish, laser or waterjet cut, 52 × 36 with one Ø13 hole centred for the glide's M10 rivnut; inside the band on its bottom face, clamped by that rivnut | 52 × 36 × 3; Ø13 | Ø13 +0.10/0 (critical; HOLD with the nut); centred ±0.2; other sizes ISO 2768-m (BASE's row) | the doubler's long edges | pin gauges; caliper on the hole's position | 1 of each number (the first article) | source (BASE's parts list, PR #55); its edge distance under the PM's exception of 2026-11-01 (the mechanical check's edge exceptions); the 3 mm thickness an assumption; no drawing (D-89 part 4) |  | PLANNED |  |

## F. Air, electrical and interior

| ID | Applies to | Characteristic | Nominal | Limits | Datum | Method and gauge | Sample | Source and status | Result | Conclusion | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K-A01 | `61xxxx` | Cartridge: 173 × 314 × 1750, two 80 mm passages between three 50 mm layers | as stated | pending: set on the drawing (HOLD) | — | steel tape and caliper | 1 of each number (the first article) | calculation (D-61, the air report) |  | PLANNED |  |
| K-A02 | `61xxxx` `81xxxx` | Air column 217 × 360 × 2105 and soffit 2332 × 360 × 220 | as stated | pending: set on the drawing (HOLD) | the pod's inside corner | steel tape | 1 of each number (the first article) | calculation (D-61, the air report, skeleton P04) |  | PLANNED |  |
| K-A03 | `61xxxx` | Each shipped air piece ≤ 20 kg: the soffit with its fan box about 13.9, the riser with the supply fan box about 14.9 | ≤ 20 | — | — | scale | 1 of each number (the first article) | DECIDED (D-03, D-87); calculation |  | PLANNED |  |
| K-A04 | `611501` | AIR's intake riser, in DR's supply-box space: galvanised steel DX51D+Z duct; its open foot 140 mm over the base opening | 140 | pending: set on the drawing (HOLD) | the base opening | caliper; tape | 1 of each number (the first article) | source (AIR's parts list, PR #91; the air table, D-60); AIR's part, placed in DR's reserved air space (D-105) |  | PLANNED |  |
| K-A05 | `610401` | AIR's supply fan box: 2 mm aluminium with a 50 mm lining inside, joined to the riser and shipped as its own pallet piece; 12 mm from the fixed glass channel | 2; 50; 12; ≤ 20 kg as it ships | pending: set on the drawing (HOLD); lining and bulkhead HOLD (air detail) | the glass channel | caliper; feeler gauge; scale | 1 of each number (the first article) | source (AIR's parts list, PR #91; the air table, D-60); DECIDED (D-03, D-87, D-105) |  | PLANNED |  |
| K-E01 | `71xxxx` | Harness tested at the factory; the hub's self-test passes | pass | — | — | the factory test record; the self-test log | 1 of each number (the first article) | DECIDED (D-87) |  | PLANNED |  |
| K-I01 | `81xxxx` | Light shelf within 0.4 kg/m; the 1000 mm ledge in 1.5 mm folded aluminium | 0.4; 1.5 | pending: set on the drawing (HOLD) | — | scale; caliper | 1 of each number (the first article) | DECIDED (D-85) |  | PLANNED |  |

## G. Functional checks on the first pod

| ID | Check | Pass mark | Method and gauge | Sample | Source and status | Result | Conclusion | Evidence |
|---|---|---|---|---|---|---|---|---|
| F-01 | The door swings outward to 90° and clears the soffit (door top Z 2116, soffit 4 mm above it) | no contact | swing the door; feeler at the top | the first pod | calculation (the air report); the mechanical check's swing sweep |  | PLANNED |  |
| F-02 | The door closes and stays shut: the 35 N catch, the drop seal on the threshold, the magnetic seal pair on the glass edge | closed, no gap | visual; light test from inside | the first pod | DECIDED (D-40, D-83) |  | PLANNED |  |
| F-03 | Every seam and seal: no light through any joint | no light | lamp inside, room dark | the first pod | confirmed (REQ-SND-02) |  | PLANNED |  |
| F-04 | Fans: 53 l/s at 26 dB(A) or less and the 65 l/s boost at 30 dB(A) or less, at seated ear height; with two people inside, 53 l/s holds the inside within 4 K of the room | as stated | flow hood; sound level meter; thermometers inside and in the room | the first pod | DECIDED (D-50, D-52); calculation (25.3 and 29.7 dB(A), D-62; 249 W and 3.9 K at 53 l/s, PR #72); the fan sample's T04 |  | PLANNED |  |
| F-05 | Control: fans start on presence; CO2 and the 4 K limit drive the flow; boost by hand; with the voice kit fitted, the boost holds 4 K | as stated | logged readings over a session | the first pod | DECIDED (D-44, D-50, D-88) |  | PLANNED |  |
| F-06 | The hub's self-test button runs and passes | pass | press it; read the log | the first pod | DECIDED (D-87) |  | PLANNED |  |
| F-07 | Lights: the light shelf scenes, including a 'call' scene that lights the face from the screen side | as stated | visual | the first pod | DECIDED (D-70) |  | PLANNED |  |
| F-08 | Assembly: two people, one 5 mm key, every piece but the glass 20 kg or less | about 127 min; never over 4 h | timed trial with the guide | the first pod | DECIDED (D-03, D-63; 4 h, REQ-ASM-01); calculation (the guide, PR #59; D-87's target about 126) |  | PLANNED |  |
| F-09 | Mass as shipped | ≤ 420 kg (cap); 415.2 calculated | weigh every piece | the first pod | DECIDED cap (D-37); calculation (the layout study's live count, PR #68) |  | PLANNED |  |
| F-10 | Sound: speech level reduction to ISO 23351-1 | the measured figure; about 19 dB calculated | lab, after the wall sample's T01 from 100 Hz | the first pod | DECIDED (D-53); calculation |  | PLANNED |  |
| F-11 | Voice kit, once it exists: average draw over a session and peak on its 12 V 5 A outlet; with it on, the inside within 4 K at 30 dB(A) or less | ≤ 40 W average; ≤ 60 W peak; ≤ 4 K | power logger on the outlet; thermometers; sound level meter | the first pod | DECIDED (D-11, D-88); calculation (4 K takes 62 l/s at 28.7 dB(A), PR #72) |  | PLANNED |  |

## H. Bought parts: the test that accepts each

| Applies to | Part | Test | Source |
|---|---|---|---|
| `838001` | Socket head bolt M6 × 16 | T06, J-T1 | test plan T06 (the bolt sets the torque); joints register J-T1 |
| `838002` | Closing-seam pin bolt M6 × 25 | J-T1 | joints register J-T1 |
| `838003` | Rivnut M6 | T06, J-T1 | test plan T06; joints register J-T1 |
| `838004` | Head washer 6.4 × 18 | T06 | test plan T06 |
| `838005` | Captive retainer | J-T2 | joints register J-T2 |
| `838010` | Flanged button head screw M6 × 12, the corner keys' fixing screws | J-T6 | joints register J-T6 (the hook-in corner key mock-up); they carry the joint's pull (D-102) |
| `848001` | Joint gasket | J-T3 | joints register J-T3 |
| `848004` | Closing-seam seal | J-T3, J-T5 | joints register J-T3, J-T5 |
| `848012` | Cassette edge seal | F-03 | the light test |
| `118001` | Base seal | J-T4 | joints register J-T4 |
| `518001` | Cassette clip | T07 | test plan T07 |
| `518002` | Ceiling safety catch | T08 | test plan T08 |
| `108002` | ACP bond set | T09 | test plan T09 |
| `108001` | The 5 mm hex key | F-08 | the timed assembly |
| `368001` `368003` `368006` `368101` `368103` | Drop seal, magnetic seal halves, hinges, pull | T13 | test plan T13 (once the hinges and lock are named) |
| `368007` `368102` | Door catch and strike | F-02 | the door check |
| `368002` `368004` `368005` | Glazing U-seal, U-profile, frame-stop seal | F-03 | the light test |
| `618xxx` | AIR's bought parts (the fans) | T04 | test plan T04 |
| `71xxxx` | ELECTRICAL's parts | F-06 | the hub's self-test, with the harness tested at the factory (D-87) |

A bought part with no line here has no test yet; the release checklist shows it as open.

## How this plan grows

- When a part's drawing lands, its characteristics move onto the drawing with these IDs, and new ones get the next free ID in their section.
- When a test or a first article is measured, the result, conclusion and evidence columns fill in (the measured value, the sample number, the gauge's calibration, the date and the file). Only then can a line say PASS.
- The release checklist re-reads this file to show which parts have characteristics and which bought parts have a test.
