"""One-time photo prep for the ASCII portrait (run locally, not in CI).

    pip install pillow numpy opencv-python rembg
    python scripts/prep_photo.py path/to/photo.jpg

Removes the background, boosts local contrast (CLAHE) and keeps the cut-out
mask as alpha -> source-prepped.png, which make_ascii_svg.py picks up automatically.
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "source-prepped.png")


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: python scripts/prep_photo.py <photo>")
    im = Image.open(sys.argv[1]).convert("RGB")
    im.thumbnail((1200, 1200))

    cut = remove(im)  # RGBA with transparent background
    white = Image.new("RGBA", cut.size, (255, 255, 255, 255))
    white.alpha_composite(cut)
    gray = np.array(white.convert("L"))

    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # crop to the subject's bounding box with a little margin
    alpha = np.array(cut.split()[-1])
    out = Image.merge("LA", [Image.fromarray(gray), Image.fromarray(alpha)])
    ys, xs = np.where(alpha > 20)
    if len(xs):
        m = 20
        out = out.crop((max(xs.min() - m, 0), max(ys.min() - m, 0), xs.max() + m, ys.max() + m))

    out.save(OUT)  # gray + alpha
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
