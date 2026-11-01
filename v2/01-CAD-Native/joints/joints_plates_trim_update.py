"""Update run on the saved mitre plate family design (version 1 to version 2): the trimmed blanks.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/joints/joints_plates_trim_update.py \\
        --doc 831007_P01_HARDWARE-MITRE-PLATE-TABULATED_CAD --folder "Default Project/FocusPod v2/joints" --close

The Lead's steer (2026-11-01, WALL's L1 clash): each plate stays a laser-cut rectangle with square edges, made shorter
so its square ends sit about 0.5 inside the frame's faces on both plate faces. A plate the mitre's full size pokes out
at the frame's outer corner by its half thickness x the cut's cosine: 0.71 at 45 deg, and 0.45 (the back face) and
0.89 (the rail's face) where a 20 x 40 meets a 40 x 40. The blanks (joints_hardware_build.PLATE_BLANKS, checked by
frame_steel_check.py): 831007 26.5 from 1.75 along the mitre, 831008 41.5 from 3.15, 831009 54.8 from 1.75. The
origin stays at the frame's outer corner (WALL's placement doesn't move).

In the saved design: the old outline's extrude and sketch are deleted, the new parameters added (plate_mitre takes
the old plate_len formula; plate_x0; plate_len becomes the blank's length), and the build script's own
plate_geometry() draws the new outline, so a fresh build and this update make the same plate. The design is saved as
831007 (a new version, never a copy); the .f3d, three STEPs (each with its own part number) and three DXFs are
exported; an edit test moves the blank along the mitre and back; the document closes without keeping the per-STEP
changes.
"""
import importlib.util
import os
import time

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
REPO = ARGS.get("repo_root", "")
PLATES = "831007_P01_HARDWARE-MITRE-PLATE-TABULATED_CAD"
CAD_DIR = "v2/01-CAD-Native/joints"
MFG_DIR = "v2/03-Manufacturing/joints"


def build_module():
    """The build script, loaded by full path under a name of its own (Fusion keeps modules between runs)."""
    path = os.path.join(REPO, CAD_DIR, "joints_hardware_build.py")
    spec = importlib.util.spec_from_file_location("joints_hardware_build_plate_trim_%d" % int(time.time()), path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load " + path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    setattr(mod, "REPO", REPO)          # its own REPO comes from SCRIPT_ARGS, which an import doesn't have
    print("  build helpers from %s" % path)
    return mod


def export(em, opts, label):
    for _attempt in range(10):
        adsk.doEvents()
        if em.execute(opts):
            return
        time.sleep(3)
    raise RuntimeError("export failed: " + label)


def run(_context):
    app = adsk.core.Application.get()
    doc = app.activeDocument
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent
    if root.partNumber != "831007" or not doc.name.startswith(PLATES):
        raise RuntimeError("open %s with --doc first (active: %s, part %s)" % (PLATES, doc.name, root.partNumber))
    try:
        update(doc, design, root)
    except Exception:
        try:                         # nothing half-changed is left open for the next team's run
            if doc.isValid:
                doc.close(False)
                print("  closed %s without saving after the error" % PLATES)
        except Exception as e:
            print("  could not close %s: %s" % (PLATES, e))
        raise


def update(doc, design, root):
    jhb = build_module()
    up = design.userParameters
    if up.itemByName("plate_x0") is not None:
        raise RuntimeError("plate_x0 is already there: this design has had the update")
    ext = root.features.extrudeFeatures.itemByName(jhb.PLATE_EXTRUDE)
    sk = root.sketches.itemByName(jhb.PLATE_SKETCH)
    if ext is None or sk is None:
        raise RuntimeError("the saved design has no %r or %r" % (jhb.PLATE_EXTRUDE, jhb.PLATE_SKETCH))
    old = jhb.box(root.bRepBodies.item(0))
    print("  the saved plate (831007): %s" % jhb.fmt(old))
    if not ext.deleteMe() or not sk.deleteMe():
        raise RuntimeError("could not delete the old outline")
    # parameters: add what's new, give plate_len the blank's length, and every comment as the build writes it
    for name, expr, unit, comment in jhb.PLATE_PARAMS:
        p = up.itemByName(name)
        if p is None:
            if up.add(name, jhb.vi(expr), unit, comment) is None:
                raise RuntimeError("could not add parameter " + name)
        else:
            if name == "plate_len":
                p.expression = expr
            p.comment = comment
    body = jhb.plate_geometry(design, root)
    mat = jhb.material(root, ["Steel, Galvanized", "Steel"], ["steel"])
    jhb.health(design)
    print("  new outline: %s, material %s" % (jhb.fmt(jhb.box(body)), mat))
    v0 = jhb.PLATE_VARIANTS[0]
    jhb.plate_state(design, root, v0)
    family = ("831007", "%s | %s | rev %s | %s" % (
        v0[1], "Tấm đệm góc vát - thép 2.0", jhb.REV,
        "UNITS MM; MATERIAL S280GD+Z (EN 10346) OR SGC400, Z100, 2.0 SHEET; ISO 2768-m; THICKNESS 2.0 +-0.1; laser "
        "cut, no drawing (D-89 part 4); BLANKS 831007 26.5 X 40, 831008 41.5 X 40, 831009 54.8 X 40, EACH END 0.5 "
        "INSIDE THE FRAME'S FACES; joints register H-40 to H-42; PROPOSED"))
    root.partNumber, root.description = family
    if not doc.save("Mitre plate blanks trimmed so each square end sits 0.5 inside the frame's faces (the Lead's "
                    "steer 2026-11-01): 831007 26.5, 831008 41.5, 831009 54.8 long; joints_plates_trim_update.py"):
        raise RuntimeError("save failed")
    em = design.exportManager
    f3d = os.path.join(REPO, CAD_DIR, PLATES + ".f3d")
    export(em, em.createFusionArchiveExportOptions(f3d, root), "f3d")
    print("saved (a new version) and exported %s" % os.path.basename(f3d))
    for v in jhb.PLATE_VARIANTS:
        jhb.plate_state(design, root, v)
        path = os.path.join(REPO, MFG_DIR, v[4] + "_STEP.step")
        for _attempt in range(10):
            adsk.doEvents()
            if em.execute(em.createSTEPExportOptions(path, root)) and os.path.exists(path) and \
                    os.path.getsize(path) > 2000:
                break
            time.sleep(3)
        else:
            raise RuntimeError("STEP export failed: " + path)
        print("  STEP %s as %s" % (os.path.basename(path), v[0]))
    jhb.write_plate_dxfs(design, root)
    jhb.plate_state(design, root, v0)
    root.partNumber, root.description = family
    jhb.plate_edit_test(design, root)
    if not doc.close(False):
        raise RuntimeError("close failed")
    print("closed %s (the per-STEP changes and the edit test were not kept; the saved version is 831007)" % PLATES)
