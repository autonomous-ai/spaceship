"""Which parts drawgen draws, and the few choices a STEP can't give: datums, extra notes and the tolerance note.

The entries live in one file per team, tools/drawgen/teams/<team>.py (D-139: each team edits its own parts'
entries in its own PRs, so they don't collide); the file name is the team's folder name under v2/03-Manufacturing
and v2/02-Drawings. This file only gathers them into SPECS and NO_DRAWING, plain data the mechanical check (C05)
and the release checklist also read. A number in two files, or in both lists, is an error.

Everything else (views, sections, holes, sizes, names, material, finish, revision) is read from the part's STEP,
its team parts list and the feature registers each time the drawing is made. Tolerances are the project's own,
from the joints register, the parts lists and the team drawings; never a blanket ISO 2768 (guideline 3.2).
"""

import glob as _glob
import importlib.util as _ilu
import os as _os

_TEAMS = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "teams")

# pn: (team, kind, spec). kind "part": one part on its own drawing.
SPECS = {}
# Parts that need no drawing at all, and why (drawgen won't make one).
NO_DRAWING = {}
for _path in sorted(_glob.glob(_os.path.join(_TEAMS, "*.py"))):
    _team = _os.path.splitext(_os.path.basename(_path))[0]
    if _team.startswith("_"):
        continue
    _s = _ilu.spec_from_file_location("drawgen_team_" + _team, _path)
    _m = _ilu.module_from_spec(_s)
    _s.loader.exec_module(_m)
    for _pn, _conf in getattr(_m, "PARTS", {}).items():
        if _pn in SPECS or _pn in NO_DRAWING:
            raise ValueError("drawgen: %s is listed twice (%s, and %s)" % (_pn, _team, SPECS.get(_pn, ("no drawing",))[0]))
        SPECS[_pn] = (_team, "part", _conf)
    for _pn, _why in getattr(_m, "NO_DRAWING", {}).items():
        if _pn in SPECS or _pn in NO_DRAWING:
            raise ValueError("drawgen: %s is listed twice (%s's no-drawing list, and elsewhere)" % (_pn, _team))
        NO_DRAWING[_pn] = _why

# The sample the PM reviewed before anything else was generated (#202): the frame, its RH pair, the tube. The
# sample's table drawing of the fills was dropped by D-128 (the fill pieces go on DXFs), and its plate (811205)
# needed no drawing under D-125, then D-126 cancelled it.
SAMPLE = ["211101", "211102", "111101"]
