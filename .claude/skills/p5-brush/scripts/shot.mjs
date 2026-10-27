// Screenshot a p5.brush page in headless Chromium (software WebGL2 via SwiftShader).
//
//   node shot.mjs <url> <out.png> [--selector 'canvas'] [--frames 145,295,...] [--wait-done]
//
// --frames  : p5 build only. Injects a p5 addon right after the p5 <script> tag that
//             calls noLoop() at each listed frameCount; one PNG per frame: <out>-f<frame>.png.
// --wait-done: wait for window.__done === true (set it at the end of a static drawing), else waits 4 s.
// Playwright is imported from PLAYWRIGHT_MJS, else the normal `@playwright/test` package.
// Software GL is slow: heavy scenes take seconds per frame, so give it time (timeouts are 10 min).
const PW = process.env.PLAYWRIGHT_MJS || '@playwright/test';
const { chromium } = await import(PW);

const args = process.argv.slice(2);
const [url, out] = args;
const opt = (k) => { const i = args.indexOf(k); return i > 0 ? args[i + 1] : undefined; };
const selector = opt('--selector') || 'canvas';
const frames = (opt('--frames') || '').split(',').filter(Boolean).map(Number);
const waitDone = args.includes('--wait-done');

const hook = `window.__targets=${JSON.stringify(frames)};window.__paused=0;
p5.registerAddon((p5c, fn, lc) => { lc.postdraw = function () {
  if (window.__targets.includes(this.frameCount)) { window.__paused = this.frameCount; this.noLoop();
    window.__resume = () => { window.__paused = 0; this.loop(); }; } }; });`;

const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 900, height: 900 } });
page.on('console', (m) => { if (['error', 'warning'].includes(m.type()) && !/GPU stall|GL Driver/.test(m.text())) console.log('[console]', m.type(), m.text().slice(0, 240)); });
page.on('pageerror', (e) => console.log('[pageerror]', e.message));
if (frames.length) {
  await page.route('**/__hook.js', (r) => r.fulfill({ contentType: 'application/javascript', body: hook }));
  await page.route(url, async (r) => {
    const resp = await r.fetch();
    let html = await resp.text();
    // insert the hook right after the p5 <script> tag (p5 must exist, the sketch must not have started)
    html = html.replace(/<script[^>]+src="[^"]*\/p5(@[^/"]*)?\/lib\/p5(\.min)?\.js"[^>]*><\/script>|<script[^>]+src="[^"]*p5(\.min)?\.js"[^>]*><\/script>/, '$&<script src="/__hook.js"></script>');
    await r.fulfill({ response: resp, body: html });
  });
}
await page.goto(url);
const snap = async (file) => {
  const bb = await page.locator(selector).first().boundingBox();
  await page.screenshot({ path: file, clip: bb, timeout: 600000 });
  console.log('saved', file);
};
if (frames.length) {
  for (const f of frames) {
    await page.waitForFunction((n) => window.__paused === n, f, { timeout: 600000, polling: 250 });
    await snap(out.replace(/\.png$/, `-f${f}.png`));
    await page.evaluate(() => window.__resume());
  }
} else {
  if (waitDone) await page.waitForFunction(() => window.__done === true, null, { timeout: 600000 });
  else await page.waitForTimeout(4000);
  await page.waitForTimeout(800);
  await snap(out);
}
await browser.close();
