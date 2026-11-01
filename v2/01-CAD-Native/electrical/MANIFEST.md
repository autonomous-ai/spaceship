# Manifest: ELECTRICAL P01 native CAD (guideline §4.5)

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-CAD-ELE-00 | P01 | DRAFT | 2026-11-01 | ELECTRICAL Engineer |

Every design ELECTRICAL makes, with the bodies, the sketches and features that make them, the parameters that drive them, the exports from the same saved version, and how editability was checked. Cloud copies sit in Default Project / FocusPod v2.

## 1. Route model: 710000_P01_ELECTRICAL_CAD

| Item | Value |
|---|---|
| Native file | `710000_P01_ELECTRICAL_CAD.f3d`, exported from the saved cloud version with the derive link broken in memory, so it opens on its own. The cloud copy keeps its link to skeleton P04. |
| Built by | `electrical_build.py` from `electrical_model.py` (the same tables the documents use) |
| Linked to | skeleton P04 (`100000_P04_POD-SKELETON_CAD`, v4 of 2026-11-01) by Derive: 16 favourite parameters arrive as `<name>_Ref`. A user parameter of the same plain name equals each one, so every expression follows the skeleton. The air column's top `col_z1` is the skeleton's named value `dt_zb` (the soffit underside, Z 2120), not a number of its own. |
| Components | 710001 power unit, 710011 light feed, 710021 trunk, 710023 air column, 710024 call light, 710031 ceiling draw wire, 710041 hub zone |
| Bodies | 40 reserved spaces, each `<code> <name>`: routes (T1-*, L1-*, C1-*, CALL-R2, CHASE, TO-*, IN-DR), connector pockets (P1 to P7, P3-KIT), bushings and slots (G-*, S-*), felt holes (FX-*, FS-CNR, FA-KIT), the power unit and its front plate (over the felt edge, 2 mm off the felt), the inlet, the LAN feed-through, the sleeve, the hub zone |
| Sketch and feature per body | one sketch `OUTLINE - <code>` on an origin plane, fully constrained by parameter expressions (box: width, height and corner to the origin; cylinder: diameter and centre to the origin); one extrude `EXTRUDE - <code>` from and to parameter expressions along its axis |
| Main parameters | `pu_x0`, `pu_zc` (DECIDED 1000), `pu_w`, `pu_h`, `pu_d`, `trunk_z`, `lt_x`, `shelf_z`, `call_y`, `call_z`, `hub_zc`, `col_*`, `ch_w`, `grm_d`, `pk_l`, `rt_h`, `inlet_x`, `inlet_z`, `lan_z`, each with its status and source in the parameter comment |
| Exports (same saved version) | `../../03-Manufacturing/electrical/710000_P01_ELECTRICAL_STEP.step` (cm, declared in the file, D-13), re-read in Fusion, box compared to 0.05 mm |
| Drawing | sheet 3 of the wiring diagram `710000_P01_ELECTRICAL-WIRING-DIAGRAM_DWG.pdf`: the route and joint views, computed from `electrical_model.py`, the same numbers the build checks every body against (0.01 mm). No separate Fusion drawing of the route model (PM ruling 2026-11-01). |
| Checks in the build | timeline health, loose sketches, every body box against the offline model (0.01 mm), no overlap between its own bodies, no overlap with a skeleton P04 body except the listed intended ones, each with its reason (exact Fusion intersections, 0.1 mm³) |
| Edit test | `edit_test_electrical.py` on a copy of the `.f3d`: four edits (power unit height, trunk height, the skeleton's `pod_d`, pocket and bushing sizes), each checked against the offline model, then reverted. Result in `EDIT-TEST-RECORD.md`. |

## 2. Sheet-metal parts (each in its own design, so its drawing shows only it)

Built by `electrical_parts_cad.py` in one Fusion run (`--arg parts=front,hub,body --arg export=1`, the plates first). Each part opens its design from Default Project / FocusPod v2 or makes it the way the PM set on 2026-11-01 while the runner's `--doc-new` is paused: the script reads every entry of the folder first and makes nothing if one can't be read, and a new design gets a name never used before and is saved there at once, empty. A part that fails doesn't stop the others. The plates' DXF is written from their outline sketch by `flat_dxf.py`: plain ASCII DXF in mm (`$INSUNITS` 4), every line and circle on the CUT layer and nothing else (D-89 part 4); the offline test reads it with the mechanical check's own DXF reader.

| Part / Rev | Native file | Body | Sketches and features | Parameters | Exports | Drawing |
|---|---|---|---|---|---|---|
| 711001 P01 ELECTRICAL - POWER UNIT - ENCLOSURE BODY | `711001_P01_ELECTRICAL-POWER-UNIT-ENCLOSURE-BODY_CAD.f3d` | one sheet-metal body, 5052-H32 1.0 mm | `OUTLINE - BACK` → `BASE - BACK` (base flange), `FLANGE - RETURNS`, `FLANGE - FRONT LIPS`; `HOLE - …` sketches → `CUT - LEAD EXIT 1/2 RIGHT SIDE`, `CUT - LIGHT FEED EXIT TOP`, `CUT - SLEEVE ENTRY BOTTOM`, `CUT - CLINCH NUT HOLE 1-4 IN THE LIP` | `t`, `w`, `h`, `d`, `lip`, `hole_b`, `lead_z1`, `lead_z2`, `lead_y`, `top_x`, `sleeve_*`, `clinch_*` | STEP; DXF flat pattern | `711001_P01_ELECTRICAL-POWER-UNIT-ENCLOSURE-BODY_DWG.pdf`: Fusion drawing, A2, first-angle views from the room-side Front (set by the build), overall dimensions, datums A-B-C; text block and hole list H01-H08 written into the PDF (`../../02-Drawings/electrical/make_body_drawing.py`, `body_drawing_text.py`, offline test `test_body_drawing_offline.py`) |
| 711002 P01 ELECTRICAL - POWER UNIT - FRONT PLATE | `711002_P01_ELECTRICAL-POWER-UNIT-FRONT-PLATE_CAD.f3d` | flat plate 320 x 284, 5052-H32 1.5 mm, covering B2-CASS's cut felt edge 8 mm all round | `OUTLINE AND CUT-OUTS - FRONT` → `EXTRUDE - PLATE FRONT` | `t`, `w`, `h`, `edge_off`, `box_*` (HOLD), `din_*`, `vent_*`, `screw_*` (every opening placed from the unit's edge) | STEP; DXF of the outline sketch, CUT layer only | none: flat laser-cut part, the DXF and its parts-list row define it (D-89 part 4) |
| 711005 P01 ELECTRICAL - HUB ZONE COVER PLATE | `711005_P01_ELECTRICAL-HUB-ZONE-COVER-PLATE_CAD.f3d` | flat plate, 5052-H32 1.5 mm | `OUTLINE AND CUT-OUTS - HUB` → `EXTRUDE - PLATE HUB` | `t`, `w`, `h`, `win_*`, `btn_*`, `knob_*` (HOLD), `screw_*` | STEP; DXF of the outline sketch, CUT layer only | none: flat laser-cut part, the DXF and its parts-list row define it (D-89 part 4) |

**HOLD features** (PM ruling 2026-11-01: model and draw now, mark what waits on module data):
- 711001: the fixing to B2's frame (WALL, IF-12) and the earth stud hole (PEM data) aren't cut yet.
- 711002: the GFCI receptacle's decorator opening and the two keystone openings (D-133: the picked parts' drawings set them, H-ELE-04).
- 711005: the hub window, the button and knob holes (ISS-060) and the fixing holes (CEILING's column).

**Bought items** (supplies, breaker, inlet, GFCI receptacle, plugs and so on) aren't modelled, by guideline §4.4's rule for bought parts. They are in the parts list with maker and SKU, or HOLD.
