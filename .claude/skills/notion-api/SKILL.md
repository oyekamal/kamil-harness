---
name: notion-api
version: 1.0.0
description: Notion API for workspace automation including databases, pages, blocks, query/filter syntax, and integration patterns. Use when automating Notion database entries, querying with complex filters, creating/updating pages programmatically, or building Notion integrations.
---

# Notion API Integration Skill

**Requires:** a Notion integration token (`NOTION_API_KEY`) with the target pages/databases shared to it.

Master the Notion API for workspace automation, including databases, pages, blocks, query/filter syntax, and integration patterns.

## When to Use

USE when: automating database entries, building dashboards from Notion data, syncing external data to Notion, querying with complex filters, creating pages programmatically.

DON'T USE when: real-time sync needed (API has rate limits), building chat features, need sub-second response times.

## Setup

```bash
export NOTION_API_KEY="secret_xxxxxxxxxxxxxxxxxxxxx"
# Verify connection
curl -s "https://api.notion.com/v1/users/me" \
    -H "Authorization: Bearer $NOTION_API_KEY" \
    -H "Notion-Version: 2022-06-28" | jq
```

```python
from notion_client import Client
import os
notion = Client(auth=os.environ["NOTION_API_KEY"])
```

## Database Operations

```python
# Search for databases
results = notion.search(filter={"property": "object", "value": "database"})

# Query all items
results = notion.databases.query(database_id="your-database-id")

# Query with filter
results = notion.databases.query(
    database_id="your-database-id",
    filter={"property": "Status", "select": {"equals": "In Progress"}}
)

# Paginated query (handles large databases)
def query_all_pages(database_id, filter=None):
    all_results = []
    has_more = True
    start_cursor = None
    while has_more:
        response = notion.databases.query(
            database_id=database_id, filter=filter,
            start_cursor=start_cursor, page_size=100
        )
        all_results.extend(response["results"])
        has_more = response["has_more"]
        start_cursor = response.get("next_cursor")
    return all_results
```

## Filter Syntax Reference

```python
# Text filters
{"property": "Name", "title": {"equals": "Exact Match"}}
{"property": "Name", "title": {"contains": "partial"}}
{"property": "Name", "title": {"starts_with": "Prefix"}}
{"property": "Notes", "rich_text": {"contains": "keyword"}}

# Number filters
{"property": "Amount", "number": {"greater_than": 50}}
{"property": "Amount", "number": {"less_than_or_equal_to": 99}}
{"property": "Amount", "number": {"is_not_empty": True}}

# Date filters
{"property": "Due Date", "date": {"before": "2025-01-20"}}
{"property": "Due Date", "date": {"after": "2025-01-10"}}
{"property": "Due Date", "date": {"past_week": {}}}
{"property": "Due Date", "date": {"next_month": {}}}
{"property": "Due Date", "date": {"this_week": {}}}

# Select/Multi-select
{"property": "Status", "select": {"equals": "Done"}}
{"property": "Status", "select": {"does_not_equal": "Done"}}
{"property": "Tags", "multi_select": {"contains": "urgent"}}

# Checkbox
{"property": "Completed", "checkbox": {"equals": True}}

# Relation
{"property": "Project", "relation": {"is_not_empty": True}}
{"property": "Project", "relation": {"contains": "page-id"}}

# Compound (AND / OR / Nested)
{"and": [
    {"property": "Status", "select": {"equals": "In Progress"}},
    {"property": "Priority", "select": {"equals": "High"}},
    {"property": "Due Date", "date": {"before": "2025-02-01"}}
]}

{"or": [
    {"property": "Status", "select": {"equals": "To Do"}},
    {"property": "Status", "select": {"equals": "In Progress"}}
]}

# Nested AND with OR
{"and": [
    {"or": [
        {"property": "Priority", "select": {"equals": "High"}},
        {"property": "Priority", "select": {"equals": "Medium"}}
    ]},
    {"property": "Status", "select": {"does_not_equal": "Done"}}
]}
```

## Page Operations

```python
# Create page in database
new_page = notion.pages.create(
    parent={"database_id": "your-database-id"},
    properties={
        "Name": {"title": [{"text": {"content": "New Task"}}]},
        "Status": {"select": {"name": "To Do"}},
        "Priority": {"select": {"name": "High"}},
        "Due Date": {"date": {"start": "2025-01-20"}},
        "Tags": {"multi_select": [{"name": "dev"}, {"name": "urgent"}]},
        "Notes": {"rich_text": [{"text": {"content": "Description here"}}]},
        "Completed": {"checkbox": False},
        "Amount": {"number": 100},
        "URL": {"url": "https://example.com"}
    }
)

# Update page properties
notion.pages.update(
    page_id="page-id",
    properties={
        "Status": {"select": {"name": "Done"}},
        "Completed": {"checkbox": True}
    }
)

# Archive (soft delete)
notion.pages.update(page_id="page-id", archived=True)

# Read property value helpers
def get_title(page): 
    return page["properties"]["Name"]["title"][0]["plain_text"] if page["properties"]["Name"]["title"] else ""

def get_select(page, prop):
    return page["properties"][prop]["select"]["name"] if page["properties"][prop]["select"] else None

def get_date(page, prop):
    return page["properties"][prop]["date"]["start"] if page["properties"][prop]["date"] else None
```

## Block Operations

```python
# Get page blocks
blocks = notion.blocks.children.list(block_id="page-id")

# Append blocks to page
notion.blocks.children.append(
    block_id="page-id",
    children=[
        {"type": "heading_2", "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": "Section Title"}}]
        }},
        {"type": "paragraph", "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": "Paragraph text"}}]
        }},
        {"type": "bulleted_list_item", "bulleted_list_item": {
            "rich_text": [{"type": "text", "text": {"content": "List item"}}]
        }},
        {"type": "to_do", "to_do": {
            "rich_text": [{"type": "text", "text": {"content": "Task"}}],
            "checked": False
        }},
        {"type": "code", "code": {
            "language": "python",
            "rich_text": [{"type": "text", "text": {"content": "print('hello')"}}]
        }}
    ]
)

# Update a block
notion.blocks.update(
    block_id="block-id",
    paragraph={"rich_text": [{"type": "text", "text": {"content": "Updated text"}}]}
)
```

## Rate Limiting

Notion API: 3 requests/second. Use delays for bulk operations:

```python
import time

def safe_notion_request(fn, *args, delay=0.35, **kwargs):
    time.sleep(delay)  # 350ms between calls
    return fn(*args, **kwargs)
```

## Common Patterns (task-tracker database)

```python
# Query a task database for pending tickets assigned to the agent (set these env vars to your own IDs)
pending = notion.databases.query(
    database_id=os.environ["NOTION_DATABASE_ID"],
    filter={
        "and": [
            {"property": "Status", "status": {"equals": "Not started"}},
            {"property": "Assignee", "people": {"contains": os.environ["NOTION_AGENT_USER_ID"]}}
        ]
    }
)

# Update ticket status
notion.pages.update(
    page_id=ticket_id,
    properties={"Status": {"status": {"name": "In progress"}}}
)

# Add agent session log as page comment
notion.comments.create(
    parent={"page_id": ticket_id},
    rich_text=[{"type": "text", "text": {"content": f"Session started: {session_id}"}}]
)
```
