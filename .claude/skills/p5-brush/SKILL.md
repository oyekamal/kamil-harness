---
name: p5-brush
description: Draw with p5.brush (acamposuribe/p5.brush v2.2.3, MIT), natural-media brushes for p5.js 2.x or with no p5 at all. Covers pencils (2B/HB/2H), pen, rotring, charcoal, crayon, pastel, spray and marker strokes, watercolor fill with bleed and texture, wash, hatching and dry-media "mass" fills, flow fields that bend strokes, custom and image brush tips, splines, seeding and scaleBrushes. Covers both builds (p5 WEBGL addon and the standalone WebGL2 build that needs brush.render()), CDN and npm load order, instance mode, offscreen targets, the slow-render facts, the pitfalls agents hit, a guide to recreating the upstream teaser sketches, and hand-drawn marker or chalk diagrams on a whiteboard. Triggers on "p5.brush", "p5 brush", "brush.set", "brush.flowLine", "watercolor fill in p5", "hand-drawn look", "pencil/charcoal/marker strokes", "hatching in p5", "generative art brushes", "make the whiteboard look drawn", "chalk/marker diagram", "sketchy diagram". For core p5 (shapes, loop, input, p5 2.x API changes) use the sibling skill `p5js`.
---

# p5.brush: natural-media drawing for p5.js

Source: github.com/acamposuribe/p5.brush (npm `p5.brush` **2.2.3**, released 2026-09-20, `latest` tag). The author is Alejandro Campos Uribe, MIT licensed; the license text is in `references/LICENSE-p5brush-MIT`. Every fact here was checked against `src/` (commit 0e85177) and by rendering in Chromium. Every template has been rendered and checked:

| File | Use |
|---|---|
| `templates/p5-global.html` | p5 build from the CDN: rect, watercolor circle, hatch, spline, mass |
| `templates/standalone.html` | standalone ESM from the CDN, the full frame lifecycle |
| `templates/whiteboard.html` | marker-on-white and chalk-on-board diagrams with HTML labels (whiteboard look) |
| `templates/brushBoard.js` + `BrushCard.example.jsx` | React/Vite module: one shared surface, cached PNG per card, StrictMode-safe |
| `scripts/shot.mjs` | headless screenshot: `--wait-done` for static pages, `--frames a,b,c` pauses a p5 sketch on given frames |
| `references/api.md` | every export, built-in brush parameters, `add()` keys, return values, error messages, issue history |
| `references/teaser-scenes.md` | upstream example/ and example2/ rebuilt scene by scene, with exact values |

## 1. Pick the build first. Mixing the two is the main source of broken code.

| | **p5 build** `dist/p5.brush.js` | **Standalone** `dist/brush.js` / `brush.esm.js` |
|---|---|---|
| Needs | **p5.js 2.x** (peer `^2.2`; tested 2.2.0 and 2.3.4; the upstream examples pin 2.1.1) | Nothing. Any WebGL2 browser |
| Canvas | `createCanvas(w, h, WEBGL)`, nothing else needed | `brush.createCanvas(w, h, {parent, id, pixelDensity})` or `brush.load(myCanvas)` |
| Transforms | p5 `push/pop/translate/rotate/scale` (hooked) | `brush.push/pop/translate/rotate/scale` |
| Angles | p5 `angleMode(DEGREES)` | `brush.angleMode(brush.DEGREES)` |
| Seed | `randomSeed(n)` / `noiseSeed(n)` also seed brush | `brush.seed(n)` / `brush.noiseSeed(n)` |
| Flush | Automatic at the end of `setup()` and every `draw()` | **`brush.render()` after drawing**, or nothing shows (it warns once in the console) |
| Clear | `background(c)` | `brush.clear(c?)` (no argument clears to transparent) |
| Text | p5 `text()` after the brush calls (WEBGL needs `await loadFont`) | No text. Put HTML labels on top |

- **Load order (p5 build):** p5 first, then p5.brush, then your sketch. The addon registers itself with `p5.registerAddon` when it loads.
  ```html
  <script src="https://cdn.jsdelivr.net/npm/p5@2.3.4/lib/p5.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/p5.brush@2.2.3/dist/p5.brush.js"></script>
  <script src="sketch.js"></script>
  ```
  `https://cdn.jsdelivr.net/npm/p5.brush@latest` serves the same p5 build. Pin the version.
- **Standalone by CDN:** `<script src="https://cdn.jsdelivr.net/npm/p5.brush@2.2.3/dist/brush.js">` (UMD, global `brush`) or `import * as brush from "https://cdn.jsdelivr.net/npm/p5.brush@2.2.3/dist/brush.esm.js"`.
- **npm:** `npm i p5.brush`, then `import * as brush from 'p5.brush'` (the p5 build, which also needs `p5`) or `import * as brush from 'p5.brush/standalone'`. This works under Vite 8 and React 19 (checked).
- **WEBGL is required.** A 2D p5 canvas throws `p5.brush could not resolve an active WEBGL sketch...`. With p5 1.x you get `p5.registerAddon is not a function` and then `brush.X is not a function`. p5.brush v2 does not work with p5 1.x.

## 2. Minimal working sketches (both verified)

```js
// p5 build: global mode
function setup() {
  createCanvas(600, 600, WEBGL);
  angleMode(DEGREES);        // brush angles follow p5. The default is RADIANS
  brush.scaleBrushes(3);     // 3 suits 600x600; scale with the canvas size
  randomSeed(7); noiseSeed(7);
  noLoop();                  // static art: draw once
}
function draw() {
  background("#fffceb");
  translate(-width / 2, -height / 2);          // WEBGL origin is the CENTRE, so shift to top-left
  brush.set("2B", "#0e2d58", 1.5); brush.rect(60, 60, 200, 140);
  brush.fill("#fcd300", 90); brush.fillBleed(0.3); brush.fillTexture(0.4, 0.4);
  brush.circle(420, 140, 90, 0.3); brush.noFill();
  brush.hatchStyle("rotring", "#ff2702", 1); brush.hatch(10, 30);
  brush.polygon([[80, 320], [260, 300], [220, 520], [60, 480]]); brush.noHatch();
  brush.set("charcoal", "#2c695a", 1);
  brush.spline([[320, 320, 1], [420, 380, 1.5], [380, 480, 0.8], [560, 560, 1]], 1);
}
```
```js
// Instance mode: call brush.instance(p) before setup/draw. After that, brush.* has no p. prefix
new p5((p) => {
  brush.instance(p);
  p.setup = () => { p.createCanvas(500, 300, p.WEBGL); p.angleMode(p.DEGREES); brush.scaleBrushes(2.5); };
  p.draw  = () => { p.background(245); p.translate(-p.width / 2, -p.height / 2); brush.set("HB", "#333", 1); brush.line(40, 40, 460, 260); };
}, document.getElementById("holder"));
```
Standalone: copy `templates/standalone.html`. It goes `createCanvas → scaleBrushes → angleMode → seed → clear → push → translate(-W/2,-H/2) → draw → pop → render()`.

## 3. The drawing model: set state, then draw

**Stroke.** `brush.set(name, color, weight=1)` sets the brush, its colour and a weight multiplier, and turns stroke on. `brush.pick(name)` changes only the brush, `brush.stroke(c)` only the colour, `brush.strokeWeight(w)` only the weight. `brush.noStroke()` turns stroke off. Colours can be hex, CSS names, `r,g,b`, or a p5.Color (p5 build only).

**Built-in brushes.** There are exactly 11, read from `src/stroke/stroke.js`: `pen`, `rotring`, `2B`, `HB`, `2H`, `cpencil`, `pastel`, `crayon`, `charcoal`, `spray`, `marker`. The README also lists `marker2` and `hatch_brush`, but those names are out of date and **do not exist**: `pick`/`set` throws `Brush "x" not found. Available brushes: ...`. Call `brush.box()` to list the names at runtime. How they look at `scaleBrushes(2.5)`: `pen` and `rotring` are crisp ink. `HB` and `2H` are thin grainy graphite, `2B` is darker and grainier, and `cpencil` is a light coloured pencil. `charcoal` and `crayon` are thick and grainy. `pastel` is a very soft wide haze. `spray` is a scattered dot cloud. `marker` is a soft translucent felt or highlighter band whose ends build up. Raise `weight` to get thicker lines. Strokes are always semi-transparent and build up where they overlap.

**Primitives.** `line(x1,y1,x2,y2)`, `flowLine(x,y,len,dir)` and `spline(pts,curv)` draw stroke only. So does `arc(x,y,r,start,end)`. `beginStroke("curve"|"segments",x,y)`, then `move(angle,len,pressure)` as often as needed, then `endStroke(angle,pressure)` draws a stroke by hand. `rect(x,y,w,h,"corner"|"center")`, `circle(x,y,radius,irregularity0..1)` (the third argument is the **radius**, not the diameter), `polygon([[x,y],...])` and `beginShape(curv)`/`vertex(x,y,pressure?)`/`endShape(close)` take stroke, fill, hatch and mass. A spline or vertex point can carry a third value, the pressure (about 0.5–2), which changes the width along the stroke. A curvature of 0 gives straight segments and 1 gives the roundest curve. `polygon()` **ignores flow fields**. Rect, circle, shapes, lines and flowLine all follow the active field. **No `ellipse`, `point` or `text` exist** (#46).

**Fill (watercolor).** `brush.fill(color, opacity0..255)`. Low values such as 60–110 layer well. `brush.fillBleed(0..1, "out"|"in", angle?)` sets how far the edge spreads. `brush.fillTexture(texture0..1, border0..1, scatter=true)` adds paper grain and a darker rim, and `false` as the third argument draws a cleaner edge. `brush.noFill()` turns fill off. `brush.wash(color, opacity)` is a fast flat fill with no bleed (`noWash()` to stop). If the outline should not show, call `brush.noStroke()` before the shape. Watercolor at opacity 60–110 is light and mixes like paint (spectral.js), so a navy `#002185` fill comes out light aqua rather than dark navy. To get a darker colour, layer several fills or raise the opacity.

**Hatch.** `brush.hatchStyle(name, color, weight)` sets the hatch brush. If you skip it, hatching uses the current stroke. `brush.hatch(dist, angle, {rand, continuous, gradient})` turns hatching on for every following closed shape, and `brush.noHatch()` turns it off. **Always call noHatch()**, or every shape after it is hatched too. `brush.hatchArray(polygons)` hatches several `brush.Polygon`s in one pass, so the lines run straight across all of them.

**Mass (dry media).** `brush.mass(brushName, color, {precision, strength, gradient, outline})` fills shapes with layered hand-drawn strokes. `crayon` and `pastel` suit it best. `brush.massArray([outer, ...holes])` works even-odd, so later polygons cut holes. Turn it off with `brush.noMass()`.

**Flow fields.** `brush.field(name)` with one of `hand`, `curved`, `zigzag`, `waves`, `seabed`, `spiral`, `columns`, or `brush.listFields()`. `brush.wiggle(n)` is shorthand for the `hand` field (n of about 1–3 adds a slight hand wobble). `brush.noField()` turns it off. `brush.refreshField(t)` animates the field. `brush.addField(name, (t, field) => { field[col][row] = deg; return field }, {angleMode})` defines your own field.

**Custom brushes.** `brush.add(name, {type: "default"|"spray"|"marker"|"custom"|"image", weight, scatter, sharpness, grain, opacity, spacing, pressure, tip, image, rotate: "none"|"natural"|"random", markerTip, noise})`. A `custom` tip is `(_m) => {...}`, drawn on a 100×100 space centred on the origin, where dark means opaque. In the standalone build `_m.rotate` takes radians and colours must be numbers or CSS strings. An `image` brush returns a Promise, so use `await brush.add(...)` inside `async setup()`. All parameters are in `references/api.md`, and https://acamposuribe.github.io/p5.brush/tools/brush-maker.html designs brushes visually. `brush.clip([x1,y1,x2,y2])` and `noClip()` clip strokes and hatches, but not fills.

**Reusing geometry.** `polygon()` returns a `brush.Polygon` with `.hatch()`, `.mass()`, `.fill()` and `.draw()`. `spline()`, `arc()` and `endShape()` return a `brush.Plot`, and `plot.genPol(plot.origin[0], plot.origin[1], 1, 0.3)` turns one into a Polygon for `hatchArray`/`massArray`. `circle()` returns `[plot, x, y]`. To restyle a shape, call the same primitive again with new state.

## 4. Scale, seed, determinism

- `brush.scaleBrushes(k)` **multiplies** weight, scatter and spacing of every brush registered so far. It **adds up across calls**, so calling it twice (React StrictMode, HMR, re-init) gives k² and blobby strokes. Call it once and guard it with a flag. Brushes you `add()` later are not scaled. A rough guide: k ≈ canvas width / 200 (3 for 600, 2.5 for 500, 3.5 in the first teaser).
- Every brush mark is random. To redraw the same image each frame, re-seed right before each element (`randomSeed(base * seeds[i])` in p5, `brush.seed(n)` standalone). The teasers do this. `push()`/`pop()` saves and restores stroke, fill, hatch, mass **and field** state, as well as the transform.

## 5. Performance and lifecycle (read before animating)

- The library aims for print-quality texture, not real-time speed (upstream issue #11). A fill, a mass, or 20 long flowLines with big brushes can take hundreds of milliseconds or more per frame. In headless software GL, one teaser scene took about 1–5 s per frame. Draw static work once (`noLoop()`), or **add a few strokes per frame onto a background you never clear**. That is how the "brush rain" and watercolor scenes in the teasers work.
- Group fills by colour and opacity so the internal cache gets reused. Keep the canvas size fixed: `resizeCanvas` is not supported (#40), so scale with CSS instead.
- In the p5 build, compositing is flushed in the `postsetup`/`postdraw` hooks. Marks drawn from `mousePressed` and similar handlers show up on the next `draw()`. If you used `noLoop()`, call `redraw()`. The old v1 `brush.reDraw()`/`reBlend()` no longer exist.
- In the standalone build, call `render()` once per pass, at the end. `toDataURL()` straight after `render()` works (verified), so you can rasterise once and cache.
- The library keeps one global target. `brush.load(otherCanvas)` switches it. Switching between **two live WebGL canvases** works but logs `bindFramebuffer: object does not belong to this context`. It is better to keep **one shared surface**, resize it for each drawing, and export images (see §7).

## 6. Pitfalls checklist

1. If you forgot the `WEBGL` argument, or are on p5 1.x, see the errors in §1.
2. Coordinates are relative to the centre until you `translate(-w/2, -h/2)`. Without the translate, the art sits in the bottom-right quarter.
3. Angles are **radians** unless you set `angleMode(DEGREES)`. This applies to `hatch`, `flowLine`, `arc`, `rotate`, `move` and the `fillBleed` angle.
4. `rect` modes are the strings `"corner"` and `"center"`, not p5 constants. Fill opacity runs 0–255, not 0–1.
5. `fill`, `hatch`, `mass` and fields stay on until you turn them off with `noFill`, `noHatch`, `noMass` or `noField`, which is a common reason the next shape looks wrong.
6. Draw p5 `text()` and other overlays **after** the brush geometry, or the composite covers them. In WEBGL, text needs `font = await loadFont(url)` inside `async setup()` and then `textFont(font)`.
7. Image brushes need `await`. Custom tips draw dark on white, where white means transparent.
8. Names that do not exist are `marker2`, `hatch_brush`, `brush.ellipse`, `brush.point`, `brush.reDraw`, and `brush.push`/`translate` in the p5 build. In the standalone build, p5's `push` and `background` do not apply.
9. `line()` and `flowLine()` **throw** `No brush or color set...` after `noStroke()` (src, not what the README says). Call `set()` again before the next line.
10. Multiple p5 instances work in 2.x (#39 fixed), but each sketch must call `brush.instance(p)`.

## 7. Hand-drawn whiteboard diagrams in a React/Vite app

Use p5.brush to make diagrams (boxes, arrows, circles, underlines, hatched regions) look drawn with a **whiteboard marker** or **chalk** instead of rendered with vectors. The approach below was verified in a Vite + React 19 StrictMode test (`templates/brushBoard.js`).

- Use the **standalone** build (`npm i p5.brush`, `import * as brush from 'p5.brush/standalone'`, which Vite bundles, so it needs no network). If the app has no p5, do not add it.
- Inside a sandboxed **interactive** (iframe with `default-src 'none'`, no network), no CDN load works. Paste `dist/brush.js` (UMD, about 77 kB, global `brush`) into an inline `<script>`, the same way the `p5js` skill's `scripts/inline-p5.cjs` inlines p5. This was verified: an inline UMD build in `sandbox="allow-scripts"` with that CSP drew a marker rect and a watercolor circle with no errors. Avoid `image` tips there, because the CSP blocks image loads. Use `custom` tips.
- Keep **one module** (`brushBoard.js`) that owns the library. It runs `scaleBrushes` and `add` once behind a `ready` flag, and keeps **one shared offscreen canvas**. It sizes that canvas to `w*dpr × h*dpr`, then runs `load → seed(fixed) → clear(bg) → push → translate(-W/2,-H/2) → scale(dpr) → draw → pop → render`. It returns `toDataURL()` and caches the result by card id. Cards then render a plain `<img>` (one image, not one WebGL context per card), so panning and zooming cost nothing. A fixed seed per card means the same card looks the same on every re-render.
- **Labels are HTML, not brush strokes.** Absolutely position text (KaTeX, Inter, or a hand font) over the image, because brush has no text. Excalidraw can keep its own text elements.
- Recipes that look right (verified, `templates/whiteboard.html`):
  - **Marker on white:** a custom brush, `brush.add("whiteboard", {type:"marker", weight:3, scatter:0.12, opacity:8, spacing:0.025, pressure:[1.05,0.95], markerTip:false, noise:0.15})`. Use it at weight 0.9–1.4 with `brush.wiggle(1)` for a slight wobble. Colours: ink `#1f2937`, blue `#1d4ed8`, red `#dc2626`, green `#15803d`. The built-in `marker` is too pale for ink at small weights, but it makes a good **highlighter**: `set("marker", "#facc15", 2)` with one `line` under the answer.
  - **Chalk on a board** (`#2b3a33`): use `charcoal` in `#f1f5f9` at 1–1.2, with a pale yellow `charcoal` hatch (`#fde68a`, `hatch(12, π/4, {rand:0.15})`) to shade regions.
  - **Arrow:** draw `line` for the shaft and two short `line`s for the head at ±0.5 rad, about 16–18 px long (see the `arrow()` helper).
  - **Soft region:** `fill(color, 60–90)`, `fillBleed(0.2)`, `fillTexture(0.3, 0.3)`, `noStroke()`.
- Keep it static. Draw when the card mounts or its content changes, never in a frame loop. If you want the diagram to appear stroke by stroke, show the cached image under a CSS clip or mask animation rather than re-rendering.
- Whiteboard background: say the canvas is `#f5f6f8`. Clear the brush surface to the card's own background colour (`#ffffff` for cards), or to transparent (`brush.clear()`) when the image sits directly on the board.

## 8. Recreating the upstream teasers (example/ and example2/)

Both are 600×600 WEBGL canvases with `angleMode(DEGREES)` and `frameRate(30)`, a paper background of `#fffceb`, and labels in Inter (loaded with `await loadFont` from gstatic) that start with `*`. Both register a custom `"watercolor"` brush: `{type:"custom", weight:10, scatter:1.05, opacity:9, spacing:0.3, pressure:[0.8,1.3], rotate:"natural", tip: _m => { _m.fill(0,200); _m.rect(-20,-20,50,50); _m.rect(25,25,20,20) }}`. `example/` uses `scaleBrushes(3.5)` and 6 scenes of 5 s each. `example2/` uses `scaleBrushes(3)` and 7 scenes of 6 s each, and adds mass, massArray and hatchArray scenes. The full per-scene recipe (colours, counts, brush lists, coordinates) is in `references/teaser-scenes.md`. Here is what each scene does:
- **Brush rain:** the paper is never cleared. Each frame, with the `seabed` field on, it adds one `flowLine` at a random position, 140–240 long, in a random direction. The brush is picked at random from marker, watercolor, spray, charcoal, HB, 2B, cpencil, 2H and rotring, at weight 0.7–1.6. Colours come from teal, mint, sky, blue, coral and yellow. A black `*p5.brush` sits in the centre at size 50.
- **Fields:** a `#080f15` background with a white charcoal `circle(300,300,180,0.3)` and 30 HB `flowLine(rand, rand, 75, 0)`. The field changes every second through `listFields()`.
- **Stroke wheel:** `#e2e7dc`, 20 flowLines of length 320 fired outward from a ring of radius 100 that turns 30°/s, plus a centre `circle(300,300,100,0.2)` and the `*stroke()` label.
- **Hatches:** `#ffe6d4`, a jittering 6-point polygon hatched with HB `#c76282` at `hatch(15,45)`, and a triangle hatched with marker `#e0b411` at `hatch(10,130,{rand:0.1})`.
- **Watercolor:** paper that keeps building up, adding one rect (example) or circle (example2) every third frame. Each has fill opacity 60–110, `fillBleed` 0.1–0.55, `fillTexture(0.4,0.4)`, and a marker `#e0b411` outline. The colours are brown, navy, dark green, yellow, red and olive.
- **Splines** (example only): `#445e87`, a `2B #0e2d58` circle, and a white charcoal spline from (30,30) to (570,570) at curvature 1, with four `2H` white copies offset to the side.

Verify by serving the repo root (`python3 -m http.server`) and screenshotting. `scripts/shot.mjs` pauses p5 on chosen frames before taking the screenshot.
