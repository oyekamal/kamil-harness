---
name: reflect
description: "Spawn three parallel review agents over the active session transcript, surface durable learnings, and route each to a concrete edit on an existing skill/rule/agent file. Use when {{USER_NAME}} says 'reflect' or '/reflect', after a complex task lands cleanly, or after the agent hit dead ends and found a working path worth keeping. Feeds the same files harness-evolve and evolve-skill-from-traces write to."
---

# Reflect

Mine the current conversation for durable learnings, then route them into edits — same destination files as `harness-evolve` (`.claude/rules/`, `.claude/agents/`, `.claude/skills/`) and the same spirit as `evolve-skill-from-traces`.

**How this differs from `harness-evolve`:** `harness-evolve` is eval-gated and driven by `failures.jsonl` and drift checks, so it finds *failure* patterns. `reflect` is invoked explicitly ("reflect", after a task lands cleanly) and mines the *live transcript in this conversation* for learnings whether or not anything failed — a clean multi-step success worth encoding is just as valid a trigger as a mistake. Both write to the same file set; `reflect`'s job here is producing that Accepted/Rejected/Backlog list from a fresh three-reviewer read of the transcript, not re-scanning `failures.jsonl`. If a `reflect` run turns up a real recurring failure pattern instead of a one-off learning, say so explicitly and hand it to `harness-evolve` instead of applying it here.

## When to invoke

- {{USER_NAME}} said "reflect" or "/reflect".
- A complex task (5+ tool calls) just landed cleanly and the recipe is worth keeping.
- The agent hit dead ends, found the working path, and the path generalizes.
- {{USER_NAME}} corrected the agent's approach mid-task.
- A non-trivial workflow emerged that isn't captured anywhere.

Skip when the conversation is trivial, off-topic, or already covered by an existing skill/rule the agent followed correctly. One-offs are not learnings.

## Process

### 1. Locate the active transcript

{{AGENT_NAME}}'s session context lives in `vault/logs/YYYY-MM-DD.md` (per `CLAUDE.md`'s session logging rule) plus the current conversation itself. There is no Cursor-style `agent-transcripts/*.jsonl` directory here — the "transcript" for this skill's purposes is:

1. The current conversation's own turns (available to you directly — you don't need to re-read them from disk).
2. Today's `vault/logs/<date>.md` entries for this session, if the work spanned multiple actions logged there.

If neither is enough to reconstruct what happened (e.g. reflecting on a much older session), write a tight digest of what you remember/can reconstruct from `vault/logs/` and pass that to reviewers instead of a raw transcript.

### 2. Spawn three reviewers in parallel

**One message, three Agent tool calls**, `subagent_type` omitted or `"general-purpose"`. Claude Code has one model per session, so unlike the upstream Cursor skill (which assigns each lens a different configured model), all three reviewers here run on the same model — the diversity comes entirely from the distinct lens prompt each one gets, which already differentiates them sharply (judgment vs. tooling-specifics vs. contrarian/second-order). Don't skip a reviewer thinking "it'll just repeat the others" — the lens, not the model, is what's doing the differentiating work.

| Lens | Prompt template |
|---|---|
| Judgment | `references/judgment-reviewer.md` |
| Tooling | `references/tooling-reviewer.md` |
| Divergent | `references/divergent-reviewer.md` |

Pass each template verbatim, substituting the transcript source (conversation + `vault/logs/` digest) where marked. Reviewers may use any tool available to them (Read, Grep, Bash, Notion/Slack MCP for context lookups) but must not write or edit files — the parent applies edits after {{USER_NAME}}'s approval.

### 3. Synthesize

One more Agent tool call, `general-purpose`, using `references/synthesizer.md` verbatim with each reviewer's full output inlined where marked. The synthesizer returns a structured Accepted / Rejected / Backlog list.

### 4. Structural enforcement check

Sanity-check the synthesizer's Accepted list. For any item that would be enforced more reliably by a hook, a script, a metadata flag, or a runtime check than by more prose in a skill/rule file, move it from Accepted to Backlog. The synthesizer already applies this criterion; this is a final pass before edits land.

### 5. Apply

Before applying any Accepted edit, present the synthesizer's full Accepted/Rejected/Backlog output to {{USER_NAME}} and wait for explicit approval. {{USER_NAME}} picks which subset to apply and may redirect routings. Rule/skill/agent-file changes affect every future {{AGENT_NAME}} session — never auto-apply, same discipline `harness-evolve` follows for anything above its auto-apply tier.

Backlog items are noted for {{USER_NAME}}, not filed to an external tracker ({{AGENT_NAME}} has no devex tracker integration) — list them plainly so {{USER_NAME}} can decide.

For each approved Accepted item, follow the Routing field:

- **Trivial existing-file edit** (a one-line bullet, a tightened sentence, a stale fact corrected in `.claude/rules/*.md` or `.claude/agents/*.md`): apply directly.
- **Substantive existing-file edit** (a new section, a new pattern table, more than ~10 lines): apply directly but flag it clearly in the summary as a larger change, since there's no separate draft/iterate skill in this repo — `skill-creator` covers new-skill creation and iteration, not rule/agent file edits.
- **`tune description: <skill path>`** (the skill exists but didn't trigger when it should have): edit that skill's frontmatter `description` directly, and add the missing trigger phrases explicitly.
- **`new skill via skill-creator: <kebab-name>`**: hand creation to the `skill-creator` skill rather than inventing the shape ad hoc.

### 6. Summarize for {{USER_NAME}}

Short list, no preamble:

- Edits applied: `<file path>`. What changed, one line each.
- New skills created: `<skill path>`. One line each (rare).
- Backlog (noted, not filed anywhere automatically): `<item>` — one line each.
- Dropped: one line per rejected finding + reason from the synthesizer.
- If any finding looked like a recurring failure pattern rather than a one-off learning, say so and suggest handing it to `harness-evolve` instead.
