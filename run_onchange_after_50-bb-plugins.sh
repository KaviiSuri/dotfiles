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
  shift 2
  current_source=$(jq -r --arg id "$id" '.plugins[] | select(.id == $id) | .source' <<<"$plugins_json")

  if [[ -z $current_source ]]; then
    echo "bb plugins: installing $id from $source"
    bb plugin install "$source" "$@" --yes
  elif [[ $current_source != "$source" ]]; then
    echo "bb plugins: $id already uses $current_source; preserving its data and not replacing it with $source" >&2
  fi

  bb plugin enable "$id" >/dev/null
}

# Installed but deliberately off. Listed rather than omitted so the intent is
# explicit, and disabled without installing so a fresh machine does not pull
# down plugins only to switch them off.
disable_if_present() {
  local id=$1
  if jq -e --arg id "$id" '.plugins[] | select(.id == $id)' <<<"$plugins_json" >/dev/null; then
    bb plugin disable "$id" >/dev/null
  fi
}

# These repositories are public, so plain https clones anonymously on any machine.
ensure_plugin notifications 'git:https://github.com/KaviiSuri/bb-plugin-notifications.git@main'
ensure_plugin tasks-kv 'git:https://github.com/KaviiSuri/bb-plugin-tasks.git@main'
ensure_plugin worktree-setup 'git:https://github.com/KaviiSuri/bb-plugin-worktree-setup.git@main'
ensure_plugin plannotator 'git:https://github.com/patleeman/bb-plugins.git@main' \
  --subdirectory packages/bb-plugin-plannotator

# Community plugins, pinned to a compatible range rather than a moving branch.
ensure_plugin attention 'npm:bb-plugin-attention@^0.1.0'
ensure_plugin context-meter 'git:https://github.com/Hazihell/bb-plugin-context-meter.git@semver:^0.1.0'
ensure_plugin web-push-notify 'git:https://github.com/MayankBansal12/bb-plugin-web-push-notify.git@semver:^0.2.0'

for id in ask-user-question automations connect custom-instructions github inline-vis secrets side-chat t3sidebar workflows; do
  bb plugin enable "$id" >/dev/null
done

# The custom tasks-kv plugin replaces BB's bundled Tasks plugin.
plugins_json=$(bb plugin list --json)
for id in tasks provider-retry pets usage; do
  disable_if_present "$id"
done

echo "bb plugins: desired plugin set is enabled"
