---
name: game-retention-design
description: Diagnose and design what makes a game worth replaying, talking about, and coming back to — "one more run", popularity/virality, "addictive" loops, game feel, onboarding, retention metrics, and where engagement tips into manipulation. Use for "why isn't my game fun / sticky", "make players come back", "what makes X addictive", "how do I make this go viral", "add replayability", "review my game design", "core loop", "meta-progression", "juice", "daily challenge", "retention", playtest analysis, or before designing any new game. Works on a running build, source code, a design doc, or a pitch.
---

# Game Retention Design

A procedure, not a lecture. Given a game (build, code, doc, or pitch), it produces **the single biggest reason players won't come back, and a ranked list of concrete fixes with numbers you can tune and a way to check each one**.

Evidence is graded throughout: **[S]** peer-reviewed or measured data, **[I]** strong industry practice (GDC, postmortems, shipped hits), **[H]** heuristic/aphorism. Don't present [H] as science.

Deep references (sourced, with URLs) — load only the one you need:
- `references/psychology.md` — SDT/PENS, flow, reward prediction error, goal-gradient, endowed progress, near-miss, Yee's 12 motivations, Koster
- `references/replayability.md` — loop layering, interesting decisions, StS/Hades/Balatro/Vampire Survivors/Spelunky/BotW, 25-question checklist
- `references/virality.md` — 16 breakout case studies, design vs marketing levers, Steam numbers, survivorship caveats
- `references/feel-onboarding-metrics.md` — juice with tunable numbers, FTUE, D1/D7/D30 benchmarks, playtest protocol
- `references/live-ops-ethics.md` — dailies, streaks, passes, gacha, FOMO; green/amber/red table; regulation

## The model in one screen

People come back to a game for exactly two healthy reasons and one unhealthy one:

1. **They're still learning something** (Koster [H], flow [S], SDT competence [S]). Fun is pattern-mastery; boredom is a solved pattern. Replay dies when the *decision space* is exhausted, not when content runs out.
2. **Something is unfinished or changed** (goal-gradient [S], endowed progress [S], Zeigarnik [H — replication mixed]). A visible, nearly-closed loop at the moment they stop.
3. *(Unhealthy)* **They'll lose something if they don't** — manufactured loss, obligation, chance-for-money. Works short-term, burns trust, and is increasingly illegal (see Gate 4).

Popularity is a different machine: a game spreads when **playing it produces something worth showing someone else** (a clip, a grid, a story, an invite) and the game can be understood from that artifact in ~3 seconds [I].

Everything below is these three ideas turned into checks.

## Audit procedure

Run in order. **Stop at the first failing gate and make that the headline** — fixing later layers on top of a broken earlier one is the most common waste in game dev.

### Step 0 — Get the real thing

Play it or run it if at all possible (Godot: `godot` skill's run/capture tools; web: browser). If only code, read the main loop, player controller, game-over/restart flow, and progression/save code. Write down, with evidence (`file:line` or timestamp):

- **3-second pitch**: one sentence, one concrete verb. ("Dodge sea creatures in the dark.") If you can't write it, that's finding #1.
- **The three loops** with durations: core (seconds: the verb), session (a run/level/match: minutes), meta (across sessions: unlocks, best score, story). Mark any that are missing.
- **Restart time**: death/fail → back in control, in seconds. Count every screen and forced wait.
- **Session length** and **time-to-first-fun** (seconds from launch to first satisfying action).

### Gate 1 — The toy (is the verb fun with nothing else?)

If the core verb isn't satisfying with no score, no unlocks, no story, nothing layered on top fixes it. Meta-progression propping up a weak core loop gets "grinded out and quit" [I].

Check:
- Moving/acting with no goal is pleasant for 30 s (Nintendo's "fun to just move" test [I]).
- Every input gets **visible + audible feedback within ~100 ms**; impacts have weight (hit-stop, shake, particles, sound). Tunables in `references/feel-onboarding-metrics.md`.
- Control forgiveness where the genre expects it (coyote time, input buffering, generous hitboxes for the player, strict for enemies).
- A failure you can read: the player sees exactly what killed them and how close they were.
- **Failure → understanding time.** Seconds from the fail moment until the player *knows why*. Target ~1–2 s, shown in the world (freeze on the cause, highlight it), wordless if possible. Minit does death → lesson in ~1 s with no text. A post-mortem screen of text listing several causes at once is a Gate 1 fail, not an onboarding nit. Measure it from the fail event through any drift/fade/transition to the moment the cause is on screen.
- **Comprehension load.** Count the invented nouns (custom terms for mechanics, currencies, systems) a player must understand before their first fun moment. More than ~2 = flag it; replace with plain words or show instead of name.

Starting tunables (60 fps; tune by feel, sources in the reference):

| Knob | Start at | Grade |
|---|---|---|
| Hit-stop | light 2–4 frames, heavy 6–10, dramatic finisher 15–20+ | [I] fighting-game data; *presence* matters more than exact length [S, 2022 survey] |
| Screenshake | `trauma` 0–1, amplitude ∝ trauma² (or ³), trauma decays 1–3/s | [I] community convention, no primary spec |
| Coyote time | 3–6 frames (~50–100 ms); Celeste ≈ 5 frames | [I] |
| Jump buffer | 3–8 frames; Celeste ≈ 4 | [I] |
| Attack input buffer | 5–10 frames; parry/dodge 3–4 | [I] |
| Input → feedback latency | < 100 ms | [I] |
| Restart after fail | ≤ 3 s to control | [I] |

**Fail → stop. Headline = "the toy isn't fun yet". Prescribe a toy prototype + a silent playtest, not features.** (Hard lesson: a game can pass every paper design review and still playtest as confusing and not fun. Test the toy with a human before a long design pass.)

**Name the smallest testable core.** When a design is big (many interlocking systems, many characters, long sessions), say concretely what the cut-down toy is: e.g. "2 characters, 1 threat, 1 location, one 3-minute loop, no meta". Also say the scope number if the docs give one (months, team size). A 3-year plan with an unproven toy is itself a finding.

### Gate 2 — Decisions and mastery (is there something left to learn after run 5?)

- **Interesting decisions** (Sid Meier [I]): the right answer changes with the situation, choices trade off, information is enough to reason. List every choice point; flag any with one dominant answer or pure-coin-flip. A fake choice is worse than none: it teaches players to stop reading.
- **Skill ceiling above the finish line**: optional technique, score/time optimisation, harder modes. And it must be *legible* (score, splits, replays, leaderboard) or it doesn't motivate [I].
- **Variety that changes strategy, not just scenery**: count distinct viable strategies/builds. Layout randomisation alone = "different route, same strategy"; drafted pools (cards, perks, relics) = different strategy [I]. Procgen from hand-authored chunks with a fairness check, never unconstrained (Spelunky [I]).
- **Risk/reward push-your-luck** moment at least once per session ("bank now or go deeper").
- **Flow**: difficulty adapts or offers lanes; neither only-up nor flat. [S]

### Gate 3 — Loop closure (why open it again tomorrow?)

- **Something persists after a failed session**: best score, unlock, new line of dialogue, codex entry. Even tiny. Death with no meta feedback is "the worst thing you can do" (Meier) [I]. Hades: story advances *on death* [I].
- **Show distance-to-go, not progress-made** at session end ("3 m short of your best", "1 more for the next unlock") [S goal-gradient]. Never start a progress bar at empty (honest head start) [S endowed progress].
- **Unlocks widen options, not raw power**. Power creep trivialises the core loop [I]. Cadence: first unlock during/right after run 1, then every 1–2 → 3–5 → 10+ runs [I].
- **Restart ≤ ~3 s** and no unskippable screens after the first viewing [I]. Session short enough that "one more" is a cheap promise.
- **An open loop at the stopping point**: the player quits with one visible, nearly-finished thing.
- **Daily seed / shared challenge** if there's any randomness: same seed for everyone, one attempt, shareable result (Spelunky dailies, Wordle) [I]. The scarcity and the share are the load-bearing parts.

### Gate 4 — Respect (ethics + legality)

Classify every retention mechanic with the traffic light in `references/live-ops-ethics.md`. Short form:

- 🟢 honest progress bars, unconditional daily gifts, opt-in social, seasonal content that returns, real-world-value hooks.
- 🟡 streaks (need a freeze/grace), battle passes, returning limited events, finite collections, honest notifications.
- 🔴 **chance + real money** (loot boxes/gacha: banned in Belgium, odds-disclosure mandated in China, FTC $520M Epic and ~$20M miHoYo actions), manufactured near-misses in levels, punitive decay (crops rot), social quotas, never-returning FOMO, energy that exists only to sell refills, timers tuned to sleep cycles.

Test for any mechanic: **does it make them want to come back, or feel they have to?** If players describe it as a rule imposed on them, it's red. Anything a plausibly under-13 audience touches gets a stricter pass (both FTC cases were COPPA). Red items go in the report as must-remove, whatever their retention lift.

### Gate 5 — Spread (does playing produce something worth sharing?)

Only after Gates 1–3 pass. A viral spike into a game that fails Gate 1–3 just churns faster.
- One-sentence verb pitch a 10-year-old gets; readable in a thumbnail/GIF [I].
- **Clip moments by design**: failure more spectacular/funny than success (Fall Guys, PEAK, Getting Over It), physics/proximity-voice comedy, awe moments [I].
- **Friend-pull**: co-op for 2–4 makes every player an invite [I].
- **Spoiler-safe shareable artifact** as a by-product of play (Wordle grid, end-of-run card, seed code) [I].
- Depth under the meme, or the tail is short (Only Up! vs Balatro) [I].
- Marketing levers (Steam capsule CTR, trailer first 3–5 s, wishlists, Next Fest, creator keys) live in `references/virality.md`. Always state survivorship bias: thousands of games had these traits and didn't break out.

## Output format (the report)

```
GAME: <name> — <3-second pitch, or "can't state one">
LOOPS: core <verb, Ns> · session <what, N min> · meta <what / MISSING>
RESTART: <N s, screens counted>   TIME-TO-FUN: <N s>
FIRST FAILING GATE: <1-5> — <one sentence why, with evidence>

THE BIGGEST GAP: <one sentence. The thing that, if unfixed, makes everything else irrelevant.>

TOP FIXES (ranked by retention impact ÷ effort):
1. <concrete change> — <tunable numbers> — evidence [S/I/H] — effort S/M/L
   Check: <playtest observation or metric that proves it worked>
2. ...
(3–7 items. Each must name a file/system/screen, not a principle.)

RED FLAGS (must remove): <ethics gate items, or "none">
DON'T BOTHER YET: <tempting work that is premature given the failing gate>
PLAYTEST PLAN: <3–5 things to watch for in a silent playtest of the fixed build>
```

Rules for the report:
- **Evidence must be real.** Cite `file:function` or quote the line. Give a line number ONLY if you got it from `grep -n` or a Read in this session. Never estimate one. A wrong citation is worse than none: the dev will trust it. Before writing the report, re-grep every citation and number you use, and delete any you can't confirm.
- **Word budget is hard.** Default ≤ 600 words, or the budget you were given; check with `wc -w` and cut. Drop empty sections rather than pad them. The headline + top 3 fixes matter more than completeness.
- **Specific beats comprehensive.** "Add hit-stop" is weak. "On player death in `player.gd:_on_hit`, freeze 80 ms, shake 8 px decaying over 0.3 s, then show 'best: 41 s / this run: 37 s' within 1 s" is the standard.
- Every fix gets a **Check**, a way to know if it worked. No check = speculation.
- Tie each fix to evidence grade. Don't cite a [H] as if it were [S].
- Don't list everything on the checklists; list what moves *this* game most.
- Say what's already working in one line, so it isn't broken by the fixes.

## Design mode (new game, no build yet)

Same gates, forward:
1. Write the 3-second pitch and the verb. Kill the idea if the verb isn't novel or exaggerated vs genre neighbours [I].
2. Build **the toy only** (verb + feedback + fail + instant restart). Silent playtest with a real person before anything else. Gate 1 must pass on a grey-box.
3. Add one decision layer (draft/choice/risk-bank) and a best-score meta. Playtest.
4. Then the meta loop, a daily seed, and a shareable end-of-run card.
5. Ethics review before any monetisation or streak lands.

## Measuring it

- Retention is measured, not argued. Mobile medians (GameAnalytics 2026 report, 2025 data) [S]: **D1 ≈ 22%, D7 ≈ 4%, D30 ≈ 0.7%**; top 10% D1 ≈ 40%; 64%+ D1 is a freak hit, not a target. PC table and regional splits in `references/feel-onboarding-metrics.md`. For a hobby build: count "voluntary second runs" in silent playtests. That's your D0 retention and the single best early signal.
- In playtests, **don't explain anything**. Watch for: first death, first confusion pause, first "one more" (restart without being asked), the moment they stop. Where they quit is your churn point.
- Instrument restart time and session length even in a prototype. Treat restart > 3 s as a bug.

## Anti-patterns this skill should catch

- Content volume mistaken for pattern novelty (more levels of a solved mechanic) [H Koster].
- Meta-progression propping up a weak toy.
- Choice screens with a dominant pick; trap options.
- Unfair or unreadable deaths (off-screen hits, invisible RNG), which make players stop trusting the game, and they stop retrying.
- Tutorials that explain instead of letting the player do (World 1-1 teaches by doing [I]).
- Bartle types presented as science (never validated; use Yee's 12 motivations [S-ish, large N]).
- "It'll go viral" plans with no clip moment, no share artifact, no friend-pull.
- Using dark patterns because a competitor does. Red is red.
