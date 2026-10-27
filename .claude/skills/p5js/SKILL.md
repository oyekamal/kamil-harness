---
name: p5js
description: Write correct p5.js 2.x sketches (current major, p5@2.3.4) that run first time - standalone HTML from the CDN, global vs instance mode, several sketches on one page, React/Vite embedding with StrictMode-safe cleanup, 2D drawing, transforms, colour modes, noise and randomness, typography and textToPoints, images and pixels, mouse/keyboard/touch, frame-rate independent animation, WEBGL (camera, lights, buildGeometry), and exporting PNG / GIF / MP4 explainer videos through a headless recorder + ffmpeg. Lists the 1.x→2.x breaking changes that trip agents (preload removed → async setup, mouseButton object, keyCode, bezierVertex/curveVertex→splineVertex, textToPoints signature, WEBGL fonts). Includes a template and inline-p5 script for sandboxed, no-network iframe interactives. Triggers on "p5", "p5.js", "p5js", "processing sketch", "creative coding", "generative art", "sketch.js", "createCanvas", "draw loop", "particle system", "flow field", "Perlin noise animation", "flocking / boids", "fractal tree", "interactive simulation", "animated diagram", "recreate a p5js.org example", "p5 in React", "saveGif", "record a p5 sketch to video". For hand-drawn / pencil / watercolour looks use the sibling skill `p5-brush`.
---

# p5.js (2.x)

Verified headless: npm `latest` = **2.3.4** (`r1` tag = 1.11.13, v1 is frozen). Every
snippet below was run headless (Chromium + Playwright); findings marked *verified* came from those runs.
Most examples online and in your memory are **1.x**: read the trap list before writing code.

| File | Use |
|---|---|
| `templates/standalone.html` | copy-paste start: CDN tag, async setup, noise particles, deltaTime |
| `templates/P5Sketch.jsx` | React/Vite component, StrictMode-safe, props without re-creating the sketch |
| `templates/iframe-interactive.html` | sandboxed iframe interactive (controls + readouts + postMessage contract) |
| `scripts/render.cjs` | headless check: PNG of the canvas + console errors; `--frames N` deterministic recording |
| `scripts/inline-p5.cjs` | inline p5 for no-network pages (sandboxed iframes, offline HTML, email-safe artifacts) |
| `references/v1-to-v2.md` | full breaking-change table + behaviour notes found while verifying |
| `references/api-cheatsheet.md` | 2D API by topic: shapes, colour ranges, text, images, input, DOM, saving |
| `references/webgl.md` | WEBGL origin, camera, lights/materials, buildGeometry, fonts, framebuffers |

## 1. Load it

```html
<script src="https://cdn.jsdelivr.net/npm/p5@2.3.4/lib/p5.min.js"></script>
```
Pin the exact version (npm latest is 2.3.4; p5js.org/download still linked `p5@2.3.3` and the floating `p5@2`). npm: `npm i p5` then
`import p5 from 'p5'` (ESM, instance mode only). Sound is a separate library (`p5.sound@0.4.x`, after p5);
the old v1 p5.sound does not run on 2.x. Old sketch you must not rewrite: `p5@1.11.13`.

## 2. Two modes

**Global mode** (one sketch per page): define `setup`/`draw` (and handlers) as top-level functions.
The canvas goes into the first `<main>` (p5 creates one if missing).

```js
async function setup() {            // async OK in 2.x; this is where loading happens now
  createCanvas(710, 400);
  img = await loadImage('cat.png'); // every load*() returns a Promise; preload() no longer exists
  describe('What the canvas shows, for screen readers.');
}
function draw() { background(0); image(img, mouseX, mouseY); }
```

**Instance mode** (required for 2+ sketches on a page, React, bundlers, libraries): everything is a
method/property of `p`; nothing leaks onto `window`.

```js
const sketch = (p) => {
  let x = 0;
  p.setup = async () => { p.createCanvas(400, 200); };
  p.draw = () => { p.background(240); x = (x + p.deltaTime * 0.1) % p.width; p.circle(x, 100, 20); };
  p.mousePressed = () => { if (p.mouseButton.left) x = p.mouseX; };
};
const inst = new p5(sketch, document.getElementById('slot'));  // node or element id
// later: inst.remove()  -> stops the loop, removes canvas + DOM elements it made
```
Constants and statics in instance mode: `p.WEBGL`, `p.HSB`, `p.PI`, `p.CENTER`; but `p5.Vector.sub(a, b)`
(class static, no `p.`). Expose `window.__p5 = p` if a harness must drive it.

**React / Vite** (`templates/P5Sketch.jsx`, *verified* with React 19 StrictMode, 2 sketches → 2 canvases):

```jsx
useEffect(() => {
  let disposed = false;
  const inst = new p5((p) => {
    sketch(p, () => propsRef.current);          // read live props through a ref, never re-create
    const userSetup = p.setup;
    p.setup = async () => { if (userSetup) await userSetup(); if (disposed) p.remove(); };
  }, host.current);
  return () => { disposed = true; inst.remove(); };
}, [sketch]);                                    // sketch = module-level function (stable)
```
Why the extra `disposed` step: in 2.3.4, `remove()` called before setup has started (StrictMode's instant
unmount) is a no-op, so the naive `return () => inst.remove()` left **4 live canvases for 2 sketches**
(*verified*). Never put props in the effect deps: that tears down and rebuilds the canvas on every change.

## 3. The 1.x habits that break in 2.x (details: `references/v1-to-v2.md`)

1. `preload()` is gone → `async function setup(){ x = await loadX(...) }`.
2. `mouseButton === LEFT` → `mouseButton.left` / `.right` / `.center`.
3. `keyCode === UP_ARROW` is always false (constants are strings now: `UP_ARROW === 'ArrowUp'`) → `keyIsDown(UP_ARROW)` or `code === UP_ARROW`.
4. `createVector()` → `createVector(0, 0)` (vectors have any dimension).
5. `bezierVertex(6 numbers)` → one `bezierVertex(x, y)` per point: anchor, then 3 per cubic (`bezierOrder(2)` = quadratic); `quadraticVertex` gone.
6. `curveVertex/curve/curveTightness` → `splineVertex/spline/splineProperty('tightness', t)`; the spline now passes through the first and last points.
7. `font.textToPoints(str, x, y, size, opts)` → `textSize(size); font.textToPoints(str, x, y, opts)` (4th arg is a box width now; *verified* tiny output otherwise).
8. `textWidth` no longer counts leading/trailing spaces → `fontWidth` does.
9. WEBGL text needs `textFont(await loadFont(url))`; a CSS font name throws.
10. `touchStarted/Moved/Ended` → mouse handlers fire for touch; `touches[]` for multitouch.
11. Removed helpers `append, arrayCopy, concat, reverse, shorten, sort, splice, subset, createStringDict/NumberDict` → plain JS.
12. `shader()` applies to fills only (`strokeShader`, `imageShader` for the rest).

## 4. Core patterns (full API: `references/api-cheatsheet.md`)

- **Frame**: `background()` at the top of `draw()` clears; skip it (or `background(0, 20)`) for trails.
- **Transforms**: wrap every local change in `push()/pop()`; rotate about a pivot with
  `translate(px, py); rotate(a); shape-at-origin`. Recursion (fractal trees) = `push(); rotate(a);
  line(0,0,0,-h); translate(0,-h); branch(h*0.66); pop();` twice, stop below a length.
- **Colour**: `colorMode(HSB)` ranges are **360, 100, 100, alpha 1** (alpha max is 1, not 255); values
  above max clamp. `colorMode(OKLCH)` is L 0-100, C 0-150, H 0-360 (not CSS units). CSS strings work everywhere:
  `fill('#2563eb')`, `fill('rgb(0 0 0 / 50%)')`. Hue by index: `fill((i * 30) % 360, 80, 100)`.
- **Noise/random**: `noise(x*0.01, y*0.01, t)` (small steps = smooth); `randomSeed(n)`/`noiseSeed(n)`
  for repeatable output (needed for screenshots, tests and video). `random(arr)` picks an element.
- **Vectors and agents** (particles, boids): class with `position, velocity, acceleration` vectors;
  `update(){ vel.add(acc); vel.limit(maxSpeed); pos.add(vel); acc.mult(0); }`; steering =
  `p5.Vector.sub(desired, vel).limit(maxForce)`; heading for drawing: `rotate(vel.heading() + HALF_PI)`.
  Wrap edges with `if (pos.x < -r) pos.x = width + r` etc. Remove dead particles iterating backwards.
- **Text**: `textAlign(CENTER, CENTER)` before `text()` for centred labels; `text(str, x, y, w)` wraps.
  `textFont('Georgia')` is fine in 2D; for exact typography or points/3D use `await loadFont(...)`.
- **Images**: `await loadImage()`, `image(img, x, y, w, h)`, `tint()`, `filter(BLUR, 3)`, `createGraphics()`
  as an offscreen layer. Pixel loops: `pixelDensity(1)` first, then index `4*(y*width+x)`.
- **Interaction**: handlers (`mousePressed`, `mouseDragged`, `keyPressed`, `mouseWheel(e)`) for events,
  `mouseIsPressed`/`keyIsDown()` for polling in `draw()`. They fire for presses anywhere on the page:
  check the mouse is inside the canvas. DOM controls: `createSlider(min, max, value, step).input(fn)`.
- **Timing**: `deltaTime` (ms since last frame) for real-time motion, `frameRate(n)` to cap,
  `millis()` for clocks. For anything you will record, drive motion from `frameCount` only.
- **Responsive**: `createCanvas(windowWidth, windowHeight)` + `windowResized(){ resizeCanvas(windowWidth, windowHeight); }`.

## 5. WEBGL in five lines (more: `references/webgl.md`)

`createCanvas(w, h, WEBGL)` → origin is the **centre**, y down. Port 2D code with
`translate(-width/2, -height/2)`. Call `orbitControl()`, `lights()` (or `ambientLight/directionalLight/pointLight`)
inside `draw()`. Materials: `normalMaterial()`, `fill()`, `specularMaterial(c) + shininess(n)`, `emissiveMaterial`.
`noStroke()` before heavy meshes. Build static compound shapes once with
`g = buildGeometry(() => {...}); g.normalize();` then `model(g)` per frame; `freeGeometry(g)` before rebuilding.
Stroke on at `model()` time draws wireframe edges (*verified*).

## 6. Export: PNG, GIF, MP4

- One frame: `saveCanvas('name', 'png')` (or `keyPressed(){ if (key === 's') saveCanvas(...) }`).
- GIF: `saveGif('loop', 3)` seconds, or `saveGif('loop', 90, { units: 'frames' })` (*verified*: 60 frames, triggers a download).
- Headless PNG / proof it runs: `node scripts/render.cjs sketch.html out.png [--wait 1500] [--mouse 0.42,0.5]`
  (exits 1 on page errors, prints console errors; grabs `canvas.p5Canvas` via `toDataURL`, works for WEBGL).
- **Explainer video** (deterministic, any length, no dropped frames):
  1. animate from `const t = frameCount / 30` only; seed randomness; end of `setup()`: `if (window.__RECORD) noLoop();`
  2. `node scripts/render.cjs sketch.html frames/ --frames 300` (calls `redraw()` per frame, saves `f00000.png`...)
  3. `/usr/bin/ffmpeg -y -framerate 30 -i frames/f%05d.png -pix_fmt yuv420p -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" out.mp4`
  Use `pixelDensity(2)` for crisp 2x video; add narration with ffmpeg `-i voice.mp3 -shortest`.
  `saveFrames()` is capped at 15 s / 22 fps and downloads a file per frame: avoid it for video.

## 7. Performance rules

1. Do work once: precompute in `setup()`, cache with `createGraphics()`/`createFramebuffer()`, `buildGeometry()` in 3D.
2. Static picture? `noLoop()` and `redraw()` only on input. Pause off-screen sketches (`noLoop()` on `IntersectionObserver`).
3. O(n²) neighbour loops (boids, connected particles) are fine to ~300 agents; beyond, use a grid/bins.
4. Avoid per-frame object churn: reuse vectors (`v.set(x, y)`), avoid `createVector` in tight inner loops.
5. `pixelDensity(1)` for pixel-heavy or full-screen sketches on retina; `noStroke()` in WEBGL; batch shapes in one `beginShape()`.
6. `loadPixels/updatePixels` once per frame, not per pixel; `get(x,y)` per pixel is very slow.
7. `p5.disableFriendlyErrors = true` before setup when using the unminified `p5.js` build (`p5.min.js` printed no friendly errors in tests).

## 8. Mistakes agents make (check before you say done)

- Writing 1.x code (section 3). Grep your output for `preload`, `curveVertex`, `quadraticVertex`, `keyCode ===`, `mouseButton ===`.
- Calling p5 functions at top level before setup (`random()`, `color()`, `createVector()` in a global initialiser) → ReferenceError in global mode. Initialise inside `setup()`.
- Mixing modes: `circle()` inside an instance sketch (must be `p.circle`), or two global sketches on one page.
- Forgetting `push()/pop()` → transforms and styles bleed into everything drawn later.
- `angleMode(DEGREES)` set, then passing radians (or `PI`) into `rotate()` - and vice versa.
- `circle(x, y, r)`: the third argument is the DIAMETER.
- HSB alpha as 0-255 (`fill(h, 80, 100, 128)` is fully opaque; alpha max is 1).
- WEBGL: drawing at 2D coordinates (off by half a canvas), text without a loaded font, lights in `setup()` only.
- Re-creating the p5 instance on React re-render; missing cleanup; StrictMode double canvas.
- `millis()`/`deltaTime` motion in a recorded video (frames jitter); unseeded random in screenshots meant to be compared.
- Translucent `background()` trails never fully fade on an 8-bit canvas (grey ghosts).
- Claiming it works without running `scripts/render.cjs` and looking at the PNG.

## 9. Embedding in a sandboxed iframe

A host that shows generated HTML in `<iframe sandbox="allow-scripts">` (no same-origin) with a strict CSP
(`default-src 'none'`: inline script/style only, no network) and a fixed box needs a self-contained page.
p5 fits as the visual layer (simulations, animated diagrams, draggable mechanisms):

1. Start from `templates/iframe-interactive.html`: `window.manifest` and `window.model` defined
   synchronously first; real HTML `<input>` controls with ids (so a test can drive them by selector); readout
   elements printed from `model()`; `parent.postMessage({type:'interactive', event:{type:'change', params, outputs}}, '*')`
   on each change; the p5 sketch in **instance mode** mounted in a div, drawing only from that shared state.
2. Layout: fixed `html,body{width:720px;height:460px;margin:0}` (adjust to your host), controls in a ~250 px left column, canvas sized to the rest.
3. Inline p5 before shipping: `node scripts/inline-p5.cjs in.html out.html` (~970 KB; also adds a guard that
   stops p5's `devicemotion` listeners, which log console errors in a sandboxed iframe on an http host).
4. No network means no CDN, no `loadFont(url)`, no `loadImage(url)`: use `data:` URIs or draw in code.
5. Check with `scripts/render.cjs` (no console errors, readouts match `window.model()`). P2D and WEBGL both render inside the sandbox (*verified*).

For a hand-drawn whiteboard look (marker, chalk, pencil, watercolour fills) layer the sibling skill
**`p5-brush`** on top of this one. Narrated 3Blue1Brown-style clips: record with section 6, or see
`karpathy-explainers` / Manim if the board needs a rendered video object instead of a live sketch.

## 10. Done checklist

- [ ] 2.x idioms only (section 3 grep is clean); exact CDN pin.
- [ ] `node scripts/render.cjs file.html out.png` exits 0, no console errors, and you looked at `out.png`.
- [ ] Interaction tested with `--mouse fx,fy` (or Playwright clicks/drags) when the sketch depends on input.
- [ ] `describe()` present; canvas size and colours match the brief; seeded if output is compared.
- [ ] Embedded: one canvas per sketch after StrictMode remount; `remove()` on unmount.
