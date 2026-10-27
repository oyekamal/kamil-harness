#!/usr/bin/env python3
"""Code-drawn explainer video engine (rung 4). No manim, no diffusion.

pycairo + Pango draw every frame, matplotlib mathtext draws formulas (no LaTeX needed),
raw BGRA frames are piped to /usr/bin/ffmpeg, narration comes from ElevenLabs (if
ELEVENLABS_API_KEY is set) or the free offline flite voice built into ffmpeg.

Usage:
  python3 explainer_video.py SCENE.py --out out.mp4 --script-only   # 1. write script.md, review it
  python3 explainer_video.py SCENE.py --out out.mp4 --stills DIR     # 2. render + one PNG per beat
  also writes OUT.vtt (captions) and OUT.script.md (timed script + claims checklist)
  options: --no-audio  --no-captions  --tts flite|eleven|none  --fps 30

A scene file defines BEATS = [Beat(say=..., draw=fn, claims=[...], source=...), ...]
and fn(p, t, T): p is a Pen, t = seconds into the beat, T = beat length.
Beat length = narration length + hold, so picture and voice stay in sync.
"""
import argparse, functools, hashlib, importlib.util, io, json, math, os, shutil, subprocess, sys, tempfile, urllib.request, wave
from dataclasses import dataclass, field

import cairo
import gi
gi.require_version("Pango", "1.0"); gi.require_version("PangoCairo", "1.0")
from gi.repository import Pango, PangoCairo  # noqa: E402

FFMPEG = shutil.which("ffmpeg") or "/usr/bin/ffmpeg"
FFPROBE = shutil.which("ffprobe") or "/usr/bin/ffprobe"
W, H = 1280, 720
# 3b1b-like palette: dark ground, few strong colours, one colour = one quantity for the whole video
C = dict(bg="#14171c", fg="#ece8dc", dim="#8a8f98", blue="#58c4dd", yellow="#ffd75e",
         green="#83c167", red="#fc6255", teal="#5cd0b3", purple="#9a72ac", grid="#2a2f38")


def rgb(h, a=1.0):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (a,)


def ease(x):  # smoothstep, 0..1 -> 0..1
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)


def seg(t, a, b):
    """Eased progress of an action that runs from second a to second b of the beat."""
    return 1.0 if b <= a else ease((t - a) / (b - a))


@dataclass
class Beat:
    say: str                      # narration, one idea, STE100 style
    draw: object                  # fn(p, t, T)
    claims: list = field(default_factory=list)  # every fact shown or spoken -> checked vs source
    source: str = ""              # where the claims come from (book page, URL)
    min_dur: float = 2.0
    hold: float = 0.6             # silence after the voice so the picture can land


class Pen:
    def __init__(self, ctx):
        self.c = ctx

    def clear(self, color=C["bg"]):
        self.c.set_source_rgba(*rgb(color)); self.c.paint()

    def grid(self, step=80, color=C["grid"]):
        c = self.c; c.set_source_rgba(*rgb(color)); c.set_line_width(1)
        for x in range(0, W, step): c.move_to(x, 0); c.line_to(x, H)
        for y in range(0, H, step): c.move_to(0, y); c.line_to(W, y)
        c.stroke()

    def text(self, s, x, y, size=34, color=C["fg"], alpha=1.0, anchor="l", bold=False, width=None, markup=False):
        """Pango text. markup=True allows <sub>, <sup>, <i>, <b>, <span foreground=...>."""
        if alpha <= 0: return (0, 0)
        lay = PangoCairo.create_layout(self.c)
        fd = Pango.FontDescription(f"DejaVu Sans {'Bold ' if bold else ''}{size * 0.75:.1f}")
        lay.set_font_description(fd)
        if width: lay.set_width(int(width * Pango.SCALE)); lay.set_wrap(Pango.WrapMode.WORD)
        (lay.set_markup if markup else lay.set_text)(s, -1)
        if anchor == "c": lay.set_alignment(Pango.Alignment.CENTER)
        tw, th = (v / Pango.SCALE for v in lay.get_size())
        if width and anchor == "c": tw = width
        ox = {"l": 0, "c": -tw / 2, "r": -tw}[anchor]
        self.c.move_to(x + ox, y - th / 2)
        self.c.set_source_rgba(*rgb(color, alpha)); PangoCairo.show_layout(self.c, lay)
        return (tw, th)

    def math(self, tex, x, y, size=44, color=C["fg"], alpha=1.0, anchor="c"):
        """Formula via matplotlib mathtext, e.g. r'$E = E^\\circ - \\frac{RT}{nF}\\ln Q$'."""
        if alpha <= 0: return
        surf = _math_surface(tex, size, color)
        w, h = surf.get_width(), surf.get_height()
        ox = {"l": 0, "c": -w / 2, "r": -w}[anchor]
        self.c.set_source_surface(surf, x + ox, y - h / 2); self.c.paint_with_alpha(alpha)

    def line(self, x1, y1, x2, y2, color=C["fg"], width=4, progress=1.0, alpha=1.0, dash=None):
        if progress <= 0: return
        c = self.c; c.set_source_rgba(*rgb(color, alpha)); c.set_line_width(width); c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.set_dash(dash or [])
        c.move_to(x1, y1); c.line_to(x1 + (x2 - x1) * progress, y1 + (y2 - y1) * progress); c.stroke(); c.set_dash([])

    def arrow(self, x1, y1, x2, y2, color=C["fg"], width=4, progress=1.0, num=None, label=None, alpha=1.0):
        """Arrow drawn on with progress; num = step number badge at the middle (diagram rule: numbered arrows)."""
        if progress <= 0: return
        ex, ey = x1 + (x2 - x1) * progress, y1 + (y2 - y1) * progress
        self.line(x1, y1, ex, ey, color, width, 1.0, alpha)
        ang = math.atan2(ey - y1, ex - x1); L = 16
        c = self.c; c.set_source_rgba(*rgb(color, alpha))
        c.move_to(ex, ey)
        c.line_to(ex - L * math.cos(ang - 0.45), ey - L * math.sin(ang - 0.45))
        c.line_to(ex - L * math.cos(ang + 0.45), ey - L * math.sin(ang + 0.45)); c.close_path(); c.fill()
        mx, my = (x1 + ex) / 2, (y1 + ey) / 2
        if num is not None and progress > 0.5:
            c.arc(mx, my, 16, 0, 2 * math.pi); c.set_source_rgba(*rgb(C["bg"])); c.fill_preserve()
            c.set_source_rgba(*rgb(color, alpha)); c.set_line_width(2.5); c.stroke()
            self.text(str(num), mx, my, 20, color, alpha, "c", bold=True)
        if label and progress > 0.9:
            self.text(label, mx, my - 30, 22, color, alpha, "c")

    def box(self, x, y, w, h, label="", color=C["fg"], alpha=1.0, fill=None, size=28, progress=1.0):
        """Labelled box; every box carries its real name (diagram rule)."""
        if progress <= 0 or alpha <= 0: return
        c = self.c; r = 12
        c.new_sub_path()
        for cx, cy, a0 in ((x + w - r, y + r, -90), (x + w - r, y + h - r, 0), (x + r, y + h - r, 90), (x + r, y + r, 180)):
            c.arc(cx, cy, r, math.radians(a0), math.radians(a0 + 90))
        c.close_path()
        if fill: c.set_source_rgba(*rgb(fill, alpha * 0.25 * progress)); c.fill_preserve()
        c.set_source_rgba(*rgb(color, alpha * progress)); c.set_line_width(3); c.stroke()
        if label: self.text(label, x + w / 2, y + h / 2, size, color, alpha * progress, "c", width=w - 16, markup=True)

    def dot(self, x, y, r=9, color=C["yellow"], alpha=1.0):
        self.c.arc(x, y, r, 0, 2 * math.pi); self.c.set_source_rgba(*rgb(color, alpha)); self.c.fill()

    def axes(self, x, y, w, h, xr, yr, xlabel="", ylabel="", xticks=(), yticks=(), progress=1.0, color=C["dim"]):
        """Draws axes with box (x, y, w, h) in pixels; returns map(xv, yv) -> pixels."""
        X = lambda v: x + (v - xr[0]) / (xr[1] - xr[0]) * w
        Y = lambda v: y + h - (v - yr[0]) / (yr[1] - yr[0]) * h
        self.line(x, y + h, x + w, y + h, color, 2.5, progress); self.line(x, y + h, x, y, color, 2.5, progress)
        a = ease(progress)
        for tv in xticks:
            self.line(X(tv), y + h, X(tv), y + h + 8, color, 2, a); self.text(_fmt(tv), X(tv), y + h + 26, 20, color, a, "c")
        for tv in yticks:
            self.line(x - 8, Y(tv), x, Y(tv), color, 2, a); self.text(_fmt(tv), x - 14, Y(tv), 20, color, a, "r")
        if xlabel: self.text(xlabel, x + w, y + h + 56, 24, C["fg"], a, "r", markup=True)
        if ylabel: self.text(ylabel, x, y - 28, 24, C["fg"], a, "l", markup=True)
        return lambda xv, yv: (X(xv), Y(yv))

    def plot(self, m, fn, x0, x1, color=C["blue"], width=4, progress=1.0, n=200):
        if progress <= 0: return
        c = self.c; c.set_source_rgba(*rgb(color)); c.set_line_width(width); c.set_line_join(cairo.LINE_JOIN_ROUND)
        xe = x0 + (x1 - x0) * progress
        for i in range(n + 1):
            xv = x0 + (xe - x0) * i / n; px, py = m(xv, fn(xv))
            (c.move_to if i == 0 else c.line_to)(px, py)
        c.stroke()


def _fmt(v):
    return str(int(v)) if float(v).is_integer() else f"{v:g}"


@functools.lru_cache(maxsize=256)
def _math_surface(tex, size, color):
    import matplotlib; matplotlib.use("Agg")
    from matplotlib import mathtext  # noqa
    from matplotlib.figure import Figure
    fig = Figure(figsize=(0.01, 0.01), dpi=100)
    fig.text(0, 0, tex, fontsize=size * 0.75, color=color, math_fontfamily="cm")
    buf = io.BytesIO(); fig.savefig(buf, format="png", transparent=True, bbox_inches="tight", pad_inches=0.04, dpi=100)
    buf.seek(0); return cairo.ImageSurface.create_from_png(buf)


# ---------------- narration ----------------
def _wav_len(path):
    with wave.open(path) as w: return w.getnframes() / w.getframerate()


def narrate(text, out_wav, engine):
    """ElevenLabs if key present, else ffmpeg's built-in flite (offline, free). Output: 44.1 kHz mono s16 wav."""
    tmp = out_wav + ".src"
    if engine == "eleven":
        key = os.environ["ELEVENLABS_API_KEY"]
        voice = os.environ.get("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128",
            data=json.dumps({"text": text, "model_id": os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")}).encode(),
            headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
        with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f: f.write(r.read())
        src = ["-i", tmp]
    else:
        tf = out_wav + ".txt"
        open(tf, "w").write(text)
        src = ["-f", "lavfi", "-i", f"flite=textfile={tf}:voice={os.environ.get('FLITE_VOICE', 'slt')}"]
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", *src, "-ar", "44100", "-ac", "1", "-sample_fmt", "s16", out_wav], check=True)


def _concat_audio(parts, durs, out):
    with wave.open(out, "wb") as o:
        o.setnchannels(1); o.setsampwidth(2); o.setframerate(44100)
        for p, d in zip(parts, durs):
            need = int(d * 44100); got = 0
            if p:
                with wave.open(p) as w: fr = w.readframes(min(w.getnframes(), need)); o.writeframes(fr); got = len(fr) // 2
            o.writeframes(b"\x00\x00" * max(0, need - got))


# ---------------- main ----------------
def load_scene(path):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    spec = importlib.util.spec_from_file_location("scene", path); mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod); return mod


def write_script(mod, durs, path):
    t, out = 0.0, [f"# Script: {getattr(mod, 'TITLE', 'explainer')}\n", "Review this text BEFORE rendering. Check every claim against its source.\n"]
    for i, b in enumerate(mod.BEATS):
        d = durs[i] if durs else None
        out.append(f"\n## Beat {i + 1}" + (f"  [{t:5.1f}s - {t + d:5.1f}s]" if d else ""))
        out.append(f"\nSAY ({len(b.say.split())} words): {b.say}")
        for c in b.claims: out.append(f"\n- [ ] CLAIM: {c}")
        if b.source: out.append(f"\n  SOURCE: {b.source}")
        if d: t += d
    open(path, "w").write("\n".join(out) + "\n")


def write_vtt(beats, durs, path):
    ts = lambda x: f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{x % 60:06.3f}"
    t, out = 0.0, ["WEBVTT", ""]
    for i, (b, d) in enumerate(zip(beats, durs), 1):
        if b.say.strip(): out += [str(i), f"{ts(t)} --> {ts(t + d - 0.05)}", b.say.strip(), ""]
        t += d
    open(path, "w").write("\n".join(out))


def caption(p, text):
    p.c.set_source_rgba(0, 0, 0, 0.55); p.c.rectangle(0, H - 92, W, 92); p.c.fill()
    p.text(text, W / 2, H - 46, 26, C["fg"], 1.0, "c", width=W - 120)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene"); ap.add_argument("--out", required=True)
    ap.add_argument("--fps", type=int, default=30); ap.add_argument("--stills")
    ap.add_argument("--script-only", action="store_true"); ap.add_argument("--no-audio", action="store_true")
    ap.add_argument("--no-captions", action="store_true"); ap.add_argument("--tts", choices=["auto", "eleven", "flite", "none"], default="auto")
    a = ap.parse_args()
    mod = load_scene(a.scene); beats = mod.BEATS
    base = os.path.splitext(a.out)[0]
    if a.script_only:
        write_script(mod, None, base + ".script.md"); print(open(base + ".script.md").read()); return
    engine = "none" if a.no_audio or a.tts == "none" else a.tts
    if engine == "auto": engine = "eleven" if os.environ.get("ELEVENLABS_API_KEY") else "flite"
    work = tempfile.mkdtemp(prefix="explainer-")
    parts, durs = [], []
    for i, b in enumerate(beats):
        if engine != "none" and b.say.strip():
            wp = os.path.join(work, f"beat{i:02d}.wav"); narrate(b.say, wp, engine); parts.append(wp)
            durs.append(max(b.min_dur, _wav_len(wp) + b.hold))
        else:
            parts.append(None); durs.append(max(b.min_dur, len(b.say.split()) / 2.6 + b.hold))
    write_script(mod, durs, base + ".script.md"); write_vtt(beats, durs, base + ".vtt")
    audio = None
    if engine != "none":
        audio = os.path.join(work, "narration.wav"); _concat_audio(parts, durs, audio)
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(a.fps), "-i", "-"]
    if audio: cmd += ["-i", audio, "-c:a", "aac", "-b:a", "160k"]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium", "-movflags", "+faststart", "-shortest", a.out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf); pen = Pen(ctx)
    if a.stills: os.makedirs(a.stills, exist_ok=True)
    for i, (b, T) in enumerate(zip(beats, durs)):
        n = max(1, round(T * a.fps)); snap = int(n * 0.9)
        for f in range(n):
            ctx.save(); pen.clear(); b.draw(pen, f / a.fps, T); ctx.restore()
            if not a.no_captions and b.say: caption(pen, b.say)
            surf.flush(); ff.stdin.write(bytes(surf.get_data()))
            if a.stills and f == snap: surf.write_to_png(os.path.join(a.stills, f"beat{i + 1:02d}.png"))
    ff.stdin.close(); rc = ff.wait()
    if rc: sys.exit(f"ffmpeg failed ({rc})")
    print(json.dumps({"out": a.out, "seconds": round(sum(durs), 2), "beats": len(beats), "tts": engine,
                      "script": base + ".script.md", "vtt": base + ".vtt", "stills": a.stills}, indent=1))


if __name__ == "__main__":
    main()
