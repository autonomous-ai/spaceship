# Mechanical checks

Checks that catch mechanical issues in the v2 design before manufacturing. They run on main after every merge; each finding goes into the register (`v2/04-Checks/findings.md`) with an owner group and a status, and is posted to that group with the file and the fix. **Severe findings block the owner's merge until they're fixed** (PM rule).

```sh
python3 tools/checks/run_checks.py                         # check this checkout, print findings
python3 tools/checks/run_checks.py --root <tree> --rev <sha> --update   # check a tree, update the register
python3 -m pytest tools/checks/tests -q                    # offline tests
python3 tools/checks/register.py set F-004 ACCEPTED --note "D-60: ..."  # change a status by hand
```

Standard library only, plus PyMuPDF (or `pdftotext`) to read drawing PDFs. Nothing here edits another group's files. Exit code 1 when a severe finding is open in the run.

## After every merge to main

```sh
python3 tools/checks/run_checks.py --ref origin/main --update                        # offline checks, register
python3 tools/checks/run_fusion_checks.py --ref origin/main --model skeleton --update  # exact, through the lock
python3 tools/checks/run_fusion_checks.py --ref origin/main --update                   # the assembled design, once it exists
```

Each run checks exactly that revision in a clean export (deleted afterwards), updates `v2/04-Checks/findings.md`, and closes what it no longer finds, with the revision as evidence. New findings go to their owner groups with the file and the fix. Open PRs get the same runs on their head before they merge (`--ref origin/<branch>`, without `--update`).

## The checks

| Code | Check | How | Runs |
|---|---|---|---|
| C01 | Clash and minimum gaps | Offline: the pod's outer shell must be closed (back, sides and roof sampled every 5 mm, 1 mm inside; open regions of 10 mm or more are findings). Exact interference with an allow-list of intended contacts goes through Fusion (below). | offline and Fusion |
| C02 | Tolerance stack-ups | Gap rules between named bodies (`v2/04-Checks/config/gap-rules.csv`, the same file the Fusion check reads), and worst-case stacks per joint (`v2/04-Checks/stacks/`). RSS is shown for information only (guideline §6.3). A stack with a missing tolerance stays OPEN and is listed, not failed. | offline |
| C03 | Fastener and tool access | Every bolt reachable with the one hand tool from the side the assembly order uses: a tool envelope along each bolt axis must miss every part already in place at that step. | Fusion |
| C04 | Weight, doorway, pallet | Every shipping piece 20 kg or less except glass (D-03); passes a 914 × 2032 doorway (PLAN Target 2; the 810 mm door of REQ-ASM-06, PROPOSED, is a note); fits its pallet, 48 × 40 in or the standard long 48 × 96 in, at most 1679 mm tall above a 150 mm deck (REQ-SHP-01, REQ-SHP-03). Today from the layout study's decided list; from the CAD and parts lists as they merge. | offline |
| C05 | Drawing completeness | Every part we make has a drawing, every assembly an assembly drawing, same revision as its CAD and STEP; units, material, finish and tolerances stated; holes tagged, in a hole table or called out, counted against the STEP's hole axes. | offline |
| C06 | BOM completeness | Every parts-list row complete (number, English and Vietnamese name, material, quantity, mass, status, source); numbers valid, unique and not reserved (D-28); bought items with maker and SKU or HOLD; every CAD product in a parts list and every made part in the CAD. | offline |
| C07 | Fastener schedule | Every screw, bolt, nut, washer and rivnut with size, length, grade, finish, torque, quantity, maker, SKU and CAD locations, written to `v2/04-Checks/fastener-schedule.csv`. Thread engagement and bottoming are measured along each bolt in Fusion. | offline + Fusion |
| C08 | Hole-to-hole alignment | Coaxial holes in different parts must share one nominal axis; the clearance budget for bolt plus tolerances is stack ST-03. | offline |
| C09 | Edge distance and sheet metal | Hole centre to free edge at least 2 hole diameters (under 1.5 is severe); hole spacing at least 2 diameters; bend inner radius and hole-to-bend distance from `v2/04-Checks/config/sheet-rules.csv` (assumptions until the factory's coupons). | offline |
| C10 | Mixed metals | No bare steel against aluminium (contacts from the assembled CAD); fasteners must state a material and finish. | offline + Fusion contacts |
| C11 | Material grade and finish | Every part and bought item states a material grade and a finish. | offline |

## Inputs it looks for

- STEP files under `v2/03-Manufacturing/` (not `proof/`). `skeleton/` is checked as its own model. Other STEP files whose top product is an assembly (xx0000 to xx0999) and whose bodies all sit inside the pod box are combined into the assembled model in pod coordinates; every STEP also gets the per-part checks.
- Parts lists: CSV files under `v2/03-Manufacturing/`, `v2/04-BOM/`, `v2/02-Drawings/` or `v2/01-CAD-Native/` with a part-number column and a quantity column. Recognised headers: `part_number`, `name`, `name_vi`, `material`, `grade`, `finish`, `qty`, `mass_kg`, `status`, `source`, `rev`, `maker`, `sku`, `size`, `length_mm`, `torque_nm` (common variants work too). Fasteners need `size`, `length_mm`, `grade`, `finish`, `torque_nm`, `maker` and `sku`.
- Drawings: `PARTNO_REV_NAME_DWG.pdf` under `v2/02-Drawings/` (conventions §7).
- The shipping list: `v2/05-Engineering/layout-study/out/parts-option-B1-final-stack.csv`.

## The STEP reader

`stepfile.py` reads Fusion's AP214 STEP without a CAD kernel: the declared unit (Fusion writes cm, D-13), products and their use counts, every solid placed in the top assembly's coordinates, and per solid its planes, holes (cylinders with the material outside that add up to a full turn), bends (a concave and a convex coaxial cylinder one thickness apart) and box. Limits: boxes come from vertices; only planes and cylinders are classified; a faceted body's box hides gaps inside it. The Fusion check is exact where these limits matter.

## Fusion part (C01 exact, C02 true distances, C03, C07 engagement, C10 contacts)

```sh
python3 tools/checks/run_fusion_checks.py --model skeleton --rev <sha> --update   # skeleton STEP
python3 tools/checks/run_fusion_checks.py --rev <sha> --update                    # assembly STEPs in pod coordinates
python3 tools/checks/run_fusion_checks.py --from-json result.json --update         # convert a saved run, no Fusion
```

Fusion runs only through `tools/fusion/run_script.py`, which takes the machine-wide lock and waits its turn (PM rule: never call the Fusion MCP tools directly). `fusion/whole_pod_check.py` makes its own new document, imports the STEP files, and:

- intersects every pair of bodies whose boxes overlap; an overlap over 0.1 mm3 that isn't in `v2/04-Checks/config/clash-allow.csv` is a severe clash (guideline §10: a 1 mm3 threshold can hide small clashes, so the gap rules add minimum clearances);
- measures the gap rules as true minimum distances;
- walks each bolt or screw from its head to 30 mm past its tip: what surrounds the shank (clamped parts, the nut, rivnut or insert), what sits on the axis with no hole (a collision; past the tip, the tip clearance), engagement in the thread, at least one thread past a through nut, tip clearance at least 1 mm;
- sweeps the tool envelope (`v2/04-Checks/config/tools.csv`: the decided 5 mm hex key, ruling R-J2, as an 8 mm shaft for 70 mm through the access hole and fill pocket, then a 40 mm hand and handle) out from each bolt head; any body in place when the bolt is tightened (all but the lining cassettes, which go on last) that it hits blocks the tool;
- lists bodies that touch, for the mixed-metal check;

then writes JSON and closes its document without saving. Its findings carry the scope `<model>/fusion`, so an offline run never closes them and the reverse.

Live run, 2026-10-31, skeleton P03 on main c9ae2a4 (Fusion 2706.1.17, through the lock): 32 bodies; one clash, BAND-R x DR 14393.5 mm3, the same as the skeleton's own record (14394); seam and kick-strip gaps 0.0 mm and the linings 4.0 mm off the frames, as the offline check measures. No bolts are modelled yet, so C03 and C07 had nothing to walk.

## Findings

`register.py` keeps `v2/04-Checks/findings.json` and renders `findings.md`. A finding keeps its F-number for life. A run on main adds new findings, reopens ones that come back, and closes an automatic finding when the check that made it ran on that revision (and model) and no longer finds it, with the revision as evidence. Findings written by hand close by hand.
