---
name: interrogate
description: "Use for 'interrogate', 'adversarial review', 'multi-angle review', 'challenge this', 'stress test this code', 'find blind spots', or 'tear this apart'. Multiple reviewer agents challenge changes from independently-framed adversarial angles before a lead-judgment synthesis. Pairs with review-pull-request; use this when you want genuine adversarial pressure, not just a checklist pass."
---

# Interrogate

Spawn multiple reviewer agents to adversarially review code changes, each with a distinctly different adversarial framing. Every reviewer gets the same prompt and rubric except for its persona. The adversarial signal comes from framing diversity, not assigned model diversity — Claude Code runs one model per session, unlike the upstream Cursor `interrogate` skill, which spawns one reviewer per configured model family (claude/gpt/grok/etc.) to get independent blind spots. See the adaptation note in Step 3 for how this is compensated.

The deliverable is a synthesized verdict. Do NOT auto-apply changes.

## Step 1. Determine Scope

Identify what to review from context:

- If the user points at specific files or a diff, use that.
- If on a feature branch, run `git diff main...HEAD` (or the appropriate base branch) for the full changeset.
- If the user's message references recent work, gather the relevant files.

Package the diff (or file contents) plus any surrounding context files the reviewers need to understand the code.

## Step 2. State the Intent

Before spawning reviewers, state the intent explicitly. What is this code trying to accomplish? Derive this from the user's message, commit messages, the PR description if one exists, and the code itself. Write one clear paragraph. Reviewers challenge whether the work achieves the intent well, not whether the intent itself is correct. If unsure about intent, ask before proceeding.

## Step 3. Spawn Reviewers

Launch all reviewers **in a single message with multiple Agent tool calls** so they run concurrently (same pattern as `superpowers:dispatching-parallel-agents`). Use `general-purpose` for each — there is no per-model routing available.

**Adaptation note:** the upstream skill's rigor comes from asking genuinely different model families the same question. That lever doesn't exist here. The substitute is prompting diverse personas — each reviewer gets a distinctly different adversarial stance in its `{PERSONA}` slot, so they still catch different classes of problem even running on the same model:

| Reviewer | Default persona |
|----------|------------------|
| Reviewer A | "Review as a security-focused skeptic. Assume every input is attacker-controlled until proven otherwise." |
| Reviewer B | "Review as a performance- and correctness-focused engineer who has been burned by silent data corruption before. Trace every state mutation." |
| Reviewer C | "Review assuming the author is subtly wrong somewhere and your job is to find where. Distrust the PR description; read only the diff and the call sites." |
| Reviewer D (optional, for a large/risky change) | "Review as a maintainer who will own this code in six months with no memory of why it was written this way. Flag anything that won't explain itself." |

Use 2-3 reviewers for a normal change, 4 for something big or high-stakes. Fewer, more sharply-differentiated personas beat many similar ones.

For each reviewer:
- `Agent` tool call, `subagent_type` omitted or `"general-purpose"`
- Read `references/reviewer-prompt.md` and fill in the template with: the stated intent, the diff/files, the rubric from `references/rubric.md`, the code-quality lens from `references/code-quality-review.md`, and this reviewer's persona.

The same filled template (minus persona) goes to all reviewers, so every one applies the same rubric and code-quality lens.

## Step 4. Synthesize

As results come back, build a unified picture:

1. **Parse all findings** from the reviewers.
2. **Identify consensus.** Findings raised by 2+ reviewers independently are highest signal.
3. **Identify lone-reviewer findings.** Still worth reading, weighted lower.
4. **Deduplicate.** Different reviewers may describe the same issue differently — merge and note which reviewers raised it.
5. **Note disagreements.** If one reviewer flags something and another explicitly says the opposite, that's useful context for the verdict.

## Step 5. Lead Judgment

You are the lead reviewer, a pragmatic senior engineer, not a neutral aggregator. Read `references/lead-judgment.md` for the full framework. Reviewers only saw a slice of the codebase and a one-paragraph intent statement — you have the full context (what was already tried, what constraints exist, what stage this is at). Use that context aggressively.

Categorize every finding:

- **Act on.** Real issues affecting correctness, security, or maintainability given the actual goals. Would block a real PR.
- **Consider.** Legitimate points, unclear if they outweigh the cost of addressing them now.
- **Noted.** Technically valid, not actionable. Context-dependent or low-impact given the current stage.
- **Dismissed.** Wrong, nitpicky, or missing context. Brief explanation why.

For each finding: which reviewer(s) raised it, the category, a one-line rationale.

## Output Format

### Intent
> [The stated intent paragraph from Step 2]

### Reviewers
- Reviewer [label]: [persona summary], [N findings] (one bullet per reviewer)

### Act On
[Findings that should be addressed. For each: description, which reviewers raised it, why it matters.]

### Consider
[Findings worth thinking about. For each: description, which reviewers raised it, tradeoff involved.]

### Noted
[Valid but low-priority. Brief list.]

### Dismissed
[Rejected findings with brief rationale — shows what was filtered out so the user can override.]

### Agreement Map
[Where reviewers agreed, where they diverged, and what the pattern tells us.]

## Where this fits with existing skills

`review-pull-request` is the standard checklist self-review before opening a PR. `interrogate` is heavier — reach for it on a change you genuinely don't trust yet, or before a PR that touches security or data-isolation invariants. `reflect` and `harness-evolve` are a different pipeline entirely: they mine a *finished session's transcript* for durable process learnings, not a diff for correctness bugs. Don't conflate the two.
