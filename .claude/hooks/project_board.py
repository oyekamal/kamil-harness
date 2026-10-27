#!/usr/bin/env python3
"""
project_board.py — Agent's cross-project registry + task board.

Absorbed from researching the best multi-project Claude Code orchestrators
on GitHub (ccmanager, agent-kanban, claude-mpm, kanban-code): auto-discovery
of every project Agent works in, a lightweight cross-repo task board with
dependencies and claiming, and idle/active/blocked status per project — all
inside the shared harness.db (see agent_harness_db.py) rather than a separate tool.

Tables added to ~/.agent-harness/harness.db (additive, safe to re-run):
  projects — every git repo Agent has touched: id, name, path, kind, last_touched_at
  tasks    — cross-project task board: id, project_id, title, status,
             depends_on (task id, nullable), claimed_by, created_at, updated_at

Usage:
    project_board.py scan [root ...]         # discover git repos under given roots
    project_board.py list                     # list known projects
    project_board.py task add <project> <title> [--depends-on ID]
    project_board.py task claim <task_id> <who>
    project_board.py task done <task_id>
    project_board.py board                     # cross-project kanban view (text)
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agent_harness_db import get_db  # noqa: E402

_EXTRA_SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    path            TEXT NOT NULL UNIQUE,
    kind            TEXT NOT NULL DEFAULT 'repo',
    last_touched_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  TEXT NOT NULL REFERENCES projects(id),
    title       TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'todo',
    depends_on  INTEGER REFERENCES tasks(id),
    claimed_by  TEXT,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tasks_project_status ON tasks(project_id, status);
"""

STATUSES = ("todo", "in_progress", "blocked", "done")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _db():
    db = get_db()
    db.executescript(_EXTRA_SCHEMA)
    db.commit()
    return db


def _slug(path: Path) -> str:
    return path.name.lower().replace(" ", "-")


def scan(roots: list[str]) -> list[str]:
    """Discover git repos under each root (root itself, or its direct children)."""
    db = _db()
    found = []
    for root_str in roots:
        root = Path(root_str).expanduser().resolve()
        if not root.exists():
            continue
        candidates = [root] if (root / ".git").is_dir() else [
            p for p in root.iterdir() if p.is_dir() and (p / ".git").is_dir()
        ]
        for path in candidates:
            pid = _slug(path)
            db.execute(
                "INSERT INTO projects (id, name, path, kind, last_touched_at) VALUES (?, ?, ?, 'repo', ?) "
                "ON CONFLICT(path) DO UPDATE SET last_touched_at=excluded.last_touched_at",
                (pid, path.name, str(path), _now()),
            )
            found.append(f"{pid}  {path}")
    db.commit()
    return found


def list_projects() -> list[tuple]:
    db = _db()
    return db.execute(
        "SELECT id, name, path, last_touched_at FROM projects ORDER BY last_touched_at DESC"
    ).fetchall()


def touch_project(project_id: str) -> None:
    db = _db()
    db.execute("UPDATE projects SET last_touched_at=? WHERE id=?", (_now(), project_id))
    db.commit()


def task_add(project_id: str, title: str, depends_on: int | None = None) -> int:
    db = _db()
    row = db.execute("SELECT id FROM projects WHERE id=?", (project_id,)).fetchone()
    if row is None:
        raise SystemExit(f"unknown project '{project_id}' — run `scan` first")
    now = _now()
    cur = db.execute(
        "INSERT INTO tasks (project_id, title, status, depends_on, created_at, updated_at) "
        "VALUES (?, ?, 'todo', ?, ?, ?)",
        (project_id, title, depends_on, now, now),
    )
    db.commit()
    return cur.lastrowid


def task_set_status(task_id: int, status: str, claimed_by: str | None = None) -> None:
    if status not in STATUSES:
        raise SystemExit(f"status must be one of {STATUSES}")
    db = _db()
    if status == "in_progress":
        blocker = db.execute(
            "SELECT t2.id, t2.title, t2.status FROM tasks t1 "
            "JOIN tasks t2 ON t1.depends_on = t2.id WHERE t1.id=? AND t2.status != 'done'",
            (task_id,),
        ).fetchone()
        if blocker:
            raise SystemExit(f"blocked: depends on task #{blocker[0]} '{blocker[1]}' ({blocker[2]})")
    fields = "status=?, updated_at=?"
    params: list = [status, _now()]
    if claimed_by is not None:
        fields += ", claimed_by=?"
        params.append(claimed_by)
    params.append(task_id)
    db.execute(f"UPDATE tasks SET {fields} WHERE id=?", params)
    db.commit()


def board() -> str:
    db = _db()
    rows = db.execute(
        "SELECT p.name, t.id, t.title, t.status, t.claimed_by, t.depends_on "
        "FROM tasks t JOIN projects p ON t.project_id = p.id "
        "WHERE t.status != 'done' ORDER BY p.name, t.status"
    ).fetchall()
    if not rows:
        return "No open tasks. Board is clear."
    by_project: dict[str, list] = {}
    for name, tid, title, status, claimed_by, depends_on in rows:
        by_project.setdefault(name, []).append((tid, title, status, claimed_by, depends_on))
    icon = {"todo": "○", "in_progress": "◐", "blocked": "⛔"}
    lines = []
    for name, tasks in sorted(by_project.items()):
        lines.append(f"\n📁 {name}")
        for tid, title, status, claimed_by, depends_on in tasks:
            dep = f"  (waits on #{depends_on})" if depends_on else ""
            who = f"  [{claimed_by}]" if claimed_by else ""
            lines.append(f"  {icon.get(status, '?')} #{tid} {title}{dep}{who}")
    return "\n".join(lines)


def _main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_scan = sub.add_parser("scan")
    p_scan.add_argument("roots", nargs="*", default=os.environ.get("PROJECT_ROOTS", "~/projects:~/Documents").split(":"))

    sub.add_parser("list")

    p_task = sub.add_parser("task")
    task_sub = p_task.add_subparsers(dest="task_cmd", required=True)
    p_add = task_sub.add_parser("add")
    p_add.add_argument("project")
    p_add.add_argument("title")
    p_add.add_argument("--depends-on", type=int, default=None)
    p_claim = task_sub.add_parser("claim")
    p_claim.add_argument("task_id", type=int)
    p_claim.add_argument("who")
    p_status = task_sub.add_parser("status")
    p_status.add_argument("task_id", type=int)
    p_status.add_argument("status", choices=STATUSES)
    p_done = task_sub.add_parser("done")
    p_done.add_argument("task_id", type=int)

    sub.add_parser("board")

    args = ap.parse_args()

    if args.cmd == "scan":
        found = scan(args.roots)
        print(f"Registered/updated {len(found)} project(s):")
        for line in found:
            print(f"  {line}")
    elif args.cmd == "list":
        for pid, name, path, touched in list_projects():
            print(f"{pid:30s} {path}   (last touched {touched})")
    elif args.cmd == "task":
        if args.task_cmd == "add":
            tid = task_add(args.project, args.title, args.depends_on)
            print(f"Created task #{tid}")
        elif args.task_cmd == "claim":
            task_set_status(args.task_id, "in_progress", claimed_by=args.who)
            print(f"Task #{args.task_id} claimed by {args.who}")
        elif args.task_cmd == "status":
            task_set_status(args.task_id, args.status)
            print(f"Task #{args.task_id} -> {args.status}")
        elif args.task_cmd == "done":
            task_set_status(args.task_id, "done")
            print(f"Task #{args.task_id} -> done")
    elif args.cmd == "board":
        print(board())


if __name__ == "__main__":
    _main()
