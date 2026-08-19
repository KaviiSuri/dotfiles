#!/usr/bin/env bash

set -euo pipefail

export PATH="/opt/homebrew/bin:$HOME/.local/bin:$PATH"

if ! command -v bb >/dev/null 2>&1; then
  echo "bb plugins: bb is not installed; skipping" >&2
  exit 0
fi

for _ in {1..30}; do
  if bb plugin list --json >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

plugins_json=$(bb plugin list --json)

ensure_plugin() {
  local id=$1 source=$2 current_source
  current_source=$(jq -r --arg id "$id" '.plugins[] | select(.id == $id) | .source' <<<"$plugins_json")

  if [[ -z $current_source ]]; then
    echo "bb plugins: installing $id from $source"
    bb plugin install "$source" --yes
  elif [[ $current_source != "$source" ]]; then
    echo "bb plugins: $id already uses $current_source; preserving its data and not replacing it with $source" >&2
  fi

  bb plugin enable "$id" >/dev/null
}

ensure_plugin notifications 'git:https://github-personal/KaviiSuri/bb-plugin-notifications.git@main'
ensure_plugin tasks-kv 'git:https://github-personal/KaviiSuri/bb-plugin-tasks.git@main'
ensure_plugin worktree-setup 'git:https://github.com/KaviiSuri/bb-plugin-worktree-setup.git@main'

for id in ask-user-question automations connect custom-instructions inline-vis secrets side-chat t3sidebar workflows; do
  bb plugin enable "$id" >/dev/null
done

# The custom tasks-kv plugin replaces BB's bundled Tasks plugin.
if jq -e '.plugins[] | select(.id == "tasks")' <<<"$plugins_json" >/dev/null; then
  bb plugin disable tasks >/dev/null
fi

echo "bb plugins: desired plugin set is enabled"
