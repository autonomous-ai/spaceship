# WALL (210000) and the wall lining cassettes: native Fusion designs

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| WALL CAD, sample set (L1 and its cassette) | P01 | DRAFT | 2026-10-31 | WALL Engineer |

Spaceship is the working name of v2 (FocusPod v2, the team's "Indoor Pod"). This folder holds the WALL assembly's native Fusion designs and the scripts that build them. Sample first, because the factory builds the wall-and-door sample first (`v2/06-Samples/wall-door-sample/`, items S1 and S2). Read `EDIT-TEST-RECORD.md` for the edit test, `../../02-Drawings/wall/FEATURE-RATIONALE-210101.md` for why every hole and gap is where it is, and `../../03-Manufacturing/wall/` for the STEP, the cut files and the parts list.

## What is in it

| Part number | Name · Vietnamese | Kind | Qty per pod |
|---|---|---|---|
| 210101 | WALL - PANEL ASSY - SIDE LOWER - LH (L1) · Vách trái - cụm tấm dưới | bonded and hardware-fitted assembly | 1 |
| 211101 | WALL - PANEL FRAME - SIDE LOWER - LH · Vách trái - khung dưới | made: aluminium tube 20 × 40 × 1.2, back stile 40 × 40 × 1.2; 7 members | 1 |
| 211301 | WALL - SKIN - SIDE LOWER - LH · Vách trái - tấm ốp alu dưới | made: ACP 3 mm EV3038, V-grooved back return | 1 |
| 211501 | WALL - CAVITY FILL - SIDE LOWER - LH · Vách trái - bông PET dưới | made: PET fill 40 mm, 4 pieces | 1 set |
| 510101 | LINING - CASSETTE - SIDE LOWER - LH (L1-CASS) · Cassette lót vách trái dưới | assembly, floating inner leaf | 1 |
| 511101 | LINING - TRAY - SIDE LOWER - LH · Khay thép lót vách trái dưới | made: sheet metal 0.5 mm galvanised, 34 mm returns, 12 mm lips | 1 |
| 511301 | LINING - FELT - SIDE LOWER - LH · Tấm tiêu âm vách trái dưới | made: cut PET felt 9 mm | 1 |

Part numbers follow `conventions.md` section 6, as the PM ruled for this work (WALL 21xxxx, LINING 51xxxx; checked against D-28's reserved list by `test_wall_offline.py`). R1, L2 and R2 take the next numbers (`2101 02` to `2101 04`, and so on); the back wall takes `2102 0n` and `5102 0n`. Bought hardware has no number here: the joints register owns that list (PM ruling, 2026-10-31).

## How it is built

- **Pod coordinates** (conventions section 4), the same as skeleton P04: every part sits where it goes in the pod, so the WALL assembly and the GA insert these designs with no transform.
- **Linked to the skeleton by Fusion's Derive.** The build derives the favorite parameters of the cloud file `100000_P04_POD-SKELETON_CAD`; they arrive as `<name>_Ref`. The wall adds one alias per skeleton name it uses (`side_h = side_h_Ref`) and its own parameters on top, each with its status and source in the parameter comment. A new skeleton version reaches the part with `Document.updateAllReferences()`.
- **Every sketch fully constrained** (the run fails otherwise), every feature, body and sketch named by function, each part its own component with its part number. Joint holes follow the joints register (PR #23) and the PM's rulings: Ø7.0 bolt holes with the M6 × 16 ISO 4762 captive bolts, Sherex CAH3-610-4.2 rivnuts with 1.5 mm stop washers, the 2.26 mm seam gap, the 40 × 40 back stile, J-BASE-01 at the base band's rivnuts.
- **Checks in every build:** timeline health, sketch constraint state, a clash check over all bodies (any overlap over 1 mm³ fails the run), masses per component.

## Files

| File | What it does |
|---|---|
| `wall_side_panel.py` | Builds one side panel (`part=panel`: frame, skin, fill, joint holes) or its cassette (`part=cassette`: sheet-metal tray, felt, HOLD clip zones) into the active document. `side=L|R`, `row=1|2`. |
| `post_wall_doc.py` | Everything after a build in one Fusion run: `export_wall_doc.py` (.f3d and STEP, STEP re-read), `report_wall_doc.py` (CAD report JSON), `export_flat_dxf.py` (the tray's flat pattern) and `edit_test_wall.py` (guideline §4.4, on a copy). |
| `test_wall_offline.py` | Offline checks: parameter values against the decided sizes, the 400 mm stile rule over other wall depths, part numbers and names, statuses. |
| `*_CAD.f3d` | The native designs, exported from the saved cloud versions. |

```sh
python3 v2/01-CAD-Native/wall/test_wall_offline.py
python3 tools/fusion/run_script.py v2/01-CAD-Native/wall/wall_side_panel.py --label "WALL Engineer" \
    --doc 210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_CAD --doc-new --arg part=panel --arg side=L --arg row=1 --save "build"
python3 tools/fusion/run_script.py v2/01-CAD-Native/wall/post_wall_doc.py --label "WALL Engineer" \
    --doc 210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_CAD --arg pn=210101 --close
python3 v2/03-Manufacturing/wall/make_parts_list.py 210101 510101
python3 v2/03-Manufacturing/wall/make_cut_files.py 210101 510101
python3 v2/02-Drawings/wall/make_feature_rationale.py 210101 510101
```

Add `--arg rebuild=1` to rebuild a design this script made (it refuses any other).

## Open items (HOLD) in these parts

| Item | What waits | Release |
|---|---|---|
| Frame member joints (H11) | butt joints modelled, rails full length; welded, cleated or riveted not decided | the PM's joint decision |
| Cassette clip (H03, HOLD-08) | 4 reserved zones in the 4 mm gap on the first and last intermediate stiles | a clip named with its ratings |
| Captive retainer (HOLD-02) | the 7 bolts this panel drives | a part named, test T-04 |
| ACP V-groove rule (H16) | the skin blank uses outer-face lengths, fold allowance 0 | the maker's rule |
| Tube alloy and finish (H15, ISS-034) | 2700 kg/m³ used for mass | the alloy recorded |

## Fusion 2706.1 traps found here (for the next engineer)

| What | What happens | What the build does |
|---|---|---|
| Rectangular pattern with only direction one | direction two defaults to 3 instances at 0 mm: 3 identical bodies on every instance, found only by a clash check | sets direction two to 1 instance |
| A pattern of a cut over separate bodies | `PATTERN_FEATURES_NO_PASTE_INT_EDGES`: no instance may cut a body other than the seed's | one cut per position, each allowed to cut any fill piece |
| Root part number right after `--doc-new` | set while the first upload is still running, it can be overwritten by that upload | sets it again at the end of the run; the export refuses a wrong one |
| A script that raises | all its changes are rolled back, so the document is as it was | nothing to clean up after a failed run |
| A derived skeleton plane | stretches the root component's box to Z 0 | boxes are taken from the solid bodies only |
| Construction plane offset from the XZ plane | the offset runs along that plane's normal, which needn't point along +Y | the sign follows the normal, and every plane is checked to land on its coordinate |
