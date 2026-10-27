# p5.js 2.x API cheat-sheet (2D)

Instance mode: prefix everything with `p.` (`p.circle`, `p.width`, `p.mouseX`, `p.PI`, `p.HSB`).
Static helpers stay on the class: `p5.Vector.sub(a, b)`, `p5.Vector.fromAngle(a, len)`.

## Structure and timing
| Need | Call |
|---|---|
| lifecycle | `setup()` once (may be `async`), `draw()` every frame; `windowResized()` |
| canvas | `createCanvas(w, h[, WEBGL])`, `resizeCanvas(w, h)`, `noCanvas()`, `pixelDensity(n)` (default = devicePixelRatio) |
| full window | `createCanvas(windowWidth, windowHeight)` + `function windowResized(){ resizeCanvas(windowWidth, windowHeight) }` |
| loop control | `noLoop()`, `loop()`, `redraw()`, `isLooping()` |
| time | `frameCount`, `millis()` (ms since draw loop began), `deltaTime` (ms since last frame) |
| fps | `frameRate(30)` sets target; `frameRate()` reads the measured fps; `getTargetFrameRate()` |
| frame-rate independent motion | `x += speedPerSecond * deltaTime / 1000` |
| recordable (deterministic) motion | `const t = frameCount / 30` (seconds at 30 fps); never `millis()` in a sketch you will record |
| accessibility | `describe('what the canvas shows')`, `textOutput()`, `gridOutput()` |

## Shapes
`point(x,y)` `line(x1,y1,x2,y2)` `rect(x,y,w,h[,radius])` `square(x,y,s)` `ellipse(x,y,w[,h])`
`circle(x,y,d)` (d = DIAMETER) `arc(x,y,w,h,start,stop[,PIE|CHORD|OPEN])` `triangle(...)` `quad(...)`
`bezier(x1,y1,cx1,cy1,cx2,cy2,x2,y2)` `spline(...)` (was `curve`).
Modes: `rectMode(CENTER|CORNER|CORNERS|RADIUS)`, `ellipseMode(...)`, `imageMode(...)`.
Custom: `beginShape([POINTS|LINES|TRIANGLES|TRIANGLE_STRIP|TRIANGLE_FAN|QUADS|QUAD_STRIP])`
`vertex(x,y)` ... `endShape([CLOSE])`. Holes: `beginContour()` ... `endContour(CLOSE)` inside the shape
(contour vertices wound opposite to the outer ones).
Curves in 2.x: `bezierOrder(3)` then `bezierVertex(x,y)` point by point (anchor + 3 per cubic);
`splineVertex(x,y)` passes through every point including the ends.

## Style
`fill(...)`, `noFill()`, `stroke(...)`, `noStroke()`, `strokeWeight(px)`, `strokeCap(ROUND|SQUARE|PROJECT)`,
`strokeJoin(MITER|BEVEL|ROUND)`, `blendMode(BLEND|ADD|MULTIPLY|SCREEN|...)`, `erase()`/`noErase()`,
`clip(() => { circle(...) })` (draw only inside a mask; callback form).
`background(...)` each frame clears; translucent `background(0, 20)` leaves trails (8-bit canvas: faint
ghosts never fully fade; fix with an occasional opaque clear or `clear()` + an offscreen buffer).
Canvas 2D extras through `drawingContext` (P2D only): `drawingContext.shadowBlur = 20;
drawingContext.shadowColor = 'rgba(0,0,0,.4)'`, `createLinearGradient` + `drawingContext.fillStyle = g`.

## Colour
`color(...)` accepts the current mode's numbers, CSS strings (`'#2563eb'`, `'rgb(0 0 0 / 50%)'`,
`'tomato'`), or a p5.Color.
Default ranges per mode (from the 2.3.4 source): `RGB` 255,255,255,a255 · `HSB`/`HSL`/`HWB` 360,100,100,a**1** ·
`LCH`/`OKLCH` L100, C150, H360, a1 · `LAB`/`OKLAB` L100, ±125, ±125, a1. Override: `colorMode(HSB, 360, 100, 100, 1)`.
So `colorMode(OKLCH); color(70, 40, 30)` (not 0.7, 0.15 as in CSS). Values above the max clamp (HSB `fill(h, 255, 255)` = full).
Mixing: `lerpColor(c1, c2, t)`, `paletteLerp([[c1, 0], [c2, 0.5], [c3, 1]], t)`.
Read parts: `red(c) green(c) blue(c) alpha(c) hue(c) saturation(c) brightness(c) lightness(c)`.
Alpha in fill: `fill(255, 0, 0, 128)` (RGB 0-255) or `fill(0, 80, 90, 0.5)` (HSB with alpha max 1).

## Transforms
`translate(x,y)`, `rotate(a)`, `scale(s[, sy])`, `shearX/shearY`, `applyMatrix(...)`, `resetMatrix()`.
Always pair `push()` / `pop()` (they save style AND transform). Order matters: last call applies first to
the shape, so "move to pivot, rotate, draw at origin" is `translate(px,py); rotate(a); rect(-w/2,-h/2,w,h)`.
`angleMode(DEGREES|RADIANS)` (default RADIANS); constants `PI`, `HALF_PI`, `TWO_PI`, `TAU`, `QUARTER_PI`.

## Maths, noise, randomness
`random(a, b)`, `random(array)`, `randomGaussian(mean, sd)`, `randomSeed(n)` (repeatable runs).
`noise(x[, y[, z]])` Perlin in 0..1, smooth for small steps (0.005..0.05 per pixel); `noiseDetail(octaves, falloff)`;
`noiseSeed(n)`. Animated field: `noise(x*s, y*s, frameCount*0.01)`. Flow angle: `noise(...) * TWO_PI * 2`.
`map(v, a1, b1, a2, b2[, clamp])`, `constrain(v, lo, hi)`, `lerp(a, b, t)`, `dist(x1,y1,x2,y2)`, `mag`, `norm`,
`sq`, `sqrt`, `pow`, `abs`, `floor/ceil/round`, `min/max`, `sin/cos/tan/atan2`, `degrees/radians`.
Vectors: `v = createVector(x, y)`; `.add .sub .mult .div .mag .setMag .normalize .limit(max) .heading()
.rotate(a) .dist(w) .copy() .set(x,y) .lerp(w,t) .dot .cross`; static `p5.Vector.add/sub/dist/fromAngle/random2D()`.
Mutating methods change `v` in place: use `p5.Vector.sub(a, b)` or `a.copy().sub(b)` when you need a new one.

## Text and typography
`text(str, x, y[, boxW, boxH])`, `textSize(px)`, `textAlign(LEFT|CENTER|RIGHT, TOP|CENTER|BASELINE|BOTTOM)`,
`textLeading(px)`, `textStyle(NORMAL|BOLD|ITALIC|BOLDITALIC)`, `textWeight(100..900)` (variable fonts),
`textWrap(WORD|CHAR)` (with box width), `textFont('Georgia')` (CSS name, P2D only) or
`textFont(await loadFont(url))`. Measure: `textWidth` (tight), `fontWidth` (with spaces), `textAscent()`,
`textDescent()`, `textBounds(str, x, y)`.
Points from glyphs: `textSize(160); pts = font.textToPoints('Hi', x, y, { sampleFactor: 0.2 })` → `{x, y, alpha}`;
`font.textToContours(...)` for one array per contour; `font.textToModel(...)` for 3D extrusion.
Fonts offline (sandbox / no network): `loadFont('data:font/ttf;base64,...')` or a CSS `@font-face` string.

## Images and pixels
`img = await loadImage(url)`; `image(img, x, y[, w, h])`; `tint(r,g,b,a)`/`noTint()`; `img.resize(w, 0)`;
`img.get(x,y[,w,h])`; `createImage(w, h)`; `copy(...)`; `filter(GRAY|THRESHOLD|INVERT|POSTERIZE|BLUR|ERODE|DILATE|OPAQUE[, param])`.
Pixel loop: `loadPixels(); const d = pixelDensity(); /* index = 4*((y*d)*width*d + x*d) */ ... updatePixels()`.
With `pixelDensity(1)` the index is just `4*(y*width + x)`.
Offscreen layer: `g = createGraphics(w, h)`; draw with `g.circle(...)`; show with `image(g, 0, 0)`.
Data URLs work for images without network: `loadImage('data:image/png;base64,...')`.

## Interaction
Variables: `mouseX mouseY pmouseX pmouseY movedX movedY mouseIsPressed mouseButton.left/.right/.center
keyIsPressed key code touches[] width height windowWidth windowHeight focused`.
Handlers: `mousePressed mouseReleased mouseClicked doubleClicked mouseMoved mouseDragged mouseWheel(e)`
(`e.delta`; `return false` stops page scroll EVERYWHERE, not only over the canvas: verified; check the mouse is over the canvas first), `keyPressed keyReleased keyTyped`, `windowResized`.
Polling: `keyIsDown(LEFT_ARROW)`, `keyIsDown('a')`. Constants: `LEFT_ARROW RIGHT_ARROW UP_ARROW DOWN_ARROW ENTER ESCAPE BACKSPACE DELETE TAB SHIFT CONTROL OPTION ALT`.
Hit tests yourself: circle `dist(mouseX, mouseY, cx, cy) < r`; rect `mouseX > x && mouseX < x+w && ...`.
Drag pattern: on press pick the hit object and store the offset; on drag set `obj.x = mouseX - offX`; on release clear.
Handlers fire for presses anywhere on the page; check `mouseX/Y` are inside `0..width/height` if the canvas is not full page.
Mouse coordinates are canvas pixels in CSS units; in WEBGL the origin is the centre, so subtract `width/2, height/2`.

## DOM helpers (p5 creates real HTML elements)
`createSlider(min, max, value, step)` → `.value()`, `.input(fn)`; `createButton('Go').mousePressed(fn)`;
`createCheckbox('label', false).changed(fn)` → `.checked()`; `createSelect()` + `.option('a')`;
`createInput('')`; `createP('text')`, `createDiv()`, `createSpan()`; every element has `.position(x,y)`, `.parent(el)`,
`.id('x')`, `.class('c')`, `.style('font-size','16px')`, `.html('...')`, `.remove()`.
Elements are appended after the canvas in document flow unless you `.position()` or `.parent()` them.

## Saving output
`saveCanvas('name', 'png')`; `save('name.png')`; `saveGif('name', 5)` (seconds; or `{ units: 'frames' }`;
re-renders the frames itself, verified: 60 frames at 160x90 in ~2 s headless); `saveFrames('f', 'png', 3, 20)`
(capped at 15 s and 22 fps; downloads one file per frame; prefer `scripts/render.cjs --frames`).
Graphics buffers: `g.save('layer.png')`.
