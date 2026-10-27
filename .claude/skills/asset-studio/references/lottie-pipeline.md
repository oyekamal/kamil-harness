# Lottie Pipeline Reference

Everything needed to deliver Lottie assets, with every pitfall already hit once so it never has to be hit again.

## What Lottie is (say this to users when relevant)

A Lottie animation is a JSON file describing vector shapes, transforms, and keyframes, rendered live by players (lottie-web on web, `lottie` package in Flutter, dotLottie players, native iOS/Android). Because it is vectors-as-text: infinite resize with zero quality loss, recolor via text edit, tiny file sizes, and files open in the LottieFiles editor and After Effects. A `.lottie` (dotLottie) file is the same JSON zipped with assets.

## The flipbook technique (default conversion path)

Hand-keyframing Lottie JSON is fragile. The robust path: draw each animation frame as a complete SVG (parameterized variations of one generator function), then merge frames into one Lottie where each frame is a layer with in/out points. Stylized 2–3 frame loops look intentional, convert reliably, and stay editable. Use `scripts/svg_to_lottie.py` — do not re-derive the merge logic; it already handles the pitfalls below.

Suggested timing at 30fps: ride/roll cycles 3 ticks per frame, walk cycles 8, idle pulses 10–12, static assets a single frame with out_point 2. Ship distinct character states (run/jump/duck/hit) as separate .json files — engines swap files far more easily than they seek segments.

## Pitfalls (each of these cost real debugging time)

1. **Fixed `width=`/`height=` attributes on the root `<svg>` clip or mis-scale the parse.** python-lottie must size from the viewBox alone. The bundled script strips them; if converting by other means, strip them yourself. Symptom: only a sliver of the art renders, usually the top-left region.
2. **Lottie has no `<text>` support.** SVG text silently disappears or errors. Replace labels with drawn glyphs (an icon, a crescent, a chili) — usually an aesthetic upgrade anyway.
3. **python-lottie API signatures** (do not guess): `parse_svg_file(path)` → Animation; `export_lottie(animation, file_obj)`; validation renderer is `from lottie.exporters.cairo import export_png` with signature `export_png(animation, fp, frame=0, dpi=96)` — there is **no width/height kwarg**; re-import a .json with `from lottie.parsers.tgs import parse_tgs`.
4. **Merging multi-layer SVG frames**: offset every layer's `index` by `k*100` per frame and apply the same offset to `parent_index` when present, or layers collide and parenting breaks.
5. **Validate from the exported file, not the source SVG.** Render a mid-animation frame with `svg_to_lottie.py --check out.json` and VIEW the PNG. The mid frame catches per-frame layer bugs a frame-0 check misses.
6. Gradients, filters, masks, and CSS classes convert unreliably — stick to plain fills, strokes, groups, and transforms in source SVGs destined for Lottie.

## Recolor tables (include one in every Lottie delivery README)

Lottie stores colors as `[r, g, b]` float arrays (0–1). Convert each palette hex to floats and publish the table so users can recolor with find-and-replace, e.g. `#3A8C3F` → `[0.227, 0.549, 0.247]`. Formula: `round(int(hex[i:i+2], 16) / 255, 3)` per channel. Note in the README that files may store more decimal places — search a short prefix like `0.227` to locate occurrences.

Runtime recolor in Dart (also powers a great preview-page demo — walk the JSON, swap color arrays, reload):

```dart
final raw = await rootBundle.loadString('assets/lottie/character.json');
final skinned = raw.replaceAll('[0.227,0.549,0.247]', '[0.18,0.451,0.722]');
final comp = await LottieComposition.fromBytes(utf8.encode(skinned));
```

## Flutter Flame integration (copy-paste for game deliveries)

```yaml
dependencies:
  flame: ^1.18.0
  flame_lottie: ^0.4.0   # Lottie inside Flame
  lottie: ^3.1.0         # Lottie in UI screens
```

```dart
import 'package:flame_lottie/flame_lottie.dart';

final asset = await loadLottie(Lottie.asset('assets/lottie/enemy_walk.json'));
final enemy = LottieComponent(asset, size: Vector2.all(100), repeating: true)
  ..position = spawnPos
  ..add(RectangleHitbox(size: Vector2(34, 66), position: Vector2(36, 24)));
```

Multi-state characters: preload one `LottieComponent` per state file and swap children on state change (remove active, add next). Backgrounds: two components per layer leapfrogging for infinite scroll.

**Honest performance note to include in READMEs**: Lottie re-renders vectors per frame, costlier than sprite blitting. Fine for one player plus a handful of entities on mid-range phones; if profiling shows a hot spot, rasterize just that asset to a sprite sheet (raster-pipeline.md) while keeping Lottie as the editable source of truth.

## Preview page pattern

Deliver an HTML preview loading lottie-web from `https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.12.2/lottie.min.js`, with every animation playing in a card grid (`lottie.loadAnimation({container, renderer:'svg', loop:true, autoplay:true, animationData})`). Embed the JSONs directly into the page (they are small). Add a global CSS scale slider (proves lossless resize) and, when a hero asset exists, live recolor buttons using the JSON color-walk technique — these two demos consistently land the "why Lottie" argument.
