---
name: clip-stack
description: Spatially composes 2+ local video clips or still frames into ONE side-by-side (hstack), stacked (vstack), or grid comparison panel, separated by divider strips and downscaled to a readable width, output as a single combined PNG (frames) or MP4 (video). Use when someone asks to put two or more clips/frames side by side, next to each other, stack or tile them, or build an input-vs-output / before-after / A-vs-B comparison panel, grid, or montage image from clips or frames — the deliverable is one combined picture or video that lays all the sources out together in space. Not for rapidly alternating between two clips in time (jumpy-toggle), not for a diff/brightness heatmap (luma-diff-map), not for a numeric luma/color/sharpness measurement (region-shift, sharpness-diff), not for exporting a single still from one clip (frames-to-tiff), and not for scanning one clip for flicker (temporal-flicker).
---

# clip-stack

Build one comparison image or video from 2+ local clips/frames laid out horizontally
(`hstack`) or vertically (`vstack`), with a white divider between panels and the combo
downscaled to ~1900px wide so it is readable. Two helper scripts do all the work; they
probe every input with `ffprobe` and never assume a resolution.

Requires: `ffmpeg`, `ffprobe`, `python3`, `numpy`. All paths are local files.

## Frame mode — one still per input at time T -> a PNG

Extracts one frame from each input at timestamp T, resizes every panel to the first
input's size, concatenates with a 10px white divider, and scales the result.

```bash
python3 scripts/frame_stack.py -t 3.5 -o compare.png input.mp4 output.mp4 diff.mp4
```

- `-t` timestamp (seconds `3.5` or `HH:MM:SS.mmm`); default `0`. Same T for all inputs.
- `--axis h` (side-by-side, default) or `v` (stacked).
- `--width 1900` final combo width; `0` disables downscaling.
- Inputs may be video files or still images. 2+ inputs required.

## Video mode — stack N clips -> an MP4

Scales each clip to a common height (`h`) or width (`v`), inserts a white divider,
stacks, downscales the combo, and clamps to the shortest input.

```bash
python3 scripts/video_stack.py -o compare.mp4 input.mp4 output.mp4
python3 scripts/video_stack.py --axis v --labels "in|out|diff" -o grid.mp4 a.mp4 b.mp4 c.mp4
```

- `--axis h` (default) / `v`; `--width 1900` (`0` = none).
- `--labels "in|out"` optional pipe-separated per-panel captions (drawn top-left).
- Output is always the length of the **shortest** input.

## What the scripts encode (so you don't have to)

- Panels are normalised to a common cross-axis size first — `hstack` needs equal
  heights, `vstack` needs equal widths, or ffmpeg errors out.
- A 10px white divider strip is always inserted between panels.
- The final combo is downscaled to ~1900px wide (`--width`) so it fits on screen.
- Dimensions/fps are probed per input; nothing is hardcoded (no 1920x1080 assumptions).
- Video mode uses `hstack/vstack ...:shortest=1` plus a `color` divider source; the
  `shortest=1` is essential — without it the infinite divider source runs forever.

## Gotchas

- `--labels` uses ffmpeg's `drawtext`, which some ffmpeg builds omit (`No such filter:
  'drawtext'`). If labels error, drop `--labels` — the stack still works. Check with
  `ffmpeg -hide_banner -filters | grep drawtext`.
- For a raw pixel diff panel, make it yourself first (e.g.
  `ffmpeg -i a.mp4 -i b.mp4 -filter_complex blend=all_mode=difference diff.mp4`) then
  pass it as a third input.
- Mismatched aspect ratios are stretched to the common cross-axis size; that is
  expected for a comparison. Crop beforehand if you need exact framing.

## Manual one-liners (if you skip the scripts)

Frame: `ffmpeg -y -ss T -i IN -frames:v 1 -pix_fmt rgb24 -f rawvideo pipe:1` -> numpy
`(H,W,3)` -> `np.concatenate(axis=1)` with `np.full((H,10,3),255,uint8)` dividers ->
`ffmpeg -f rawvideo -pix_fmt rgb24 -s WxH -i pipe:0 -vf scale=1900:-1 out.png`.

Video: `ffmpeg -i A -i B -filter_complex "hstack=inputs=2:shortest=1" -shortest out.mp4`
(scale inputs to equal height first; `vstack` for vertical).
