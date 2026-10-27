---
name: two-axis-code-review
description: "Review the changes since a fixed point (commit, branch, tag, or merge-base) along two independent axes — Standards (does the code follow this repo's documented coding standards + a Fowler smell baseline?) and Spec (does the code match what the originating ticket/spec asked for?) — using two parallel Agent-tool calls that never see each other's output. Use when {{USER_NAME}} wants a branch/PR/work-in-progress reviewed, or says \"review since X\", \"two-axis review\", \"does this match the spec\". Heavier than the built-in review-pull-request checklist — reach for review-pull-request for a fast single-pass sanity check before opening a PR; reach for this when {{USER_NAME}} explicitly wants Standards and Spec judged separately (e.g. a long-running branch, a contested implementation, or before a PR that touched a lot of surface area)."
---

# Two-Axis Code Review

Two-axis review of the diff between `HEAD` and a fixed point {{USER_NAME}} supplies:

- **Standards**: does the code conform to this repo's documented coding standards?
- **Spec**: does the code faithfully implement the originating ticket / spec?

Both axes run as **parallel sub-agents** (Claude Code's `Agent` tool — two `Agent` calls in one message so they run concurrently) so they don't pollute each other's context, then this skill aggregates their findings.

**When to reach for this vs. `review-pull-request`**: `review-pull-request` is already installed and does a fast, single-pass checklist review — the right default before opening most PRs. Reach for this heavier two-axis version when Standards and Spec need to be judged independently (a change can pass one and fail the other — see "Why two axes" below), typically for a longer-running branch, a contested implementation, or a PR with enough surface area that a single pass would conflate "well-written" with "did what the ticket asked."

The tracker for the originating spec is whatever your project uses (GitHub Issues, Linear, Jira, Notion), or a `project_board.py` task/local file (see `.claude/rules/multi-project.md`) — never a generic "issue tracker."

## Process

### 1. Pin the fixed point

Whatever {{USER_NAME}} said is the fixed point (a commit SHA, branch name, tag, `main`/`develop`, `HEAD~5`, etc.). If he didn't specify one, ask for it.

Capture the diff command once: `git diff <fixed-point>...HEAD` (three-dot, so the comparison is against the merge-base). Also note the commit list: `git log <fixed-point>..HEAD --oneline`.

Before going further, confirm the fixed point resolves (`git rev-parse <fixed-point>`) and the diff is non-empty. A bad ref or empty diff should fail here, not inside two parallel sub-agents.

### 2. Identify the spec source

Look for the originating spec, in this order:

1. A ticket id/URL (GitHub issue, Linear, Jira, Notion page) referenced in the commit messages or branch name.
2. A `project_board.py` task id referenced in the commit messages or branch name (`python3 .claude/hooks/project_board.py list` / `board` to look it up).
3. A path {{USER_NAME}} passed as an argument.
4. A spec file under `docs/`, `specs/`, `vault/`, or `.scratch/` matching the branch name or feature.
5. If nothing is found, ask {{USER_NAME}} where the spec is. If he says there isn't one, the **Spec** sub-agent skips and reports "no spec available."

### 3. Identify the standards sources

Anything in the repo that documents how code should be written — `CODING_STANDARDS.md`, `CONTRIBUTING.md`, the repo's own `.claude/standards/`, or a project's `architecture.md`.

On top of whatever the repo documents, the Standards axis always carries the **smell baseline** below: a fixed set of Fowler code smells (_Refactoring_, ch.3) that applies even when a repo documents nothing. Two rules bind it:

- **The repo overrides.** A documented repo standard always wins; where it endorses something the baseline would flag, suppress the smell.
- **Always a judgement call.** Each smell is a labelled heuristic ("possible Feature Envy"), never a hard violation. Like any standard here, skip anything tooling already enforces (linters, type checkers).

<smell-baseline>

- **Mysterious Name**: a function, variable, or type whose name doesn't reveal what it does or holds. → rename it; if no honest name comes, the design's murky.
- **Duplicated Code**: the same logic shape appears in more than one hunk or file in the change. → extract the shared shape, call it from both.
- **Feature Envy**: a method that reaches into another object's data more than its own. → move the method onto the data it envies.
- **Data Clumps**: the same few fields or params keep travelling together (a type wanting to be born). → bundle them into one type, pass that.
- **Primitive Obsession**: a primitive or string standing in for a domain concept that deserves its own type. → give the concept its own small type.
- **Repeated Switches**: the same `switch`/`if`-cascade on the same type recurs across the change. → replace with polymorphism, or one map both sites share.
- **Shotgun Surgery**: one logical change forces scattered edits across many files in the diff. → gather what changes together into one module.
- **Divergent Change**: one file or module is edited for several unrelated reasons. → split so each module changes for one reason.
- **Speculative Generality**: abstraction, parameters, or hooks added for needs the spec doesn't have. → delete it; inline back until a real need shows.
- **Message Chains**: long `a.b().c().d()` navigation the caller shouldn't depend on. → hide the walk behind one method on the first object.
- **Middle Man**: a class or function that mostly just delegates onward. → cut it, call the real target direct.
- **Refused Bequest**: a subclass or implementer that ignores or overrides most of what it inherits. → drop the inheritance, use composition.

</smell-baseline>

### 4. Spawn both sub-agents in parallel

Use **one message with two `Agent` tool calls** (`subagent_type: general-purpose`) so they run concurrently and genuinely can't see each other's output.

**Standards sub-agent prompt** should include:

- The full diff command and commit list.
- The standards-source files found in step 3, **plus the smell baseline above pasted in full** (the sub-agent has no other access to it).
- The brief: "Report, per file/hunk where relevant, (a) every place the diff violates a documented standard: cite the standard (file + rule); and (b) any baseline smell you spot: name it and quote the hunk. Distinguish hard violations from judgement calls: documented-standard breaches can be hard, but baseline smells are always judgement calls, and a documented repo standard overrides the baseline. Skip anything tooling enforces. Under 400 words."

**Spec sub-agent prompt** should include:

- The diff command and commit list.
- The path or fetched contents of the spec (Notion page text, `project_board.py` task title/description, or spec file).
- The brief: "Report: (a) requirements the spec asked for that are missing or partial; (b) behaviour in the diff that wasn't asked for (scope creep); (c) requirements that look implemented but where the implementation looks wrong. Quote the spec line for each finding. Under 400 words."

If the spec is missing, skip the Spec sub-agent and note this in the final aggregation.

### 5. Aggregate

Present the two reports under `## Standards` and `## Spec` headings, verbatim or lightly cleaned. Do **not** merge or rerank findings across axes — that's the reranking the separation exists to prevent (see "Why two axes").

End with a one-line summary: total findings per axis, and the worst issue _within each axis_ (if any). Don't pick a single winner across axes.

If your project has an E2E or CI gate before `gh pr create`, feed this review's findings into it — a Standards or Spec finding that's a hard violation should block the PR, not just get logged.

## Why two axes

A change can pass one axis and fail the other:

- Code that follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Code that does exactly what the ticket asked but breaks the project's conventions → **Spec pass, Standards fail.**

Reporting them separately stops one axis from masking the other.
