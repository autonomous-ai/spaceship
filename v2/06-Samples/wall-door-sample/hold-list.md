# HOLD list: what waits, who releases it, and when

| Doc code | Revision | Status | Date |
|---|---|---|---|
| V2-SMP-WD (proposed) | P01 | DRAFT | 2026-10-31 |

A HOLD stops the item or test it blocks; nothing is guessed around it. Each one has an owner, a scope and a release condition (guideline §13). D-56 lists the project-wide HOLDs, and those carry their issue numbers here. Items marked **new** have no issue row yet: the control pack registers them (`issue-register.csv` belongs to the control pack). The owner does the work, and the PM lifts the HOLD on the evidence named (D-32).

| ID | On HOLD | Blocks | Owner | Released when | Ref |
|---|---|---|---|---|---|
| H01 | Door hinges, lock and pull rated for the 8.76 mm laminate of toughened, heat-soaked panes, the 47.5 kg unit and the 1176 mm width. The candidate dormakaba OFFICE 11.233 is listed for toughened 8 or 10 mm only. | S4, T13 | Hardware Engineer (question list for the factory) | A set rated for all three is named, with its data sheet | D-46, D-56; ISS-002 |
| H02 | The 4+4 glass product: grey, toughened and heat-soaked, with an acoustic interlayer if it is offered toughened | S4, T13 | Hardware Engineer; the factory gets the supplier's answer | The product is named with its heat-soak certificate, edge work and hole data | D-56; ISS-074 |
| H03 | A cassette clip with a rated load and a captive lock, and its fixing to the 0.5 mm tray return. Candidate: Häfele KEKU EH, with no stated rating basis or pull-out rating. | S2, S3, T07, T11 | Hardware Engineer | A clip is named with its rated shear and pull-out loads, the basis of the rating, and its tray fixing; T07 then checks it | D-47, D-56; ISS-076 |
| H04 | The ceiling safety catch: a steel lanyard with a rated working load, and its fixings to the cassette return and the 20 × 40 ceiling member | S3, T08 | Hardware Engineer | A catch is named with its rating, and the selection's fixing to a 20 × 100 member is corrected to 20 × 40 | D-47, D-56; ISS-076, ISS-079 |
| H05 | The rivnut tightening torque | The torque used on S1 and in T11 | The PM, from T06 | T06 is done and the PM sets the torque | D-48, D-56; ISS-011 |
| H06 | The 12 V fans' octave data | The published noise figure (REQ-AIR-05) | Hardware Engineer, through T04 | T04 is done, or the maker's octave data is on file | D-56; ISS-077 |
| H07 | The fit of the cartridges, fan boxes, riser, grilles and removable inner panel inside the 205 mm right decor block (199 mm clear) | S5's final geometry and drawings D08, D09. R3 waits for the Air Engineer's size table under D-60 (interior air column and soffit); it is not built to the old sizes. | Fusion Engineer, with the Hardware Engineer | The fit is shown in CAD with a clearance check | D-56, D-59; ISS-078 |
| H08 | The felt's emission certificate | The felt's release (REQ-MAT-01). It doesn't block the build. | Hardware Engineer; the factory gets the certificate | The certificate is on file with its standard and number | D-56; ISS-075 |
| H09 | How the felt's edges fix to the tray returns. It isn't designed. | S2, S3, the R3 inner panel | Fusion Engineer (drawing), Hardware Engineer (the fixing and its spec) | A fixing is chosen, either a bond with its spec (guideline §8.2) or a mechanical strip, and drawn in D05 and D06 | new |
| H10 | How the 40 mm fill fixes to the ceiling cassette's back (D-24). It isn't designed. | S3, T08 | As H09 | Drawn in D06, and it stays on through T08 | new |
| H11 | How the 20 × 40 × 1.2 frame members join each other: welded, cleated, riveted or otherwise. It isn't decided. The Phase 0 proof frame was welded 20 × 20 steel, a different build. | S1, drawing D03 | Fusion Engineer and Hardware Engineer propose; the PM decides | A joint decision with its register entry (guideline §8), drawn in D03 | new |
| H12 | The bond's bead and tape pattern, and its coupon (HW-SEL A9) | S1's bonding, T09 | Hardware Engineer | The pattern is in the bond spec D10, and T09 passes | HW-SEL A9 |
| H13 | The captive M6 bolt and the tool-free seam connector. No parts are named. | The captive and clip timings in T11. Plain bolts meanwhile. | Hardware Engineer | Parts are named with their loads and their pull-out on the aluminium frame | LS-03 (layout study) |
| H14 | The gasket's converter: PORON 4701-40 laminated with PSA in 10 to 20 mm strips | The gaskets on S1, S2 and S3 | Hardware Engineer | A converter's strip is named with its data sheet | HW-SEL D |
| H15 | The tube's alloy, temper and finish | S1, S7. The results hold only for the alloy tested. | Hardware Engineer; the factory records what it uses | The alloy and finish are recorded and decided | ISS-034 |
| H16 | The ACP's real kg/m² and core type | S1's mass, T10 | The factory weighs it in T10; the Hardware Engineer asks the maker (question 1) | T10's weight, or the maker's data | HW-SEL A1 |
| H17 | The base band joint and the panel's locating features (pins, hooks or a rebate). They aren't designed. | R1, S1's base, T11 | Fusion Engineer (BASE drawing) | Drawn in D12 | REQ-ASM-04; new |

Not a HOLD, but decided by a test: whether each cartridge splits in two with a sealed slip joint (D-59, T12), and whether the lighter fill replaces the 32 kg/m³ (D-54, T02).
