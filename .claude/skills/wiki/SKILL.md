---
name: wiki
description: {{AGENT_NAME}}'s compiled knowledge wiki (Karpathy LLM-Wiki pattern via mhmzdev's gist). Modes - ingest (compile a source note/research folder into vault/wiki pages), triage (route IDEA/RESEARCH/ACTION/DID markers from vault/dump), ask (answer from the wiki, cite pages; `ask queue <topic>` parks a question), lint (contradictions, orphans, stale, broken links). Use on "/wiki", "add this to the wiki", "ingest this", "what do we know about X", "what did we learn about X", "triage my dump", "park this question", "wiki lint", or after a research sweep lands in vault/research/.
argument-hint: ingest <path|folder> | triage | ask <question> | ask queue [<topic>|more|drop <match>] | lint
---

Input: $ARGUMENTS — first word picks the mode. Spec: `vault/wiki/SCHEMA.md` (wins on conflict).

## Layers
Raw ({{USER_NAME}} / other agents write, wiki never edits content): `vault/research/`, `vault/dump/`, `vault/logs/`, `vault/projects/`, `vault/experiments/`, `vault/plans/`.
Compiled (only this skill writes): `vault/wiki/`. The wiki is the readable synthesis on top of the raw notes.

## ingest <path|folder>
1. Read the source in full. If it has a `## My take` heading that is empty → stop: "`## My take` is empty; write your lines and run ingest again." Never fill it in for {{USER_NAME}}. (No heading = already {{USER_NAME}}'s/{{AGENT_NAME}}'s own words → passes.)
2. Pick relevant pages in `vault/wiki/` (Grep `Index.md` first). Prefer updating over new stubs.
3. New page: filename `<type> - <name>.md`, lowercase, types `concept | person | tool | project | synthesis | decision`. Header is plain text, no YAML (keeps `[[links]]` live as backlinks):
   ```
   Tags: [[<type>]] [[topic]]
   Status: #growing
   Updated: YYYY-MM-DD
   Sources: [[vault/research/x/file]]
   ```
   Existing page: add/refine only, never delete; bump `Updated:`, append to `Sources:`.
4. Facts on concept/person/tool pages; analysis on synthesis pages. Never paste source prose — compress. Every page links ≥2 other wiki pages; mark claims the source flagged unverified as `(unverified)`.
5. Extract signals into `synthesis - project ideas.md`, `synthesis - research topics.md`, `synthesis - post ideas.md` (format hint `[linkedin]`/`[reel]`/`[blog]`). Already there → add a "second signal" line, don't duplicate.
6. Outcome notes ({{USER_NAME}}'s "tried X, Y happened", `> DID:` lines, playtest results, a shipped/killed project) → `## In practice` section on the concept page, or the idea's `> **Status:**` line, or `synthesis - posted.md` for something published. Lived evidence stays separate from source-derived text.
7. Raw sources are not moved or re-statused (other agents read them by path).
8. Update `Index.md`; append to `Log.md`: `- #ingest YYYY-MM-DD — "<source>" → [[page1]], [[page2]], N signals`.

## triage
1. Read `vault/dump/*.md` (and any path {{USER_NAME}} names).
2. Route markers: `> IDEA:`/`> EXPERIMENT:` → project ideas · `> RESEARCH:` → research topics · `> ACTION:` → report to {{USER_NAME}}, not the wiki · `> DID:` → ingest step 6. Mark each routed line `*(triaged)*`.
3. Unmarked files → three lists: Ready to ingest | Stub (URL/title only) | Needs {{USER_NAME}}. Ingest the ready ones without asking (Drive-to-Done rule) unless a `## My take` gate blocks.
4. Log: `- #triage YYYY-MM-DD — N files, M markers routed, K ingested`.

## ask <question>
1. Read `Index.md` → relevant pages → their `Sources:` if detail needed.
2. Answer grounded in pages, cite them as `[[page]]`. Say plainly where the wiki is thin.
3. Reusable answer → save `synthesis - <topic>.md`. Real gap → offer `ask queue <topic>` in one line.
4. Log `#query`.

## ask queue
Backlog = `synthesis - research topics.md`, no separate store.
- `queue <topic>`: dedup on substance; title as a closable question; needs a payoff (what answering it unlocks) — ask once, never invent. Append:
  `### <question>` / `> Queued — YYYY-MM-DD` / `> <why, what would settle it>`. Never answers it.
- `queue` / `queue more`: 5 open entries at a time, oldest first, one line each. Never dump the page; never log a listing.
- `queue drop <match>`: append `*(dropped YYYY-MM-DD)*` to the heading. Never delete.

## lint
1. `python3 .claude/skills/wiki/wiki_lint.py` — deterministic: broken links, orphans, missing header fields, `#growing` pages >60 days stale, pages missing from Index.
2. Then read pages for what a script can't see: contradictions between pages (High), one wrong number copied across pages, stubs whose sources could fill them.
3. Fix without asking (add/correct/cross-link only, never delete content). A contradiction the sources can't settle → flag to {{USER_NAME}}. `Log.md` is append-only — never edit it, even for dead links.
4. Log `- #lint YYYY-MM-DD — found N, fixed M`.

## Drafting posts
Not a mode here: pull the wiki pages + `synthesis - post ideas.md` entry, then hand to `marketing-skills:social-content` (LinkedIn) / `blog` / `instagram-content`. After {{USER_NAME}} posts, ingest the outcome into `synthesis - posted.md`.
