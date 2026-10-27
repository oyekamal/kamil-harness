# Kamil Harness

A Claude Code harness that turns a folder into a personal agent with a name, rules, memory and
180+ skills. It also learns from every session, and it can't quietly rewrite its own rules: a change
only lands when an eval shows nothing got worse.

Needs [Claude Code](https://docs.claude.com/claude-code), Python 3.10+ and git. Linux or macOS (Windows: WSL).

```bash
git clone https://github.com/oyekamal/kamil-harness.git my-agent
cd my-agent
./setup.sh "Nova" "Sam"      # your agent's name, your name
claude                       # start talking
```

That's the whole install. `setup.sh` only edits files inside this folder: it writes the names in,
checks Python and git, and runs the self-tests. It never touches `~/.claude`. Rename any time by
running it again; it renames whatever names it set last time (tracked in `.claude/agent.json`).

### Your first five minutes (real output, fresh clone, Haiku)

```text
$ ./setup.sh "Nova" "Sam"
  named Nova (owner: Sam) in 35 files
Checking the harness
  hooks and tests OK
Done. Start talking to Nova:

$ claude -p "Who are you and who do you work for? Then: which skill would you use for a failing test?"
I'm Nova, Sam's personal agent, built on Claude Code with the Kamil Harness. I work for Sam.

For a failing test, I'd use `diagnosing-bugs` (reproduce, hypothesise, prove), then `debugging` for root cause.

$ claude -p "What am I focused on this week?"
Nothing is recorded for this week yet, so I can't tell you what you're focused on.

- STANDUP.md still has the template placeholders under "This week" and "Waiting on."
- The task board (project_board.py board) is empty: no open tasks in any project.

If you tell me your top 1-3 priorities for the week, I'll write them into STANDUP.md and add
matching tasks to the board.
```

> **Heads-up:** by default the Stop hook commits `vault/` (your agent's logs and notes) after each
> session. Your working tree is never staged. Turn it off with `AGENT_AUTOCOMMIT=0`.

---

## What you get

| | |
|---|---|
| **A router, not a wall of text** | `CLAUDE.md` stays under 150 lines (a hook enforces it). Detail lives in `.claude/rules/`, loaded only when needed. |
| **180+ skills, routed** | `.claude/rules/skills-router.md` maps "what you asked" → "which skill". Debugging, TDD, code review, research, diagrams, video (Remotion, HyperFrames), Blender, Godot, scraping, writing, and more. |
| **40+ specialist agents** | Engineering, design, testing, marketing, sales, finance. The main agent delegates with a brief instead of doing everything itself. |
| **Guardrails** | Hooks block `rm -rf ~`, force-pushing `main`, `git add -A`, and staging `.env`. |
| **Memory you can read** | `vault/` is plain Markdown in git: daily logs, a compiled wiki, a project catalog. The Stop hook commits it, so memory has history. |
| **Learns every session** | `continual_harness.py` reviews each finished session, keeps up to 3 lessons with quoted evidence, and injects only the relevant ones into later prompts. Lessons that hurt get retired automatically. |
| **Evolves only behind a gate** | The `harness-evolve` skill finds drift, proposes one-file changes, and applies a change only if it beats the current harness in a blind, two-split eval. |
| **Honest by rule** | `CAPABILITIES.md`: never claim "done" or "sent" without checking it happened. |

## How it works

```
 you ─► claude ─► CLAUDE.md (router) ─► rule / skill / agent ─► work
            │                                              │
            ├─ SessionStart: today's log, STANDUP.md, open tasks
            ├─ every prompt: relevant lessons from past sessions
            ├─ every tool call: guardrail hooks
            └─ session end: learn lessons ─► vault/ committed to git
                                    │
              weekly: harness-evolve ─► eval gate ─► rule change (or rejected)
```

| Speed | What | Where |
|---|---|---|
| Every session | Lessons: small hints, evidence-gated, reversible | `continual_harness.py list` |
| On request | "reflect": mine one session for durable learnings | `reflect` skill |
| Weekly | Turn proven lessons into rules, behind an eval gate | `harness-evolve` skill |

## Make it yours

| File | What to put there |
|---|---|
| `vault/memory/agent_personality.md` | Voice, how you like answers, what never to automate |
| `STANDUP.md` | This week's focus. Read at every session start. |
| `.claude/rules/skills-router.md` | Add a row when you add a skill |
| `.claude/rules/CAPABILITIES.md` | Known gaps and the honest fallback for each |
| `.claude/agents/`, `.claude/skills/` | Delete what you don't need; it's all plain Markdown |

Useful commands:

```bash
python3 .claude/hooks/continual_harness.py list          # what your agent has learned
python3 .claude/hooks/continual_harness.py retire <id>   # drop a bad lesson
python3 .claude/hooks/project_board.py scan && python3 .claude/hooks/project_board.py board
bash scripts/check.sh                                    # self-test (also runs in CI)
AGENT_AUTOCOMMIT=0 claude                                # skip the vault auto-commit for a session
```

## Requirements

- [Claude Code](https://docs.claude.com/claude-code)
- Python 3.10+ and git. The hooks use only the standard library, so there's no `pip install`.
- Optional: [`uv`](https://docs.astral.sh/uv/) for the free DuckDuckGo search MCP. Some skills need their
  own tools (Blender, Godot, Node, ffmpeg); each SKILL.md says what.
- Optional: `SKILLSMP_API_KEY` in your environment to search [SkillsMP](https://skillsmp.com) when no
  bundled skill fits.
- Optional plugins the router mentions when present: [superpowers](https://github.com/obra/superpowers)
  (`/plugin marketplace add obra/superpowers-marketplace`) for planning and TDD flows. Everything
  works without them; the router marks each such row "optional".
- Skills that need an account or app mostly say so on a `Requires:` line (Gmail/Notion/Canva MCPs, Blender,
  Godot, a browser). Skim a skill's first lines before you rely on it.
- About 20 bundled skills are written in a terse "caveman" English variant on purpose (fewer
  tokens, same meaning). See CREDITS.md.
- First run: Claude Code asks once whether to trust this folder's hooks and its `.mcp.json` server.

## What it writes, and where

| Where | What | Who writes it |
|---|---|---|
| `vault/` (in this repo) | daily logs, wiki, project catalog | the agent, and `stop.py` commits it |
| `.claude/agent.json` | your agent/user names, for renaming | `setup.sh` |
| `~/.agent-harness/continual/` | learned lessons + review log (`AGENT_CH_DIR` overrides) | `continual_harness.py` |
| `~/.agent-harness/harness.db` | the cross-project task board (SQLite) | `project_board.py` |

The learning step sends a trimmed transcript of the finished session (up to 60k characters) to
Claude through your own `claude -p` login, to decide which lessons to keep. Nothing goes anywhere else.

## What it will not do

- Send, post, publish, pay or delete on its own initiative. That's a rule the model follows (rule 7
  in `CLAUDE.md`), not a hook, so it's strong but not absolute. Hooks hard-block the dangerous few:
  `rm -rf ~`, force-push to main, staging everything at once, staging secret files. If you ask it
  to delete something, it will, after listing what goes.
- Phone home. No telemetry. The only network calls are: Claude, through your own login; the
  DuckDuckGo search MCP when the agent searches the web; SkillsMP only if you set `SKILLSMP_API_KEY`;
  and whatever a skill you invoke says it calls on its `Requires:` line.
- Stage your whole working tree. The Stop hook commits `vault/` only.

## Privacy

This repo ships with no personal data: no names, logs, memories, tokens or IDs. Your agent's memory
starts empty in `vault/`. If you push your copy somewhere public, remember that `vault/` will hold
your logs. Make the repo private, or set `AGENT_AUTOCOMMIT=0`.

## Credits and licence

MIT for the harness itself. Bundled third-party skills keep their own licences. See [CREDITS.md](CREDITS.md).
