# Game Feel, Onboarding, and Metrics/Playtesting — Research Dossier

Compiled 2026-09-26. Sources cited inline; "no published number" flagged where the literature
is qualitative rather than quantitative (common for juice/hit-stop — see caveats).

---

## PART 1 — GAME FEEL / JUICE

### 1.1 Foundational texts

- **Steve Swink, *Game Feel: A Game Designer's Guide to Virtual Sensation*** (Morgan Kaufmann,
  2008). Establishes "three building blocks of game feel": **input** (the control scheme),
  **response** (how the game reacts, incl. friction/momentum/animation), and **context**
  (level design, environment, embellishments/juice). Feel is "real-time control of virtual
  objects in a simulated space, with interactions emphasized by polish." Full PDF:
  https://gamifique.files.wordpress.com/2011/11/2-game-feel.pdf ·
  https://www.sciencedirect.com/book/monograph/9780123743282/game-feel
- **Martin Jonasson & Petri Purho — "Juice It or Lose It"** (GDC 2012, GDC Europe).
  Video: https://www.youtube.com/watch?v=Fy0aCDmgnxg · GDC Vault:
  https://gdcvault.com/play/1016487/Juice-It-or-Lose . Live-demo talk that takes a bare Breakout
  clone and incrementally layers **tweening, particles, sound, and screen effects** until the
  same input/output logic "overflows with life" — the point being that juice is cheap
  (days, not months) and separable from core mechanics. Quote used to define the term: "the
  juicier your game is, the more fun it is to play." No public transcript with numeric values
  survives outside the video itself (a "coming soon" placeholder page was checked and had no
  content: gamejuice.co.uk/articles/juice-it-or-lose-it-lessons — treat as unavailable, not a
  source).
- **Jan Willem Nijman (Vlambeer) — "The Art of Screenshake"** (INDIGO Classes 2013, later
  reprised at GDC/Fantastic Arcade). Establishes screenshake, hit-stop/freeze-frames, knockback,
  and "juice" as a coherent design vocabulary for action games (Nuclear Throne, Luftrausers,
  Ridiculous Fishing). Coverage: gamedeveloper.com/design/vlambeer-co-founder-shares-advice-on-building-better-action-games ·
  roblog.co.uk/2024/03/juicy-games/. **Caveat:** the talk is demo-driven (live tweaking on stage);
  no official published numeric table of shake amplitude/decay exists from Vlambeer. Community
  implementations (see 1.4) converge on parameters below, but attribute them to derived/typical
  practice, not a Vlambeer-published spec — flagged accordingly.

### 1.2 Hit-stop (freeze-frames)

- **Mechanism:** briefly freezing (or near-freezing) both attacker and defender for a handful of
  frames on impact, to sell weight and give the hit a "beat." Source: multiple game-dev
  explainers, e.g. shane-sicienski.com/blog (Capcom beat-em-up survey), glossary.infil.net
  (fighting-game glossary — "frames of hitstop exist outside the standard startup/active/recovery
  measurement").
- **Concrete published numbers found:**
  - *Guilty Gear Xrd -SIGN-*: light attacks freeze animation for **7 frames**, heavy attacks for
    **~10 frames** (cited in the arXiv impact-feel study below).
  - *Street Fighter V* dev seminar: "we're using **8 frames** of hit stop" as a worked example in
    the official Capcom "SF Seminar" column — game.capcom.com/cfn/sfv/column/131545.
  - *Dragon Ball FighterZ*: opponent animation freezes "for a whole second" during an ultimate
    charge-up (extreme/outlier case, not a general hit).
  - **Masahiro Sakurai** (Famitsu column, translated at sourcegaming.info/2015/11/11): hitstop
    scales with damage dealt but is **capped** — "regardless of how much damage an attack
    inflicts, the hitstop period will never exceed this limit." He deliberately shortened Ryu's
    hitstop versus the Street Fighter II original because Smash is often free-for-all (frozen
    players are vulnerable to a third attacker); projectiles get reduced hitstop; electric
    attacks get automatically increased hitstop; grounded characters "vibrate" horizontally
    during freeze, airborne characters vertically. No exact frame table published.
  - **arXiv 2208.06155 "What Features Influence Impact Feel? A Study of Impact Sensation Design
    Patterns"** (2022) — surveyed 40 games' combat systems; found **hit-stop presence,
    sound coherence (audio-visual sync), and camera control** are the three features most
    correlated with player-perceived impact in Steam review text-mining, but explicitly did
    **not** find a quantified duration-vs-impact correlation — presence/absence mattered more
    than exact length in their qualitative coding. https://arxiv.org/html/2208.06155v3
- **Practical rule of thumb** (not from a single named source, but consistent across the above):
  **short hits (jabs, bullets) ≈ 2–4 frames; heavy hits ≈ 6–10 frames; special/finisher hits can
  go to 15–20+ frames or even a full second for a dramatic beat** — scale hit-stop with damage/
  weight, and cap it so multiplayer/free-for-all fairness isn't broken (Sakurai's explicit design
  constraint above).

### 1.3 Squash & stretch

- One of Disney's 12 animation principles (Thomas & Johnston, *The Illusion of Life*), adapted to
  games: "compressing or elongating a character/object to emphasize weight, speed, and impact
  while conserving apparent volume." On landing/impact, squash flat; at max velocity, stretch
  along the movement vector. Sources: animationmentor.com/blog/squash-and-stretch-the-12-basic-principles-of-animation/ ·
  gamedesign.gg/glossary/squash-and-stretch/ · Josh W. Comeau's interactive explainer
  (joshwcomeau.com/animation/squash-and-stretch/) · Chris Totten, "12 Principles for Game
  Animation" (totter87.medium.com/12-principles-for-game-animation-a9137ef44345) — the games-
  specific adaptation of the 12 principles, useful because arcade/action games apply it to non-
  organic objects (bullets, crates, UI elements) as well as characters.
- No universal numeric ratio is published (it's an art-directed exaggeration, tuned by eye), but
  the consistent guidance is: **conserve volume** (stretch on one axis, compress the perpendicular
  axis proportionally) and **keep it fast** — squash/stretch reads as "alive" only when it resolves
  within a few frames, not as a lingering deformation.

### 1.4 Screenshake

- Community-standard implementation pattern (widely attributed to Vlambeer-style juice, refined
  in shader/tween libraries): **"trauma" model** — maintain a `trauma` value (0–1) that increases
  on impact events and **decays linearly or exponentially per frame/second** (typical decay rate
  cited across tutorials: trauma decreases at roughly **1.0–3.0 per second**, i.e. a shake fully
  resolves in well under a second), then **shake amplitude = trauma², or trauma³** (squaring/
  cubing so small hits barely shake but big hits ramp up fast — this nonlinearity is the load-
  bearing trick, not the raw amplitude number). Offsets are typically driven by simplex/Perlin
  noise sampled at a frequency in the 20–40 Hz range rather than pure random jitter, to avoid a
  buzzing look. (This pattern is the de-facto standard taught in most "juice" tutorials that cite
  Vlambeer/Jonasson-Purho as origin, though as noted in 1.1 there is no single canonical published
  source with an official amplitude/decay table — treat the numbers above as **widely-replicated
  community convention**, not a primary-source spec.)
- Practical constraints repeatedly stressed: shake should be **short and camera-only** (never
  move actual game-object hitboxes), should **not exceed a duration where players lose track of
  their character**, and should scale down or disable entirely for accessibility (motion
  sensitivity) — echoed in Celeste's own settings (screen-shake toggle) and general accessibility
  guidance.

### 1.5 Coyote time & jump buffering

- **Coyote time**: the player can still jump for a short window *after* walking off a ledge
  (named for the cartoon-physics moment before Wile E. Coyote falls). **Jump buffering**: an
  early jump press is *remembered* for a short window and executes the instant the player lands/
  becomes eligible, instead of being dropped. Together they compensate for human reaction-time
  imprecision without the computer's frame-perfect requirement feeling unfair. Sources:
  devforum.roblox.com/t/coyote-time-and-jump-buffer-for-platformer-games/2809273 ·
  gamedesignskills.com/game-design/platformer/ ("Celeste uses jump buffering and coyote time so
  the game doesn't eat player inputs for imperfect execution").
- **Celeste's own numbers** (Maddy Thorson, "Celeste & Forgiveness," maddythorson.medium.com/
  celeste-forgiveness-31e4a40399f1 — the primary-source designer writeup):
  1. **Coyote Time** — jump still registers for a short grace period after leaving a ledge.
  2. **Jump Buffering** — pressing/holding jump slightly before landing still triggers the jump.
  3. Plus **corner correction** (nudging the player around a corner they almost cleared) and other
     "forgiveness" mechanics — Thorson's framing: these don't make the game *easier*, they make
     controls match player *intent* rather than literal input timing.
  - Community/technical breakdowns converge on **~4–5 frames** for Celeste's coyote time window
    and **~4 frames** for jump buffering (h5rift.com technical manifesto cites "approximately 5
    frames" coyote and "up to 4 frames before touching the ground" for jump buffer; a Reddit
    thread on r/gamedesign independently states "In Celeste you can jump up to 5 frames after
    leaving a ledge"). At Celeste's 60fps, that's roughly **65–85ms** — note these are fan/
    technical-analysis figures reverse-engineered from the (open-source-adjacent, heavily
    datamined) game, not an official Maddy Makes Games spec sheet, so treat as **strong
    consensus estimate**, not verbatim developer-published constant.
  - Celeste's **Extended Variant Mode** mod exposes coyote time as a tunable, defaulting to
    **0.1 seconds (100ms)** — gamebanana.com/mods/53650 — giving an independent, mod-tool-
    documented figure in the same ballpark as the frame-count estimates above.
  - General industry rule of thumb repeated across multiple tutorials (Godot/Unity coyote-time
    guides): **coyote time ≈ 3–6 frames (~50–100ms at 60fps); jump buffer ≈ 3–8 frames**, tuned
    per game feel — tighter for precision platformers, looser for casual/mobile.

### 1.6 Input buffering (general, beyond jump)

- In fighting games, buffer windows are commonly **5–10 frames** for a queued special-move input
  (gamedev.stackexchange.com/questions/43708) — attacks tolerate wider buffers (dev forum post
  cites **6–8 frames** tolerable for attack inputs) while dodge/parry inputs need **tighter
  windows (~3–4 frames)** to avoid feeling "sticky"/unresponsive (moonjump.com forum thread, a
  practitioner report, not an academic source — flagged as anecdotal but consistent with fighting-
  game glossary definitions at glossary.infil.net).
- Mechanism: record every input with a timestamp/frame number into a small FIFO queue; when the
  game becomes able to accept that action, check the queue instead of only the current frame's
  raw input (wayline.io/blog/input-buffering-fighting-games — clear step-by-step explainer).

### 1.7 Celeste's assist mode (accessibility, not just forgiveness)

- Beyond coyote/buffer, Celeste ships an **Assist Mode** exposing game-speed slider, infinite
  stamina, invincibility, and dash-count toggles — an explicit design statement that "difficulty"
  and "who gets to finish the game" are separable, cited widely as a model for other games'
  accessibility settings (referenced across the Celeste sources above; Thorson's broader public
  design philosophy per puzzlebyrinth.com/en/articles/designer-thorson: "keep it hard, make it
  kind").

### 1.8 "Fun to just move" — Nintendo / Mario 64 garden test

- **Shigeru Miyamoto**, developing *Super Mario 64* (1996), spent months getting Mario's movement
  (acceleration, friction, turning, jump arc) to feel good *before* building real levels — testing
  it in a large, empty "garden" test level so the team could judge whether simply walking, running,
  and jumping Mario around was enjoyable in isolation, independent of any objective or level
  design. Source (developer interview, translated): shmuplations.com/mario64/ — Miyamoto: "One of
  our big development themes was letting [players] move Mario and Luigi around with the 3D control
  stick... we wanted to make a game where just moving Mario around was fun." Secondary analysis:
  sourcegaming.info/2017/06/21/15864/ ("Holism: The Wonderful Worlds of Super Mario 64" — "the
  months Miyamoto spent perfecting his friction and weight in a 'garden' he built just to test
  them paid off"). This is the canonical "movement-first" design story cited across the industry
  as the origin of "does it feel good to just move, before you've added a single goal."

---

## PART 2 — ONBOARDING / FTUE

### 2.1 First 30 seconds / first 5 minutes

- Multiple 2025–2026 mobile-UX sources converge on the **first 30 seconds** as the make-or-break
  window for a mobile game/app: "stacking three choices on one screen in the first 30 seconds
  splits attention before the player has any context" — punchev.com/blog/game-onboarding-ux-best-practices.
  A parallel non-game UX piece: "your app's first 30 seconds determine its fate... users judge
  apps like restaurants, through instant sensory impressions" — medium.com/@tekinalper (Aug 2025).
- **"Hello World principle"**: engineer a tiny, unmistakable win inside the first 30 seconds to
  activate an early sense of competence/progress (framed via Yu-kai Chou's "Core Drive 2:
  Development & Accomplishment" octalysis vocabulary) — professorgame.com/podcast/443/.
- **Time-to-Fun (TTF)**: the amount of time from install/launch to the player's first genuine
  moment of enjoyment/value. Framed as games' answer to "time-to-value" in SaaS. Rovio
  (Angry Birds) reportedly lists TTF as a North Star metric in job postings for game designers —
  cyprus-mail.com/2021/06/12/shorter-time-to-fun-video-games/ ; jonlai.co/time-to-fun ("games
  deliver value quickly and unpack complexity slowly" — apps/games compete for the same finite
  attention as every other app on the home screen, so slow ramps lose to instant ones).
  etchuk.com/play/blog/time-to-fun-how-to-master-the-art-of-player-retention (practical framing:
  every menu, load screen, and forced tutorial step is *TTF debt*).

### 2.2 Teach-by-doing: World 1-1 as the canonical case study

- **Super Mario Bros. World 1-1** (1985) is the most cited teach-by-doing tutorial level in game
  design pedagogy. Wikipedia (en.wikipedia.org/wiki/World_1-1): "designed by Shigeru Miyamoto to
  be a tutorial for new players, orienting them to platform jumping and the rest of the game" —
  entirely through **level geometry and enemy placement**, with **zero text or explicit
  instructions**.
- Canonical structure (widely documented, e.g. nocontextculture.com and mainstream404.wordpress.com
  breakdowns, plus IGN's 2025 Miyamoto-narrated retrospective ign.com/articles/miyamoto-explains-how-super-mario-bros-world-1-1-was-created):
  1. Mario starts facing right with **nothing else on screen** — the only possible action is to
     move right, which the player does instinctively, immediately teaching "right = forward."
  2. The **first Goomba** appears close enough that a naive player who just walks right will
     likely bump it and lose a coin/get hurt in a *safe, low-stakes* way — teaching "enemies are
     dangerous" cheaply, early, with no death.
  3. The first **"?" block** is placed at a height Mario can only hit by jumping *into* it,
     teaching jump-to-interact simultaneously with movement.
  4. A **pipe** shortly after teaches vertical traversal/warping optionally (skippable — an
     early example of "the tutorial is the level, and it's optional depth, not a gate").
  5. A staircase of blocks culminating in a **gap and a flag** teaches the jump arc needed for
     the goal itself, right before the player needs it for real.
- Miyamoto's own framing (per the IGN piece and Game Developer's "How Miyamoto built Super Mario
  Bros.' legendary World 1-1", gamedeveloper.com/design/how-miyamoto-built-i-super-mario-bros-i-legendary-world-1-1):
  World 1-1 was built so the player would **"gradually and naturally understand what they're
  doing"** without being told — the level *is* the tutorial, and every teaching moment doubles as
  real, non-throwaway gameplay (nothing is quarantined into a "tutorial area" that gets discarded).

### 2.3 Tutorial anti-patterns

Compiled from UX/game-design practitioner sources (no single canonical academic list, but
consistent themes across FTUE literature and the "dark patterns in games" academic paper cited
below):
- **Text-wall/pop-up tutorials** that stop gameplay to explain a mechanic instead of teaching it
  through a safe, real gameplay moment (the World 1-1 alternative in 2.2).
- **Forced tutorials with no skip**, imposed on returning/experienced players every session —
  directly costs Time-to-Fun for anyone who already knows the game.
- **Front-loading every mechanic** before the player has a reason to care about any of them
  (violates "teach one thing at a time, right before it's needed").
- **Explaining instead of demonstrating** — telling the player "press X to jump" rather than
  placing them where jumping is the obvious next move (this is precisely what a silent
  playtest, §3.3, is designed to catch: if you have to explain your tutorial out loud, it has
  failed).
- Related academic framing: Zagal et al., **"Dark Patterns in the Design of Games"** (FDG 2013,
  fdg2013.org/program/papers/paper06_zagal_etal.pdf) — coins "dark game design patterns," a
  broader category than pure onboarding but overlapping (e.g. patterns that manipulate rather
  than teach).

### 2.4 "The first session decides D1"

- Consistent with the metrics section below: multiple 2025–2026 benchmark write-ups explicitly
  connect onboarding quality to D1 outcomes — "onboarding is the most important retention lever
  the marketing team influences indirectly... if the first session doesn't deliver on what the ad
  promised, D1 collapses" (hubapps.team/blog/mobile-game-retention-strategies, 2026). A first-
  session/"Level 0 churn" funnel analysis (medium.com/@jesssong837, "Analyzing the First 60
  Seconds") frames the very first 60 seconds of a mobile game session as "a critical leak in the
  user funnel" worth instrumenting as its own funnel, separate from later-level funnels.

---

## PART 3 — METRICS & PLAYTESTING

### 3.1 Retention benchmarks by platform/percentile (GameAnalytics, 2025 data, published Aug 2026)

Source: **GameAnalytics — "2026 Mobile & PC Gaming Benchmarks"**
(gameanalytics.com/reports/2026-mobile-pc-gaming-benchmarks), dataset: 16,000+ mobile games / 9
regions / 1,000+ MAU threshold (mobile), 3,582 PC games / 100+ MAU / 4+ months live (PC). This
cycle's report does **not** break out by genre ("genre-level cuts aren't included this cycle" per
report, due to ongoing re-categorization) — genre-specific historical figures are given separately
below from the 2025 report and other trackers.

**Mobile — global, by percentile:**

| Metric | P25 | P50 (median) | P75 | P90 | P99 |
|---|---|---|---|---|---|
| D1 retention | 12.45% | ~22% | ~30% | ~40% | 64–68% |
| D7 retention | 1.67–1.94% | ~4% | 6–7% | 11–12% | 25–28% |
| D30 retention | <0.5% | 0.68–0.79% | 1.6–1.8% | n/a | 13–15% |
| Session length | — | 3.1–3.5 min | ~5.2 min | >8 min | 22–24 min |
| Sessions/day | 2.7 | 3.8–3.9 | 5.3–5.7 | ~9.6 | 12–14 |
| Daily playtime | — | ~12 min | 22–24 min | 40–42 min | 94–99 min |

**PC — global, by percentile:**

| Metric | P25 | P50 | P75 | P90 | P99 |
|---|---|---|---|---|---|
| D1 retention | ~3% | ~7% | 12–13% | 21–23% | 40–50% |
| D7 retention | <0.5% | 1.1–1.3% | 2.7–3.2% | 5.8–6.9% | 18–27% |
| D30 retention | 0% | 0.2–0.25% | 0.7–0.9% | ~2% | 10–16% |
| Session length | — | ~18 min | 30+ min | 50+ min | 100+ min |
| Sessions/day | — | 1.65–1.70 | ~2 | ~3 | 7–10 |

**Regional D1/D7/D30 (mobile, median/P90/P99)** — full table in report; e.g. North America
23.28% / 36.90% / 50.89% (D1), 4.97% / 12.58% / 24.78% (D7), 1.18% / 4.78% / 13.26% (D30); Europe
and Oceania post the highest medians across all three windows; Asia and South America the lowest
D1 medians (17.5% and 20.1% respectively).

**Trend context (2023→2024→2025):** GameAnalytics' prior-year reports show D1 retention has been
**declining year over year**: "in 2024, D1 retention rates dropped slightly, with the top 25% of
games achieving ~26–28% [down] from 28–29% in 2023" (gamedevreports.substack.com/p/gameanalytics-mobile-gaming-benchmarks,
citing the 2025 report); GameAnalytics' own historical average is cited elsewhere as **D1 ≈
26–28%, D7 ≈ 8%, D30 < 3%** for 2024 (blog.playio.co/dau-retention-analysis-mobile-games-2026).

**Other trackers (cross-check, same rough order of magnitude):**
- **Adjust/CORE MBA 2026 medians**: D1 25–26%, D7 11–13%, D30 5–7% — fintech apps top out D1 at
  ~30% (core-mba.pro/tool-hub/mobile-app-retention). Note this source aggregates across app
  categories, not games-only, so its medians run a bit higher than GameAnalytics' games-only D7/D30.
- **Pushwoosh Benchmarks Study 2025**: D7 retention 6.89% (iOS) dropping to 3.10% by D30; Android
  figures given as generally lower (pushwoosh.com/blog/increase-user-retention-rate/).
- **Segwise (2026)**: "cross-genre... 25 to 33% at D1, 6 to 14% at D7, and 1 to 7% at D30
  depending on genre" (segwise.ai/blog + x.com/segwise_ai — Aug 2026 post gives a single-number
  version: "~27% D1, 8–14% D7, ~3% D30").
- **Genre note (2025 GameAnalytics cycle, before genre cuts were dropped)**: "the best genres for
  medium- and long-term retention are board games, card games, puzzle, and casino games. Multiplayer
  projects lead only in session length" — gamedevreports.substack.com/p/gameanalytics-mobile-gaming-benchmarks.
- **Session length by genre (Adjust, cited in a 2026 market-stats roundup)**: action games ~43.8
  min/day, strategy ~37.5 min/day, racing ~16.3 min/day — illustrating how wildly session-length
  benchmarks split by genre, so a single cross-genre median should be treated as a rough anchor
  only (linkedin.com/pulse "Mobile Gaming Statistics 2026").

**How to read all of this as a solo/small dev:** treat GameAnalytics' median row (D1 ~22–27%, D7
~4–8%, D30 <1–3%) as "average," their P75/P90 rows as realistic stretch targets, and don't chase
P99 (64%+ D1) — those are outlier hits, not a normal target.

### 3.2 How small devs measure with no budget

- Free/low-cost stacks repeatedly recommended: **Firebase/GA4 + BigQuery** (SQL-free dashboards
  for retention/LTV/ARPDAU — ga4gameanalytics.com), **GameAnalytics' own free tier**
  (industry-standard funnels product, purpose-built for games — see 3.3), and various free-tier
  live-ops/analytics tool round-ups aimed specifically at indies (gamineai.com/resources/25-free-live-ops-analytics-tools-indie-games-2026-edition).
- **GameAnalytics' built-in funnel types** (docs.gameanalytics.com/products-and-features/analytics-iq/funnels/):
  an **Onboarding Funnel** ("measure each step in your FTUE and where players drop off") and a
  **Level Progression Funnel** ("track how players move through worlds/levels, highlighting
  where difficulty spikes may cause churn") — these are the two funnel types a solo dev should
  set up first, since they directly answer "where do people quit" without custom engineering.
- Practical framing from a practitioner blog (blog.gamemantra.ai/first-session-funnel-measuring-early-drop-off,
  2026): "a first-session funnel is only as useful as its steps are honest — break the opening
  experience into the smallest meaningful units a player passes through, then measure how many
  reach each one" — i.e. instrument *within* the first session (menu → tutorial step 1 → step 2 →
  first real choice → first death/win), not just D1/D7/D30, because by D1 the interesting churn
  has often already happened.
- **Analytics vs. playtesting, when to use which** (emhance.ai/blog — "Should I use analytics or
  playtesting to find out why players churn on day 1?"): "both, for different jobs — analytics
  shows you the exact point where players stop; playtesting shows you *why*." This is the
  cleanest one-line summary found in this research pass and is used as the spine of §3.5 below.

### 3.3 Playtesting method

- **Silent observation / "don't explain"**: the single most repeated rule across every
  playtesting how-to found in this pass: **do not explain the game, do not intervene, do not
  visibly react** while someone plays. If you find yourself explaining something mid-test,
  that's not a saved test — it's a **found bug in your onboarding**, logged as such.
  - "The most important rule in a playtesting session: do not explain, intervene, or visibly
    react. If you explain something when a player is confused, you have invalidated the test for
    that section." — flukz.org/devlog/playtesting-your-game/
  - "The golden rule of observation-based playtesting is: do not help. When a player gets stuck,
    resist every instinct to explain the mechanic or point to the button." — gtstu.com/playtest-indie-game-solo-developer/
  - "Do not explain the game beforehand. If a player needs instructions from you to understand
    the first ten minutes, your onboarding is broken." — closedbeta.substack.com/p/how-indie-studios-should-think-about
  - "A good playtest environment is usually non-intrusive: the developer observes silently,
    takes notes on where players struggle, and only offers [help] ..." — r/gamedev discussion,
    reddit.com/r/gamedev/comments/1mdmn4e
- **Think-aloud protocol** (Clayton Lewis, 1982, HCI usability method adapted to games): ask the
  player to narrate their thoughts continuously while playing, so you learn *why* they clicked
  something, not just *that* they did. Trade-off explicitly noted by practitioners: narrating
  changes cognitive load and can itself alter behavior, so it's best used for **early, rough
  builds** where you need "why," and dropped in favor of pure silent observation for **late-stage
  polish** where you need honest, undistorted flow. Sources: academic Oxford chapter
  (academic.oup.com/book/26677/chapter/195457270), gur.ucsc.edu/testing-methods (traces the
  method to Lewis 1982), and a practitioner counterpoint (linkedin.com/posts/stevebromley —
  "think-aloud has its place, but... moderated 1-to-1 playtesting [without narration] is often
  considered the gold standard because researchers can observe behavior and ask the right
  [follow-up] questions" after the fact instead of during).
- **What to watch for, specifically** (compiled across gamemaker8.com/design/playtests-that-improve-your-game/
  and gametradejournal.com/run-a-game-playtest-that-works/):
  - **The first death** — was it perceived as fair ("I get it, my fault") or unfair/confusing
    ("what just happened")? This single moment predicts a lot of early churn.
  - **The first quit** — the exact second/action right before someone puts the controller down or
    alt-tabs. Log the *context* (what screen, what just happened), not just that it happened.
  - **"One more" moments** — does the player, unprompted, reach for another turn/run/level without
    being told to? (Directly mirrored in the grey-box "find the fun" test in 3.4 — replay-without-
    being-asked is the single cleanest fun signal found in this whole research pass.)
  - Silence/confusion pauses, backtracking, repeated failed attempts at the same input, and
    verbal sighs/frustration cues (if observing in person) are the concrete "where it's broken"
    signals to log with a timestamp.
- **Schell Games' "Definitive Guide to Playtest Questions"** (schellgames.com/blog/the-definitive-guide-to-playtest-questions-for-video-game-playtesters)
  — a working studio's actual post-session question bank; useful as a template for the interview
  half of a session (after silent observation, ask open questions, not leading ones).

### 3.4 "Find the fun" prototyping (grey-box before art)

- **Grey-box / white-box prototyping**: build the core mechanic with placeholder
  cubes/capsules/primitives, *no art, no sound, no UI*, specifically so a mechanic has to prove
  itself as fun on its own merits rather than being carried by attractive art
  (leekon.studio/blog/finding-the-fun/ — direct quote: "before a single polished asset exists,
  the game has to be fun with cubes"). Standard three-step loop documented at that source:
  1. **One mechanic, one week** — smallest playable slice of just the core loop.
  2. **Hands-on Friday** — the whole team plus at least one outside tester (someone who's never
     seen the concept) plays it.
  3. **Keep / Twist / Kill** — decide to advance, iterate one targeted change for another week, or
     archive the idea and move on.
  - **Their fun test, verbatim**: "Does anyone replay it without prompting? ... if testers replay
    the loop without being asked, we have something. If they check their phone, we don't — and it
    only cost us a week to find out." — the single clearest operational definition of "found the
    fun" surfaced in this research.
- **Rami Ismail** (Vlambeer co-founder, indie consultant) — consistent public advice across talks
  and his "Levelling the Playing Field" resource site (ltpf.ramiismail.com/prototypes-and-vertical-slice/,
  ltpf.ramiismail.com/feedback/): distinguish a **Prototype** (answers one design question, throw-
  away code, not meant to look/feel like the final game) from a **Vertical Slice** (a polished
  representative sample meant to sell the whole game) — most indies conflate the two and waste
  time polishing a prototype or, conversely, treating a vertical slice as disposable. On
  feedback specifically: "practice getting feedback with smaller games, jam projects" before your
  real project, so you build the *skill* of taking feedback well on low-stakes work first. Recent
  LinkedIn post (Aug 2026, linkedin.com/posts/ramiismail): "playtest early, get feedback on your
  grey box... waiting on external validation during early prototyping is a momentum killer" —
  i.e. don't over-wait for a "real" test before you get *any* eyes on it.
- **Derek Yu** (Spelunky, UFO 50) — public design writing (derekyu.com/makegames/, the widely-
  circulated "Finishing a Game" post, video summary at youtube.com/watch?v=wlJ6oJChdbE) emphasizes
  starting from **arcade-style instant feedback loops**: prototype the smallest possible action-
  reaction pair first (the callie.zone case study on Yu frames this as tools/prototyping enabling
  fast iteration, not just for level generation but for "finding the fun" of the core interaction
  before content is built around it). His broader, widely-quoted advice (paraphrased across
  multiple secondary sources, since Yu himself writes more about finishing than pure fun-finding):
  ship something small and complete before attempting something big and ambitious — momentum and
  a track record of *finished* small games matters more early on than chasing an unproven big idea.
- **Valve's playtesting practice** (secondary sourcing — no single official Valve document found,
  but consistent across multiple independent accounts): Valve is repeatedly described as running
  extensive **silent, logged, observational playtests** during Half-Life/Half-Life 2 development
  — sitting behind testers, taking notes, using logging software to capture where players got
  stuck, and iterating heavily based on that data rather than developer intuition. Representative
  quotes: "Valve spent a tremendous amount of time playtesting [Half-Life], with logging software"
  (Quora response referencing public accounts) and "one of the key practices that Valve used to
  take their games from mediocre to great is Observational Testing. They call it Play Testing...
  [testers are] silently observed while notes are taken" (linkedin.com/pulse/how-dramatically-improve-your-product-andrew-rusling).
  Treat this as **well-corroborated industry lore**, not a primary Valve-published methodology
  doc — no official Valve playtesting whitepaper surfaced in this search pass.

### 3.5 Putting 3.1–3.4 together: analytics vs. playtesting division of labor

Per the emhance.ai framing (3.2): use **analytics/funnels** to find *where* players drop (which
funnel step, which level, which minute) at scale and continuously; use **silent
observational playtesting** (3.3) to find out *why*, in depth, on a small sample, especially
during the pre-launch/early-access period before you have funnel volume. Both are needed —
funnels without playtesting tell you "step 3 leaks 40%" without telling you it's because the jump
prompt is unreadable; playtesting without funnels risks over-indexing on the 5–10 people you
watched.

---

## ACTIONABLE SUMMARIES

### Juice / Game Feel Checklist (apply per action that matters — jump, hit, pickup, death)

- [ ] **Input** responds within 1 frame of press where possible (Swink's #1 building block —
      unresponsive controls is repeatedly named the #1 juice-killer, gamedeveloper.com "6 mistakes").
- [ ] **Hit-stop** on impacts: ~2–4 frames for light hits, ~6–10 frames for heavy hits, up to
      15–20+ frames (or a deliberate full-second freeze) for finishers/specials — scale with
      damage/weight, and **cap the max** so it never breaks multiplayer fairness (Sakurai's rule).
- [ ] **Screenshake**: drive off a decaying "trauma" value (not raw amplitude) so small hits barely
      shake and big hits ramp nonlinearly (amplitude ∝ trauma² or trauma³); resolve within well
      under a second; **camera-only**, never touches hitboxes; add an accessibility toggle.
- [ ] **Squash & stretch** on impact/launch, conserving apparent volume, resolving within a few
      frames — applies to bullets/props, not just characters.
- [ ] **Particles + sound** layered on every meaningful action (Jonasson/Purho's core demo) —
      cheap, fast to add, and separable from core-mechanic risk.
- [ ] **Nothing sits dead-still** on screen (idle animation, ambient particles) — "dead stillness"
      is a named juice-killer.
- [ ] **Coyote time** ≈ 3–6 frames (~50–100ms @60fps) after leaving a ledge; **jump buffer** ≈
      3–8 frames before landing; both tuned tighter for precision platformers, looser for casual.
- [ ] **Input buffering** for combo/attack inputs ≈ 5–10 frames tolerance; tighten to ~3–4 frames
      for parry/dodge-type inputs where over-buffering feels unresponsive.
- [ ] Playtest **just moving** (Mario 64 garden test) before you build a single real level —
      if walking/jumping/turning isn't fun in an empty room, no level design will save it.

### FTUE Checklist

- [ ] **First 30 seconds**: one clear goal, no more than one decision on screen at a time, an
      unmissable tiny win ("Hello World principle").
- [ ] **Teach through level geometry**, not text — replicate World 1-1's pattern: (1) force the
      one possible action, (2) let a low-stakes mistake teach a danger safely, (3) require the new
      skill to progress, immediately after introducing it, (4) never quarantine "tutorial content"
      as separate from real content.
- [ ] **No forced, un-skippable tutorial** on repeat sessions — every second here is Time-to-Fun
      debt for the returning/experienced player.
- [ ] Instrument the **first session as its own funnel** (menu → step 1 → step 2 → first real
      decision → first death/win) — most early churn is inside minute one, before D1 even applies.
- [ ] If you ever catch yourself explaining the tutorial out loud to a tester, that's a **logged
      onboarding bug**, not a saved playtest.

### Benchmark Table (mobile, GameAnalytics 2025 data / 2026 report, see 3.1 for full table + PC + regional splits)

| | D1 | D7 | D30 |
|---|---|---|---|
| Median (P50) | ~22% | ~4% | ~0.7–0.8% |
| Top 25% (P75) | ~30% | 6–7% | 1.6–1.8% |
| Top 10% (P90) | ~40% | 11–12% | n/a |
| Top 1% (P99) | 64–68% | 25–28% | 13–15% |

Median session length ~3.1–3.5 min, ~3.8–3.9 sessions/day (mobile). Cross-check with Adjust/
Segwise/Pushwoosh: same order of magnitude (D1 ~25–27%, D7 ~4–14%, D30 ~1–7%) — treat GameAnalytics
median row as your primary anchor since it's games-only and largest sample (16,000+ titles).

### 1-Page Playtest Protocol

1. **Recruit** 3–5 people per round who have **never seen the build** (friends/family for very
   early rounds are acceptable per Rami Ismail's "practice on low-stakes work" advice, but replace
   with strangers as soon as possible — internal-only testing is a known trap).
2. **Say nothing** before the session beyond a content/safety notice. No rules explanation, no
   "here's how it works." If the first ten minutes require your voice, that's the finding.
3. **Sit where you can see the screen and the player, not vice versa.** Take timestamped notes
   silently. Do not react, do not help, do not answer questions ("what do I do?" → "whatever you'd
   naturally try").
4. **Log four things continuously**: (a) any pause/confusion >3–5 seconds and what caused it, (b)
   the first death and whether the player's own reaction reads as "fair" or "confused," (c) the
   exact moment/context of quitting or disengaging (phone check, sigh, "can I stop"), (d) any
   unprompted "one more" behavior (reaching for another attempt without being asked).
5. **Only after the session ends**, switch to think-aloud-style follow-up questions (Schell Games'
   template is a good bank) — ask open questions ("what were you trying to do here?") not leading
   ones ("did you find the jump hard?").
6. **Decide**: Keep (advance as-is) / Twist (one targeted change, retest in a week) / Kill (archive)
   — per the grey-box loop in 3.4. The single deciding signal, if you can get nothing else: did
   anyone replay the loop without being asked to?
7. **Pair with analytics once you have any live volume**: set up an Onboarding Funnel and a Level
   Progression Funnel (GameAnalytics free tier or GA4/BigQuery) so you can see *where* at scale
   what you *saw why for* in the room with 5 people.

---

## SOURCE LIST (for quick reference)

Game Feel: sciencedirect.com/book/monograph/9780123743282 · gamifique.files.wordpress.com PDF ·
youtube.com/watch?v=Fy0aCDmgnxg (Jonasson/Purho) · gdcvault.com/play/1016487 ·
gamedeveloper.com/design/vlambeer-co-founder-shares-advice-on-building-better-action-games ·
arxiv.org/html/2208.06155v3 · sourcegaming.info/2015/11/11/thoughts-on-hitstop-sakurais-famitsu-column-vol-490-1 ·
game.capcom.com/cfn/sfv/column/131545 · glossary.infil.net · gamedesign.gg/glossary/squash-and-stretch ·
joshwcomeau.com/animation/squash-and-stretch · totter87.medium.com/12-principles-for-game-animation-a9137ef44345 ·
gamedeveloper.com/design/6-mistakes-that-ll-drain-the-juice-out-of-your-game ·
maddythorson.medium.com/celeste-forgiveness-31e4a40399f1 · h5rift.com (Celeste technical manifesto) ·
gamebanana.com/mods/53650 (Extended Variant Mode) · gamedesignskills.com/game-design/platformer ·
gamedev.stackexchange.com/questions/43708 · wayline.io/blog/input-buffering-fighting-games ·
shmuplations.com/mario64 · sourcegaming.info/2017/06/21/15864 (Mario 64 Holism piece).

Onboarding: punchev.com/blog/game-onboarding-ux-best-practices · medium.com/@tekinalper ·
professorgame.com/podcast/443 · jonlai.co/time-to-fun · cyprus-mail.com/2021/06/12/shorter-time-to-fun-video-games ·
etchuk.com/play/blog/time-to-fun-how-to-master-the-art-of-player-retention ·
en.wikipedia.org/wiki/World_1-1 · ign.com/articles/miyamoto-explains-how-super-mario-bros-world-1-1-was-created ·
gamedeveloper.com/design/how-miyamoto-built-i-super-mario-bros-i-legendary-world-1-1 ·
fdg2013.org/program/papers/paper06_zagal_etal.pdf (Dark Patterns in Games) ·
hubapps.team/blog/mobile-game-retention-strategies · medium.com/@jesssong837.

Metrics/Playtesting: gameanalytics.com/reports/2026-mobile-pc-gaming-benchmarks ·
gamedevreports.substack.com/p/gameanalytics-mobile-gaming-benchmarks ·
core-mba.pro/tool-hub/mobile-app-retention · pushwoosh.com/blog/increase-user-retention-rate ·
segwise.ai/blog/mobile-gaming-app-user-retention-strategies · blog.playio.co/dau-retention-analysis-mobile-games-2026 ·
docs.gameanalytics.com/products-and-features/analytics-iq/funnels · blog.gamemantra.ai/first-session-funnel-measuring-early-drop-off ·
emhance.ai/blog/should-i-use-analytics-or-playtesting-to-find-out-why-players-churn-on-day-1 ·
flukz.org/devlog/playtesting-your-game · gtstu.com/playtest-indie-game-solo-developer ·
closedbeta.substack.com/p/how-indie-studios-should-think-about ·
academic.oup.com/book/26677/chapter/195457270 (think-aloud) ·
linkedin.com/posts/stevebromley (think-aloud vs moderated) · schellgames.com/blog/the-definitive-guide-to-playtest-questions ·
leekon.studio/blog/finding-the-fun · ltpf.ramiismail.com/prototypes-and-vertical-slice ·
ltpf.ramiismail.com/feedback · linkedin.com/posts/ramiismail (Aug 2026 grey-box post) ·
derekyu.com/makegames · callie.zone/blog/creative-practitioner-case-study-derek-yu ·
linkedin.com/pulse/how-dramatically-improve-your-product-andrew-rusling (Valve).
