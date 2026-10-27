#!/usr/bin/env python3
"""Rung-3 gate for a single self-contained HTML explainer.

  python3 html_check.py page.html [--out DIR] [--csp] [--size 720x460]

Loads the page offline in headless Chromium (every network request is blocked and reported),
optionally under a strict sandbox CSP (--csp), then:
  1. errors:   console errors, uncaught exceptions, any network request, external <script>/<link>/<img>
  2. layout:   screenshots at 1280 wide and 390 wide (phone); horizontal overflow at 390 is an error;
               --size WxH also checks the page fits that box (e.g. an embedded interactive = 720x460)
  3. controls: drives every <input type=range|number>, <select>, tab and <details> and checks that some
               visible text changes when a control moves (a slider that changes nothing = error)
  4. numbers:  if the page defines window.model(params) and window.checks = [{input:{..}, expect:{..},
               tol:0.005, source:"..."}], every check is run against model(); each miss is an error.
               This is the "numbers match the primary source" gate.
Exit 1 on any error. Screenshots go to --out (default: next to the page).
"""
import argparse, json, os, re, sys
from playwright.sync_api import sync_playwright

CSP = "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; font-src data:"


def static_checks(html):
    errs = []
    for m in re.finditer(r"<(script|link|img|iframe|source|video|audio)\b[^>]*\b(src|href)\s*=\s*[\"']?(https?:|//)[^\"' >]+", html, re.I):
        errs.append(f"external dependency: {m.group(0)[:100]}")
    if re.search(r"@import\s+url\(\s*[\"']?https?:", html): errs.append("external CSS @import")
    if re.search(r"\bfetch\(\s*[\"']https?:|import\(\s*[\"']https?:", html): errs.append("runtime fetch/import of a URL")
    return errs


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("file"); ap.add_argument("--out"); ap.add_argument("--csp", action="store_true")
    ap.add_argument("--size", help="WxH box the page must fit, e.g. 720x460")
    a = ap.parse_args()
    path = os.path.abspath(a.file); out = a.out or os.path.dirname(path); os.makedirs(out, exist_ok=True)
    html = open(path, encoding="utf-8").read()
    errs, warns = static_checks(html), []
    kb = len(html.encode()) / 1024
    if kb > 1500: warns.append(f"page is {kb:.0f} KB (keep under ~1.5 MB)")
    if a.csp:
        html = html.replace("<head>", f'<head><meta http-equiv="Content-Security-Policy" content="{CSP}">', 1) if "<head>" in html else \
            f'<meta http-equiv="Content-Security-Policy" content="{CSP}">' + html
    stem = os.path.splitext(os.path.basename(path))[0]
    with sync_playwright() as p:
        b = p.chromium.launch()
        for width, height, tag in ((1280, 900, "desktop"), (390, 844, "phone")):
            ctx = b.new_context(viewport={"width": width, "height": height})
            pg = ctx.new_page(); log = []
            pg.on("console", lambda m, log=log: m.type == "error" and log.append("console: " + m.text[:200]))
            pg.on("pageerror", lambda e, log=log: log.append("exception: " + str(e)[:200]))
            def block(route, request=None, log=log):
                u = route.request.url
                if u.startswith(("data:", "blob:", "about:")): return route.continue_()
                log.append("network request: " + u[:120]); route.abort()
            ctx.route("**/*", block)
            pg.set_content(html, wait_until="load"); pg.wait_for_timeout(600)
            pg.screenshot(path=os.path.join(out, f"{stem}.{tag}.png"), full_page=True)
            if tag == "phone":
                sw = pg.evaluate("document.documentElement.scrollWidth")
                if sw > width + 1: errs.append(f"horizontal overflow on phone: page is {sw}px wide in a {width}px viewport")
            if tag == "desktop":
                inv = pg.evaluate("""() => ({ranges: document.querySelectorAll('input[type=range],input[type=number]').length,
                    selects: document.querySelectorAll('select').length, details: document.querySelectorAll('details').length,
                    tabs: document.querySelectorAll('[role=tab]').length, buttons: document.querySelectorAll('button').length,
                    svg: document.querySelectorAll('svg').length, canvas: document.querySelectorAll('canvas').length,
                    toc: !!document.querySelector('nav a[href^="#"]'), model: typeof window.model === 'function',
                    checks: Array.isArray(window.checks) ? window.checks.length : 0})""")
                print("inventory:", json.dumps(inv))
                if not (inv["ranges"] or inv["selects"] or inv["buttons"]): warns.append("no controls: the page is read-only (rung 3 should let the reader change something)")
                # drive controls: does visible text change?
                moved = pg.evaluate("""async () => {
                  const txt = () => document.body.innerText; const res = [];
                  for (const el of document.querySelectorAll('input[type=range],input[type=number],select')) {
                    const before = txt();
                    if (el.tagName === 'SELECT') { el.selectedIndex = (el.selectedIndex + 1) % el.options.length; }
                    else { const lo = +el.min || 0, hi = el.max === '' ? lo + 10 : +el.max; el.value = String(lo + (hi - lo) * 0.83); }
                    el.dispatchEvent(new Event('input', {bubbles: true})); el.dispatchEvent(new Event('change', {bubbles: true}));
                    await new Promise(r => setTimeout(r, 120));
                    res.push({id: el.id || el.name || el.outerHTML.slice(0, 40), changed: txt() !== before});
                  }
                  for (const t of document.querySelectorAll('[role=tab],details>summary')) { t.click(); await new Promise(r => setTimeout(r, 60)); }
                  return res; }""")
                for m in moved:
                    if not m["changed"]: errs.append(f"control {m['id']!r} moved but no visible text changed (readout not wired?)")
                pg.screenshot(path=os.path.join(out, f"{stem}.desktop-after.png"), full_page=True)
                if inv["model"] and inv["checks"]:
                    res = pg.evaluate("""() => window.checks.map(c => { let got; try { got = window.model(c.input); } catch (e) { return {c, err: String(e)}; }
                        const bad = Object.entries(c.expect).filter(([k, v]) => { const g = got[k]; if (typeof v === 'number') {
                          const tol = c.tol ?? 0.005; return !(Math.abs(g - v) <= Math.max(Math.abs(v) * tol, c.abs ?? 1e-9)); } return g !== v; });
                        return {c, got, bad}; })""")
                    for r in res:
                        if r.get("err"): errs.append(f"model() threw on {r['c']['input']}: {r['err']}")
                        elif r["bad"]: errs.append(f"model{json.dumps(r['c']['input'])} = {json.dumps({k: r['got'].get(k) for k, _ in r['bad']})}, source says {json.dumps(dict(r['bad']))} ({r['c'].get('source', 'no source')})")
                        else: print(f"check ok: model{json.dumps(r['c']['input'])} matches {json.dumps(r['c']['expect'])}  [{r['c'].get('source', '')}]")
                elif inv["ranges"]: warns.append("sliders but no window.model + window.checks: numbers on screen are unchecked")
                if a.size:
                    bw, bh = (int(v) for v in a.size.lower().split("x"))
                    pg.set_viewport_size({"width": bw, "height": bh}); pg.wait_for_timeout(200)
                    dims = pg.evaluate("[document.documentElement.scrollWidth, document.documentElement.scrollHeight]")
                    if dims[0] > bw or dims[1] > bh: errs.append(f"does not fit {a.size}: content is {dims[0]}x{dims[1]}")
                    pg.screenshot(path=os.path.join(out, f"{stem}.box.png"))
            errs += sorted(set(log)); ctx.close()
        b.close()
    for e in errs: print("ERROR ", e)
    for w in warns: print("warn  ", w)
    print("screenshots:", ", ".join(sorted(f for f in os.listdir(out) if f.startswith(stem + ".") and f.endswith(".png"))), "in", out)
    print("RESULT:", "FAIL" if errs else "PASS")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
