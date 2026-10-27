---
name: gmail
description: >
  Gmail management via a connected Gmail MCP. Use when reading, searching, drafting,
  labeling, or threading emails. Wraps mcp__claude_ai_Gmail__* tools with decision logic.
  USE WHEN: "check my email", "search emails", "draft a reply", "send email", "label this",
  "what emails came in", "find the email about X", "mark as read", "create draft".
  DO NOT USE FOR: Slack messages (use the Slack MCP), Notion notifications (use the Notion MCP).
source: custom
allowed-tools: [mcp__claude_ai_Gmail__search_threads, mcp__claude_ai_Gmail__get_thread, mcp__claude_ai_Gmail__create_draft, mcp__claude_ai_Gmail__list_labels, mcp__claude_ai_Gmail__create_label, mcp__claude_ai_Gmail__label_thread, mcp__claude_ai_Gmail__label_message, mcp__claude_ai_Gmail__list_drafts, mcp__claude_ai_Gmail__unlabel_thread, mcp__claude_ai_Gmail__apply_sensitive_thread_label]
---

# Gmail — Email Management via MCP

**Requires:** a Gmail MCP connected in Claude Code (`mcp__claude_ai_Gmail__*` tools).

## Decision Tree

```
Request arrives
├── "search / find / check" → search_threads(query)
├── "read / open / what does it say" → get_thread(threadId)
├── "draft / compose / write" → create_draft(to, subject, body)
├── "label / tag / categorize" → label_thread or label_message
├── "what labels exist" → list_labels()
├── "show drafts" → list_drafts()
└── "send" → create_draft first, confirm, then note: no send tool yet (MCP read-only for sends)
```

## Tool Reference

| Tool | When to use | Key params |
|---|---|---|
| `search_threads` | Find emails by keyword, sender, date | `query` (Gmail syntax) |
| `get_thread` | Read full conversation | `threadId` |
| `create_draft` | Compose unsent email | `to`, `subject`, `body` |
| `list_labels` | See all Gmail labels | — |
| `create_label` | Make a new label | `name` |
| `label_thread` | Apply label to whole thread | `threadId`, `labelId` |
| `label_message` | Apply label to one message | `messageId`, `labelId` |
| `list_drafts` | Show unsent drafts | — |
| `apply_sensitive_thread_label` | Mark thread as sensitive | `threadId` |

## Gmail Search Syntax

```
from:person@example.com          # by sender
to:me                            # sent to me
subject:"project update"         # subject contains
after:2026/06/01                 # after date
before:2026/06/30                # before date
is:unread                        # unread only
is:starred                       # starred
has:attachment                   # has file attached
label:important                  # specific label
"exact phrase"                   # exact match
-word                            # exclude word
```

## Common Workflows

### Triage inbox
```
1. search_threads("is:unread after:yesterday") — find unread
2. get_thread(id) for each relevant one — read content
3. label_thread by category (action-needed, fyi, waiting-on)
```

### Draft a reply
```
1. get_thread(threadId) — read the original
2. create_draft(to=sender, subject="Re: ...", body=...) — compose
3. Tell {{USER_NAME}}: "Draft saved — review and send from Gmail"
```

## Hard Rules

1. **Never claim to have sent an email** — MCP has no send tool. Always say "draft saved."
2. **Confirm before labeling in bulk** — "Label all 47 threads? (yes/no)" before mass ops.
3. **Sensitive emails** — Use `apply_sensitive_thread_label` before any label op on HR/finance threads.
4. **Read before acting** — `get_thread` before drafting a reply; don't reply blind.
5. **Search before creating labels** — `list_labels` first to avoid duplicates.
