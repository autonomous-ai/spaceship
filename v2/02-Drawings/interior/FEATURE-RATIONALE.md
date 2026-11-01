# Feature rationale: INTERIOR, light shelf, work wall ledge, screen rail (INTERIOR P01)

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| 810000-FR | P01 | DRAFT | 2026-11-01 | CEILING Engineer (INTERIOR) |

Why every feature is where it is (guideline §7). Decisions: D-70 (interior principles, light shelf, work wall ledge and screen), D-85 (budgets: the light shelf 0.4 kg/m with its strip, the 1000 mm ledge in 1.5 mm folded aluminium) and ELECTRICAL's input through the PM (2026-11-01). Every value is a named parameter in `v2/01-CAD-Native/interior/interior_model.py`. Coordinates: the pod system (conventions §4), mm.

INTERIOR parts sit on the floating linings or stand off them (D-17): the light shelf is light and screws to the wall cassettes; the ledge and the screen rail take people's weight, so they stand on stand-offs through clearance holes in the lining, fixed to the wall frame's stiles, 2 mm off the felt so nothing touches the floating leaf.

## Light shelf 810201 (1.0 mm folded aluminium U along the side and back wall tops)

| Feature ID | Feature | Size, offset | Function | Constraint source or calculation | Status |
|---|---|---|---|---|---|
| F-8102-01 | Section | U: back flange 40, bottom 60, front lip 20, 1.0 thick; 118 mm² (0.32 kg/m) | Holds one 8 mm up-light strip on its bottom, aimed at the felt ceiling; the lip hides the strip from a seated eye; the U is the wiring channel | D-70; D-85 budget 0.4 kg/m with the strips (0.39 averaged, offline test) | assumption (sizes) |
| F-8102-02 | Height | underside Z 2230, back flange top Z 2270 | Lights the felt ceiling (Z 2316) from 46 below; the cable points sit in the back flange | ELECTRICAL's feed and drop at Z 2250 | assumption |
| F-8102-03 | Back run 811201 | X −1166…1166 on the back lining (Y 766) | Full width | D-70 | calculation |
| F-8102-04 | Side runs 811202 LH, 811203 RH | Y −285…706, butting the back run | From the soffit's back face to the back run | D-70 (side walls back of the soffit) | calculation |
| F-8102-05 | Down-light LED profile 718101 with its clip-on opal cover 718102, end caps 718103 and clips 718104 (right wall only) | 23 x 12.5 outside, 20 inside, 991 long: the right run's own length, from the soffit's face (Y -285) to the corner joint with the back run (Y 706), 15 off the lining | ELECTRICAL's two 8 mm down-light strips over the ledge (its last 34.5 lit from beside it); every clip fixes to the right run and no end shows past it (Reviewer 6: a 1036 version ran 45 under the back run's corner, open to view from below); the cover is held its whole length and unclips to change a strip; the profile is made for the strips' heat | D-126 (replaces the folded channel 811204 and the cut diffuser 811205, both cancelled); a Tech-Light P13-2 type from public catalogues, cover 70 % light (brochure) | source (type); product HOLD |
| F-8102-06 | Cable holes Ø10 | back run's flange at X 355; right run's flange at Y −209.5; both Z 2250 | The feed and the call-light drop | ELECTRICAL via the PM (2026-11-01) | confirmed (points) |
| F-8102-07 | Fixing | back flange screwed to the wall cassettes | Light: no need to reach the outer frame, so the lining stays floating | Fixing type HOLD (WALL's cassette tray, 0.5 steel) | HOLD |

## Work wall ledge 810101 (right wall beside the air column)

| Feature ID | Feature | Size, offset | Function | Constraint source or calculation | Status |
|---|---|---|---|---|---|
| F-8101-01 | Ledge top 811101 | 1000 long, 250 deep, top Z 1067; 1.5 folded: front lip 25 down, back flange 25 down | Lean on it standing, a keyboard on it | D-70 (1000), D-85 (1.5 folded aluminium); depth and height assumption | confirmed; assumption |
| F-8101-02 | Place | Y −259.5…740.5, centred in the 1051 of right wall beside the column; 2 mm off the felt | Fits the free wall; never touches the floating lining | D-70; D-17 | calculation |
| F-8101-03 | Brackets 818101 (2) | under the ledge at Y 98.63 and 464.32 | Carry the ledge into R1's two middle stiles through stand-offs | WALL's R1 stile pitch 365.69 (mirror of L1); rating HOLD: a 225 N lean at the front edge × 3 | HOLD |
| F-8101-04 | Mass | 1.20 kg top + 2 × 0.1 brackets = 1.40 kg | Within D-85's 1.4 kg | calculation | calculation |

## Screen rail 818102

| Feature ID | Feature | Size, offset | Function | Constraint source or calculation | Status |
|---|---|---|---|---|---|
| F-8103-01 | Rail | 900 long at Y −209.5…690.5, centre Z 1300, 2 mm off the felt | Carries a screen up to about 900 wide over the ledge; its left end meets ELECTRICAL's call-light drop at Y −209.5 | D-70; height assumption | HOLD (bought rail) |
| F-8103-02 | Fixing | stand-offs to R2's stiles (same Y as R1's) | The screen's weight goes to the frame, not the lining | WALL interface | HOLD |

## Interfaces to settle (PROPOSED)

- WALL: rivnuts in R1's stiles at Y 98.63 and 464.32 (ledge brackets, about Z 930 to 1040) and in R2's stiles (screen rail, about Z 1300); clearance holes in R1-CASS and R2-CASS at those points; a fixing for the light shelf's flange in the upper wall cassettes.
- ELECTRICAL: the strips (up-light all round, two down-light strips on the right) and their wiring are ELECTRICAL's parts; the shelf's channels and the two cable holes are INTERIOR's.
