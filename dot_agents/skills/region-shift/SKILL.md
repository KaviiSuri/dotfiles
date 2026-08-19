---
name: region-shift
description: Reports a single number — the mean-luma (optionally per-channel R/G/B) delta of one named region (face, background, bbox) between an input clip and a processed output clip, frame-aligned, out-minus-in, with a same-clip zero control. This is the numeric measurement skill for a region between TWO clips. Use when the ask is to measure/quantify/report as a number how much a region darkened, brightened, dimmed, or tinted between two versions of a clip — "measure how much the face darkened between input and output", "quantify the luma shift in the background region between two clips", "how many luma levels did the bbox drop", or gating a re-encode/filter/composite/colorspace-tag/model pass on mask bleed, face shadow, seam, or gamma/gain drift by a threshold. NOT for a picture of WHERE the change sits (use luma-diff-map's heatmap), NOT for brightness over time within ONE clip (use temporal-flicker), and NOT for sharpness/blur loss (use sharpness-diff).
---

# region-shift

Measures how much a region got brighter/darker (and optionally redder/greener/bluer)
going from an input clip to an output clip, at a matched frame.

## Why per-region and frame-aligned

- **Per-region, not one global number.** Model/composite shifts are content-dependent:
  a face may darken while the background is untouched. Averaging the whole frame
  makes opposing shifts cancel and hides the artifact. Always pass the rects you care
  about (`face`, `bg`, `bbox`) separately.
- **Frame-align first.** A 1-frame offset between clips produces a fake "shift" from
  motion. The script matches by frame index and scans +-N frames, keeping the output
  frame that minimises full-frame mean|Y_out - Y_in|.
- **Raw Y-plane via yuv444p is tag-independent.** It reads the stored luma bytes
  directly, so a colorspace/range *tag* difference alone shows ~0. If you instead
  compare gray/full-range *decodes* you can be misled into "seeing" a shift that is
  only a tag reinterpretation. This script deliberately reads bytes, not display pixels.
- **Control.** Always run input-vs-itself; every region must read `0.000`. If it
  doesn't, the harness/args are wrong — fix before trusting real numbers.

## Quick start

```bash
S=~/.agents/skills/region-shift/scripts/region_shift.py

# Control: same clip vs itself -> every region must be 0.000, frame_shift 0
python3 "$S" --input in.mp4 --output in.mp4 --frame 120 -r "face:820,300,280,340"

# Real comparison: luma shift in a face rect and a background rect at frame 120
python3 "$S" --input in.mp4 --output out.mp4 --frame 120 \
  -r "face:820,300,280,340" -r "bg:40,40,200,200" --rgb
```

Output (JSON):

```json
{
  "input_frame": 120,
  "aligned_output_frame": 120,
  "frame_shift": 0,
  "regions": {
    "face": { "luma_out_minus_in": -6.412, "rgb_out_minus_in": [-5.9, -6.6, -7.1] },
    "bg":   { "luma_out_minus_in":  0.031, "rgb_out_minus_in": [ 0.0,  0.1,  0.0] }
  }
}
```

Sign convention: **out minus in.** Negative = output is darker/less of that channel.

## Arguments

- `--input`, `--output` — the two clips (any container ffmpeg reads).
- `--frame N` — 0-based frame index in the **input** to measure (default 0).
- `--scan K` — search +-K output frames for best alignment (default 3; use 0 to force
  exact same index).
- `-r name:x,y,w,h` — region rect in pixels, repeatable. `name:full` or omitting `-r`
  uses the whole frame. Coordinates are top-left origin, clamped to frame bounds.
- `--rgb` — also report `[R,G,B]` mean shift (decodes rgb24 alongside Y).

## Notes / gotchas

- Both clips must share width/height (probed via ffprobe, never hardcoded); the script
  errors on mismatch — resample/scale to match resolution first.
- Get region rects from the same coordinate space as the clips (e.g. a detector bbox or
  a composite paste rect). A rect in the wrong space measures the wrong pixels.
- `frame_shift` in the output tells you which output frame was actually compared; a
  non-zero value means the clips were offset — sanity-check that it's expected.
- **Alignment confound:** the scan minimises full-frame mean|delta|, so a large
  *near-uniform* shift (e.g. global gain/gamma) can drown the content-match signal and
  misalign to a wrong frame. If the clips are already frame-locked (same pipeline,
  same take), pass `--scan 0` to force the exact index; only scan when a real temporal
  offset is possible.
- Deterministic and dependency-light: ffmpeg + ffprobe + python3 + numpy only.
