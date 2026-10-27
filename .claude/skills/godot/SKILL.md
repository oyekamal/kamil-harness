---
name: godot
description: Build games and game assets in Godot 4.7 — new project scaffold, driving the live editor through the godot-ai MCP, headless run/error checks through the godot MCP, Blender→glTF 3D assets, and the verify gate. Use for "make a game", "Godot", "GDScript", "platformer", "add a level/enemy/player", "import this model into Godot", or any .tscn/.gd/project.godot work.
---

# Godot (glue skill)

This skill is wiring, not Godot knowledge. For engine patterns load the **godot-prompter**
plugin skills (56 skills: state machines, physics, tilemaps, shaders, UI…). For art direction
and asset families load **create-game-assets**. For 3D models use the **blender** MCP.

## Expected setup

| Piece | Where |
|---|---|
| Godot 4.7.2 stable (checksum verified) | any install dir, with `godot` on your PATH |
| `godot-ai` MCP (hi-godot/godot-ai 4.2.3) — live editor: scenes, nodes, scripts, signals, materials, animation, particles, screenshots, test runs | user-scope in `~/.claude.json`, `uvx … godot-ai attach` |
| `godot` MCP (Coding-Solo/godot-mcp) — launch editor, run project, capture debug output, headless | user-scope, `npx @coding-solo/godot-mcp`, `GODOT_PATH` set |
| godot-ai editor plugin zip (per project) | from the godot-ai release page |
| Official reference demos (the quality bar) | clone godot-demo-projects, e.g. `~/godot-games/_reference/` |
| Games live in | `~/godot-games/<name>/` (or any parent dir you pass to the scaffold script) |

Telemetry is off: `godot_ai/telemetry_enabled = false` in editor settings + `GODOT_AI_DISABLE_TELEMETRY=1`.

## Workflow

1. **Scaffold:** `bash .claude/skills/godot/scripts/new-project.sh <name>` → project with the godot-ai plugin enabled and imported.
2. **Open the editor on the real display** (godot-ai needs a live editor; headless editor won't serve it):
   `cd <project> && DISPLAY=${DISPLAY:-:0} setsid godot --editor --path . >/tmp/godot-<name>.log 2>&1 < /dev/null & disown`
   Wait until `ss -ltn | grep -E ':8000|:9500'` shows both ports. Only ONE editor can own port 9500 at a time.
3. **Build through `mcp__godot-ai__*`** (scene/node/script/resource tools). Prefer the tools over hand-editing `.tscn`; they validate GDScript on write.
4. **Assets:**
   - 2D: `create-game-assets` brief → generate (asset-studio / kie-ai-imagegen) → normalize → `res://art/…`; pixel art needs Texture filter = Nearest.
   - 3D: model in Blender MCP → `bpy.ops.export_scene.gltf(filepath=…/x.glb, export_format='GLB', export_apply=True)` straight into the project → Godot imports `.glb` natively. Keep 1 unit = 1 m, +Y up (the glTF exporter handles Blender's Z-up).
5. **Verify gate (before claiming done):**
   - `godot --headless --path <project> --quit-after 300 2>&1 | grep -E 'ERROR|WARNING' | grep -vE 'leaked at exit|still in use at exit'` must be empty. `--quit-after` counts frames. A plain `--headless --quit` only loads the project; it does not run the main scene's frames. The two filtered lines come from the forced quit, and the official demos print them too, so they're noise, not bugs.
   - Screenshot the running game (godot-ai screenshot tool, or `mcp__godot__run_project` + debug output) and compare side by side with the matching `_reference` demo.

## Gotchas

- **Never `pkill -f godot…`**: the pattern matches your own shell's command line and kills the Bash tool (exit 144). Find PIDs with `ps -eo pid,comm,args | awk '$2 ~ /Godot/'` and `kill <pid>`.
- The editor-spawned backend self-terminates when idle; if tools vanish, reopen the editor (step 2), don't re-register the MCP.
- New MCP servers only appear in Claude Code sessions started *after* registration.
- Godot 3 syntax drift: `KinematicBody2D`, `yield`, `onready var` without `@` are Godot 3 and WRONG. Use `CharacterBody2D/3D`, `await`, `@onready`, `@export`.
- Upgrading godot-ai: use the dock's **Update** button, never unzip over an existing `addons/godot_ai/`.
