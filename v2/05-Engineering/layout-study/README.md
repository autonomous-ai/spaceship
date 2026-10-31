# Layout study (Milestone 1)

Weight, panel split, pallets and 2-person assembly for Spaceship (v2). Read [report.md](report.md) first.

- `report.md` is generated: edit `report_template.md` or `scripts/`, then run `python3 scripts/run_all.py`.
- `python3 scripts/run_all.py --check` fails if the report or any file in `out/` no longer matches the scripts.
- `python3 scripts/test_layout.py` runs the regression tests (nested overrides; decided-build counts, limits and open weight; skeleton sizes; air parts; status words).
- `out/` holds the part lists (CSV) and one pallet diagram (SVG) per pallet and option.
- `data/v1_step_solids.csv` comes from `scripts/step_crosscheck.py` (needs cadquery-ocp; see its header).
