---
name: why
description: "Use for 'why does this code/design work this way', design rationale, 'who decided this', regressions, postmortems, or data-backed thresholds — investigate the history behind a decision. Queries the evidence sources you have connected in parallel (git/GitHub always; plus Notion, Slack, a data-warehouse MCP if present) via the Agent tool, then returns a cited read on decisions and tradeoffs. Use `debugging` for 'how does this run right now', not this."
---

# Why

**Requires:** `git` and `gh` (authenticated); optionally Notion, Slack or data-warehouse MCPs if you want those evidence sources searched.

Investigate the motivation and intent behind code or a decision. Why was it built this way? What edge cases were considered? What business or operational constraint shaped the design? What alternatives were rejected, and why?

Companion to reading code directly. Reading the code tells you what it does and how it runs. `why` answers what forces led to its shape — ported from Cursor's `pstack` plugin, adapted to run on Claude Code's Agent tool against {{AGENT_NAME}}'s actual evidence sources instead of Cursor's generic MCP discovery.

## How this skill works

Historical context spreads across several evidence categories, and you cannot predict from the question alone which one holds the answer. So this skill enumerates {{AGENT_NAME}}'s real evidence sources, queries all of them in parallel via the Agent tool, then synthesizes with explicit confidence calibration. Null results are first-class evidence about how the decision was made; report them alongside positive findings. The default is coverage, not minimalism.

**Adaptation note:** the upstream Cursor skill discovers MCPs at runtime and spawns one investigator per matched category (ticket tracker, docs, chat, infra observability, error tracking, analytics warehouse — 7 in all). This version keeps the roster small and fixed. Git is always available; the other three investigators run only if the matching MCP is connected:

| Category | Source | Tool |
|---|---|---|
| Source control & code | git history, GitHub PRs, inline code comments | `git log`/`git blame`/`gh pr view` (Bash) |
| Tickets + long-form docs | Your ticket tracker and docs (Notion, Linear, Jira, etc.) | e.g. `mcp__claude_ai_Notion__*` if the Notion MCP is connected |
| Real-time team chat | Slack engineering channels, DMs, threads | Slack MCP search, if connected |
| Infra + error + product-analytics | A data-warehouse MCP (observability tables, error logs, usage analytics — three upstream categories collapse into one here) | whichever warehouse MCP you have connected |

If you have no dedicated error tracker (Sentry-equivalent) or infra-observability tool (Datadog-equivalent), say so as a named gap rather than skipping the search silently; the warehouse may still hold relevant rows.

## Operating Posture

Operate as a careful, cautious, precise investigator. Think like a detective piecing together a historical case from fragmentary records. When the record is thin, say so.

- **Evidence before narrative.** Collect the pieces first, then see what story they support. Never pick a story and recruit the evidence that fits it.
- **Precision over polish.** Prefer the exact quote and citation over a smooth paraphrase. A reader should be able to follow any claim back to its source and verify it in under a minute.
- **Consider what you haven't seen.** The evidence you find is a sample, not the whole truth.
- **Name the gaps.** If a thread goes cold, a source isn't searchable, or a question has no answer, document the gap. Don't paper it over with an authoritative-sounding guess.
- **Hedge on purpose.** When evidence is indirect, language should signal it ("appears to", "likely", "suggests"). This is a feature of the output, not something to override for polish.
- **No shortcut by code-reading.** The code tells you what it does, rarely why it exists. Resist inferring intent from code shape.

## Core Epistemics

Read `references/epistemics.md` for the full confidence-tier framework and phrasing guide before writing any synthesis — it is mandatory, not optional background.

Principles in brief:
- **Cite everything.** Every claim about intent references a commit hash, PR number, Notion page/ticket, Slack permalink, or code comment. Uncited = inference, and must be labeled.
- **Prefer "appears to" over "because".** Reserve confident language for direct, explicit evidence.
- **Surface contradictions.** If two sources disagree, show both.
- **Acknowledge gaps.** An honest "we couldn't find out why" beats a confident guess.
- **Beware rationalization.** Code that makes sense today may have been written for reasons that no longer apply.

## Step 1. Understand the Target and the Question

Parse the target (code, pattern, feature, decision) and the question type: design rationale / tradeoff / defensive reasoning / external constraint / "why does this still exist" / broad history. If the target is vague, state your best-guess interpretation from context and proceed — don't stall on a clarifying question the thread can answer.

## Step 2. Establish the Code Anchor

Before spawning investigators, build the code anchor inline (it's cheap and every investigator needs it):

```bash
git blame -L <start>,<end> <file>
git log --follow -p -- <file>
git log --oneline -20 -- <file>
git log -1 --format=%B <commit>
gh pr view <number> --json title,body,author,createdAt,mergedAt,labels,closingIssuesReferences,comments,reviews
```

Capture file paths, symbols, commit hashes, PR numbers, and any linked Notion ticket ID. Pass this to every investigator so none of them re-derive it.

## Step 3. Spawn Parallel Investigators

Launch one investigator per category **in a single message with multiple Agent tool calls** so they run concurrently (same pattern as `superpowers:dispatching-parallel-agents`). Each investigator gets a `general-purpose` agent — Claude Code has one model per session, so the diversity here comes from giving each investigator a distinct source and a distinct playbook, not from model diversity (unlike the upstream skill's per-category model routing, which doesn't apply here).

Each investigator's prompt is built from `references/investigator-prompt.md`, filled in with:
1. The code anchor from Step 2
2. The user's original question
3. Its assigned category playbook: `references/sources/code-archaeology.md`, `references/sources/notion.md`, `references/sources/slack.md`, or `references/sources/data-warehouse.md`
4. `references/sources/incident-postmortem.md` too, **if the target code looks defensive** (null checks, retry logic, timeouts, rate limiting, feature flags)

Investigators only gather and report evidence — they do not write files, and they do not answer the "why" themselves. That's the synthesizer's job (Step 4).

### Investigator roster

1. **Source control investigator** (git/gh + code comments). Always spawn — the only guaranteed source. Best at implementation-time rationale: PR descriptions, review threads, inline comments, test names encoding edge cases.
2. **Tickets/docs investigator** (e.g. `mcp__claude_ai_Notion__*`, if connected). Best at product/business forcing functions and long-form design rationale: ticket descriptions, "alternatives considered" sections, specs, postmortems.
3. **Slack investigator** (Slack MCP search across engineering channels, if connected). Best at real-time deliberation that never reached a doc: incident fire-drills, author/reviewer Q&A, casual "we decided X because Y" threads.
4. **Data-warehouse investigator** (your warehouse MCP, if connected). Best at runtime/data reality: usage trajectories, error-log spikes bracketing a ship date, threshold constants that trace back to a p99 in a query. Always call `get_rules`/`describe_data`/`get_table_schema` before querying — never guess a table name (see the MCP's own contract note, if it has one).

### When to skip an investigator

Only skip with a written justification in the final "Sources Consulted" section, and only for one of two reasons:
- Genuinely no way to reach that source in this environment (the MCP isn't connected).
- The source is **provably irrelevant** ("target is a build-time script with no runtime code path" — not "probably nothing there").

"It's pure feature code, the warehouse won't have anything" is not sufficient. Run the search; let the null result speak.

## Step 4. Synthesize

Spawn one synthesizer agent (`general-purpose`) after all investigators return. Give it:
1. All investigator findings, including nulls and skip justifications
2. The code anchor
3. The user's original question
4. `references/epistemics.md` in full
5. `references/synthesizer-prompt.md`

Its job: a confidence-weighted, evidence-cited narrative with clearly separated "what we know" vs. "what we're inferring," honest gaps, and a coverage map.

## Step 5. Present

Present the synthesizer's output. Lightly edit for clarity if needed, but **do not rewrite the confidence language** — the hedges are the product, not a stylistic flaw to smooth over.

## Output Format

**The Question** — restate concisely.
**The Code in Question** — file paths, line ranges, key symbols.
**What We Found (direct evidence)** — cited claims only.
**What We Can Reasonably Infer** — hedged claims with explicit inference chains.
**Competing Hypotheses** — only if the evidence genuinely fits more than one story.
**What We Don't Know** — explicit, specific gaps.
**Sources Consulted** — one line per category, format: `- <Source>: <what was searched>. <what was found, or "no relevant results," or "skipped. reason">.`

After Sources Consulted, if this `why` question is a precursor to actually changing the code, convert the findings into a Preserve / Change / Avoid / Risk constraint set — feed that into `blast-radius` before touching anything.

## Common Failure Modes to Avoid

- **Confident storytelling.** An uncited bullet goes in "inferred" or "hypotheses," never "what we found."
- **Citing the code as evidence for its own intent.** Motivation comes from an external source or is labeled inference.
- **Recency bias.** The current shape is often the accretion of many earlier decisions. Trace back.
- **Sycophantic agreement.** If the user embeds a hypothesis in the question, treat it as a candidate, check it independently.
- **Skipping investigators by anticipation.** Search first; a null result is data, a skipped search is a blind spot.
- **Collapsing investigators into one agent.** Each source has its own query vocabulary and pitfalls — one investigator per category, always launched together in one message.

## Reference Files

- `references/epistemics.md` — confidence tiers and phrasing guide (mandatory for the synthesizer)
- `references/investigator-prompt.md` — base prompt template for investigator agents
- `references/source-playbook.md` — index of category playbooks
- `references/sources/*.md` — one playbook per {{AGENT_NAME}} evidence category, plus cross-cutting `incident-postmortem.md`
- `references/synthesizer-prompt.md` — prompt template + output format for the synthesizer agent
