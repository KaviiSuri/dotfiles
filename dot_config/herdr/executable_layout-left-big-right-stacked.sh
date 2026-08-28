#!/usr/bin/env bash
set -euo pipefail

pane_id="${HERDR_ACTIVE_PANE_ID:-}"

if [[ -z "$pane_id" ]]; then
  pane_id="$(herdr pane list | python3 -c 'import json,sys; data=json.load(sys.stdin); panes=data.get("result", {}).get("panes", []); focused=[p for p in panes if p.get("focused")]; print(focused[0]["pane_id"] if focused else "")')"
fi

if [[ -z "$pane_id" ]]; then
  echo "Could not determine focused Herdr pane" >&2
  exit 1
fi

right_pane="$(herdr pane split "$pane_id" --direction right --no-focus | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["pane"]["pane_id"])')"
bottom_right_pane="$(herdr pane split "$right_pane" --direction down --no-focus | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["pane"]["pane_id"])')"

printf 'Created layout: left=%s right-top=%s right-bottom=%s\n' "$pane_id" "$right_pane" "$bottom_right_pane"
