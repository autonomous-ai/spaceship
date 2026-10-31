
## Edit test record
Run 2026-10-31 on Mac 1, Fusion 2706.1.17, scripts at commit c137378.

Copy: `v2/01-CAD-Native/proof/V2-SWL-00_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_CAD.f3d` opened as a new, unsaved document (closed without saving at the end).

### 1. Reopen check

- Timeline: 31 items, 0 not healthy
- Sketches: 9, fully constrained: 9
- Design type: parametric (history captured)
- User parameters (18):

| Name | Expression | Unit |
|---|---|---|
| frame_width | `1470 mm` | mm |
| frame_height | `1150 mm` | mm |
| tube_size | `20 mm` | mm |
| tube_wall | `1.2 mm` | mm |
| frame_material | `'Steel'` | Text |
| hole_dia | `6.6 mm` | mm |
| hole_edge_dist | `60 mm` | mm |
| rail_hole_pitch_max | `500 mm` | mm |
| rail_hole_count | `ceil(( frame_width - 2 * hole_edge_dist ) / rail_hole_pitch_max) + 1` | (count) |
| rail_hole_pitch | `( frame_width - 2 * hole_edge_dist ) / ( rail_hole_count - 1 )` | mm |
| stile_hole_pitch_max | `400 mm` | mm |
| stile_hole_count | `ceil(( frame_height - 2 * hole_edge_dist ) / stile_hole_pitch_max) + 1` | (count) |
| stile_hole_pitch | `( frame_height - 2 * hole_edge_dist ) / ( stile_hole_count - 1 )` | mm |
| mid_rail_z | `frame_height / 2` | mm |
| skin_thk | `3 mm` | mm |
| skin_overhang_rear | `30 mm` | mm |
| skin_width | `frame_width + skin_overhang_rear` | mm |
| skin_height | `frame_height` | mm |

### 2. Edit

| Parameter | Before | After |
|---|---|---|
| frame_width | 1470 | 1170 |
| rail_hole_pitch_max | 500 | 300 |
| rail_hole_count | 4 | 5 |
| rail_hole_pitch | 450 | 262.5 |
| skin_width | 1500 | 1200 |

Rebuild: 31 timeline items, 0 not healthy; sketches not fully constrained: 0

### 3. Bodies before and after

| Body | Changed | Bounding box before (mm) | Bounding box after (mm) | Volume mm3 before -> after | Holes before -> after |
|---|---|---|---|---|---|
| WALL - FRAME RAIL - BOTTOM - TUBE | yes | X 20..1450, Y -20..0, Z 0..20 | X 20..1150, Y -20..0, Z 0..20 | 128715 -> 101561 | 4 -> 5 |
| WALL - FRAME RAIL - MID - TUBE | yes | X 20..1450, Y -20..0, Z 565..585 | X 20..1150, Y -20..0, Z 565..585 | 129043 -> 101971 | 0 -> 0 |
| WALL - FRAME RAIL - TOP - TUBE | yes | X 20..1450, Y -20..0, Z 1130..1150 | X 20..1150, Y -20..0, Z 1130..1150 | 128715 -> 101561 | 4 -> 5 |
| WALL - FRAME STILE - FRONT - TUBE | no | X 0..20, Y -20..0, Z 0..1150 | X 0..20, Y -20..0, Z 0..1150 | 103776 -> 103776 | 0 -> 0 |
| WALL - FRAME STILE - REAR - TUBE | yes | X 1450..1470, Y -20..0, Z 0..1150 | X 1150..1170, Y -20..0, Z 0..1150 | 103448 -> 103448 | 4 -> 4 |
| WALL - SKIN ACP 3 - SIDE LOWER - LH - SHEET | yes | X 0..1500, Y 0..3, Z 0..1150 | X 0..1200, Y 0..3, Z 0..1150 | 5.175e+06 -> 4.14e+06 | 0 -> 0 |

- WALL - FRAME RAIL - BOTTOM - TUBE hole centres after: [(60.0, -10.0), (322.5, -10.0), (585.0, -10.0), (847.5, -10.0), (1110.0, -10.0)]
- WALL - FRAME RAIL - TOP - TUBE hole centres after: [(60.0, -10.0), (322.5, -10.0), (585.0, -10.0), (847.5, -10.0), (1110.0, -10.0)]

Expected to change: WALL - FRAME RAIL - BOTTOM - TUBE, WALL - FRAME RAIL - MID - TUBE, WALL - FRAME RAIL - TOP - TUBE, WALL - FRAME STILE - REAR - TUBE, WALL - SKIN ACP 3 - SIDE LOWER - LH - SHEET. Expected unchanged: WALL - FRAME STILE - FRONT - TUBE. Result: the right bodies changed.

### 4. Revert

frame_width back to 1470 mm, rail_hole_pitch_max back to 500 mm. Timeline: 0 not healthy; sketches not fully constrained: 0. Every body equal to the before values: yes.

**RESULT: PASS (CAD check on a copy; not a physical test)**
