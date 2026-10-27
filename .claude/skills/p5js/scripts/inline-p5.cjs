#!/usr/bin/env node
// Make a p5 sketch page self-contained for a no-network sandbox (sandboxed iframe interactives,
// CSP default-src 'none'): replaces the p5 CDN <script src> with the library inlined, and adds a
// guard so p5 does not register devicemotion/deviceorientation listeners (in a sandboxed iframe
// Chromium logs those as console ERRORS, which can fail a host's checks).
//
//   node inline-p5.cjs in.html out.html [--version 2.3.4]
//
// Library source, first hit wins: $P5_MIN path, ~/.cache/p5js/p5@<v>.min.js, else downloaded once
// from cdn.jsdelivr.net into that cache. Output is ~1 MB (p5.min.js is ~990 KB).
const fs = require('fs');
const path = require('path');
const https = require('https');

const [, , input, output, ...rest] = process.argv;
if (!input || !output) { console.error('usage: inline-p5.cjs in.html out.html [--version 2.3.4]'); process.exit(2); }
const vi = rest.indexOf('--version');
const version = vi >= 0 ? rest[vi + 1] : '2.3.4';
const cache = path.join(process.env.HOME, '.cache/p5js', `p5@${version}.min.js`);

const GUARD = "<script>{const a=EventTarget.prototype.addEventListener;EventTarget.prototype.addEventListener=function(t,...r){if(t==='devicemotion'||t==='deviceorientation')return;return a.call(this,t,...r)}}</script>";

function get(url) {
  return new Promise((res, rej) => https.get(url, r => {
    if (r.statusCode >= 300 && r.statusCode < 400 && r.headers.location) return res(get(new URL(r.headers.location, url).href));
    if (r.statusCode !== 200) return rej(new Error(`${url} -> ${r.statusCode}`));
    const chunks = []; r.on('data', c => chunks.push(c)); r.on('end', () => res(Buffer.concat(chunks).toString('utf8')));
  }).on('error', rej));
}

(async () => {
  let lib;
  if (process.env.P5_MIN) lib = fs.readFileSync(process.env.P5_MIN, 'utf8');
  else if (fs.existsSync(cache)) lib = fs.readFileSync(cache, 'utf8');
  else {
    lib = await get(`https://cdn.jsdelivr.net/npm/p5@${version}/lib/p5.min.js`);
    fs.mkdirSync(path.dirname(cache), { recursive: true });
    fs.writeFileSync(cache, lib);
  }
  const inline = GUARD + '<script>' + lib.replace(/<\/script/gi, '<\\/script') + '</script>';
  let html = fs.readFileSync(input, 'utf8');
  const tag = /<script[^>]+src=["'][^"']*p5(@[\d.]+)?(\/lib)?\/p5(\.min)?\.js["'][^>]*>\s*<\/script>/i;
  if (tag.test(html)) html = html.replace(tag, () => inline);
  else if (/<head[^>]*>/i.test(html)) html = html.replace(/<head[^>]*>/i, m => m + inline);
  else html = inline + html;
  if (/<script[^>]+src=/i.test(html)) console.error('warning: other external <script src> tags remain; they will be blocked offline');
  fs.writeFileSync(output, html);
  console.log(`wrote ${output} (${(html.length / 1024).toFixed(0)} KB, p5 ${version})`);
})().catch(e => { console.error(e.message); process.exit(1); });
