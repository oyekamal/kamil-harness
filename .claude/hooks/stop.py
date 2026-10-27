#!/usr/bin/env python3
"""Stop hook: commit vault/ (logs, wiki, catalog) so the agent's memory has git history.
Stages vault/ only, never `git add -A`. Opt out with AGENT_AUTOCOMMIT=0."""
import datetime, os, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, timeout=20)


def main():
    if os.environ.get("AGENT_AUTOCOMMIT") == "0" or git("rev-parse").returncode != 0:
        return
    if not git("status", "--porcelain", "--", "vault").stdout.strip():
        return
    git("add", "--", "vault")
    git("commit", "-q", "-m", f"log: session {datetime.date.today().isoformat()}", "--", "vault")


if __name__ == "__main__":
    try:
        main()
    except Exception:  # a hook must never break the session
        pass
