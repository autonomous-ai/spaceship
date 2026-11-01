# 07-Packaging: how Spaceship ships (910000 PACKAGING)

Read first: **[910000_P01_PACKAGING-PLAN_PKG.md](910000_P01_PACKAGING-PLAN_PKG.md)**, the packing plan: two pallets, every piece with its place, mass and label, protection, checks and open items. The assembly guide that uses the same labels is [../02-Drawings/30-Assembly-Instructions/100000_P04_POD-ASSEMBLY-GUIDE_INS.md](../02-Drawings/30-Assembly-Instructions/100000_P04_POD-ASSEMBLY-GUIDE_INS.md).

| File | What it is | Status |
|---|---|---|
| `910000_P01_PACKAGING-PLAN_PKG.md` | Packing plan (generated) | DRAFT |
| `910000_P01_PACKING-LIST_BOM.csv` | Packing list: one row per labelled piece, with pallet, place, step, mass and both sources (generated) | DRAFT |
| `910001_P01_PALLET-1-48X40_PKG.svg` | Pallet 1 diagram (generated) | DRAFT |
| `910002_P01_PALLET-2-96X48_PKG.svg` | Pallet 2 diagram (generated) | DRAFT |
| `pack.py` | The one script: pieces, pallets, crate, assembly steps, time model and checks; writes everything above and the assembly guide | - |
| `templates/` | The plan's and the guide's text; `pack.py` fills in the tables and numbers | - |
| `test_pack.py` | Regression tests | - |

Masses come from the layout study's P04 roll-up (`../05-Engineering/layout-study/out/parts-decided-P04.csv`), which the PM made the mass source for every part; pallet tares, pack allowances and unit times come from the layout study's `scripts/inputs.py`. `pack.py` reads both at run time and copies no number from them.

```sh
python3 v2/07-Packaging/pack.py            # write every output
python3 v2/07-Packaging/pack.py --check    # fail if an output is stale or a check fails
python3 v2/07-Packaging/test_pack.py       # regression tests
```

Part numbers come from the master BOM (`../04-BOM/100000_P01_POD-MASTER_BOM.csv`): a piece marked "TBD (owner)" takes its number as soon as the owner's parts list carries its exact name, and check K13 holds every number on a label to the BOM's name.

Sizes come from each part's own CAD as it ships (`v2/03-Manufacturing/*/*_STEP.step`, read with the mechanical checks' STEP reader in `tools/checks/stepfile.py`): check K14 fails when a merged CAD outgrows its planned size, and pallet 2's lanes and tiers follow from the sizes with the wrap a side, so the pallets are checked on the real parts.

Edit `templates/` or `pack.py`, never the generated files. When a team's CAD replaces a roll-up line, regenerate the roll-up, then run `pack.py`; run it again after the master BOM changes.
