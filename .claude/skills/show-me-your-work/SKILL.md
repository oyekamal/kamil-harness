---
name: show-me-your-work
description: "Keep a reviewable decision trail for long-running or unattended {{AGENT_NAME}} work: a TSV log with one row per decision (what, why, evidence, result). Local by default; commit it when a reviewer needs the trail to trust the result. Use for autonomous or multi-phase runs, scheduled/looped runs, or work {{USER_NAME}} reviews after stepping away."
---

# Show me your work

For work {{USER_NAME}} reviews after the fact (a looped run that ran unattended, a multi-phase fix in your main app, a batch job), a decision trail lets him reconstruct what was decided, why, and on what evidence, without rerunning the work or reading the whole transcript. Keep one canonical log so the trail is consistent and a future {{AGENT_NAME}} session can find it.

## The format

A single TSV file, one row per decision. TSV because GitHub renders it as a sortable table, `column -s$'\t' -t` and spreadsheets read it, and a row appends with one command. Cells stay single-line. Evidence is a pointer, not prose.

Copy `references/decision-log-template.tsv` (the header row) to start a clean log. Columns:

- **ts.** ISO8601 timestamp. The timeline axis.
- **phase.** The phase or workstream (e.g. `plan`, `build`, `test`, `ship`, or a ticket/task id).
- **decision.** What was chosen or done, one line.
- **why.** The reason in plain words. If a principle drove it, say it plainly (`explored options first, this was a one-way door`), not as jargon.
- **evidence.** A link or path that proves it: commit SHA, PR number, `file:line`, Notion page URL, or an artifact/trace/screenshot path. Never a paragraph.
- **result.** The outcome or predicate state: `tests green`, `reverted`, `pixel-diff 0`, `INCONCLUSIVE`, `open`.

An example, plain-spoken so a reviewer reads it at a glance. Illustration only — don't copy these rows into a real log.

```
ts	phase	decision	why	evidence	result
2026-08-24T09:02:00Z	plan	counted the affected files first, about 40 across the repo	wanted to know the size before starting a long run	commit 3a9f1c2	found 5 things to sort out before starting
2026-08-24T09:40:00Z	develop	took screenshots of the old settings screen before changing anything	so we can compare old against new and catch any visual change	scripts/snapshot.sh, baseline/	saved 12 reference screenshots
2026-08-24T11:15:00Z	develop	moved the widget styles over without changing how it looks	keep the change small and the result identical	commit 7c21e0a, pixel-diff 0	looks identical, tests pass
2026-08-24T12:30:00Z	deliver	threw out a subagent's earlier draft because its screenshots were blank	checked the real files instead of trusting its summary	worktree reset	reverted, tightened the instructions for next run
```

## Logging a row

Write each entry the way you'd tell {{USER_NAME}} what happened. Plain words, concrete actions, no AI-speak or abstract jargon (the `unslop` skill's standard applies to log text too). A reviewer should understand each row without decoding it.

Use `scripts/log.sh <logfile> <phase> <decision> <why> <evidence> <result>` so rows stay well-formed. It stamps `ts`, writes the header on first use, strips stray tabs/newlines, and prefixes any cell starting with `=`, `+`, `-`, or `@` with a single quote so opening the log in a spreadsheet doesn't trigger formula execution. A bare `printf` appending a row works too, but mind those same bytes if cells come from generated or user-supplied text (a PR title, a Slack message).

Log decision points and checkpoints, not every action: a fork chosen, a unit completed with its verification result, a pivot or revert with its trigger, a blocker surfaced. For loop/tick runs, one row per iteration is enough. Skip the trivial and self-evident.

## Where it lives

By default the log is a working artifact, not committed. Keep it at `decisions.tsv` in the work dir, or `.audit/<task-slug>.tsv` when several efforts run at once (e.g. `.audit/<ticket-id>.tsv`), and leave it out of git. Most work doesn't need a committed trail; the local log still keeps the run honest and can be discarded after.

Commit it only when the work is ambitious enough that {{USER_NAME}} needs the trail to trust the result: a large multi-file migration, a multi-day autonomous effort, anything where confidence has to be shown rather than assumed. A committed log renders as a table in the PR.

## Rules

- One row is one decision or checkpoint. If it doesn't fit on one line, the decision isn't crisp yet.
- Append-only. A wrong call gets a new row that supersedes it. Never edit or delete history.
- Prefer evidence produced by a committed script (`scripts/log.sh`, an existing test runner) over a hand-made one-off, so a reviewer can re-run it.

## Audit the log against the transcript

At the end of the run, before handing back, check the log told the truth. Read this session's transcript/log — for an agent session this is `vault/logs/YYYY-MM-DD.md` (per `CLAUDE.md`'s session rule) not any other project's logs. Walk the log against what actually happened:

- Every row maps to a real action. Cut invented or aspirational entries.
- Each row's evidence resolves and shows what the row claims.
- A fork, pivot, or abandoned approach that shaped the work but isn't logged is a gap. Add it.
- Drop padding. If nobody would audit a row, it doesn't earn its place.

Fix the log, not the story. If the work diverged from what a row claims, the row is wrong.

## Cross-perspective review of the trail

Before handing back, spawn one Agent-tool subagent to review the trail with a framing genuinely different from the one that produced it — for example "review this as a skeptical auditor who assumes every row without a resolving evidence pointer is a fabrication until proven otherwise." Self-review is not a substitute; the point is fresh eyes.

**Adaptation note:** the upstream Cursor skill gets this diversity by spawning the reviewer on a different *model family* than the one that did the work. Claude Code runs one model per session, so that lever isn't available — the substitute is framing diversity: a distinctly adversarial persona in the reviewer's prompt, not a different model. Note this plainly rather than silently dropping the cross-check.

The reviewer reads the audit trail and this session's log, then flags what {{USER_NAME}} should pay attention to. Not a redo of the work — a scan for what's suboptimal or risky:

- Decisions logged with weak or absent evidence.
- Verification steps skipped or claimed without proof in the transcript.
- Choices that look risky in hindsight (premature, scope-creeping, papering over a symptom).
- Gaps {{USER_NAME}} would otherwise miss on a casual skim.

Every reply for a run that produced a trail ends with an "Attention" section. Lead with `reviewed by: framing-diverse subagent` on its own line, then list each flag pointing to specific rows or moments. "No flags" is a valid value. The self-audit above asks if the log told the truth; this asks what {{USER_NAME}} should still scrutinize even when it did.

## Reviewing the trail

Read top to bottom, follow the evidence pointers, spot-check. GitHub renders a committed TSV as a table; `column -s$'\t' -t decisions.tsv` renders it in a terminal. A row whose evidence doesn't resolve, or whose result is unverified, is the audit catching a gap.

## Composing this skill

Other skills and agents that run unattended route their audit trail here instead of inventing one. Reference it by name and let it own the format; don't restate the columns elsewhere.
