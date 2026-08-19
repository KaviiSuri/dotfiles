# Mission: Media timing in the lip-sync pipeline

## Why

Kavii owns lip-sync-studio, where nearly every serious prod bug this month traced to the same
place: milliseconds and frame indices disagreeing at a boundary. Right now diagnosing those
means handing them to an agent and trusting the answer — and that trust has been misplaced
more than once (two confidently wrong explanations of the same edit-list bug, both killed by
measurement). The goal is to stop being dependent on that: to read the media evidence
directly, judge an RCA on its merits, and make the timing-model calls himself.

## Success looks like

- Given a symptom ("wrong frame at the end of a take"), run the ffprobe/ffmpeg commands that
  isolate it, and reach a proven root cause without an agent.
- Read an agent's RCA and spot the unproven step — the place where it asserts a mechanism it
  measured only by inference.
- Decide the pipeline's timing contracts on the merits: round vs floor on take ends, whether
  shot boundaries snap to the frame grid, what a clip promises its consumers.
- Explain to a teammate why a clip has two clocks, and which one each consumer reads.
- Generalise beyond this pipeline: containers, timestamps, timebases, filtergraphs.

## Constraints

- Learning happens between prod incidents — lessons must be short and self-contained.
- Strong senior-engineer background; skip programming fundamentals, go straight to the media
  specifics.
- Dislikes premature abstraction and hand-waving. Every claim needs evidence or an explicit
  "unverified".
- Real prod artifacts are available (GCS + prod DB + pinned ffmpeg 8.1) and should be used as
  the teaching material wherever possible.

## Out of scope

- Codec internals (H.264 bitstream, motion estimation) beyond what timing requires.
- Colour science — already handled elsewhere in the pipeline.
- Audio DSP. Audio timing is in scope; audio processing is not.
