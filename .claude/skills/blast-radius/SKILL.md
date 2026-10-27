---
name: blast-radius
description: "Find what a change could break somewhere else before it ships, beyond the diff, and prove the one fact it's safe because of by running real code instead of writing it up. Use for 'blast radius of X', 'what could this break', or reviewing a small diff you don't trust. Pairs with any claim gate or E2E gate you run before calling a fix done — this is where the safety fact behind those gates actually gets proven."
---

# Blast radius

Find what a change breaks somewhere else, before it ships. Use for "blast radius of X", "what could this break", or reviewing a small diff you don't trust yet.

Companion to reading the code and to `why`. Reading the code tells you what it does. `why` tells you why it's shaped that way. Blast radius tells you what it breaks somewhere else.

Listing the callers is not the job — a grep does that in a second. The job is the breakage grep won't show you.

## Don't trust your own writeup

A blast-radius writeup that sounds right is worthless. It reads as convincing whether or not it's true, and that is the trap you are walking into. So don't hand back the writeup. Find the one or two facts the whole thing depends on and prove them by running code. Words are where you start, not what you ship.

### How sure are you

For each fact the change's safety depends on, get it as far down this list as is cheap, and say where it stopped.

1. You said so. Worthless on its own.
2. You pointed at the line. A real `file:line`, or the library's own source.
3. You showed the bad case can't happen. You walked the failure step by step and it doesn't reach.
4. You ran it. A script or test that calls the real code and fails loud if you're wrong.
5. You reproduced it in the running app.

Any safety fact you can't get to step 4, say so out loud. Don't write it up as settled. Step 4 is usually one small script that imports the same code the app ships and calls the exact function you're worried about. For frontend work specifically, step 5 is what `webapp-testing` (Playwright) is for — use it rather than hand-waving "it should render fine."

## Steps

1. **Read the change.** The diff, the symbols it adds, changes, and deletes, and what it now does differently, including the part the diff doesn't spell out. Use `why` Step 2 (git/gh anchor-building) to pull the PR and commits if the diff isn't already in context.
2. **Find the one fact it's safe because of.** Most changes that look scary are safe because of a single fact, like "this call only drops already-dead cache entries and does nothing else." Find that fact. If it holds, most of the scary cases die at once. Spend your time here, not on a long list of maybes.
3. **Look where grep stops.** Read the source of the library you call, and check its pinned version and any local patch. Work out when things run (async ordering, teardown/unmount, sync vs. IndexedDB vs. React lifecycle). Follow what a symbol search misses: the JSON an API returns, a DB column, a wire format, a feature flag, code three hops downstream (another service, another repo).
4. **Be honest about each risk.** Give it a real chance of happening and a real cost if it does. Keep the risks you confirmed; list the ones you checked and cleared separately. Same rules as `why` — cite a real `file:line`, a search that finds nothing is still an answer, and never make up a caller or an API.
5. **Prove the one fact.** Write a script or test that runs the real code, run it, and paste what happened. If you can't prove it cheaply, mark it unproven. Don't round up.
6. **For a big or wide change, spawn multiple review angles.** Claude Code runs one model per session, so the diversity here comes from prompting, not from asking different model families the same question (the upstream Cursor skill's "arena" step). Launch 2-3 Agent tool calls in one message, each with a distinctly different adversarial framing — e.g. "review this assuming the async ordering is wrong," "review this as someone who only trusts what a test proves," "review this looking specifically for cross-profile/cross-tenant leakage" — then merge what each one catches. Different framings catch different real bugs even on the same model.

## What to hand back

- **What it does.** What changed, including the part that isn't obvious.
- **The one fact it's safe because of.** State it, say which step (1-5 above) you got it to, and show the proof. If you couldn't prove it, write unproven.
- **Risks.** Only the real ones. Each names how it breaks, the `file:line`, how likely and how bad, and how to check. Paste the proof for the ones that matter.
- **Cleared.** What you checked and why it's fine.
- **Before you merge.** The cheapest test or repro that catches the real bug, including the script you wrote.

Write it through `unslop`, cite real code, and strip anything private before it goes anywhere public (Slack, a PR description).

**Reply:** the writeup above, with the one safety fact either proven or marked unproven.

## Where this fits with existing gates

- If you gate "done" claims on a verification checklist (see `superpowers:verification-before-completion`), a blast-radius/call-site grep belongs on it. Run this skill to actually produce that item, not just narrate it.
- Orchestrator rule 10 (E2E gate) requires a passing E2E run before `gh pr create`. `blast-radius` step 5 (reproduce in the running app) is what makes that gate real rather than a checkbox — use `webapp-testing` to drive the actual repro.
