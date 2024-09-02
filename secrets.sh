#!/bin/bash

# Export variables from keychain
bw unlock --check || { export BW_SESSION="$(bw unlock --raw)"; }
# export GITHUB_TOKEN=$(security find-generic-password -a "$USER" -s "GITHUB_TOKEN" -w)
# export ANTHROPIC_API_KEY=$(security find-generic-password -a "$USER" -s "ANTHROPIC_API_KEY" -w)
export GITHUB_TOKEN=$(bw get item --raw "GITHUB_TOKEN" | jq '.notes' -r)
export ANTHROPIC_API_KEY=$(bw get item --raw "ANTHROPIC_API_KEY" | jq '.notes' -r)
export NPM_TOKEN=$GITHUB_TOKEN
