# Fusion scripting through the local MCP

How agents drive Autodesk Fusion on Mac 1, what worked in the v2 Phase 0 proof, and the limits we hit. Read this before writing CAD or drawing scripts.

Found on 2026-10-31 with Fusion 2706.1.17. Proof part: `v2/01-CAD-Native/proof/`.

## Tools here

| File | What it does |
|---|---|
| `run_script.py` | Sends a Fusion API script file to Fusion's MCP server and prints what the script printed. Exit 0 = ran, 1 = the script raised (traceback with the real file and line), 2 = Fusion not reachable. `--arg KEY=VALUE` reaches the script as `SCRIPT_ARGS`; `--read-only` for inspect-only scripts; `--screenshot out.png --direction front` saves a zoomed-to-fit picture. Standard library only. |
| `step_check.py` | Reads a STEP file without Fusion: declared length unit, products, solids and the bounding box in mm. `--expect xmin,ymin,zmin,xmax,ymax,zmax` checks it. Never edits the file. |

```sh
python3 tools/fusion/run_script.py v2/01-CAD-Native/proof/wall_panel_frame.py --arg close_previous=1
python3 tools/fusion/run_script.py v2/01-CAD-Native/proof/edit_test.py
python3 tools/fusion/step_check.py v2/03-Manufacturing/proof/V2-SWL-00_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_STEP.step --expect=0,-20,0,1500,3,1150
```

## Ground rules

- Fusion's MCP server answers only on this Mac, at `http://127.0.0.1:27182/mcp`. It runs every script on the **active** document of the one Fusion app, so only one agent may drive Fusion at a time. Others write and review scripts and hand them over.
- A script must define `run(_context)`. Don't catch exceptions in it: an uncaught one is how the runner learns it failed.
- Never close, save or change a document you didn't create. Unsaved documents are all called "Untitled", so find your own by something you set, such as the root component's part number.
- A script cannot run while a command dialog is open in Fusion. `--read-only` scripts can, but they may not change anything.

## Recipe that worked: a native, editable part

The proof script `v2/01-CAD-Native/proof/wall_panel_frame.py` follows these steps. Copy its helpers.

1. **New document.** `app.documents.add(FusionDesignDocumentType)`, then `design.designType = ParametricDesignType` and `fusionUnitsManager.distanceDisplayUnits = MillimeterDistanceUnits`.
2. **User parameters first**, each with a unit and a comment carrying its status and source (SOURCE / CALCULATION / ASSUMPTION / PROPOSED / HOLD). Derived values are expressions: `ceil((frame_width - 2 * hole_edge_dist) / rail_hole_pitch_max) + 1` works. A text parameter uses unit `"Text"` and a quoted value: `"'Steel'"`.
3. **One component per part** (`occurrences.addNewComponent(identity)`), with `name`, `partNumber` and `description` set. Build each part's geometry inside its own component, on that component's origin planes.
4. **Sketches on defined planes**: the origin planes, or construction planes offset by a parameter expression (`setByOffset(plane, ValueInput.createByString("frame_height"))`). Draw each curve at its true size first, then add dimensions and set `dimension.parameter.expression`, so the solver never has to move anything. Use `sketch.modelToSketchSpace()` to place points and to work out which sketch axis a model axis maps to (it differs per plane). Finish with `sketch.isFullyConstrained`. Never fix geometry to fake it.
5. **Features named by function** (`feature.name = "EXTRUDE - RAIL TOP TUBE"`), bodies and sketches too. A rail starts off its sketch plane with `OffsetStartDefinition.create(ValueInput("tube_size"))`.
6. **Holes**: `holeFeatures.createSimpleInput(ValueInput("hole_dia"))`, `setPositionBySketchPoint(point)`, `setDistanceExtent(ValueInput("tube_size"))` to go through both walls of a tube, and `participantBodies = [body]`. The hole runs against the sketch plane normal; set `isDefaultDirection = False` to flip it. Pattern it with `rectangularPatternFeatures.createInput(features, axis, ValueInput("rail_hole_count"), ValueInput("frame_width - 2 * hole_edge_dist"), ExtentPatternDistanceType)`, so the count and pitch follow the parameters.
7. **Measure after every step** and compare with intent: body bounding boxes, hole centres (read them from the cylindrical faces of the hole diameter), sketch constraint state, timeline health (`timeline.item(i).healthState`), mass (`component.getPhysicalProperties()`). Then take a screenshot. The proof script runs in steps with `--arg stop_after=N`.
8. **Materials** from the Fusion Material Library by name ("Steel", "Aluminum"). For a material the library lacks, copy one into the design (`design.materials.addByCopy`) and set `materialProperties.itemById("structural_Density").value` (kg/m3). Say in the name that it is an assumption.

## Exports and checks

- **.f3d**: `exportManager.createFusionArchiveExportOptions(path, rootComponent)`. It keeps the timeline, sketches and parameters.
- **STEP**: `createSTEPExportOptions(path, rootComponent)`. Fusion writes it in **centimetres**, even with the design in mm and the units set again right before the export, and `STEPExportOptions` has no unit setting. The unit is declared in the file, so every CAD reads it at true size. DECIDED by the PM (2026-10-31): keep Fusion's STEP as written, don't convert it, and record "STEP length unit: cm, declared in the file". Drawings and DXF must be in mm.
- **Re-read the STEP twice**: in Fusion (`importManager.importToNewDocument(createSTEPImportOptions(path))`, compare `rootComponent.boundingBox`, close the copy with `close(False)`), and with `step_check.py`, which applies the declared unit.
- **Export before you save.** A STEP export started right after `Document.saveAs` (while Fusion is still uploading) returned False and wrote a file with only the header. Five seconds later the same call worked.
- **Edit test (guideline section 4.4)**: open the exported .f3d as a copy (`importToNewDocument(createFusionArchiveImportOptions(path))`), change parameters, call `adsk.doEvents()`, check timeline health and measure every body, revert, compare with the "before" values, close without saving. See `v2/01-CAD-Native/proof/edit_test.py`.

## Saving to the Fusion cloud

Drawings need a saved design (`DrawingManager.createDrawingInput` takes a cloud `DataFile`). Save with `document.saveAs(name, folder, description, "")` into **Default Project / FocusPod v2**. The proof script refuses to save when a file with the same name is already there, so the folder keeps one copy.

## Drawings: what works and what needs a person

The drawing API (`adsk.drawing`) is a preview API in this build. Tested on 2026-10-31:

- **Starting a drawing needs a person once.** Manual creation needs a drawing template with view placeholders, and none exists (no `.f2t` ships with the install, none in the hub). Automatic creation hung. So a person makes the first sheet in Fusion: open the saved design, File > New Drawing > From Design, ISO, mm, A2, save. After that, scripts do the rest on the open drawing (`v2/02-Drawings/proof/make_drawing.py`).
- **Templates can't be made by script.** `DrawingDocument.saveAs` writes a normal drawing (`.f2d`), and `DrawingExportManager` exports PDF, DWG and DXF only. To start later drawings by script, a person saves one drawing as a template once in Fusion. `CreateDrawingInput.templateFile` then takes it (a cloud `DataFile`), and `DataFolder.uploadFile` can upload a template file kept in the repo.
- **Views.** `Views.add` makes base views only. Projected, section and detail views can't be created by the API. The PM ruled that base views at the same scale, aligned in the first-angle layout, are fine. Sections go on the person list. A base view shows the whole design (`BaseViewInput` "uses the drawing's active model reference"), so make the drawing from the design you want to show.
- **Dimensions** attach to view geometry: `DrawingDimensions.addLinearDimension(a, b, place, False)` with `a`, `b` taken from `ViewCurve.startPoint`, `endPoint` or `centerPoint`. Take datum points from line ends and hole centres from circles. A hole through two tube walls can show as two coincident circles; keep one per centre.
- **Hole tables**: `HoleTables.createInput()`, set `view`, `originPoint` (a point on that view's geometry: put it on the datum corner) and `title`, then `add`. One origin marker per view.
- **Text**: sheet sketches (`DrawingSketch`) have lines, rectangles, circles, arcs and ellipses, but no text and no hatch. Title block values come from the model and document properties: `TitleBlock.setAttributes` only places predefined tags. Free text goes in a custom table (`CustomTables`), whose position the API can't set.
- **Test offline first.** `v2/02-Drawings/proof/test_make_drawing_offline.py` fakes the few drawing objects and checks the annotation logic without Fusion.

## Limits found

| What | Exact call or message | Workaround |
|---|---|---|
| STEP unit | `ExportManager.createSTEPExportOptions` writes `SI_UNIT(.CENTI.,.METRE.)`; `STEPExportOptions` has only `wantTempIds` | Keep it (unit declared in the file); check with `step_check.py` |
| STEP of one occurrence | `createSTEPExportOptions(path, occurrence)` raises `RuntimeError: 3 : invlid argument geometry` | Export the root component |
| STEP right after save | `execute()` returns False; the file has only the header | Export before `saveAs` |
| Screenshot framing | The MCP screenshot `direction` turns the camera but doesn't zoom to fit | `run_script.py --screenshot` turns and fits first |
| Named views | Fusion's "Front" looks along +Y; both iso views look from the -Y side | Put the side you want to see in drawings toward -Y |
| Manual drawing creation | `DrawingManager.createDrawing(input)` with `ManualDrawingCreationMode` raises `RuntimeError: 3 : Manual drawing creation requires a template with view placeholder information.` | A person starts the first sheet once |
| Automatic drawing creation | `createDrawing` with `AutomaticDrawingCreationMode` (sub-assembly sheet only, auto dimensions off) never returned: over 10 minutes, Fusion idle, a second copy of the design opened, no drawing made | Same |
| Drawing templates | No API call saves a template; no `.f2t` in the install or the hub | A person saves one template once |
| Projected, section, detail views | `adsk.drawing.Views` has only `createBaseViewInput` and `add` | Aligned base views; sections listed for a person |
| Text and hatch on sheets | `DrawingSketch` has no text or hatch collections | Custom tables for notes |
| **Fusion froze** | A wide API help search (`fusion_mcp_read`, `queryType: apiDocumentation`, pattern `[Tt]emplate`, category `all`, no filter) timed out and Fusion sat at 100% CPU until restarted | Always give API help searches a narrow `filter` such as `adsk.drawing.Views`. The Python stubs on disk (`Autodesk Fusion.app/Contents/Api/Python/packages/adsk/*.py`) can be searched offline with grep |
