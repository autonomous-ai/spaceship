# v2/04-BOM: the master BOM

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-BOM-000 | P01 | DRAFT | 2026-10-31 | Control pack |

One master BOM for the whole pod, built by a script from every team's parts lists and the joints register's hardware, and checked. The control pack owns this folder (D-78, D-80). Nothing here is released for production, and there are no prices.

## Files

| File | Doc code | What it is |
|---|---|---|
| `build_master_bom.py` | V2-BOM-001 | Reads the parts lists and the joints register, writes the four outputs below, and checks them. Standard library only. |
| `test_build_master_bom.py` | V2-BOM-003 | One planted fault per check rule, plus the readers (15 tests). |
| `100000_P01_POD-MASTER_BOM.csv` | generated | POD, then each assembly with its parts, then the joints register's hardware that has no number yet. |
| `100000_P01_POD-MADE-PARTS-BY-PROCESS_BOM.csv` | generated | Made parts, sorted by process. |
| `100000_P01_POD-BOUGHT-PARTS_BOM.csv` | generated | Bought parts, one row per part number, with their HOLD status and register row. |
| `BOM-CHECK.md` | V2-BOM-002, generated | The check result and what is missing or on HOLD, per team. |

The generated files show main as it stands. Re-run the script after every merge that adds or changes a parts list.

## How to run

```
python3 v2/04-BOM/build_master_bom.py                      # main: the files in this working tree
python3 v2/04-BOM/build_master_bom.py --no-write --ref origin/main --ref origin/BRANCH ...
python3 v2/04-BOM/test_build_master_bom.py
```

With `--ref`, the script reads the files straight from those git refs, so open branches can be checked without merging them; for the same path, a later ref wins. Exit code 1 means the check failed.

## What each team's parts list needs

A parts list is any `*_BOM.csv` under `v2/03-Manufacturing/<team>/` or `v2/07-Packaging/` with a `part_number` column (cut lists without one are skipped and named in the report). The script reads these columns, by name, in any order:

| Column | Meaning |
|---|---|
| `part_number` | 6 digits, in the family band of `conventions.md` section 6. Fastener and hardware numbers come from the joints register (D-63). |
| `name`, `name_vi` | English name in capitals; Vietnamese name. |
| `type` or `kind`, or `make_buy` | Make or buy: `made ...`, `bought ...` or `assembly ...` in words, or the codes MP (made), HS (sub-assembly), BS or PI (bought), HOLD. |
| `qty_per_pod`, or `qty` | Quantity per pod. With `qty` only, the file's first row is its unit, and the other rows' `qty` is per unit. |
| `material` | Material and grade. A finish may follow as `, finish ...`. |
| `finish` | Optional; otherwise read from `material`. Hidden tubes: 6063-T6 mill finish with the bond prep (D-79); visible aluminium: black anodised AA20 (D-67). |
| `unit_mass_kg` or `mass_each_kg` | Mass of one, in kg. |
| `mass_status` | confirmed, source, calculation or assumption (`conventions.md` section 9). |
| `status` | DRAFT, HOLD and so on; HOLD anywhere in the row marks the item as on HOLD. |
| `process` | Optional, for made parts; otherwise taken from `made (...)` or, as an assumption, from the material. |
| `source`, `note` | Where the numbers come from. |

The joints register (`v2/05-Engineering/joints/joints-register.md`) gives the hardware: its hardware set table (`ID | Item | ...`, IDs H-nn) and any table with a part-number column, merged by ID. Give each item a part number there (and, if you can, its quantity per pod and mass); the BOM matches every bought item to it by number.

## The check

It fails on:
1. a part with no number;
2. one number for two different items (the same item in two lists is fine, and its quantities add up);
3. a part with no mass;
4. a hardware item with no joints-register row: hardware is every bought item except AIR (61), ELECTRICAL (71) and PACKAGING (91) items, which their own teams number (PM, 2026-10-31);
5. a reserved old number (D-28).

It lists, per team, without failing: no parts list yet, no quantity, make or buy not stated, a metal part with no finish, a made part with no process, every HOLD item, and register items with no number.

## Statuses

Every number in the outputs carries the status its parts list gives it. Quantities are `source (parts list)`, or `calculation` when a unit's quantity multiplies them. Group and pod masses are calculations: the sum of the listed parts, quantity times mass each, so an assembly with no list counts 0 and the pod total is not the pod's weight until every team has a list. The pod's weight estimate stays in `v2/00-Control/requirements.md` REQ-LGT-01 (D-81).
