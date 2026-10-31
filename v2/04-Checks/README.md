# 04-Checks: mechanical check results

| Doc code | Revision | Status | Owner |
|---|---|---|---|
| V2-CHK-000 | P01 | Live | Mechanical Checker |

What's here and what to read first:

1. `findings.md`: the findings register. Every finding has an owner group, a severity and a status. Severe findings block the owner's merge until they're fixed. Rendered from `findings.json`; don't edit the markdown by hand.
2. `results/latest.md`: the last run of the checks on main, with what ran, the stacks and the shipping table.
3. `fastener-schedule.csv`: every fastener from the parts lists, with its CAD locations and the engagement result once the Fusion check measures it.
4. `config/gap-rules.csv`: minimum and maximum gaps between named parts (seams, running gaps, floating linings), each with its status and source.
5. `config/sheet-rules.csv`: bend radius and hole-to-bend rules per material (assumptions until the factory's coupons).
6. `stacks/`: the tolerance stacks per joint (`stacks.csv`) and their contributors (`contributors.csv`), each number with its status and source.

The checks are in `tools/checks/` (see its README). Folder note: the guideline's §12 layout uses `04-BOM` and `06-Verification`; the PM's brief put the check results here.
