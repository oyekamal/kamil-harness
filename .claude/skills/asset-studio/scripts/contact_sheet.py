#!/usr/bin/env python3
"""contact_sheet.py — Build a labeled review grid from a folder of PNGs.

Use after generating any asset pack: view the sheet and critique every
asset like an art director before delivering.

Usage:
  python contact_sheet.py assets_dir out.png [--cols 4] [--cell 520]

Requires: pip install pillow --break-system-packages
"""
import argparse, math, os
from PIL import Image, ImageDraw, ImageFont


def build(src_dir, out_path, cols=4, cell=520):
    files = sorted(f for f in os.listdir(src_dir) if f.lower().endswith(".png"))
    if not files:
        raise SystemExit(f"no PNGs in {src_dir}")
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    except OSError:
        font = ImageFont.load_default()

    ch = cell - 190  # image area height inside a cell
    rows = math.ceil(len(files) / cols)
    grid = Image.new("RGBA", (cols * cell, rows * (ch + 70)), (240, 237, 232, 255))
    d = ImageDraw.Draw(grid)
    for i, f in enumerate(files):
        orig = Image.open(os.path.join(src_dir, f))
        im = orig.convert("RGBA")
        im.thumbnail((cell - 40, ch))
        x, y = (i % cols) * cell, (i // cols) * (ch + 70)
        d.text((x + 16, y + 8), f"{f}  ({orig.width}x{orig.height})",
               fill=(23, 33, 43, 255), font=font)
        grid.paste(im, (x + 16, y + 42), im)
    grid.save(out_path)
    print(f"wrote {out_path} ({len(files)} assets) — VIEW it and critique before delivering.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src_dir")
    ap.add_argument("output")
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--cell", type=int, default=520)
    a = ap.parse_args()
    build(a.src_dir, a.output, a.cols, a.cell)
