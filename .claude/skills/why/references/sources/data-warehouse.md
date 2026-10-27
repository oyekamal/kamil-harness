# Data warehouse (e.g. BigQuery — infra, errors, and product analytics combined)

Merged from upstream Cursor's three separate playbooks (`datadog.md` infra observability, `sentry.md` error tracking, `databricks.md` product analytics warehouse) into one, because this setup assumes one tool covering this territory: a data-warehouse MCP (ideally a thin, governed query layer — see its own server instructions). If you have a dedicated Datadog/Sentry-equivalent, split this file back into separate playbooks rather than overloading it.

## What this source contains

- Observability/error tables — whatever BigQuery datasets the app logs errors, exceptions, or incident-relevant events into.
- Product/usage analytics tables — feature usage, event counts, experiment/flag exposure if instrumented.
- Table freshness metadata (a `check_table_freshness`-style tool, if the server has one).
- Governance rules (a `get_rules`-style tool, if present) — the contract for what SQL is allowed.

This is the runtime/data-reality layer: what actually happened in production or in user behavior around the time the target code shipped, as opposed to what was planned or discussed.

## How to search it

**If your MCP has a governed-query contract, follow it: never write ad-hoc SQL against the execute tool.** Tool names vary by server; the pattern is discovery first:

```
list_datasets
get_table_schema <dataset>.<table>
preview_table <dataset>.<table>
describe_data ...
get_rules        # read the governance rules before writing any query
```

Then, and only then, run the query, passing along any audit fields the server asks for (such as the verbatim user question). Treat every call against live data as a real, logged action, not a free scratch query.

1. **Orient before querying.** `list_datasets` / `get_table_schema` / `preview_table` are read-only discovery — use them to confirm a table exists and its columns, never to answer the actual "why" question directly.
2. **Time-bound every query.** Filter on a timestamp column with a window bracketing the code's ship date (commonly ±30 days).
3. **Look for a usage/error trajectory shift.** A step-function change in a relevant count right around the ship date is circumstantial evidence the code caused or resolved something.
4. **Look for a threshold match.** If the target code hardcodes a constant (a limit, a timeout, a retry count), check whether a percentile of a relevant column in the pre-ship window matches it.
5. **Check table freshness** with `check_table_freshness` before trusting a "no results" — a stale or empty table is a gap, not a null result.

## What good evidence looks like here

- An error-classifying event count that drops to near-zero in the days after a defensive-code PR ships.
- A usage count that ramps from zero right after a feature-flag PR merges.
- A hardcoded constant that matches a p99/p95 of a real column from the relevant time window.

## Common pitfalls

- **Correlation is not causation.** A spike-then-stabilize pattern around a PR date is suggestive, not definitive — check for other changes in the same window via the git investigator's findings.
- **Instrumented ≠ caused.** A table's existence means someone cared enough to log something, not that the target code exists because of it.
- **Schema drift / freshness gaps.** Always call `check_table_freshness` and `get_table_schema` before concluding "no relevant data" — an empty result from a stale table is a gap, not a null.
- **Never bypass governance.** Do not attempt raw SQL outside the server's governed contract even to "just check something quickly."

## What to return

For each finding: table name (fully qualified), the exact query run, time window, a compact numeric summary (counts/percentiles/first-last-seen) — never raw row dumps — and the temporal correlation with the target's ship date.
