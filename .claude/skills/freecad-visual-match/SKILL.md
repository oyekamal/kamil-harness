---
name: freecad-visual-match
description: Rebuild/refine a FreeCAD model until renders visually match reference images (turnaround shots, product photos). Use for "make the model look like this image", character/product shells, gauntlet-loop runs against visual references. Provides a deterministic multi-view render rig for the FreeCAD MCP, a blind A/B critic protocol, numeric silhouette comparison, and VibeCAD-derived geometry diffing.
---

# FreeCAD Visual Match

Iteratively drive a FreeCAD model toward reference images. Distilled from a real gauntlet-loop
built from rawwerks/VibeCAD's model-compare design.

## Architecture (the loop)

1. **One idempotent build script** — the whole model rebuilds from a parameter block each
   iteration (BSpline `revolve_profile` for organic shells). NEVER hand-mutate the document;
   iteration N+1 must not inherit N's mistakes. (VibeCAD: "the model is code".)
2. **Deterministic render rig** — see below. Same 4 views every round: front, side, back, 3/4.
3. **Self-review first** — look at your own renders next to the refs and fix what YOU can see
   before spending critics. Catches ~half the gaps for free.
4. **Blind A/B critics** — one subagent per view (Opus for the hard calls), given a composite
   with labels A/B randomized per round, told to ignore lighting/material/framing and name the
   SINGLE biggest geometric difference + verdict MATCH/CONTINUE. Never let the builder judge.
5. **Median the critics, don't chase one** — individual critics contradict each other on the
   SAME reference (head ratio estimates varied 45%→61% across rounds). When two rounds of
   critiques flip direction on the same dimension, you are at the judge-noise floor: stop
   iterating that dimension and close.

## Deterministic render rig (the hard-won part)

All the obvious FreeCAD camera APIs are broken for scripted multi-view rendering:
- `setViewDirection()` leaves camera ROLL arbitrary → tilted renders.
- `setCameraOrientation()` ANIMATES → the next `saveImage` catches mid-flight frames.
- `viewFront()` after a raw coin-node change also animates → stale snapshots.
- Naive `App.Matrix`→`App.Rotation` extraction garbles non-trivial orientations.

The working recipe: build the camera basis by hand and set the Coin node directly:

```python
# camera axes for view direction d (unit), world-up (0,0,1):
Z = -d;  X = normalize(cross(up, Z));  Y = cross(Z, X)
q = mat2quat(X, Y, Z)          # FULL branch quaternion (trace<=0 cases too — 180° views!)
view.getCameraNode().orientation.setValue(coin.SbRotation(*q))
Gui.SendMsgToActiveView("ViewFit"); Gui.updateGui()
view.saveImage(path, 1024, 1024, "White")
```

- Verify with `view.getViewDirection()` after setting — print the azimuth every time.
- Match the reference's framing margin (refs rarely fill the frame): after ViewFit, move the
  camera back ~15% about the model center, or critics misread proportions from zoom alone.
- Fixed orthographic scale (`cam.height.setValue(mm)`) when you need numeric comparability.
- `md5sum` the renders — identical hashes mean the camera silently didn't move (happened).

## Critic protocol

Composite: render and reference side by side, 768px each, labels "A"/"B" randomized per round
(keep the mapping to yourself). Prompt the critic to: pick which is the WIP, name the single
biggest geometric difference precisely/measurably, two lesser ones, verdict line. "Ignore
lighting, materials, gloss, render quality, background, screen graphics, framing/zoom."

## Numeric comparison (when refs segment cleanly)

`scripts/silhouette_compare.py` — per-band width profiles (% of height) of ref vs fixed-ortho
render, signed errors tell you which spline control point to move. CAVEAT: glossy white
product shots on light-grey studio backdrops DO NOT threshold cleanly (body tone ≈ background);
in that case trust direct pixel reads of key landmarks + critic medians instead.
`scripts/model_diff.py` (from VibeCAD, needs build123d/OCP) — volume IoU/precision/recall
between two solids with typed diagnosis ("over-generating", "undersized by X%") — use when a
gold STEP/STL exists, e.g. regression-checking a refactored build script against the last
approved STLs.

## Geometry recipes (Part workbench, scripted)

- Organic shells: `Part.BSplineCurve().interpolate(pts)` profile → revolve. Polygon profiles
  leave print-visible facet ribs.
- Non-round heads: revolve then `transformGeometry(Matrix.scale(1, depth_factor, 1))`.
- Curved visor/lens on a shell: lens = rounded-rect prism ∩ scaled-up copy − scaled-down copy
  (scale about the shell's center). Cut the SAME lens from the head → recess is coincident by
  construction. Check `lens.BoundBox` after — a too-shallow prism clips the lens silently.
- Fillet edge selection by predicate (tangent direction), never by index.

## Exit condition

Every view wins its blind A/B, or two consecutive rounds of critiques contradict each other on
the same dimension (judge-noise floor) — then close with an honest report of what converged
and what remains subjective. Never exit on a round count.
