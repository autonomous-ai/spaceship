# Build record: wall_panel_frame.py

Run 2026-10-31 on Mac 1, Fusion 2706.1.17, scripts at commit c137378, with `--arg export=1 --arg save=1`. Output as printed by `tools/fusion/run_script.py`. Masses are CALCULATION from CAD with the material status given in the script.

```text
step 1: document 'Untitled', 18 user parameters
  frame_width            = 1470.000 mm    [1470 mm]
  frame_height           = 1150.000 mm    [1150 mm]
  tube_size              = 20.000 mm      [20 mm]
  tube_wall              = 1.200 mm       [1.2 mm]
  frame_material         = Steel          ['Steel']
  hole_dia               = 6.600 mm       [6.6 mm]
  hole_edge_dist         = 60.000 mm      [60 mm]
  rail_hole_pitch_max    = 500.000 mm     [500 mm]
  rail_hole_count        = 4.000          [ceil(( frame_width - 2 * hole_edge_dist ) / rail_hole_pitch_max) + 1]
  rail_hole_pitch        = 450.000 mm     [( frame_width - 2 * hole_edge_dist ) / ( rail_hole_count - 1 )]
  stile_hole_pitch_max   = 400.000 mm     [400 mm]
  stile_hole_count       = 4.000          [ceil(( frame_height - 2 * hole_edge_dist ) / stile_hole_pitch_max) + 1]
  stile_hole_pitch       = 343.333 mm     [( frame_height - 2 * hole_edge_dist ) / ( stile_hole_count - 1 )]
  mid_rail_z             = 575.000 mm     [frame_height / 2]
  skin_thk               = 3.000 mm       [3 mm]
  skin_overhang_rear     = 30.000 mm      [30 mm]
  skin_width             = 1500.000 mm    [frame_width + skin_overhang_rear]
  skin_height            = 1150.000 mm    [frame_height]
  components: V2-SWL-10 WALL - PANEL FRAME - SIDE LOWER - LH, V2-SWL-11 WALL - FRAME STILE - REAR, V2-SWL-13 WALL - FRAME RAIL - BOTTOM, V2-SWL-12 WALL - FRAME STILE - FRONT, V2-SWL-14 WALL - FRAME RAIL - TOP, V2-SWL-20 WALL - SKIN ACP 3 - SIDE LOWER - LH, V2-SWL-15 WALL - FRAME RAIL - MID, (Unsaved)
step 2: front stile (on datums A, B, C). SECTION - STILE FRONT TUBE: fully constrained (8 curves, 6 dims)
  WALL - FRAME STILE - FRONT - TUBE  X 0.0..20.0  Y -20.0..0.0  Z 0.0..1150.0
step 3: rear stile. SECTION - STILE REAR TUBE: fully constrained (8 curves, 7 dims)
  WALL - FRAME STILE - REAR - TUBE   X 1450.0..1470.0  Y -20.0..0.0  Z 0.0..1150.0
step 4: rails. SECTION - RAIL BOTTOM TUBE: fully constrained (8 curves, 6 dims); SECTION - RAIL TOP TUBE: fully constrained (8 curves, 7 dims); SECTION - RAIL MID TUBE: fully constrained (8 curves, 7 dims)
  WALL - FRAME RAIL - BOTTOM - TUBE  X 20.0..1450.0  Y -20.0..0.0  Z 0.0..20.0
  WALL - FRAME RAIL - TOP - TUBE     X 20.0..1450.0  Y -20.0..0.0  Z 1130.0..1150.0
  WALL - FRAME RAIL - MID - TUBE     X 20.0..1450.0  Y -20.0..0.0  Z 565.0..585.0
step 5: rail holes. HOLE POSITION - TOP RAIL TO UPPER FRAME: fully constrained (0 curves, 2 dims); HOLE POSITION - BOTTOM RAIL TO BASE: fully constrained (0 curves, 2 dims)
  WALL - FRAME RAIL - TOP - TUBE     4 holes (expect 4), centres X,Y: [(60.0, -10.0), (510.0, -10.0), (960.0, -10.0), (1410.0, -10.0)]
                                     cylindrical faces 8 (2 walls per hole)
  WALL - FRAME RAIL - BOTTOM - TUBE  4 holes (expect 4), centres X,Y: [(60.0, -10.0), (510.0, -10.0), (960.0, -10.0), (1410.0, -10.0)]
                                     cylindrical faces 8 (2 walls per hole)
step 6: rear stile holes. HOLE POSITION - REAR STILE TO BACK WALL: fully constrained (0 curves, 2 dims)
  WALL - FRAME STILE - REAR - TUBE   4 holes (expect 4), centres Y,Z: [(-10.0, 60.0), (-10.0, 403.33), (-10.0, 746.67), (-10.0, 1090.0)]
  mid rail zone check (no hole within tube/2 + 12 of mid_rail_z): OK
step 7: ACP skin. OUTLINE - ACP SKIN: fully constrained (4 curves, 2 dims)
  WALL - SKIN ACP 3 - SIDE LOWER - LH - SHEET X 0.0..1500.0  Y 0.0..3.0  Z 0.0..1150.0
step 8: materials. tubes = Steel (frame_material 'Steel'); skin = ACP 3 mm PE core (effective 1300 kg/m3, ASSUMPTION), yellow paint look (stand-in for EV3038 Dark Yellow)
  WALL - FRAME STILE - REAR           0.812 kg  Steel, 103.4 cm3
  WALL - FRAME STILE - FRONT          0.815 kg  Steel, 103.8 cm3
  WALL - FRAME RAIL - BOTTOM          1.010 kg  Steel, 128.7 cm3
  WALL - FRAME RAIL - TOP             1.010 kg  Steel, 128.7 cm3
  WALL - FRAME RAIL - MID             1.013 kg  Steel, 129.0 cm3
  FRAME TOTAL                         4.661 kg  (frame, CALCULATION from CAD)
  ACP SKIN                            6.728 kg  (1.725 m2 x 3.9 kg/m2)
  PANEL ASSY                         11.388 kg  (limit 20 kg per part, v2 PLAN target 1)
step 9: checks
  timeline items: 31, not healthy: 0 
  sketches: 9, fully constrained: 9 
  features with default names: 0 
  timeline:  V2-SWL-10 WALL - PANEL FRAME - SIDE LOWER - LH:1 |  V2-SWL-11 WALL - FRAME STILE - REAR:1 |  V2-SWL-12 WALL - FRAME STILE - FRONT:1 |  V2-SWL-13 WALL - FRAME RAIL - BOTTOM:1 |  V2-SWL-14 WALL - FRAME RAIL - TOP:1 |  V2-SWL-15 WALL - FRAME RAIL - MID:1 |  V2-SWL-20 WALL - SKIN ACP 3 - SIDE LOWER - LH:1 | SECTION - STILE FRONT TUBE | EXTRUDE - STILE FRONT TUBE | SECTION - STILE REAR TUBE | EXTRUDE - STILE REAR TUBE | SECTION - RAIL BOTTOM TUBE | EXTRUDE - RAIL BOTTOM TUBE | SECTION - RAIL TOP TUBE | EXTRUDE - RAIL TOP TUBE | SECTION - RAIL MID TUBE | EXTRUDE - RAIL MID TUBE | PLANE - TOP RAIL TO UPPER FRAME HOLE ENTRY FACE | HOLE POSITION - TOP RAIL TO UPPER FRAME | HOLE - M6 CLEARANCE - TOP RAIL TO UPPER FRAME | PATTERN - TOP RAIL TO UPPER FRAME HOLES | PLANE - BOTTOM RAIL TO BASE HOLE ENTRY FACE | HOLE POSITION - BOTTOM RAIL TO BASE | HOLE - M6 CLEARANCE - BOTTOM RAIL TO BASE | PATTERN - BOTTOM RAIL TO BASE HOLES | PLANE - REAR STILE TO BACK WALL HOLE ENTRY FACE | HOLE POSITION - REAR STILE TO BACK WALL | HOLE - M6 CLEARANCE - REAR STILE TO BACK WALL | PATTERN - REAR STILE TO BACK WALL HOLES | OUTLINE - ACP SKIN | EXTRUDE - ACP SKIN
  user parameters: 18 (unitless only the hole counts: yes)
  RESULT: all checks pass
done through step 9
export: v2/01-CAD-Native/proof/V2-SWL-00_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_CAD.f3d
export: v2/03-Manufacturing/proof/V2-SWL-00_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_STEP.step  (STEP length unit: cm, declared in the file)
  model bounding box (assembly):  X -0.0..1500.0  Y -20.0..3.0  Z -0.0..1150.0
  STEP re-read bounding box:      X -0.0..1500.0  Y -20.0..3.0  Z -0.0..1150.0  (6 bodies)
  largest difference: 0.0000 mm -> MATCH
save: 'V2-SWL-00_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH' saved to Default Project / FocusPod v2
```
