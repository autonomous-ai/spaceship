# BASE sample tests

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-BASE-TP | P02 | PLANNED | 2026-11-01 | BASE Engineer |

Physical tests for the BASE parts of the factory sample. The floor's tests (panel edge load, chair castor) went with the floor (D-132: no floor); the seal test BT-06 now checks the lip on the room floor. Every test is **PLANNED / NOT TESTED** until the factory records real data (guideline §10). The pass marks are assumptions until the PM confirms them. The wall-and-door sample package (`v2/06-Samples/wall-door-sample/test-plan.md`) runs its own tests; these add what BASE needs.

| ID | What | Sample | Method | Pass mark | Feeds | Status |
|---|---|---|---|---|---|---|
| BT-03 | Rivnut in the 1.5 mm band | A 300 mm piece of the 100 × 40 × 1.5 band, 3 rivnuts CAH3-610-4.2 set through 1.5 mm stop washers | Torque to spin-out, and axial pull-out, on each rivnut | Records the values that set the rivnut torque (HOLD-01); added to the joints rivnut test T06 as its 1.5 mm coupon (PM ruling) | J-BASE-01, HOLD-01 | PLANNED |
| BT-04 | Glide on its doubler | A band piece with one glide, its M10 rivnut and the 3 mm doubler | 1500 N (three times the ~500 N glide load) on the glide for 1 minute | Bottom face set under 0.1 mm after unloading; rivnut doesn't turn (assumption) | FD-01 | PLANNED |
| BT-05 | Band levelling | The band pieces of the sample on their glides on the factory floor | Set the glides from above with the 5 mm key; measure the band top at each glide | Band top level within ±1 mm over the sample, in 10 minutes or less (layout study t_level_min) | D-87 (glides preset), layout study | PLANNED |
| BT-06 | Lip seal on the room floor, across the glides' range (D-132) | A side band piece (at least 600 mm, with its back end) on 2 glides on a flat concrete floor, the 118001 lip bonded along its inner face, and the back band's end butted to it with its own lip | Set the band's bottom at 8.5, 13.5 and 18.5 mm above the floor with the glides; at each, check the fin's contact along its whole length with a 0.1 mm feeler and a lamp from the inside; check the butt joint the same way; leave it 24 h at 8.5, then set 18.5 and check again | Continuous contact at all three heights and at the butt; the fin doesn't fold under at 8.5 and springs back to touch at 18.5 after the 24 h (assumption until the seal is named, HOLD) | FE-01 to FE-03; D-132 | PLANNED |
| BT-07 | Glide stop and the corner keys' screw heads | A side band's back end with its corner key (111211, 2 × 838010 button heads; D-129) and a glide fully home in its M10 rivnut | Screw the glide fully home; measure the band's bottom face and the screw heads' lowest point above a flat plate | Band bottom 8.5 mm or more above the plate with the glide fully home (its base is the stop); heads 5 mm or more above it (PM ruling on F-018; joints register PR #99) | FB-08, FB-11 | PLANNED / NOT TESTED |
