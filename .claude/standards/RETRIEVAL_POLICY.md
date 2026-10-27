---
type: reference
last_verified: 2026-10-27
owner: agent
---

# Retrieval Policy

## L1 — always
- CLAUDE.md ; recent decisions/failures (last 10 lines of `.beads/decisions.jsonl` / `.beads/failures.jsonl`)

## L2 — load one, by task type
- Cross-project work → `.claude/rules/multi-project.md`
- Past projects / reuse → `.claude/rules/project-catalog.md`
- Learned lessons → `.claude/rules/continual-harness.md`
- Any issue type → `.claude/rules/skills-router.md`

## L3 — only when blocked
- The one doc that unblocks the task; max 2-3 per session. Personality → `vault/memory/agent_personality.md`.

## Never auto-load
- Archives, full changelogs, completed investigations, full work-log history.
