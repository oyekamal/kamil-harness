---
type: reference
last_verified: 2026-10-27
owner: agent
---

# Metadata Contract

Every markdown file (except CLAUDE.md) starts with:

    ---
    type: router|runbook|reference|investigation|plan|changelog
    last_verified: YYYY-MM-DD
    owner: agent
    ---

## Freshness SLOs
| Doc | Max staleness |
|-----|---------------|
| CLAUDE.md | 2 weeks |
| Routers / rules | 1 month |
| Reference docs | 2 months |
| Changelogs | none |

When `last_verified` exceeds the SLO → open a bead.
