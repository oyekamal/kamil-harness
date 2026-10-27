---
type: reference
last_verified: 2026-10-27
owner: agent
paths:
  - ".claude/hooks/continual_harness.py"
---

# Continual Harness — {{AGENT_NAME}} Learns From Every Session

Port of PrimeIntellect-ai/prime-agent's `/refine` (Continual Harness, arXiv 2605.09998), hardened
with {{AGENT_NAME}}'s rule that nothing evolves without a gate. **File:** `.claude/hooks/continual_harness.py`
(stdlib, one file) · **Tests:** `test_continual_harness.py` · **State:** `~/.agent-harness/continual/`

## The loop (automatic, every project — user-level hooks)

```
SessionEnd / PreCompact → hook-review (detached, never blocks)
   haiku gate: "lesson worth keeping?" + helped/hurt verdict on each lesson injected this session
   sonnet planner: ≤3 edits (memory | prompt | procedure | subagent) × (project | global)
   deterministic gates → state.json + history.jsonl
UserPromptSubmit → hook-inject: BM25-ranked lessons for this repo, global, and any repo the prompt
   names; each lesson at most once per session, ≤8 lessons / 1800 chars
SessionStart → hook-status: one line when global candidates are waiting
```

## Gates (why this is safer than prime-agent's version)

1. **Evidence** — every quote must appear verbatim in the transcript, ≥30 chars, on-topic. Global
   lessons must quote {{USER_NAME}}'s own words (USER lines), not assistant or tool output.
2. **Scope** — project lessons go live at once. Global lessons start as `candidate` and go live only
   when a *second independent session* produces the same lesson, or {{USER_NAME}} runs `approve`.
3. **No rewrites** — one session can reinforce a global or pinned lesson, never rewrite it.
4. **Feedback** — the reviewer judges each injected lesson once per session; harmful ≥2 and
   harmful > helped → retired. A candidate that hurts is retired at once.
5. **Lint** — refuses secrets, gate-bypass advice (`--no-verify`, skip tests…), remote fetch/exec,
   foreign URLs (prompt-injection shape).
6. **Undo** — `rollback <event>` restores; it skips entries changed later unless `--force`.
   `state.json.bak` keeps the previous save; a corrupt store is quarantined, never overwritten.

## Commands

```bash
H=.claude/hooks/continual_harness.py
python3 $H list [--all|--candidates]     # what {{AGENT_NAME}} has learned
python3 $H show <id> | approve <id> | retire <id>
python3 $H rollback <event-id> [--force]  # event ids are in history.jsonl / review.log
python3 $H stats
python3 $H maintain                       # weekly cron: retire dead lessons, list promotion-ready
tail ~/.agent-harness/continual/review.log
```

## Relationship to harness-evolve

Lessons are **hints** injected at runtime. Turning a proven lesson into a permanent rule, skill or
CLAUDE.md change stays with `harness-evolve` (re-executed, eval-gated). `maintain` writes
`maintain-YYYY-MM-DD.md` listing lessons with helped ≥3 and helped ≥ 3×hurt: feed that to
`harness-evolve` as its signal. Never hand-copy a lesson into a rule.

## Rules for {{AGENT_NAME}}

- If an injected lesson is wrong for the task, **say so in the reply**. That sentence is the evidence
  the reviewer uses to retire it.
- Don't edit `state.json` by hand; use `approve`/`retire`/`rollback` so history stays complete.
- Kill switch: remove the four `continual_harness.py` hook entries from `~/.claude/settings.json`.
