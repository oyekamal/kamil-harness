---
name: thinking-orbs
description: Add Jakub Antalik's "thinking-orbs" dotted thought-orb loading indicators (npm `thinking-orbs`, MIT) to an AI or agent UI. Nine hand-tuned 2D-canvas states (working, searching, solving, listening, connecting, weaving, composing, breathing, shaping), 64px and 20px presets, monochrome auto dark/light. Use for "thinking orb", "agent loading indicator", "AI thinking animation", "spinner for an agent/chatbot", "show the assistant is listening/thinking", "orbs.jakubantalik.com" / "libraries.dev/orbs", or recreating the orbs demo page. Covers the React API with every prop and default, the React-free `thinking-orbs/engine` for vanilla JS and canvas, a verified CDN-only standalone HTML recipe, theme resolution, reduced motion and aria, tuning or adding a state, the React Native port.
---

# thinking-orbs

Dotted, depth-shaded 3D "thought orbs" drawn with plain 2D canvas arcs. They use no WebGL and no filters, so they render identically in Chrome, Safari and Firefox.

- Source: github.com/Jakubantalik/thinking-orbs (now also inside github.com/Jakubantalik/Libraries.dev).
- npm: `thinking-orbs`. The latest is **0.3.2**; the repo `src/` is at 0.3.1.
- License: MIT © 2026 Jakub Antalik. The demo is by Jakub Antalik & Alex Brinza. Keep the credit in anything you ship.
- Live demo: `orbs.jakubantalik.com` now only shows a "moved" notice. The demo lives at **https://libraries.dev/orbs**, where weaving, shaping and 32px are Pro-gated in the site UI but all of them are free in the npm package.

## Install

```bash
npm install thinking-orbs        # peerDependency: react >= 18 (React 19 works)
```

## States: what each one looks like and when to use it

| state | animation (from source) | default aria-label | use it when the agent is… |
|---|---|---|---|
| `working` (default) | particles on tilted orbits around a ghost sphere | Working… | doing generic work or running tools |
| `searching` | a scan meridian sweeps a dotted globe | Searching… | searching the web, docs or files; retrieval |
| `solving` | latitude bands scramble in quarter turns, then click back solved | Solving… | reasoning, planning or working a problem |
| `listening` | a waveform rolls through latitude rings | Listening… | taking voice or mic input, or waiting on the user |
| `connecting` | a constellation wires itself, with packets running along the edges | Connecting… | calling APIs or MCP, handing off between agents, networking |
| `weaving` | three strands plait around the sphere | Weaving… | merging sources or synthesising (the demo labels it "planning") |
| `composing` | an undulating multi-band sash | Composing… | writing or streaming output (the demo hero labels it "Thinking….") |
| `breathing` | a face-on ring slowly morphs | **Thinking…** | idle, or generic "thinking", or waiting |
| `shaping` | a dotted outline morphs circle → triangle → square | Shaping… | drawing, laying out or generating visuals |

Internally each state maps to a mode (`STATE_TO_MODE`): working→orbits, searching→globe, solving→rubik, listening→wave, connecting→web, weaving→braid, composing→ribbon, breathing→ring, shaping→morph. `ring` is `ribbon` with `faceOn: 1` and no ghost sphere.

## Sizes

- `size` takes one of the tuned presets: **64** (chat-avatar scale) or **20** (inline-text scale). 0.3.2 also ships **32**.
- They are separate designs, not a scale factor. Each preset has its own dot count, dot radius and speed.
- The canvas backing store is `size × min(2, devicePixelRatio)`. CSS size is `size`px unless you override `style`.
- To show a 64 preset smaller, override CSS width and height. The demo does this: `style={{ width: 56, height: 56 }}` inside its 74px pills.
- Do not pass sizes such as 48. Only the listed keys exist; anything else has no preset.

## React API (`<ThinkingOrb />`)

```tsx
import { ThinkingOrb } from 'thinking-orbs';
<ThinkingOrb state="searching" size={64} />
```

| prop | type | default | notes |
|---|---|---|---|
| `state` | `OrbState` (the 9 above) | `'working'` | |
| `size` | `64 \| 20` (0.3.2: also `32`) | `64` | tuned preset |
| `theme` | `'auto' \| 'dark' \| 'light'` | `'auto'` | `dark` = light ink for dark backgrounds; `light` = dark ink for light backgrounds |
| `speed` | number | `1` | multiplier on the preset's baked speed (the demo slider runs 0.25–3) |
| `paused` | boolean | `false` | freezes on the current frame (one frame is still drawn) |
| `aria-label` | string | per-state label (table above) | overrides the label |
| `style` | CSSProperties | — | merged after `{width:size,height:size,display:'block'}` |
| …rest | any `<canvas>` attribute | — | `className`, `data-*`, `id`, and so on pass through |

The following props exist **only in 0.3.2**. They are in the published package, not in repo `src/`:

| prop | type | default | notes |
|---|---|---|---|
| `color` | string | — | ink tint: `#rgb`, `#rrggbb` or `rgb()`. Keeps the depth ramp (fades toward black on dark, toward white on light). |
| `dots` | number | `1` | density multiplier, floor 0.1 |
| `dotSize` | number | `1` | radius multiplier, floor 0.1 |
| `opts` | `ModeOpts` | — | raw engine knobs, merged last (see Tuning) |
| `frame` | `ModeFrame` | — | replaces the geometry entirely (custom state) |
| `gravity` | `boolean \| GravityOptions` | off | cursor-warp effect. It stays off unless you supply a platform cursor sprite (`setGravitySprite`). It is also off under reduced motion, forced colours, coarse pointers and zoom. Skip it. |

Exports from `thinking-orbs`:
- 0.3.1: `ThinkingOrb`, `resolvePreset`, `STATE_TO_MODE`, `MODE_DRAWS`, and the types `ThinkingOrbProps`, `OrbState`, `OrbSize`, `OrbTheme`.
- 0.3.2 adds: `MODE_FRAMES`, `scaleCounts`, `scaleRadii`, `countDots`, the core math helpers (`finalizeFrame`, `makeProj`, `radiusScale`, `fibDir`, `hashD`, `vnoise`, `lerp`, `frac`, `angleDelta`) and the gravity API.

## Theme resolution (as implemented in `src/theme.ts`)

1. An explicit `theme="dark"` or `theme="light"` wins.
2. For `auto`, the component walks up from the canvas and takes the **nearest** ancestor that has one of:
   - `data-theme="dark"` or `data-theme="light"`, or
   - the class `dark` or `light` (the Tailwind/shadcn convention).

   A `MutationObserver` on `<html>` (subtree; attributes `class` and `data-theme`) re-resolves live.
3. If no ancestor matches, it uses `matchMedia('(prefers-color-scheme: dark)')`, subscribed for live OS switches.
4. SSR: everything runs in effects, so the canvas paints only on the client. The pre-mount fallback is dark.

Ink is strictly grayscale: `rgba(g,g,g,a)`.
- On light themes, `g = white*255`, where `white` is the dot's ink value.
- On dark themes it is mirrored to `(1-white)*255`, so near dots read bright.
- The canvas is transparent, so the background is yours.

**Gotcha:** if the app is light-only and has no `data-theme` or class, `auto` follows the OS. On a dark-mode OS that gives light dots on a white page, which are invisible. Pin `theme="light"` in light-only apps.

## Accessibility and performance (as implemented)

- The canvas gets `role="img"` and `aria-label` (the per-state default, or yours). For an orb that only decorates visible text, pass `aria-hidden` and keep the text.
- `prefers-reduced-motion: reduce` (watched live) renders **one static frame at t=0.6** and no rAF loop. That frame still follows theme changes.
- Each instance stops its rAF loop when it is offscreen (`IntersectionObserver`) or when the tab is hidden (`visibilitychange`). All instances read the same `performance.now()` clock, so they resume in phase.
- DPR is capped at 2. The heaviest mode (composing) draws about 566 dots per frame.

## Standalone HTML, no build step (verified)

Both recipes were rendered in headless Chromium (Playwright): all 18 canvases (9 states × 2 sizes) were non-blank, every one changed between frames 400 ms apart, and with reduced motion none did. There were no console errors.

**A. React through an esm.sh import map.** `?external=react` makes React a single shared instance; without it you get duplicate React and hooks errors. Needs network: esm.sh fails offline, so for an offline build `npm i thinking-orbs` and bundle with Vite.

```html
<script type="importmap">
{ "imports": {
  "react": "https://esm.sh/react@18.3.1",
  "react/": "https://esm.sh/react@18.3.1/",
  "react-dom/client": "https://esm.sh/react-dom@18.3.1/client?external=react",
  "thinking-orbs": "https://esm.sh/thinking-orbs@0.3.2?external=react"
} }
</script>
<div id="root"></div>
<script type="module">
  import React from 'react'; import { createRoot } from 'react-dom/client';
  import { ThinkingOrb } from 'thinking-orbs';
  const h = React.createElement;   // no JSX without a build; or use esm.sh/htm
  createRoot(document.getElementById('root')).render(
    h('div', null, ['working','searching','solving'].map(s => h(ThinkingOrb, { key: s, state: s, size: 64 }))));
</script>
```

**B. Vanilla, no React.** Use the `thinking-orbs/engine` entry, which imports nothing from React or the DOM. Either CDN works:
- `https://cdn.jsdelivr.net/npm/thinking-orbs@0.3.2/dist/engine.es.js`
- `https://esm.sh/thinking-orbs@0.3.2/engine`

```js
import { resolvePreset, MODE_DRAWS } from 'https://cdn.jsdelivr.net/npm/thinking-orbs@0.3.2/dist/engine.es.js';
function mountOrb(el, { state = 'working', size = 64, speed = 1, dark = true } = {}) {
  const c = document.createElement('canvas'), dpr = Math.min(2, devicePixelRatio || 1);
  c.width = c.height = Math.round(size * dpr); c.style.width = c.style.height = size + 'px';
  c.setAttribute('role', 'img'); c.setAttribute('aria-label', state + '…'); el.append(c);
  const ctx = c.getContext('2d'), { mode, speed: base, opts } = resolvePreset(state, size), draw = MODE_DRAWS[mode];
  const frame = t => { ctx.setTransform(dpr,0,0,dpr,0,0); ctx.clearRect(0,0,size,size); draw(ctx, size, t, dark, opts); };
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return frame(0.6);
  (function loop(){ frame(performance.now() / 1000 * base * speed); requestAnimationFrame(loop); })();
}
```

The component's time formula is `t = performance.now()/1000 × presetSpeed × speed`. Keep it, or your orbs drift out of phase with React ones.

`references/vanilla-orbs.html` is the full verified version. It adds auto-theme detection, which re-reads `data-theme` every frame.

## Recreating the orbs demo page

`references/demo-page.html` is a **verified, single-file recreation** of the original orbs.jakubantalik.com demo. It uses recipe A plus inline CSS, and it was screenshot-compared against the repo's own built demo.

To recreate the demo, copy that file and adjust it. Do not rebuild it from memory.

What it contains:

1. **Header**
   - "‹ jakubantalik.com" pill link at top left.
   - Theme toggle, GitHub and X icon buttons (36px circles) at top right.
   - header.png from `https://cdn.jsdelivr.net/gh/Jakubantalik/thinking-orbs@main/demo/public/header.png` (146x117, margin `-190px 0 -20px`).
   - Title "Thinking orbs" (22px/500) and subtitle "Animated thinking orb component" (14px, 50% opacity).
2. **Hero row**: two boxes, 314px tall, radius 30px, fill `rgba(217,217,217,.035)`. Each holds a large pill: 270×74, `padding-left 9px`, `padding-right 32px`, gap 12px, fill `rgba(29,29,29,.42)` plus an inset 1px ring. The pill contains a 64-size orb at 56px CSS and an 18px label.
   - Left: `solving` labelled "Solving…."
   - Right: `composing` labelled "Thinking…."
3. **Chip grid**: 2 columns, `grid-auto-rows:151px`, gap 12px, filled in this order:
   - listening (small)
   - working (large, 2 rows)
   - searching (large, 2 rows)
   - connecting (large, labelled "Solving….")
   - weaving (small, "Agent planning…")
   - breathing (small, "Agent thinking…")
   - shaping (small, "Agent shaping…")

   Small chips are 36px tall with `padding-left 8px` and `padding-right 14px`, a 20-size orb and a 12px "Agent X…" label. Labels shimmer with a `background-clip:text` highlight sweep (2 s, linear).
4. **Installation and Usage code boxes**: `#121212`, radius 10px, Roboto Mono 14/22, copy button on the right.
5. **Playground**:
   - 9 State tabs (default Listening) and 64px/20px Size tabs. Tabs are 36px tall, radius 8px, 13px text.
   - Speed range 25–300% shown as "1.00×". It drives the hero orbs too.
   - A 304px stage with the orb and a 32px play/pause button. The playground **starts paused**.
   - A live snippet that adds `speed={x.xx}` when the speed isn't 1.
6. **Footer**: "Made by Jakub Antalik & Alex Brinza".

Page details:
- Background `#070707`; column max-width 883px; padding 24px; font Inter.
- Light theme: `html[data-theme="light"]` with background `#fff` and panels `#ebebeb`. The orbs flip on their own via `auto`.
- At ≤640px the grid drops to one column.

Note: the upstream demo wires `useTheme` but never renders a toggle button, so the live page is dark only. The recreation adds the toggle on purpose.

## Tuning, and adding a state (spec/ + engine)

- **Presets**: `PRESETS[mode][size] = { speed, count, size, extra? }` scales `BASE_PROFILES[mode]`.
  - `count` multiplies dot counts. Paired lattices take √count on each side.
  - `size` multiplies every radius key.
  - `spec/orbs-spec.json` holds all of these, plus the paint contract and labels. `spec/orbs-golden.json` holds 72 golden frames (1e-4 tolerance) for checking ports.
- **Knobs per state** (0.3.2 `opts`):

  | state | knobs |
  |---|---|
  | working | `ghostA`, `particles` |
  | searching | `scanMul`, `dimBase` |
  | connecting | `thr`, `signals`, `lineW`, `spread` |
  | weaving | `turns` |
  | composing, breathing | `wobMul`, `bandMul`, `spin` |
  | shaping | `spread`, `shape` (`0` circle, `1` triangle, `2` square holds that shape instead of cycling) |

  Example: `<ThinkingOrb state="shaping" opts={{ shape: 1 }} />`. Prefer `dots` and `dotSize` over raw counts.
- **Custom state**: pass `frame={(size, t, opts) => ({ dots, lines })}`.
  - A `Dot` is `{x, y, z, r, white, a?}`. `white` runs 0..1, where 0 is the darkest ink on paper.
  - A `Line` is `{x1, y1, x2, y2, white, a?, w}`.
  - Build `dots` from `fibDir` and `makeProj(yaw, tilt, cx, cy, R)`, then return `finalizeFrame(dots, lines, rMin)`, which culls `a < 0.02`, clamps radii and z-sorts.
  - The library still handles theme, tint, pause, reduced motion and offscreen.
  - In 0.3.1, fork `src/engine/` and register the frame in `MODE_FRAMES`, `STATE_TO_MODE` and `PRESETS` instead.
- **Speed**: tune with `speed`. The baked speeds are already tuned per size.

## Other platforms (`ports/`)

- `ports/react-native/thinking-orbs-native` uses `@shopify/react-native-skia` with `react-native-reanimated`.
  - Props mirror the web package (`accessibilityLabel` replaces `aria-label`). Theme comes from `useColorScheme()`; reduced motion from `AccessibilityInfo`.
  - It imports the same `thinking-orbs/engine` geometry.
  - Its README says it is **not yet runtime-verified on a device**, so don't ship it unverified.
- SwiftUI appears only as a plan in `PORT_PLAN.md`. libraries.dev lists "Swift UI" install tabs that this repo does not contain.

## Verify before claiming done

Screenshot the page and check that every canvas is non-blank (count non-zero alpha with `getImageData`). Two frames about 300 ms apart must differ, unless the orb is paused or reduced motion is on. Flipping `data-theme` must invert the ink. With `reducedMotion: 'reduce'` emulated, frames must stay identical.
