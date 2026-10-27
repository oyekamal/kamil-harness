---
type: rule
owner: agent
last_verified: 2026-10-27
---

# SkillsMP — Skill Discovery for Hard/Unknown Tasks

SkillsMP is a GitHub-indexed marketplace of 2M+ SKILL.md files. Each skill is a markdown
instruction file that teaches Claude how to perform a specific task better.
Search it when {{AGENT_NAME}} hits a capability gap or a task is genuinely stuck.

**API key:** `$SKILLSMP_API_KEY` (export it in your shell or `.env` — never commit it; 500 req/day, 30/min)
**API:** GET only — search/discovery. No publish endpoint. Publishing = push a SKILL.md to GitHub.

## When to Search

- `capability_gap` is non-null in manager output
- A task is stuck 3+ ticks with no progress
- {{USER_NAME}} explicitly says "this is very difficult" or "find a skill for this"
- No row in `skills-router.md` covers the task

## How to Search

```bash
# Quick lookup
python3 ./.claude/hooks/skillsmp_search.py "task description"

# With occupation filter (better dev results)
python3 .claude/hooks/skillsmp_search.py "browser automation" --occupation software-developers

# JSON for programmatic use (response shape below)
python3 .claude/hooks/skillsmp_search.py "CSV pipeline" --json
```

## Response Shape (actual API fields)

```json
{
  "id": "author-repo-path-to-skill-md",
  "name": "skill-name",
  "author": "github-username",
  "description": "one-liner description",
  "githubUrl": "https://github.com/author/repo/tree/main/path/to/skill",
  "skillUrl": "https://skillsmp.com/creators/author/repo/path-dashes",
  "stars": 380125,
  "updatedAt": "unix-timestamp"
}
```

Read the actual SKILL.md via: `curl https://raw.githubusercontent.com/<author>/<repo>/main/<path>/SKILL.md`

## Decision Tree

```
Task arrives → no matching {{AGENT_NAME}} skill?
    ↓
skillsmp_search.py "<task description>"
    ↓
Skills found (stars > 0)?
    ├─ YES → DM {{USER_NAME}} with top 3 (template below) → await "use 1/2/3"
    │        On approval: fetch githubUrl SKILL.md → follow its instructions
    └─ NO  → log the gap in .beads/failures.jsonl → escalation-broker agent
```

## Message Template (Slack DM if the Slack MCP is connected, otherwise plain chat)

```
🔍 Stuck on: <task title>
No built-in skill. Top SkillsMP results for "<query>":

1. ★<N> <author>/<name> — <description>
   <skillUrl>
2. ★<N> <author>/<name> — <description>
   <skillUrl>
3. ★<N> <author>/<name> — <description>
   <skillUrl>

Reply "use 1/2/3" to proceed, or "escalate" to hand off directly.
```

## How to PUBLISH an agent skill to SkillsMP

SkillsMP auto-indexes public GitHub repos. No submit form — just push to GitHub.

**SKILL.md format** (based on openclaw/browser-automation reference):

```markdown
# <Skill Name>

<One-line description — this becomes the SkillsMP card description>

## When to Use
<Trigger conditions — be specific>

## How It Works
<Step-by-step instructions for the AI>

## Key Rules
- Rule 1
- Rule 2

## Error Handling
<What to do when things go wrong>
```

**To publish a skill from this harness:**
1. Create `skills/<skill-name>/SKILL.md` in `agent-harness` repo (or a new public repo)
2. Push to GitHub
3. SkillsMP picks it up on next crawl (usually within 24–48h)
4. URL will be: `skillsmp.com/creators/<your-github>/<your-repo>/skills-<skill-name>`

Good candidates to publish: your own custom skills.

## Protocol Rules

1. **Search before escalating.** SkillsMP runs BEFORE `escalation-broker` for capability gaps.
2. **Surface, don't auto-run.** Never install or follow an external skill without {{USER_NAME}}'s approval.
3. **Read the SKILL.md** before claiming you can use a skill — fetch the raw GitHub content.
4. **Log every search.** Append query + top result to `.beads/failures.jsonl`.
5. **Quota awareness.** 500/day. Only search on genuine capability gaps, not every tick.
6. **Quota exceeded** → treat as "no results" → escalation-broker as usual.

