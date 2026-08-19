# Notes

## How Kavii wants to be taught

- **Evidence or explicitly labelled as unverified.** He asks for mechanisms specifically to
  find the inconsistencies. Flag the soft parts before he has to.
- **Real artifacts over toy examples.** Lessons should use actual prod projects/shots — he has
  DB and GCS access and will re-run the commands.
- **Terse.** Senior engineer. No programming fundamentals, no restating what he just said.
- **He will push back, and is usually right.** Two design calls this session (editor-offset is
  invalid; "our renderer is better than the browser" needed justification) came from him.
- Dislikes premature abstraction and unnecessary churn — proposals must come with blast radius
  (he rejected re-cutting 5,346 clips and asked for the cheap path instead).

## Workspace

- Lives at `~/.agents/teaching/media-timing/` — deliberately NOT in the lip-sync-studio repo
  (bb worktrees are disposable and lessons would pollute PR diffs), and NOT inside
  `~/.agents/skills/teach/` (that's the skill definition; `~/.claude/skills/teach` symlinks to it).

## Open threads for future lessons

- The raw (`-ignore_editlist`) start time: 0.08 synthetic / 0.12 prod — encoder delay, only
  partly characterised.
- `round` vs `floor` on take end frames — his decision to make.
- Should shot boundaries snap to the frame grid at ingest? Would dissolve the whole bug class.
- VFR: `docs/vfr-feasibility.md` on branch `docs/vfr-feasibility` is related reading.
