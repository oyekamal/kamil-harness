---
name: karpathy-explainers
description: Make LLM output easy to understand and easy to check with Karpathy's "four rungs". Rung 1 is ASD-STE100 Simplified Technical English text, rung 2 is SVG or Mermaid diagrams with numbered arrows and listed weak spots, rung 3 is a single self-contained interactive HTML page, rung 4 is a code-drawn 3Blue1Brown-style narrated video (pycairo + ffmpeg, ElevenLabs or a free flite voice, no manim, no diffusion). Each rung has a lint or render gate that runs locally. Use for "explain X simply", "explain this in STE100 / simplified technical English", "draw a diagram of", "make an interactive explainer / HTML page for", "3b1b style video", "explainer video", "make me understand this paper/PR/concept", "Karpathy four rungs", and for tutoring content (short explanatory text, diagrams, sandboxed interactives, short clips).
---

# Karpathy explainers: four rungs, one fact sheet, every rung checked

Karpathy (X, 2 Oct 2026, x.com/karpathy/status/2105819303471976479) ranks output formats by how
fast a human understands them: **STE100 text → diagrams → HTML pages → custom explainer videos**,
each "even better". His reason: as agents do more of the work, our work moves "up into oversight
and understanding", and models can now build large, custom, *disposable* artifacts for one
question. Source write-up: explainx.ai/blog/karpathy-understand-llm-outputs-ste100-diagrams-html-video-2026.

The main risk: **a better format makes an error easier to believe.** So this skill adds two
things to the bare prompts: (1) one fact sheet, computed in code, that every rung renders, and
(2) a gate per rung that a script or a reader can check. Skip neither.

Paths below are relative to this skill's folder (`.claude/skills/karpathy-explainers/`).

## Step 0: pick the rung(s)

| The reader needs to... | Rung | Deliverable |
|---|---|---|
| Follow a procedure, re-read a definition, paste text into a doc or chat | 1 STE100 | `rung1.md` |
| See structure: parts, a flow, an order of events, cause → effect | 2 Diagram | `diagram.svg` / `.mmd` + PNG |
| Explore: "what if this number changes?", several parameters, a paper or a PR to review | 3 HTML | `explainer.html` |
| Learn a concept from zero, with motion and voice | 4 Video | `clip.mp4` + `script.md` |
| A nuanced "it depends" argument | 1 only (a table is fine) | no diagram |

If the user names rungs, do those. "Explain X properly" = rungs 1–3. Add rung 4 only if asked
or if the concept is a change over time. Effort grows with the rung: 1 (minutes) < 2 < 3 < 4.
When doing several rungs, do them in order. Each one reuses the one before it.

## Step 1: the fact sheet (always, before any rung)

Write `facts.md` from `references/fact-sheet.md`. It holds the primary source (book + section,
paper, official docs), the core statement, the symbols with units, conditions and sign
conventions, the direction rule, the worked numbers, the misconceptions, the limits, and three
surprising claims to spot-check. Add a glossary with one term per concept.
- **Compute every number in code.** Write a 5-line Python `model()` and paste its output.
  The same formula becomes `window.model` in rung 3 and `model()` in the rung-4 scene.
- **Reason in normal prose here.** STE style is a render step that runs AFTER the thinking.
  Style rules applied during the reasoning can bend the facts.
- Look up the primary source (WebFetch/WebSearch, the PDF, the repo). If you cannot reach it,
  say so in the fact sheet and in the final report. Do not cite from memory as if you checked.
- **Bridge every alternate form.** If the idea has two common forms (ln vs log10, RT/nF vs
  0.0592/n, SI vs everyday units), derive one from the other with numbers in code
  (0.0592 = ln 10 × 8.314 × 298.15 / 96485) and show that bridge in every rung. A reader who
  meets both forms elsewhere must see why they are the same thing.
- Save the glossary as `glossary.json` (`{"term": ["banned synonym", ...]}`).

## Rung 1: STE100 text, "80% of the way"

Read `references/ste100.md` (the rules table, the before/after example and the shape below).
Key rules: sentences ≤ 20 words (procedural) / ≤ 25 (descriptive), ≤ 6 sentences per paragraph,
active voice, one instruction per sentence, one word = one meaning (the glossary), simple
approved verbs (use, show, start, increase), keep the articles, no hedges or contractions.
Technical names are allowed. Define each one once.

Shape: **What it is** → **The equation** (one line per symbol: meaning, unit) → **What it tells
you** (the direction rule) → **How to use it** (numbered steps) → **Worked example** (units on
every number) → **Limits** → **Glossary**.

Gate:
```bash
python3 scripts/ste_lint.py rung1.md --glossary glossary.json   # PASS = 0 errors, warnings <= 20%
```
Then diff the facts: every number, sign, unit and condition in `rung1.md` must match `facts.md`.
In the rung-1 text itself, never write a banned synonym, not even in the glossary section
(write "Do not use other words for this." instead of naming them). The linter reads consecutive `- ` lines as one paragraph, so put a blank line between list items.

## Rung 2: diagrams

Read `references/diagrams.md`. Start SVG from `references/diagram-template.svg`. Use Mermaid for
flows and sequences, and hand-written SVG for physical setups.
- Every box has its real name. Every arrow has a number (the order of events) and says what moves.
- Each arrow direction is a claim. Check it against the source.
- Use ≤ 9 boxes. Mark anything unverified with a dashed stroke + `class="uncertain"` + `data-why`.
- Use the same colours and terms as the other rungs.
- **Draw the weak spots INTO the diagram** as a footer box inside the SVG, so the PNG carries
  its own limits when it is seen alone (on a whiteboard, in a chat). Also list them below: `label/arrow — why it may be wrong or
  simplified — how to check it`. The weak points must be real (simplifications, assumed
  conditions, not-to-scale parts). Do not invent weak points to fill the list.

Gate:
```bash
python3 scripts/diagram_check.py diagram.svg --png diagram.png   # or flow.mmd
```
Then **open the PNG with Read and look**. Check for overlaps, cut-off text, wrong arrow heads
and a wrong reading order. A diagram you have not looked at is not done.

## Rung 3: one self-contained HTML page

Start from `references/html-template.html`. It already passes the gate and has a TOC, a summary,
tabs (one claim per tab), a predict-then-reveal box, sliders wired to `window.model`, an animated
canvas plot, a worked-numbers table built from `model()`, a weak-spots + "what would change my
mind" box, and sources.
- **The explorer is the first screen.** At 1280x800, above the fold: title, the formula, the
  sliders, the live readout and the plot. The template already puts `#lab` first. Keep it there.
  Summary, tabs, tables and sources go below it. A reader should be able to play before reading.
- **No external dependencies**: no CDN, no web fonts, no fetch. Put everything inline. Draw
  formulas with HTML/Unicode (`E°<sub>cell</sub>`) or inline SVG. (KaTeX/MathJax from a CDN
  breaks offline and inside a sandboxed iframe.)
- **One source of truth**: every readout, plot point and table cell comes from
  `window.model(params)`. Put values copied from the primary source in `window.checks`
  (`{input, expect, tol, source}`). The gate fails the page if `model()` disagrees with them.
  `tol` is RELATIVE (0.005 = 0.5%); add `abs` for values near zero.
- **Predict first**: ask the reader to guess what the slider will do before you show the rule.
- Show the direction rule on the plot (a marked point that moves, a readout with units, a note
  that names the region). Slider ranges must stay inside the formula's valid range.
- The page must work at 390 px wide, in dark mode, and with reduced motion.
- Put the rung-1 text in the summary and the rung-2 diagram inline (paste the SVG).

Gate:
```bash
python3 scripts/html_check.py explainer.html --csp      # offline + sandbox CSP, drives every control
```
It fails on a network request, an external tag, a console error, a slider that changes nothing,
phone overflow, or a `window.checks` miss. Look at the `*.desktop.png`, `*.desktop-after.png`
and `*.phone.png` screenshots it writes.

## Rung 4: a code-drawn explainer video

Read `references/video.md` first. Assumes **no manim and no LaTeX** are installed. The engine is
`scripts/explainer_video.py`: pycairo + Pango draw the frames, matplotlib mathtext draws the
formulas, and ffmpeg encodes them. The voice is ElevenLabs if `ELEVENLABS_API_KEY` is set,
otherwise the free offline flite voice built into ffmpeg. Copy `scripts/example_scene.py`
(3 beats, axes, plot, formula, numbered arrows) and edit it.

```bash
python3 scripts/explainer_video.py scene.py --out clip.mp4 --script-only        # 1. review script.md AS TEXT
python3 scripts/explainer_video.py scene.py --out clip.mp4 --stills stills      # 2. render
ffprobe -v error -show_entries stream=codec_name,duration -of compact clip.mp4  # 3. h264 + aac
ffmpeg -i clip.mp4 -af volumedetect -vn -f null - 2>&1 | grep mean_volume       # 4. voice present
```
Run scene files with `PYTHONPATH=scripts` (or from inside `scripts/`), because `scene.py` imports
`explainer_video`. Keep every drawn box out of the caption band (y ≥ 620). The engine does not
enforce this. Then Read every `stills/beatNN.png`. Rules: **every beat moves.** Animate the change itself (a dot sliding along the line as Q
rises, a term appearing, a readout counting). A finished graph sitting still is a slide, not a
beat. One idea per beat. Narration ≤ 25 words, STE style,
symbols written as words. Each beat builds on the one before. Show the change before you name the
rule. Compute every on-screen number from `model()`. Before rendering, spot-check the 3 most
surprising claims against the primary source. A short clip is 3–6 beats, 20–60 s. The clip is
disposable. If anyone wants to publish it, it needs a full human review.

## Across rungs (this is what makes the set checkable)

- One rounding rule: pick the significant figures once in `facts.md` (e.g. 0.0592 V) and use that exact string in every rung. Do not show 0.0296 in the text and 0.030 in the video.
- One glossary, one colour per quantity, one `model()`, one list of sources, in every rung.
- The numbers in the rung-1 worked example, the diagram labels, the HTML checks and the video
  claims must all match `facts.md`. Grep for each key number across the files before you finish.
- Each rung states its own limits. Rung 1 has "Limits", rung 2 has the weak-spots list, rung 3
  has the weak-spots box, rung 4 has the claims checklist in `script.md`.

## Review captures (for you and for any reviewer)

```bash
# first screen of the page, no scroll: html_check.py already writes NAME.desktop.png at 1280x800
for t in 0.2 0.5 0.85; do ffmpeg -v error -y -ss $(python3 -c "import subprocess as s;d=float(s.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','clip.mp4']));print(d*$t)") -i clip.mp4 -frames:v 1 still_$t.png; done
```

## Final report (what you hand back)

1. The files (absolute paths): `facts.md`, `rung1.md`, `diagram.svg/.png`, `explainer.html`,
   `clip.mp4`, `clip.script.md`, `clip.vtt`, stills.
2. The gate results, pasted: ste_lint summary line, diagram_check RESULT, html_check RESULT +
   `check ok` lines, the ffprobe line and mean_volume.
3. What you spot-checked against the primary source (claim → page/URL) and what you could NOT verify.
4. The TTS engine used (ElevenLabs or flite) and any gate you could not run, with the reason.
Never write "done" for a rung whose gate you did not run.

## Files

- `references/fact-sheet.md`: the fact-sheet template + a complete worked example (Nernst)
- `references/ste100.md`: rules, approved simple verbs, render-step rule, before/after
- `references/diagrams.md` + `diagram-template.svg`: diagram forms, rules, weak-spots format
- `references/html-template.html`: the rung-3 starting page (passes `html_check.py`)
- `references/video.md`: the rung-4 pipeline, the scene API, the tools it assumes, gotchas
- `scripts/ste_lint.py`, `scripts/diagram_check.py`, `scripts/html_check.py`: the gates
- `scripts/explainer_video.py` + `scripts/example_scene.py`: the video engine + an example scene
