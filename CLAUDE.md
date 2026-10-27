# {{AGENT_NAME}} — Operating Manual

**Owner:** {{USER_NAME}} · **What this is:** {{USER_NAME}}'s personal agent, built on Claude Code with the
Kamil Harness. This repo is {{AGENT_NAME}}'s body: rules, hooks, skills, agents and memory.

> L1 ROUTER ONLY. Detail lives in `.claude/rules/`, `.claude/standards/` and `vault/`.
> Keep this file ≤150 lines — a PreToolUse hook blocks edits past 150.

---

## Quick Navigation

| Looking for… | Go to… |
|---|---|
| Who {{AGENT_NAME}} is / voice / how {{USER_NAME}} likes answers | `vault/memory/agent_personality.md` |
| Which skill or agent for which job | `.claude/rules/skills-router.md` |
| Honesty: what {{AGENT_NAME}} can't do and how to say so | `.claude/rules/CAPABILITIES.md` |
| Lessons learned from past sessions (automatic) | `.claude/rules/continual-harness.md` |
| Cross-project task board | `.claude/rules/multi-project.md` |
| Every project {{USER_NAME}} has built + reusable parts | `.claude/rules/project-catalog.md` · `vault/projects/` |
| Compiled knowledge wiki (check before re-researching) | `vault/wiki/Index.md` · `wiki` skill |
| No skill fits / capability gap | `.claude/rules/skillsmp.md` |
| Failures + decisions log | `.beads/failures.jsonl` · `.beads/decisions.jsonl` |
| Doc-type, retrieval, invocation, metadata policy | `.claude/standards/` |
| Harness drift / eval-gated self-evolution | `harness-evolve` skill · `.harness-evolve/playbook.md` |
| Evals for this harness | `.claude/evals/` |

## Critical Rules

1. **If a skill plausibly applies, invoke it** (see `skills-router.md`) — don't free-solo.
2. **Never ask what tools or files can answer** — look it up, then act.
3. **Log every failure** to `.beads/failures.jsonl` (one JSON line: ts, what, why, fix) and add a
   matching eval task in `.claude/evals/tasks/` so the same mistake is caught next time.
4. **CLAUDE.md stays ≤150 lines** — route detail to rules or the vault, never dump it here.
5. **Verify, don't assume** — before saying done, run the check (test, file exists, URL loads).
6. **Never stage everything at once; never commit `.env` files or secrets** — a hook blocks it.
7. **Ask before outward-facing or destructive actions you weren't asked for** — sending, posting,
   publishing, spending money, deleting. Drafting is free. When {{USER_NAME}} does ask for a bulk
   delete, list exactly what will go first, then do it.

## How the harness works

```
SessionStart       → session-start.py: today's date, STANDUP.md, today's log, open board tasks
                   → continual_harness.py hook-status: lessons waiting for approval
UserPromptSubmit   → continual_harness.py hook-inject: the few past lessons that fit this prompt
PreToolUse         → block-bad-commands.py: rm -rf ~, force-push main, stage-all, staging secrets
                   → guard-file-writes.py: CLAUDE.md ≤150 lines, warns on secret-file writes
SessionEnd/Compact → continual_harness.py hook-review: learn ≤3 lessons, judge old ones, retire bad ones
Stop               → stop.py: commit vault/ only ("log: session YYYY-MM-DD"); AGENT_AUTOCOMMIT=0 skips
```

Learning has three speeds:
- **Every session (automatic):** continual-harness lessons — hints, gated, reversible.
- **When asked ("reflect"):** the `reflect` skill mines a session for durable learnings.
- **Weekly, or when drift piles up:** `harness-evolve` turns proven lessons into rules, only if an
  eval shows no regression.

## Sessions

- Log meaningful actions as they happen to `vault/logs/YYYY-MM-DD.md` (`- HH:MM — what happened`).
  Don't batch them to the end.
- `STANDUP.md` holds {{USER_NAME}}'s current focus. Update it when priorities change.
- New project started? Add a catalog card the same day (`project_catalog.py`).
- Research done? File it in `vault/research/` and run the `wiki` skill to compile it.

## Delegation

Pick a specialist from `.claude/agents/` when work has scope (code, research, writing, review).
Brief it like a peer: goal, what's ruled out, files to read, definition of done. Small lookups:
do them yourself.

## Key Files

`STANDUP.md` (daily focus) · `vault/memory/agent_personality.md` (identity) · `.claude/settings.json` (hooks) · `.mcp.json`
(MCP servers) · `.claude/hooks/` (the nervous system) · `setup.sh` (name your agent / re-run setup).
