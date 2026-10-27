# Source playbooks

The `why` skill spawns one investigator per {{AGENT_NAME}} evidence category, each reading a single source-specific playbook below.

| Category | Playbook | {{AGENT_NAME}}'s real tool |
|---|---|---|
| Source control & code | [`code-archaeology.md`](./sources/code-archaeology.md) | `git`, `gh` (Bash) |
| Tickets + long-form docs | [`notion.md`](./sources/notion.md) | `mcp__claude_ai_Notion__*` (or your tracker's MCP) |
| Real-time team chat | [`slack.md`](./sources/slack.md) | Slack MCP search, engineering channels |
| Infra + errors + product analytics | [`data-warehouse.md`](./sources/data-warehouse.md) | your warehouse MCP (e.g. BigQuery) |

Cross-cutting:

- [`incident-postmortem.md`](./sources/incident-postmortem.md) — add this if the target code looks defensive (null checks, retry, timeout, rate limit, feature flag, egress guard, OOM handler).

Upstream Cursor's `why` skill discovers MCPs at runtime and maps them to 7 categories (issue tracker, long-form docs, chat, infra observability, error tracking, product analytics, plus source control). This version's toolset is fixed and smaller: Notion (or your tracker) covers both tickets and docs, and one data-warehouse source covers what would otherwise be three categories (infra, error tracking, analytics). If you connect a dedicated error tracker or observability tool, split `data-warehouse.md` back into separate playbooks rather than overloading one file.
