# {{AGENT_NAME}} Wiki — Schema

Adapted from mhmzdev's "Obsidian LLM Base" gist (Karpathy LLM-Wiki pattern). Operations live in `.claude/skills/wiki/SKILL.md`.

## Layers
| Layer | Folder | Writer |
|---|---|---|
| Raw research sweeps | `vault/research/` | research agents |
| Quick captures | `vault/dump/` | {{USER_NAME}} (quick dumps, markers) |
| Session logs | `vault/logs/` | hooks |
| Projects / experiments / plans | `vault/projects/`, `vault/experiments/`, `vault/plans/` | {{AGENT_NAME}} + {{USER_NAME}} |
| **Compiled wiki** | `vault/wiki/` | `wiki` skill only |

## Page types (filename prefix)
`concept -` · `person -` · `tool -` · `project -` · `synthesis -` · `decision -`. Lowercase. New types allowed when a real page needs one.

## Header (plain text, no YAML — YAML breaks `[[backlinks]]` in Obsidian)
```
Tags: [[concept]] [[topic]]
Status: #growing
Updated: YYYY-MM-DD
Sources: [[vault/research/x/file]]
```
Status: `#stub` placeholder · `#rough` unrefined · `#growing` living page (lint flags after 60 days untouched) · `#in-progress` living reference, never "stale" · `#completed` · `#archived` · `#superseded`.

## Capture markers (in `vault/dump/` or any note)
```
> IDEA: ...        → synthesis - project ideas
> EXPERIMENT: ...  → synthesis - project ideas (Experiments)
> RESEARCH: ...    → synthesis - research topics (the queue)
> ACTION: ...      → told to {{USER_NAME}}, not stored
> DID: ...         → outcome: ## In practice / idea Status / synthesis - posted
```

## Rules
- Raw is never edited by the wiki; wiki never pastes raw prose.
- A note with an empty `## My take` is never ingested (Collector's Fallacy gate).
- Update over create; never delete content; every page links ≥2 others; `## Related` when 3+ links.
- `Log.md` is append-only, even dead links stay.
- Lived evidence (`## In practice`) is kept apart from source-derived text.
- Contradictions the sources can't settle → flag {{USER_NAME}}, don't guess.
