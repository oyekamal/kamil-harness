#!/usr/bin/env bash
# Name your agent and check the machine.   ./setup.sh ["Agent name"] ["Your name"]
# Safe to re-run: it renames the agent/user everywhere it set them before.
set -euo pipefail
cd "$(dirname "$0")"

say()  { printf '\033[1m%s\033[0m\n' "$*"; }
warn() { printf '\033[33m! %s\033[0m\n' "$*"; }
die()  { printf '\033[31mx %s\033[0m\n' "$*" >&2; exit 1; }

command -v python3 >/dev/null || die "python3 not found (need 3.10+)"
python3 -c 'import sys; sys.exit(sys.version_info < (3, 10))' || die "python3 is $(python3 -V 2>&1 | cut -d' ' -f2); need 3.10+"
command -v git >/dev/null || die "git not found"

AGENT="${1:-}"; USER_NAME="${2:-}"
[ -n "$AGENT" ]     || read -rp "What should your agent be called? " AGENT
[ -n "$USER_NAME" ] || read -rp "And what's your name? " USER_NAME

python3 - "$AGENT" "$USER_NAME" <<'PY'
import json, re, sys
from pathlib import Path

agent, user = (s.strip() for s in sys.argv[1:3])
for label, v in (("Agent name", agent), ("Your name", user)):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 ._'-]{0,39}", v):
        sys.exit(f"x {label} {v!r}: use 1-40 letters, digits, spaces, . _ ' -")

state_file = Path(".claude/agent.json")
skip = {"setup.sh", "README.md", "scripts/check.sh", ".claude/agent.json"}

# Placeholders are always filled (a `git pull` can bring new ones in). On a re-run, the names set
# last time are also swapped, but only in the files setup touched before.
st = json.loads(state_file.read_text()) if state_file.exists() else {"files": []}
swaps = [("{{AGENT_NAME}}", agent), ("{{USER_NAME}}", user)]
if "agent_name" in st:
    swaps += [(st["agent_name"], agent), (st["user_name"], user)]
files = {Path(f) for f in st["files"] if Path(f).exists()}
for p in Path(".").rglob("*"):
    if not p.is_file() or ".git" in p.parts or str(p) in skip:
        continue
    try:
        text = p.read_text()
    except (UnicodeDecodeError, OSError):
        continue
    if "{{AGENT_NAME}}" in text or "{{USER_NAME}}" in text:
        files.add(p)

changed = 0
for p in files:
    text = p.read_text()
    new = text
    for old, repl in swaps:
        if old == repl or (not old.startswith("{{") and str(p) not in st["files"]):
            continue  # old names are only swapped in files setup wrote them into
        pat = re.escape(old) if old.startswith("{{") else rf"(?<![\w-]){re.escape(old)}(?![\w-])"
        new = re.sub(pat, lambda _m: repl, new)
    if new != text:
        p.write_text(new)
        changed += 1

st.update(agent_name=agent, user_name=user, files=sorted({str(p) for p in files}))
state_file.write_text(json.dumps(st, indent=2) + "\n")
print(f"  named {agent} (owner: {user}) in {changed} files")
PY

mkdir -p vault/logs
say "Checking the harness"
LOG=$(mktemp)
if bash scripts/check.sh --quick >"$LOG" 2>&1; then
  echo "  hooks and tests OK"
else
  warn "self-check failed — see $LOG"
fi
command -v claude >/dev/null || warn "Claude Code CLI not found: https://docs.claude.com/claude-code"
command -v uvx    >/dev/null || warn "uvx not found: the free DuckDuckGo search MCP needs it (https://docs.astral.sh/uv/)"

NAME=$(python3 -c 'import json; print(json.load(open(".claude/agent.json"))["agent_name"])')
say "Done. Start talking to $NAME:"
cat <<EOF
  claude                      # in this folder
  > who are you?              # $NAME reads CLAUDE.md + vault/memory/agent_personality.md

Make it yours:
  vault/memory/agent_personality.md   voice + how you like to work
  STANDUP.md                          what you're focused on this week
  ./setup.sh "New Name" "You"         rename any time
EOF
