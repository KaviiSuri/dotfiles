---
name: luma-diff-map
description: Renders a spatial heatmap image showing WHERE two frame-aligned video clips differ in luma/brightness, using a low-pass (box-blurred) signed difference that surfaces broad brightness/shading shifts as colored regions while hiding re-encode noise and high-frequency motion. Use when you want to SEE the location of a brightness/shading change as a picture or heatmap between two clips — "show me where the brightness changed between these two clips as a heatmap", "make a low-pass difference map of input vs output", "luma diff map", "brightness heatmap", "where did it get darker", or locating a face shadow, mask bleed, gamma/gain drift, seam, or colorspace-tag shift where a raw pixel diff is too noisy; this is the only skill that outputs a WHERE-is-it brightness heatmap picture, unlike region-shift (one per-region delta number, no image), temporal-flicker (per-frame luma over time in ONE clip), sharpness-diff (detail/blur loss, not brightness), clip-stack (side-by-side panel, not a diff), and jumpy-toggle (A/B flicker video, not a static map).
---

# Luma diff map

Extract the Y (luma) plane of one frame from each of two frame-aligned
clips, compute a **box-blurred signed difference**, and render maps that
show broad luma shifts. The low-pass blur strips re-encode noise and
high-freq motion (moving mouth, hair) so only genuine broad shifts remain.

## Quick start

```bash
python3 scripts/luma_diff_map.py IN.mp4 OUT.mp4 -t 3.5 -o /tmp/diff
# writes /tmp/diff/diff_gray.png, diff_hot.png, panel.png
# prints e.g. "peak |low-pass diff| = 12.35 luma levels"
```

- `-t SECONDS` timestamp to sample; the SAME frame is taken from both clips.
- `-o DIR` output directory (created if missing).
- `-k N` box-blur half-width (default 25); larger = lower frequency.
- `-a N` amplification (default 7); raise if the map looks flat gray.
- `--min-luma N` mask out input pixels darker than N (default 16).

Read the outputs:
- **diff_gray.png** — signed: mid-gray 128 = no change, brighter = output
  is brighter, darker = output is darker. Best for reading direction.
- **diff_hot.png** — magnitude on a black→red→yellow→white ramp. Best for
  spotting *where* the strongest change is.
- **panel.png** — `[input | output | hot diffmap]` side by side.
- The printed peak tells you the largest broad shift in luma levels
  (0–255). A few levels is a real, visible shift.

## How it works

1. `ffprobe` reads each clip's W×H (never hardcoded).
2. Each frame is decoded to raw `yuv444p`; the **first W*H bytes are the Y
   plane**, taken directly.
3. `diff = outY - inY`, then a box blur (integral image) low-passes it.
4. Signed diff → gray (`128 + d*amp`); magnitude → hot colormap; both
   masked to the visible region (`inY > min-luma`).

## Gotchas

- **Use the raw `yuv444p` Y plane, NOT `-pix_fmt gray`.** `gray` applies a
  colorspace-matrix conversion that varies with the clip's colorspace
  TAGS, injecting fake differences. Slicing the Y plane out of yuv444p is
  tag/colorspace-independent — the whole point when chasing a shading or
  colorspace-tag artifact.
- **Clips must be frame-aligned.** Same fps and start; `-t` must land on
  the same frame in both. Misalignment shows up as motion, not a shift.
- **Amplify.** Real broad shifts are often only a few luma levels; without
  `-a` (~6–8) the map looks blank. Raise `-a` if flat, lower if clipped.
- **Low-pass is the feature, not a bug.** It deliberately removes
  re-encode noise and the moving mouth so a broad face-shadow / gamma
  shift survives. Shrink `-k` only to localize a sharp seam.
- Clips must share dimensions; the script exits if W×H differ.

Deterministic logic lives in `scripts/luma_diff_map.py` (pure ffmpeg +
python3 + numpy; no repo/DB deps).
