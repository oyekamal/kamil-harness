# Notion (tickets + docs)

Adapted from upstream Cursor's separate `linear.md` (ticket tracker) and `notion.md` (long-form docs) playbooks — here these collapse into one source, on the assumption that your Notion workspace holds both the ticket database and the long-form docs. If your tickets live elsewhere (Linear, Jira), adapt the steps to that MCP.

## What this source contains

- **Ticket databases** — task/bug/PR trackers and any related databases in the workspace.
- **Notion pages** — specs, PRDs, design notes, the "Self-Questions" page, project pages. This is the long-form-doc layer: problem statements, alternatives-considered sections, postmortems.
- **Page comments** — `@`-mentions and threaded discussion on a ticket or doc, often where the real "why" lives.

## How to search it

Use `mcp__claude_ai_Notion__*` tools (or the `notion-api` skill for query patterns). Look database IDs up via search — never guess one.

1. **Start with linked tickets.** If the code anchor's commits/PRs reference a ticket ID, fetch that page directly and read its full body plus comments, not just the property table.
2. **Keyword search** across the ticket database and general Notion search for the feature name, key symbols, or business terms. Try multiple phrasings.
3. **Walk parent/related pages.** A ticket may link a parent initiative or a spec page — follow it.
4. **Read comments in full.** Decisions ("we decided X because Y") often live in a comment thread on the ticket, not the page body.
5. **Check Status history where visible** — a ticket that moved Blocked → In progress → Done multiple times signals a decision that took several passes.

## What good evidence looks like here

- A ticket description stating the business problem or {{USER_NAME}}'s original request verbatim.
- A comment recording a decision or a scope change.
- A linked spec/doc with a "Problem statement" or "Alternatives considered" section.
- A postmortem page naming the target code as the fix for a specific incident.

## Common pitfalls

- **Stale tickets.** A ticket's Status may not reflect current reality. Cross-check its last-edited date against the code's actual ship date.
- **Boilerplate.** Auto-generated ticket bodies (e.g. stubs created from a Slack mention) may be thin. Don't mistake absence of detail in the stub for absence of a real reason — check comments and linked PR.
- **Access gaps.** If a page can't be reached, note it as a gap, don't guess its content.

## What to return

For each relevant ticket/page: title, ID/URL, the motivation text (verbatim quote), comments, linked PR/Slack thread, author and dates.
