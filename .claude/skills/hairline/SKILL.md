---
name: hairline
description: Use @lucasmarkes/hairline, 27 isometric line-drawing SVG figures that answer the pointer (Terrain, Riffle, Exploded, Phosphor, Sieve, Loupe, Vault and more), in React or plain DOM or straight from a CDN. Covers install, the vanilla `terrain(el, opts)` and React `<Terrain />` APIs, every option with its real default (intensity, theme, label, onRead), what each figure is and what intensity drives, theming with `--hairline-*` properties, a standalone HTML recipe, rebuilding the hairline.lucasmarkes.com figures page (tile grid plus intensity-slider drawer), drawing a new figure with the vendored hairline-create kernel, and using figures as calm empty, loading and state visuals. Triggers on "hairline", "hairline figure", "isometric line illustration", "line-art empty state", "interactive SVG illustration", "figure that follows the cursor", "hairline-create", "/hairline-create", "recreate hairline.lucasmarkes.com".
---

# hairline: isometric line figures that answer the pointer

Vendored from github.com/lucasmarkes/hairline (commit bc78224, npm `@lucasmarkes/hairline` **0.3.0**, MIT, © 2026 Lucas Marques; license in `references/LICENSE-hairline-MIT`). The facts below were read from `packages/hairline/src` (index.ts, mount.ts, intensity.ts, react.tsx, core/styles.ts) and the site source, not guessed. The upstream skill for drawing new figures is in `references/hairline-create/` (its SKILL.md is renamed `UPSTREAM-SKILL.md` so the harness doesn't load it as a second skill).

## Install and import

```sh
npm i @lucasmarkes/hairline        # ESM only, no dependencies; React >=18 is an optional peer, needed only for /react
npx shadcn@latest add https://hairline.lucasmarkes.com/r/hairline.json   # shadcn wrapper that reads your theme tokens
```

CDN, no bundler, in `<script type="module">`. All four URLs were tested and return 200:
- `https://esm.sh/@lucasmarkes/hairline@0.3.0` (the site's own CDN snippet uses esm.sh, unpinned)
- `https://cdn.jsdelivr.net/npm/@lucasmarkes/hairline@0.3.0/dist/index.js` (one self-contained file, about 170 kB raw)
- `https://cdn.jsdelivr.net/npm/@lucasmarkes/hairline@0.3.0/+esm` or `https://unpkg.com/@lucasmarkes/hairline@0.3.0/dist/index.js`
Always pin `@0.3.0`. Leave the React entry (`/react`) off the CDN; in a CDN page, use the functions.

## API

**Vanilla.** There is one function per figure, and every one has the same signature:
```ts
import { terrain } from "@lucasmarkes/hairline";
const fig = terrain(el, { intensity: 0.8 });   // (el: HTMLElement, options?) => { update, destroy }
fig.update({ intensity: 0.3 });   // a key set to undefined goes back to its default; a key you leave out stays as it is
fig.destroy();                    // removes only what it added (the svg, the live region, its attributes); safe to call twice
```
- The figure draws into `el` at **the element's width and a 5:4 aspect ratio**. Its CSS gives `[data-hairline]` `display:block; aspect-ratio:5/4; position:relative`, so **you must give `el` a width** (or put it in a sized grid cell). The SVG viewBox is `0 0 400 320`.
- Calling a figure again on the same element destroys the earlier one first.
- It throws without a DOM. Call it after the element exists: in `useEffect`, in `onMount`, or in a module script placed after the element.
- It has the shape of a Svelte action, so `use:terrain={{ intensity }}` works as written.
- On first mount it injects its stylesheet once per document or shadow root (adoptedStyleSheets, or `<style data-hairline-style>` as a fallback). Every selector sits inside `:where()`, so any rule of yours wins without `!important`.

**React** (a client module, so a Server Component can render it directly):
```tsx
import { Terrain, Sieve } from "@lucasmarkes/hairline/react";
<Terrain intensity={0.7} theme="auto" onRead={(t) => setRead(t)} className="w-full" />
```
The component renders one `<div style="aspect-ratio:5/4">` and mounts in a layout effect. It mounts **once**: a changed prop reaches the figure through `update`, and `onRead` goes through a ref, so an inline arrow function never remounts it. It takes every `<div>` prop except `children`, forwards its ref, and `aria-label` works as `label`. On the server it renders an empty 5:4 box, so nothing shifts when the figure draws. Exported types: `Figure`, `HairlineOptions`, and `HairlineProps` from /react.

## Options (all optional, the same for all 27)

| Option | Type | Default | Notes |
|---|---|---|---|
| `intensity` | number | `0.5` | 0 is subtle, 1 is strong. Values outside 0…1 are clamped. Numeric strings are parsed. Anything else (NaN, null, an object) becomes 0.5. Each figure maps it to its own number along two straight lines that meet at 0.5 (see the lo/mid/hi column below). |
| `theme` | `"auto"\|"light"\|"dark"` | `"auto"` | auto checks, in order: an ancestor with class `dark` or `[data-theme="dark"]`, then the page's `color-scheme` through `light-dark()`, then light. light and dark set `data-hairline-theme` on the element. |
| `label` | string | figure's English description | The accessible name. It is set as `aria-label` unless the host already has `aria-labelledby`. |
| `onRead` | `(text) => void` | none | Receives the figure's caption every time it changes. It is called once at mount with the rest caption, then with values like `cell 4·4`, `03` or `rate 0.20×`. |

The host gets `data-hairline="<id>"` and `role="img"` (Riffle is the exception: `role="group" tabindex="0"`, with an `aria-live` span, and the arrow keys walk its cards).

## The 27 figures

Each figure exists as `fn` (vanilla) and `Name` (React). The "intensity" column shows the figure's internal number at intensity 0 / 0.5 / 1. The "rest" column is the caption `onRead` gets at mount. Shelves follow the site's order.

| fn / Name | Shelf | What it is | Higher intensity | 0 / .5 / 1 | rest |
|---|---|---|---|---|---|
| `exploded` Exploded | Interfaces | An app window in four layers. Moving across opens the gap; moving down picks a layer. | The layers open further. | gap 12/28/40 | `""` |
| `terrain` Terrain | Data | 81 pillars on a plinth that rise around the pointer and settle into a dune with two rises. | A wider area rises. | radius 1.5/3/5 cells | `rest` |
| `phosphor` Phosphor | Data | A 7×7 dot matrix playing a loop. Where the pointer paints, the dots fade like phosphor. Ambient. | The trail lingers longer. | 150/520/1500 ms | `loop` |
| `riffle` Riffle | Data | A tray of eight cards. The card under the pointer stands up; the arrow keys walk the cards. | The ripple spreads further. | stagger 0/40/90 ms | `rest` |
| `slow` Slow | Machines | Crates riding a belt through a gate. Hovering slows the clock without stopping it. Ambient. | Time slows more. | rate 0.6/0.2/0.05× | `rate 1.00×` |
| `turntable` Turntable | Machines | Blocks on a turntable. A flick spins it, and it settles on the nearest quarter turn. | The spin coasts longer. | 200/650/1500 ms | `az 045° · el 30°` |
| `elevator` Elevator | Machines | Four floors beside an open shaft. The pointer's height picks a floor and the car travels there. | The car moves faster. | stiffness 40/100/220 | `rest` |
| `keyboard` Keyboard | Devices | A sixty-key board. The key under the pointer sinks and its neighbours follow it down. | A wider patch sinks. | 1/2/3.5 keys | `rest` |
| `phone` Phone | Devices | A phone in layers: glass, board, battery, shell. Across opens the gap; down picks a layer. | The layers open further. | gap 16/28/40 | `rest` |
| `laptop` Laptop | Devices | A thin laptop. The pointer's height sets the lid, which follows on a spring. | The lid opens wider. | 100/125/150° | `rest` |
| `terminal` Terminal | Coding | A terminal's history in rows. The pointer's height scrolls back and the line under it lifts. | The lift spreads further. | 1/2/3.5 lines | `rest` |
| `cabinet` Cabinet | Coding | A rack of twelve blades, a few half out. The pointer's height pulls the nearest ones out. | More blades come out. | 1.5/3/5 blades | `rest` |
| `branches` Branches | Coding | A commit graph forking off main and merging back. The commit under the pointer rises, then its history. | More history rises. | 1/3/6 commits | `rest` |
| `vault` Vault | Security | A vault door with a dial and three bolts. Circling turns the dial, and on 40 the bolts draw back. | The dial coasts longer. | 250/600/1500 ms | `rest` |
| `lockers` Lockers | Security | Twelve lockers, one ajar at rest. The one under the pointer opens and the open one shuts. | The door opens wider. | 55/90/120° | `rest` |
| `padlock` Padlock | Security | A padlock. As the pointer nears, the shackle lifts out and swings open. | It swings further. | 45/90/100° | `rest` |
| `patch` Patch | Connectivity | A patch panel of 24 ports. The cable under the pointer lifts and its neighbours lean away. | The lean spreads further. | 1/2.5/5 ports | `rest` |
| `dish` Dish | Connectivity | A parabolic dish on a two-axis gimbal. The pointer aims it and it follows on a spring. | It swings further. | 30/50/70° | `rest` |
| `router` Router | Connectivity | A wifi router whose antennas lean toward the pointer, the nearest most. | The lean spreads further. | 0.5/1.5/3 antennas | `rest` |
| `loupe` Loupe | Empty | A stand loupe on a blank ruled sheet. It drags along and the rules pass enlarged, with nothing between them. | It magnifies more. | 1.3/1.8/2.6× | `rest` |
| `sieve` Sieve | Empty | Three test sieves over a pan. The pointer's height lifts one clear, and every mesh is bare. | The gap opens further. | 6/14/24 | `rest` |
| `rail` Rail | Empty | A garment rail with seven bare hangers that rock away from the pointer and settle. | It reaches more hangers. | 1/2/3.5 hangers | `rest` |
| `plug` Plug | Empty | A wall socket, and a plug on the floor. The pointer draws the plug up, but it stops short and falls back. | It comes closer. | 0.35/0.6/0.9 of the way | `rest` |
| `query` Query | Empty | A question mark built as a bent bar over a loose ball. The hook turns toward the pointer and the ball rolls after it. | The hook turns further. | 20/40/55° | `rest` |
| `drawer` Drawer | Empty | Three filing drawers. The pointer's height opens one, showing two dividers and nothing between them. | It opens further. | 12/22/34 | `rest` |
| `basket` Basket | Empty | A wire basket under a bail handle. It tilts toward the pointer to show its bare floor. | It tilts further. | 8/16/28° | `rest` |
| `plot` Plot | Empty | A bar chart with no data: seven flat tabs that lift a little near the pointer and drop back to zero. | The tabs lift higher. | 3/6/12 | `rest` |

Phosphor and Slow are the only figures that move on their own. Under `prefers-reduced-motion` both hold still, and every figure still answers the pointer.

## Theme

Set any of these six custom properties on the figure or on any ancestor:

| Property | Light default | Dark default | Role |
|---|---|---|---|
| `--hairline-plate` | `#ffffff` | `#08090a` | Fill of every plate. **It must equal the background the figure sits on**, because plates are opaque so they can hide what's behind them. |
| `--hairline-hi` | `#232327` | `#d0d6e0` | The lit stroke: what's picked, a dot that's on. |
| `--hairline-edge` | `#a4a4ac` | `#5b5d64` | Silhouettes, and dots at half strength. |
| `--hairline-mid` | `#c3c3c9` | `#3e3e44` | Every other stroke. |
| `--hairline-lo` | `#e0e0e4` | `#29292d` | What recedes: guides, dots that are off. |
| `--hairline-stroke` | `0.9` | `0.9` | Stroke width in CSS px at any size (`vector-effect: non-scaling-stroke`). |

On a tinted background (a grey like `#f5f6f8`, a card, anything that is neither `#fff` nor `#08090a`), set `--hairline-plate` to that colour, or the plates show as white boxes. The palette is grey only. Change the hues through these properties and never with CSS filters.

## Minimal standalone page (verified: renders and answers the pointer, no console errors)

```html
<!doctype html><meta charset="utf-8"><title>hairline</title>
<style>body{margin:40px;background:#fff} .row{display:grid;grid-template-columns:repeat(3,260px);gap:16px} .row>div{--hairline-plate:#fff}</style>
<div class="row"><div id="a"></div><div id="b"></div><div id="c"></div></div>
<label>intensity <input id="i" type="range" min="0" max="1" step="0.01" value="0.5"></label> <code id="r"></code>
<script type="module">
  import { terrain, riffle, sieve } from "https://cdn.jsdelivr.net/npm/@lucasmarkes/hairline@0.3.0/dist/index.js";
  const figs = [terrain(a, { onRead: (t) => (r.textContent = t) }), riffle(b), sieve(c)];
  i.oninput = () => figs.forEach((f) => f.update({ intensity: +i.value }));
</script>
```
(Element ids become globals, which is why `a`, `b` and `i` work without lookups. In real code, use `getElementById`.)

## Recreating the hairline.lucasmarkes.com demo (the /figures page)

In v0.3.0 the site's **root `/` is a hero**: the headline "Line drawings that *answer* the pointer.", an npm pill, and a self-assembling window that is a site-only drawing, not a package figure. The demo with **a grid of live figures and the intensity slider is `/figures`**, with a tile picked. A verified, near pixel-identical rebuild ships at `references/demo-figures-page.html`. Copy that file whole. If you only have this SKILL.md, build it from this spec:

- **Fonts** (Google Fonts): Geist 400/500 (body, 14px/1.6), Geist Mono (counts, slider, code), Instrument Serif italic (only the word *draws*). Fallbacks: `Geist, system-ui, sans-serif`; `"Geist Mono", ui-monospace, monospace`; `"Instrument Serif", Georgia, serif`. **Colours:** canvas `#fff`, stone `#f4f4f4`, ink `#0a0a0a`, muted `#737373`, faint `#a3a3a3`, line `rgba(0,0,0,.07)`. Pure greys.
- **Top bar:** sticky, 54px, padding `0 max(28px, calc((100% - 1080px)/2 + 28px))`, white at 82% with `backdrop-filter: blur(12px)`. On the left, "hairline" (15px/500, letter-spacing -.02em) with "v0.3.0" (12px muted). On the right, Figures, Skill, Docs, Inspo (13px muted, links 30px tall with 10px padding) and a 16px GitHub mark.
- **Layout:** `main` has max-width 1080px, centred, padding `56px 28px 96px`. At 1100px and wider it's a grid of `200px minmax(0,760px)` with a 60px column gap.
- **Left rail** (sticky at 110px): rows 34px tall, radius 9px, 13px muted text, a 16px icon (16×16 viewBox, 1.5 stroke, a fill at 20% opacity, grey at 45% opacity unless pressed, when it takes the shelf colour), and a count right-aligned in 11.5px mono faint. The rows are: All 30 (pressed, `#f4f4f4` plate, ink), Interfaces 1, Data 3, Machines 3, Devices 3, Coding 3, Security 3, Connectivity 3, Empty 8, Marks 3. Shelf colours: Interfaces `#3b82f6`, Data `#8b5cf6`, Machines `#f59e0b`, Devices `#10b981`, Coding `#0ea5e9`, Security `#ef4444`, Connectivity `#ec4899`, Empty `#64748b`, Marks `#f97316`.
- **Header:** h1 is 16px/500, "Every figure, by what it *draws*." Below it, a muted lede (margin-top 12px, max 60ch): "Eight shelves, twenty-seven figures, grouped by what they draw. They ship in the package, but they are here to show what a figure can be: the [/hairline-create] skill draws your own. Pick one to see it large and copy its code. A last shelf holds three the skill drew from a company's mark." (The link is ink-coloured and underlined with a faint underline offset 4px.)
- **Shelves:** each `section` has padding-top 56px and gap 14px. Its head is the title (14px/500) followed by "1 of 1" in 12px mono faint. The grid is `repeat(auto-fill, minmax(220px,1fr))` with a 14px gap, and shelves come in the table order above.
- **Tile:** white, radius 14px, `box-shadow: inset 0 0 0 1px #f4f4f4, 0 1px 2px #00000008, 0 10px 28px -16px #00000024`. The stage is `aspect-ratio:5/4; --hairline-plate:#fff` with the live figure inside. Below it, a foot with `padding:10px 14px 12px; border-top:1px solid var(--line)` and the name in 13.5px/500. The picked tile gets `inset 0 0 0 1.5px #0a0a0a` instead of the stone ring.
- **Drawer** (opens on Terrain): `position:fixed; inset:68px 14px 14px auto; width:360px; padding:18px 18px 22px; radius 16px; box-shadow: 0 1px 2px #00000008, 0 2px 6px #00000008, 0 32px 64px -34px #00000038, 0 0 0 1px var(--line)`, laid out as a grid with gap 16px and `grid-template-columns:minmax(0,1fr)` (without it the large figure and code card overflow the 360px width). From top to bottom it holds:
  - the name (16px/500) with a × button (30px round, muted), and under the name the shelf chip (12.5px muted, with the shelf icon in its colour);
  - a large stage (radius 12px, `inset 0 0 0 1px #f4f4f4`);
  - the summary (13.5px/1.55 muted) followed by **Higher intensity:** and the stronger sentence (bold in ink);
  - the slider row: a grid of `auto 1fr auto` with gap 12px, set in 12px mono muted, reading `intensity`, then the range input, then the value as `0.50` (`toFixed(2)`). The track is 1.5px `#e5e5e5`. The thumb is 14px, white, with `box-shadow: 0 0 0 1px #0a0a0a` and `margin-top:-6.25px` (`appearance:none`);
  - `reads` followed by the onRead text in 11.5px mono ink;
  - a code card (radius 12px, card shadow) with React / Vanilla / CDN tabs (13px/500, the selected tab gets the card shadow), the file name on the right (`app/page.tsx`, `main.ts` or `index.html`), and a copy icon. The code is 12.5px/1.65 mono with line numbers in faint.
- **Behaviour:** mount one figure per tile, and every tile is live. Clicking a tile destroys the drawer figure, mounts the picked one, resets the slider to 0.5, and marks the tile as picked. The slider calls `big.update({ intensity })`.

## Gotchas

- A figure with no width collapses to 0×0. Give the host a width or put it in a grid cell.
- A wrong `--hairline-plate` shows as white boxes on a non-white background.
- `theme:"auto"` on a dark page that doesn't use a `.dark` class or `color-scheme: dark` renders light strokes for a light background. Pass `theme:"dark"` explicitly, or set `color-scheme`.
- In React, don't key the component on intensity. Let props flow; it was built to mount once.
- Don't wrap Riffle in a `<button>`, because it is its own focusable group.
- All figures share one requestAnimationFrame loop that sleeps off screen and at rest. Dozens on a page are fine (the site runs all 27).

## Make a new figure (vendored hairline-create)

Use this when someone asks for a figure the package lacks (`/hairline-create a sales funnel`). Follow `references/hairline-create/UPSTREAM-SKILL.md` exactly. In short:
1. **Concept.** Read `concepts.md` and offer 2–3 one-line concepts in the form "**Name.** object · what the pointer does · read-out", then wait for a pick. A concept is an object you could put on a desk, not a diagram. For an empty state, draw the tool holding nothing.
2. **Build.** Read `rules.md` (ten rules: hit areas don't move; stagger by distance; clamp the reach; the stroke is the only highlight; rest is designed; paint back to front; loops sleep; 700ms tween for *which* and a spring k100 c18 for *where*; round every corner and draw less; no words in the figure). Read only the index at the top of `kernel.js` (the `HL` API) and the nearer example (`examples/terrain.js` for a field, `examples/riffle.js` for items). Write `<name>.js` ending with `hairline({ name, means, rules, range:[lo,mid,hi], mount })`, at most 200 lines. Never edit `kernel.js` or `bench.html`.
3. **Check.** Run `node references/hairline-create/build.mjs <name>.js` to get `hairline-<name>.html`, then `node .../validate.mjs hairline-<name>.html` (verified to pass on the terrain example), then `node .../look.mjs <name>.js --answer x,y,z --edge x,y,z` for the eight-shot sheet. That last step installs playwright-core once into `~/.cache/hairline-look`. Answer `look.md`'s 13 questions.
4. **Hand over** one dependency-free `hairline-<name>.html`, along with the metaphor, the rules it leans on, and anything you could not verify.

A custom figure is a page with its own kernel copy, not an npm export. To use one in an app, copy its `mount` and the kernel into a module.

## Verify before claiming done

Open the page or app in Playwright at 1400×900. Wait about 1.5s, because springs settle in about a second. Check that `document.querySelectorAll('[data-hairline] svg').length` equals the number of figures you mounted. Hover a figure and check that the onRead text changes from `rest` (Terrain gives `cell i·j`). Move the slider and check that the drawing changes. Confirm there are no console errors. Then screenshot it and look at the image.
