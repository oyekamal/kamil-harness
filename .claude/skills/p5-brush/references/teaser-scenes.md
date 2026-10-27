# Upstream teaser sketches: how each scene is built

Two sketches in the repo show the library off: `example/` (6 scenes) and `example2/`, the "2.x teaser" (7 scenes). Both use the p5 build. The p5 version is pinned by the html. Both run on p5@2.1.1, and p5.brush 2.2.3 also runs on 2.2.0 and 2.3.4. The setup is shared:

```js
let font;
async function setup() {
  const c = createCanvas(600, 600, WEBGL); c.id("main");
  // CSS fit: canvas max 100vw/100vh, width/height auto, object-fit contain; body is a centred flex box, margin 0, overflow hidden
  font = await loadFont("https://fonts.gstatic.com/s/inter/v3/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuGKYMZhrib2Bg-4.ttf");
  angleMode(DEGREES);
  brush.scaleBrushes(3.5);            // example/ ; example2/ uses 3
  brush.add("watercolor", { type: "custom", weight: 10, scatter: 1.05, opacity: 9, spacing: 0.3,
    pressure: [0.8, 1.3], rotate: "natural",
    tip: (_m) => { _m.fill(0, 200); _m.rect(-20, -20, 50, 50); _m.rect(25, 25, 20, 20); } });
  frameRate(30);
}
function draw() {
  const t = frameCount / 30;
  const scene = floor(t / 5) % 6;      // example2: floor(t / 6) % 7
  textFont(font);
  translate(-width / 2, -height / 2);
  // ... scene switch ...
}
function mouseClicked() { noLoop(); }  // click pauses
```

Labels use native p5 `text()` in Inter, are centred with `textAlign(CENTER, CENTER)`, start with `*`, and are drawn with `noStroke(); fill(gray)` inside `push()`/`pop()`. Shared palette: `["#002185","#003c32","#fcd300","#ff2702","#6b9404"]`. example2 adds `"#4e93cc"` and `"#9b1d10"`. To keep shapes from shimmering, each element is re-seeded before it is drawn (`randomSeed(33213 * seeds[i])`, where `seeds` is 150 `random()` values made in setup in example/, or fixed integers in example2), so the same element looks the same in every frame.

## example/ (5 s per scene, 30 s loop)

0. **Brush rain**: `*p5.brush`, black, size 50, at (280, 295). Paper `#fffceb` is painted **once** when the scene starts and never again, so strokes pile up. Each frame: `brush.field("seabed")`; `brush.set(random(["marker","watercolor","spray","charcoal","HB","2B","cpencil","2H","rotring"]), random(["#2c695a","#4ad6af","#7facc6","#4e93cc","#f6684f","#ffd300"]), random(0.7, 1.6))`; `brush.flowLine(random(600), random(600), random(140, 240), random(360))`. The label is drawn every frame, before the stroke. Result: a dense tangle of about 150 wavy, mostly diagonal strokes in teal, mint, sky blue, coral and yellow, mixing thin pencil lines, broad soft marker bands, speckled spray clouds and grainy charcoal.
1. **Fields**: a `#080f15` background redrawn every frame. Once a second, `brush.field(listFields()[floor(t % n)])` cycles through the 7 fields. Then `randomSeed(fixed)`, `brush.set("charcoal","white",1); brush.circle(300,300,180,0.3)`, `brush.pick("HB")`, and 30 times `brush.flowLine(random(600), random(600), 75, 0)` from fixed seeds. `*field()` at 40 in gray 210 sits in the centre. Result: a large chalky white ring, warped by whichever field is active, with 30 short white pencil dashes all flowing the same way.
2. **Stroke wheel**: a `#e2e7dc` sage background, `field("seabed")`. For i in 0..19: `angle = i*18 + t*30`, re-seed, `brush.set(random(["marker","marker","watercolor","watercolor","charcoal","HB","2B","rotring"]), random(palette), 1)`, `brush.flowLine(300 + 100*cos(-angle), 300 + 100*sin(-angle), 320, angle)`. Then `noField()`, re-seed every half second, a random brush and colour, and `brush.circle(300,300,100,0.2)`. `*stroke()` at 40 in gray 40. Result: 20 coloured rays bursting from a ring around a hand-drawn centre circle, slowly turning.
3. **Hatches**: a `#ffe6d4` peach background. `brush.hatchStyle("HB","#c76282",1.3); brush.hatch(15,45)`, then a 6-point polygon (80,150) (180,150) (420,150) (480,450) (280,450) (130,450), each point jittered ±20 by `sin(random(360) + t*150)`. Then `brush.hatchStyle("marker","#e0b411",1.3); brush.hatch(10,130,{rand:0.1})` and a triangle near (250,250) (500,300) (300,520), also jittering. `*hatch()` at 40 in gray 50, then `brush.noHatch()`. The polygon outlines use whatever stroke was left from the previous scene, so they come out a random colour, often a yellow-green marker. Result: a pink diagonal-hatched quadrilateral overlapped by a yellow cross-hatched triangle.
4. **Watercolor**: paper painted once with `*fill()` at 40, black, in the centre. `brush.set("marker","#e0b411",1.1)`. On every frame where `(10*t) % 3 === 0` (every 9th frame, about 16 per scene): `brush.fill(random(["#7b4800","#002185","#003c32","#fcd300","#ff2702","#6b9404"]), random(60,110)); brush.fillBleed(random(0.1,0.55)); brush.fillTexture(0.4,0.4); brush.rect(random(600), random(600), random(50,140), random(50,140), "center"); brush.noFill()`. Result: pale watercolor rectangles in ochre, lime, aqua and yellow, each with a thin yellow marker outline, a darker pooled rim and blobby bled edges. Navy and dark green at this opacity come out as light aqua or teal, not dark.
5. **Splines**: `#445e87` slate blue, `noField()`. `brush.set("2B","#0e2d58",2); brush.circle(155,140,50)`. The points are `[[30,30,1],[250,100,~1.2],[280-150*cos(...), 300+50*sin(...), ~1.2],[570,570,1]]`. `brush.set("charcoal","white",1); brush.spline(points,1)`. Then `brush.set("2H","white",1)` and 4 copies with p0.x + 55i, p1 shifted (−3i, +5i), the same p2, and p3.x − 100i. `*spline()` at 40 in gray 210, left-aligned at the moving middle point. Result: a thick white charcoal S-curve from top-left to bottom-right, a fan of four fine white pencil curves splaying toward the bottom, and a dark navy circle at the top left.

## example2/ (6 s per scene, 42 s loop; labels at (300,300) via `label(str, col=40, size=40)`)

0. **Brush rain**: the same as example/ scene 0, but the label is drawn after the stroke and `noField()` is called after each line.
1. **Mass**: `background(PAPER)` every frame, `brush.wiggle(2)`, and `sweep = 0.5 - 0.5*cos((t%6)*60)`. Three blobs, each built from 8 points at `R*(1 + 0.13 sin(a+ph1) + 0.08 sin(2a+ph2) + 0.04 sin(3a+ph3))` with seeded phases: yellow `#fcd300` R245 at (130,245), strength 1, gradient=sweep; blue `#002185` R220 at (390,425), strength 0.65; red `#ff2702` R180 at (455,205), strength 0.3. For each: `noStroke(); brush.mass("pastel", col, {precision: sweep, gradient, strength, outline:false}); beginShape(1) / vertex... / endShape(true)`. Then `noMass(); brush.set("HB","#000000",1)` and redraw the same shape as a pencil outline. `*mass()` at gray 60. Result: three huge overlapping soft pastel pebbles, cropped by the canvas edges, filled with layered directional crayon strokes, each with a thin black outline.
2. **Mass array**: `#141b24` near-black. Three "cheeses" with crayon mass, precision 0.25. Yellow `#fcd300` is a rounded 7-point blob at (140,165), contoured in `#9b1d10`. Red `#ff2702` is a pointy pentagon (235,20) (560,55) (625,260) (440,365) (230,245), gradient 0.45, contoured in `#4e93cc`. Navy `#002185` is a rounded blob at (320,465), strength 0.65, contoured in `#003c32`. Each has 6 seeded holes, which appear one by one over the scene. The holes are converted with `plot.genPol(...)` and passed to `brush.massArray([outer, ...holes])`, then outer and holes are retraced in HB. `*massArray()` at gray 235. Result: dark board, three bright crayon-filled shapes with round holes punched through them.
3. **Hatch array**: `#ffe6d4` peach. A fixed rotated rectangle (250×210 centred at (345,325), −12°) plus five shapes from one of three families, switching every 2 s: rounded pebbles, pointy polygons, and oversized ribbons that run off the canvas. All of them are converted to Polygons and hatched by **one** `hatchArray` call. The styles in turn: `HB #002185` dist 0.75 at 25° (almost solid), `watercolor #ff2702` dist 9 at 65°, and `charcoal #003c32` dist 11 at 130° with `field("seabed")`. Options `{rand:0.15, gradient:0.15, continuous:false}`. Then the outlines are drawn in `HB #003c32` 1.2. `*hatchArray()` at gray 50.
4. **Fields**: the same as example/ scene 1 (label gray 210).
5. **Stroke wheel**: the same as example/ scene 2, with seeds `33213 + i*17` and the centre circle re-seeded from `floor(t*10)`.
6. **Watercolor**: the same as example/ scene 4, but with **circles** (`brush.circle(random(600), random(600), random(40,90), 0.4)`). The label is drawn every frame in black at size 40.

## Capturing the bar

Serve the repo root (`python3 -m http.server PORT` in the p5.brush checkout) and open `/example/index.html`. Use `scripts/shot.mjs <url> out.png --frames 145,295,445,595,745,895 --selector canvas` (example2: 175,355,535,715,895,1075,1255). This takes one screenshot near the end of each scene. Scenes 0 and 4 (and example2 0 and 6) build up over time, so a late frame shows the full pile. In headless software GL the heavy scenes take about 1–5 s per frame, so a full example/ capture takes roughly 9 minutes.
