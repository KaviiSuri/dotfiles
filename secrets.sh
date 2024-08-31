export GITHUB_TOKEN=$(security find-generic-password -a "$USER" -s "GITHUB_TOKEN" -w)
export NPM_TOKEN=$GITHUB_TOKEN
