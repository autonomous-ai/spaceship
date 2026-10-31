# First-article inspection plan: Spaceship (FocusPod v2)

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-VER-001 | P01 | DRAFT: a plan, no result yet | 2026-10-31 | Control pack |

What to inspect on the first article of each made part and assembly, and the functional checks on the first pod. Guideline §10: an FAI line traces to a drawing characteristic (part and revision, characteristic ID, nominal, limits, unit, datum, method and gauge, result, conclusion, evidence). This is the plan: every result is empty and every line is **PLANNED**, not passed.

- **IDs.** Each characteristic gets an ID here (K-J01 and so on). When the part's drawing exists, its balloon carries the same ID, and the drawing's own tolerance governs.
- **Limits.** A limit is written only where a source sets it, with its status. Where none does, the line says "set on the drawing", because §10 forbids inventing numbers to fill a table.
- **Applies to.** Part numbers or number patterns in backticks (x is any digit). The release checklist (`v2/00-Control/release-checklist.md`) reads them to list each part's characteristics.
- **Units.** mm, kg and N unless a line says otherwise.

## A. Site joints and frames

| ID | Applies to | Characteristic | Nominal | Limits | Datum | Method and gauge | Source and status | Result | Conclusion | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| K-J01 | `211xxx` `411xxx` `1111xx` `1112xx` | Bolt clearance hole diameter | 7.0 | set on the drawing | — | pin gauges, go and no-go | DECIDED (D-64, joints register R-J6) | | PLANNED | |
| K-J02 | `211xxx` `411xxx` `1111xx` `1112xx` | Bolt hole position from the spigot hole | 0 | Ø0.4 (±0.2) | the spigot hole | CMM, or the drill jig's check fixture | DECIDED (D-64, R-J6); calculation (stack ST-03: 0.05 to spare) | | PLANNED | |
| K-J03 | `211xxx` `411xxx` `1111xx` `1112xx` | Spigot hole and slot | Ø8.5; slot 8.5 × 14 | set on the drawing | — | pin gauge Ø8.5; slot gauge | DECIDED (D-64) | | PLANNED | |
| K-J04 | `211xxx` `411xxx` `1111xx` `1112xx` | Rivnut hole | Ø9.53 | +0.10 / 0 | — | pin gauges | source (maker's data, joints register H-03) | | PLANNED | |
| K-J05 | `211xxx` `411xxx` `1111xx` `1112xx` | Frame flatness at a joint face | 0 | ±0.5 over a seam | the joint face | straightedge and feeler gauge | assumption (joints register 2.7; the frame drawings set it with the maker's capability) | | PLANNED | |
| K-J06 | `211xxx` `411xxx` | Tube wall: perimeter members 1.2, wall panels' inner studs 1.0, ceiling cross members 1.2 | 1.2 / 1.0 | to the profile standard (unverified) | — | wall-thickness micrometer on a cut sample | DECIDED (D-54, D-85) | | PLANNED | |
| K-J07 | `831001` | Locating spigot diameter and stand | Ø8; 8 proud | set on the drawing | the rivnut face | micrometer; height gauge | PROPOSED sizes (joints register H-05, assumption) | | PLANNED | |
| K-J08 | `831002` | Stop washer thickness | 1.5 | ±0.05 | — | micrometer | PROPOSED part; assumption tolerance (joints register H-08) | | PLANNED | |
| K-J09 | `210xxx` `410xxx` | Seam gap at a stopped seam, assembled | 2.26 | 2.13–2.39 | — | feeler gauges | DECIDED (D-64); calculation (the stop's tolerance, joints register 2.8) | | PLANNED | |
| K-J10 | `210xxx` `410xxx` | Closing gap at B1–B2, B3–B4 and C1–C2, assembled | 5.5 | ±0.3 (5.2–5.8) | — | feeler or taper gauge | DECIDED (D-65); calculation (stacks ST-02 and ST-04) | | PLANNED | |
| K-J11 | `848001` | Gasket squeeze at a stopped seam (free thickness 3.97) | 43% | 33–51% | — | micrometer on the free strip, then the seam gap | calculation (joints register 2.8) | | PLANNED | |
| K-J12 | `210xxx` `410xxx` | Fit-up force per edge, without scraping a seal | — | ≤ 150 | — | push-pull force gauge on the panel edge | source (joints register J-T3, J-T5, HOLD-12) | | PLANNED | |
| K-J13 | `838001` `838002` | Bolt thread past the rivnut's far end | 2.28 | ≥ 1.9 | — | depth gauge on a coupon | calculation (joints register 2.2; length tolerance js15, unverified) | | PLANNED | |
| K-J14 | `838004` | A head washer under every bolt head | 1 per bolt | — | — | visual count | DECIDED (D-63) | | PLANNED | |

## B. Outer panels and skins

| ID | Applies to | Characteristic | Nominal | Limits | Datum | Method and gauge | Source and status | Result | Conclusion | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| K-P01 | `210xxx` | Outer panel size: side panels 1492.74 × 1142.74; back panels 1200.61 × 1118.61, frames 1198.99 wide at the closing seams | as stated; 46 thick | set on the drawing | the panel's spigot hole | steel tape and caliper; height gauge for the thickness | calculation (skeleton P04, PRs #24 and #58; D-66) | | PLANNED | |
| K-P02 | `410xxx` | Ceiling half size | 1200.61 × 1495 × 46 | set on the drawing | the spigot hole | steel tape and caliper | calculation (skeleton P04; D-66) | | PLANNED | |
| K-P03 | `2113xx` `4113xx` | ACP skin bonded flat: bond line 3, skin flatness | 3 | flatness set with the bond spec | — | straightedge and feeler; the bond spec's T09 coupons | DECIDED (D-66); source (bond spec, sample test T09) | | PLANNED | |
| K-P04 | `2113xx` `4113xx` | Skin colour Dark Yellow EV3038 | EV3038 | match the approved sample | — | visual, against the sample, under daylight | DECIDED (D-12) | | PLANNED | |
| K-P05 | `2115xx` `5133xx` | Cavity fill density | 24 | the maker's data | — | weigh a cut piece and measure it | DECIDED (D-81), the wall sample's T02 confirms | | PLANNED | |

## C. Lining cassettes

| ID | Applies to | Characteristic | Nominal | Limits | Datum | Method and gauge | Source and status | Result | Conclusion | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| K-L01 | `5111xx` `5131xx` | Tray: 0.5 mm galvanised steel, 34 mm returns, 12 mm lips | 0.5; 34; 12 | sheet to its standard (unverified); returns and lips set on the drawing | — | micrometer; caliper | DECIDED (D-37, D-69) | | PLANNED | |
| K-L02 | `5111xx` `5131xx` | Inside bend radius and flat-pattern size | from the CAD flat pattern | set on the drawing | — | radius gauge; tape on the flat blank | source (the team's sheet-metal model; CEILING's flat pattern matches its bend calculation to 0.01, PR #32) | | PLANNED | |
| K-L03 | `510xxx` | Cassette size: wall cassettes per skeleton P04; ceiling cassette 1160 × 1045 | as stated; 34 thick | set on the drawing | — | steel tape and caliper | calculation (skeleton P04; D-77) | | PLANNED | |
| K-L04 | `5113xx` `5132xx` | Felt 9 mm, 1.8 kg/m², Dark Gray | 9; 1.8 | the maker's data | — | caliper; scale on a cut piece; colour against the sample | DECIDED (D-17, D-79); unverified (felt data, ISS-075) | | PLANNED | |
| K-L05 | `518001` `518002` | Clip and catch hold: wall clip 7.7 kg in shear, ceiling clip 8.0 kg in pull-out, catch lanyard 48 kg | as stated | ≥ | — | pull test (T07) and drop test (T08) | calculation, safety factor 3 an assumption (ISS-076); HOLD | | PLANNED | |

## D. Front

| ID | Applies to | Characteristic | Nominal | Limits | Datum | Method and gauge | Source and status | Result | Conclusion | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| K-F01 | `361001` `361003` | Glass: 4+4 laminate of toughened, heat-soaked panes | 8.76 | the glass standard (supplier) | — | micrometer; the toughening and heat-soak certificates | DECIDED (D-46, D-82); product HOLD (ISS-074) | | PLANNED | |
| K-F02 | `361001` `361003` | Glass outline against its DXF (door trapezoid 1175 × 893 × 2011; fixed pentagon) | the DXF | set on the drawing | the bottom edge | full-size template or tape against the DXF | source (v1 STEP outline via skeleton P04) | | PLANNED | |
| K-F03 | `360002` | Fixed glass free edge to the door: gap, parallel | 4.0 | set on the drawing | the door's edge | feeler gauges at the top, middle and bottom | DECIDED (D-68, D-74); PR #28 measured 4.00 in CAD | | PLANNED | |
| K-F04 | `360002` | Glass depth in its channels | 11.5 | set on the drawing | — | depth gauge before glazing | DECIDED (D-68) | | PLANNED | |
| K-F05 | `361002` | Kick strip running gap over the threshold | 7 | ±0.5 (the mechanical check's rule) | the threshold | feeler gauges | DECIDED (D-66, D-72) | | PLANNED | |
| K-F06 | `361002` `110xxx` `1111xx` | Black anodised, matte (kick strip and every base band piece) | ≥ 20 µm | class AA20 (EN ISO 7599) | — | eddy-current coating thickness gauge; visual against the sample | DECIDED (D-67) | | PLANNED | |
| K-F07 | `360001` | Door unit mass, as hung | 50.2 | weigh; the hardware is rated ≥ 60 kg | — | scale | calculation (PR #27); DECIDED rating (D-68) | | PLANNED | |
| K-F08 | `360001` | Door keep: magnetic catch in DT holds the door | 35 N | ≥ | — | push-pull gauge at the latch corner | DECIDED (D-83); product to be named | | PLANNED | |

## E. Base

| ID | Applies to | Characteristic | Nominal | Limits | Datum | Method and gauge | Source and status | Result | Conclusion | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| K-B01 | `110xxx` `1111xx` | Base band wall 1.5, with a load block at each glide | 1.5 | the profile standard (unverified) | — | caliper; check each block is in | DECIDED (D-86) | | PLANNED | |
| K-B02 | `1114xx` | Floor panel: 9 mm poplar-core ply with a hard face, 1210 × 1455 | 9; 1210 × 1455 | set on the drawing | the band's inner face | caliper; steel tape | DECIDED (D-85, D-86); calculation (skeleton P04) | | PLANNED | |
| K-B03 | `1114xx` | Panel edge and half-lap seam under 1000 N on the foam | — | ≤ 1 deflection | the room floor | dial gauge under a 1000 N load; castor rolled over the edge | assumption until tested (D-76); calculation about 0.6 (D-86) | | PLANNED | |
| K-B04 | `1115xx` | Floor foam: 3 mm firm closed-cell, about 200 kg/m³, bonded under the panel | 3 | the maker's data | — | caliper; check the bond | DECIDED (D-76, D-87); product HOLD (ISS-085) | | PLANNED | |
| K-B05 | `110000` | Door threshold (BASE assembly until the profile has its own number): 13 high, a 6 mm upright, then a 1:2 bevel | 13; 6; 1:2 | set on the drawing | the room floor | height gauge; angle gauge | DECIDED (D-72) | | PLANNED | |
| K-B06 | `110000` | Intake mesh band piece under the right decor block (BASE assembly until it has its own number): free area | 0.028 m² | ≥ | — | measure the open area | DECIDED (D-62) | | PLANNED | |
| K-B07 | `118001` | Base seal at the floor's edge, against the band's inner face | 4 gap | sealed | — | feeler gauge; light test | DECIDED (D-86) | | PLANNED | |

## F. Air, electrical and interior

| ID | Applies to | Characteristic | Nominal | Limits | Datum | Method and gauge | Source and status | Result | Conclusion | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| K-A01 | `61xxxx` | Cartridge: 173 × 314 × 1750, two 80 mm passages between three 50 mm layers | as stated | set on the drawing | — | steel tape and caliper | calculation (D-61, air report 7e) | | PLANNED | |
| K-A02 | `61xxxx` `81xxxx` | Air column 217 × 360 × 2105 and soffit 2332 × 360 × 220 | as stated | set on the drawing | the pod's inside corner | steel tape | calculation (D-61, air report 7e, skeleton P04) | | PLANNED | |
| K-A03 | `61xxxx` | Each shipped air piece ≤ 20 kg (soffit with its fan box about 13.9; riser with the supply fan box about 14.9) | ≤ 20 | — | — | scale | DECIDED (D-03, D-87); calculation | | PLANNED | |
| K-E01 | `71xxxx` | Harness tested at the factory; the hub's self-test passes | pass | — | — | the self-test log | DECIDED (D-87) | | PLANNED | |
| K-I01 | `81xxxx` | Light shelf within 0.4 kg/m; the 1000 mm ledge in 1.5 mm folded aluminium | 0.4; 1.5 | set on the drawing | — | scale; caliper | DECIDED (D-85) | | PLANNED | |

## G. Functional checks on the first pod

| ID | Check | Pass mark | Method and gauge | Source and status | Result | Conclusion | Evidence |
|---|---|---|---|---|---|---|---|
| F-01 | The door swings outward to 90° and clears the soffit (door top Z 2116, soffit underside Z 2120) | no contact | swing the door; feeler at the top | calculation (air report 7e); the mechanical check's swing sweep | | PLANNED | |
| F-02 | The door closes and stays shut: the 35 N catch, the drop seal on the threshold, the magnetic seal pair on the glass edge | closed, no gap | visual; light test from inside | DECIDED (D-40, D-83) | | PLANNED | |
| F-03 | Every seam and seal: no light through any joint | no light | lamp inside, room dark | confirmed (REQ-SND-02) | | PLANNED | |
| F-04 | Fans: 53 l/s at 26 dB(A) or less and the 65 l/s boost at 30 dB(A) or less, at seated ear height | as stated | flow hood; sound level meter | DECIDED (D-52); calculation (25.3 and 29.7 dB(A), D-62); the fan sample test T04 | | PLANNED | |
| F-05 | Control: fans start on presence; CO2 and the 4 K limit drive the flow; boost by hand | as stated | logged readings over a session | DECIDED (D-44, D-50) | | PLANNED | |
| F-06 | The hub's self-test button runs and passes | pass | press it; read the log | DECIDED (D-87) | | PLANNED | |
| F-07 | Lights: the light shelf scenes, including a 'call' scene that lights the face from the screen side | as stated | visual | DECIDED (D-70) | | PLANNED | |
| F-08 | Assembly: two people, one 5 mm key, every piece but the glass 20 kg or less | about 126 min; never over 4 h | timed trial with the guide | DECIDED (D-03, D-63, D-87); calculation (the guide) | | PLANNED | |
| F-09 | Mass as shipped | the live count | weigh every piece | calculation (the layout study's live count) | | PLANNED | |
| F-10 | Sound: speech level reduction to ISO 23351-1 | the measured figure; about 19 dB calculated | lab, after the wall sample's T01 from 100 Hz | DECIDED (D-53); calculation | | PLANNED | |

## How this plan grows

- When a part's drawing lands, its characteristics move onto the drawing with these IDs, and new ones get the next free ID in their section.
- When a test or a first article is measured, the result, conclusion and evidence columns fill in (the measured value, the sample number, the gauge's calibration, the date and the file). Only then can a line say PASS.
- The release checklist re-reads this file to show which parts have characteristics.
