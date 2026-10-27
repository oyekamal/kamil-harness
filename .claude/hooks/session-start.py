#!/usr/bin/env python3
"""SessionStart hook: hand the agent today's context in one short block. Never blocks the session."""
import datetime, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def tail(path, n):
    try:
        return "\n".join(path.read_text().splitlines()[-n:]).strip()
    except OSError:
        return ""


def main():
    today = datetime.date.today().isoformat()
    parts = [f"Today is {today}. Log meaningful actions to vault/logs/{today}.md as `- HH:MM — what happened`."]
    if s := tail(ROOT / "STANDUP.md", 15):
        parts.append("STANDUP.md (current focus):\n" + s)
    if s := tail(ROOT / "vault/logs" / f"{today}.md", 10):
        parts.append("Earlier today:\n" + s)
    board = subprocess.run([sys.executable, str(ROOT / ".claude/hooks/project_board.py"), "board"],
                           capture_output=True, text=True, timeout=10)
    if board.returncode == 0 and board.stdout.strip() and "no open tasks" not in board.stdout.lower():
        parts.append("Open tasks across projects:\n" + "\n".join(board.stdout.splitlines()[:15]))
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                             "additionalContext": "\n\n".join(parts)}}))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # a hook must never break the session
        pass
