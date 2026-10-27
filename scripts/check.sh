#!/usr/bin/env bash
# Harness self-check: secrets scan, hook smoke tests, unit tests, tier-1 evals.
#   bash scripts/check.sh          full (CI runs this)
#   bash scripts/check.sh --quick  skip the slower harness-evolve selfcheck
set -uo pipefail
cd "$(dirname "$0")/.."
FAIL=0
ok()  { echo "  ok   $*"; }
bad() { echo "  FAIL $*"; FAIL=1; }

echo "== secrets scan"
# ponytail: high-signal token shapes only; a placeholder like sk-ant-xxxx is too short to match
PAT='(sk-ant-[A-Za-z0-9_-]{20,}|sk_live_[A-Za-z0-9]{16,}|xox[abpr]-[0-9]{6,}-[A-Za-z0-9-]{10,}|ntn_[A-Za-z0-9]{30,}|secret_[A-Za-z0-9]{40,}|gh[pousr]_[A-Za-z0-9]{36}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35})'
hits=$(git ls-files -z 2>/dev/null | xargs -0 grep -IEn "$PAT" -- 2>/dev/null | grep -v '^scripts/check.sh:' | grep -v 'continual_harness.py' | grep -v 'test_continual_harness.py' | grep -v 'harness_evolve.py')
[ -z "$hits" ] && ok "no secret-shaped tokens in tracked files" || { bad "secret-shaped tokens:"; echo "$hits" | cut -c1-160; }
pem=$(git ls-files -z | xargs -0 grep -IA1 -- '-----BEGIN [A-Z ]*PRIVATE KEY-----' 2>/dev/null | grep -E -- '-[A-Za-z0-9+/=]{60,}$')
[ -z "$pem" ] && ok "no private keys" || bad "private key material: $(echo "$pem" | cut -d- -f1 | sort -u)"
for f in .env .slack; do git ls-files --error-unmatch "$f" >/dev/null 2>&1 && bad "$f is tracked"; done

echo "== hook smoke tests"
H=.claude/hooks
echo '{"tool_input":{"command":"git add -A"}}' | python3 $H/block-bad-commands.py 2>/dev/null; [ $? -eq 2 ] && ok "blocks git add -A" || bad "git add -A not blocked"
echo '{"tool_input":{"command":"ls -la"}}'    | python3 $H/block-bad-commands.py 2>/dev/null; [ $? -eq 0 ] && ok "allows ls" || bad "ls blocked"
python3 -c 'import json; print(json.dumps({"tool_input":{"file_path":"CLAUDE.md","content":"x\n"*200}}))' \
  | python3 $H/guard-file-writes.py 2>/dev/null; [ $? -eq 2 ] && ok "blocks CLAUDE.md > 150 lines" || bad "CLAUDE.md cap not enforced"
python3 $H/session-start.py | python3 -c 'import json,sys; json.load(sys.stdin)' && ok "session-start emits JSON" || bad "session-start output"
AGENT_CH_DIR=$(mktemp -d) python3 $H/continual_harness.py list >/dev/null && ok "continual_harness runs" || bad "continual_harness list"
python3 -c "import json; json.load(open('.claude/settings.json')); json.load(open('.mcp.json'))" && ok "settings.json + .mcp.json parse" || bad "settings/.mcp.json"

echo "== unit tests"
python3 $H/test_continual_harness.py >/tmp/agent-check-ch.log 2>&1 && ok "continual_harness (see /tmp/agent-check-ch.log)" || bad "continual_harness tests: /tmp/agent-check-ch.log"
python3 $H/test_project_catalog.py   >/tmp/agent-check-pc.log 2>&1 && ok "project_catalog" || bad "project_catalog tests: /tmp/agent-check-pc.log"
if [ "${1:-}" != "--quick" ]; then
  (cd /tmp && python3 "$OLDPWD/.claude/skills/harness-evolve/scripts/harness_evolve.py" selfcheck >/tmp/agent-check-he.log 2>&1) \
    && ok "harness-evolve selfcheck" || bad "harness-evolve selfcheck: /tmp/agent-check-he.log"
fi

echo "== router integrity"
python3 - <<'PYR' && ok "every routed skill/agent exists (or is marked optional/plugin/built-in)" || bad "router names something that doesn't ship"
import re, pathlib as P, sys
have = {p.name for p in P.Path(".claude/skills").iterdir() if p.is_dir()} | {p.stem for p in P.Path(".claude/agents").glob("*.md")}
bad = 0
for i, l in enumerate(P.Path(".claude/rules/skills-router.md").read_text().splitlines(), 1):
    if not l.startswith("| ") or l.startswith("|---"):
        continue
    names = [n for n in re.findall(r"`([a-z][a-z0-9:_*-]+)`", l.split("|")[2]) if ("-" in n or ":" in n) and not n.startswith("mcp__")]
    missing = [n for n in names if n not in have and not (n.endswith("*") and any(h.startswith(n[:-1]) for h in have))]
    if missing and not re.search(r"optional|plugin|built-in|install", l):
        print(f"    line {i}: {missing}"); bad = 1
sys.exit(bad)
PYR
for d in .claude/skills/*/; do n=$(basename "$d"); f=$(sed -n 's/^name: *//p' "$d/SKILL.md" | head -1 | tr -d "\"'"); [ "$n" = "$f" ] || bad "skill $n has name: $f"; done
ok "skill names match folders (checked)"
leak=$(git ls-files -z .claude CLAUDE.md | xargs -0 grep -IlE 'this machine|DISPLAY=:1|/home/[a-z]|/tmp/claude-[0-9]+/' 2>/dev/null)
[ -z "$leak" ] && ok "no machine-specific notes" || { bad "machine-specific notes in:"; echo "$leak" | sed 's/^/    /'; }

echo "== tier-1 evals"
bash .claude/evals/graders/run-tier1.sh >/tmp/agent-check-t1.log 2>&1 && ok "tier-1" || { bad "tier-1:"; grep FAIL /tmp/agent-check-t1.log; }

[ $FAIL -eq 0 ] && echo "CHECK: PASS" || echo "CHECK: FAIL"
exit $FAIL
