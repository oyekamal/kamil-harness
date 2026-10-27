# Incident & Postmortem Context

Not a separate source — a **cross-cutting angle**. Incidents often motivate defensive code ("we added this check after the outage"). If the target looks defensive (null checks, retry logic, timeout handling, rate limiting, feature flags), specifically hunt for incident history across every {{AGENT_NAME}} source:

- **Notion**: search for postmortem pages mentioning the target file, feature, or error string; look for tickets tagged incident/reliability-related.
- **Slack**: search engineering channels and any incident-flavored channel/thread around the dates the target code was added.
- **Git**: commit messages like "fix for incident", "add defensive check", "revert" followed by "re-apply with..." are strong signals.
- **Data warehouse**: an error-classifying event count that spikes right before the target's ship date, then drops after, is circumstantial corroboration even when the other sources are thin.

If you find an incident link in any source, pull the full postmortem — postmortems typically have an "Action Items" section that ties directly to code changes. When multiple sources corroborate each other (a Notion postmortem references a Slack thread that links the target PR, and the warehouse error count drops after the fix), the evidence is especially strong.

Worth spending time on when the code's defensive character makes an incident-driven origin plausible. Skip it for code that plainly isn't defensive.
