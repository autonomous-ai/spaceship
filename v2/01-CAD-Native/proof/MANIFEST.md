# Proof part: source manifest

Engineering guideline sections 4.4 and 4.5. Phase 0 proof only: **DRAFT, PROPOSED, not for manufacture.** Part numbers, names and revision P01 are proposals until the v2 control pack sets the numbering.

Last updated 2026-10-31. Built by `wall_panel_frame.py` in Fusion 2706.1.17 on Mac 1.

## Files

| What | File | Status |
|---|---|---|
| Build script (source of truth for the geometry) | `v2/01-CAD-Native/proof/wall_panel_frame.py` | Runs end to end, all checks pass (`build-record.md`) |
| Native CAD, same revision | `v2/01-CAD-Native/proof/V2-SWL-00_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_CAD.f3d` | Exported from Fusion cloud file Default Project / FocusPod v2 / V2-SWL-00_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH, version 1 |
| STEP, same revision | `v2/03-Manufacturing/proof/V2-SWL-00_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_STEP.step` | AP214. STEP length unit: cm, declared in the file. Re-read in Fusion and with `tools/fusion/step_check.py`: box 0..1500 x -20..3 x 0..1150 mm, same as the model |
| Edit test | `v2/01-CAD-Native/proof/edit_test.py`, record in `edit-test-record.md` | PASS on a copy (CAD check, not a physical test) |
| Drawing | `v2/02-Drawings/proof/` | See the drawing record there |

## Coordinate system and datums

Right-handed, mm, drawn for the left-hand (LH) wall. Origin O = front-bottom corner of the frame's outer face. +X along the wall toward the back of the pod, +Y outward (toward the skin), +Z up. Datum A = frame outer face (Y = 0), B = bottom face (Z = 0), C = front face (X = 0); all three meet at O. Fusion's "Front" view looks at the frame from inside the pod. The RH frame is the mirror image (not modelled).

## Part to sketch, feature and parameter map

Every body below is created and driven by the named sketch and features in its own component. All sketches are fully constrained (checked by script). No imported or base-feature bodies.

| Part no. (PROPOSED) | Component name | Vietnamese name | Body | Sketch (plane) | Features | Driving parameters |
|---|---|---|---|---|---|---|
| V2-SWL-00 | WALL - PANEL ASSY - SIDE LOWER - LH (root) | Vách bên dưới - trái (cụm) | none | none | none | all |
| V2-SWL-10 | WALL - PANEL FRAME - SIDE LOWER - LH | Khung vách bên dưới - trái | none (welded frame of the 5 tubes below) | none | none | none |
| V2-SWL-11 | WALL - FRAME STILE - REAR | Thanh đứng sau | WALL - FRAME STILE - REAR - TUBE | SECTION - STILE REAR TUBE (XY) | EXTRUDE - STILE REAR TUBE; PLANE - REAR STILE TO BACK WALL HOLE ENTRY FACE; HOLE POSITION - REAR STILE TO BACK WALL (sketch); HOLE - M6 CLEARANCE - REAR STILE TO BACK WALL; PATTERN - REAR STILE TO BACK WALL HOLES | frame_width, frame_height, tube_size, tube_wall, hole_dia, hole_edge_dist, stile_hole_pitch_max (stile_hole_count, stile_hole_pitch) |
| V2-SWL-12 | WALL - FRAME STILE - FRONT | Thanh đứng trước | WALL - FRAME STILE - FRONT - TUBE | SECTION - STILE FRONT TUBE (XY) | EXTRUDE - STILE FRONT TUBE | frame_height, tube_size, tube_wall |
| V2-SWL-13 | WALL - FRAME RAIL - BOTTOM | Thanh ngang dưới | WALL - FRAME RAIL - BOTTOM - TUBE | SECTION - RAIL BOTTOM TUBE (YZ) | EXTRUDE - RAIL BOTTOM TUBE; PLANE - BOTTOM RAIL TO BASE HOLE ENTRY FACE; HOLE POSITION - BOTTOM RAIL TO BASE (sketch); HOLE - M6 CLEARANCE - BOTTOM RAIL TO BASE; PATTERN - BOTTOM RAIL TO BASE HOLES | frame_width, tube_size, tube_wall, hole_dia, hole_edge_dist, rail_hole_pitch_max (rail_hole_count, rail_hole_pitch) |
| V2-SWL-14 | WALL - FRAME RAIL - TOP | Thanh ngang trên | WALL - FRAME RAIL - TOP - TUBE | SECTION - RAIL TOP TUBE (YZ) | EXTRUDE - RAIL TOP TUBE; PLANE - TOP RAIL TO UPPER FRAME HOLE ENTRY FACE; HOLE POSITION - TOP RAIL TO UPPER FRAME (sketch); HOLE - M6 CLEARANCE - TOP RAIL TO UPPER FRAME; PATTERN - TOP RAIL TO UPPER FRAME HOLES | frame_width, frame_height, tube_size, tube_wall, hole_dia, hole_edge_dist, rail_hole_pitch_max |
| V2-SWL-15 | WALL - FRAME RAIL - MID | Thanh ngang giữa | WALL - FRAME RAIL - MID - TUBE | SECTION - RAIL MID TUBE (YZ) | EXTRUDE - RAIL MID TUBE | frame_width, tube_size, tube_wall, mid_rail_z |
| V2-SWL-20 | WALL - SKIN ACP 3 - SIDE LOWER - LH | Tấm ốp ACP 3 mm (VT01) | WALL - SKIN ACP 3 - SIDE LOWER - LH - SHEET | OUTLINE - ACP SKIN (XZ) | EXTRUDE - ACP SKIN | skin_width (= frame_width + skin_overhang_rear), skin_height, skin_thk |

Top and bottom rails are the same geometry today (same length, same hole pattern). They are kept as two parts until the base joint is designed; if it stays the same they can share one part number (COMMON).

## Parameters and status

| Parameter | Value | Status and source |
|---|---|---|
| frame_width | 1470 mm | CALCULATION: side wall depth 1500 (SOURCE: build plan II) minus rear skin overhang 30 |
| frame_height | 1150 mm | CALCULATION: wall height 2300 (SOURCE: v1 BOM) / 2 frames (SOURCE: build plan II). HOLD: a thin floor makes walls about 80 mm taller |
| tube_size | 20 mm | SOURCE: build plan VT10, box section 20x20 |
| tube_wall | 1.2 mm | ASSUMPTION: the plan gives none; UNVERIFIED with a supplier |
| frame_material | Steel | SOURCE: build plan VT10. Aluminium is PROPOSED in the v2 plan; switch the text parameter and rebuild |
| hole_dia | 6.6 mm | SOURCE: ISO 273 medium clearance for M6. Bolt M6x60 (SOURCE: build plan VT11) |
| hole_edge_dist | 60 mm | ASSUMPTION: stile 20 + weld 3 + washer radius 6 + wrench swing 25 = 54, rounded up. To check in the joint register |
| rail_hole_pitch_max | 500 mm | ASSUMPTION until the joint and gasket calculation (J-WALL-01) |
| rail_hole_count, rail_hole_pitch | 4, 450 mm | CALCULATION |
| stile_hole_pitch_max | 400 mm | ASSUMPTION until J-WALL-02 |
| stile_hole_count, stile_hole_pitch | 4, 343.33 mm | CALCULATION |
| mid_rail_z | 575 mm | ASSUMPTION: halves the unsupported skin span |
| skin_thk | 3 mm | SOURCE: build plan VT01, ACP 3 mm, Dark Yellow EV3038 |
| skin_overhang_rear | 30 mm | SOURCE: build plan joint detail, ACP 3 + ply 6 + frame 20 + gap 1 |
| skin_width, skin_height | 1500, 1150 mm | CALCULATION / ASSUMPTION (skin flush with the frame top and bottom; seam gap HOLD) |

## Mass (CALCULATION from CAD)

Steel frame 4.66 kg (tubes 20x20x1.2, density 7850, square corners: real tube corner radii make it slightly lighter). ACP skin 6.73 kg at an ASSUMED 3.9 kg/m2 (PE core, 0.3 mm skins; a mineral FR core is about 6 kg/m2). Panel 11.4 kg, under the 20 kg per part limit. With aluminium tubes (1.5 mm wall, ASSUMPTION) the frame would be about 2 kg.

## Open items (HOLD)

1. Joint design: bolt pitch, edge distance, washer and nut or rivnut, tool access and gasket compression for J-WALL-01 (top rail to upper frame), J-WALL-02 (rear stile to back wall) and the base joint. The M6x60 from the build plan is too long for the rear stile joint if the back wall takes a rivnut (it would reach the back wall's skin); the stack has to be drawn.
2. Front stile to decor frame: no holes yet, the decor bracket interface is not designed.
3. ACP bonded straight to the frame with no plywood (PROPOSED in the v2 plan): bond spec, and the sound check, decide it.
4. Skin seam to the upper panel, tube end caps, tube corner radii, weld spec.
5. The horizontal split puts a seam across the side wall at about 1150 mm. v1's side wall has a vertical seam instead. The look rule needs a decision on this.
6. Wall height follows the floor choice (thin floor PROPOSED).
