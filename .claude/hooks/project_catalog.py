#!/usr/bin/env python3
"""
project_catalog.py — every project the user has built, to share and reuse.

Cards (one JSON per project, facts only) live in vault/projects/catalog/<slug>.json.
`render` writes two human pages from them:
  vault/projects/CATALOG.md — every project, grouped by kind, newest first
  vault/projects/REUSE.md   — every reusable component across all projects ("we already built X")

Usage:
  python3 .claude/hooks/project_catalog.py render            # cards → CATALOG.md + REUSE.md
  python3 .claude/hooks/project_catalog.py check             # git repos on disk with no card (exit 1 if any)
  python3 .claude/hooks/project_catalog.py validate          # schema-check every card (exit 1 on errors)
Rule: .claude/rules/project-catalog.md — a new project gets a card the day it starts.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CARDS = REPO / "vault/projects/catalog"
CATALOG = REPO / "vault/projects/CATALOG.md"
REUSE = REPO / "vault/projects/REUSE.md"
ROOTS = [Path(p).expanduser() for p in os.environ.get("PROJECT_ROOTS", "~/projects:~/Documents").split(":")]
IGNORE = {"repos", "screenshots", REPO.name}  # ponytail: name-based ignore list; add an "ignore" card field if it grows
KINDS = ["learning-tool", "game", "agent", "ai-tooling", "app", "web", "research", "design-asset",
         "hardware-cad", "infra", "experiment", "other"]
STATUSES = ["live", "shipped", "in-progress", "prototype", "research-only", "shelved", "archived"]
REQUIRED = ("slug", "name", "one_liner", "kind", "status")


def load():
    cards = []
    for f in sorted(CARDS.glob("[!_]*.json")):  # _minor.json etc. are lists, not cards
        try:
            cards.append(json.loads(f.read_text()))
        except ValueError as exc:
            print(f"bad JSON {f.name}: {exc}", file=sys.stderr)
    return cards


def validate(cards):
    errors = []
    for c in cards:
        for k in REQUIRED:
            if not c.get(k):
                errors.append(f"{c.get('slug', '?')}: missing {k}")
        if c.get("kind") not in KINDS:
            errors.append(f"{c.get('slug')}: kind {c.get('kind')!r} not in {KINDS}")
        if c.get("status") not in STATUSES:
            errors.append(f"{c.get('slug')}: status {c.get('status')!r} not in {STATUSES}")
        for r in c.get("reusable") or []:
            if not isinstance(r, dict) or not r.get("what"):
                errors.append(f"{c.get('slug')}: reusable entry without 'what'")
    return errors


def _link(c):
    url = c.get("repo_url") or c.get("live_url")
    return f"[{c['name']}]({url})" if url else c["name"]


def render(cards):
    cards = sorted(cards, key=lambda c: (c.get("last_active") or ""), reverse=True)
    reusable = sum(len(c.get("reusable") or []) for c in cards)
    out = ["# Project Catalog", "",
           f"Everything the user has built: {len(cards)} projects, {reusable} reusable components "
           f"(see [REUSE.md](REUSE.md)). Generated from `vault/projects/catalog/*.json` by "
           "`.claude/hooks/project_catalog.py render`; edit the cards, not this file.", ""]
    by_status = {}
    for c in cards:
        by_status[c["status"]] = by_status.get(c["status"], 0) + 1
    out += ["**By status:** " + " · ".join(f"{s} {by_status[s]}" for s in STATUSES if s in by_status), ""]
    for kind in KINDS:
        group = [c for c in cards if c.get("kind") == kind]
        if not group:
            continue
        out += [f"## {kind.replace('-', ' ').title()} ({len(group)})", "",
                "| Project | What it is | Stack | Status | Last active | Reusable |", "|---|---|---|---|---|---|"]
        for c in group:
            stack = ", ".join((c.get("stack") or [])[:4])
            out.append(f"| {_link(c)} | {c['one_liner']} | {stack} | {c['status']} | "
                       f"{c.get('last_active') or '—'} | {len(c.get('reusable') or [])} |")
        out.append("")
    minor = CARDS / "_minor.json"
    if minor.exists():
        small = json.loads(minor.read_text())
        out += [f"## Small repos ({len(small)})", "",
                "Tutorials, scaffolds and one-off experiments: too small for a card, logged so nothing is lost.", ""]
        out += [f"- [{m['name']}]({m['url']}) — {m.get('note') or ''}" for m in small]
        out.append("")
    out += ["## Lessons worth sharing", ""]
    for c in cards:
        for lesson in (c.get("lessons") or [])[:2]:
            out.append(f"- **{c['name']}:** {lesson}")
    CATALOG.write_text("\n".join(out) + "\n")

    rows = ["# Reuse Index — we already built this", "",
            "Before building something new, search here. Each row is a working piece from a past project.", "",
            "| Component | Reuse it for | From project | Where |", "|---|---|---|---|"]
    for c in sorted(cards, key=lambda c: c["name"].lower()):
        for r in c.get("reusable") or []:
            rows.append(f"| {r['what']} | {r.get('reuse_for') or '—'} | {_link(c)} | `{r.get('where') or '—'}` |")
    REUSE.write_text("\n".join(rows) + "\n")
    return CATALOG, REUSE


def uncarded(cards):
    """Git repos under the scan roots that have no card — the 'log every project' check."""
    known = set()
    for c in cards:
        known.add(c["slug"])
        if c.get("local_path"):
            known.add(Path(c["local_path"]).name.lower())
        known.update(a.lower() for a in c.get("aliases") or [])
    for extra in ("_skip.json", "_minor.json"):  # deliberate skips (with reasons) and small repos are logged too
        f = CARDS / extra
        if f.exists():
            data = json.loads(f.read_text())
            known.update(k.lower() for k in data) if isinstance(data, dict) else \
                known.update(m["name"].lower() for m in data)
    missing = []
    for root in ROOTS:
        for d in sorted(p for p in root.glob("*/") if (p / ".git").exists()):
            name = d.name.lower()
            if name in IGNORE or name in known or name.replace("_", "-") in known:
                continue
            last = subprocess.run(["git", "-C", str(d), "log", "-1", "--format=%ad", "--date=short"],
                                  capture_output=True, text=True).stdout.strip()
            missing.append((str(d), last))
    return missing


def main(argv):
    cmd = argv[0] if argv else "render"
    cards = load()
    if cmd == "validate":
        errs = validate(cards)
        print("\n".join(errs) or f"ok: {len(cards)} cards")
        sys.exit(1 if errs else 0)
    if cmd == "render":
        errs = validate(cards)
        if errs:
            sys.exit("refusing to render, fix cards first:\n" + "\n".join(errs))
        print(*render(cards))
    elif cmd == "check":
        missing = uncarded(cards)
        for path, last in missing:
            print(f"no card: {path} (last commit {last or 'none'})")
        if missing:
            print(f"{len(missing)} project(s) without a card — add vault/projects/catalog/<slug>.json")
        sys.exit(1 if missing else 0)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
