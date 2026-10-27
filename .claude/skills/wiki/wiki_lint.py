#!/usr/bin/env python3
"""Deterministic wiki lint: broken links, orphans, header fields, stale #growing, index gaps.
Usage: wiki_lint.py [wiki_dir]   (default vault/wiki relative to repo root)"""
import re, sys, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STRUCTURAL = {"Index", "Log", "SCHEMA"}
LINK = re.compile(r"\[\[([^\]|#]+)")
CODE = re.compile(r"```.*?```|`[^`\n]*`|^Tags:[^\n]*", re.S | re.M)  # code = template examples; Tags: = topic nodes


def lint(wiki: Path, today=None):
    today = today or datetime.date.today()
    pages = {p.stem: p.read_text() for p in wiki.glob("*.md")}
    issues, inbound = [], {name: 0 for name in pages}
    index = pages.get("Index", "")
    for name, text in pages.items():
        if name in STRUCTURAL:
            continue
        head = text[:400]
        for field in ("Tags:", "Status:", "Updated:"):
            if field not in head:
                issues.append(("Low", name, f"missing {field}"))
        m = re.search(r"Updated:\s*(\d{4}-\d{2}-\d{2})", head)
        if m and "#growing" in head and (today - datetime.date.fromisoformat(m.group(1))).days > 60:
            issues.append(("Medium", name, "#growing but not updated in 60+ days"))
        if f"[[{name}]]" not in index:
            issues.append(("Low", name, "not listed in Index.md"))
    for name, text in pages.items():
        if name in ("Log", "SCHEMA"):  # Log: append-only ledger, dead links are history
            continue
        for target in {t.strip() for t in LINK.findall(CODE.sub("", text))}:
            leaf = target.split("/")[-1]
            if leaf in pages:
                if leaf != name and name != "Index":
                    inbound[leaf] += 1
            elif "/" in target:  # path link to a raw source
                if not any((ROOT / f"{target}{ext}").exists() for ext in (".md", "")):
                    issues.append(("Low", name, f"broken source link [[{target}]]"))
            else:
                issues.append(("Medium", name, f"broken link [[{target}]]"))
    for name, n in inbound.items():
        if name not in STRUCTURAL and n == 0:
            issues.append(("Medium", name, "orphan: no inbound links from other pages"))
    return issues


def demo():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        w = Path(d)
        (w / "Index.md").write_text("[[concept - a]] [[concept - b]]")
        (w / "concept - a.md").write_text("Tags: [[concept]]\nStatus: #growing\nUpdated: 2020-01-01\n[[concept - b]] [[ghost]] `[[example]]`")
        (w / "concept - b.md").write_text("Tags: [[concept]]\nStatus: #stub\nUpdated: 2026-10-13\n")
        (w / "concept - c.md").write_text("Status: #stub\n")
        got = {(n, msg.split(":")[0].split(" [[")[0]) for _, n, msg in lint(w, datetime.date(2026, 10, 13))}
        assert ("concept - a", "#growing but not updated in 60+ days") in got
        assert ("concept - a", "broken link") in got
        assert not any("example" in m for *_, m in lint(w, datetime.date(2026, 10, 13)))
        assert ("concept - a", "orphan") in got and ("concept - b", "orphan") not in got
        assert ("concept - c", "missing Tags") in got and ("concept - c", "not listed in Index.md") in got
    print("demo ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--demo"]:
        demo(); sys.exit()
    wiki = Path(sys.argv[1]) if sys.argv[1:] else ROOT / "vault/wiki"
    found = sorted(lint(wiki), key=lambda i: ["High", "Medium", "Low"].index(i[0]))
    for i, (sev, name, msg) in enumerate(found, 1):
        print(f"{i}. [{sev}] {name} — {msg}")
    print(f"{len(found)} issue(s)")
