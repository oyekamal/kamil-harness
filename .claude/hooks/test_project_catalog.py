#!/usr/bin/env python3
"""Tests for project_catalog.py. Run: python3 .claude/hooks/test_project_catalog.py"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import project_catalog as pc  # noqa: E402


def card(**kw):
    c = {"slug": "demo", "name": "Demo", "one_liner": "a demo", "kind": "game", "status": "shipped",
         "stack": ["Godot"], "last_active": "2026-09-01", "repo_url": "https://github.com/x/demo",
         "reusable": [{"what": "capture rig", "where": "tools/cap.py", "reuse_for": "trailers"}],
         "lessons": ["playtest before polishing"]}
    c.update(kw)
    return c


class Catalog(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        pc.CARDS, pc.CATALOG, pc.REUSE = self.tmp / "catalog", self.tmp / "CATALOG.md", self.tmp / "REUSE.md"
        pc.CARDS.mkdir()

    def test_validate_flags_bad_kind_status_and_missing_fields(self):
        errs = pc.validate([card(kind="toy"), card(status="done"), card(one_liner=""), card(reusable=[{"where": "x"}])])
        self.assertEqual(len(errs), 4)
        self.assertEqual(pc.validate([card()]), [])

    def test_render_groups_by_kind_and_indexes_reuse(self):
        pc.render([card(), card(slug="b", name="Bee", kind="agent", reusable=[])])
        cat, reuse = pc.CATALOG.read_text(), pc.REUSE.read_text()
        self.assertIn("## Game (1)", cat)
        self.assertIn("## Agent (1)", cat)
        self.assertIn("[Demo](https://github.com/x/demo)", cat)
        self.assertIn("| capture rig | trailers |", reuse)
        self.assertNotIn("Bee", reuse)

    def test_check_lists_repos_without_cards(self):
        root = self.tmp / "root"
        for name in ("carded", "new-thing", pc.REPO.name):  # the harness repo itself is ignored, whatever its folder is called
            (root / name).mkdir(parents=True)
            subprocess.run(["git", "init", "-q", str(root / name)], check=True)
        pc.ROOTS = [root]
        missing = [Path(p).name for p, _ in pc.uncarded([card(slug="carded")])]
        self.assertEqual(missing, ["new-thing"])  # ignored + carded repos don't count

    def test_aliases_and_local_path_count_as_carded(self):
        root = self.tmp / "root2"
        for name in ("old_name", "Folder"):
            (root / name).mkdir(parents=True)
            subprocess.run(["git", "init", "-q", str(root / name)], check=True)
        pc.ROOTS = [root]
        cards = [card(slug="x", aliases=["old_name"]), card(slug="y", local_path=str(root / "Folder"))]
        self.assertEqual(pc.uncarded(cards), [])

    def test_skip_and_minor_lists_count_as_logged(self):
        root = self.tmp / "root3"
        for name in ("someones-fork", "tiny-tutorial", "real-new"):
            (root / name).mkdir(parents=True)
            subprocess.run(["git", "init", "-q", str(root / name)], check=True)
        pc.ROOTS = [root]
        (pc.CARDS / "_skip.json").write_text(json.dumps({"someones-fork": "no the user commits"}))
        (pc.CARDS / "_minor.json").write_text(json.dumps([{"name": "tiny-tutorial", "url": "u"}]))
        self.assertEqual([Path(p).name for p, _ in pc.uncarded([])], ["real-new"])
        self.assertEqual(len(pc.load()), 0)  # underscore files are never loaded as cards


if __name__ == "__main__":
    unittest.main(verbosity=2)
