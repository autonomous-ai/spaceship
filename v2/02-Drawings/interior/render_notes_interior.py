"""Render the INTERIOR drawings' notes and title data as PNG images (offline), as the ceiling's."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "ceiling"))
import drawing_specs_interior as S  # noqa: E402
import render_notes as RN  # noqa: E402

RN.S, RN.OUT = S, os.path.join(HERE, ".notes")
if __name__ == "__main__":
    RN.main()
