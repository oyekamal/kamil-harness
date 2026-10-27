#!/bin/bash
# Tier-1 deterministic eval grader. Exit 0 = pass, 1 = fail. No LLM, $0.
cd "$(dirname "$0")/../../.." || exit 1
FAIL=0

echo "== Tier-1: every eval task's route file exists =="
for y in .claude/evals/tasks/*.yaml; do
  route=$(sed -n 's/^ *route: *"\{0,1\}\([^"]*\)"\{0,1\} *$/\1/p' "$y" | head -1)
  if [ -n "$route" ] && [ -e "$route" ]; then echo "  OK $route"; else echo "  FAIL missing route: '$route' ($y)"; FAIL=1; fi
done

echo "== Tier-1: frontmatter on rules/standards =="
for f in .claude/rules/*.md .claude/standards/*.md; do
  if head -1 "$f" | grep -q '^---'; then echo "  OK fm $f"; else echo "  FAIL no frontmatter: $f"; FAIL=1; fi
done

echo "== Tier-1: CLAUDE.md <=150 lines =="
L=$(wc -l < CLAUDE.md)
if [ "$L" -le 150 ]; then echo "  OK CLAUDE.md $L lines"; else echo "  FAIL CLAUDE.md $L > 150"; FAIL=1; fi

echo "== Tier-1: rules <=300 lines =="
for f in .claude/rules/*.md; do
  L=$(wc -l < "$f"); if [ "$L" -le 300 ]; then echo "  OK $f ($L)"; else echo "  FAIL $f $L > 300"; FAIL=1; fi
done

echo "== Tier-1: every skill has a SKILL.md with a description =="
for d in .claude/skills/*/; do
  s="$d/SKILL.md"
  if [ -f "$s" ] && grep -q '^description:' "$s"; then :; else echo "  FAIL $d"; FAIL=1; fi
done
echo "  checked $(ls -d .claude/skills/*/ | wc -l) skills"

echo "== Tier-1: freshness (info only; re-verify rules older than 90 days) =="
python3 - <<'PY'
import datetime, glob, re
for f in sorted(glob.glob(".claude/rules/*.md")):
    m = re.search(r"last_verified:\s*(\d{4}-\d{2}-\d{2})", open(f).read())
    age = (datetime.date.today() - datetime.date.fromisoformat(m.group(1))).days if m else None
    print(f"  {'STALE' if age is None or age > 90 else 'OK'} {f} ({age}d)")
PY

if [ "$FAIL" -eq 0 ]; then echo "TIER-1: PASS"; else echo "TIER-1: FAIL"; fi
exit $FAIL
