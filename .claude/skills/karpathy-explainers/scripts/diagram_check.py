#!/usr/bin/env python3
"""Rung-2 diagram gate: structure lint + render to PNG so you can LOOK at it.

  python3 diagram_check.py diagram.svg  [--png out.png]
  python3 diagram_check.py diagram.mmd  [--png out.png]   # Mermaid, rendered offline in headless Chromium

SVG convention this checks (write diagrams this way):
  <svg viewBox=...> <title>..</title> <desc>..</desc>
  <g class="node" id="anode"><rect .../><text>Zn anode</text></g>        every box is a labelled node
  <g class="edge" data-step="1" data-from="anode" data-to="wire">           every arrow is numbered
      <path ... marker-end="url(#arrow)"/><text>1</text> <text>e⁻ leave Zn</text></g>
  <g class="node uncertain" data-why="...">  nodes/edges the model is unsure of (dashed + listed)
Errors: external refs/scripts, node without text, edge without data-step or a visible number,
        steps not 1..N, edge data-from/data-to pointing at no node, label wider than its box,
        text smaller than 12px. Mermaid: parse/render errors, unnumbered edges with labels.
"""
import argparse, os, re, sys, xml.etree.ElementTree as ET

NS = "{http://www.w3.org/2000/svg}"
MERMAID_JS = [os.path.expanduser(p) for p in (
    os.environ.get("MERMAID_JS", "~/.cache/karpathy-explainers/mermaid.min.js"),
    "~/.cache/karpathy-explainers/mermaid.min.js")]


def tag(e): return e.tag.replace(NS, "")


def texts(e): return " ".join("".join(t.itertext()).strip() for t in e.iter() if tag(t) == "text").strip()


def fnum(v, d=0.0):
    try: return float(re.sub(r"[a-z%]+$", "", str(v)))
    except (TypeError, ValueError): return d


def check_svg(path):
    errs, warns = [], []
    src = open(path).read()
    if re.search(r"<script|javascript:|@import|(href|src)\s*=\s*[\"']https?:", src, re.I): errs.append("external reference or script in SVG")
    root = ET.fromstring(src)
    if not root.get("viewBox"): errs.append("no viewBox (diagram will not scale)")
    if root.find(f"{NS}title") is None: warns.append("no <title> (screen readers, alt text)")
    groups = list(root.iter(f"{NS}g"))
    nodes = [g for g in groups if "node" in (g.get("class") or "").split()]
    edges = [g for g in groups if "edge" in (g.get("class") or "").split()]
    if not nodes: errs.append('no <g class="node"> groups found (label every box as a node)')
    ids = {g.get("id") for g in nodes}
    for g in nodes:
        lab = texts(g)
        if not lab: errs.append(f"node {g.get('id')!r} has no label text")
        r = next((c for c in g if tag(c) in ("rect", "ellipse", "circle", "polygon", "path")), None)
        if r is not None and tag(r) == "rect":
            w = fnum(r.get("width"))
            for t in g.iter(f"{NS}text"):
                fs = fnum(t.get("font-size") or re.search(r"font-size:\s*([\d.]+)", t.get("style") or "font-size:16").group(1), 16)
                longest = max((len(x) for x in "".join(t.itertext()).split("\n")), default=0)
                if fs < 12: errs.append(f"node {g.get('id')!r}: font-size {fs} < 12")
                if longest * fs * 0.56 > w - 8: warns.append(f"node {g.get('id')!r}: label '{''.join(t.itertext())[:30]}' may overflow box (~{longest * fs * 0.56:.0f}px text in {w:.0f}px box)")
        if "uncertain" in (g.get("class") or "") and not g.get("data-why"): errs.append(f"uncertain node {g.get('id')!r} has no data-why")
    steps = []
    for g in edges:
        st = g.get("data-step")
        if not st or not st.isdigit(): errs.append(f"edge {texts(g)[:30]!r} has no numeric data-step"); continue
        steps.append(int(st))
        if st not in re.findall(r"\d+", texts(g)): errs.append(f"edge step {st}: number not drawn on the arrow")
        for k in ("data-from", "data-to"):
            if g.get(k) and g.get(k) not in ids: errs.append(f"edge step {st}: {k}={g.get(k)!r} is not a node id")
        if not any(c.get("marker-end") for c in g.iter()): warns.append(f"edge step {st}: no marker-end (arrow head)")
    if steps and sorted(steps) != list(range(1, len(steps) + 1)):
        warns.append(f"edge steps are {sorted(steps)}, expected 1..{len(steps)} (fine only if two arrows share a step on purpose)")
    unc = [g for g in groups if "uncertain" in (g.get("class") or "")]
    print(f"{len(nodes)} nodes, {len(edges)} numbered edges, {len(unc)} marked uncertain")
    return errs, warns


def render_svg(path, png):
    import cairosvg
    cairosvg.svg2png(url=path, write_to=png, output_width=1400, background_color="white")


def check_mmd(path, png):
    errs, warns = [], []
    src = open(path).read()
    if re.search(r"click\s+\w+|<script|javascript:", src, re.I): errs.append("mermaid source may not script or link")
    labelled = re.findall(r"--\s*\"?([^\"|>-]+)\"?\s*-->|-->\|([^|]+)\|", src)
    for a, b in labelled:
        lab = (a or b).strip()
        if lab and not re.match(r"^\(?\d+[).:]?", lab): warns.append(f"edge label '{lab[:30]}' has no step number (write '1. ...')")
    js = next((p for p in MERMAID_JS if os.path.exists(p)), None)
    if not js:
        errs.append("no local mermaid.min.js; fetch once: curl -sL https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js "
                    "-o ~/.cache/karpathy-explainers/mermaid.min.js"); return errs, warns
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1400, "height": 900})
        pg.set_content("<html><body style='background:#fff'><div id=o></div></body></html>")
        pg.add_script_tag(path=js)
        res = pg.evaluate("""async (s) => { try { mermaid.initialize({startOnLoad:false, securityLevel:'strict'});
            const {svg} = await mermaid.render('d', s); document.getElementById('o').innerHTML = svg; return {ok:true, svg}; }
            catch (e) { return {ok:false, err: String(e.message || e)}; } }""", src)
        if not res["ok"]: errs.append("mermaid render error: " + res["err"][:300])
        else:
            open(os.path.splitext(png)[0] + ".rendered.svg", "w").write(res["svg"])
            pg.locator("#o svg").screenshot(path=png)
        b.close()
    return errs, warns


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("file"); ap.add_argument("--png")
    a = ap.parse_args(); png = a.png or os.path.splitext(a.file)[0] + ".png"
    if a.file.endswith(".mmd"): errs, warns = check_mmd(a.file, png)
    else:
        errs, warns = check_svg(a.file)
        try: render_svg(a.file, png)
        except Exception as e: errs.append(f"SVG does not render: {e}")
    for e in errs: print("ERROR ", e)
    for w in warns: print("warn  ", w)
    if os.path.exists(png): print("PNG:", png, "<- open it with Read and look before you ship")
    print("RESULT:", "FAIL" if errs else "PASS")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
