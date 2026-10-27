---
type: reference
last_verified: 2026-10-27
owner: agent
---

# Multi-Project Board — Manage Any Project, Not Just One

{{AGENT_NAME}} works across many repos (your main app, side projects, client work). This
board is a small cross-repo task list with enforced dependencies, inspired by open-source
Claude Code orchestrators (ccmanager's auto-discovery, agent-kanban's cross-repo dependency
board, claude-mpm's per-project session model). It lives in a local SQLite file instead of a
separate tool.

**File:** `.claude/hooks/project_board.py` · **Tables:** `projects`, `tasks` in `~/.agent-harness/harness.db`
(created by `.claude/hooks/agent_harness_db.py`)

## What it's for

- **Every repo you work in** — side projects, personal repos, client work — gets one place
  to track open tasks, instead of living only in {{USER_NAME}}'s head or a stale TODO comment.
- If a repo has its own tracker (GitHub Issues, Linear, Jira), keep using that for team-visible
  work; use this board for your own cross-repo view.

## Commands

```bash
python3 .claude/hooks/project_board.py scan [root ...]        # discover/refresh git repos
python3 .claude/hooks/project_board.py list                    # every known project
python3 .claude/hooks/project_board.py task add <project> "<title>" [--depends-on ID]
python3 .claude/hooks/project_board.py task claim <id> <who>
python3 .claude/hooks/project_board.py task status <id> todo|in_progress|blocked|done
python3 .claude/hooks/project_board.py task done <id>
python3 .claude/hooks/project_board.py board                    # cross-project view, open tasks only
```

Default scan roots: `~/projects` and `~/Documents` (override with `PROJECT_ROOTS=dir1:dir2`). Project id = dir name, lowercased.

## Rules

1. **Before starting non-trivial work in ANY repo**, check
   `project_board.py list` for the project id — run `scan` first if it's new — then
   `task add <project> "<what>"` before touching code.
2. **Dependencies are enforced, not advisory** — `task status <id> in_progress` is
   refused if `depends_on` points at a task that isn't `done` yet. Don't route around
   this by skipping straight to a manual DB write.
3. **Claim before working, `done` when merged/shipped** — a claimed-but-stale task is a
   signal something stalled. There is no auto-reap, so sanity-check `board`
   output for anything claimed that's clearly abandoned.
4. **`board` is the check-in command** — when {{USER_NAME}} asks "what's going on across
   my projects" or "what am I working on", run `board`, not a manual `find`/`grep` sweep.
5. **Re-scanning is always safe** — `path` is UNIQUE with an upsert, so running `scan`
   repeatedly (e.g. at session start) never duplicates a project row.

## Design notes (why it's built this way, for future evolution)

- Text-based board, not a GUI — {{AGENT_NAME}} runs everywhere Kanban Code (macOS/Windows-only
  Tauri/SwiftUI app) couldn't, matching {{USER_NAME}}'s Linux environment.
- `depends_on` is a single task id (not a list) — deliberately simpler than agent-kanban's
  full dependency graph. Upgrade to a join table only if a real task needs 2+ blockers.
- No session-status view (idle/busy/waiting) yet, unlike ccmanager; add one only if
  the work grows enough subagent parallelism to need it.
