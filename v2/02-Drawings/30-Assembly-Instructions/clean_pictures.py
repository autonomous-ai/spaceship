"""The guide's step pictures without the layout grid, the axes or the origin mark.

    python3 v2/02-Drawings/30-Assembly-Instructions/clean_pictures.py RAW_DIR                # writes img/
    python3 v2/02-Drawings/30-Assembly-Instructions/clean_pictures.py RAW_DIR --out DIR      # writes elsewhere

RAW_DIR holds what step_pictures.py saved in Fusion: each step's picture (...-STEP-NN_IMG.png) and its twin with the
same camera and every body hidden (...-STEP-NN_GRID.png). Every pixel the two share, within TOL on each colour, is the
background, the grid, an axis or the origin mark, so it turns white; every pixel that differs is a part, so it stays as
Fusion drew it. Nothing in Fusion's settings changes. Needs Pillow and numpy.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
TOL = 24          # out of 255 on each colour: enough for the renderer's edge smoothing, far below a faded body's 50 or more
WHITE = 255


def clean(step_png, grid_png):
    """The step picture with every pixel it shares with the grid-alone twin turned white: (image, share of pixels kept)."""
    a = np.asarray(Image.open(step_png).convert("RGB"), dtype=np.int16)
    b = np.asarray(Image.open(grid_png).convert("RGB"), dtype=np.int16)
    if a.shape != b.shape:
        raise ValueError(f"{Path(step_png).name} and {Path(grid_png).name} differ in size: {a.shape} and {b.shape}")
    part = np.abs(a - b).max(axis=2) > TOL
    out = np.where(part[..., None], a, WHITE).astype(np.uint8)
    return Image.fromarray(out, "RGB"), float(part.mean())


def pairs(raw_dir):
    out = []
    for step in sorted(Path(raw_dir).glob("*-STEP-*_IMG.png")):
        grid = step.with_name(step.name[:-len("_IMG.png")] + "_GRID.png")
        if not grid.exists():
            raise FileNotFoundError(f"{grid.name} is missing: rerun step_pictures.py for this step")
        out.append((step, grid))
    if not out:
        raise FileNotFoundError(f"no step pictures in {raw_dir}")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("raw_dir")
    ap.add_argument("--out", default=str(HERE / "img"), help="where the clean pictures go (default: the guide's img/)")
    a = ap.parse_args(argv)
    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    for step, grid in pairs(a.raw_dir):
        img, kept = clean(step, grid)
        img.save(out_dir / step.name, optimize=True)
        print(f"{step.name}: {kept:.1%} of the pixels are parts; written to {out_dir / step.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
