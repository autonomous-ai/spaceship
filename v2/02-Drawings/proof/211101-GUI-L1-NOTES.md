# 211101 L1 frame drawing made through the Fusion GUI (bake-off entry)

Status: comparison piece for the L1 bake-off. Not for main unless Reviewer 5 picks it.

- Drawing in Fusion: `211101_P01_WALL-PANEL-FRAME-SIDE-LOWER-LH-GUI_DWG`, team folder, version 3 (2026-11-01 04:23 UTC).
- Design: `211101_P01_WALL-PANEL-FRAME-SIDE-LOWER-LH_CAD` as it was in the team folder (Fusion showed "1 reference is out of date" on it; not touched).
- PDF exported by `tools/fusion/export_drawing.py` (the "Created by" account name removed; checked: no account name in text or metadata).

## How it was made

Clicks and keys sent to Fusion's window, each button found by on-screen text (OCR) before it was clicked; one hold of the Fusion lock; nobody used the Mac.

1. Opened the design from Home search. New → Drawing, Automate off, ISO, mm, A2 landscape.
2. Base view Front (the frame face), visible edges only, 1:5. Projected views: above (seen from below), below (seen from above), right (front end). First-angle (Fusion's ISO default).
3. Auto Dimension (a GUI-only tool): ordinate style, density 35 of 35.
4. Moved the labels that sat inside the views or off the sheet.

Time: 25 minutes of GUI work (04:01 to 04:26 UTC), plus 9 minutes in a first try that stopped at the base view (another app came to the front).

## Checked against the STEP answer key

All ordinate values match: overall 1489.74 x 1142.74, stud edges 364.94/384.94, 729.87/749.87, 1094.81/1114.81, back stile 1449.74 to 1489.74, spigot 100, Ø7 holes 220 / 570.91 / 921.83 / 1272.74, slot edges 1388.49 / 1396.99 (centre 1392.74), front stile holes 220 / 571.37 / 922.74, back stile holes 220 / 559.31 / 898.61 at 1466.74. Text heights 2.5 mm caps (3.5 mm font) and up.

## What is missing or wrong (would not pass a careful drafter as it is)

- No notes: material and tube sizes, the coaxial Ø19 holes, deburr, general tolerances.
- No section view: the Ø19 holes in the far walls are hidden in visible-edge views, so the drawing does not show them.
- The hole notes say "Ø7 x 1.2" (depth = one wall); the slot's two ends and the spigot came out as "3x Ø8.5 x 1.2", which is wrong for the slot.
- Title block: DWG No. and Rev. are empty and the title is the CAD file name; double-click and right-click on the title block gave no way to edit the fields.
- No first-angle symbol on the sheet.
- Layout: the back-stile hole heights (220 / 559.31 / 898.61) have long leaders across the whole main view; the stud ordinates run through the strip view below; several separate "0" origins.

## What broke in the GUI

- The plan's "Left" orientation showed the frame's edge; "Front" is the face.
- Tidy Up shrank every view to about 1:16 and pushed dimensions past the border: undone.
- Dragging a label only selects it; moving it needs select, then drag its grip.
- A late Recovered Documents window came up 6 minutes after the relaunch (closed with Close).
- Closing the design while the drawing was open: Fusion said it closed but kept it open and marked the drawing changed; close the drawing first.
