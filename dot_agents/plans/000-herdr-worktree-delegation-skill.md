---
name: 000-herdr-worktree-delegation-skill
description: Design a herdr-native delegation policy and skill that decides when to use plain herdr tabs, when to use Worktrunk-backed worktrees, how to launch child agents, and how to coordinate completion back to the parent agent.
steps:
  - phase: discovery
    steps:
      - "- [ ] step 1: inventory current delegation primitives across herdr, the pi herdr tool, bash, raw wt, and the existing wtab/worktrunk affordances"
      - "- [ ] step 2: define the minimum supported agent families and how current-agent detection should work"
      - "- [ ] step 3: confirm the first delivery shape: skill-first orchestration using existing tools, with helper scripts or extension support only if repeated pain justifies them"
  - phase: policy-design
    steps:
      - "- [ ] step 1: define the delegation decision tree across same-pane, sibling pane, new herdr tab, and new worktree plus tab"
      - "- [ ] step 2: define user override rules such as 'do not create a worktree', 'use the same agent', or 'spawn a specific command'"
      - "- [ ] step 3: define parent-child communication and completion rules, including wait strategy, pane aliases, and optional file handoff"
  - phase: interface-design
    steps:
      - "- [ ] step 1: define the skill invocation contract, including branch, base, label, agent command override, optional initial task, and no-worktree mode"
      - "- [ ] step 2: define child-agent lifecycle states: created, booting, prompted, waiting, done, failed, canceled"
      - "- [ ] step 3: decide which operations should use the herdr tool directly versus raw bash wt or git commands"
  - phase: implementation
    steps:
      - "- [ ] step 1: write the skill instructions that compose herdr plus wt without requiring a helper script for v1"
      - "- [ ] step 2: add startup and readiness logic for supported agents, plus safe fallbacks when readiness cannot be inferred"
      - "- [ ] step 3: identify the smallest justified helper or extension additions if the pure skill flow proves too brittle"
  - phase: validation
    steps:
      - "- [ ] step 1: test from inside herdr with pi as the parent agent and verify both no-worktree and worktree-backed delegation flows"
      - "- [ ] step 2: test at least one non-pi agent family if available, or document unsupported cases clearly"
      - "- [ ] step 3: document when to use herdr delegation versus in-process subagents and when to escalate to an extension"
---

# 000-herdr-worktree-delegation-skill

## Phase 1 — Discovery
- [ ] step 1: inventory current delegation primitives across herdr, the pi herdr tool, bash, raw wt, and the existing wtab/worktrunk affordances
- [ ] step 2: define the minimum supported agent families and how current-agent detection should work
- [ ] step 3: confirm the first delivery shape: skill-first orchestration using existing tools, with helper scripts or extension support only if repeated pain justifies them

## Phase 2 — Policy Design
- [ ] step 1: define the delegation decision tree across same-pane, sibling pane, new herdr tab, and new worktree plus tab
- [ ] step 2: define user override rules such as 'do not create a worktree', 'use the same agent', or 'spawn a specific command'
- [ ] step 3: define parent-child communication and completion rules, including wait strategy, pane aliases, and optional file handoff

## Phase 3 — Interface Design
- [ ] step 1: define the skill invocation contract, including branch, base, label, agent command override, optional initial task, and no-worktree mode
- [ ] step 2: define child-agent lifecycle states: created, booting, prompted, waiting, done, failed, canceled
- [ ] step 3: decide which operations should use the herdr tool directly versus raw bash wt or git commands

## Phase 4 — Implementation
- [ ] step 1: write the skill instructions that compose herdr plus wt without requiring a helper script for v1
- [ ] step 2: add startup and readiness logic for supported agents, plus safe fallbacks when readiness cannot be inferred
- [ ] step 3: identify the smallest justified helper or extension additions if the pure skill flow proves too brittle

## Phase 5 — Validation
- [ ] step 1: test from inside herdr with pi as the parent agent and verify both no-worktree and worktree-backed delegation flows
- [ ] step 2: test at least one non-pi agent family if available, or document unsupported cases clearly
- [ ] step 3: document when to use herdr delegation versus in-process subagents and when to escalate to an extension
