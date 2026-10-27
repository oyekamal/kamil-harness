# Slack (real-time chat source)

Adapted from upstream Cursor's generic `slack.md` playbook assuming read access through a Slack MCP (or a user-token search), scoped to your engineering channels.

## What this source contains

- Your engineering channels (e.g. `#engineering`, `#backend`, `#frontend`) — where PR discussion and incident fire-drills happen.
- DM threads with {{USER_NAME}} — casual "we decided X because Y" exchanges that never made it into a ticket.
- Thread replies linked from a ticket or PR.

## How to search it

Investigation is read-only: use the Slack MCP search/read tools, never a send-message tool.

1. **Search by feature name, symbol, or PR URL** across the engineering channels and any linked thread from the code anchor's PR/ticket.
2. **Search incident-flavored channels/threads** (`#sev-*`/`#incident-*` equivalents, or whatever your team's convention is) around the ship date if the code looks defensive.
3. **Pull full threads, not just the top message.** The rationale is often three replies deep.
4. **Check DM history with {{USER_NAME}}** if a ticket links to a DM thread.

## What good evidence looks like here

- A thread where the PR author and a reviewer debate an approach and land on a reason.
- A fire-drill decision made during an incident that never got written up elsewhere.
- A casual "let's just do X because Y" message that shaped a small, undocumented change.

## Common pitfalls

- **Thread sprawl.** A long thread may bury the actual decision in the middle — read the whole thing, don't stop at the first few replies.
- **Ephemeral context.** Slack messages can be edited or deleted; treat a message you can't re-verify as lower confidence.
- **Read-only.** Never attempt to post while investigating — this source is read-only for `why`.

## What to return

For each relevant message/thread: channel, permalink, author, timestamp, verbatim quote, and what it bears on the question.
