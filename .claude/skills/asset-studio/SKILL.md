---
name: asset-studio
description: Generate professional-quality visual assets entirely as code — game sprites and sprite sheets, characters with animation cycles, Lottie animations, icons, UI graphics, illustrations, logos, seamless backgrounds, and HUD elements. Use this skill whenever the user wants any kind of visual or art asset created, edited, animated, resized, recolored, or exported for a game engine (Flutter Flame, Unity, Godot, Phaser), a mobile/web app, or a website — even if they just say "draw me X", "make assets for my game", "I need an icon/character/animation", or ask to convert art between formats (SVG, PNG, Lottie, sprite sheet). Also use it when the user complains that existing assets are hard to resize or recolor.
---

# Asset Studio

Produce visual assets the way a small studio would: a consistent art direction, vector sources that stay editable forever, verified output, and a package the client can actually use. The method below was battle-tested building a full game asset pack (player character with animation states, five obstacle types, collectibles, HUD, four background zones) delivered as both sprite sheets and Lottie.

## The core method: art as code

Never hand-wave art or produce one-off files. Write **parameterized generator functions** (Python producing SVG strings) with **named palette constants** at the top. This single decision gives the user everything they will later ask for: recolor any asset by changing one line, resize with no quality loss, add animation frames by calling the function with different parameters, and regenerate the whole pack in seconds. Always ship the generator scripts with the assets.

```python
INK  = "#17212B"   # outlines
BODY = "#3A8C3F"   # named for meaning, not appearance
def character(pose="idle", frame=0): -> returns an SVG string
```

## Workflow (follow in order)

### 1. Pin the art direction before drawing anything
Decide and state: subject, target platform, canvas size (design in a small viewBox like 160×160 and render at 2× or higher), a 4–6 color palette as named constants, outline weight, and one signature detail grounded in the subject's world (a cultural reference, a texture, a motif). Consistency across a pack comes from reusing these tokens, never from luck. If the user has a spec or brand colors, use them exactly.

### 2. Choose the output format by target, not preference

| Target | Primary format | Notes |
|---|---|---|
| Flutter / Flame game | Lottie via `flame_lottie` | Vector, runtime recolor/resize; rasterize only if profiling demands |
| Unity, Godot, Phaser, pixel-perf | PNG sprite sheets | Horizontal strip, one row, equal frames |
| Web page / app UI | Inline SVG or Lottie | SVG for static, Lottie for animation |
| App animations (loaders, success states, mascots) | Lottie | Also usable in After Effects / LottieFiles editor |
| Icons / logos | SVG source + PNG exports at needed sizes | |

When the user is unsure, deliver Lottie or SVG as the source of truth — raster can always be derived later, never the reverse.

### 3. Build frames as parameterized variations
Animation frames are the same function with different parameters: wheel rotation angle, bob offset, limb positions, glow radius, steam phase. Two to three frames is enough for stylized loops (walk cycles, spins, pulses). Distinct states (jump, duck, hit) are separate poses from the same parts. Keep character parts as separate sub-functions (head, torso, limbs, vehicle) so poses recombine them.

### 4. Render, LOOK, critique, fix — this step is mandatory
After every render, **view the output image and critique it like an art director** before moving on: Does each shape read as what it is? Are silhouettes distinct at small size? Any element that looks like a blob, floats disconnected, or has broken layering? Fix and re-render until it reads cleanly. Most quality failures come from skipping this look. Generate a labeled **contact sheet** of the whole pack (use `scripts/contact_sheet.py`) and view it whenever more than two assets exist.

### 5. Export and validate FROM the exported format
Convert to the target format, then render a frame back **from the exported file itself** (not from the source SVG) and view it. Format converters silently drop or distort features; only round-trip rendering catches it. For the SVG→Lottie pipeline use `scripts/svg_to_lottie.py`, which has the known pitfalls already fixed. Read `references/lottie-pipeline.md` before any Lottie work and `references/raster-pipeline.md` before sprite-sheet work — both contain hard-won gotchas that are not guessable.

### 6. Package like a studio, not a file dump
A finished delivery always contains: the asset files; an **interactive preview HTML** showing everything animating (with lottie-web from cdnjs for Lottie packs; include live resize/recolor demos when relevant — they delight users); an **integration README** with copy-paste code for the user's exact engine, recommended sizes, animation timings, and hitboxes; the **generator scripts**; and a **zip bundle**. Present the preview and README, not just the zip.

## Non-negotiable quality rules

- Limited palette, consistent outline weight everywhere, flat fills over gradients unless the direction demands otherwise.
- Every animated element's motion must mean something: squash on impact, bob while riding, mist trailing a rolling canister.
- Backgrounds intended to scroll must tile seamlessly: identical edge geometry (same y-values where bands meet the edges) on every tile, and a margin near both edges free of elements. If several zone tiles will be cut between, share the same sky/horizon/ground bands across all of them.
- Ground assets in the subject's real world — local landmarks, food, objects, vernacular — rather than generic clip-art choices.
- Raster exports at 2× minimum for high-DPI screens. Vector canvases small and clean (multiples of 8).
- For game obstacles, document hitboxes smaller than the visible sprite (~70–80%) so near-misses feel fair, and exclude decorative effects (mist, glow) from them.

## Environment notes

`pip install` needs `--break-system-packages` in this environment. Dependencies: `cairosvg` and `pillow` (rendering), `lottie` (the python-lottie package, SVG→Lottie). All are on pypi and install cleanly.

## References

- `references/lottie-pipeline.md` — SVG→Lottie conversion recipes, the flipbook technique, every known gotcha, recolor-by-JSON tables, Flutter/Flame integration code. Read before any Lottie task.
- `references/raster-pipeline.md` — sprite sheet construction, contact sheets, engine integration snippets (Flame, Unity, Godot), preview HTML patterns. Read before sprite-sheet or PNG deliveries.
- `references/design-guide.md` — style-token systems, character construction, seamless tiles, UI asset specifics, the critique checklist expanded. Read when starting a new pack or when output quality disappoints.
