# p5.js 1.x → 2.x: what breaks (verified against p5@2.3.4)

Sources: github.com/processing/p5.js-compatibility README, p5js.org/tutorials/v2_transition/, and
the 2.3.4 build itself (grep of `lib/p5.js`, plus headless runs). npm dist-tags at that date:
`latest` = 2.3.4, `r1` = 1.11.13 (v1 is frozen, "will not be maintained"). Most tutorials,
Stack Overflow answers and model training data are 1.x, so these are the traps.

| 1.x code (what you remember) | 2.x code | Notes |
|---|---|---|
| `function preload(){ img = loadImage('a.png') }` | `async function setup(){ createCanvas(..); img = await loadImage('a.png') }` | `preload` is gone. Every `load*()` returns a Promise. Instance mode: `p.setup = async () => {...}`. |
| `loadJSON(url, cb)` in preload | `data = await loadJSON(url)` | Callbacks still accepted. `loadBytes` returns the `Uint8Array` directly; `loadTable(file, separator, header)`. |
| `mouseButton === LEFT` | `mouseButton.left` (`.right`, `.center`) | It is an object of booleans now; several can be true. |
| `keyCode === UP_ARROW` | `keyIsDown(UP_ARROW)` (both versions) or `code === 'ArrowUp'` | In 2.x the constants are strings (`UP_ARROW === 'ArrowUp'`, `ENTER === 'Enter'`), so comparing them to the numeric `keyCode` is always false. `keyIsDown` is the safe choice; `key` is still the character (`key === 's'`). |
| `touchStarted/Moved/Ended` | `mousePressed/Dragged/Released` + `touches[]` | Pointer events: mouse handlers fire for touch too. |
| `createVector()` = (0,0,0) | `createVector(0, 0)` or `createVector(0, 0, 0)` | Vectors have any dimension; always pass the zeros. |
| `bezierVertex(cx1,cy1,cx2,cy2,x,y)` | `bezierVertex(x,y)` once per point; first one is the anchor, then 3 per cubic | `bezierOrder(2)` gives quadratic (3 points per segment incl. anchor). |
| `quadraticVertex(cx,cy,x,y)` | `bezierOrder(2)` + `bezierVertex(cx,cy)` + `bezierVertex(x,y)` | |
| `curveVertex(...)`, `curve()`, `curvePoint`, `curveTangent`, `curveTightness(t)` | `splineVertex`, `spline()`, `splinePoint`, `splineTangent`, `splineProperty('tightness', t)` | 2.x spline passes THROUGH the first and last points (no duplicated end points needed); `splineProperty('ends', EXCLUDE)` restores 1.x ends. `endShape(CLOSE)` closes it smoothly. |
| `bezierDetail`, `curveDetail` | `curveDetail()` covers both | |
| `endContour()` closed by default | pass `endContour(CLOSE)` explicitly | |
| `textWidth("  Hi  ")` incl. spaces | `fontWidth("  Hi  ")` incl. spaces; `textWidth` = tight box without leading/trailing space | Measured: Anton 24px `textWidth('Hi')`=18, `fontWidth('Hi ')`=24. |
| `font.textToPoints(str, x, y, fontSize, {sampleFactor})` | `textSize(n); font.textToPoints(str, x, y, {sampleFactor})` | 4th arg is NOT fontSize in 2.x (signature `str, x, y, [width, height], [options]`). Passing 160 there silently gives a tiny glyph. Verified. |
| `text()` in WEBGL with a CSS font name | `font = await loadFont(url)` then `textFont(font)` | WEBGL throws "you must load and set a font before drawing text". |
| `loadFont('x.ttf')` only | also a Google Fonts CSS URL or an `@font-face` string | `loadFont('https://fonts.googleapis.com/css2?family=...')` works in 2.x. |
| `createStringDict`, `createNumberDict`, `append`, `arrayCopy`, `concat`, `reverse`, `shorten`, `sort`, `splice`, `subset` | plain JS objects / `Array` methods | Removed. |
| old `p5.sound` bundled with v1 | new `p5.sound.js` (`p5.sound@0.4.x`, script after p5) | The v1 sound library does not run on v2. |
| custom shader auto-applied to strokes/images by uniforms | `shader(s)` = fills only; `strokeShader(s)`, `imageShader(s)` | 2.x also has `baseMaterialShader().modify({...})` and p5.strands (JS-written shaders). |

New in 2.x worth using: colour modes `OKLCH`, `LCH`, `HWB`, `LAB` alongside `RGB/HSB/HSL`;
`textWeight()` for variable fonts; `buildGeometry()` + `freeGeometry()`; `createFramebuffer()`;
`paletteLerp()`; pointer-unified input; better `keyIsDown` smoothness.

Escape hatches (only for porting old sketches): pin v1 with
`https://cdn.jsdelivr.net/npm/p5@1.11.13/lib/p5.min.js`, or load the compatibility add-ons
(`preload.js`, `shapes.js`, `data.js`, `events.js` from processing/p5.js-compatibility) after p5 2.x.
For new work, write 2.x code.

Behaviour notes found while verifying (not in the docs):
- 2.x creates a default 100x100 canvas before `setup()` runs; `createCanvas` replaces it. A sketch
  with no `createCanvas` still shows a 100x100 canvas (use `noCanvas()` for DOM-only sketches).
- Global mode appends the canvas to the first `<main>` element (creating one if missing). Instance
  mode puts it inside the node you pass to `new p5(sketch, node)`.
- `instance.remove()` called while the page is already loaded and setup has not started yet is a
  no-op (start is async; there is no canvas to remove yet), so React StrictMode leaks a second live
  canvas. See the fix in `templates/P5Sketch.jsx`.
- In a sandboxed iframe (`sandbox="allow-scripts"`) p5 registers `devicemotion`/`deviceorientation`
  listeners and Chromium logs "Permissions policy violation: accelerometer is not allowed" as a
  console ERROR (2 per sketch; seen with an http:// or file:// host page, not with a Playwright
  `set_content` host). Harmless, but any check that fails on console errors fails. The guard that
  `scripts/inline-p5.cjs` injects removes them.
