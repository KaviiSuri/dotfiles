#!/bin/bash

unlock() {
    # Export variables from keychain
    NODE_OPTIONS="--no-deprecation" bw unlock --check || { export BW_SESSION="$(NODE_OPTIONS="--no-deprecation" bw unlock --raw)"; }
    # export GITHUB_TOKEN=$(security find-generic-password -a "$USER" -s "GITHUB_TOKEN" -w)
    # export ANTHROPIC_API_KEY=$(security find-generic-password -a "$USER" -s "ANTHROPIC_API_KEY" -w)
    export GITHUB_TOKEN=$(NODE_OPTIONS="--no-deprecation" bw get item --raw "GITHUB_TOKEN" | jq '.notes' -r)
    export ANTHROPIC_API_KEY=$(NODE_OPTIONS="--no-deprecation" bw get item --raw "ANTHROPIC_API_KEY" | jq '.notes' -r)
    export NPM_TOKEN=$GITHUB_TOKEN
}

