# p5.js 2.x WEBGL basics

`createCanvas(w, h, WEBGL)`. Instance mode: `p.createCanvas(w, h, p.WEBGL)`.

## Coordinate system (the #1 mistake)
- Origin (0,0,0) is the CENTRE of the canvas, x right, y DOWN, z toward the viewer.
- 2D code ported to WEBGL is offset by half a canvas: add `translate(-width/2, -height/2)` at the
  top of `draw()` to get top-left origin back, and convert mouse: `mouseX - width/2`, `mouseY - height/2`.
- Rotations follow `angleMode()`; `rotateX/rotateY/rotateZ(a)`, `rotate(a, [x,y,z])`.
- Default camera: perspective, eye at z = `(height/2) / tan(PI/6)` looking at the origin, so a
  shape at z=0 with size `width` exactly spans the canvas.

## Primitives (centred on the current origin)
`plane(w[,h])` `box(w[,h,d])` `sphere(r[,detailX,detailY])` `ellipsoid(rx,ry,rz)` `cylinder(r,h)`
`cone(r,h)` `torus(r,tubeR)`. 2D shapes, `beginShape()/vertex(x,y,z)/endShape()`, `line`, `point`
work in 3D too. `box()` with no args = 50-unit cube.

## Camera
`orbitControl([sx, sy, sz, {freeRotation}])` call every frame in `draw()`: drag rotates, wheel zooms,
right-drag pans. `camera(ex,ey,ez, cx,cy,cz, ux,uy,uz)`; `perspective(fovy, aspect, near, far)`;
`ortho()` for flat orthographic diagrams; `cam = createCamera(); cam.setPosition(..); cam.lookAt(..)`.
`debugMode()` draws a grid + axes while building a scene.

## Lights and materials (lights are reset every frame: call them inside draw)
- `lights()` = default ambient + directional. Or `ambientLight(v)`, `directionalLight(r,g,b, dx,dy,dz)`,
  `pointLight(r,g,b, x,y,z)`, `spotLight(...)`, `noLights()`.
- `normalMaterial()` (rainbow by face direction, ignores lights, great for debugging),
  `fill(c)` (lit colour), `ambientMaterial(c)`, `emissiveMaterial(c)` (glows), `specularMaterial(c)` +
  `shininess(1..)` for highlights, `metalness(n)`.
- Textures: `texture(img | graphics | framebuffer | video)`, `textureMode(NORMAL)` for 0..1 uv,
  `textureWrap(REPEAT)`.
- `noStroke()` for anything with many faces: WEBGL strokes are costly and look noisy on spheres.

## Building geometry once (big performance win)
```js
let shape;
function setup() {
  createCanvas(700, 400, WEBGL);
  shape = buildGeometry(() => {      // draws are captured into ONE p5.Geometry, fills/colours kept
    fill('tomato'); sphere(40);
    translate(60, 0, 0); fill('black'); box(20);
  });
  shape.normalize();                  // centre + scale to a standard size
}
function draw() { background(255); noStroke(); lights(); model(shape); }  // stroke ON at model() time = wireframe edges (verified)
// Replacing it: freeGeometry(shape); shape = buildGeometry(...)   (frees GPU buffers)
```
Model files: `m = await loadModel('a.obj', true)` (true = normalize) in `async setup`, then `model(m)`.
OBJ/STL only. Offline: no network in a sandbox, so build geometry in code instead.

## Text in WEBGL
Requires a loaded font: `font = await loadFont(url_or_dataURL); textFont(font); textSize(32); text('Hi', 0, 0)`.
Without it p5 throws "WEBGL: you must load and set a font before drawing text".
3D letters: `font.textToModel('Hi', x, y, w, h, { extrude: 20 })` → geometry for `model()`.

## Offscreen + effects
- `fb = createFramebuffer()`; `fb.begin(); ...draw...; fb.end(); image(fb, -width/2, -height/2)` (or `texture(fb)`).
  Faster than `createGraphics(w, h, WEBGL)` and keeps depth.
- `filter(BLUR, 4)`, `filter(GRAY)` etc. run as GPU shaders in WEBGL.
- Custom shaders: `createShader(vert, frag)`, `createFilterShader(frag)` + `filter(sh)`;
  2.x: `baseMaterialShader().modify({...})`, `buildFilterShader(fn)` (p5.strands, shaders written in JS).
  `shader(s)` applies to fills only; strokes use `strokeShader`, images `imageShader`.

## Headless notes
Chromium headless renders WEBGL via SwiftShader: pass
`--use-gl=angle --use-angle=swiftshader --enable-unsafe-swiftshader` (scripts/render.cjs does).
Plain `chromium.launch()` also works for simple scenes but logs "GPU stall due to
ReadPixels" warnings (warnings, not errors). Capture the canvas with `canvas.toDataURL()`: p5 WEBGL
keeps the drawing buffer, and element screenshots of a busy WEBGL page can time out.
