#!/usr/bin/env bash
# ponytail: one script, three verbs. up|down|run "<brief>"
set -e; cd "$(dirname "$0")"
case "$1" in
  up)
    [ -f .env ] || { cp .env.example .env; sed -i "s|^OD_API_TOKEN=.*|OD_API_TOKEN=$(openssl rand -hex 32)|; s|^OD_CLAUDE_HOME=.*|OD_CLAUDE_HOME=$PWD/claude-home|" .env; }
    grep '^OD_API_TOKEN=' .env | cut -d= -f2 > .token
    # minimal Claude home: readable creds copy (container uid 1001 can't read host 0600), no host hooks
    mkdir -p claude-home/.claude; cp ~/.claude/.credentials.json claude-home/.claude/; chmod 644 claude-home/.claude/.credentials.json
    echo '{}' > claude-home/.claude/settings.json; echo '{"hasCompletedOnboarding":true,"theme":"dark"}' > claude-home/.claude.json
    mkdir -p ~/.opencode/bin
    docker image inspect open-design-local >/dev/null 2>&1 || docker build -t open-design-local -f Dockerfile.local .
    docker compose -f docker-compose.yml -f docker-compose.linux.yml up -d --no-build
    for i in $(seq 1 30); do curl -sf http://127.0.0.1:7456/api/health >/dev/null && break; sleep 2; done
    echo "OpenDesign up: http://127.0.0.1:7456  (login open-design / $(cat .token))";;
  down) docker compose -f docker-compose.yml -f docker-compose.linux.yml down;;
  run) shift; BRIEF="$*" python3 od_run.py;;
  *) echo "usage: od.sh up|down|run \"<brief>\""; exit 1;;
esac
