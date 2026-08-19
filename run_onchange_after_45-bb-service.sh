#!/usr/bin/env bash

set -euo pipefail

label='com.kaviisuri.bb-app'
domain="gui/$(id -u)"
plist="$HOME/Library/LaunchAgents/$label.plist"

if [[ $(uname -s) != Darwin ]]; then
  echo 'bb service: launchd setup is only supported on macOS; skipping' >&2
  exit 0
fi

if [[ ! -x "$HOME/.local/bin/bb-app" ]]; then
  echo 'bb service: bb-app is not installed; skipping' >&2
  exit 0
fi

mkdir -p "$HOME/.bb/logs" "$HOME/Library/LaunchAgents"

if launchctl print "$domain/$label" >/dev/null 2>&1; then
  echo 'bb service: launch agent is loaded'
  exit 0
fi

# Do not start a competing process when BB was launched manually (including the
# BB session running this apply). The plist will be loaded automatically at the
# next login; if BB is currently stopped, bootstrap it immediately.
if lsof -nP -iTCP:38886 -sTCP:LISTEN >/dev/null 2>&1; then
  echo 'bb service: plist installed; existing BB process is running, so launchd activation is deferred until next login'
  exit 0
fi

launchctl bootstrap "$domain" "$plist"
launchctl enable "$domain/$label"

for _ in {1..100}; do
  if curl -fsS --max-time 1 http://127.0.0.1:38886/ >/dev/null 2>&1; then
    echo 'bb service: BB is running under launchd at http://127.0.0.1:38886'
    exit 0
  fi
  sleep 0.1
done

echo "bb service: launch agent loaded, but BB did not become healthy; inspect $HOME/.bb/logs/launchd.stderr.log" >&2
exit 1
