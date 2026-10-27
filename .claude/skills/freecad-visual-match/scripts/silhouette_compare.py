#!/usr/bin/env python3
# Numeric silhouette comparison: reference turnaround vs fixed-ortho FreeCAD renders.
# Prints per-band signed width errors (in % of total height) so the builder knows
# exactly which spline control points to move. VibeCAD-style typed diagnosis.
import numpy as np
from PIL import Image
import sys, os

# Paths: env vars REF_DIR (reference images) and RENDER_DIR (FreeCAD renders), default ./reference-images/ and ./renders/
REF = os.environ.get("REF_DIR", "./reference-images/").rstrip("/") + "/"
S = os.environ.get("RENDER_DIR", "./renders/").rstrip("/") + "/"

def runs_of(row, gap=10):
    xs = np.where(row)[0]
    if len(xs) == 0: return []
    runs = []; s = p = xs[0]
    for x in xs[1:]:
        if x > p + gap: runs.append((s, p)); s = x
        p = x
    runs.append((s, p))
    return runs

def center_run_width(row, cx, gap=10):
    best = None
    for a, b in runs_of(row, gap):
        if b - a < 8: continue
        d = 0 if a <= cx <= b else min(abs(a - cx), abs(b - cx))
        if best is None or d < best[0]: best = (d, a, b)
    return (best[1], best[2]) if best else None

def ref_mask_profile(path, nb=40):
    rgb = np.array(Image.open(path).convert("RGB")).astype(int)
    g = rgb.mean(axis=2); H, W = g.shape
    bg = np.median(g[0:40, :])
    navy = (rgb[:, :, 2] > rgb[:, :, 0] + 12) & (g < 150)
    obj = (g > bg + 6) | navy | (g < bg - 25)   # bright body, navy, deep shading (not soft shadow)
    ys = np.where(navy.any(axis=1))[0]
    y_foot = ys.max() if len(ys) else H - 1     # ground = bottom of navy foot
    cx = W // 2
    tops = np.where(obj[:, cx - 200:cx + 200].any(axis=1))[0]
    y_top = tops.min()
    Ht = y_foot - y_top
    prof = []
    for i in range(nb):
        y = int(y_top + (i + 0.5) / nb * Ht)
        r = center_run_width(obj[y], cx)
        prof.append((r[1] - r[0]) / Ht if r else 0.0)
    return prof, Ht

def render_mask_profile(path, nb=40):
    g = np.array(Image.open(path).convert("L")).astype(int)
    obj = g < 248
    ys = np.where(obj.any(axis=1))[0]
    y_top, y_bot = ys.min(), ys.max()
    Ht = y_bot - y_top
    cx = obj.shape[1] // 2
    prof = []
    for i in range(nb):
        y = int(y_top + (i + 0.5) / nb * Ht)
        r = center_run_width(obj[y], cx)
        prof.append((r[1] - r[0]) / Ht if r else 0.0)
    return prof, Ht

def compare(view, reff, rendf):
    rp, _ = ref_mask_profile(REF + reff)
    mp, _ = render_mask_profile(S + rendf)
    print(f"\n== {view}  (z% from top | ref width | model width | signed err, all %H)")
    tot = 0
    for i, (a, b) in enumerate(zip(rp, mp)):
        z = (i + 0.5) / len(rp) * 100
        err = (b - a) * 100
        tot += abs(err)
        flag = "" if abs(err) < 2 else ("  << model too WIDE" if err > 0 else "  << model too NARROW")
        if i % 2 == 0:
            print(f"  {z:4.0f}%  {a*100:5.1f}  {b*100:5.1f}  {err:+5.1f}{flag}")
    print(f"  mean |err| = {tot/len(rp):.2f} %H")

if __name__ == "__main__":
    compare("FRONT", "turnaround-front.jpeg", "ortho-front.png")
    compare("SIDE", "turnaround-side.jpeg", "ortho-side.png")
    compare("BACK", "turnaround-back.jpeg", "ortho-back.png")
