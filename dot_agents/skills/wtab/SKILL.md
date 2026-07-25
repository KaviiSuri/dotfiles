---
name: wtab
description: Spin up (or refresh) a git worktree and open it in a new tmux window with a 3-pane layout. Use when the user wants to start work on a branch in its own worktree + tmux tab, or refresh an existing worktree from main. Triggers on phrases like "wtab", "open a worktree for X", "spin up a tab for branch Y", "refresh the worktree", or after merging a PR when the user wants the next branch's tab created.
---

# wtab

A CLI helper that creates or refreshes a git worktree and opens a tmux window with the user's 3-pane template (full-height left, top-right, bottom-right).

The script is `wtab` (in this skill folder; symlinked to `~/.local/bin/wtab`, which is on `PATH` in both interactive and non-interactive shells).

## When to use this skill

Invoke the `wtab` CLI when the user wants any of:

- A new worktree + tmux window for a branch they're about to work on.
- An existing worktree refreshed against `origin/main` (or another base) AND surfaced in a tmux window.
- A series of windows opened for several branches in parallel (one `wtab` invocation per branch).

If the user describes the *outcome* ("get me a tab for kavii/foo so I can start work") rather than naming the tool, this skill still applies — `wtab` is the right tool for that outcome.

## Usage

```
wtab <branch> [--base <base-branch>]
wtab -h | --help
```

`--base` defaults to `main`. The branch argument should be the full branch name (e.g. `kavii/render-take-tracer`); the tmux window is named after the part after the last `/`.

### Behavior

1. Looks the branch up via `wt list --format json`.
2. **If a worktree exists for the branch:**
   - `git -C <worktree> fetch origin <base>`
   - `git -C <worktree> reset --hard origin/<base>`
3. **Otherwise:** `wt switch --create <branch> --base <base>`.
4. Opens a new tmux window in the **current** session (must be running inside tmux), named after the branch's basename, with the 3-pane template applied. All panes start in the worktree directory; pane 1 (the editor pane) is selected.
5. If a window with that name already exists in the session, it is selected instead of creating a duplicate.

## How to apply

- When the user asks for a tab/window for a branch: run `wtab <branch>` directly via the Bash tool. Do not re-implement the worktree-creation or tmux-splitting logic — call the script.
- When the user has just merged a PR for branch X and wants to start the next slice on branch Y: run `wtab Y`. (You don't need to clean up X's window/worktree as part of `wtab` — that's a separate cleanup step the user usually drives explicitly.)
- When the user wants several branches set up at once: call `wtab` once per branch. The script is idempotent — repeated invocations select the existing window rather than duplicating it.
- If the user is not inside a tmux session, `wtab` exits with an error. In that case, surface the error and ask whether they want to start tmux first; do not try to invent a substitute.

## Requirements

- Must be invoked from inside a tmux session.
- `wt`, `bun`, and `git` must be on `PATH`.

## Source

The script source lives at `wtab` in this skill directory. It is a Bun script using Bun's `$` shell template. Edit it here; the symlink at `~/tools/wtab` follows automatically.
