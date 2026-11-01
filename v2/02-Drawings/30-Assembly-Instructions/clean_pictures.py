"""The guide's step pictures on white, from step_pictures.py's transparent captures.

    python3 v2/02-Drawings/30-Assembly-Instructions/clean_pictures.py RAW_DIR                # writes img/
    python3 v2/02-Drawings/30-Assembly-Instructions/clean_pictures.py RAW_DIR --out DIR      # writes elsewhere

RAW_DIR holds what step_pictures.py saved in Fusion: each step's picture (...-STEP-NN_IMG.png) with a transparent
background, so Fusion's layout grid, the axes and the origin mark aren't in it (probe, 2026-11-01). Each one is laid on
white: a solid part stays as Fusion drew it, a faded part keeps its light tone, the background turns white. A picture
without a transparent background is refused, since its grid would come through. Needs Pillow.
"""
import argparse
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent


def on_white(step_png):
    """The transparent step picture laid on white: (image, share of its pixels that hold a part)."""
    im = Image.open(step_png)
    if im.mode != "RGBA" or im.getchannel("A").getextrema()[0] != 0:
        raise ValueError(f"{Path(step_png).name} has no transparent background: run step_pictures.py again")
    hist = im.getchannel("A").histogram()
    white = Image.new("RGBA", im.size, (255, 255, 255, 255))
    white.alpha_composite(im)
    return white.convert("RGB"), 1 - hist[0] / (im.size[0] * im.size[1])


def pictures(raw_dir):
    out = sorted(Path(raw_dir).glob("*-STEP-*_IMG.png"))
    if not out:
        raise FileNotFoundError(f"no step pictures in {raw_dir}")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("raw_dir")
    ap.add_argument("--out", default=str(HERE / "img"), help="where the pictures on white go (default: the guide's img/)")
    a = ap.parse_args(argv)
    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    for step in pictures(a.raw_dir):
        img, kept = on_white(step)
        img.save(out_dir / step.name, optimize=True)
        print(f"{step.name}: {kept:.1%} of the pixels hold a part; written to {out_dir / step.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
