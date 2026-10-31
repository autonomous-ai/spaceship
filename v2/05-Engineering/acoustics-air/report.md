# Spaceship sound and fresh-air check

Spaceship is the working name for FocusPod v2 ("Indoor Pod").

- **Status:** calculation, not a test. Every number below comes from `calc.py` in this folder, and every input there carries its own status and source. Bought-part data and links are in [`../hardware/selection.md`](../hardware/selection.md).
- **Date:** 2026-10-31.
- **Rerun:** `python3 calc.py` prints every table in this report. `python3 calc.py --verify` rebuilds them and checks that this file quotes each one exactly.
- **Decisions:** DECIDED means the PM ruled on it on 2026-10-31. Decision IDs (D-xx) refer to `v2/00-Control/decision-log.md`; the other rulings were made in the project chat and are being logged. PROPOSED means it still needs a call. HOLD means a supplier or a sample has to confirm it.
- **Fix pass:** the PR #11 version answered Reviewer 3's hold at 5c1003b and applied the PM's 8 rulings on it (2026-10-31).
- **D-60 pass (this version):** rechecks the air path after D-58 (intake low) and D-59 (service from inside). The right decor block's real shape, from skeleton P03, can't hold PR #11's air path, so D-60 moves the silencers inside the pod. Section 7b onward has the layouts, the noise, the sizes, the weight and the recirculation check.

## Results first

1. **v1 as built: about 15 dB speech reduction (D_S,A, range 11–18), not the 30 dB on the product page.** Its open vent slots (35%), door gaps (33%) and raised floor (14%) let out most of the sound. v1's lab test will settle this.
2. **Spaceship as planned: about 14.5 dB (11–17), level with v1.** The light fixes take it to about 16 dB: perimeter and drop seals, sealed glass, joint gaskets, silenced vents, and the thin floor with a base seal. After that, the walls and ceiling carry about 90% of the sound that gets out.
3. **DECIDED build: about 429 kg in this model, 19.3 dB (14.7–21.7).** That's over the 420 kg cap, which stays open until the wall sample settles it (D-54); D-60's air parts add 11.8 kg (section 7f).
   - Walls and ceiling: ACP 3 mm on a 20×40×1.2 aluminium frame at 400 mm, 40 mm PET fill, and a floating lining cassette (0.5 mm steel tray, 25 mm air gap, 9 mm felt).
   - Front: 4+4 laminated glass of toughened, heat-soaked panes, frameless like v1. Hinges and lock are on HOLD until a rated set is named.
   - Air (D-60, DECIDED): four 12 V fans and two splitter cartridges, one in a 217 × 360 mm air column in the front-right inside corner and one in a 360 mm deep soffit above the door head. Intake through a black mesh band piece under the right decor block, exhaust out a roof slot.
   - Smoked acrylic stays an optional experiment on the factory sample: 19.0 dB at about 402 kg.
4. **Why the headline fell from 24.0 to 19.3 dB: the felt data.**
   - The 24.0 used Autex Cube 12 mm data on a 25 mm gap as a stand-in.
   - Ruling 5 asks for the published data of the felt picked. The only published data for a 9 mm, 1.8 kg/m² felt is Polyx Board 9, and it's measured glued flat, which absorbs far less at 125–500 Hz.
   - Our felt sits on a 25 mm gap, which absorbs more, but no data for that is published. So 19.3 is on the safe side and 24.0 is roughly the best case.
   - The wall sample measures the real felt down to 100 Hz and settles it.
   - The range also widened at the bottom: the low case now carries the 125–250 Hz risks (no finite-panel gain, and a 4 dB dip at each double wall's resonance).
5. **30 dB isn't reached anywhere in this search, up to 520 kg (best about 23 dB).** Beyond 420 kg each extra dB costs about 20–30 kg. Low voices (125–250 Hz) limit a light pod, and only mass, cavity depth and low-frequency absorption help there. A thicker felt on the ceiling (24 mm Autex Cube) would add about 1.2 dB; its weight isn't sourced yet.
6. **Air (D-60, DECIDED):**
   - 53 l/s normal at 25.3 dB(A), against the 26 dB(A) target (D-52).
   - The boost: 65 l/s at 29.7 dB(A), and 66 l/s at 30 dB(A) (target 30 or less at 65); 70 l/s would give 31.3 dB(A).
   - One person at 33 l/s hears about 15 dB(A).
   - Two people in a 600 ppm office: 796 ppm at 53 l/s with perfect mixing, 845 ppm at the PM's mixing effectiveness of 0.8. Holding 800 ppm at 0.8 takes about 65 l/s, which is the boost. The supply leaves low at the front-right and the exhaust high at the far end of the soffit, 2.9 m apart, which should mix better than 0.8.
   - Heat: with ELECTRICAL's loads (PR #64: the light shelf and call light, the hub, the supplies' losses and the supply fans), two people need 53 l/s to stay within 4 K of the room and one person 31 l/s, so the 53 l/s normal flow sits right at the heat limit and one person needs more than the 26 l/s floor (D-44). With the voice kit fitted at its full 60 W reserve plus 12 W of supply loss, 4 K needs 69 l/s, over the 65 l/s that the 30 dB(A) boost reaches: 4.2 K at the boost.
7. **Corrections in this fix pass:**
   - The 5c1003b fans were 6 kg S&P TD-500s loose in the decor cavity. Their own casings radiate 44 dB(A), which the old model left out. With it, that design gives 35.8 dB(A) at 53 l/s. They also don't fit: the decor is 205 mm deep (measured from v1), not 230–235.
   - Four 12 V fans at about 0.3 kg each replace them. That saves about 11 kg, which pays for the bigger cartridges and the exhaust riser.
   - D-10's 12 V check was argued at 42 Pa. At the new 12–17 Pa (53 l/s, riser included) a 12 V pair per path works, so the mains fan exception isn't needed.
8. **D-60 recheck (this version):**
   - PR #11 sized the air path to the layout study's 2290 × 1016 × 235 box for the right decor block. Skeletons P03 and P04 show the block following the fixed glass: 145–343 mm wide below Z 1521, with a flat top only 27 mm deep. Two 405 mm cartridges and the riser need 960 mm.
   - Every layout kept inside the decor blocks gave 39–46 dB(A) at 53 l/s, or couldn't reach 53 l/s at all (section 7c).
   - D-60 puts one cartridge in an air column in the front-right inside corner and one in a soffit above the door head. With 50 mm layers, a kick grille at the column's foot, one cartridge size for both, and the intake through a black mesh band piece under the right block (skeleton P04), it gives 25.3 dB(A) at 53 l/s and 29.7 at 65 l/s.
   - The outside doesn't change. Inside, the column takes about 0.08 m² of floor, and the soffit leaves 2120 mm headroom, as at the door.

## 1. The DECIDED stack, for the Layout and Fusion Engineers

Outside to inside. DECIDED by the PM on 2026-10-31 (D-02 weight and sound target, D-05 thin floor, D-09 air, plus rulings in the project chat). D-07 still reads acrylic-first, but the PM's later ruling made 4+4 laminated glass the baseline; that is to be logged.
- aluminium frames at 400 mm, 20 × 40 × 1.2 (the rivnut grip check passed);
- no plywood behind the ACP;
- 0.5 mm lining tray (0.4 mm would cost 1 dB);
- fill at 32 kg/m³ (the lighter 24–25 kg/m³ grade has no published absorption data);
- 4+4 laminated front of toughened, heat-soaked panes (8.76 mm), with the door hardware on HOLD until it's rated (ruling 3);
- the air path of D-60: intake under the right decor block, a riser up that block to the supply fans, the supply cartridge in a felt-covered air column in the front-right inside corner with a kick grille at its foot, the exhaust cartridge and fans in a felt-covered soffit above the door head, and a roof slot (section 7);
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
| Supply cartridge, in the air column (D-60) | 173 × 314 × 1750 | 11.2 |
| Exhaust cartridge, in the soffit (same part) | 173 × 314 × 1750 | 11.2 |
| Air column: faces, fill, frame, grille | 217 × 360 × 2105 | 10.0 |
| Soffit: faces, fill, frame, grille | 2332 × 360 × 220 | 10.0 |
| Intake riser, 1 mm steel, with a mesh allowance | 139–250 × 155 × 1740 | 9.2 |
| Each 12 V fan | 140 × 140 × 25 | about 0.3 (assumption) |
| Door (4+4) | 1176 × 2011 | 47.5 (PM figure), glass is exempt |

The inside ends up about 2332 × 1411 × 2301 mm on skeleton P04: about 4 cm narrower and 7 cm shallower than v1 (2372 × 1480), and 8 cm taller (2223). D-60's air column takes 217 × 360 mm in the front-right corner, and its soffit runs 360 mm deep along the front at 2120 mm headroom, the door head's height.

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
| Tempered 8 mm | 68 | 14.6 | 19.3 | 21.7 | +0.0 |
| Tempered 10 mm (v1) | 86 | 14.6 | 19.3 | 21.7 | +0.0 |
| Laminated acoustic 4+4 (8.76 mm) | 72 | 14.7 | 19.3 | 21.7 | +0.0 |
| Smoked acrylic 8 mm | 33 | 14.3 | 18.7 | 21.1 | -0.6 |
| Smoked acrylic 10 mm | 41 | 14.5 | 19.0 | 21.4 | -0.3 |
| Smoked acrylic 12 mm | 49 | 14.6 | 19.1 | 21.5 | -0.2 |

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
| + all light fixes (plan wall) | 13.0 | 16.3 | 18.7 |
| + fixes, plan wall without plywood | 8.8 | 11.4 | 13.6 |
| + fixes, light double wall DL-HDF | 13.0 | 17.7 | 20.0 |
| + fixes, DL-HDF decoupled | 13.0 | 17.7 | 20.0 |
| + fixes, DL-ST (steel 0.5 inner skin) | 14.6 | 19.3 | 21.7 |
| + fixes, DL-ST decoupled | 14.6 | 19.3 | 21.7 |
| + fixes, honeycomb sandwich SW-HC20 | 3.4 | 5.0 | 6.8 |
| + fixes, foam sandwich + inner skin | 12.0 | 16.9 | 19.3 |
| DECIDED stack, 4+4 laminated front | 14.7 | 19.3 | 21.7 |
| DECIDED stack with the acrylic experiment | 14.5 | 19.0 | 21.4 |

Where the sound gets out (share of the speech energy, central case):

| Path (share of speech sound getting out) | v1 | Plan, 8 mm | Plan + fixes | DECIDED stack |
|---|---:|---:|---:|---:|
| walls | 6% | 41% | 70% | 63% |
| ceiling | 2% | 12% | 20% | 18% |
| glass | 2% | 2% | 3% | 4% |
| front decor | 2% | 3% | 6% | 12% |
| floor | 14% | 6% | 0% | 0% |
| door edge gaps | 22% | 12% | 0% | 0% |
| door bottom | 11% | 6% | 0% | 0% |
| fixed glass edges | 1% | 1% | 0% | 0% |
| panel joints | 5% | 3% | 0% | 0% |
| vents | 35% | 14% | 1% | 2% |
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
| 0 | Spaceship as planned, 8 mm glass | 11.2 | 14.5 | 17.3 |  |  |
| 1 | Door edge seals on 3 sides | 11.6 | 15.0 | 17.9 | +0.5 | 1.0 |
| 2 | Door drop seal | 11.8 | 15.3 | 18.2 | +0.3 | 1.0 |
| 3 | Fixed glass in sealed U-profiles | 11.8 | 15.4 | 18.2 | +0.0 | 0.0 |
| 4 | Gaskets on every panel joint | 12.0 | 15.5 | 18.4 | +0.2 | 1.0 |
| 5 | Silenced vents (D-60: cartridges in the air column and the soffit, intake riser in the right decor block) | 12.7 | 16.3 | 19.0 | +0.8 | 52.5 |
| 6 | Thin floor with base seal (DECIDED, D-05) | 12.9 | 16.2 | 18.7 | -0.1 | 0.5 |
| 7 | Sealed cable holes | 13.0 | 16.3 | 18.7 | +0.0 | 0.1 |

The gains are small one at a time because the plan's single-leaf walls dominate. The same fixes on v1's leaky pod would gain about 6 dB, so they matter as soon as the walls are double. A thicker ceiling absorber (Autex Cube 24 mm) would add about 1.2 dB with today's felt data. Its weight isn't sourced, so it isn't in the stack.

## 6. What each dB costs: the total-pod curve

Total pod kg is the sum of:
- the rest of the pod from the layout study, 102.4 kg: thin floor and base band, decor blocks, door hardware with drop seal and glazing profiles, fans at 1.5 kg, silencer boxes at 1.5 kg each, electrics and the voice-kit reserve;
- the fixes the study doesn't carry, 2.6 kg;
- D-60's air parts (cartridges, air column, soffit, fan boxes, intake riser and roof slot), less the ceiling lining the soffit replaces and the study's boxes;
- the four 12 V fans at about 0.3 kg each, against the study's 2 × 1.5 kg;
- the walls, ceiling and front from this report.

All light fixes are on. The search covers every wall and ceiling in table 2 with each front. In this model D-60's air parts take the DECIDED pod from 418 kg (PR #11's air path) to 429 kg. The layout study's own list comes to about 427 kg before D-60 and about 438.5 kg after it (section 7f; D-54, ISS-080).

Glass front (8 mm tempered or 4+4 laminated):

| Pod budget kg | Best wall / ceiling / front | Total kg | D_S,A low / central / high |
|---:|---|---:|---|
| 280 | nothing fits |  |  |
| 300 | nothing fits |  |  |
| 320 | nothing fits |  |  |
| 340 | SW-FOAM20 / SW-FOAM20 / Tempered 8 mm | 332 | 8.7 / 11.4 / 13.6 |
| 360 | SW-FOAM20 / DL-ST-40-FLG-12 / Tempered 8 mm | 354 | 9.4 / 12.2 / 14.4 |
| 380 | PLAN-NOPLY / DL-ST-40-FLG-12 / Laminated acoustic 4+4 (8.76 mm) | 366 | 9.5 / 12.3 / 14.5 |
| 400 | DL-ST4-40-FLG-12 / PLAN-NOPLY / Tempered 8 mm | 397 | 11.9 / 15.4 / 17.7 |
| 420 | DL-ST4-40-FLG-12 / DL-ST-40-FLG-12 / Tempered 8 mm | 416 | 14.0 / 18.5 / 20.9 |
| 440 | DL-ST-40-FLG-12 / DL-2HDF-60-FL / Tempered 8 mm | 437 | 14.8 / 19.7 / 22.1 |
| 460 | DL-ST-60-FL / DL-2HDF-60-FL / Tempered 8 mm | 457 | 14.8 / 20.3 / 22.7 |
| 480 | DL-2HDF-60-FL / DL-P6-HDF-60-FL / Tempered 8 mm | 479 | 15.7 / 21.5 / 23.9 |
| 500 | DL-P6-HDF-60-FL / DL-P6-P9-60-FL / Tempered 8 mm | 500 | 16.3 / 22.1 / 24.6 |
| 520 | DL-P6-P9-DEC / DL-P6-P9-60-FL / Laminated acoustic 4+4 (8.76 mm) | 519 | 17.4 / 23.1 / 25.6 |

Smoked acrylic 10 mm front:

| Pod budget kg | Best wall / ceiling / front | Total kg | D_S,A low / central / high |
|---:|---|---:|---|
| 280 | nothing fits |  |  |
| 300 | nothing fits |  |  |
| 320 | SW-FOAM20 / PLAN-NOPLY / Smoked acrylic 10 mm | 311 | 8.7 / 11.4 / 13.5 |
| 340 | SW-FOAM20 / DL-ST-60-FL / Smoked acrylic 10 mm | 336 | 9.4 / 12.2 / 14.4 |
| 360 | PLAN-NOPLY / DL-P6-HDF-60-FL / Smoked acrylic 10 mm | 353 | 9.5 / 12.3 / 14.5 |
| 380 | SW-FOAM20-DL / SW-FOAM20-DL / Smoked acrylic 10 mm | 380 | 11.9 / 16.8 / 19.1 |
| 400 | DL-ST-40-FLG-12 / DL-ST4-40-FLG-12 / Smoked acrylic 10 mm | 399 | 14.3 / 18.8 / 21.1 |
| 420 | DL-ST-40-FLG-12 / DL-P6-HDF-60-FL / Smoked acrylic 10 mm | 417 | 14.7 / 19.4 / 21.8 |
| 440 | DL-ST-60-FL / DL-P6-HDF-60-FL / Smoked acrylic 10 mm | 437 | 14.7 / 20.0 / 22.4 |
| 460 | DL-2HDF-60-FL / DL-P6-P9-DEC / Smoked acrylic 10 mm | 459 | 15.7 / 21.1 / 23.6 |
| 480 | DL-P6-P9-DEC / DL-2HDF-60-FL / Smoked acrylic 10 mm | 478 | 16.4 / 21.8 / 24.3 |
| 500 | DL-P6-P9-60-FL / DL-P6-HDF-60-FL / Smoked acrylic 10 mm | 499 | 17.2 / 22.4 / 24.9 |
| 520 | DL-P6-P9-60-FL / DL-P6-P9-60-FL / Smoked acrylic 10 mm | 509 | 17.9 / 22.9 / 25.4 |

Best builds inside the DECIDED rules:

| Case | Walls | Ceiling | Front | Silencer casing | Total kg | D_S,A low / central / high |
|---|---|---|---|---|---:|---|
| DECIDED stack | DL-ST-40-FLG-12 | DL-ST-40-FLG-12 | Laminated acoustic 4+4 (8.76 mm) | aluminium 2.0 mm | 429 | 14.7 / 19.3 / 21.7 |
| Same with 20x40x1.5 frames | DL-ST-40-FLG | DL-ST-40-FLG | Laminated acoustic 4+4 (8.76 mm) | aluminium 2.0 mm | 436 | 14.7 / 19.3 / 21.7 |
| Same with a 0.4 mm tray (rejected: costs 1 dB) | DL-ST4-40-FLG-12 | DL-ST4-40-FLG-12 | Laminated acoustic 4+4 (8.76 mm) | aluminium 2.0 mm | 416 | 13.9 / 18.3 / 20.7 |
| Same, felt flat on the ceiling lining (no gap) | DL-ST-40-FLG-12 | DL-ST-40-FL | Laminated acoustic 4+4 (8.76 mm) | aluminium 2.0 mm | 430 | 14.7 / 19.3 / 21.7 |
| Acrylic experiment: 10 mm with hinge stile | DL-ST-40-FLG-12 | DL-ST-40-FLG-12 | Smoked acrylic 10 mm | aluminium 2.0 mm | 402 | 14.5 / 19.0 / 21.4 |
| Light 0.8 mm cartridge casings (rejected: misses the fan-noise target, section 7d) | DL-ST-40-FLG-12 | DL-ST-40-FLG-12 | Laminated acoustic 4+4 (8.76 mm) | aluminium 0.8 mm | 418 | 14.7 / 19.3 / 21.7 |

- **The curve rises fastest from about 380 to 420 kg:** about 3 dB for every 20 kg. Beyond 420 kg, each dB costs about 20–30 kg.
- **30 dB isn't reached in this search.** At 520 kg the walls and ceiling are double leaves with plywood, and the pod still stops at about 23 dB.
- **The curve is a calculation with about −5 / +2.5 dB of spread.** The low side carries the 125–250 Hz risks and the felt data. The factory's wall-and-door sample is the physical check, and it comes before any further weight goes in.

## 7. Fresh air

### 7a. CO2 and heat

Inside volume 8.35 m3; CO2 from 2 people 10.4 ml/s. The last column uses a mixing effectiveness of 0.8 (PM ruling 8); the others assume perfect mixing.

| Fresh air l/s | Air changes /h | Minutes per change | CO2 rise ppm | CO2 ppm, room 400 | CO2 ppm, room 600 | Minutes to 95% | Heat rise K | Heat rise K with voice kit | CO2 ppm, room 600, mixing 0.8 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 26 | 11 | 5.4 | 400 | 800 | 1000 | 16 | 8.0 | 10.3 | 1100 |
| 40 | 17 | 3.5 | 260 | 660 | 860 | 10 | 5.3 | 6.7 | 925 |
| 53 | 23 | 2.6 | 196 | 596 | 796 | 8 | 4.0 | 5.1 | 845 |
| 70 | 30 | 2.0 | 149 | 549 | 749 | 6 | 3.1 | 4.0 | 786 |

Heat into the air at 53 l/s: two people 257 W, with the voice kit 329 W (people and laptops, the light shelf and call light, the hub, the supplies' losses and the supply fans; ELECTRICAL, PR #64).
Flow that keeps the inside 4 K or less over the room: one person 31 l/s, two people 53 l/s, two with the voice-kit reserve 69 l/s. One person at the 26 l/s floor (D-44), room 600, mixing 0.8: 850 ppm.
CO2 after 2 h at 40 l/s from 400 ppm (room 400): 660 ppm; after 3 h at 26 l/s, room 600: 1000 ppm.

- 800 ppm needs 26 l/s **only when the room air is at outdoor CO2 (400 ppm)** and the air is perfectly mixed. In a 600 ppm office two people need about 52 l/s with perfect mixing, and about 65 l/s at the mixing effectiveness of 0.8 the PM set (ruling 8).
- **Heat also drives the fans (D-44, D-50):** the inside stays at most 4 K over the room. With ELECTRICAL's loads (PR #64) that takes 53 l/s for two people (25.4 dB(A)) and 31 l/s for one person. With the voice kit fitted at its full 60 W reserve and its 12 W supply loss it takes 69 l/s, about 31.1 dB(A), over the 30 dB(A) boost; at the 65 l/s boost the inside is 4.2 K over the room. The kit's real draw, measured when it exists, settles this.
- **Control (D-44):** CO2 leads, with a floor of 26 l/s while one person is inside. Temperature can raise the flow. 53 l/s for two, and a boost of up to 65 l/s inside 30 dB(A).
- **Supply low, exhaust high (D-60, DECIDED):** the supply leaves through a kick grille at the foot of the air column in the front-right corner, so the cool room air spreads across the floor. The exhaust grille sits in the soffit's underside at its far end, above the door's hinge side, 2.9 m away, and takes the warm, stale air out. That should mix better than the 0.8 used here.

### 7b. The right decor block's real shape (D-58 and D-59 recheck)

D-58 moved the room-side intake low and D-59 asked for service from inside. Rechecking the PR #11 air path against them showed it doesn't fit. PR #11 sized it to the layout study's F-DR box, 2290 × 1016 × 235. Skeleton P03, measured from v1, shows the block's glass-side edge following the fixed glass:

| Height Z mm | Glass-side edge X mm | Clear width for a 159 mm deep cartridge mm | Clear width at the full 199 mm depth mm | Inner face seen from inside mm |
|---:|---:|---:|---:|---:|
| 115 | 946 | 146 | 102 | 220 |
| 500 | 892 | 200 | 156 | 274 |
| 1000 | 822 | 270 | 226 | 344 |
| 1521 | 749 | 343 | 299 | 417 |
| 1800 | 507 | 585 | 541 | 659 |
| 2117 | 233 | 860 | 815 | 933 |

Inside its skins the block holds 0.20 m3. Its flat top is the strip from Y -672 to -645, 27 mm deep; the rest of the top is the chamfer. PR #11's layout needs 960 mm of width over 2100 mm, 0.32 m3 with the fan boxes and riser.

- Below the fixed glass's knee (Z 1521) the block is a column 145–343 mm wide behind its inner face. It reaches 860 mm only just under the top block.
- Its flat top is 27 mm deep. A slot there has about 0.012 m² free, so it can't take the exhaust at low speed.
- The left block (189 mm wide at 100 mm deep, and the door hinges fix into it) and the top block (0.030–0.038 m² inside) are thinner still.

### 7c. Layouts compared

Same fans, same methods and the same conservative felt data as PR #11. Sizes for (a) to (c) come from the clear widths above.

| Layout | Where the air path runs | At 53 l/s dB(A) | At 65 l/s dB(A) | At 33 l/s dB(A) | Flow at 26 dB(A) l/s | Flow at 30 dB(A) l/s | Fan speed at 53 l/s, supply / exhaust |
|---|---|---:|---:|---:|---:|---:|---|
| PR #11 (D-51), taking the right block as a 1016 x 2290 box | two 405 mm cartridges and a riser in the block: doesn't fit | 25.8 | 30.2 | 15.5 | 54 | 64 | 64% / 73% |
| (a) right block only | supply up the block's column; exhaust in its upper part, out the 27 mm top strip | 45.6 | out of reach | 35.3 | 21 | 26 | 98% / 95% |
| (b) right and left blocks | supply in the right block; exhaust up the left block and across the top block | out of reach | out of reach | 34.6 | 22 | 27 | out of reach |
| (c) right and top blocks | supply in the right block; exhaust along the top block | out of reach | out of reach | 32.9 | 24 | 29 | out of reach |
| (c) improved, exhaust out a roof slot: the best inside the decor | as (c), with the column as a plain duct and bigger openings | 39.0 | out of reach | 28.7 | 29 | 35 | 82% / 84% |
| (e) D-60 as sized here | an air column in the front-right inside corner and a soffit above the door head | 25.3 | 29.7 | 15.0 | 55 | 66 | 73% / 65% |

- **Every layout kept inside the decor fails.** The passages are narrow, so the pressure rises two to three times and the fans run at 80–100%, and the lined legs on the pod side of the fans are short. The best, (c) with a roof slot, gives 39.0 dB(A) at 53 l/s.
- **D-60 (DECIDED by the PM, 2026-10-31):** the silencers move inside the pod, into an air column in the front-right inside corner and a soffit above the door head. The outside look doesn't change.
- The PR #11 row shows what a box-shaped block would have given: 25.8 dB(A) here, 25.6 in PR #11's own model, which leaves out its riser's friction.

### 7d. D-60: noise inside

Targets (D-52): 26 dB(A) or less at 53 l/s and 30 or less at the 65 l/s boost, at a seated head.

| Flow l/s | Supply fans: speed, pressure | Supply duct / breakout / total dB(A) | Exhaust fans: speed, pressure | Exhaust duct / breakout / total dB(A) | Inside, both paths dB(A) |
|---:|---|---|---|---|---:|
| 26 | 36%, 4 Pa | 5.0 / 5.0 / 8.0 | 32%, 3 Pa | 2.5 / 1.6 / 5.1 | 9.8 |
| 33 | 45%, 7 Pa | 10.2 / 10.2 / 13.2 | 40%, 5 Pa | 7.7 / 6.8 / 10.3 | 15.0 |
| 53 | 73%, 18 Pa | 20.5 / 20.5 / 23.5 | 65%, 12 Pa | 18.0 / 17.1 / 20.6 | 25.3 |
| 65 | 90%, 27 Pa | 24.9 / 24.9 / 27.9 | 79%, 18 Pa | 22.4 / 21.5 / 25.0 | 29.7 |
| 70 | 96%, 31 Pa | 26.5 / 26.5 / 29.5 | 86%, 21 Pa | 24.0 / 23.1 / 26.6 | 31.3 |

Two fan signals keep both paths at the same flow: at 53 l/s the supply pair runs at 73% and the exhaust pair at 65%. One shared signal would run both at about 69% and leave the pod 2.7 Pa below the room at 53 l/s (4.1 Pa at 65 l/s).
Flow at 26 dB(A): 55 l/s; at 30 dB(A): 66 l/s (targets, D-52: 26 dB(A) or less at 53 l/s, 30 or less at the 65 l/s boost). With a 5 dB fan tone at 250 Hz (risk): 28.7 dB(A) at 53 l/s and 56 l/s at 30 dB(A).

The cartridge, the same part on both paths:

| Cartridge casing | Air parts kg | Passage IL 125 | 250 | 500 | 1k | 2k | 4k dB | Casing + 30 mm fill + felt-covered face R 125 | 250 | 500 | 1k | 2k | 4k dB | At 53 l/s dB(A) | Flow at 30 dB(A) l/s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| aluminium 2.0 mm (pick) | 60.6 | 3 | 13 | 28 | 32 | 29 | 28 | 14 | 20 | 31 | 48 | 55 | 46 | 25.3 | 66 |
| aluminium 0.8 mm | 49.3 | 3 | 13 | 28 | 32 | 29 | 28 | 10 | 16 | 23 | 41 | 51 | 42 | 30.0 | 53 |

Pressure per path, supply / exhaust: 26 l/s 4 / 3 Pa; 53 l/s 18 / 12 Pa; 65 l/s 27 / 18 Pa. At full speed the supply pair reaches 73 l/s and the exhaust pair 82 l/s.

- **Supply.** Room air comes in through the front base band piece under the right block, which becomes a flush black mesh with the band's outline (PM, on skeleton P04), into the space under the block; a plate at Y −645 closes that space from the pod. It rises up a 1 mm steel riser behind the air column to two NF-A14 fans in a lined box high in the block, behind its removable inner face. The fans blow through an opening in the block's inner face into the top of the air column, down its cartridge and out of a 100 mm kick grille at the column's foot, so the cool room air spreads across the floor.
- **Exhaust.** Air leaves the pod through a grille in the soffit's underside at its far end, above the door's hinge side. It runs the length of the soffit's cartridge to two NF-A14 fans lying flat in the soffit's right end, which blow straight up through a roof slot 2.3 m above the intake.
- **One cartridge for both paths:** 173 × 314 × 1750 mm, a 2 mm aluminium casing, and two 80 mm passages between three 50 mm Pyrotek Sorberpoly 2D layers (published ISO 354 data, so nothing is interpolated). At 125–250 Hz, where the fan noise left after a splitter sits, 50 mm layers absorb about twice what 25 mm layers do.
- **Why 2 mm casings.** The cartridges now sit inside the pod, behind 30 mm of fill and a felt-covered face, so the casing is their main barrier. 0.8 mm casings would save about 11 kg but give 29.9 dB(A) at 53 l/s.
- **Where the noise comes from at 53 l/s:** about two thirds from the supply path (23.5 dB(A)), half through the kick grille and half as breakout from the column, riser and fan box. The exhaust gives the other third (20.6 dB(A)).
- **One person** at 33 l/s hears about 15 dB(A), and the 26 l/s floor about 10.
- **Risks (HOLD):** the fans have no octave data (a 5 dB tone at 250 Hz would give 28.7 dB(A) at 53 l/s), the fan curve is a straight line, and the splitter derating (0.8) and the bend and grille losses are assumptions. The fan-sample test measures a fan pair in its box on a cartridge: flow against pressure, and octave sound power at 53 and 65 l/s.

### 7e. Sizes for the CEILING and FRONT Engineers

The CEILING Engineer models the air column, the soffit, the cartridges in them and the roof slot. FRONT and BASE model the intake: the mesh band piece under the right block, the block's support behind it and the closing plate (PM, 2026-10-31). Status: calculation; the fan data and the felt on its gap are HOLD for the samples.

**Intake route.** Skeleton P04 runs the front base band flush under the right block and along its corner facet, so room air can only come in through that band piece. The PM chose the flush black mesh (2026-10-31):

| Intake route | Free area m2 | Speed at 53 l/s m/s | At 53 l/s dB(A) | At 65 l/s dB(A) | Flow at 30 dB(A) l/s |
|---|---:|---:|---:|---:|---:|
| The 10 mm glide gap under the band only (skeleton P04 as it is) | 0.0037 | 14.3 | out of reach | out of reach | 24 |
| The band piece under the block becomes a flush black mesh with the same outline (DECIDED) | 0.0282 | 1.9 | 25.3 | 29.7 | 66 |
| The band stops short under the block, with a mesh set back | 0.0301 | 1.8 | 25.2 | 29.6 | 66 |
| A louvred band piece | 0.0193 | 2.7 | 26.6 | 31.0 | 62 |

The band piece under the block is 371 mm long (skeleton P04). Open heights and free ratios are assumptions until the mesh is picked.

| Item | Size mm | Where (pod coordinates, mm) | Notes |
|---|---|---|---|
| Air column, outer | 217 x 360 x 2105 | X 949 to 1166, Y -645 to -285, Z 15 to 2120 | front and left faces felt-covered (12 mm: 3 mm ACP + 9 mm felt); the front face lifts off full height for service; back on the right block's inner face, right side on the side lining |
| Supply cartridge | 173 x 314 x 1750, 11.2 kg | X 988 to 1161, Y -640 to -326, Z 135 to 1885 | 2 mm aluminium casing; two 80 mm passages running up and down between three 50 mm Pyrotek Sorberpoly 2D layers parallel to the front face; 27 mm polyester fill to the front and left faces; 5 mm clear on the other sides to slide it out |
| Kick grille, supply out | 100 tall x 529 along the front and left faces | Z 25 to 125 | 0.032 m2 free or more (60%); base plenum Z 15 to 135 under the cartridge |
| Opening from the right block into the column top | 200 x 215 | in the block's inner face at X 961 to 1161, Z 1895 to 2110 | supply air from the fan box; column top plenum Z 1885 to 2120 |
| Sensor hub and controls | 180 x 180 zone, up to 29 deep | on the column's front face, centred X 1058, Z 1200 | no fill behind it; a 30 x 30 mm cable chase in the column's front-left corner runs up to the top plenum and on to the fans; the supply fan inlet sensor (D-50) sits in the fan box inlet |
| Supply fans and box | 300 x 155 x 300 | X 645 to 945, Y -847 to -692, Z 1650 to 1950, inside the right block | two Noctua NF-A14 industrialPPC-3000 PWM on a level bulkhead, blowing up; 2 mm aluminium, 50 mm lining; 44 mm fill to the block's inner face, which lifts off here (D-59); a transition carries the air right to the opening |
| Intake riser | 139 to 250 wide x 155 deep x 1740 | X 955 to 1094, Y -803 to -648, Z 105 to 1445, behind the column; then it widens and turns into the fan box inlet below Z 1650 | 1 mm galvanised steel, 0.021 m2 free or more |
| Intake (FRONT and BASE) | band piece 371 long x 100 tall | the front base band under the right block: its front face from X 947 to 1052 and along the corner facet, Z 10 to 110 | a flush black mesh with the band's outline, 80% free over 95 mm, 0.028 m2 free (PM, 2026-10-31); the block gets its own support behind it (BASE); a closing plate at Y -645 from Z 15 to 110 separates the space under the block from the pod; the riser opens down into that space |
| Soffit, outer | 2332 x 360 x 220 | X -1166 to 1166, Y -645 to -285, Z 2120 to 2340 | underside and front face felt-covered, front face flush with the column's; the underside lifts off in sections; the ceiling lining cassettes start at Y -285 (1051 long); headroom 2120, as the door head |
| Exhaust grille | 265 x 336 | soffit underside, X -1150 to -885, Y -633 to -297 | 0.036 m2 free or more (40%) |
| Exhaust cartridge | same part, lying along X | X -883 to 867, Y -640 to -326, Z 2159 to 2332 | passages along X; fill and clearances as the column |
| Exhaust fans and box | 294 x 314 x 173 | X 867 to 1161, Y -640 to -326, Z 2162 to 2335, the soffit's right end | two NF-A14 lying flat, blowing up into the roof sleeve; 2 mm aluminium, 50 mm lining |
| Roof slot (CEILING) | 285 x 294 | through the roof panel above the exhaust box, X 872 to 1157, Y -630 to -336 | sleeve through the 14 mm gap and the 46 mm roof panel; grille 50% free or more, 0.040 m2 free; 2.3 m above the intake |
| Clearances |  |  | 5 mm round each cartridge and fan box; door top Z 2116 to the soffit 4 mm, so check the door's swing; the soffit top, Z 2340, is 14 mm under the roof panel |

**What shows from outside.** Only the soffit's underside shows, never its front face, which faces into the pod. The underside runs at Z 2120, flush with the top block's underside behind the glass. In the top band's dark tone it reads as the top band running deeper (PM, D-60). How much of the glass shows it:

| Viewer outside | Glass band that shows the soffit's underside, Z mm | Glass height showing it mm |
|---|---|---:|
| standing, eye 1650 mm, 1 m from the glass | 1982 to 2096 | 114 |
| standing, eye 1650 mm, 2 m from the glass | 2039 to 2108 | 68 |
| standing, eye 1650 mm, 4 m from the glass | 2076 to 2114 | 38 |
| seated, eye 1200 mm, 1 m from the glass | 1851 to 2073 | 222 |
| seated, eye 1200 mm, 2 m from the glass | 1962 to 2096 | 134 |
| seated, eye 1200 mm, 4 m from the glass | 2034 to 2108 | 74 |

### 7f. Weight

| Part | Size mm | kg | Basis |
|---|---|---:|---|
| Supply cartridge, in the air column | 173 x 314 x 1750 | 11.2 | aluminium 2.0 mm casing, three 50 mm layers at 40 kg/m3 |
| Exhaust cartridge, in the soffit | same | 11.2 | same part |
| Air column: felt-covered faces, fill, frame, kick grille, hub plate | 217 x 360 x 2105 | 10.0 | faces 3 mm ACP + 9 mm felt; 30 mm fill; 4 corner angles; 0.6 kg grille and plate (assumption) |
| Soffit: felt-covered faces, fill, frame, exhaust grille | 2332 x 360 x 220 | 10.0 | underside and front face as the column; 2 angles; 0.5 kg hangers and 0.4 kg grille (assumption) |
| Supply fan box and transition, in the right block | 300 x 155 x 300 + transition | 5.1 | 2 mm aluminium, 50 mm lining; transition 0.35 m2 (calculation) |
| Exhaust fan box and roof sleeve, in the soffit | 294 x 314 x 173 | 3.5 | 2 mm aluminium, 50 mm lining |
| Intake riser with a mesh allowance, in the right block | 139-250 x 155 x 1740 | 9.2 | 1 mm galvanised steel; 0.5 kg for its foot and the mesh band piece's extra over the band it replaces (assumption) |
| Roof slot grille and sleeve | 285 x 294 | 0.5 | assumption |
| Four 12 V fans | 140 x 140 x 25 | 1.2 | 0.3 kg each (assumption) |
| **Air parts in all** |  | **61.8** | heaviest part under the 20 kg rule: 11.2 kg |
| Less the ceiling lining the soffit replaces | 2332 x 360 | -5.0 | 0.5 mm tray, returns and felt |
| Less PR #11's cartridges, fill, riser and fans |  | -45.0 | the model's earlier air parts |
| **Change to the pod** |  | **+11.8** | the DECIDED stack in this model goes to 429 kg |

The layout study carries PR #11's air parts at 45.0 kg (its `hw_air_kg`). With D-60 its 426.7 kg becomes about 438.5 kg, still open against the 420 kg cap (D-54, ISS-080). Every D-60 part stays under the 20 kg rule.

### 7g. Recirculation check (D-58, ISS-078)

| Check | Value | Basis |
|---|---|---|
| Intake to roof slot, height apart | 2.29 m | Z 110 to 2400 (skeleton P04); D-58 asks 1 m or more |
| Intake capture distance at 65 l/s, where its pull falls to 0.1 m/s | 0.45 m | quarter-sphere sink at the floor and the pod's front, v = Q / (pi r^2); 0.1 m/s room air (assumption) |
| Exhaust leaving the roof slot at 65 l/s | 1.6 m/s, upward | 0.040 m2 free |
| Exhaust over the room at boost | 4 K or less | D-50 holds the inside within 4 K of the room |
| Largest recirculated share that keeps the inlet within 0.5 K | 12.5% | 0.5 K / 4 K (D-58's test limit) |
| Supply kick grille to exhaust grille, inside the pod | 2.9 m | short-circuit inside the pod |

How it's checked:
1. **Calculation (above).** The exhaust leaves 2.3 m above the intake, moving up at 1.6 m/s and up to 4 K warmer than the room, so it rises away. At boost the intake draws from within about 0.45 m of the shadow gap, where the room's coolest air is. For the inlet to read 0.5 K warm, 12.5% of the exhaust would have to come back down to the floor at the pod's front-right corner. It can only get there after mixing into the room, so the expected share is well under 1%.
2. **Test, on the fan sample or the prototype.** At the 65 l/s boost, heat the inside to 4 K over the room (two 150 W heaters, or people) and log for 30 minutes: the supply fan inlet sensor, the room at 1.1 m height 1.5 m in front of the pod and out of the exhaust plume, and the roof slot. Pass: the inlet stays within 0.5 K of the room. As a second check, raise the inside CO2 to about 1500 ppm; the inlet's CO2 stays within 30 ppm of the room's, a recirculated share under about 3%.
3. **Smoke.** A smoke pencil at the roof slot and at the shadow gap shows the plume going up and the intake drawing from the floor.

### 7h. Servicing, pressure and controls

- **Servicing (D-59), all from inside.** The column's front face and the soffit's underside lift off. Each cartridge (11.2 kg) slides out into the pod. The supply fans come out through the right block's inner face beside the column top, and the exhaust fans drop out of the soffit. Nothing on the walls or the outside comes off.
- **Pressure balance and the door.** The hub drives the two fan pairs with two signals, so both paths move the same flow and the pod stays near room pressure (section 7d). One shared signal would leave the pod about 2.7 Pa below the room at 53 l/s, about 3 N at the door handle; a 5 Pa difference adds about 6 N.
- **Controls.** The in-house Desk Pro AI sensor hub (D-09) sits on the air column's front face at seated eye height (Z 1200), with the boost button below it. It reads the room air 1.1 m above the kick grille, shows CO2 inside, and drives both fan pairs through the column's cable chase.
  - 26 l/s floor with one person (D-44), 53 l/s for two, more on CO2 or temperature, boost by hand, up to 66 l/s inside 30 dB(A).
  - The supply fan inlet sensor (D-50) sits in the fan box inlet, so it reads the intake air from the floor.
  - Run-on of 15–30 min after the last presence.
  - The hub's fan output has to suit PWM fans; the exact interface belongs to the electrical scope (HOLD).
  - The plan's UTEN S300 "triết áp quạt" (S300G-1D/S, phase-cut for 25–300 W) doesn't suit these fans and is replaced.

### 7i. PR #11's fan options, with the block taken as a box (for the record)

| Fans and cartridges (PR #11, right block taken as a box) | Fits the real right block | Fans kg | Cartridges, fill, riser kg | At 53 l/s: fan speed supply / exhaust | At 53 l/s: duct / breakout / total dB(A) | Boost flow at 30 dB(A) l/s | At 70 l/s: total dB(A) |
|---|---|---:|---:|---|---|---:|---:|
| 2 x S&P TD-500/150-160 SILENT, 4 V, as at 5c1003b, with casing sound | no (ØD 221 mm) | 12.0 | 29.8 | 4 V | 23.4 / 35.5 / 35.8 | 41 | 41.8 |
| Exhaust high with a riser: exhaust fans at the foot, 150 mm steel riser, 405 mm cartridges (D-51, replaced by D-60) | no: needs 960 mm | 1.2 | 43.8 | 64% / 72% | 22.6 / 22.5 / 25.6 | 65 | 31.6 |
| Same, with a 5 dB fan tone at 250 Hz (risk) | no: needs 960 mm | 1.2 | 43.8 | 64% / 72% | 26.2 / 25.9 / 29.0 | 55 | 35.1 |
| Both grilles low, no riser, 450 mm cartridges (not chosen: exhaust low) | no: needs 900 mm | 1.2 | 37.2 | 60% / 60% | 20.2 / 19.4 / 22.8 | 74 | 28.9 |
| Exhaust in the top block, no riser: 266 mm wide, 1.35 m, two fans in series (they can't sit side by side) | no: the top block is 119 to 199 mm deep | 1.2 | 28.5 | 60% / 94% | 29.8 / 25.6 / 31.2 | 50 | out of reach |

- The 12 V fans stay: the S&P TD-500s of 5c1003b are 221 mm across and their casings radiate 44 dB(A).
- **Breakout method** (all rows and D-60): ASHRAE's rectangular-duct formula through the casing alone; the fill and the face toward the pod count only in bands fully above the double wall's f0. A fan box is a reverberant box behind the same double wall.

## 8. Hooks for the later voice cockpit kit

Mic array, speakers, screen and status light. Reserved here; the kit itself isn't designed.
- **Power:** 12 V 5 A (60 W) on the 12 V bus (D-11), the same as the layout study, plus about 12 W of supply loss (ELECTRICAL). Both are in the heat figures above (+0.9 K at 70 l/s).
- **Cable path:** the 25 mm gap inside each lining cassette carries cables behind the felt without touching the outer wall. Cassettes lift off with no tools. The ceiling cassettes link the back wall to the soffit (D-60), and the air column's cable chase carries the sensor hub's cables.
- **Mounting points:** M6 rivnuts in the 20 × 40 aluminium members, one bolt size, at positions the Layout Engineer fixes. The screen goes on the back wall and the status light on the front decor top block.
- **Sound:** speakers and mics mount on the lining cassette, never through the ACP skin. A hole through the outer leaf would be a new leak, about 0.1 dB for a 28 mm hole. The 26 dB(A) fan target also helps the mic array.

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
| Silencer attenuation | Sabine formula × 0.6–1.0, capped at 40 dB per band; D-60: two 80 mm passages between 50 mm Pyrotek layers, P/S 25 per m (PR #11: 25 mm layers, P/S 50) | no product data for this splitter | factory mock-up of one cartridge with its fans |
| Breakout from the cartridges | ASHRAE duct breakout through the 2 mm casing alone; the 30 mm fill and the felt-covered face count only above f0; the intake riser behind the air column gets the same filled double wall; the side faces' flanking is taken as covered by the face mass left out | standard method, conservative at 125–250 Hz | the same mock-up, measured inside the pod |
| Fan sound at our duty | maker's 41.3 dB(A) read as sound pressure at 1 m (LwA = LpA + 11), TD-500 spectrum shape, 50 lg of speed | no octave data for 12 V fans | fan-sample test: octave sound power and tones |
| Fan duty point | straight-line curve between the maker's free-air flow and maximum pressure; PR #11's system loss K = 7.5 | the maker gives two points only | fan-sample test: flow against pressure |
| D-60 path losses | each part at its own speed: splitter entry 0.5, exit 1.0 and 2.0 per 1.8 m of 40 mm passages, scaled by length over passage width; 0.8 per 90° bend; duct friction 0.02; each grille 2.0 | PR #11's values, split by part; standard values | fan-sample test with a cartridge and its grilles |
| D-60 grilles and openings | kick grille 60% free, exhaust grille 40%, roof slot 50%, intake mesh band 80% over 95 mm of its height | typical for perforated and bar grilles and coarse mesh | the grilles' data when they're picked |
| D-60 felt-covered faces | 3 mm ACP and 9 mm felt, with 30 mm polyester fill behind | the same build as the decor's inner face | the CEILING model and the fan sample |
| CO2 per person | 5.2 ml/s | matches the brief's 26 l/s for 800 ppm | CO2 logger on the prototype |
| Heat per person | 75 W sensible + 30 W laptop | seated office work | temperature logger on the prototype |
| Acrylic sound data | Sharp model | published PMMA figures contradict each other | door sample test |
| 125–250 Hz model risks | low case: no finite-panel gain, 4 dB dip at f0 | Reviewer 3 P2-4, ruling 5 | wall sample measured down to 100 Hz |
| Mixing effectiveness | 0.8 for CO2 | PM ruling 8 | CO2 logger on the prototype |
| Decor section | 205 mm deep, 3 mm faces, 199 mm clear; the right block follows the fixed glass (skeleton P03) | measured from v1 | the CEILING and FRONT models |
| Recirculation | capture distance from a quarter-sphere sink at the floor, against 0.1 m/s room air | standard first estimate | the recirculation test (section 7g) |

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
  - D-60 recheck: each path is a chain of parts with their own sizes (splitter, lined duct, plain duct), a fan box and its two openings. Pressure is summed part by part at each one's own speed. The duct path runs through the parts on the pod side of the fans; every part facing the pod adds breakout, with the sound power it carries at that point. This reproduces PR #11's design at 25.8 dB(A) against its 25.6; the difference is the riser's friction (0.8 Pa).
- **Weights:** the rest of the pod comes from the layout study (branch super-tab/7667a51, commit cb7009f, work in progress). Wall build-ups, glass and fixes come from this report. D-60's air parts are summed from their sheet, lining and face areas (section 7f).
- **The right block's shape:** from skeleton P03's parameters (measured from v1): the glass-side edge along the fixed glass, the corner facet, the joint to the top block and the top chamfer, each inside the 3 mm skins.

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
11. The layout study's F-DR (2290 × 1016 × 235) and D-51's layout took the right decor block as a box. Skeletons P03 and P04 show it 145–343 mm wide below Z 1521, with a 27 mm flat top. D-60 replaces the layout, so REQ-AIR-05 and REQ-AIR-07 need D-60's numbers and placement: 25.3 dB(A) at 53 l/s, 29.7 at 65 l/s, 66 l/s at 30 dB(A), and the column, soffit, intake and roof slot of section 7e. D-60's own row still gives a 200–235 mm soffit and 29.5 dB(A); the PM's later rulings set the 360 × 220 soffit, the supply fans high in the right block and the mesh band intake.
12. The soffit's underside shows through the top 68–114 mm of the glass from a standing viewer 1–2 m away. Its finish is the top band's dark tone (PM, D-60).
13. The layout study carries PR #11's air parts at 45.0 kg and the ceiling cassettes at full length. D-60 needs 61.8 kg of air parts and ceiling cassettes 1051 mm long (skeleton P04's 1411 less the soffit's 360), +11.8 kg net, taking its 426.7 kg to about 438.5 kg.
14. If the door swings into the pod, its top edge (Z 2116) passes 4 mm under the soffit: the CEILING model checks the swing.
15. On skeleton P04 the front band closes the space under the right block, so the intake comes in through that band piece, made a flush black mesh with the band's outline (PM, 2026-10-31). The block needs its own support behind the mesh (BASE), and a closing plate at Y −645, Z 15 to 110, between that space and the pod (FRONT and BASE).
