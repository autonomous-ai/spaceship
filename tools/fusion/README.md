# Fusion scripting through the local MCP

How agents drive Autodesk Fusion on Mac 1, what worked in the v2 Phase 0 proof, and the limits we hit. Read this before writing CAD or drawing scripts.

Found on 2026-10-31 with Fusion 2706.1.17. Proof part: `v2/01-CAD-Native/proof/`.

## Tools here

| File | What it does |
|---|---|
| `run_script.py` | Sends a Fusion API script file to Fusion's MCP server and prints what the script printed. Every run takes **the Fusion lock** first (below), so only one script drives Fusion at a time. Exit 0 = ran, 1 = the script or a document step raised (traceback with the real file and line), 2 = Fusion not reachable, 3 = the lock was busy past `--lock-wait`. `--arg KEY=VALUE` reaches the script as `SCRIPT_ARGS`; `--read-only` for inspect-only scripts; `--screenshot out.png --direction front` saves a zoomed-to-fit picture; `--doc NAME` / `--doc-new` / `--save` / `--close` open your own document, save it and close it. Standard library only. |
| `test_run_script.py` | Offline tests of the lock and the document steps against a fake Fusion MCP server: `python3 tools/fusion/test_run_script.py`. |
| `step_check.py` | Reads a STEP file without Fusion: declared length unit, products, solids and the bounding box in mm. `--expect xmin,ymin,zmin,xmax,ymax,zmax` checks it. Never edits the file. |
| `pdf_clear_field.py` | Removes a title block field's value (default "Created by", which Fusion fills with the account holder's name) from an exported drawing PDF, then re-reads it to prove the text is gone. Needs PyMuPDF. |

```sh
python3 tools/fusion/run_script.py v2/01-CAD-Native/proof/wall_panel_frame.py --arg close_previous=1
python3 tools/fusion/run_script.py v2/01-CAD-Native/proof/edit_test.py
python3 tools/fusion/step_check.py v2/03-Manufacturing/proof/V2-SWL-00_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_STEP.step --expect=0,-20,0,1500,3,1150
```

## Ground rules

- Fusion's MCP server answers only on this Mac, at `http://127.0.0.1:27182/mcp`. It runs every script on the **active** document of the one Fusion app. Several agents write scripts in parallel; Fusion runs them one at a time. **Always go through `run_script.py`**, which takes the Fusion lock. Calling Fusion's MCP tools directly (for example the `fusion` MCP tools in Claude Code or Codex) skips the lock and can run in the middle of someone else's script.
- A script must define `run(_context)`. Don't catch exceptions in it: an uncaught one is how the runner learns it failed.
- Never close, save or change a document you didn't create. Unsaved documents are all called "Untitled", so find your own by something you set, such as the root component's part number.
- A script cannot run while a command dialog is open in Fusion. `--read-only` scripts can, but they may not change anything.

## One run at a time: the Fusion lock

Several Engineers write Fusion scripts at once, and the one Fusion runs them one after the other. `run_script.py` makes that safe:

- **The lock.** Before it talks to Fusion, every run makes the directory `/tmp/fusion-mcp-27182.lock` (`mkdir` is atomic, so exactly one run gets it) and writes `owner.json` in it: label, script, worktree, process id, since and expiry. It keeps the lock for the whole run (document steps, script, screenshot) and removes it at the end, also after an error, Ctrl-C or SIGTERM. Every worktree on this Mac uses the same path; `--lock DIR` or `$FUSION_MCP_LOCK` changes it (tests only).
- **Waiting, oldest first.** A run that finds the lock taken takes a ticket in `/tmp/fusion-mcp-27182.lock.queue` and waits its turn: only the oldest live ticket may take the lock, so no run loses every race. It prints who holds the lock and how many runs are ahead every 30 s, and gives up after `--lock-wait` seconds (default 1200) with exit 3. Tickets of runs that have ended are dropped. Set `--label` or `$FUSION_MCP_LABEL` (for example `"WALL engineer"`) so the others see who they wait for. A long wait can pass a tool call's time limit, so start long runs in the background.
- **Crashed runs.** A lock whose process has ended (checked by process id; `/tmp` is local to this Mac, so the hostname doesn't matter), or that is past its expiry, is stale: the next run in line clears it, under a guard directory (`.guard`), so two runs can't clear a fresh lock, and says so. Anything else at the lock path (a plain file, a link, a lock it can't delete) counts as held: the run says once that it can't clear it and gives up at `--lock-wait` with exit 3.
- **UNVERIFIED:** whether Fusion finishes a killed run's script before it starts the next one. Not tested; if a run is killed mid-script, check the document before the next run builds on it.
- **Who has it now:** `python3 tools/fusion/run_script.py --lock-status`.

Each run looks after its own document, so it never depends on what the run before it left active:

```sh
# make the design the first time (new mm parametric design, saved into Default Project / FocusPod v2)
python3 tools/fusion/run_script.py build.py --doc PARTNO_P01_DESCRIPTIVE-NAME_CAD --doc-new --save "first build" --close
# later runs: activate it if open, else open it from the folder; save and close at the end
python3 tools/fusion/run_script.py add_holes.py --doc PARTNO_P01_DESCRIPTIVE-NAME_CAD --save "rail holes" --close
```

- `--doc NAME` runs before the script: it activates the open document called NAME, or opens the file NAME from `--folder` (default `Default Project/FocusPod v2`), and fails if there are two of either. `--doc-new` makes it when it doesn't exist.
- `--save [DESCRIPTION]` (a new version) and `--close` run after the script and the screenshot, only when the script succeeded. `--close` refuses to drop unsaved changes unless `--discard` is given; it never shows Fusion's save prompt.
- Exports stay in your script, after a save: save, export (with the STEP retries below), then let `--close` close it. A script that makes its own document (like the proof and skeleton scripts) can skip `--doc` but must still save and close what it opened.

**Steps that must stay together** across several runs (a script, then a click in Fusion, then another script, as when starting a drawing) hold the lock, at most an hour:

```sh
export FUSION_MCP_LOCK_TOKEN=$(python3 tools/fusion/run_script.py --lock-hold 900 --label "drawing start")
python3 tools/fusion/run_script.py step1.py     # runs inside the held lock, no waiting
python3 tools/fusion/run_script.py step2.py
python3 tools/fusion/run_script.py --lock-release
```

A held lock has no live process behind it, so only its expiry ends it if you forget `--lock-release`. Each run that joins it moves the expiry out to cover that run (under the guard), so a hold can't run out while one of its runs is still in Fusion.

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
- **Save first, then export with retries.** Save the design before exporting, so the exports come from a saved version (review note on PR #6). A STEP export started right after `Document.saveAs` (while Fusion is still uploading) returned False and wrote a header-only file, so retry: call `adsk.doEvents()`, wait 3 s, try again, up to 10 times (`pod_skeleton.py` does this).
- **Edit test (guideline section 4.4)**: open the exported .f3d as a copy (`importToNewDocument(createFusionArchiveImportOptions(path))`), change parameters, call `adsk.doEvents()`, check timeline health and measure every body, revert, compare with the "before" values, close without saving. See `v2/01-CAD-Native/proof/edit_test.py`.

## Pod skeleton (Milestone 2)

`v2/01-CAD-Native/skeleton/pod_skeleton.py` builds the whole pod as envelope bodies, one component per panel, block, band or pane, under the assembly tree's components. Each envelope is a polygon on an XY plane offset by a parameter, its corners dimensioned from the origin with `abs(<coordinate expression>)` (or aligned to the origin when the coordinate is 0), and extruded by a parameter, so every sketch is fully constrained and every size follows the parameter table. Two rules from the PR #6 review are built in: **the clash check fails the run** (every pair of envelopes is intersected; an overlap over 1 mm3 that is not on the script's list of intended overlaps, each with its reason, raises an error), and the design is **saved before the STEP export**. The current revision is **P04** (`BUILD-RECORD.md`). `edit_test_skeleton.py` checks every envelope against its own expressions after an edit; `skeleton_view.py` sets the cameras for the renders.

## Linking a part to the skeleton

The skeleton is the single source for the pod's sizes. Every user parameter in `100000_P04_POD-SKELETON_CAD` is a **favorite**, so a part design takes them with Fusion's Derive and stays linked:

```python
skel_file = <the DataFile "100000_P04_POD-SKELETON_CAD" in Default Project / FocusPod v2>
skel_doc = app.documents.open(skel_file, False)          # invisible
skel = adsk.fusion.Design.cast(skel_doc.products.itemByProductType("DesignProductType"))
part_doc.activate()
di = root.features.deriveFeatures.createInput(skel)
di.isIncludeFavoriteParameters = True
di.sourceEntities = [skel.rootComponent.xYConstructionPlane]   # parameters only; add a body if you want it
root.features.deriveFeatures.add(di)
skel_doc.close(False)
design.userParameters.add("panel_h", ValueInput.createByString("side_h_Ref"), "mm", "SOURCE: skeleton P04 side_h (1142.74)")
```

- Derived parameters arrive as **`<name>_Ref`** (`side_h_Ref`, `wall_depth_Ref`) and work in the part's own expressions; only favorites come across.
- When the skeleton saves a new version, the part reports `Document.isUpToDate == False`; `Document.updateAllReferences()` brings the new values in and the part's expressions follow. Tested 2026-10-31 on throwaway designs (300 -> 400 mm after the source changed).
- A script that raises an exception has all its changes rolled back (found twice on 2026-10-31), so derive and use the parameters in the same successful run.
- Skeleton changes that keep its shape (new values) go in as new versions of the same cloud file; a new revision (P05) is a new file, and parts then derive from it.

## Saving to the Fusion cloud

Drawings need a saved design (`DrawingManager.createDrawingInput` takes a cloud `DataFile`). Save with `document.saveAs(name, folder, description, "")` into **Default Project / FocusPod v2**. The proof script refuses to save when a file with the same name is already there, so the folder keeps one copy.

## Drawings: the sequence that worked (2026-10-31)

1. Point the Data Panel at the right project first: `app.data.activeProject = <Default Project>`, then open the saved design. Without this, Fusion's Create Drawing command logged "No valid project id, using first project and root folder path" (the first project is the special Assets project) and **Fusion crashed** a second later.
2. Start Create Drawing outside your script: `ui.commandDefinitions.itemById("FusionDrawingCreateFromComponentsCommand").execute()` queues it to run after the script returns. Its dialog defaults to Manual, From scratch, ISO, mm.
3. One click on OK. Fusion's MCP refuses every script while a dialog is open ("Cannot perform 'script' while a command dialog is open"), so a script can't press OK or Cancel. Fusion then opens the Base View dialog by itself: one click on Cancel. On 2026-10-31 the Lead made both clicks through the macOS accessibility controls. These two clicks are the only steps done outside the API.
4. `make_drawing.py --arg step=save`: sets A2 and saves the empty drawing into FocusPod v2.
5. `--arg step=front`, then `top`, then `right`: one view per call, each saved. Then `dims_front`, `dims_top`, `dims_right`, and `export`. See `v2/02-Drawings/proof/DRAWING-RECORD.md`.
6. `python3 tools/fusion/pdf_clear_field.py <raw pdf> <repo pdf>`: removes the account holder's name that Fusion prints under "Created by" (text removed, not covered). Only that copy goes into the repo; raw exports go to the git-ignored `.raw/` folder.

Keep every call small, and save after each step. Fusion hung twice during this work and lost an unsaved drawing once.

## Leftover clicks for whoever unlocks the Mac (proof drawing)

In Fusion, Default Project / FocusPod v2 / `V2-SWL-00_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_DWG`:

1. Delete sheets 1 and 2: Sheet1 is the first try and CLEAN is the second try. Keep CLEAN2, the sheet in the repo PDF.
2. Title block on CLEAN2: DWG No. V2-SWL-00, Rev. P01, Document status DRAFT, Document type ASSEMBLY DRAWING, units mm, scale 1:5, material "see parts list"; clear "Created by". The API can't set these: the design's part number is set but DWG No. doesn't read it, and there is no revision property.
3. Save, then save the sheet as our drawing template (Fusion's New Drawing Template or Output Drawing Template command), so later drawings start without the two clicks.
4. Add sections A-A (through H01) and B-B (through H09) at 2:1; the API can't make section views.
5. Re-export: `make_drawing.py --arg step=export --arg sheet=CLEAN2 --arg sheet_range=1` (after the old sheets are gone), then `pdf_clear_field.py`.

## Drawings: what works and what needs a person

The drawing API (`adsk.drawing`) is a preview API in this build. Tested on 2026-10-31:

- **Starting a drawing takes two clicks.** `DrawingManager.createDrawing` can't do it here: manual creation needs a drawing template with view placeholders (none ships with the install, none in the hub), and automatic creation hung. Fusion's own Create Drawing command works when started as in the sequence above, with one OK and one Cancel click.
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
| STEP right after save | `execute()` returns False; the file has only the header | Save first, then retry the export (doEvents, 3 s wait, up to 10 tries) |
| Screenshot framing | The MCP screenshot `direction` turns the camera but doesn't zoom to fit | `run_script.py --screenshot` turns and fits first |
| Named views | Fusion's "Front" looks along +Y; both iso views look from the -Y side | Name views and renders by pod direction (conventions.md section 4: front = the door side, -Y; left/right as seen from outside facing the door), never by Fusion's view names. In the pod system Fusion's "Front" is the pod's front view; in the proof part's own system it was the view from inside the pod |
| Manual drawing creation | `DrawingManager.createDrawing(input)` with `ManualDrawingCreationMode` raises `RuntimeError: 3 : Manual drawing creation requires a template with view placeholder information.` | A person starts the first sheet once |
| Automatic drawing creation | `createDrawing` with `AutomaticDrawingCreationMode` (sub-assembly sheet only, auto dimensions off) never returned: over 10 minutes, Fusion idle, a second copy of the design opened, no drawing made | Same |
| Drawing templates | No API call saves a template; no `.f2t` in the install or the hub | A person saves one template once |
| Projected, section, detail views | `adsk.drawing.Views` has only `createBaseViewInput` and `add` | Aligned base views; sections listed for a person |
| Text and hatch on sheets | `DrawingSketch` has no text or hatch collections | Custom tables for notes |
| Sheet units | The API help says sheet points are in cm; in this build `Sheet.width`, view curve points and `BaseViewInput.placementPoint` are all mm (A2 = 594 x 420) | Work in mm; `make_drawing.py` checks it on the front view |
| Placement point type | `BaseViewInput.placementPoint = Point2D` raises `TypeError ... argument 2 of type 'adsk::core::Ptr< adsk::drawing::DrawingPoint > const &'` | `DrawingPoint.create(Point2D.create(x, y))` |
| View scale | `viewParameters.scaleValue = 0.2` on the input was ignored; the view came out 1:10 | Set `View.scaleValue` after `Views.add` |
| View orientation | Reading `View.orientation` of a view the API had just added raised `RuntimeError: 3 : failed to read view orientation`; Fusion hung soon after | Tell views apart by their size on the sheet |
| Hole table, view from above | `HoleTables.add` succeeded but the table has no rows (the view from the right worked, tags A1-A4) | Dimensions on the view carry the positions; listed for a person |
| Hole tags, table position | No API for the tag letters (Fusion uses A1, A2, ... per table) or for where tables go: both landed stacked at the top right, over the front view | Listed for a person |
| Text in custom tables | `CustomTable.setCellData(row, col, text)` returns True, but `getCellData` reads back `''` and the PDF cells are blank | No free text on sheets by API |
| Deleting anything | `HoleTables.item(i)` and `Drawing.deleteEntities(...)` raise `RuntimeError: 5 : API Function not yet implemented` | Views and tables can't be removed or moved by API |
| Title block text | `TitleBlock.setAttributes` places tags only; values come from properties. "Created by" prints the Fusion account holder's name | `pdf_clear_field.py` strips it from the PDF; a person fills the fields once and saves a template |
| After a restart | A "Recovered Documents" dialog blocks every script until someone closes it | Check `activeCommand` first |
| **Fusion froze** | A wide API help search (`fusion_mcp_read`, `queryType: apiDocumentation`, pattern `[Tt]emplate`, category `all`, no filter) timed out and Fusion sat at 100% CPU until restarted | Always give API help searches a narrow `filter` such as `adsk.drawing.Views`. The Python stubs on disk (`Autodesk Fusion.app/Contents/Api/Python/packages/adsk/*.py`) can be searched offline with grep |
