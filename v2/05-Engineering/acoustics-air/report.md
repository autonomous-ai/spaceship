# Spaceship sound and fresh-air check

Spaceship is the working name for FocusPod v2 ("Indoor Pod").

- **Status:** calculation, not a test. Every number below comes from `calc.py` in this folder, and every input there carries its own status and source. Bought-part data and links are in [`../hardware/selection.md`](../hardware/selection.md).
- **Date:** 2026-10-31.
- **Rerun:** `python3 calc.py` prints every table in this report. `python3 calc.py --verify` rebuilds them and checks that this file quotes each one exactly.
- **Decisions:** DECIDED means the PM ruled on it on 2026-10-31. Decision IDs (D-xx) refer to `v2/00-Control/decision-log.md`; the other rulings were made in the project chat and are being logged. PROPOSED means it still needs a call. HOLD means a supplier or a sample has to confirm it.

## Results first

1. **v1 as built is predicted at about 15 dB speech reduction (D_S,A, range 12–18), not the 30 dB on the product page.** Its open vent slots (35%), door gaps (33%) and raised floor (14%) let out most of the sound, and its bare wood interior adds to it. v1's lab test will settle this.
2. **Spaceship as planned comes out at about 19 dB (16–22).** That's already above v1, mostly because of the felt lining. The light fixes take it to about 21 dB: perimeter and drop seals, sealed glass, joint gaskets, silenced vents, and the thin floor with a base seal. After that, the walls and ceiling carry about 90% of the sound that gets out.
3. **DECIDED build: about 414 kg in this model, 24.0 dB (21.5–26.5).** The PM's figure with Layout's clips is about 418 kg, under the 420 kg cap.
   - Walls and ceiling: ACP 3 mm on a 20×40×1.2 aluminium frame at 400 mm, 40 mm PET fill, and a floating lining cassette (0.5 mm steel tray, 25 mm air gap, 9 mm felt).
   - Front: 4+4 acoustic laminated glass, frameless like v1.
   - Air: fans and splitter silencers inside the hollow front decor blocks.
   - Smoked acrylic is now only an optional experiment on the factory sample: 23.7 dB at about 387 kg.
4. **30 dB isn't reached anywhere in this search, up to 520 kg (best about 26 dB).** Each extra dB costs about 25–40 kg of wall. What limits a light pod is low voices (125–250 Hz). Only mass, cavity depth and low-frequency absorption help there.
5. **Air (DECIDED):**
   - 53 l/s normal at 25 dB(A) or less, which is the published figure.
   - 70 l/s boost at about 31 dB(A). The CO2 reading triggers it automatically, or people trigger it by hand.
   - At 53 l/s, two people stay at or under 800 ppm even in a 600 ppm office, and the pod runs 3.6 °C over the room.
   - Heat, more than CO2, is why the flow is this high: at 26 l/s the pod would run about 7 °C warm.
6. **Correction to an earlier figure:** my first fan-noise result (24 dB(A) at 70 l/s) left out sound breaking out through the silencer's thin walls. That breakout is why the silencers now sit outside the pod's sound shell, inside the decor blocks, with 2 mm aluminium casings and 37.5 mm linings. The plan's Panasonic FV-15AUL1 can't be used: its manual forbids ceiling mounting, and it has no published fan curve.

## 1. The DECIDED stack, for the Layout and Fusion Engineers

Outside to inside. DECIDED by the PM on 2026-10-31 (D-02 weight and sound target, D-05 thin floor, D-07 front, D-09 air, plus rulings in the project chat):
- aluminium frames at 400 mm, 20 × 40 × 1.2 (the rivnut grip check passed);
- no plywood behind the ACP;
- 0.5 mm lining tray (0.4 mm would cost 1 dB);
- fill at 32 kg/m³ (the lighter 24–25 kg/m³ grade has no published absorption data);
- 4+4 laminated front;
- fans and silencers in the decor blocks;
- dormakaba OFFICE 11.233 hinges;
- decor depth from v1's real geometry, 230–235 mm;
- cap 420 kg.

**Walls and ceiling (vách, trần), 81 mm, 12.6 kg/m² including frame and felt**

| # | Layer (Vietnamese name) | mm | kg/m² | Status and source |
|---|---|---:|---:|---|
| 1 | ACP skin, Alcorest EV3038 Dark Yellow, 3 × 0.21 mm skins, PE core (tấm ốp alu VT01) | 3 | 3.5 | calculation from the maker's skin spec; the maker publishes no kg/m² (selection.md VT01) |
| 2 | Bond, ACP to frame: SikaTack Panel-50 system or equivalent, factory only (keo dán) | — | ~0.1, not in total | source for substrates (selection.md glue row); bond pattern HOLD for a coupon test |
| 3 | Aluminium frame 20 × 40 × 1.2 mm, members at 400 mm (khung nhôm) | 40 | 1.9 | calculation: 0.373 kg/m × 5.0 m of tube per m² |
| 4 | Polyester fill between members, Pyrotek Sorberpoly 2D 32 kg/m³ or equal (bông PET) | (40) | 1.3 | source for the product and its absorption (selection.md B) |
| 5 | Resilient gap: perimeter gasket PORON 4701-40, 3.2 mm, plus hook-and-loop pads; no screws through (gioăng) | 3 | ~0.1, not in total | source for the gasket (selection.md); decoupling is a calculation assumption, HOLD for the wall-sample test |
| 6 | Lining cassette: galvanised steel 0.5 mm tray with 25 mm returns (khay thép lót) | 0.5 | 4.2 | calculation: 3.93 kg/m² sheet + 0.26 kg/m² returns |
| 7 | Air gap inside the cassette (spare cable path) | 25 | — | calculation: this gap lets the felt absorb at 250–500 Hz |
| 8 | PET felt 9 mm, Dark Gray, on the cassette face (tấm tiêu âm PET VT03); the factory's felt, tested in the wall sample first (DECIDED) | 9 | 1.8 | source for 9 mm at 1.8 kg/m² (Polyx Board 9, layout study S11); absorption data from Autex Cube (proxy) |
| | **Total** | **81** | **12.6** | the outer panel (layers 1–4) and the lining cassette (5–8) ship as separate parts |

**Part weights for the 20 kg rule** (calculation):

| Part | Size, mm | kg |
|---|---|---:|
| Side-wall outer panel | 1500 × 1145 | 11.4 |
| Lining cassette for it | — | 10.3 |
| Ceiling half outer panel | 1212 × 1500 | 12.1 |
| Supply silencer cartridge | — | 19.6 |
| Exhaust silencer cartridge | — | 10.2 |
| Each fan | — | 6.0 |
| Door (4+4) | — | about 50, glass is exempt |

The inside ends up about 2338 × 1460 × 2301 mm: about 3 cm narrower and shallower than v1 (2372 × 1480), and 8 cm taller (2223).

**Why this stack.** Inside the decided rules, it's the quietest at the cap (section 6). It uses one lining material, galvanised steel: no formaldehyde, fire class A1, and a smooth face behind the felt. The steel tray stiffens itself through its returns, and the floating cassette never touches the frame through a screw. The 25 mm gap behind the felt is worth about 2 dB at 250–500 Hz, where felt fixed flat on a board absorbs too little.

## 2. Wall, ceiling and floor build-ups compared

R by octave band from the Sharp model (single and double leaf, stud bridging, a finite-panel correction below 500 Hz). R speech is the A-weighted reduction of a standard speech spectrum through the element alone. kg/m² includes frame, fill and felt.

| Key | Build, outside / cavity / inside | kg/m2 with frame | mm | 125 | 250 | 500 | 1k | 2k | 4k | R speech |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V1-DWG | v1 as drawn: Al 2 + ply 6 / 40 empty, wood studs / ply 15 | 21.0 | 63 | 23 | 27 | 38 | 32 | 35 | 44 | 33.6 |
| V1-BOM | v1 per BOM: Al 2 + ply 6 / 40 empty, wood studs / ply 9 | 17.4 | 57 | 21 | 25 | 34 | 41 | 34 | 40 | 32.9 |
| PLAN | Plan: ACP 3 + ply 6 / 20 steel frame, empty / felt 9 | 11.1 | 38 | 16 | 20 | 24 | 28 | 20 | 25 | 23.8 |
| PLAN-NOPLY | Plan without plywood: ACP 3 / 20 / felt 9 | 7.5 | 32 | 9 | 13 | 18 | 24 | 29 | 21 | 18.7 |
| SW-HC10 | Sandwich: ACP-faced Al honeycomb 10 / felt 9 | 6.5 | 19 | 9 | 13 | 15 | 11 | 14 | 21 | 13.1 |
| SW-HC20 | Sandwich: Al honeycomb 20 / felt 9 | 7.1 | 29 | 10 | 12 | 8 | 11 | 18 | 25 | 9.6 |
| SW-FOAM20 | Sandwich: Al-faced foam core 20 / felt 9 | 6.8 | 29 | 9 | 13 | 18 | 23 | 28 | 32 | 18.6 |
| SW-FOAM20-DL | Foam core 20 / 30 fill, shared studs / HDF 3 + felt 9 | 11.2 | 62 | 14 | 18 | 26 | 43 | 50 | 55 | 26.0 |
| DL-HDF | ACP 3 / 40 fill, shared studs / HDF 3 + felt 9 | 11.6 | 55 | 14 | 18 | 29 | 40 | 44 | 37 | 27.2 |
| DL-PLY4 | ACP 3 / 40 fill, shared studs / ply 4 + felt 9 | 11.3 | 56 | 14 | 18 | 28 | 38 | 42 | 34 | 26.4 |
| DL-HDF-DEC | ACP 3 / 40 fill / HDF 3 on resilient pads + felt 9 | 11.6 | 58 | 14 | 18 | 29 | 45 | 52 | 44 | 27.3 |
| DL-ST | ACP 3 / 40 fill, shared studs / steel 0.5 + felt 9 | 12.8 | 53 | 16 | 20 | 32 | 43 | 48 | 39 | 29.5 |
| DL-ST-DEC | ACP 3 / 40 fill / steel 0.5 on resilient pads + felt 9 | 12.8 | 56 | 16 | 20 | 32 | 49 | 56 | 47 | 29.6 |
| DL-P6-PLY4 | ACP 3 + ply 6 / 40 fill, shared studs / ply 4 + felt 9 | 14.9 | 62 | 18 | 22 | 30 | 34 | 26 | 32 | 28.9 |
| DL-HDF-60 | ACP 3 / 60 fill, shared studs / HDF 3 + felt 9 | 13.0 | 75 | 14 | 19 | 32 | 40 | 44 | 37 | 28.5 |
| DL-HDF-40-FL | ACP 3 / 40 fill / HDF 3 floating (no stud bridge) + felt 9 | 11.6 | 55 | 14 | 18 | 29 | 46 | 62 | 61 | 27.3 |
| DL-HDF-60-FL | ACP 3 / 60 fill / HDF 3 floating + felt 9 | 13.0 | 75 | 14 | 19 | 32 | 49 | 62 | 61 | 28.7 |
| DL-ST-40-FL | ACP 3 / 40 fill / steel 0.5 floating + felt 9 | 12.8 | 53 | 16 | 20 | 32 | 49 | 65 | 64 | 29.6 |
| DL-ST-60-FL | ACP 3 / 60 fill / steel 0.5 floating + felt 9 | 14.3 | 73 | 16 | 21 | 36 | 53 | 65 | 64 | 30.9 |
| DL-2HDF-60-FL | ACP 3 / 60 fill / 2 x HDF 3 floating + felt 9 | 15.7 | 78 | 18 | 23 | 38 | 55 | 68 | 53 | 33.0 |
| DL-P6-HDF-60-FL | ACP 3 + ply 6 / 60 fill / HDF 3 floating + felt 9 | 16.6 | 81 | 18 | 24 | 38 | 55 | 54 | 64 | 33.6 |
| DL-P6-P9-60-FL | ACP 3 + ply 6 / 60 fill / ply 9 floating + felt 9 | 19.3 | 87 | 20 | 28 | 44 | 57 | 45 | 55 | 37.6 |
| DL-ST-100-FL | ACP 3 / 100 fill / steel 0.5 floating + felt 9 | 17.2 | 113 | 16 | 23 | 40 | 54 | 65 | 64 | 33.2 |
| DL-AL1-60-FL | ACP 3 / 60 fill / aluminium 1.0 floating + felt 9 | 13.0 | 73 | 14 | 19 | 32 | 49 | 62 | 61 | 28.7 |
| DL-AL1-100-FL | ACP 3 / 100 fill / aluminium 1.0 floating + felt 9 | 15.9 | 113 | 14 | 20 | 37 | 50 | 62 | 61 | 30.5 |
| DL-ST-40-FLG | ACP 3 / 40 fill / floating cassette: steel 0.5 tray, 25 air, felt 9 | 13.1 | 81 | 16 | 20 | 32 | 49 | 65 | 64 | 29.6 |
| DL-ST-40-FLG-12 | ACP 3 / 20x40x1.2 frame, 40 fill / floating cassette: steel 0.5 tray, 25 air, felt 9 | 12.6 | 81 | 16 | 20 | 32 | 49 | 65 | 64 | 29.6 |
| DL-ST4-40-FLG-12 | ACP 3 / 20x40x1.2 frame, 40 fill / floating cassette: steel 0.4 tray, 25 air, felt 9 | 11.8 | 81 | 15 | 19 | 30 | 47 | 63 | 62 | 28.2 |
| DL-ST-100-FLG | ACP 3 / 100 fill / floating cassette: steel 0.5 tray, 25 air, felt 9 | 17.4 | 141 | 16 | 23 | 40 | 54 | 65 | 64 | 33.2 |
| DL-HDF-100-DEC | ACP 3 / 100 fill / HDF 3 on resilient pads + felt 9 | 15.9 | 115 | 14 | 20 | 37 | 47 | 52 | 44 | 30.4 |
| DL-ST-100-DEC | ACP 3 / 100 fill / steel 0.5 on resilient pads + felt 9 | 17.2 | 113 | 16 | 23 | 40 | 51 | 56 | 47 | 33.1 |
| DL-P6-P9-DEC | ACP 3 + ply 6 / 40 fill / ply 9 on resilient pads + felt 9 | 17.9 | 67 | 20 | 26 | 39 | 42 | 35 | 41 | 34.8 |
| DL-P6-P9-100-DEC | ACP 3 + ply 6 / 100 fill / ply 9 on resilient pads + felt 9 | 22.2 | 127 | 21 | 32 | 39 | 42 | 35 | 41 | 37.2 |
| DL-2HDF-100-DEC | ACP 3 / 100 fill / 2 x HDF 3 on resilient pads + felt 9 | 18.6 | 118 | 18 | 26 | 42 | 49 | 54 | 46 | 35.5 |

What it shows:
- **v1's wall is a good wall** (R speech 33–34). It has two heavy leaves on a 40 mm cavity. Its pod still leaks, through the vents and gaps.
- **The plan's wall is effectively a single leaf** (ACP + ply bonded, R speech 24). PET felt absorbs but barely blocks sound, so it counts for absorption only.
- **Dropping the plywood with nothing in its place costs about 5 dB** on the wall (19 against 24).
- **Honeycomb sandwich panels are poor sound barriers** (R speech 10–13). Their stiff cores put the coincidence dip at 450–950 Hz, right in the speech band. Foam-core sandwiches, with soft cores, behave like plain mass (19), so they're light but weak too. Either only works as the outer leaf of a double wall.
- **Two thin leaves with fill, decoupled, are the light answer.** At 13 kg/m², the floating steel lining beats the plan's 11 kg/m² wall by about 6 dB. The 100 mm versions reach v1's wall at 17–18 kg/m².

Matching v1's wall alone, element for element, would cost 16–17 kg/m² (about 250–270 kg of walls and ceiling):

| Target (wall element only) | Lightest build that reaches it | kg/m2 | mm | R speech | Walls + ceiling kg |
|---|---|---:|---:|---:|---:|
| V1-BOM (32.9) | DL-2HDF-60-FL: ACP 3 / 60 fill / 2 x HDF 3 floating + felt 9 | 15.7 | 78 | 33.0 | 251 |
| V1-DWG (33.6) | DL-P6-HDF-60-FL: ACP 3 + ply 6 / 60 fill / HDF 3 floating + felt 9 | 16.6 | 81 | 33.6 | 266 |

**Floor.** The thin floor (DECIDED, D-05) sits on the room's slab, so sound doesn't get out through it. Only its edge joint counts, and the base seal closes that. The plan's raised floor lets sound out through 15 mm boards over an open frame: 14% of what leaves v1.

## 3. The front: glass against acrylic

Glass values are measured lab data from the PVB maker's acoustic booklet (Eastman, 1/3-octave, tests TR16-105/106/269). Acrylic is modelled, because the only published PMMA figures contradict each other (selection.md).

| Key | Front pane | kg/m2 | Door kg | Door + fixed kg | 125 | 250 | 500 | 1k | 2k | 4k | R speech | Basis |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| G8 | Tempered 8 mm | 20.0 | 47 | 68 | 29 | 29 | 32 | 33 | 33 | 41 | 32.4 | measured, lab (Eastman via HW) |
| G10 | Tempered 10 mm (v1) | 25.0 | 59 | 86 | 28 | 31 | 33 | 33 | 35 | 44 | 33.0 | measured, lab (Eastman via HW) |
| L44 | Laminated acoustic 4+4 (8.76 mm) | 21.0 | 50 | 72 | 29 | 30 | 33 | 37 | 39 | 42 | 33.6 | measured, lab (Eastman via HW) |
| A8 | Smoked acrylic 8 mm | 9.5 | 22 | 33 | 18 | 22 | 27 | 32 | 38 | 33 | 27.4 | model (Sharp) |
| A10 | Smoked acrylic 10 mm | 11.9 | 28 | 41 | 20 | 24 | 29 | 34 | 37 | 33 | 29.3 | model (Sharp) |
| A12 | Smoked acrylic 12 mm | 14.3 | 34 | 49 | 22 | 26 | 30 | 36 | 35 | 33 | 30.8 | model (Sharp) |

Effect in the DECIDED pod (all else equal):

| Front pane (door + fixed) | kg | D_S,A low | central | high | vs 8 mm |
|---|---:|---:|---:|---:|---:|
| Tempered 8 mm | 68 | 21.4 | 24.0 | 26.4 | +0.0 |
| Tempered 10 mm (v1) | 86 | 21.5 | 24.0 | 26.5 | +0.0 |
| Laminated acoustic 4+4 (8.76 mm) | 72 | 21.5 | 24.0 | 26.5 | +0.0 |
| Smoked acrylic 8 mm | 33 | 20.9 | 23.4 | 25.9 | -0.6 |
| Smoked acrylic 10 mm | 41 | 21.2 | 23.7 | 26.1 | -0.3 |
| Smoked acrylic 12 mm | 49 | 21.3 | 23.8 | 26.3 | -0.2 |

- **DECIDED front: 4+4 acoustic laminated glass**, frameless like v1. It's the quietest pane, and in this pod 0.3 dB better than acrylic.
  - Acrylic would save about 27 kg, but on hinges rated for glass it needs an 80 mm opaque aluminium stile down the hinge edge. That breaks the look rule (D-01).
  - Acrylic also brings creep, scratch, fire-class and flatness risks.
  - It stays as an optional experiment on the factory sample.
- **Scratches:** cast acrylic is pencil hardness 3H (ACRYLITE cast), far softer than glass. Plan a hard-coated sheet, or accept wear on the door face. The factory sample decides.
- **Look:** the grey cast sheet is Perspex Neutral 9T56, 46% light transmission at 3 mm. The value at 10 mm isn't published (darker), so the sample decides the match with v1's smoked glass.
- **Fire, for later US rules:** PMMA is Euroclass E / UL 94 HB, while glass is A1 and PVB laminate is "no performance declared". A 2.4 m² acrylic door may be a problem for US interior-finish rules later. That's the main reason to keep the glass fallback ready.
- **Hinges:** dormakaba OFFICE 11.233 clamps the 4+4 laminate directly (rated 70 kg and 1200 mm; the door is about 50 kg). The acrylic experiment's hinge-edge stile is detailed in selection.md C9.

## 4. The whole pod: predicted speech reduction

D_S,A is the ISO 23351-1 single number: the reduction in A-weighted sound power of standard speech, measured in a reverberation room. Here it's estimated from an energy balance inside the pod: IL = 10 lg(1 + A_in / Σ Sτ) per octave, then weighted with the speech spectrum. "low / high" combine pessimistic and optimistic values of the uncertain inputs: gap widths, seal quality, silencer performance, ±2 dB on every element, and ±15% absorption.

| Pod | D_S,A low | central | high |
|---|---:|---:|---:|
| v1 as drawn (inner ply 15) | 11.6 | 14.9 | 18.3 |
| v1 per BOM (inner ply 9) | 11.6 | 14.9 | 18.4 |
| Spaceship as planned (10 mm glass) | 15.8 | 18.7 | 21.6 |
| Spaceship as planned, 8 mm glass | 15.7 | 18.7 | 21.5 |
| + all light fixes (plan wall) | 18.2 | 20.8 | 23.2 |
| + fixes, plan wall without plywood | 13.4 | 15.8 | 18.2 |
| + fixes, light double wall DL-HDF | 17.0 | 19.3 | 21.7 |
| + fixes, DL-HDF decoupled | 17.0 | 19.4 | 21.8 |
| + fixes, DL-ST (steel 0.5 inner skin) | 18.5 | 21.0 | 23.4 |
| + fixes, DL-ST decoupled | 18.5 | 21.0 | 23.4 |
| + fixes, honeycomb sandwich SW-HC20 | 6.4 | 8.5 | 10.7 |
| + fixes, foam sandwich + inner skin | 16.3 | 18.7 | 21.1 |
| DECIDED stack, 4+4 laminated front | 21.5 | 24.0 | 26.5 |
| DECIDED stack with the acrylic experiment | 21.2 | 23.7 | 26.1 |

Where the sound gets out (share of the speech energy, central case):

| Path (share of speech sound getting out) | v1 | Plan, 8 mm | Plan + fixes | DECIDED stack |
|---|---:|---:|---:|---:|
| walls | 6% | 41% | 70% | 63% |
| ceiling | 2% | 12% | 20% | 18% |
| glass | 2% | 1% | 2% | 4% |
| front decor | 2% | 3% | 5% | 12% |
| floor | 14% | 6% | 0% | 0% |
| door edge gaps | 22% | 12% | 0% | 0% |
| door bottom | 11% | 6% | 0% | 0% |
| fixed glass edges | 1% | 1% | 0% | 0% |
| panel joints | 5% | 3% | 0% | 0% |
| vents | 35% | 13% | 1% | 3% |
| cable holes | 1% | 0% | 0% | 0% |

The weak points move as the pod improves:
- In **v1** the vents and the door gaps dominate.
- In the **plan as drawn** the single-leaf walls dominate, then the door gaps and vents.
- With **seals and silencers** the walls and ceiling carry about 90%.
- In the **DECIDED pod** the front decor becomes visible (12%), because its faces are single 3 mm ACP over a hollow block, and the 4+4 glass is only 4%. If the wall sample tests better than calculated, the next step is the decor faces (felt lining or added mass), not the glass.

**Cable holes and panel joints are small once sealed.** An unsealed cable opening of 600 mm² (about one 28 mm hole) costs about 0.1 dB in the DECIDED pod. Unsealed panel joints at 0.15 mm cost about 0.2 dB in the plan pod and 0.5 dB in the DECIDED pod, so gaskets go on every joint. Leaving out the door seals would cost the DECIDED pod 2.2 dB, and open vents 1.7 dB.

## 5. Light fixes, with dB and kg

Applied one after another to the plan with 8 mm glass. kg is the added mass for the whole pod (calculation; sources in calc.py).

| Step | Change | D_S,A low | central | high | Gain (central) | kg added |
|---|---|---:|---:|---:|---:|---:|
| 0 | Spaceship as planned, 8 mm glass | 15.7 | 18.7 | 21.5 |  |  |
| 1 | Door edge seals on 3 sides | 16.2 | 19.2 | 22.1 | +0.5 | 1.0 |
| 2 | Door drop seal | 16.4 | 19.5 | 22.4 | +0.3 | 1.0 |
| 3 | Fixed glass in sealed U-profiles | 16.4 | 19.6 | 22.5 | +0.0 | 0.0 |
| 4 | Gaskets on every panel joint | 16.6 | 19.7 | 22.6 | +0.2 | 1.0 |
| 5 | Silenced vents (splitter silencers in the decor blocks) | 17.5 | 20.5 | 23.2 | +0.8 | 26.8 |
| 6 | Thin floor with base seal (DECIDED, D-05) | 18.2 | 20.7 | 23.2 | +0.2 | 0.5 |
| 7 | Sealed cable holes | 18.2 | 20.8 | 23.2 | +0.0 | 0.1 |

The gains are small one at a time because the plan's single-leaf walls dominate. The same fixes on v1's leaky pod would gain about 6 dB, so they matter as soon as the walls are double. A thick ceiling absorber was also tried and gained nothing over felt on a gap, so it isn't listed.

## 6. What each dB costs: the total-pod curve

Total pod kg is the sum of:
- the rest of the pod from the layout study, 102.4 kg: thin floor and base band, decor blocks, door hardware with drop seal and glazing profiles, fans at 1.5 kg, silencer boxes at 1.5 kg each, electrics and the voice-kit reserve;
- the fixes the study doesn't carry, 2.6 kg;
- the silencer cartridges beyond the study's boxes;
- the fans at 6 kg each, beyond the study's 1.5 kg;
- the walls, ceiling and front from this report.

All light fixes are on. The search covers every wall and ceiling in table 2 with each front. The PM's own total with Layout's clips is about 418 kg.

Glass front (8 mm tempered or 4+4 laminated):

| Pod budget kg | Best wall / ceiling / front | Total kg | D_S,A low / central / high |
|---:|---|---:|---|
| 280 | nothing fits |  |  |
| 300 | nothing fits |  |  |
| 320 | SW-FOAM20 / SW-FOAM20 / Tempered 8 mm | 317 | 13.4 / 15.8 / 18.1 |
| 340 | SW-FOAM20 / DL-ST4-40-FLG-12 / Tempered 8 mm | 335 | 14.2 / 16.6 / 19.0 |
| 360 | SW-FOAM20 / DL-ST-40-FLG-12 / Laminated acoustic 4+4 (8.76 mm) | 342 | 14.2 / 16.7 / 19.0 |
| 380 | DL-ST4-40-FLG-12 / SW-FOAM20 / Tempered 8 mm | 379 | 17.5 / 20.0 / 22.4 |
| 400 | DL-ST4-40-FLG-12 / DL-ST4-40-FLG-12 / Tempered 8 mm | 398 | 20.5 / 23.0 / 25.4 |
| 420 | DL-ST-40-FLG-12 / DL-ST-40-FLG-12 / Tempered 8 mm | 411 | 21.4 / 24.0 / 26.4 |
| 440 | DL-ST-40-FLG-12 / DL-ST-100-FLG / Laminated acoustic 4+4 (8.76 mm) | 432 | 21.9 / 24.4 / 26.8 |
| 460 | DL-ST-40-FLG-12 / DL-ST-100-FLG / Laminated acoustic 4+4 (8.76 mm) | 432 | 21.9 / 24.4 / 26.8 |
| 480 | DL-ST-100-FLG / DL-ST-40-FLG-12 / Tempered 8 mm | 470 | 22.9 / 25.4 / 27.8 |
| 500 | DL-ST-100-FLG / DL-P6-P9-60-FL / Laminated acoustic 4+4 (8.76 mm) | 498 | 23.4 / 26.0 / 28.4 |
| 520 | DL-ST-100-FLG / DL-P6-P9-60-FL / Laminated acoustic 4+4 (8.76 mm) | 498 | 23.4 / 26.0 / 28.4 |

Smoked acrylic 10 mm front:

| Pod budget kg | Best wall / ceiling / front | Total kg | D_S,A low / central / high |
|---:|---|---:|---|
| 280 | nothing fits |  |  |
| 300 | SW-FOAM20 / PLAN-NOPLY / Smoked acrylic 10 mm | 296 | 13.4 / 15.8 / 18.1 |
| 320 | SW-FOAM20 / DL-ST4-40-FLG-12 / Smoked acrylic 10 mm | 312 | 14.1 / 16.6 / 18.9 |
| 340 | PLAN-NOPLY / DL-ST-40-FLG-12 / Smoked acrylic 10 mm | 324 | 14.2 / 16.7 / 19.1 |
| 360 | DL-ST4-40-FLG-12 / PLAN-NOPLY / Smoked acrylic 10 mm | 358 | 17.4 / 19.9 / 22.3 |
| 380 | DL-ST4-40-FLG-12 / DL-ST-40-FLG-12 / Smoked acrylic 10 mm | 377 | 20.4 / 22.9 / 25.4 |
| 400 | DL-ST-40-FLG-12 / DL-ST-40-FLG-12 / Smoked acrylic 10 mm | 387 | 21.2 / 23.7 / 26.1 |
| 420 | DL-ST-40-FLG-12 / DL-ST-100-FLG / Smoked acrylic 10 mm | 404 | 21.5 / 24.0 / 26.5 |
| 440 | DL-ST-40-FLG-12 / DL-ST-100-FLG / Smoked acrylic 10 mm | 404 | 21.5 / 24.0 / 26.5 |
| 460 | DL-ST-100-FLG / DL-2HDF-60-FL / Smoked acrylic 10 mm | 457 | 22.5 / 25.0 / 27.5 |
| 480 | DL-ST-100-FLG / DL-ST-100-FLG / Smoked acrylic 10 mm | 464 | 22.9 / 25.4 / 27.8 |
| 500 | DL-ST-100-FLG / DL-ST-100-FLG / Smoked acrylic 10 mm | 464 | 22.9 / 25.4 / 27.8 |
| 520 | DL-ST-100-FLG / DL-ST-100-FLG / Smoked acrylic 10 mm | 464 | 22.9 / 25.4 / 27.8 |

Best builds inside the DECIDED rules:

| Case | Walls | Ceiling | Front | Silencer casing | Total kg | D_S,A low / central / high |
|---|---|---|---|---|---:|---|
| DECIDED stack | DL-ST-40-FLG-12 | DL-ST-40-FLG-12 | Laminated acoustic 4+4 (8.76 mm) | aluminium 2.0 mm | 414 | 21.5 / 24.0 / 26.5 |
| Same with 20x40x1.5 frames | DL-ST-40-FLG | DL-ST-40-FLG | Laminated acoustic 4+4 (8.76 mm) | aluminium 2.0 mm | 421 | 21.5 / 24.0 / 26.5 |
| Same with a 0.4 mm tray (rejected: costs 1 dB) | DL-ST4-40-FLG-12 | DL-ST4-40-FLG-12 | Laminated acoustic 4+4 (8.76 mm) | aluminium 2.0 mm | 401 | 20.5 / 23.0 / 25.5 |
| Same, felt flat on the ceiling lining (no gap) | DL-ST-40-FLG-12 | DL-ST-40-FL | Laminated acoustic 4+4 (8.76 mm) | aluminium 2.0 mm | 415 | 21.0 / 23.6 / 26.0 |
| Acrylic experiment: 10 mm with hinge stile | DL-ST-40-FLG-12 | DL-ST-40-FLG-12 | Smoked acrylic 10 mm | aluminium 2.0 mm | 387 | 21.2 / 23.7 / 26.1 |
| Light 0.8 mm casings (fails the noise target) | DL-ST-40-FLG-12 | DL-ST-40-FLG-12 | Laminated acoustic 4+4 (8.76 mm) | aluminium 0.8 mm | 400 | 21.5 / 24.0 / 26.5 |

- **The curve rises fastest from about 360 to 400 kg:** about 3 dB for 40 kg. Beyond 420 kg, each dB costs 30–40 kg.
- **30 dB isn't reached in this search.** At 500 kg the walls are 100 mm double leaves with plywood, and the pod still stops at about 26 dB.
- **The curve is a calculation with about ±2.5 dB of spread.** The factory's wall-and-door sample is the physical check, and it comes before any further weight goes in.

## 7. Fresh air

### 7a. CO2 and heat

Inside volume 8.35 m3; CO2 from 2 people 10.4 ml/s.

| Fresh air l/s | Air changes /h | Minutes per change | CO2 rise ppm | CO2 ppm, room 400 | CO2 ppm, room 600 | Minutes to 95% | Heat rise K | Heat rise K with voice kit |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 26 | 11 | 5.4 | 400 | 800 | 1000 | 16 | 7.4 | 9.3 |
| 40 | 17 | 3.5 | 260 | 660 | 860 | 10 | 4.8 | 6.1 |
| 53 | 23 | 2.6 | 196 | 596 | 796 | 8 | 3.6 | 4.6 |
| 70 | 30 | 2.0 | 149 | 549 | 749 | 6 | 2.8 | 3.5 |

CO2 after 2 h at 40 l/s from 400 ppm (room 400): 660 ppm; after 3 h at 26 l/s, room 600: 1000 ppm.

- 800 ppm needs 26 l/s **only when the room air is at outdoor CO2 (400 ppm)**. Real offices sit at 500–700 ppm, and at 600 ppm the pod needs about 52 l/s to stay at 800.
- **Heat sets the flow.** Two people plus laptops, lights and controls give about 234 W, and 294 W with the voice-kit reserve. At 26 l/s the pod runs about 7 °C over the room. At 70 l/s it's about 3 °C. So aim for 70 l/s, as DECIDED.
- With CO2 control alone the fans would sit at low speed while the pod gets hot. The controller needs a minimum flow when occupied (about 40 l/s) and should boost on temperature as well as on CO2.

### 7b. Fans, silencers and noise inside

Targets (DECIDED): 25 dB(A) or less at the normal 53 l/s, published, and about 31 dB(A) at the 70 l/s boost.

| Splitter (2 mm aluminium casing unless noted) | Two cartridges kg | Supply path IL 125 | 250 | 500 | 1k | 2k | 4k dB | Inside at 53 l/s dB(A) | at 70 l/s | Flow for 25 dB(A) l/s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| lining 25 mm | 27.6 | 2 | 11 | 24 | 35 | 40 | 40 | 27.3 | 33.3 | 48 |
| lining 37.5 mm (DECIDED) | 29.8 | 3 | 17 | 37 | 40 | 40 | 40 | 24.7 | 30.8 | 54 |
| lining 50 mm | 31.9 | 5 | 23 | 40 | 40 | 40 | 40 | 23.4 | 29.5 | 57 |
| lining 37.5 mm, casing aluminium 0.8 mm | 15.7 | 3 | 17 | 37 | 40 | 40 | 40 | 31.7 | 37.8 | 39 |
| lining 37.5 mm, casing steel 1.0 mm | 40.4 | 3 | 17 | 37 | 40 | 40 | 40 | 22.5 | 28.5 | 59 |

Pressure drop at 70 l/s: supply 9 Pa, exhaust 28 Pa. The 50 mm lining needs a 250 mm deep cartridge, which does not fit the decor blocks.

| Fan, 2 mm aluminium casings | Duct LwA dB(A) at its data point | Inside at 53 l/s: duct / breakout / total dB(A) | Inside at 70 l/s: duct / breakout / total | Flow for 25 dB(A) l/s |
|---|---:|---|---|---:|
| S&P TD-350/100-125 ECOWATT, 8 V (69 l/s @ 30 Pa) | 54 | 23.1 / 26.2 / 27.9 | 29.2 / 32.2 / 34.0 | 46 |
| S&P TD-500/150-160 ECOWATT, 4 V (56 l/s @ 42 Pa) (DECIDED) | 51 | 18.4 / 23.6 / 24.7 | 24.5 / 29.6 / 30.8 | 54 |

- **Breakout drives this design.** Sound leaves a silencer through its walls as well as through its end. A silencer box under the pod's ceiling, with a 0.5 mm steel face, would give about 43 dB(A) at 70 l/s. So the silencers sit outside the pod's sound shell, inside the hollow front decor blocks, next to their fans. Only the grilles open into the pod.
- **Splitter cartridges (DECIDED; fit HOLD for CAD):**
  - Construction: two 50 mm air passages between three 37.5 mm polyester layers, inside a 2 mm aluminium casing, 212 mm deep.
  - Supply: vertical in the right decor block, 212 × 500 × 2000 mm, about 19.6 kg.
  - Exhaust: horizontal in the top decor block, 212 × 280 × 1500 mm, about 10.2 kg.
  - The decor blocks follow v1's real depth (230–235 mm), which leaves room (DECIDED).
  - The 37.5 mm absorption is interpolated between Pyrotek's 25 and 50 mm data, so the factory mock-up must confirm it.
- **Fans (DECIDED):** two S&P TD-500/150-160 SILENT ECOWATT (EC, 0–10 V, 6 kg each), run slow: about 4 V for the supply (9 Pa at 70 l/s) and a little more for the exhaust (28 Pa). Intake and exhaust slots sit on the decor blocks' top faces, above eye level like v1's roof grilles.
  - Air path: the supply grille is on the right block's inner face, so air enters at the front and is thrown towards the back. The exhaust grille is on the top block's inner face, high at the front.
- **Servicing:** each decor block's top face is a screwed lid, M6 into rivnuts, with the slot grille in it. Lift the lid, undo the duct clamps and the fan bracket, unplug the fan, and lift it out. A cartridge slides out the same way. Nothing on the pod's walls or ceiling comes off. The decor block's inside is lined with felt, so casing noise stays in.
- **Pressure balance and the door:** both fans take the same 0–10 V signal so the pod stays near room pressure. A 5 Pa difference would add about 6 N at the door handle.
- **12 V option:** the PM asked for a quick look at a 12 V EC fan first. Result: no 12 V fan found does the job, so the mains EC fan (TD-350 class, 0–10 V from the sensor hub, on the outlet circuit) is the pick, as the PM's ruling allows. The 12 V axial fans with published data are Noctua NF-A14 industrialPPC-3000 (269 m³/h at 0 Pa, 41.3 dB(A)) and San Ace 109E5712M501 (248 m³/h at 0 Pa, 67.6 Pa maximum, 41.0 dB(A)). They give 250–270 m³/h only at zero pressure, so it would take two per path at full speed. The 12–28 V centrifugal ebm-papst RG 160-28/14 N makes 209 m³/h at 66 dB sound power, about 20 dB louder than the TD-350 at this duty (research notes, checked 2026-10-31). Unlike the 12 V figures, the TD-350's published octave data lets the silencer be sized properly: most of its energy sits at 500 Hz–1 kHz, where the lined channel works best. That's why it reaches about 24 dB(A) inside even though its total LwA is 54 dB(A).
- **Controls:** the in-house Desk Pro AI sensor hub (D-09) measures CO2, shows it inside, and drives both fans 0–10 V.
  - 53 l/s while occupied, with boost to 70 l/s triggered by CO2, by temperature or by hand.
  - Run-on of 15–30 min after the last presence.
  - The fans are hard-wired on the outlet (mains) circuit with no user switch, only boost. That's an exception to the 12 V bus (D-10), ruled by the PM because no 12 V fan performs well enough. Lights, sensors and the voice kit stay on the 12 V bus.
  - The plan's UTEN S300 "triết áp quạt" (S300G-1D/S, a 25–300 W phase-cut speed control for ceiling fans) doesn't suit EC fans and is replaced. Products are in selection.md.

## 8. Hooks for the later voice cockpit kit

Mic array, speakers, screen and status light. Reserved here; the kit itself isn't designed.
- **Power:** 12 V 5 A (60 W) on the 12 V bus (D-11), the same as the layout study. It's in the heat figures above (+0.7 °C at 70 l/s).
- **Cable path:** the 25 mm gap inside each lining cassette carries cables behind the felt without touching the outer wall. Cassettes lift off with no tools. The ceiling cassettes link the back wall to the front decor blocks.
- **Mounting points:** M6 rivnuts in the 20 × 40 aluminium members, one bolt size, at positions the Layout Engineer fixes. The screen goes on the back wall and the status light on the front decor top block.
- **Sound:** speakers and mics mount on the lining cassette, never through the ACP skin. A hole through the outer leaf would be a new leak, about 0.1 dB for a 28 mm hole. The 25 dB(A) fan target also helps the mic array.

## 9. Low-emission materials

Details and links are in selection.md, section G.
- **Felt:** Autex Cube (CDPH-compliant, Declare Red List free, HPD and EPD) or Woven Image EchoPanel (GreenTag Level A).
- **Boards:** the DECIDED stack has no wood board at all. If plywood or HDF comes back, use E0 or CARB P2 / TSCA Title VI with a certificate number. The VN maker found only self-declares it.
- **Glue:** SikaTack Panel-50 (EMICODE EC1 PLUS, Indoor Air Comfort GOLD, M1, A+) suits ACP to aluminium. Sikaflex-118 Extreme Grab (EC1 PLUS) is not for full-surface or structural bonding.

## 10. Assumptions and how to close them

| Assumption | Value used | Why | What closes it |
|---|---|---|---|
| v1's door gaps, vent path loss and raised-floor leak | sides 2–5 mm, bottom 5–10 mm; vents 0–6 dB; floor +0–6 dB | v1 drawings show no seals; vent slots measured from sheet 9 | v1 lab test (ISO 23351-1), already planned |
| Seal and gasket performance | 25–38 dB per 10 mm strip | athmer data 52–56 dB per joint is for frame seals in a test door; pod fitting is worse | door sample test |
| Sharp model accuracy | ±2 dB on every element | the model is about ±3 dB against lab data | wall-sample test |
| Floating lining is fully decoupled | no stud bridge | perimeter gasket and hook-and-loop, no screws | wall-sample test; if it fails, the 'point' model costs about 0.5 dB |
| PET fill density | 32 kg/m³ | typical polyester insulation; no product sourced | pick a product with data |
| Felt absorption | Autex Cube 12 mm data | no 9 mm panel with octave data found | test the chosen felt to ISO 354, or buy Cube |
| Silencer attenuation | Sabine formula × 0.6–1.0, capped at 40 dB per band; 37.5 mm lining absorption interpolated from Pyrotek's 25 and 50 mm data | no product data for this splitter | factory mock-up of one cartridge with its fan |
| Breakout through the silencer casing and decor face | casing 2 mm aluminium, felt-lined decor cavity (1.5 m² of felt), 0.8 m² of decor face | simple energy model | the same mock-up, measured inside the pod |
| Fan sound at our duty | S&P octave data at 4 V; exhaust +2.5 dB for its higher pressure | catalogue points only | measure on the mock-up |
| Fan duty point | read off S&P's curve figure | catalogue plots only | measure flow on the mock-up |
| CO2 per person | 5.2 ml/s | matches the brief's 26 l/s for 800 ppm | CO2 logger on the prototype |
| Heat per person | 75 W sensible + 30 W laptop | seated office work | temperature logger on the prototype |
| Acrylic sound data | Sharp model | published PMMA figures contradict each other | door sample test |

## 11. Method notes

- **Single leaf:** Sharp (1978). Field-incidence mass law below fc/2; damped coincidence above fc, with loss factor = material + radiation (σ ≤ 3); a straight line on log f between. A Sewell (1970) finite-panel correction is added below 500 Hz for 1.7 m² panels: +3.6 dB at 125 Hz and +1.7 dB at 250 Hz.
- **Sandwich panels:** fc comes from the bending and shear dispersion. A core whose shear wave speed is below the speed of sound has no coincidence. A soft core gets a dilatational dip (−6 dB) near f_d.
- **Double leaf:** Sharp (1978). f0 with the 1.8 factor. R1 + R2 + 20 lg(fd) − 29 up to c/2πd, then R1 + R2 + 6. An unfilled cavity loses 8 dB. Studs (line, b) or points (e) cap it. The stud term averages the two leaf orders, so it is the same from either side.
- **Pod:** diffuse-field energy balance inside. Absorption: Autex Cube data for felt, Acoustical Surfaces tables for glass, wood and tile. ISO 3382-3 normal-effort speech spectrum and IEC 61672 A-weighting. The 8 kHz band is left out (under 0.05 dB).
- **Leaks:** open area with τ = 1. Seals and gaskets are 10 mm strips with their own R.
- **Air:** well-mixed CO2 and heat balance. Fan noise reaches a seated head two ways:
  - Duct path: the fan's octave LwA, minus the splitter loss (Sabine 1.05 α^1.4 P/S per metre, derated) and the duct end reflection (ASHRAE).
  - Breakout path: through the cartridge casing (Sharp R + Sewell) into the felt-lined decor cavity, then through the decor's inner ACP face. The power lost through the casing is integrated along the decaying sound in the passage.
  - Both paths then get direct and reverberant room terms. Flow changes scale the fan sound by 50 lg(Q/70).
- **Weights:** the rest of the pod comes from the layout study (branch super-tab/7667a51, commit cb7009f, work in progress). Wall build-ups, glass and fixes come from this report.

## 12. Issues for the issue register (Control Engineer)

1. v1's inner wall and ceiling board is 9 mm in BOM v5 but 15 mm in the wood-part drawings (sheets 12, 17, 22, 34). The floor board is also 9 mm in the BOM against 15 mm in the drawings.
2. v1's outer skin is "Tấm nhôm 2 mm" (aluminium sheet) in the BOM but "ALU DAY 2mm" in the drawings, which in VN trade usually means ACP. This changes v1's weight (2.9 against 5.4 kg/m²) and its sound.
3. v1's fixed glass: the BOM gives 2138.5 × 723.7 mm, which is the bounding box. The finished slanted shape from the STEP is about 1.06 m², not 1.55 m².
4. Panasonic FV-15AUL1 (VT06): the manual forbids ceiling mounting, and no fan curve is published. It's replaced in selection.md.
5. The plan's felt page (DHG, VT03) gives a density of 20–30 kg/m³. That's loose-wool data, not a 9 mm panel, and there's no test standard or certificate.
6. UTEN S300G-1D/S fan speed control is rated 25–300 W phase-cut. It suits neither one FV-15AUL1 (12.5 W) nor EC fans.
7. VT03 is used for both the felt and the 50 × 100 tube in the plan (already on the register).
