# Spaceship sound and fresh-air check

Spaceship is the working name for FocusPod v2 ("Indoor Pod").

- **Status:** calculation, not a test. Every number below comes from `calc.py` in this folder, and every input there carries its own status and source. Bought-part data and links are in [`../hardware/selection.md`](../hardware/selection.md).
- **Date:** 2026-10-31.
- **Rerun:** `python3 calc.py` prints every table in this report. `python3 calc.py --verify` rebuilds them and checks that this file quotes each one exactly.
- **Decisions:** DECIDED means the PM ruled on it on 2026-10-31. Decision IDs (D-xx) refer to `v2/00-Control/decision-log.md`; the other rulings were made in the project chat and are being logged. PROPOSED means it still needs a call. HOLD means a supplier or a sample has to confirm it.
- **Fix pass:** this version answers Reviewer 3's hold at 5c1003b and applies the PM's 8 rulings on it (2026-10-31). The answers table is in the PR.

## Results first

1. **v1 as built: about 15 dB speech reduction (D_S,A, range 11–18), not the 30 dB on the product page.** Its open vent slots (35%), door gaps (33%) and raised floor (14%) let out most of the sound. v1's lab test will settle this.
2. **Spaceship as planned: about 14.5 dB (11–17), level with v1.** The light fixes take it to about 16 dB: perimeter and drop seals, sealed glass, joint gaskets, silenced vents, and the thin floor with a base seal. After that, the walls and ceiling carry about 90% of the sound that gets out.
3. **DECIDED build: about 411 kg in this model, 19.3 dB (14.6–21.7), under the 420 kg cap.**
   - Walls and ceiling: ACP 3 mm on a 20×40×1.2 aluminium frame at 400 mm, 40 mm PET fill, and a floating lining cassette (0.5 mm steel tray, 25 mm air gap, 9 mm felt).
   - Front: 4+4 laminated glass of toughened, heat-soaked panes, frameless like v1. Hinges and lock are on HOLD until a rated set is named.
   - Air: four 12 V fans and two splitter cartridges in the right decor block (PROPOSED in this fix pass).
   - Smoked acrylic stays an optional experiment on the factory sample: 18.9 dB at about 384 kg.
4. **Why the headline fell from 24.0 to 19.3 dB: the felt data.**
   - The 24.0 used Autex Cube 12 mm data on a 25 mm gap as a stand-in.
   - Ruling 5 asks for the published data of the felt picked. The only published data for a 9 mm, 1.8 kg/m² felt is Polyx Board 9, and it's measured glued flat, which absorbs far less at 125–500 Hz.
   - Our felt sits on a 25 mm gap, which absorbs more, but no data for that is published. So 19.3 is on the safe side and 24.0 is roughly the best case.
   - The wall sample measures the real felt down to 100 Hz and settles it.
   - The range also widened at the bottom: the low case now carries the 125–250 Hz risks (no finite-panel gain, and a 4 dB dip at each double wall's resonance).
5. **30 dB isn't reached anywhere in this search, up to 500 kg (best about 23 dB).** Beyond 420 kg each extra dB costs about 20–30 kg. Low voices (125–250 Hz) limit a light pod, and only mass, cavity depth and low-frequency absorption help there. A thicker felt on the ceiling (24 mm Autex Cube) would add about 1.2 dB; its weight isn't sourced yet.
6. **Air (targets DECIDED, fan design PROPOSED):**
   - 53 l/s normal at 22.8 dB(A) (target 25 or less).
   - The boost reaches 74 l/s at 30 dB(A) (target 30 or less, aiming for 70); 70 l/s gives 28.9 dB(A).
   - Two people in a 600 ppm office: 796 ppm at 53 l/s with perfect mixing, 845 ppm at the PM's mixing effectiveness of 0.8. Holding 800 ppm at 0.8 takes about 65 l/s, at about 27 dB(A).
   - Heat: two people need at least 48 l/s to stay within 4 K of the room, and one person 27 l/s, so the 26 l/s floor (D-44) sits right at the heat limit.
7. **Corrections in this fix pass:**
   - The 5c1003b fans were 6 kg S&P TD-500s loose in the decor cavity. Their own casings radiate 44 dB(A), which the old model left out. With it, that design gives 35.8 dB(A) at 53 l/s. They also don't fit: the decor is 205 mm deep (measured from v1), not 230–235.
   - Four 12 V fans at about 0.3 kg each replace them. That saves about 11 kg, which pays for the bigger cartridges.
   - D-10's 12 V check was argued at 42 Pa. At the new 10–17 Pa a 12 V pair per path works, so the mains fan exception isn't needed.

## 1. The DECIDED stack, for the Layout and Fusion Engineers

Outside to inside. DECIDED by the PM on 2026-10-31 (D-02 weight and sound target, D-05 thin floor, D-09 air, plus rulings in the project chat). D-07 still reads acrylic-first, but the PM's later ruling made 4+4 laminated glass the baseline; that is to be logged.
- aluminium frames at 400 mm, 20 × 40 × 1.2 (the rivnut grip check passed);
- no plywood behind the ACP;
- 0.5 mm lining tray (0.4 mm would cost 1 dB);
- fill at 32 kg/m³ (the lighter 24–25 kg/m³ grade has no published absorption data);
- 4+4 laminated front of toughened, heat-soaked panes (8.76 mm), with the door hardware on HOLD until it's rated (ruling 3);
- fans and silencers in the decor, outside the sound shell (this fix pass puts both paths in the right block, PROPOSED);
- every lining cassette on captive mechanical clips with a rated load, plus a safety catch on the ceiling ones; hook-and-loop only to line them up (ruling 4);
- decor 205 mm deep, measured from v1 (D-39 is being corrected);
- cap 420 kg.

**Walls and ceiling (vách, trần), 81 mm, 12.6 kg/m² including frame and felt**

| # | Layer (Vietnamese name) | mm | kg/m² | Status and source |
|---|---|---:|---:|---|
| 1 | ACP skin, Alcorest EV3038 Dark Yellow, 3 × 0.21 mm skins, PE core (tấm ốp alu VT01) | 3 | 3.5 | calculation from the maker's skin spec; the maker publishes no kg/m² (selection.md VT01) |
| 2 | Bond, ACP to frame: SikaTack Panel-50 system or equivalent, factory only (keo dán) | — | ~0.1, not in total | source for substrates (selection.md glue row); bond pattern HOLD for a coupon test |
| 3 | Aluminium frame 20 × 40 × 1.2 mm, members at 400 mm (khung nhôm) | 40 | 1.9 | calculation: 0.373 kg/m × 5.0 m of tube per m² |
| 4 | Polyester fill between members, Pyrotek Sorberpoly 2D 32 kg/m³ or equal (bông PET) | (40) | 1.3 | source for the product and its absorption (selection.md B) |
| 5 | Resilient gap: perimeter gasket PORON 4701-40, 3.2 mm; captive clips hold the cassette, hook-and-loop only locates it (ruling 4); no screws through (gioăng) | 3 | ~0.1, not in total | source for the gasket (selection.md); decoupling is a calculation assumption, HOLD for the wall-sample test |
| 6 | Lining cassette: galvanised steel 0.5 mm tray with 25 mm returns (khay thép lót) | 0.5 | 4.2 | calculation: 3.93 kg/m² sheet + 0.26 kg/m² returns |
| 7 | Air gap inside the cassette (spare cable path) | 25 | — | calculation: this gap lets the felt absorb at 250–500 Hz |
| 8 | PET felt 9 mm, Dark Gray, on the cassette face (tấm tiêu âm PET VT03); the factory's felt, tested in the wall sample first (DECIDED) | 9 | 1.8 | source for 9 mm at 1.8 kg/m² (Polyx Board 9, layout study S11); absorption from Polyx Board 9's published data, glued flat (conservative; ruling 5); emission certificate HOLD |
| | **Total** | **81** | **12.6** | the outer panel (layers 1–4) and the lining cassette (5–8) ship as separate parts |

**Part weights for the 20 kg rule** (calculation):

| Part | Size, mm | kg |
|---|---|---:|
| Side-wall outer panel | 1500 × 1145 | 11.4 |
| Lining cassette for it | — | 10.3 |
| Ceiling half outer panel | 1212 × 1500 | 12.1 |
| Supply cartridge with its fill | 159 × 450 × 2100 | 18.6 |
| Exhaust cartridge with its fill | 159 × 450 × 2100 | 18.6 |
| Each 12 V fan | 140 × 140 × 25 | about 0.3 (assumption) |
| Door (4+4) | 1176 × 2011 | 47.5 (PM figure), glass is exempt |

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
| Tempered 8 mm | 68 | 14.6 | 19.2 | 21.6 | +0.0 |
| Tempered 10 mm (v1) | 86 | 14.6 | 19.3 | 21.7 | +0.0 |
| Laminated acoustic 4+4 (8.76 mm) | 72 | 14.6 | 19.3 | 21.7 | +0.0 |
| Smoked acrylic 8 mm | 33 | 14.3 | 18.7 | 21.1 | -0.6 |
| Smoked acrylic 10 mm | 41 | 14.5 | 18.9 | 21.3 | -0.3 |
| Smoked acrylic 12 mm | 49 | 14.6 | 19.1 | 21.5 | -0.1 |

- **DECIDED front: 4+4 acoustic laminated glass**, frameless like v1. It's the quietest pane, and in this pod 0.4 dB better than 10 mm acrylic.
  - Acrylic would save about 27 kg, but on hinges rated for glass it needs an 80 mm opaque aluminium stile down the hinge edge. That breaks the look rule (D-01).
  - Acrylic also brings creep, scratch, fire-class and flatness risks.
  - It stays as an optional experiment on the factory sample.
- **Scratches:** cast acrylic is pencil hardness 3H (ACRYLITE cast), far softer than glass. Plan a hard-coated sheet, or accept wear on the door face. The factory sample decides.
- **Look:** the grey cast sheet is Perspex Neutral 9T56, with 46% light transmission, which Perspex gives as the same at any thickness. The sample decides the match with v1's smoked glass.
- **Fire, for later US rules:** PMMA is Euroclass E / UL 94 HB, while glass is A1 and PVB laminate is "no performance declared". A 2.4 m² acrylic door may be a problem for US interior-finish rules later, one more reason the baseline is glass.
- **Hinges and lock: HOLD (ruling 3).** The glass is 4+4 laminate of toughened, heat-soaked panes (8.76 mm), and the door is 47.5 kg and 1176 mm wide. dormakaba lists OFFICE 11.233 for toughened glass 8/10 only, and offers laminated glass only with its MUNDUS patch fittings. The STUDIO lock 10.200 is for doors up to 1000 mm. A rated set is still to be named; the supplier questions are in selection.md. The look stays frameless, with the hinges in the left decor block.

## 4. The whole pod: predicted speech reduction

D_S,A is the ISO 23351-1 single number: the reduction in A-weighted sound power of standard speech, measured in a reverberation room. Here it's estimated from an energy balance inside the pod: IL = 10 lg(1 + A_in / Σ Sτ) per octave, then weighted with the speech spectrum. "low / high" combine pessimistic and optimistic values of the uncertain inputs: gap widths, seal quality, silencer performance, ±2 dB on every element, and ±15% absorption. The low case also carries the 125–250 Hz risks Reviewer 3 listed (ruling 5): no finite-panel gain, and a 4 dB dip at each double wall's mass-air-mass resonance. Inside absorption uses the felt's published data (Polyx Board 9, glued flat, from 100 Hz).

**Why the range is wide at the bottom (ruling 5).** About 80% of the speech that gets out is at 125–250 Hz, where the model is weakest. Three inputs there push the low end down: the finite-panel gain (about 1.8 dB in the central case), a dip at the walls' resonance near 300 Hz, and the felt's real absorption. The felt matters most. With 12 mm Cube data on a 25 mm gap the central case would be 24.0 dB; with the published 9 mm data, glued flat, it's 19.3. The wall sample is measured down to 100 Hz to settle all three.

| Pod | D_S,A low | central | high |
|---|---:|---:|---:|
| v1 as drawn (inner ply 15) | 11.5 | 14.9 | 18.3 |
| v1 per BOM (inner ply 9) | 11.4 | 14.9 | 18.4 |
| Spaceship as planned (10 mm glass) | 11.3 | 14.5 | 17.4 |
| Spaceship as planned, 8 mm glass | 11.2 | 14.5 | 17.3 |
| + all light fixes (plan wall) | 12.9 | 16.2 | 18.7 |
| + fixes, plan wall without plywood | 8.8 | 11.4 | 13.6 |
| + fixes, light double wall DL-HDF | 13.0 | 17.6 | 20.0 |
| + fixes, DL-HDF decoupled | 13.0 | 17.7 | 20.0 |
| + fixes, DL-ST (steel 0.5 inner skin) | 14.6 | 19.2 | 21.6 |
| + fixes, DL-ST decoupled | 14.6 | 19.2 | 21.6 |
| + fixes, honeycomb sandwich SW-HC20 | 3.4 | 5.0 | 6.8 |
| + fixes, foam sandwich + inner skin | 12.0 | 16.9 | 19.3 |
| DECIDED stack, 4+4 laminated front | 14.6 | 19.3 | 21.7 |
| DECIDED stack with the acrylic experiment | 14.5 | 18.9 | 21.3 |

Where the sound gets out (share of the speech energy, central case):

| Path (share of speech sound getting out) | v1 | Plan, 8 mm | Plan + fixes | DECIDED stack |
|---|---:|---:|---:|---:|
| walls | 6% | 41% | 70% | 63% |
| ceiling | 2% | 12% | 20% | 18% |
| glass | 2% | 2% | 3% | 4% |
| front decor | 2% | 3% | 6% | 11% |
| floor | 14% | 6% | 0% | 0% |
| door edge gaps | 22% | 12% | 0% | 0% |
| door bottom | 11% | 6% | 0% | 0% |
| fixed glass edges | 1% | 1% | 0% | 0% |
| panel joints | 5% | 3% | 0% | 0% |
| vents | 35% | 14% | 1% | 3% |
| cable holes | 1% | 0% | 0% | 0% |

The weak points move as the pod improves:
- In **v1** the vents and the door gaps dominate.
- In the **plan as drawn** the single-leaf walls dominate, then the door gaps and vents.
- With **seals and silencers** the walls and ceiling carry about 90%.
- In the **DECIDED pod** the front decor becomes visible (11%), because its faces are single 3 mm ACP over a hollow block, and the 4+4 glass is only 4%. If the wall sample tests better than calculated, the next step is the decor faces (felt lining or added mass), not the glass.

**Cable holes and panel joints are small once sealed.** An unsealed cable opening of 600 mm² (about one 28 mm hole) costs about 0.1 dB in the DECIDED pod. Unsealed panel joints at 0.15 mm cost about 0.2 dB in the plan pod and 0.5 dB in the DECIDED pod, so gaskets go on every joint. Leaving out the door seals would cost the DECIDED pod 2.2 dB, and open vents 1.7 dB.

## 5. Light fixes, with dB and kg

Applied one after another to the plan with 8 mm glass. kg is the added mass for the whole pod (calculation; sources in calc.py).

| Step | Change | D_S,A low | central | high | Gain (central) | kg added |
|---|---|---:|---:|---:|---:|---:|
| 0 | Spaceship as planned, 8 mm glass | 11.2 | 14.5 | 17.3 |  |  |
| 1 | Door edge seals on 3 sides | 11.6 | 15.0 | 17.9 | +0.5 | 1.0 |
| 2 | Door drop seal | 11.8 | 15.3 | 18.2 | +0.3 | 1.0 |
| 3 | Fixed glass in sealed U-profiles | 11.8 | 15.4 | 18.2 | +0.0 | 0.0 |
| 4 | Gaskets on every panel joint | 12.0 | 15.5 | 18.4 | +0.2 | 1.0 |
| 5 | Silenced vents (splitter cartridges in the right decor block) | 12.7 | 16.3 | 19.0 | +0.8 | 34.2 |
| 6 | Thin floor with base seal (DECIDED, D-05) | 12.9 | 16.2 | 18.7 | -0.1 | 0.5 |
| 7 | Sealed cable holes | 12.9 | 16.2 | 18.7 | +0.0 | 0.1 |

The gains are small one at a time because the plan's single-leaf walls dominate. The same fixes on v1's leaky pod would gain about 6 dB, so they matter as soon as the walls are double. A thicker ceiling absorber (Autex Cube 24 mm) would add about 1.2 dB with today's felt data. Its weight isn't sourced, so it isn't in the stack.

## 6. What each dB costs: the total-pod curve

Total pod kg is the sum of:
- the rest of the pod from the layout study, 102.4 kg: thin floor and base band, decor blocks, door hardware with drop seal and glazing profiles, fans at 1.5 kg, silencer boxes at 1.5 kg each, electrics and the voice-kit reserve;
- the fixes the study doesn't carry, 2.6 kg;
- the silencer cartridges and their fill, beyond the study's boxes;
- the four 12 V fans at about 0.3 kg each, against the study's 2 × 1.5 kg;
- the walls, ceiling and front from this report.

All light fixes are on. The search covers every wall and ceiling in table 2 with each front. The PM's earlier total with Layout's clips was about 418 kg with the 6 kg fans; this fix pass takes about 3 kg off it.

Glass front (8 mm tempered or 4+4 laminated):

| Pod budget kg | Best wall / ceiling / front | Total kg | D_S,A low / central / high |
|---:|---|---:|---|
| 280 | nothing fits |  |  |
| 300 | nothing fits |  |  |
| 320 | SW-FOAM20 / SW-FOAM20 / Tempered 8 mm | 314 | 8.7 / 11.4 / 13.6 |
| 340 | SW-FOAM20 / DL-ST-40-FLG-12 / Tempered 8 mm | 335 | 9.4 / 12.2 / 14.4 |
| 360 | PLAN-NOPLY / DL-ST-60-FL / Tempered 8 mm | 350 | 9.5 / 12.3 / 14.5 |
| 380 | DL-ST4-40-FLG-12 / PLAN-NOPLY / Tempered 8 mm | 379 | 11.9 / 15.4 / 17.7 |
| 400 | DL-ST4-40-FLG-12 / DL-ST-40-FLG-12 / Tempered 8 mm | 397 | 14.0 / 18.5 / 20.8 |
| 420 | DL-ST-40-FLG-12 / DL-2HDF-60-FL / Tempered 8 mm | 419 | 14.8 / 19.6 / 22.0 |
| 440 | DL-ST-60-FL / DL-2HDF-60-FL / Tempered 8 mm | 439 | 14.8 / 20.3 / 22.7 |
| 460 | DL-2HDF-60-FL / DL-2HDF-60-FL / Tempered 8 mm | 457 | 15.6 / 21.3 / 23.8 |
| 480 | DL-P6-HDF-60-FL / DL-P6-P9-DEC / Tempered 8 mm | 476 | 16.1 / 21.9 / 24.4 |
| 500 | DL-P6-P9-DEC / DL-P6-P9-60-FL / Tempered 8 mm | 497 | 17.3 / 22.9 / 25.4 |
| 520 | DL-P6-P9-60-FL / DL-P6-P9-60-FL / Laminated acoustic 4+4 (8.76 mm) | 518 | 18.3 / 23.7 / 26.3 |

Smoked acrylic 10 mm front:

| Pod budget kg | Best wall / ceiling / front | Total kg | D_S,A low / central / high |
|---:|---|---:|---|
| 280 | nothing fits |  |  |
| 300 | SW-FOAM20 / PLAN-NOPLY / Smoked acrylic 10 mm | 293 | 8.7 / 11.4 / 13.5 |
| 320 | PLAN-NOPLY / DL-ST4-40-FLG-12 / Smoked acrylic 10 mm | 317 | 9.4 / 12.2 / 14.4 |
| 340 | PLAN-NOPLY / DL-P6-HDF-60-FL / Smoked acrylic 10 mm | 335 | 9.5 / 12.3 / 14.5 |
| 360 | PLAN / SW-FOAM20-DL / Smoked acrylic 10 mm | 360 | 12.6 / 16.2 / 18.7 |
| 380 | DL-ST-40-FLG-12 / DL-HDF-DEC / Smoked acrylic 10 mm | 380 | 14.1 / 18.6 / 20.9 |
| 400 | DL-ST-40-FLG-12 / DL-2HDF-60-FL / Smoked acrylic 10 mm | 395 | 14.7 / 19.3 / 21.7 |
| 420 | DL-2HDF-60-FL / DL-ST4-40-FLG-12 / Smoked acrylic 10 mm | 419 | 14.9 / 20.0 / 22.4 |
| 440 | DL-2HDF-60-FL / DL-P6-HDF-60-FL / Smoked acrylic 10 mm | 437 | 15.5 / 20.9 / 23.4 |
| 460 | DL-P6-P9-DEC / DL-2HDF-60-FL / Smoked acrylic 10 mm | 460 | 16.4 / 21.7 / 24.2 |
| 480 | DL-P6-P9-DEC / DL-P6-P9-60-FL / Smoked acrylic 10 mm | 473 | 17.0 / 22.2 / 24.7 |
| 500 | DL-P6-P9-60-FL / DL-P6-P9-60-FL / Smoked acrylic 10 mm | 491 | 17.8 / 22.8 / 25.3 |
| 520 | DL-P6-P9-60-FL / DL-P6-P9-100-DEC / Smoked acrylic 10 mm | 501 | 18.1 / 22.9 / 25.4 |

Best builds inside the DECIDED rules:

| Case | Walls | Ceiling | Front | Silencer casing | Total kg | D_S,A low / central / high |
|---|---|---|---|---|---:|---|
| DECIDED stack | DL-ST-40-FLG-12 | DL-ST-40-FLG-12 | Laminated acoustic 4+4 (8.76 mm) | aluminium 2.0 mm | 411 | 14.6 / 19.3 / 21.7 |
| Same with 20x40x1.5 frames | DL-ST-40-FLG | DL-ST-40-FLG | Laminated acoustic 4+4 (8.76 mm) | aluminium 2.0 mm | 418 | 14.6 / 19.3 / 21.7 |
| Same with a 0.4 mm tray (rejected: costs 1 dB) | DL-ST4-40-FLG-12 | DL-ST4-40-FLG-12 | Laminated acoustic 4+4 (8.76 mm) | aluminium 2.0 mm | 398 | 13.9 / 18.3 / 20.7 |
| Same, felt flat on the ceiling lining (no gap) | DL-ST-40-FLG-12 | DL-ST-40-FL | Laminated acoustic 4+4 (8.76 mm) | aluminium 2.0 mm | 412 | 14.6 / 19.3 / 21.7 |
| Acrylic experiment: 10 mm with hinge stile | DL-ST-40-FLG-12 | DL-ST-40-FLG-12 | Smoked acrylic 10 mm | aluminium 2.0 mm | 384 | 14.5 / 18.9 / 21.3 |
| Light 0.8 mm cartridge casings | DL-ST-40-FLG-12 | DL-ST-40-FLG-12 | Laminated acoustic 4+4 (8.76 mm) | aluminium 0.8 mm | 394 | 14.6 / 19.3 / 21.7 |

- **The curve rises fastest from about 380 to 400 kg:** about 3 dB for 20 kg. Beyond 420 kg, each dB costs about 20–30 kg.
- **30 dB isn't reached in this search.** At 500 kg the walls are 100 mm double leaves with plywood, and the pod still stops at about 23 dB.
- **The curve is a calculation with about −5 / +2.5 dB of spread.** The low side carries the 125–250 Hz risks and the felt data. The factory's wall-and-door sample is the physical check, and it comes before any further weight goes in.

## 7. Fresh air

### 7a. CO2 and heat

Inside volume 8.35 m3; CO2 from 2 people 10.4 ml/s. The last column uses a mixing effectiveness of 0.8 (PM ruling 8); the others assume perfect mixing.

| Fresh air l/s | Air changes /h | Minutes per change | CO2 rise ppm | CO2 ppm, room 400 | CO2 ppm, room 600 | Minutes to 95% | Heat rise K | Heat rise K with voice kit | CO2 ppm, room 600, mixing 0.8 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 26 | 11 | 5.4 | 400 | 800 | 1000 | 16 | 7.4 | 9.3 | 1100 |
| 40 | 17 | 3.5 | 260 | 660 | 860 | 10 | 4.8 | 6.1 | 925 |
| 53 | 23 | 2.6 | 196 | 596 | 796 | 8 | 3.6 | 4.6 | 845 |
| 70 | 30 | 2.0 | 149 | 549 | 749 | 6 | 2.8 | 3.5 | 786 |

Flow that keeps the inside 4 K or less over the room: one person 27 l/s, two people 48 l/s, two with the voice-kit reserve 61 l/s. One person at the 26 l/s floor (D-44), room 600, mixing 0.8: 850 ppm.
CO2 after 2 h at 40 l/s from 400 ppm (room 400): 660 ppm; after 3 h at 26 l/s, room 600: 1000 ppm.

- 800 ppm needs 26 l/s **only when the room air is at outdoor CO2 (400 ppm)** and the air is perfectly mixed. In a 600 ppm office two people need about 52 l/s with perfect mixing, and about 65 l/s at the mixing effectiveness of 0.8 the PM set (ruling 8).
- **Heat also drives the fans (D-44):** the inside stays at most 4 K over the room. That takes 48 l/s for two people, 61 l/s with the voice-kit reserve, and 27 l/s for one person.
- **Control (D-44):** CO2 leads, with a floor of 26 l/s while one person is inside. Temperature can raise the flow. 53 l/s for two, and a boost of up to 74 l/s inside 30 dB(A).
- **Supply low, exhaust high (ruling 8):** the supply grille sits low on the right block's inner face, so the cool room air spreads across the floor. A high exhaust grille needs a riser in the decor block and costs about 3 dB(A); see 7b.

### 7b. Fans, silencers and noise inside

Targets (PM ruling 1): 25 dB(A) or less inside at 53 l/s, and 30 dB(A) or less at boost, aiming for 70 l/s. Both tables include the fans' casing (or fan-box) sound and the real 205 mm decor section. The first table is the cartridge, the second the fans.

| Cartridge casing | Cartridges with fill kg | Fill toward the pod mm | Passage IL 125 | 250 | 500 | 1k | 2k | 4k dB | Casing + fill + inner face R 125 | 250 | 500 | 1k | 2k | 4k dB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| aluminium 2.0 mm (pick) | 37.2 | 40 | 2 | 12 | 27 | 40 | 40 | 40 | 14 | 20 | 34 | 50 | 55 | 46 |
| aluminium 0.8 mm | 19.8 | 42 | 2 | 12 | 27 | 40 | 40 | 40 | 10 | 16 | 27 | 44 | 51 | 42 |

Pressure drop per path, supply / exhaust: 26 l/s 2 / 2 Pa; 53 l/s 10 / 10 Pa; 70 l/s 17 / 17 Pa. Each fan pair reaches 88 l/s at full speed.

| Fans and cartridges | Fits the 205 mm decor | Fans kg | Cartridges with fill kg | At 53 l/s: fan speed supply / exhaust | At 53 l/s: duct / breakout / total dB(A) | Boost flow at 30 dB(A) l/s | At 70 l/s: total dB(A) |
|---|---|---:|---:|---|---|---:|---:|
| 2 x S&P TD-500/150-160 SILENT, 4 V, as at 5c1003b, with casing sound | no (ØD 221 mm) | 12.0 | 29.8 | 4 V | 23.4 / 35.5 / 35.8 | 41 | 41.8 |
| 2 x 2 Noctua NF-A14 iPPC-3000, 12 V, 2 mm Al casings, both grilles low (pick) | yes | 1.2 | 37.2 | 60% / 60% | 20.2 / 19.4 / 22.8 | 74 | 28.9 |
| Same, 0.8 mm Al casings | yes | 1.2 | 19.8 | 60% / 60% | 20.2 / 25.2 / 26.4 | 63 | 32.4 |
| Same as the pick, with a 5 dB fan tone at 250 Hz (risk) | yes | 1.2 | 37.2 | 60% / 60% | 23.8 / 22.6 / 26.3 | 63 | 32.3 |
| Exhaust grille high: exhaust fans at the foot, 150 mm steel riser, 405 mm cartridges | yes | 1.2 | 43.8 | 64% / 72% | 22.6 / 22.5 / 25.6 | 65 | 31.6 |

- **What changed and why.** The decor is 205 mm deep (measured from v1), so 199 mm inside its two 3 mm faces. The 5c1003b cartridges (212 mm) and both S&P fans (ØD 221 and 204) don't fit. Their casing sound, left out before, puts that design at 35.8 dB(A) at 53 l/s (first fan row).
- **Cartridges (PROPOSED; CAD fit HOLD):** two side by side in the right decor block, which is 1016 mm wide (layout study F-DR). The top block's 280 mm face is too small for the flow.
  - Each one: two 40 mm passages between three 25 mm Pyrotek layers (published data, so nothing is interpolated), a 2 mm aluminium casing, 159 × 450 × 1800 mm, plus a 300 mm lined fan box at the top.
  - The 40 mm between each cartridge and the decor's inner face is packed with the walls' polyester fill. Casing, fill and face then act as a filled double wall (f0 about 280 Hz). This replaces the felt-lined cavity of the old model, which couldn't be backed up.
  - 18.6 kg each with fill, 37.2 kg for both, under the 20 kg part rule.
- **Fans (PROPOSED under ruling 1):** two Noctua NF-A14 industrialPPC-3000 PWM per path, 12 V, side by side on a bulkhead in the fan box. At 53 l/s they run at about 60% speed against 10 Pa.
  - Each fan's far side is ducted airtight to its slot on the block's top face (ruling 1), so no fan port opens into the decor cavity.
  - Four fans weigh about 1.2 kg, against 12 kg for two TD-500s. That pays for the bigger cartridges, and the pod still ends about 3 kg lighter than at 5c1003b.
  - They run on the 12 V bus (D-10), driven by the sensor hub, so mains feeds only the outlets.
- **Where the noise comes from at 53 l/s:** about half through the grilles and half through the cartridge walls, nearly all at 125–250 Hz, where splitters and light walls are weakest.
- **Risks, and the test that closes them (HOLD):**
  - The 12 V fans have no octave data. The model uses the TD-500's spectrum shape and reads the maker's 41.3 dB(A) as sound pressure at 1 m. A 5 dB tone at 250 Hz would give 26.3 dB(A) at 53 l/s (third fan row).
  - The fan curve is a straight line between the maker's free-air flow and maximum pressure.
  - The fan-sample test (selection.md, Sample tests) measures a fan pair in its box: flow, octave sound power at 53 and 70 l/s, and tones.
  - If it tests loud: 1 mm steel casings (about +13 kg for about 1 dB), or a third fan per path running slower.
- **Exhaust high (ruling 8) is a PM call.** With the slots on the top face (D-29) and straight cartridges, both grilles end up low.
  - A high exhaust grille needs the exhaust fans at the foot of the block, blowing up a 150 mm steel riser between the cartridges to the slot. That gives 25.6 dB(A) at 53 l/s and 65 l/s at 30 dB(A) (last fan row), and adds about 7 kg.
  - The PROPOSED pick is the straight layout: supply grille low at the door side, exhaust grille low at the far side, about 0.5 m apart. Its mixing rests on the 0.8 the PM set.
- **Breakout method:** ASHRAE's rectangular-duct formula through the casing alone; the fill and inner face count only in bands fully above f0. The fan box is a reverberant box behind the same double wall.
- **Servicing:** the right block's top face is a screwed lid, M6 into rivnuts, with both slot grilles in it. Lift the lid and the fans come out of their boxes; a cartridge lifts out the same way. Nothing on the walls or ceiling comes off.
- **Pressure balance and the door:** both fan pairs take the same signal, so the pod stays near room pressure. A 5 Pa difference would add about 6 N at the door handle.
- **Controls:** the in-house Desk Pro AI sensor hub (D-09) measures CO2 and temperature, shows CO2 inside, and drives both fan pairs.
  - 26 l/s floor with one person (D-44), 53 l/s for two, more on CO2 or temperature, boost by hand, up to 74 l/s inside 30 dB(A).
  - Run-on of 15–30 min after the last presence.
  - The hub's fan output has to suit PWM fans; the exact interface belongs to the electrical scope (HOLD).
  - The plan's UTEN S300 "triết áp quạt" (S300G-1D/S, phase-cut for 25–300 W) doesn't suit these fans and is replaced.

## 8. Hooks for the later voice cockpit kit

Mic array, speakers, screen and status light. Reserved here; the kit itself isn't designed.
- **Power:** 12 V 5 A (60 W) on the 12 V bus (D-11), the same as the layout study. It's in the heat figures above (+0.7 °C at 70 l/s).
- **Cable path:** the 25 mm gap inside each lining cassette carries cables behind the felt without touching the outer wall. Cassettes lift off with no tools. The ceiling cassettes link the back wall to the front decor blocks.
- **Mounting points:** M6 rivnuts in the 20 × 40 aluminium members, one bolt size, at positions the Layout Engineer fixes. The screen goes on the back wall and the status light on the front decor top block.
- **Sound:** speakers and mics mount on the lining cassette, never through the ACP skin. A hole through the outer leaf would be a new leak, about 0.1 dB for a 28 mm hole. The 25 dB(A) fan target also helps the mic array.

## 9. Low-emission materials

Details and links are in selection.md, section G.
- **Felt:** Autex Cube (CDPH-compliant, Declare Red List free, HPD and EPD) or Woven Image EchoPanel (GreenTag Level A). The factory's 9 mm felt needs an emission certificate: HOLD (Target 6).
- **Boards:** the DECIDED stack has no wood board at all. If plywood or HDF comes back, use E0 or CARB P2 / TSCA Title VI with a certificate number. The VN maker found only self-declares it.
- **Glue:** SikaTack Panel-50 (EMICODE EC1 PLUS, Indoor Air Comfort GOLD, M1, A+) suits ACP to aluminium. Sikaflex-118 Extreme Grab (EC1 PLUS) is not for full-surface or structural bonding.

## 10. Assumptions and how to close them

| Assumption | Value used | Why | What closes it |
|---|---|---|---|
| v1's door gaps, vent path loss and raised-floor leak | sides 2–5 mm, bottom 5–10 mm; vents 0–6 dB; floor +0–6 dB | v1 drawings show no seals; vent slots measured from sheet 9 | v1 lab test (ISO 23351-1), already planned |
| Seal and gasket performance | 25–38 dB per 10 mm strip | athmer data 52–56 dB per joint is for frame seals in a test door; pod fitting is worse | door sample test |
| Sharp model accuracy | ±2 dB on every element | the model is about ±3 dB against lab data | wall-sample test |
| Floating lining is fully decoupled | no stud bridge | perimeter gasket and captive clips, no screws through; clip stiffness unknown | wall-sample test with the real clips; if they bridge, the 'point' model costs about 0.5 dB |
| PET fill density | 32 kg/m³ | typical polyester insulation; no product sourced | pick a product with data |
| Felt absorption | Polyx Board 9 published data from 100 Hz, glued flat; the 25 mm gap's extra absorption isn't counted | the only published data for a 9 mm, 1.8 kg/m² felt (ruling 5) | the wall sample: ISO 354 on the 25 mm gap, down to 100 Hz |
| Silencer attenuation | Sabine formula × 0.6–1.0, capped at 40 dB per band; 25 mm Pyrotek lining, P/S 50 per m | no product data for this splitter | factory mock-up of one cartridge with its fans |
| Breakout from the cartridges | ASHRAE duct breakout through the 2 mm casing alone; fill and inner face count only above f0; the side faces' flanking is taken as covered by the face mass left out | standard method, conservative at 125–250 Hz | the same mock-up, measured inside the pod |
| Fan sound at our duty | maker's 41.3 dB(A) read as sound pressure at 1 m (LwA = LpA + 11), TD-500 spectrum shape, 50 lg of speed | no octave data for 12 V fans | fan-sample test: octave sound power and tones |
| Fan duty point | straight-line curve between the maker's free-air flow and maximum pressure; system loss K = 7.5 | the maker gives two points only | fan-sample test: flow against pressure |
| CO2 per person | 5.2 ml/s | matches the brief's 26 l/s for 800 ppm | CO2 logger on the prototype |
| Heat per person | 75 W sensible + 30 W laptop | seated office work | temperature logger on the prototype |
| Acrylic sound data | Sharp model | published PMMA figures contradict each other | door sample test |
| 125–250 Hz model risks | low case: no finite-panel gain, 4 dB dip at f0 | Reviewer 3 P2-4, ruling 5 | wall sample measured down to 100 Hz |
| Mixing effectiveness | 0.8 for CO2 | PM ruling 8 | CO2 logger on the prototype |
| Decor section | 205 mm deep, 3 mm faces, 199 mm clear | measured from v1 (PM brief) | CAD |

## 11. Method notes

- **Single leaf:** Sharp (1978). Field-incidence mass law below fc/2; damped coincidence above fc, with loss factor = material + radiation (σ ≤ 3); a straight line on log f between. A Sewell (1970) finite-panel correction is added below 500 Hz for 1.7 m² panels: +3.6 dB at 125 Hz and +1.7 dB at 250 Hz.
- **Sandwich panels:** fc comes from the bending and shear dispersion. A core whose shear wave speed is below the speed of sound has no coincidence. A soft core gets a dilatational dip (−6 dB) near f_d.
- **Double leaf:** Sharp (1978). f0 with the 1.8 factor. R1 + R2 + 20 lg(fd) − 29 up to c/2πd, then R1 + R2 + 6. An unfilled cavity loses 8 dB. Studs (line, b) or points (e) cap it. The stud term averages the two leaf orders, so it is the same from either side.
- **Pod:** diffuse-field energy balance inside. Absorption: Polyx Board 9 published data for the felt (one-third octaves from 100 Hz, averaged into octaves), Acoustical Surfaces tables for glass, wood and tile. ISO 3382-3 normal-effort speech spectrum and IEC 61672 A-weighting. The 8 kHz band is left out (under 0.05 dB).
- **Leaks:** open area with τ = 1. Seals and gaskets are 10 mm strips with their own R.
- **Air:** well-mixed CO2 and heat balance. Fan noise reaches a seated head two ways:
  - Duct path: the fan's octave LwA, minus the splitter loss (Sabine 1.05 α^1.4 P/S per metre, derated) and the duct end reflection (ASHRAE).
  - Breakout path: ASHRAE's rectangular-duct breakout through the casing (Cummings), on the mean duct power along the lined length, toward the pod only; the filled double wall (casing, fill, inner face; Sharp) adds loss only above f0. The fan box is a reverberant box behind the same double wall. The 5c1003b row keeps its old cavity model, with the casing sound added.
  - Both paths then get direct and reverberant room terms. 12 V fans: operating point on a straight-line fan curve, sound by 50 lg of speed.
- **Weights:** the rest of the pod comes from the layout study (branch super-tab/7667a51, commit cb7009f, work in progress). Wall build-ups, glass and fixes come from this report.

## 12. Issues for the issue register (Control Engineer)

1. v1's inner wall and ceiling board is 9 mm in BOM v5 but 15 mm in the wood-part drawings (sheets 12, 17, 22, 34). The floor board is also 9 mm in the BOM against 15 mm in the drawings.
2. v1's outer skin is "Tấm nhôm 2 mm" (aluminium sheet) in the BOM but "ALU DAY 2mm" in the drawings, which in VN trade usually means ACP. This changes v1's weight (2.9 against 5.4 kg/m²) and its sound.
3. v1's fixed glass: the BOM gives 2138.5 × 723.7 mm, which is the bounding box. The finished slanted shape from the STEP is about 1.06 m², not 1.55 m².
4. Panasonic FV-15AUL1 (VT06): the manual forbids ceiling mounting, and no fan curve is published. It's replaced in selection.md.
5. The plan's felt page (DHG, VT03) gives a density of 20–30 kg/m³. That's loose-wool data, not a 9 mm panel, and there's no test standard or certificate.
6. UTEN S300G-1D/S fan speed control is rated 25–300 W phase-cut. It suits neither one FV-15AUL1 (12.5 W) nor EC fans.
7. VT03 is used for both the felt and the 50 × 100 tube in the plan (already on the register).
8. Decor depth: D-39 says 230–235 mm, but v1 measures 205 mm (PM brief; D-39 is being corrected). The 5c1003b fans and cartridges don't fit 205.
9. D-07 still reads acrylic-first; the PM's later ruling made 4+4 laminated glass of toughened, heat-soaked panes the baseline.
10. The 4+4 door has no rated hinge or lock yet (ruling 3, HOLD).
