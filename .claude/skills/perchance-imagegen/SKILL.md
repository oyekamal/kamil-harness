---
name: perchance-imagegen
description: Free, no-key text-to-image through perchance.org/ai-text-to-image driven in a headed Chromium. Use for batches of flat-vector picture assets (word pictures, stickers, spot art) when Gemini/Kie/fal keys or credits are dead. Native 512x512 JPEG.
---

# Perchance image generation (free, no key)

**Requires:** Python with Playwright + Chromium and a display (real or `xvfb-run`); network access to perchance.org.

Tested on a 12-prompt word-picture batch: all came back clean in one consistent flat-vector, thick-outline, warm-palette look; people, buildings, food and objects all read.

## Run

**Invisible (preferred):** headed Chromium on a virtual display, so nothing appears on the desktop and Cloudflare still passes:
```bash
PERCHANCE_VISIBLE=1 xvfb-run -a -s "-screen 0 1400x1100x24" python3 .claude/skills/perchance-imagegen/perchance_gen.py OUTDIR --jobs jobs.json --n 4
```
The examples below use `DISPLAY=:0` (a visible window; the window manager keeps it on screen, so off-screen positioning does not work).

```bash
DISPLAY=:0 python3 .claude/skills/perchance-imagegen/perchance_gen.py OUTDIR "name=what to draw" "name2=..."   # default STYLE appended
DISPLAY=:0 python3 .../perchance_gen.py OUTDIR "name=full prompt" --plain                                      # no style suffix
```

Writes `OUTDIR/<name>.jpg` (512x512) and `OUTDIR/sheet.png` (contact sheet to look at). Resumable: existing names are skipped. About 15 s per image, one at a time.

## Rules

- **Headed only.** Headless hits Cloudflare's "Just a moment" bot check. A normal headed window passes by itself. Never add stealth plugins or fingerprint spoofing; if a challenge shows, solve it by hand once. Profile persists at `~/.perchance/perchance-profile`.
- Needs a display: a real one (`DISPLAY=:0`) or `xvfb-run` as above. The window opens OFF-SCREEN by default (`PERCHANCE_VISIBLE=1` to show it); default gap between prompts is 2 s (`PERCHANCE_GAP_MS`).
- Output is white background, not transparent: flood-fill the background to transparent (a few lines of PIL), then crop and pack to webp.
- Describe the meaning, not a word ("a smiling man guest waving at a front door"). Abstract words (intention, above) still need a concrete scene or no picture.
- Look at `sheet.png` before shipping anything; the model sometimes draws a decorative extra or a wonky hand. Re-roll by deleting that jpg and re-running.
- **One Perchance run at a time across ALL sessions and projects** (any project): the script takes an exclusive lock at `~/.perchance/perchance.lock` and waits for the other run to finish. Two sessions at once very likely cause the second "Anti-bot verification failed"; always use the ONE profile `~/.perchance/perchance-profile`, never a per-project profile.
- **One window, one profile, sequential. Never parallel, never fresh profiles.** Three parallel windows with new profiles triggered "Anti-bot verification failed". If a page ever shows "Anti-bot verification failed ... Retrying", STOP the run, wait ~20 min, then resume (it is resumable) with a bigger gap (`PERCHANCE_GAP_MS=30000`). A single window on the persistent profile with the default 12 s gap is fine (~25 s per prompt, four images each).
- One generate click makes FOUR images; use `--n 4` to wait for all four and save `name__1..4.jpg`, then pick the best (critic or by eye).
- Free site with no SLA: keep batches modest (a few dozen at a time), and do not hammer it in parallel.
- Review/licence: Perchance output is free to use per the site, but check its terms page before commercial store assets.

## Second generator: perchance.org/alebrije-pic (fallback when the first page's bot check refuses)

`--site alebrije` in `perchance_gen.py` (own profile `~/.perchance/perchance-profile-alebrije` + own lock, so a session on the other page does not wait; still ONE run per page). 768 px output, count 1-8 per prompt (`--n`; the site often returns only 2 of 4: "no response", just rerun those), daily cap 250 prompts, stops after 2 empty prompts in a row.

**Consistency toolbox (all verified):**
- **Style library** (`#openStylesBtn`, search `#styleSearchIn`, chips): thousands of presets, mixed up to 5 with strength sliders ("Mix (2/5)"). Useful: `Flat Vector Illustration 2`, `Cartoon Flat icon`, `Flaticon Freepik Sticker` (sticker look), `Markhor horns`, `Addax horns`, `Unicorn Horn` (spiral), `Children's book illustration`. **Chips only register with a real Playwright click** (`locator(...).click()`), a JS `.click()` is ignored and the result says "No style".
- **Negative prompt** (`#negInput`), **seed** (`#seedInput`, inside `<details>` "Advanced options": test `details.open`, not visibility), **guidance** (`#guideInput`).
- **Edit** (✏️ on a result card -> `#editInput`, `#editNumInput`, `#editGoBtn`): re-generates from the SAME seed with only your change. Best consistency tool: fix one detail at a time on a good base ("make the eyes smaller, remove the blush").
- ✂️ Remove background, 🎯 same seed, 🎲 vary. Never click 🤍 (publishes to the community gallery).
- The page remembers prompt, negative, seed and Advanced state between runs: always set or clear them.
- The page has an adult mode and a realistic-people "Studio": leave both OFF (family mode); do not click the 18+ "I agree".

**Do not use this to recreate an existing character.** The page has no reference-image input, so it only approximates a description, and blind model critics can say "same" when a human would not. Use it for new characters/props and word pictures; an exact existing character needs an image-to-image tool (Gemini/fal/Kie with the reference). If you must approximate: mix a few flat styles (e.g. `Flat Vector Illustration 2 + Cartoon Flat icon`, not `Kawaii Flat icon`, which adds blush and huge eyes), write a detailed prompt, add negatives for what must be absent, and use the seed-locked Edit button to fix one detail at a time. Post-process: mirror if the model waves with the wrong hand, flood-fill white and grey ground shadow to transparent.
