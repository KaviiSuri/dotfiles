---
name: herdr-delegate
description: Herdr-native delegation policy for deciding between quick in-process delegation, tab-plus-worktree delegation, and rare pane-only async delegation. Use when the user asks to delegate, split work in parallel, spawn another agent, create a branch-backed background task, or explicitly wants herdr/worktree-based delegation.
---

# herdr-delegate

Use this skill to choose the right delegation mode and carry it out with minimal ceremony.

Requires `HERDR_ENV=1` and `HERDR_PANE_ID` to be set. If not inside herdr, stop and say so.

## Core policy

- **Branch-worthy work** or **user explicitly asks** → **herdr tab + worktree**
- Quick / non-branch-worthy parallel work → **quick in-process delegation**
- Explicit **no-worktree + async/background** → **rare pane-only delegation**
- Panes are for the same git context only. Delegated branch work belongs in a tab-backed worktree.

## Hard invariants

- **tab = worktree** for real delegation. No pane-based delegation for worktree tasks.
- Match existing worktrees and tabs by **exact slug only**.
- Default base branch = **current branch**.
- Default branch name (when unspecified) = **task slug**.
- Default tab label = **branch slug**.
- Default child agent = **same agent family**, fallback to **pi**.
- **Default to Remote Control on launch** for Claude-family children: start them with `claude --remote-control "<slug>"` (short form `claude --rc "<slug>"`) so the delegated thread is attachable from phone/web the moment it starts — no manual connect step, subscription-billed. This applies **only** to `claude` children; `pi` and other agent families do not support the flag — launch those normally. Skip only if the user explicitly asks for no remote.
- Send task **directly** to the child agent.
- Default behavior is **launch and return**. Wait only when explicitly needed.
- Report just the **tab name** on return.

## Reuse rules

- If an exact worktree for the branch slug already exists → **reuse it** and tell the user.
- If an exact tab with the label already exists → **reuse it** and tell the user.
- Otherwise create fresh.

## Cleanup

When delegation is done:

1. Run **`cleanup-delegation-tab <slug>`** to close the tab.
2. Add **`--remove-worktree`** to also remove the git worktree for that branch.
3. Add **`--force`** alongside `--remove-worktree` to force removal even with uncommitted changes. Use `--force` when the delegated work was exploratory, the child agent left stray files, or the user doesn't care about preserving the worktree state. Do not use `--force` if the worktree might contain meaningful uncommitted work the user wants to keep.
4. Only clean up when the user asks or the task is clearly finished.

## Tooling

- Use **`create-delegation-tab <slug>`** to create or reuse a 3-pane delegation tab. The child agent pane is the **top-right pane**. It outputs JSON with `tab_id`, `agent_pane`, `top_right_pane`, `bottom_right_pane`, and `reused`.
- Use **`cleanup-delegation-tab <slug> [--remove-worktree] [--force]`** to close the tab and optionally remove the worktree. `--force` forces worktree removal even with uncommitted changes.
- Both scripts are in this skill directory. They use `herdr` CLI and `jq` / `bun`.
- Use **bash** for `wt`, `git`, and worktree operations.
- Use the **herdr tool** for waiting, reading, and sending tasks to child agents.

## Workflow

### Tab + worktree delegation

1. Decide: task is branch-worthy or user asked.
2. Derive the slug from the task if no branch name given.
3. Run `create-delegation-tab <slug> --cwd <worktree-path>` from this skill directory.
   - If reuse happened, tell the user.
4. If the worktree didn't already exist, create it with `wt switch --create <slug> --base <current-branch>` via bash.
5. Start the child agent in the `agent_pane` from the script output. `agent_pane` is the top-right pane.
   - For a **Claude-family** child, launch it as **`claude --remote-control "<slug>"`** (not plain `claude`) so the thread is auto-attachable from phone/web from the start. For `pi`/other families, launch normally (flag unsupported).
   - Note: Remote Control is local execution + remote interface — the herdr host machine must stay awake/online for phone attach to work. For laptop-independent threads, use cloud sessions/Routines instead.
6. Send the task directly to the child.
7. Return the tab name.

### Cleanup

1. Run `cleanup-delegation-tab <slug> [--remove-worktree] [--force]` to close.
2. Use `--remove-worktree` to also remove the worktree.
3. Use `--force` if the worktree has uncommitted changes and the user doesn't need them preserved.
4. Confirm cleanup to the user.

### Pane-only async delegation

1. Only when user explicitly wants no worktree but still wants background execution.
2. Split a pane in the current tab.
3. Run the task there.
4. Launch and return.