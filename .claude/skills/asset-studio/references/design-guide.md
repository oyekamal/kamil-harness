# Design Guide

How to make code-generated art look intentional and professional rather than programmer-art.

## Style token system (define before drawing)

Declare at the top of the generator script and reuse everywhere:

- **Palette**: 4–6 hex constants with *semantic* names (`INK`, `DANGER`, `TERRAIN`) — never `COLOR1`. If the user has a spec, brand, or cultural palette, use it verbatim.
- **Outline**: one stroke width constant (e.g. `SW = 3` on a 160 viewBox) applied to every shape. Uniform outlines are what make a pack read as one artist's work.
- **Canvas**: one viewBox for all sprites of a class (160×160 works well); wide format for tiles (400×200). Consistent canvases make sheets, previews, and engine configs trivial.
- **Signature detail**: one motif grounded in the subject's real world — local food, a landmark, a cultural symbol, a period-correct object. This is what makes users say "it feels like *ours*". Choose it deliberately in step 1.

## Character construction

Build characters from named sub-functions (head, torso, limbs, vehicle/props) composed per pose. Rules that keep them readable:

- **Silhouette first**: flood-fill the character black in your head — is the pose still identifiable? Jump must read as jump at 40px.
- Limbs as thick round-capped strokes (an outline-colored stroke slightly wider underneath a fill-colored stroke gives a clean outlined limb).
- Overlap layering deliberately: far limbs behind torso, near limbs in front; draw order in SVG = z-order.
- Animation frames vary parameters, not structure: wheel angle, bob offset (±1–2 units), limb endpoints, glow radius, steam phase. Secondary motion (exhaust puff, dust, trailing mist) on alternating frames sells speed cheaply.
- Poses that must feel different (duck vs ride) should change the torso's main axis, not just the head.

## Seamless scrolling tiles

- Identical edge geometry on every tile: any band (sky, hills, ground, road) must meet the left and right edges at the same y on all tiles in the set, so any tile connects to any other.
- Keep a margin (~5% of width) at both edges free of discrete elements (trees, buildings).
- Repeating markings (road dashes) at a period that divides the tile width evenly.
- Zone variety comes from the middle of the tile; the shared bands carry continuity.

## UI assets (icons, HUD, buttons)

- Design on a grid (multiples of 8), test legibility at the smallest real size (a 36px HUD light, a 24px icon).
- Stateful elements ship as explicit state files/frames (on/off, empty/full, enabled/disabled), not as instructions to tint.
- Glow/pulse for collectibles or attention: two frames differing only in halo radius and opacity — cheap and effective.
- Respect the platform: don't imitate proprietary logos (draw a generic glyph that communicates the same idea); avoid trademarked marks and characters.

## Motion quality (loops, bounces, any eased movement)

Raw keyframes shown as linear steps read as robotic, not animated. Fix:

- **Interpolate, don't just keyframe.** Define 3–4 key poses (e.g. grounded/rising/peak/falling), then use `scripts/easing.py` to generate ~10–16 in-between frames before exporting. More frames at a low per-frame cost (GIF/sprite strip) reads far smoother than few frames at long duration.
- **Match the easing curve to the physics**: `ease_out_back` for impacts/landings (the classic squash — slight overshoot then settle), `ease_in_out_sine` for a smooth rise/fall arc, `ease_out_bounce` for a literal bounce-to-rest. Never linear for anything that has mass.
- **Secondary action moves on its own clock.** Any follow-through element (steam, hair, cloth, exhaust, a tail) should NOT be locked to the primary motion's phase — give it its own eased loop, offset in time, so it reads as reacting rather than attached. It should be continuously present (fading in/out), never popping in on frame 1.
- **Loops need a seam check**: the last interpolated frame should land back at (or very near) the first frame's values, or the loop will visibly jump. Verify by comparing frame[0] and frame[-1] numerically before rendering.

## The critique checklist (run at every contact-sheet view)

1. Anything read as a blob or unclear shape at a glance? (Commonest failure: an overlapping limb or accessory.)
2. Are all outlines the same weight? Any shape missing its outline?
3. Do the frames of each cycle differ enough to read as motion, and little enough to read as the same object?
4. Is the palette leaking — any color not in the token list?
5. Do all assets look like one pack (same weight, same level of detail, same lighting logic)?
6. Ground-contact consistent across frames (no jitter)?
7. Would the target audience recognize the signature cultural/subject details?

Fix everything found, re-render, re-view. Two critique passes is normal; zero is negligence.

## Copyright and sensitivity

Do not reproduce trademarked logos, branded characters, or copyrighted art styles tied to specific franchises. For real-world satire or political subjects, keep depictions generic-institutional (a uniform, a vehicle type) rather than identifiable individuals.
