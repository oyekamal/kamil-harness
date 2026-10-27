#!/usr/bin/env node
// Headless p5 checker + frame recorder (Playwright + Chromium, software WebGL).
//
//   node render.cjs sketch.html out.png [--wait 1500] [--mouse 0.4,0.5] [--size 1280x800]
//       -> waits, optionally moves the mouse over the canvas (fractions of canvas size),
//          saves the sketch canvas (canvas.p5Canvas, last one; override with env P5_CANVAS=selector) as PNG, prints console errors, exits 1 on page errors.
//   node render.cjs sketch.html outdir/ --frames 150
//       -> deterministic recording: calls noLoop(), then redraw() once per frame and saves
//          outdir/f00000.png ... Sketch must animate from frameCount (not millis/deltaTime).
//          For frame-exact starts put `if (window.__RECORD) noLoop();` at the end of setup()
//          (draw still runs once after setup, so the first saved frame is frameCount 2).
//          Then: /usr/bin/ffmpeg -y -framerate 30 -i outdir/f%05d.png -pix_fmt yuv420p -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" out.mp4
//
// Instance-mode sketches: expose the instance as window.__p5 = p (inside the sketch fn) so
// --frames can drive it. Global-mode sketches work as-is.
// Playwright: resolved normally, else from $PLAYWRIGHT_PATH (a path to the playwright package).
const fs = require('fs');
const path = require('path');
let chromium;
try { ({ chromium } = require('playwright')); } catch {
  ({ chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright'));
}

const [, , input, out, ...rest] = process.argv;
if (!input || !out) { console.error('usage: render.cjs sketch.html out.png|outdir/ [--wait ms] [--mouse fx,fy] [--frames n] [--size WxH]'); process.exit(2); }
const opt = (k, d) => { const i = rest.indexOf('--' + k); return i >= 0 ? rest[i + 1] : d; };
const wait = +opt('wait', 1500), frames = +opt('frames', 0), mouse = opt('mouse', null);
const [vw, vh] = opt('size', '1280x800').split('x').map(Number);

(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await browser.newPage({ viewport: { width: vw, height: vh } });
  const errors = [];
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
  if (frames > 0) await page.addInitScript(() => { window.__RECORD = true; });   // sketch may call noLoop() in setup when set
  const url = /^https?:/.test(input) ? input : 'file://' + path.resolve(input);
  await page.goto(url, { waitUntil: 'load' });
  // the sketch canvas has class p5Canvas; p5 can also add hidden helper canvases (fonts, framebuffers)
  await page.locator('canvas.p5Canvas').first().waitFor({ timeout: 15000 });
  await page.waitForTimeout(100);
  const canvas = page.locator(process.env.P5_CANVAS || 'canvas.p5Canvas').last();
  const grab = () => canvas.evaluate(c => c.toDataURL('image/png'));   // works for P2D and WEBGL (p5 keeps the buffer)
  const save = (file, dataUrl) => fs.writeFileSync(file, Buffer.from(dataUrl.split(',')[1], 'base64'));

  if (frames > 0) {
    fs.mkdirSync(out, { recursive: true });
    await page.waitForTimeout(500);                                       // let async setup finish
    await page.evaluate(() => { const p = window.__p5 || window; p.noLoop(); });
    for (let i = 0; i < frames; i++) {
      await page.evaluate(() => { const p = window.__p5 || window; p.redraw(); });
      save(path.join(out, `f${String(i).padStart(5, '0')}.png`), await grab());
    }
    console.log(`wrote ${frames} frames to ${out}`);
  } else {
    if (mouse) {
      const [fx, fy] = mouse.split(',').map(Number);
      const b = await canvas.boundingBox();
      await page.mouse.move(b.x + b.width * fx, b.y + b.height * fy, { steps: 5 });
    }
    await page.waitForTimeout(wait);
    save(out, await grab());
    const size = await canvas.evaluate(c => `${c.width}x${c.height} (css ${c.clientWidth}x${c.clientHeight})`);
    console.log(`saved ${out} canvas ${size}`);
  }
  errors.forEach(e => console.error(e));
  await browser.close();
  process.exit(errors.some(e => e.startsWith('pageerror')) ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
