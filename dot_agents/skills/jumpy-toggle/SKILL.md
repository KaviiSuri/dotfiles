---
name: jumpy-toggle
description: Builds an A/B flicker (toggle) video from TWO frame-aligned clips by rapidly alternating between them in time — output frame i shows clip A or clip B at the SAME index, switching every few frames — so a subtle static difference visibly flickers while identical pixels stay still. Use when someone wants to "flip/flicker/toggle rapidly between two versions of a clip", "make an A/B (before-and-after) flicker video of the before and after clips", "alternate between these two renders so I can see what changed", or otherwise SEE the difference between two versions/renders of the same take when a side-by-side or diff is too subtle — faint seam, color shift, mask bleed, 1-pixel artifact. This is the only skill that emits a temporal A/B toggle video; distinct from clip-stack (spatial side-by-side panel, not temporal flicker), temporal-flicker (detects/measures flicker in ONE clip, does not produce a toggle video), and luma-diff-map/region-shift/sharpness-diff (numeric or heatmap analysis, not an eye-driven flicker).
---

# jumpy-toggle

Alternate two **frame-aligned** clips (A,B,A,B...) at ~3-6 Hz. A truly static
difference visibly flickers; anything identical stays rock-still. This is a
temporal A/B, not a side-by-side — output frame `i` shows source A or B at the
SAME index `i` (identical timestamps), switching every few frames.

## When it works vs. when it lies

- Clips **MUST be frame-aligned**: same take, same frame count, same fps, same
  geometry. Frame `i` of A and frame `i` of B must depict the same instant.
  If they are offset by even one frame you will see *motion*, not the artifact.
- Toggle **3-6 Hz** is the sweet spot. Slower reads as a slideshow; faster fuses
  and hides the difference.
- Same resolution + same fps for both inputs (the script probes and enforces
  this; it never assumes 1920x1080).

## Quick start

```bash
python3 scripts/jumpy_toggle.py A.mp4 B.mp4 toggle.mp4 --hz 5
```

Requires `ffmpeg`, `ffprobe`, `python3`, `numpy`. The script:
- probes width/height/fps via ffprobe (aborts on geometry mismatch, warns on fps mismatch),
- computes hold = round(fps / (2*hz)) frames per source and prints the *effective* Hz,
- decodes both to rgb24, emits alternating groups, encodes with libx264 (yuv420p),
- burns a **corner marker so you know which source is live: A = green, B = red**
  (top-left block). Pass `--no-label` to disable.

Flags: `--hz` (default 5), `--crf` (default 16), `--no-label`.

Example output line:
`320x240 @ 25.000fps  hold=2 frames/source  effective toggle=6.25Hz`

## Pure-ffmpeg alternative (no python)

For a quick toggle without the label logic:

```bash
ffmpeg -y -i A.mp4 -i B.mp4 -filter_complex \
  "[0:v][1:v]blend=all_expr='if(lt(mod(N,10),5),A,B)'" -c:v libx264 -pix_fmt yuv420p toggle.mp4
```

`mod(N,10)<5` = 5 frames of A then 5 of B. At 25 fps that is a 10-frame cycle =
2.5 Hz; use `mod(N,8),4` for ~3.1 Hz, `mod(N,6),3` for ~4.2 Hz. Here `A`/`B` are
blend's per-pixel operands (top/bottom input), not labels — this variant draws
no on-screen label, so note which input you passed first.

## Gotchas recap

- Not frame-aligned -> you see motion, not the diff. Verify frame counts match:
  `ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 A.mp4`
- Keep timestamps identical; do not resample or retime either input first.
- If nothing flickers, the two clips may genuinely be pixel-identical — confirm
  with `ffmpeg -i A.mp4 -i B.mp4 -filter_complex psnr -f null -` (inf = identical).
