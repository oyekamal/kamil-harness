#!/usr/bin/env python3
"""svg_to_lottie.py — Convert SVG frame(s) into a Lottie .json animation.

Battle-tested "flipbook" technique: each SVG frame becomes a vector shape
layer with in/out points, so the art stays fully vector (resizable and
recolorable forever). Handles the known pitfalls:

  * strips fixed width/height attributes (they clip/scale wrongly; the
    parser must size from the viewBox alone)
  * offsets layer indices per frame (k*100) and fixes parent references,
    so multi-layer SVGs merge without collisions
  * warns on <text> elements (Lottie has NO text-from-SVG support —
    replace text with shapes/glyphs before converting)

Usage:
  python svg_to_lottie.py out.json frame1.svg frame2.svg --ticks 3 --fps 30
  python svg_to_lottie.py out.json static.svg              # static asset

Requires:  pip install lottie cairosvg --break-system-packages
Validate:  python svg_to_lottie.py --check out.json   (renders mid-frame PNG)
"""
import argparse, os, re, sys, tempfile


def convert(svg_paths, out_path, ticks_per_frame=3, fps=30, name=None):
    from lottie.parsers.svg import parse_svg_file
    from lottie.exporters.core import export_lottie
    from lottie import objects

    master = objects.Animation()
    master.name = name or os.path.splitext(os.path.basename(out_path))[0]
    master.frame_rate = fps
    master.in_point = 0
    n = len(svg_paths)
    master.out_point = max(2, ticks_per_frame * n)

    size_set = False
    for k, path in enumerate(svg_paths):
        raw = open(path).read()
        if "<text" in raw:
            print(f"WARNING: {path} contains <text> — Lottie cannot render it. "
                  f"Replace text with paths/shapes.", file=sys.stderr)
        # PITFALL: fixed width/height attrs on the root svg clip or mis-scale
        # the parse. Remove them; keep only the viewBox.
        cleaned = re.sub(r'(<svg[^>]*?)\s+width="[^"]*"', r"\1", raw, count=1)
        cleaned = re.sub(r'(<svg[^>]*?)\s+height="[^"]*"', r"\1", cleaned, count=1)

        with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False) as f:
            f.write(cleaned)
            tmp = f.name
        anim = parse_svg_file(tmp)
        os.unlink(tmp)

        if not size_set:
            master.width, master.height = anim.width, anim.height
            size_set = True

        for layer in anim.layers:
            if layer.index is None:
                layer.index = 0
            layer.index += k * 100
            if getattr(layer, "parent_index", None) is not None:
                layer.parent_index += k * 100
            if n > 1:
                layer.in_point = k * ticks_per_frame
                layer.out_point = (k + 1) * ticks_per_frame
            else:
                layer.in_point = 0
                layer.out_point = master.out_point
            layer.name = f"{master.name}_f{k}" + (f"_{layer.name}" if layer.name else "")
            master.layers.append(layer)

    with open(out_path, "w") as f:
        export_lottie(master, f)
    kb = os.path.getsize(out_path) // 1024
    print(f"wrote {out_path} ({n} frame(s), {master.out_point} ticks @ {fps}fps, {kb}KB)")
    return out_path


def check(json_path):
    """Round-trip validation: render a frame FROM the exported Lottie file."""
    from lottie.parsers.tgs import parse_tgs
    from lottie.exporters.cairo import export_png  # signature: (anim, fp, frame=0, dpi=96)

    anim = parse_tgs(json_path)
    # land strictly inside a frame window (boundary ticks can render two layers)
    mid = max(0, int(anim.out_point // 2) - 1)
    out = json_path.replace(".json", f"_check_f{mid}.png")
    export_png(anim, out, frame=mid, dpi=150)
    print(f"rendered {out} from the Lottie file itself — VIEW this image and "
          f"verify nothing is missing, clipped, or mis-layered.")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("output", help="output .json path (or input, with --check)")
    ap.add_argument("frames", nargs="*", help="SVG frame files, in order")
    ap.add_argument("--ticks", type=int, default=3, help="ticks per frame (default 3)")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--check", action="store_true", help="validate an existing .json by rendering a frame from it")
    a = ap.parse_args()
    if a.check:
        check(a.output)
    else:
        if not a.frames:
            ap.error("provide at least one SVG frame")
        convert(a.frames, a.output, a.ticks, a.fps)
