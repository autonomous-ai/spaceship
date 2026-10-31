"""INTERIOR drawings through the ceiling's drawing machinery (views, dimensions, hole tables, the
first-angle symbol, the notes and title images, the PDF), with AIR's specs.

    python3 tools/fusion/run_script.py v2/02-Drawings/interior/make_drawing_interior.py \\
        --arg parts=ledge,shelf_back --label "CEILING Engineer (INTERIOR)" --timeout 1200
"""

import importlib
import os
import sys

ARGS = globals().get("SCRIPT_ARGS", {})
HERE = os.path.dirname(os.path.abspath(__file__))
CEIL = os.path.join(HERE, "..", "ceiling")
for d in (HERE, CEIL):
    if d not in sys.path:
        sys.path.insert(0, d)
import drawing_specs_interior as S  # noqa: E402
importlib.reload(S)
import make_drawing_ceiling as MD  # noqa: E402
importlib.reload(MD)
import annotate_many as AM  # noqa: E402
importlib.reload(AM)


def run(_context):
    MD.S, MD.HERE, MD.STYLES = S, HERE, {}
    AM.S, AM.MD = S, MD
    AM.ARGS = ARGS
    AM.run(_context)
