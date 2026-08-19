#!/usr/bin/env bash

set -euo pipefail

export PATH="/opt/homebrew/bin:$HOME/.local/bin:$PATH"

if ! command -v mise >/dev/null 2>&1; then
  echo "mise tools: mise is not installed; skipping" >&2
  exit 0
fi

# Node provides npm for npm-backed tools. BB needs dependency lifecycle scripts,
# so use npm rather than mise's embedded installer for this backend.
mise use --global node@22.22.1 pnpm@10 terraform@1.13 bun uv
mise settings set npm.shell_out=true

# All user-level development applications follow mise's rolling update policy.
# `mup` upgrades this inventory together as part of a system update.
mise-get 'npm:bb-app[npm_args=--ignore-scripts=false]' bb bb
mise-get 'npm:bb-app[npm_args=--ignore-scripts=false]' bb-app bb-app

# Replacing the Herdr client while it owns this shell would create a protocol
# mismatch with the live server. Install and verify the mise copy now, then let
# a later apply outside Herdr replace a legacy direct-install command.
mise use --global github:herdrdev/herdr
mise x github:herdrdev/herdr -- herdr --version >/dev/null
if [[ -e "$HOME/.local/bin/herdr" ]] && ! grep -Fqx '# generated-by: mise-get' "$HOME/.local/bin/herdr" 2>/dev/null; then
  if [[ ${HERDR_ENV:-} == 1 ]]; then
    echo "mise tools: Herdr installed by mise; wrapper migration deferred until apply runs outside Herdr" >&2
  else
    mv "$HOME/.local/bin/herdr" "$HOME/.local/bin/herdr.pre-mise"
    mise-get github:herdrdev/herdr herdr herdr
  fi
else
  mise-get github:herdrdev/herdr herdr herdr
fi

mise-get 'npm:@earendil-works/pi-coding-agent[npm_args=--ignore-scripts=false]' pi pi
mise-get codex
mise-get claude
mise-get opencode

# Cross-platform developer CLIs belong to mise rather than a second global
# package manager. System-integrated software remains in Homebrew.
mise-get gh
mise-get deno
mise-get kubecolor
mise-get railway
mise-get worktrunk wt wt
mise-get 'pipx:tmuxp' tmuxp tmuxp
mise-get 'npm:@bitwarden/cli' bw bw
# Keep the last known Node 22-compatible agent-browser release until the
# package's current Node >=24 requirement matches our pinned runtime.
mise-get 'npm:agent-browser[npm_args=--ignore-scripts=false]@0.26.0' agent-browser agent-browser
mise-get vercel
