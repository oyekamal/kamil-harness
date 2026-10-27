#!/usr/bin/env python3
"""Free text-to-image via perchance.org, driven in a normal HEADED Chromium (needs a DISPLAY).
  Two generators, same output layout:
    (default)         perchance.org/ai-text-to-image  - 512 px, one click = 4 images (the original method)
    --site alebrije   perchance.org/alebrije-pic      - 768 px, count 1-8 (--n), styles + seed, kept working when the first page's bot check refused us
  DISPLAY=:0 python3 perchance_gen.py OUTDIR "name=prompt" ["name2=prompt2" ...] [--style "..."] [--plain]
  DISPLAY=:0 python3 perchance_gen.py OUTDIR --jobs jobs.json     # {"name": "prompt", ...}
  One generate click makes FOUR images on the page; --n 4 waits for all four and saves <name>__1..4.jpg (default --n 1 saves the first as <name>.jpg). Then pick the best.
NEVER run several windows or fresh profiles in parallel: that triggered 'Anti-bot verification failed'. One window, one profile, sequential.
Writes OUTDIR/<name>.jpg (native 512x512) and OUTDIR/sheet.png (contact sheet). Resumable: skips names that exist.
Headless is blocked by Cloudflare's bot check; headed passes on its own. Do NOT add stealth plugins. If a challenge ever
shows, solve it by hand once in the window: the profile at ~/.perchance/perchance-profile keeps the cookie."""
import base64, os, re, sys
from playwright.sync_api import sync_playwright
STYLE = ("flat vector illustration for a children's picture book, thick clean dark indigo outlines, solid flat colours, no gradients, "
         "no shading, no text, no letters, plain pure white background, one single centered subject, friendly rounded shapes, "
         "turquoise saffron red cream green palette")
args = sys.argv[1:]; style = STYLE
if "--style" in args: i = args.index("--style"); style = args[i + 1]; del args[i:i + 2]
SITE = "default"
if "--site" in args: i = args.index("--site"); SITE = args[i + 1]; del args[i:i + 2]
N = 1
if "--n" in args: i = args.index("--n"); N = int(args[i + 1]); del args[i:i + 2]
if "--plain" in args: args.remove("--plain"); style = ""
out = args[0]
if "--jobs" in args: i = args.index("--jobs"); import json; jobs = list(json.load(open(args[i + 1])).items()); del args[i:i + 2]
else: jobs = [a.split("=", 1) for a in args[1:]]
os.makedirs(out, exist_ok=True)
_SUF = "" if SITE == "default" else "-" + SITE   # one profile + one lock PER PAGE: a session on another page does not have to wait, each page still gets exactly one run at a time
PROFILE = os.environ.get("PERCHANCE_PROFILE") or os.path.expanduser(f"~/.perchance/perchance-profile{_SUF}")  # ONE profile, ONE window: parallel windows / fresh profiles trip the anti-bot check
def grab_all(pg):
    """Every distinct generated image (data URL) currently shown, across the result iframes. One generate click yields four."""
    seen = []
    for f in pg.frames:
        try:
            for r in f.evaluate("()=>[...document.images].filter(i=>i.naturalWidth>=256&&i.src.startsWith('data:image')).map(i=>i.src)"):
                if r not in seen: seen.append(r)
        except Exception: pass
    return seen
# ONE Perchance run at a time across ALL Claude sessions/projects: two simultaneous windows from one connection trip the anti-bot check.
import fcntl, time
_lock = open(os.path.expanduser(f"~/.perchance/perchance{_SUF}.lock"), "w"); _t0 = time.time()
while True:
    try: fcntl.flock(_lock, fcntl.LOCK_EX | fcntl.LOCK_NB); break
    except OSError:
        if time.time() - _t0 > int(os.environ.get("PERCHANCE_LOCK_WAIT", "3600")): sys.exit("another Perchance run is active (lock ~/.perchance/perchance.lock); giving up")
        print("waiting: another Perchance run is active ...", flush=True); time.sleep(20)
# Politeness / safety (a past block came after ~1000 generations in a day and after we kept hammering a refusing page):
#  - daily cap on prompts (PERCHANCE_DAILY_CAP, default 250), counted across ALL sessions in ~/.perchance/perchance-count-<date>.txt
#  - stop at once after 2 empty prompts in a row instead of retrying
import datetime
_cf = os.path.expanduser(f"~/.perchance/perchance{_SUF}-count-{datetime.date.today()}.txt")
def _count(): 
    try: return int(open(_cf).read().strip() or 0)
    except Exception: return 0
CAP = int(os.environ.get("PERCHANCE_DAILY_CAP", "250"))
if _count() >= CAP: sys.exit(f"daily cap reached ({_count()}/{CAP} prompts today): not touching Perchance again until tomorrow")
with sync_playwright() as p:
    # headed (headless trips Cloudflare) but placed off-screen so it does not cover the user's desktop; PERCHANCE_VISIBLE=1 shows it
    _args = [] if os.environ.get("PERCHANCE_VISIBLE") else ["--window-position=-2600,-2600", "--window-size=1280,1000"]
    ctx = p.chromium.launch_persistent_context(PROFILE, headless=False, viewport={"width": 1280, "height": 1100}, args=_args)
    pg = ctx.pages[0] if ctx.pages else ctx.new_page()
    if SITE == "alebrije":
        pg.goto("https://perchance.org/alebrije-pic", wait_until="domcontentloaded", timeout=60000)
        fr = None
        for _ in range(24):
            pg.wait_for_timeout(5000)
            c = [f for f in pg.frames if "alebrije-pic" in f.url and f != pg.main_frame]
            if c and c[0].evaluate("!!document.getElementById('promptInput')"): fr = c[0]; break
        if not fr: ctx.close(); sys.exit("alebrije-pic did not load")
        NUM = N if N in (1, 2, 3, 4, 5, 6, 8) else 4
        fr.evaluate("(n)=>{const s=document.getElementById('numInput'); s.value=String(n); s.dispatchEvent(new Event('change',{bubbles:true}))}", NUM)
        GRID = "()=>[...document.querySelectorAll('#gridEl img')].filter(i=>i.naturalWidth>=500&&i.src.startsWith('data:image')).map(i=>i.src)"
        def new_images(before):
            return [x for x in dict.fromkeys(fr.evaluate(GRID)) if x not in before]
        GAP = int(os.environ.get("PERCHANCE_GAP_MS", "5000")); WANT = NUM
    else:
        pg.goto("https://perchance.org/ai-text-to-image", wait_until="domcontentloaded", timeout=60000)
        for _ in range(24):
            pg.wait_for_timeout(5000)
            fr = [f for f in pg.frames if "perchance.org/ai-text-to-imag" in f.url and f != pg.main_frame]
            if fr: break
        fr = fr[0]
        def new_images(before): return [x for x in grab_all(pg) if x not in before]
        GAP = int(os.environ.get("PERCHANCE_GAP_MS", "2000")); WANT = 4
    empty = 0
    for name, prompt in jobs:
        labels = [name] if N == 1 else [f"{name}__{k}" for k in range(1, N + 1)]
        if all(os.path.exists(f"{out}/{l}.jpg") for l in labels): print("skip", name); continue
        if _count() >= CAP: print(f"daily cap {CAP} reached, stopping"); break
        before = set(grab_all(pg)) if SITE != "alebrije" else set(fr.evaluate(GRID)); text = f"{prompt}, {style}" if style else prompt
        if SITE == "alebrije": fr.fill("#promptInput", text); fr.click("#genTopBtn")
        else: fr.fill("input[type=text], textarea", text); fr.click("text=generate")
        got = []
        for _ in range(60):   # up to ~150 s: wait until the page has shown all the new images
            pg.wait_for_timeout(2500); got = new_images(before)
            if len(got) >= WANT: break
        for l, src in zip(labels, got): open(f"{out}/{l}.jpg", "wb").write(base64.b64decode(src.split(",", 1)[1]))
        open(_cf, "w").write(str(_count() + 1))
        print("ok" if len(got) >= len(labels) else f"PARTIAL {len(got)}/{WANT}", name, flush=True)
        empty = empty + 1 if not got else 0
        if empty >= 2: print("BLOCKED? two prompts in a row returned nothing: stopping, do not retry today", flush=True); break
        pg.wait_for_timeout(GAP)   # polite gap between prompts so the anti-bot check stays quiet
    ctx.close()
from PIL import Image, ImageDraw
fs = sorted(f for f in os.listdir(out) if f.endswith(".jpg"))
if fs:
    cols = 6; rows = (len(fs) + cols - 1) // cols; S = Image.new("RGB", (cols * 260, rows * 280), "white"); d = ImageDraw.Draw(S)
    for n, f in enumerate(fs):
        S.paste(Image.open(f"{out}/{f}").resize((250, 250)), ((n % cols) * 260 + 5, (n // cols) * 280 + 2)); d.text(((n % cols) * 260 + 8, (n // cols) * 280 + 255), f[:-4][:36], fill="black")
    S.save(f"{out}/sheet.png")
