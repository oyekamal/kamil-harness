# p5.brush 2.2.3: full API reference

These signatures were read from `src/index.shared.js` (the exports), `src/index.standalone.js` and the module sources. Where the README and src disagree, src wins, and the difference is marked **(src)**.

## Exports

Shared by both builds: `seed`, `noiseSeed`, `wRand`, `load`, `instance`, `field`, `noField`, `addField`, `refreshField`, `listFields`, `wiggle`, `Position`, `Polygon`, `Plot`, `rect`, `circle`, `arc`, `beginShape`, `vertex`, `endShape`, `beginStroke`, `move`, `endStroke`, `spline`, `polygon`, `add`, `box`, `scaleBrushes`, `pick`, `stroke`, `strokeWeight`, `set`, `noStroke`, `clip`, `noClip`, `line`, `flowLine`, `hatch`, `hatchStyle`, `noHatch`, `hatchArray`, `mass`, `noMass`, `massArray`, `fill`, `noFill`, `fillTexture`, `fillBleed`, `wash`, `noWash`.

Standalone only: `createCanvas`, `render`, `clear`, `push`, `pop`, `translate`, `rotate`, `scale`, `angleMode`, `getAngleMode`, `DEGREES` (`"degrees"`), `RADIANS` (`"radians"`), `random`, `noise`. `instance()` is a no-op in the standalone build.

In the p5 build, p5's own `push`, `pop`, `randomSeed` and `noiseSeed` are wrapped (`src/adapters/p5/addon.js`), and compositing is flushed in the `postsetup` and `postdraw` lifecycles.

## Configuration

- `brush.scaleBrushes(k)` multiplies `weight`, `scatter` and `spacing` of every brush registered so far. It adds up across calls.
- `brush.load(target?)`. **p5 build:** call it with no argument for the main canvas (rarely needed, it loads itself). Pass a `p5.Graphics` made with `WEBGL`, or a `p5.Framebuffer` while it is inside `fb.draw(() => {...})` or `begin()`/`end()`. Call `brush.load()` again to go back to the main canvas. `pg.createFramebuffer()` is not supported. Native p5 calls must target the buffer themselves (`pg.background()`). **Standalone:** pass an `HTMLCanvasElement` or `OffscreenCanvas`, which must support WebGL2.
- `brush.instance(p)` is for p5 instance mode. Call it inside the sketch function, before setup and draw.
- Standalone: `brush.createCanvas(w, h, {pixelDensity=1, parent, id})` returns the canvas and loads it. `brush.render()` flushes. `brush.clear()` clears to transparent, and `brush.clear(color)` or `clear(r,g,b)` clears to an opaque colour.

## Stroke

- `set(name, color, weight = 1)` sets brush, colour and weight, and turns stroke on.
- `pick(name)` throws `Brush "x" not found. Available brushes: ...` when the name is unknown.
- `stroke(r,g,b | color)` and `strokeWeight(w)` change one property each. `noStroke()` turns stroke off.
- `line(x1,y1,x2,y2)` and `flowLine(x,y,length,dir)` **throw** when stroke is off or has no colour **(src)**. `dir` is measured anticlockwise from +x and uses the current angle mode.
- `clip([x1,y1,x2,y2])` and `noClip()` affect strokes and hatches, not fills. The transform is captured at the moment you call it.
- `box()` returns every brush name.

## Built-in brush parameters (src/stroke/stroke.js, before scaleBrushes)

| name | weight | scatter | sharpness | grain | opacity | spacing | type |
|---|---|---|---|---|---|---|---|
| pen | 0.3 | 0.15 | 0.9 | 0.7 | 150 | 0.1 | default |
| rotring | 0.15 | 0.05 | 0.7 | 0.9 | 210 | 0.1 | default |
| 2B | 0.3 | 0.75 | 0.45 | 0.8 | 180 | 0.1 | default |
| HB | 0.3 | 0.6 | 0.3 | 0.7 | 170 | 0.1 | default |
| 2H | 0.2 | 0.6 | 0.3 | 0.75 | 120 | 0.1 | default |
| cpencil | 0.35 | 0.55 | 0.8 | 0.7 | 75 | 0.1 | default |
| pastel | 0.7 | 5 | 0.91 | 1 | 30 | 0.028 | default, rotate natural, gaussian pressure |
| crayon | 0.33 | 1.9 | 0.75 | 2 | 159 | 0.07 | default, rotate natural |
| charcoal | 0.35 | 1.5 | 0.68 | 2 | 120 | 0.03 | default |
| spray | 0.2 | 6 | 15 | 40 | 90 | 0.5 | spray |
| marker | 2 | 0.2 | – | – | 1 | 0.03 | marker |

`marker2` and `hatch_brush` (named in the README) **do not exist**. For a `default`-type brush with stroke weight w, the alpha is `opacity / min(w, 1.3)`, so heavier strokes are relatively less opaque per stamp.

## brush.add(name, params)

| key | meaning |
|---|---|
| `type` | `"default"`, `"spray"`, `"marker"`, `"custom"` or `"image"`. Any other value becomes `default` |
| `weight` | base thickness in canvas units |
| `scatter` | sideways spread (the legacy name `vibration` also works) |
| `sharpness` | 0–1, edge softness, `default` type only (legacy name `definition`) |
| `grain` | texture density, `default`/`spray` (legacy name `quality`) |
| `opacity` | 0–255 per stamp. Marker-type brushes need very low values (1–10) because the stamps build up |
| `spacing` | gap between stamps. 1 means no overlap, lower is denser |
| `pressure` | `[start,end]`, `[start,mid,end]`, `(t)=>value` where t runs 0..1, or `{mode:"gaussian", curve:[a,b], min_max:[hi,lo]}` |
| `tip` | `custom` only. `(_m) => {...}`. Draw in a 100×100 space centred on 0. Dark means opaque, white means transparent. In the standalone build `_m` is a small 2D wrapper (push/pop/translate/scale/rotate in **radians**, fill/stroke/noFill/noStroke/strokeWeight, rect/circle/ellipse/line, beginShape/vertex/endShape, pixels), and colours are numbers, arrays or CSS strings, never p5.Color |
| `image` | `image` only. `{src:"./tip.jpg"}`, and `add` returns a Promise, so `await` it |
| `rotate` | `"none"`, `"natural"` (follows the stroke) or `"random"` |
| `markerTip` | marker/custom/image only, default `true`. This builds up colour at the stroke ends |
| `noise` | 0–1, default 0.3. Random opacity variation per stroke |

If `custom` has no `tip`, `add` throws. If `image` has no `image.src`, it also throws. Re-adding a name replaces the old brush. Brushes added after `scaleBrushes` are not scaled.

## Fill, wash

- `fill(color, opacity)` or `fill(r,g,b,opacity)`. Opacity runs 0–255. `noFill()` turns fill off.
- `fillBleed(strength 0..1, direction = "out" | "in", angle = null)`. The angle sets the wash direction. With no angle the direction is random.
- `fillTexture(texture = 0.4, border = 0.4, scatter = true)`.
- `wash(color, opacity)` and `noWash()` give a flat, fast fill.
- Fills apply to `rect`, `circle`, `polygon` and closed `beginShape`/`endShape`, never to `arc` or lines.

## Hatch, mass

- `hatch(dist, angle, {rand: 0..1|false, continuous: bool, gradient: 0..1|false})`. The defaults are all `false`. The angle uses the current angle mode.
- `hatchStyle(name, color, weight)`. If you never call it, hatching uses the current stroke brush.
- `noHatch()` turns hatching off. `hatchArray(polygon | polygon[])` hatches several shapes as one gesture.
- `mass(brushName, color, {precision 0..1, strength 0..1, gradient 0..1, outline bool})`. The brush name is required. `strength` sets how many of the 3 internal layers are drawn.
- `noMass()` turns mass off. `massArray(polygon | polygon[])` uses the first polygon as the outline and the rest as even-odd holes.

## Fields

- Built-in fields: `hand`, `curved`, `zigzag`, `waves`, `seabed`, `spiral`, `columns`.
- `field(name)`, `noField()`, `wiggle(n)` (the `hand` field at intensity n), `listFields()`, `refreshField(t)`.
- `addField(name, (t, field) => { for col for row field[col][row] = angle; return field }, {angleMode: "degrees" | "radians"})`. You must return `field`.
- `polygon()` ignores fields. Lines, flowLines, rects, circles, arcs, splines and shapes all follow the active field.

## Primitives and their return values

| call | uses | returns |
|---|---|---|
| `line(x1,y1,x2,y2)` | stroke | – |
| `flowLine(x,y,len,dir)` | stroke | – |
| `spline(pts, curvature = 0.5)` | stroke. `pts` are `[x,y]` or `[x,y,pressure]`, at least 2 | `Plot` |
| `beginStroke("curve" \| "segments", x, y)` / `move(angle, len, pressure)` / `endStroke(angle, pressure)` | stroke | – |
| `arc(x,y,r,start,end)` | stroke only | `Plot`, or `null` for a zero sweep |
| `rect(x,y,w,h, mode = "corner" \| "center")` | stroke, fill, hatch, mass | – |
| `circle(x,y,radius, irregularity?)` | stroke, fill, hatch, mass (`true` means strong irregularity) | `[plot, x, y]` |
| `polygon([[x,y],...])` | stroke, fill, hatch, mass, ignores the field | `Polygon` |
| `beginShape(curvature = 0)` / `vertex(x,y,pressure = 1)` / `endShape(close = false)` | everything when closed. Needs at least 2 vertices | `Plot` |

## Classes

- `new brush.Polygon([[x,y],...])` has `.draw(brush?, color?, weight?)`, `.fill(color?, opacity?, bleed?, texture?, border?, direction?, angle?)`, `.wash(color?, opacity?)`, `.hatch(dist?, angle?, options?)`, `.mass()`, `.intersect({point1, point2})` returning `[{x,y}]`, `.vertices` and `.sides`.
- `new brush.Plot("curve" | "segments")` has `.addSegment(angle, len, pressure)`, `.endPlot(angle, pressure)`, `.rotate(a)`, `.genPol(x, y, scale?, step?)` returning a `Polygon`, `.draw(x,y)`, `.fill(x,y)`, `.wash(x,y)`, `.hatch(x,y)`, `.mass(x,y)`, `.origin`, `.segments`, `.angles`, `.press` and `.type`. Plots returned from shapes carry `.origin`. The upstream code uses `plot.genPol(plot.origin[0], plot.origin[1], 1, 0.3)` to get Polygons for `hatchArray` and `massArray`.
- `new brush.Position(x, y)` has `.moveTo(dir, len, step)`, `.plotTo(plot, len, step, scale)`, `.angle()`, `.reset()`, `.x`, `.y` and `.plotted`.

## Errors you will see, and what they mean

- `p5.brush could not resolve an active WEBGL sketch...`: the canvas is 2D, or brush was called before `createCanvas(..., WEBGL)`.
- `p5.registerAddon is not a function`: you loaded p5 1.x. p5.brush needs p5 2.x.
- `No brush or color set. Call brush.set(...)`: `line` or `flowLine` ran after `noStroke()`.
- `Brush "x" not found. Available brushes: ...`: a typo, or a stale README name.
- `vertex() called outside of beginShape()`, `endShape() requires at least 2 vertices`, `spline() requires at least 2 points`, `beginStroke() type must be "curve" or "segments"`.
- Standalone `Invalid color value "..."` comes from a colour the browser cannot parse.
- Standalone console warning `Drawing calls were made but brush.render() was never called`.
- `WebGL: INVALID_OPERATION: bindFramebuffer: object does not belong to this context` appears after switching `load()` between two live WebGL canvases. Prefer one shared surface.

## Upstream issue history worth knowing

- #11: performance is slow by design. Use it for stills or for accumulating animations.
- #14 and #20 are v1 issues where marks showed up late. In v2 the flush happens at the end of setup and draw (p5 build) or at `render()` (standalone). `reDraw`/`reBlend` were removed.
- #36: v1 broke on p5 1.10+. v2 targets p5 2.x only.
- #39: multiple p5 instances, fixed in 2.x.
- #40: the extra hidden canvases are gone. Hard canvas resizes are not supported, so resize with CSS.
- #42: there is now a clear error in 2D mode.
- #43 and #49: a crash on polygons with zero area (centroid), fixed by 2.2.3.
- #46: there is no `brush.ellipse`. Use `circle(x, y, radius)`, or `beginShape` with vertices placed on an ellipse.
