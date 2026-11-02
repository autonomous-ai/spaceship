# CEILING (410000) and the ceiling cassette (510301): native Fusion design

One native Fusion design, `410000_P01_CEILING_CAD`, built by script from named parameters. Read `BUILD-RECORD.md` for the last build and its checks, `EDIT-TEST-RECORD.md` for the edit test, and `../../02-Drawings/ceiling/FEATURE-RATIONALE.md` for why each feature is where it is.

## What is in it

| Part number | Name · Vietnamese | Kind | Qty per pod |
|---|---|---|---|
| 410000 | CEILING · Trần | assembly | 1 |
| 410101 / 410102 | CEILING - PANEL ASSY - C1 / C2 · Trần - tấm trái / phải (cụm) | assembly | 1 + 1 |
| 411101 / 411102 | CEILING - PANEL FRAME - C1 / C2 · Trần trái / phải - khung thép | made (welded galvanized steel 20 × 40 and 40 × 40, 1.0 and 0.8 walls, 7 members and 4 mitre plates, D-131) | 1 + 1 |
| 411301 | CEILING - SKIN - COMMON · Trần - tấm ốp alu (dùng chung trái/phải) | made (ACP 3 mm) | 2 |
| 510301 | LINING - CASSETTE - CEILING - COMMON · Cassette trần (dùng chung trái/phải) | assembly, one part for both halves | 2 |
| 513101 | LINING - TRAY - CEILING · Khay thép cassette trần | made (sheet metal, 0.5 mm) | 2 |
| 513102 | LINING - RIB - CEILING · Gân đỡ tấm tiêu âm trần | made (0.5 mm hat) | 4 |
| 513201 | LINING - FELT - CEILING · Tấm tiêu âm PET 9 mm - trần | made (cut felt) | 2 |
| 513301 / 513302 / 513303 | LINING - FILL - CEILING - BAY A / B / C · Bông PET 40 mm - trần | made (cut fill; bays 1, 2, 3 behind the D-60 soffit) | 2 / 2 / 2 |
| 518001 | LINING - CASSETTE CLIP - HOLD · Kẹp treo cassette (chờ chọn) | bought, HOLD envelope (H03) | 12 |
| 518002 | LINING - CEILING SAFETY CATCH - HOLD · Dây an toàn cassette trần (chờ chọn) | bought, HOLD envelope (H04) | 4 |

Part numbers follow conventions §6 and the PM's ruling of 2026-10-31 (CEILING 41xxxx; the ceiling cassette 5103xx and 513xxx; LINING bought items 518xxx). None is on the reserved list (checked by the tests).

## Files

| File | What it does |
|---|---|
| `ceiling_model.py` | Parameters and layout, no Fusion: loads the skeleton's own parameter CSV (the highest revision in `../skeleton/`), adds the ceiling's parameters with status and source, and gives every body as six expressions. The build, the tests and the exports all read it. |
| `ceiling_build.py` | The Fusion build. Every part is a component with fully constrained sketches on defined planes and named features; repeated parts are one component with several occurrences, each placed by a rigid joint to a sketch point dimensioned by expressions. Fails the run on an unhealthy feature, a loose sketch, a clash over 1 mm³ or a body away from its layout box. |
| `ceiling_checks.py` | The position check used by the build and the edit test. |
| `edit_test_ceiling.py` | Guideline §4.4 edit test on a copy of the exported `.f3d`. |
| `test_ceiling_offline.py` | Offline checks of the layout: stack, pitch, envelope and gaps, floating, fill clearances, symmetry, part numbers, weights. |
| `ceiling_exports.py`, `dxf_tools.py` | Cut files (DXF), the parts list and the tube cut list, from the parameters and the build log. |

## How to run

```sh
python3 v2/01-CAD-Native/ceiling/test_ceiling_offline.py
# build, save and export (needs the Fusion lock; the runner opens or makes the cloud file)
python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/ceiling_build.py --label "CEILING Engineer" \
    --doc 410000_P01_CEILING_CAD --doc-new --arg into_active=1 --arg save=1 --arg export=1 --close --discard
python3 v2/01-CAD-Native/ceiling/ceiling_exports.py BUILD_LOG
python3 tools/fusion/step_check.py v2/03-Manufacturing/ceiling/410000_P01_CEILING_STEP.step
python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/edit_test_ceiling.py --label "CEILING Engineer"
```

## Limits found in Fusion 2706.1 (for the next engineer)

| What | What happens | What the build does |
|---|---|---|
| Edge flanges | `createEdgeFlangeInput` fails with "Bad index parameter" unless the sheet metal component is the active one | activates the tray's occurrence (through the first cassette occurrence), then goes back to the root |
| Sheet metal rule values | `rule.thickness.expression = "tray_t"` is "Invalid expression": a rule takes values and its own names only | writes tray_t's value into the rule and uses `Thickness` for the bend radius |
| Function arguments | `max(a, b)` is "not a valid expression"; Fusion separates arguments with `;` | the layout writes `max(a; b)`; the offline evaluator reads both |
| Occurrences without a joint | the felt, added with no joint inside the cassette, kept its world position when the cassette occurrence was placed by its joint (the sheet-metal tray, activated during its build, did follow) | every placed part gets a rigid joint, the felt at the cassette origin; the build's position check fails the run on any body off its layout box |
| Root component name | "root component name cannot be changed" | only the part number and description are set |
