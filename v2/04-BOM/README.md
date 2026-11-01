# v2/04-BOM: the master BOM

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-BOM-000 | P01 | DRAFT | 2026-10-31 | Control pack |

One master BOM for the whole pod, built by a script from every team's parts lists and the joints register's hardware, and checked. The control pack owns this folder (D-78, D-80). Nothing here is released for production, and there are no prices.

## Files

| File | Doc code | What it is |
|---|---|---|
| `build_master_bom.py` | V2-BOM-001 | Reads the parts lists and the joints register, writes the four outputs below, and checks them. Standard library only. |
| `test_build_master_bom.py` | V2-BOM-003 | One planted fault per check rule, plus the readers and the register match. |
| `100000_P01_POD-MASTER_BOM.csv` | generated | POD, then each assembly with its parts, then the joints register's hardware that has no number yet. |
| `100000_P01_POD-MADE-PARTS-BY-PROCESS_BOM.csv` | generated | Made parts, sorted by process. |
| `100000_P01_POD-BOUGHT-PARTS_BOM.csv` | generated | Bought parts, one row per part number, with their HOLD status and register row. |
| `BOM-CHECK.md` | V2-BOM-002, generated | The check result and what is missing or on HOLD, per team. |
| `number-allocation.csv` | kept by hand (the control pack) | The numbers this master BOM gives out before a team's list uses them (D-120): frame members and fill pieces. Append-only; see below. |

The generated files show main as it stands. Re-run the script after every merge that adds or changes a parts list.

## How to run

```
python3 v2/04-BOM/build_master_bom.py                      # main: the files in this working tree
python3 v2/04-BOM/build_master_bom.py --no-write --ref origin/main --ref origin/BRANCH ...
python3 v2/04-BOM/test_build_master_bom.py
```

With `--ref`, the script reads the files straight from those git refs, so open branches can be checked without merging them. The first ref (main) gives every file; each later ref adds only the files its own branch changed since it left the first, and those win. So an old, untouched copy of the joints register on a team branch never hides main's newer one. Exit code 1 means the check failed.

## What each team's parts list needs

A parts list is any `*_BOM.csv` under `v2/03-Manufacturing/<team>/` with a `part_number` column. A cut list is skipped and named in the report: one without that column, and any file with `CUT-LIST` in its name, whose rows are cut pieces of the parts the parts lists carry. A row typed `reserved air space` is not counted either: it marks where one of AIR's parts sits in another team's block, and the part is counted once, in AIR's list (D-105). Under `v2/07-Packaging/` only the packaging items (family 91: pallets, crates, protection, labels) are read: a packing list names other teams' parts, which their own lists already carry. The script reads these columns, by name, in any order:

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
2. one number for two different items: the same item in two lists is fine, and its quantities add up; a line that uses a joints-register number must describe the register's item (its sizes must agree, M6 × 16 is not M6 × 25, and most of its numbered tokens and at least one word must match);
3. a part with no mass;
4. a hardware item with no joints-register row: hardware is every bought item except AIR (61), ELECTRICAL (71) and PACKAGING (91) items, which their own teams number (PM, 2026-10-31);
5. a reserved old number (D-28);
6. a given-out number (below) that is badly formed, outside its band, allocated twice, used after it was cancelled, or used for a different item: the team's name must have every word of the allocated name, in any order.

It lists, per team, without failing: no parts list yet, no quantity, make or buy not stated, a metal part with no finish, a made part with no process, every HOLD item, and register items with no number.

## Statuses

Every number in the outputs carries the status its parts list gives it. Quantities are `source (parts list)`, or `calculation` when a unit's quantity multiplies them. Group and pod masses are calculations: the sum of the listed parts, quantity times mass each, so an assembly with no list counts 0 and the pod total is not the pod's weight until every team has a list. The pod's weight estimate stays in `v2/00-Control/requirements.md` REQ-LGT-01 (D-81).

## Numbers the master BOM gives out (D-120)

Under D-120 every part is its own component with its own number: a frame becomes an assembly of member components and a panel's fill becomes separate pieces. `number-allocation.csv` gives those numbers out now, so each team uses them when it splits its parts (WALL and CEILING do it with D-117; the owner's materials answer is in, D-122).

- **What each row says.** The number, its name and Vietnamese name, kind (MP made part), team, the part it belongs to, quantities, and its basis: section, length and holes, or the fill piece's size, from the team's own list with its revision. Status ALLOCATED or CANCELLED.
- **The bands** (conventions section 6, parts we make 1000 to 7999). Frame members take the unused 2xxx block. WALL: `212FMM`, where F is the frame (1 to 4 the side frames 211101 to 211104, 5 and 6 the back frames 211201 and 211202) and MM the member. CEILING: `412FMM`, with F 1 for C1 (411101), 2 for C2 (411102) and 0 for a member common to both. FRONT: `352FMM`, with F 1 for DL's frame (351104), 2 for DT's (351204) and 3 for DR's (351306), MM in the order of FRONT's member list; DL's hinge-side stop pieces take DL's own part numbers 351105 to 351107. Fill pieces stay in the fill blocks after the panel numbers: `2115PJ` for side panel P, `2116PJ` for back panel P, J the piece. They follow WALL's fill-piece list (`v2/03-Manufacturing/wall/FILL-PIECES.md`): one number per form, by size and pocket layout, and a form two panels share takes the first panel's block (L1 for L1 and R1, L2 for L2 and R2, B1 for B1 and B2, B3 for B3 and B4). R1's and R2's own fill numbers are cancelled.
- **Bought parts** take their family's 8000 to 8999 block. D-126's LED profile parts for the light shelf are ELECTRICAL's, 718101 to 718104 (the 23 x 12.5 profile, opal cover, end caps, mounting clips), a block clear of ELECTRICAL's own 718001 to 718068: ELECTRICAL lists them and CEILING places them in the interior model (the PM, 2026-11-01).
- **One number per part.** A member gets its own number in each frame, because the lists don't give its holes and LH and RH holes mirror (conventions section 5). Members that the cut list shows identical, with no holes, share one COMMON number (CEILING's plain cross members X2 and X3). FRONT's repeats share one number only when the block STEP maps one tube onto the other corner for corner and hole for hole by a turn, never a mirror (the PM, 2026-11-01): DR's three facet and two chamfer tubes, DT's three chamfer cross tubes and DL's ring tubes (4 + 4 + 3 + 3), 48 numbers for FRONT's 63 tubes. CEILING then confirmed that C2's SIDE member and X1 are C1's turned over, with the holes, slots and mitres matching, so they share 412101 and 412105, and 412201 and 412205 are cancelled. A team that finds two allocated parts identical in form, fit and function uses the lower number for both and asks for the other to be CANCELLED; one that finds a part the list doesn't show (a fill piece with its own bolt pockets) asks for a new number.
- **Never reused.** A row is never deleted or renumbered. A CANCELLED number stays in the list and fails the check if a team uses it.
- **Re-pointing.** An allocated number may be re-pointed to another part only while no parts list, drawing or model uses it; once one does, cancel it and allocate a new number instead (the PM, 2026-11-01).
- **In the outputs.** A number no team list uses yet is a master BOM row typed `allocated number`, with no mass, under its family: the frame or the fill it splits still carries the mass. The note says it isn't in any parts list yet, so the mechanical check treats it as a placeholder. Once a team's list uses the number for its item, that row replaces the allocation, and BOM-CHECK.md shows it as in use.
