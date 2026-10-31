"""Measure every solid in the v1 STEP: volume, surface area, bounding box, oriented box, centre of mass.

Writes data/v1_step_solids.csv, which v1_weights.py and v2_model.py read. Not run by run_all.py because it needs
cadquery-ocp (OpenCascade). Set up once, outside the repo:

    uv venv /tmp/occ --python 3.12 && uv pip install --python /tmp/occ/bin/python cadquery-ocp
    /tmp/occ/bin/python -I scripts/step_crosscheck.py ../../../sources/v1/indoor-pod-v3-assembly.step data/v1_step_solids.csv

Run from v2/05-Engineering/layout-study. Solid numbers follow the STEP reader's order and are stable for the same
file and reader version. Units: mm, mm2, mm3.
"""
import sys, csv
from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.Bnd import Bnd_Box, Bnd_OBB
from OCP.BRepBndLib import BRepBndLib
from OCP.TopAbs import TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
path, out = sys.argv[1], sys.argv[2]
r = STEPControl_Reader()
assert r.ReadFile(path) == IFSelect_RetDone
r.TransferRoots()
shape = r.OneShape()
rows = []
exp = TopExp_Explorer(shape, TopAbs_SOLID)
i = 0
while exp.More():
    s = TopoDS.Solid(exp.Current()); i += 1
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g)
    a = GProp_GProps(); BRepGProp.SurfaceProperties_s(s, a)
    b = Bnd_Box(); BRepBndLib.Add_s(s, b, False)
    mn=b.CornerMin(); mx=b.CornerMax(); x0,y0,z0,x1,y1,z1 = mn.X(),mn.Y(),mn.Z(),mx.X(),mx.Y(),mx.Z()
    o = Bnd_OBB(); BRepBndLib.AddOBB_s(s, o, True, True, False)
    od = sorted([2*o.XHSize(), 2*o.YHSize(), 2*o.ZHSize()])
    c = g.CentreOfMass()
    rows.append([i, round(g.Mass(),1), round(a.Mass(),1), round(x1-x0,1), round(y1-y0,1), round(z1-z0,1),
                 round(od[0],1), round(od[1],1), round(od[2],1), round(c.X(),1), round(c.Y(),1), round(c.Z(),1)])
    exp.Next()
with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["solid","volume_mm3","area_mm2","bbx","bby","bbz","obb1","obb2","obb3","cx","cy","cz"])
    w.writerows(rows)
print(i, "solids")
