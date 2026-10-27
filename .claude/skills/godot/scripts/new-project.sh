#!/usr/bin/env bash
# Scaffold a Godot 4.7 project with the godot-ai editor plugin enabled, then import it.
# Usage: new-project.sh <name> [parent_dir]   (default parent: ~/godot-games)
set -euo pipefail
NAME=${1:?usage: new-project.sh <name> [parent_dir]}
P="${2:-$HOME/godot-games}/$NAME"
ZIP="$HOME/Applications/godot-4.7.2/godot-ai-v4.2.3-plugin.zip"
[ -e "$P/project.godot" ] && { echo "exists: $P" >&2; exit 1; }
mkdir -p "$P" && cd "$P"
unzip -q -o "$ZIP"
cat > project.godot <<EOF
config_version=5

[application]
config/name="$NAME"
config/features=PackedStringArray("4.7")

[editor_plugins]
enabled=PackedStringArray("res://addons/godot_ai/plugin.cfg")
EOF
printf '.godot/\n*.import.tmp\n' > .gitignore
timeout 180 godot --headless --editor --quit --path . >/dev/null 2>&1 || true
echo "$P"
