---
type: reference
last_verified: 2026-10-27
owner: agent
paths:
  - "vault/projects/catalog/*.json"
  - ".claude/hooks/project_catalog.py"
---

# Project Catalog — Log Every Project, Reuse What We Built

Everything {{USER_NAME}} builds (learning tools, games, agents, AI
tooling, apps, CAD) is logged so {{USER_NAME}} (and any team) can find it and reuse it instead of rebuilding.

**Data:** `vault/projects/catalog/<slug>.json`, one card per project, facts only.
`_minor.json` lists small repos (tutorials, scaffolds). `_skip.json` lists repos that are not
{{USER_NAME}}'s (forks or clones with no commits from {{USER_NAME}}), each with a reason.
**Pages (generated, never hand-edit):** `vault/projects/CATALOG.md` (all projects by kind) ·
`vault/projects/REUSE.md` (every reusable component: "we already built this").
**Tool:** `.claude/hooks/project_catalog.py render | check | validate`

## Rules

1. **New project → card the same day.** When work starts in a repo with no card, write
   `vault/projects/catalog/<slug>.json` (schema: any existing card; required fields: slug,
   name, one_liner, kind, status). Then run `render`.
2. **Ship / shelve / big change → update the card.** Change `status` and `last_active`, add
   `highlights`, and add `reusable` and `lessons` while they are fresh. `reusable` is the
   most valuable field: name the module, script or asset, its path, and what it could be
   reused for.
3. **Before building something new, search `REUSE.md` and `CATALOG.md`.** If a past project
   already has the piece, reuse it and say where it came from.
4. **Facts only.** Every claim must come from the README, code, git log or memory notes.
   Use null when you don't know.
5. **`check` must stay at exit 0.** A weekly cron runs it. Fix every "no card" line with a
   card, an alias on the right card, or a `_skip.json` entry that gives a reason.
6. **Sharing with the team** (team board, Slack) is outward-facing. {{USER_NAME}} says
   go first. When publishing, follow the `notion-board` skill: no local paths, write in
   plain language, and treat `local_path` and `where` as internal.
