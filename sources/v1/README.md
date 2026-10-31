# FocusPod v1 sources (Indoor Pod V3)

The v1 design files, exactly as the hardware team sent them on 2026-10-31. They are reference only: don't edit them in place. v2 work lives elsewhere in the repo and links back here.

FocusPod v1 is sold at [autonomous.ai/focus-pod](https://www.autonomous.ai/focus-pod). Inside the team it is called "Indoor Pod V3".

| File | Original name | What it is | Date | Format |
|---|---|---|---|---|
| `indoor-pod-v3-assembly.step` | Indoor Pod V3 (Assembly).step | Full pod assembly: floor frame, walls, ceiling, front decor, glass door and wall, fans, table, electrical fittings | Exported 2026-10-14 | STEP AP214, mm, 224 solid bodies |
| `indoor-pod-v3-bom-v5-2026-10-29.xlsx` | Indoor Pod V3 - BOM vat lieu - 29 OCT v5.xlsx | Materials BOM in Vietnamese. Sheets: pod make-up (19 assemblies), BOM (147 lines), material totals. No prices. | 2026-10-29, v5 | Excel |
| `drawings/wood-parts.pdf` | Indoor Pod - Bản vẽ Gỗ.pdf | Wood part drawings | — | PDF, 34 pages, A3 |
| `drawings/floor-frame-assembly.pdf` | Indoor Pod - Cụm Khung Sàn.pdf | Floor frame assembly drawings | — | PDF, 17 pages, A3 |
| `drawings/decor-frame-assembly.pdf` | Indoor Pod - Cụm Khung Trang Trí.pdf | Front decor frame assembly drawings | — | PDF, 16 pages, A4 (Fusion Drawings) |
The engineering guideline that applies to all versions is in `docs/engineering-guideline.md`. The plan to build v2 is in `v2/00-Control/v2-build-plan.pdf`.

The v1 files don't always agree with each other. For example, the BOM lists 6 leveling feet and the CAD has 8. Those differences go in the v2 issue register, not into edits here.
