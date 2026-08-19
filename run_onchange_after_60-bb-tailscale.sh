#!/usr/bin/env bash

set -euo pipefail

export PATH="/opt/homebrew/bin:$HOME/.local/bin:$PATH"

if ! command -v tailscale >/dev/null 2>&1; then
  echo "bb tailscale: tailscale is not installed; skipping" >&2
  exit 0
fi
if ! command -v bb-app >/dev/null 2>&1; then
  echo "bb tailscale: bb-app is not installed; skipping" >&2
  exit 0
fi

status_json=$(tailscale status --json)
if [[ $(jq -r '.BackendState' <<<"$status_json") != Running ]]; then
  echo "bb tailscale: Tailscale is not running or authenticated; skipping" >&2
  exit 0
fi

dns_name=$(jq -r '.Self.DNSName // empty' <<<"$status_json")
if [[ -z $dns_name ]]; then
  echo "bb tailscale: this machine has no Tailscale DNS name" >&2
  exit 1
fi
dns_name=${dns_name%.}
app_url="https://$dns_name"

# Tailscale persists background Serve configuration. Reapplying the declaration
# makes the desired route explicit and repairs drift without exposing BB's
# unauthenticated API beyond the tailnet.
tailscale serve --bg --https=443 http://127.0.0.1:38886
bb-app config set BB_APP_URL "$app_url"

echo "bb tailscale: serving BB at $app_url"
