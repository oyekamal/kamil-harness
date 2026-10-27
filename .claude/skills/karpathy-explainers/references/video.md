# Rung 4: a code-drawn explainer video (3b1b style, no diffusion)

Karpathy's prompt was "Create a 3b1b style video explainer on X. Use my ElevenLabs API key for
audio narration." The point is that the agent writes **programs that draw every frame**, so each
shape, number and arrow is exact and re-renderable. Never use an image or video diffusion model.

## What works (verify on your machine)

| Need | Use | Status |
|---|---|---|
| Frames | `scripts/explainer_video.py`: pycairo + Pango, piped as raw BGRA into ffmpeg | works |
| Formulas | matplotlib mathtext inside the engine (`p.math(r"$...$")`), no LaTeX needed | works |
| Encode | `/usr/bin/ffmpeg` libx264 + aac, yuv420p, faststart | works |
| Voice, paid | ElevenLabs REST, if `ELEVENLABS_API_KEY` is set | used automatically |
| Voice, free | ffmpeg's built-in **flite** (`-f lavfi -i flite=textfile=...:voice=slt`) | works, robotic |
| Manim | Not assumed installed. Do not plan on it. | - |
| LaTeX, espeak, piper | Not assumed installed | - |
| Browser canvas frames | Playwright Chromium, if installed (alternative path if a rung-3 page animation must become video: screenshot each frame, then ffmpeg) | works, slower |

ElevenLabs key: the engine reads `ELEVENLABS_API_KEY` (optional `ELEVENLABS_VOICE_ID`,
`ELEVENLABS_MODEL`). If it is not in the environment, ask before you load a key from another
project's `.env`. Keep one in your project's `.env`:
`set -a; . ./.env; set +a`. If there is no key, use
flite and say plainly in the report that the voice is the free robotic one.

## The pipeline (always in this order)

```bash
S=.claude/skills/karpathy-explainers/scripts
cp $S/example_scene.py my_scene.py            # 1. write the scene (beats = say + draw + claims + source)
python3 $S/explainer_video.py my_scene.py --out clip.mp4 --script-only   # 2. script.md -> REVIEW AS TEXT
python3 $S/explainer_video.py my_scene.py --out clip.mp4 --stills stills # 3. render + one PNG per beat
ffprobe -v error -show_entries stream=codec_name,width,height,duration -of compact clip.mp4  # 4. streams
ffmpeg -i clip.mp4 -af volumedetect -vn -f null - 2>&1 | grep mean_volume  # 5. voice is not silent
```
Then open every `stills/beatNN.png` with Read and look (step 6). Rendering speed is about 1 s of
wall time per 1 s of 720p video. A 3-second, one-beat test renders in about 10 s.

## Writing the scene

- A beat = one idea, 1 to 2 sentences of narration (≤ 25 words, STE style), one new visual.
- Beat length is set by the narration audio + `hold`, so the picture never runs ahead of the voice.
- Inside `draw(p, t, T)`, time each action with `seg(t, a, b)` (eased 0→1 between second a and b).
- Build up: a beat first redraws the end state of the beat before (`b1(p, 99, 99)`), then adds
  ONE thing. This gives the 3b1b "the picture grows" feel without a scene graph.
- Compute every number shown from the same `model()` as the fact sheet. Never type a result.
- Show it before you name it: draw the change (the dial moves, the curve drops), then say the rule.
- One colour per quantity, the same as rungs 2 and 3 (`C["yellow"]` = the answer, etc.).
- Numbered arrows (`p.arrow(..., num=1)`) for any sequence of events.
- Keep content above y ≈ 620; captions use the bottom 92 px (turn off with `--no-captions`).
- Pen API: `clear grid text(markup <sub>/<sup>) math line arrow box dot axes plot`.
  Write `E^{\circ}_{\mathrm{cell}}` for E°cell. **Never put Unicode symbols (°, ±) inside `$...$`**:
  the Computer Modern font maps ° to the wrong glyph (it rendered "γ" in testing). Unicode is
  fine in `p.text`.
- Narration for flite: write symbols as words ("E naught", "Q", "zero point zero five nine two
  volts", "log base ten"). flite reads raw symbols badly. ElevenLabs handles digits, but still
  spell out symbols.

## Length

A "short clip" = 3 to 6 beats, 20 to 60 seconds. Aim for one idea that moves: the direction
rule, shown changing. Do not narrate a whole chapter.

## Verification checklist (rung 4)

- [ ] `script.md` reviewed as text BEFORE rendering: every beat ≤ 25 words, every claim ticked
      against the fact sheet, numbers in narration = numbers on screen
- [ ] Spot-check the 3 most surprising claims against the PRIMARY source (not your memory);
      write the page or URL next to each in the report
- [ ] `ffprobe` shows h264 + aac (or h264 only with `--no-audio`) and the expected duration
- [ ] `volumedetect` mean volume is above about -40 dB (the voice is really there)
- [ ] You looked at every still: no overlaps, nothing cut off, formula glyphs correct, labels
      readable, arrows point the right way
- [ ] The report states the TTS engine used and says the clip is disposable: anything
      published needs a full human review

## Gotchas found while building this

- Text labels next to plotted points collide with arrows. Offset arrows away from the curve
  and put the value label on the other side of its dot.
- The `--stills` frame is taken at 90% of each beat, so it shows the finished state of that beat.
- If you change the narration, the beat lengths change. Re-render; do not splice by hand.
