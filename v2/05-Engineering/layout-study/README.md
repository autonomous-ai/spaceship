# Layout study (Milestone 1)

Weight, panel split, pallets and 2-person assembly for Spaceship (v2). Read [report.md](report.md) first.

**Current weight: [weight-rollup.md](weight-rollup.md)**, the live count on skeleton P04: tonight's CAD masses, the PM's adopted savings, allowances for parts not designed yet, and what is still open toward the 410 kg target (ISS-081, F-010). Its part list `out/parts-decided-P04.csv` is the pod as shipped: the mechanical check sums it for F-010, so the voice kit's reserve, outside the cap, is on the page only. The report's other sections still describe the P03 build.

- `report.md` is generated: edit `report_template.md` or `scripts/`, then run `python3 scripts/run_all.py`.
- `python3 scripts/run_all.py --check` fails if the report or any file in `out/` no longer matches the scripts.
- `python3 scripts/test_layout.py` runs the regression tests (nested overrides; decided-build counts, limits and open weight; skeleton sizes; air parts; status words; the P04 roll-up's lines and savings).
- `scripts/rollup.py` builds the P04 roll-up. It reads D-60's air parts from `../acoustics-air/calc.py`, so a change there shows up in `--check` until this study is regenerated.
- `out/` holds the part lists (CSV) and one pallet diagram (SVG) per pallet and option.
- `data/v1_step_solids.csv` comes from `scripts/step_crosscheck.py` (needs cadquery-ocp; see its header).
