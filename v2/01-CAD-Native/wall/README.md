# WALL (210000) and the wall lining cassettes: native Fusion designs

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| WALL CAD: side panels L1, R1, L2, R2 and back panels B1–B4 with their cassettes | P01 | DRAFT | 2026-11-01 | WALL Engineer |

Spaceship is the working name of v2 (FocusPod v2, the team's "Indoor Pod"). This folder holds the WALL assembly's native Fusion designs and the scripts that build them. The sample came first (L1 and its cassette), because the factory builds the wall-and-door sample first (`v2/06-Samples/wall-door-sample/`, items S1 and S2). Read `out/edit-<pn>.md` for each design's edit test, `../../02-Drawings/wall/FEATURE-RATIONALE-<pn>.md` for why every hole and gap is where it is, and `../../03-Manufacturing/wall/` for the STEP, the cut files and the parts lists.

## What is in it

One design per part number that needs one, each built by script into its own cloud document (`<pn>_P01_<NAME>_CAD`), so each drawing shows only its part. Drawings follow D-89 (`../../02-Drawings/wall/DRAWING-INDEX.md`): each position's panel assembly, frame and cassette assembly has its own; the side skins, back skins, side trays, back trays, side fills and back fills each share one tabulated drawing; the felts are defined by their parts-list rows.

| Position | Panel assembly | Frame | Skin | Fill | Cassette | Tray | Felt |
|---|---|---|---|---|---|---|---|
| L1 side lower left | 210101 | 211101 | 211301 | 211501 | 510101 | 511101 | 511301 |
| R1 side lower right | 210102 | 211102 | 211302 | 211502 | 510102 | 511102 | 511302 |
| L2 side upper left | 210103 | 211103 | 211303 | 211503 | 510103 | 511103 | 511303 |
| R2 side upper right | 210104 | 211104 | 211304 | 211504 | 510104 | 511104 | 511304 |
| B1 back lower left | 210201 | 211201 | 211401 | 211601 | 510201 | 511201 | 511401 |
| B2 back lower right | 210202 | 211202 | 211402 | 211602 | 510202 | 511202 | 511402 |
| B3 back upper left | 210203 | 211203 | 211403 | 211603 | 510203 | 511203 | 511403 |
| B4 back upper right | 210204 | 211204 | 211404 | 211604 | 510204 | 511204 | 511404 |

Numbers follow `conventions.md` section 6 (WALL 21xxxx, LINING 51xxxx), as the PM ruled for the side panels; the back numbers follow the same pattern and are PROPOSED until the PM confirms them. `test_wall_offline.py` checks them against D-28's reserved list. The joint hardware the panels carry takes the joints register's numbers (D-63): rivnut 838003, stop washer 831002, spigot 831001, bolts 838001 and 838002, washer 838004, retainer 838005, gaskets 848001, 848004 and 848012, bond set 108002, hook-and-loop 848011, clip 518001.

## How it is built

- **Pod coordinates** (conventions section 4), the same as skeleton P04: every part sits where it goes in the pod, so the WALL assembly and the GA insert these designs with no transform.
- **Linked to the skeleton by Fusion's Derive.** The build derives the favorite parameters of the cloud file `100000_P04_POD-SKELETON_CAD`; they arrive as `<name>_Ref`. The wall adds one alias per skeleton name it uses (`side_h = side_h_Ref`) and its own parameters on top, each with its status and source in the parameter comment. It restates no skeleton number: the skin, bond and frame sizes, the back panels' skin and frame widths (`half_pw`, `half_fw`), the closing gap and the bolt rules (`bolt_edge_inset`, `spigot_inset`, `n_base_bolt`, `ceil_bolt_z`) all come from the skeleton (as updated in place, PR #58). A new skeleton version reaches a part with `Document.updateAllReferences()`.
- **Frames** (D-34, D-54, D-85): aluminium 6063-T6, mill finish (D-79). Perimeter members 20 × 40 × 1.2 (they carry the rivnuts); the side panels' back stile and the upper side panels' top member are 40 × 40 × 1.2 (R-J3); intermediate studs 20 × 40 × 1.0, 3 per side panel at 364.93, 2 per back panel at 393.
- **Joints** follow the joints register and the PM's rulings: every bolted edge at the 220 rule (R-J14), bolt lines on the tube centre (Y 824, Z 2374, R-J15), Ø7.0 clearance and Ø19 access holes, Ø9.53 rivnut holes, spigots 100 from the ends. The upper side panels' ceiling rivnuts follow the ceiling's edge (from Y −645, pitch 351.67), so CEILING drills the same. The back wall's closing seam (B1–B2, B3–B4) is a pin joint: frames 5.5 apart, skins 1.62 past their frames so the skin seam is 2.26 (R-J16), a rivnut and M6 × 25 pin on B2/B4, a plain Ø7.0 on B1/B3, a 1 × 45 lead-in on the top edge (R-J9), and the round spigot hole by the seam (ST-02).
- **Joint hardware as bodies:** at every rivnut hole the panel design holds an H-03 rivnut (its installed envelope), an H-08 stop washer under each stopped-joint rivnut, and an H-05 spigot in each spigot rivnut, patterned like their holes so an edit moves them too.
- **Cassettes** (D-17, D-47, D-81): 0.5 mm galvanised tray (sheet metal, 34 mm returns, 12 mm lips), 9 mm felt behind the lips, 4 reserved clip zones (HOLD H03). The back cassettes stop 1.13 short of X 0, a 2.26 gap with the soft edge seal (PM ruling 2026-10-31 16:58).
- **Checks in every build:** timeline health, sketch constraint state, a clash check over all bodies (any overlap over 1 mm³ fails the run, except a spigot's thread in its rivnut), masses per component; then the export, the report and the edit test on a copy.

## Files

| File | What it does |
|---|---|
| `wall_side_panel.py` | Builds one side panel (`part=panel`: frame, skin, fill, joint holes, joint hardware), one of its parts (`frame`, `skin`, `fill`) or its cassette (`part=cassette`, or `tray`, `felt`) into the active document. `side=L|R`, `row=1|2`. |
| `wall_back_panel.py` | The same for a back panel, `pos=B1..B4`. It runs `wall_side_panel.py` as its library and replaces its tables, geometry and builders. |
| `wall_batch.py` | Several designs in one Fusion run (PM fair-share ruling: at most 3 queued runs per team): `--arg specs="new:side:panel:R1;rebuild:back:frame:B1"`. Checks first that the cloud skeleton's latest version has every linked favorite; makes or opens each document, builds and posts it, closes it unsaved; a failing design is reported and the batch goes on. |
| `wall_assembly.py` | The WALL assembly 210000: the 16 saved panel and cassette designs inserted in pod coordinates, a clash check across them, the STEP. Runs once all 16 exist. |
| `post_wall_doc.py` | Everything after a build in the same Fusion run: `export_wall_doc.py` (.f3d and STEP, STEP re-read and its box compared), `report_wall_doc.py` (CAD report JSON), `export_flat_dxf.py` (the tray's flat pattern) and `edit_test_wall.py` (guideline §4.4, on a copy: side designs edit `wall_depth`, `side_h` and the stud rule; back designs edit `pod_w` with its skin and frame widths, `back_ph` and the stud rule). |
| `test_wall_offline.py` | Offline checks: parameter values against the decided sizes, the stud rule over other wall depths, every bolt 30 from every stile, the corner and ceiling rivnut positions, part numbers and names, statuses, no skeleton number restated. |
| `*_CAD.f3d` | The native designs, exported from the saved cloud versions (derive links broken in memory for the export only, D-13 ruling on linked exports). |

```sh
python3 v2/01-CAD-Native/wall/test_wall_offline.py
python3 tools/fusion/run_script.py v2/01-CAD-Native/wall/wall_side_panel.py --label "WALL Engineer" \
    --doc 210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_CAD --doc-new --arg part=panel --arg side=L --arg row=1 \
    --arg post=1 --close --discard
python3 tools/fusion/run_script.py v2/01-CAD-Native/wall/wall_back_panel.py --label "WALL Engineer" \
    --doc 210201_P01_WALL-PANEL-ASSY-BACK-LOWER-B1_CAD --doc-new --arg pos=B1 --arg part=panel \
    --arg post=1 --close --discard
python3 v2/03-Manufacturing/wall/make_parts_list.py 210101 510101
python3 v2/03-Manufacturing/wall/make_cut_files.py 210101 510101
python3 v2/02-Drawings/wall/make_feature_rationale.py 210101 510101
```

Add `--arg rebuild=1` to rebuild a design this script made (it refuses any other).

## Open items (HOLD) in these parts

| Item | What waits | Release |
|---|---|---|
| Frame member joints (H11) | butt joints modelled, rails full length; welded, cleated or riveted not decided | the PM's joint decision |
| Cassette clip (H03, HOLD-08) | 4 reserved zones in the 4 mm gap on the first and last studs | a clip named with its ratings |
| Captive retainer (HOLD-02) | the bolts each panel drives | a part named, test T-04 |
| Bolt and rivnut torque (HOLD-01, D-48) | the parts lists say HOLD-01 | test T06 |
| Cassette edge seal (HOLD-13), closing-seam bulb seal (HOLD-12) | numbered (848012, 848004), product not named | the Hardware Engineer's pick with force data |
| ACP V-groove rule (H16) | the side skin blanks use outer-face lengths, fold allowance 0 | the maker's rule |

## Fusion 2706.1 traps found here (for the next engineer)

| What | What happens | What the build does |
|---|---|---|
| Rectangular pattern with only direction one | direction two defaults to 3 instances at 0 mm: 3 identical bodies on every instance, found only by a clash check | sets direction two to 1 instance |
| A pattern of a cut over separate bodies | `PATTERN_FEATURES_NO_PASTE_INT_EDGES`: no instance may cut a body other than the seed's | one cut per position, each allowed to cut any fill piece |
| Root part number and description after a save | the first upload can finish after a short build (a 2-feature skin) and overwrite the number with the document's timestamp name; new documents came out of their first save with an empty description | sets both before the save, waits for the upload (the data file's version moves on), checks both, and saves again if the cloud reset them; the export refuses a wrong number |
| A script that raises | all its changes are rolled back, so the document is as it was | nothing to clean up after a failed run |
| A derived skeleton plane | stretches the root component's box to Z 0 | boxes are taken from the solid bodies only |
| Construction plane offset from the XZ plane | the offset runs along that plane's normal, which needn't point along +Y | the sign follows the normal, and every plane is checked to land on its coordinate |
| An open document holding an old skeleton | a GA drawing left open kept an old P04 loaded, and Derive read it (missing favorites) | Derive uses an open skeleton only if it is the latest saved version, unmodified; batches check the favorites first |
| A derived design exported as .f3d | refuses: "cannot be created from a local file containing external references" | breaks the derive links in memory, exports, closes without saving |
| Body names in checks | a hardware body's name holds a member's name ("RIVNUT - TOP RAIL 1") | the edit test matches bodies by name prefix |
| A cut after a body pattern | the cut keeps the bodies it first cut; when an edit changes the pattern's count, a fill pocket can land on a new fill piece and the cut goes unhealthy (found by the L1 edit test) | skeleton edits keep the stud count (checked offline for all 8 positions); a change in the stud count is a rebuild by the script; the edit test changes the stud rule only on designs with no fill |
