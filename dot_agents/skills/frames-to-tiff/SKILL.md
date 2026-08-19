---
name: frames-to-tiff
description: Exports single frames from ONE video clip to disk as lossless uncompressed TIFF stills at the timestamps you name, for pixel-exact inspection or as evidence to hand a model/VFX provider. Use when someone asks to export, pull, grab, dump, or save a still/frame(s) or TIFF image from a clip, get lossless or pixel-exact TIFF stills at given times (e.g. 2s and 5s), or produce frames to send a provider as evidence of an artifact (seam, black line, color shift) at a moment; it writes frame image files from a single clip and does NOT compare, diff, stack, flicker, or measure two clips (see clip-stack, jumpy-toggle, luma-diff-map, region-shift, sharpness-diff, temporal-flicker).
---

# frames-to-tiff

Export **lossless** TIFF stills from a clip at exact timestamps. TIFF (uncompressed
`rgb24`) is preferred by post/VFX for pixel inspection because it introduces no
codec-side lossy artifacts, so what you see is what the encoder produced.

## Quick start

Export a single frame at 3.5s:

```
python3 scripts/frames_to_tiff.py --clip take.mp4 --times 3.5 --outdir ./frames
```

Multiple timestamps, cropped to a region (`W:H:X:Y`):

```
python3 scripts/frames_to_tiff.py \
  --clip take.mp4 --times 3.5 12.0 41.25 \
  --crop 640:640:1000:200 --outdir ./frames
```

A frame range, one TIFF per frame from 10.0s to 11.0s:

```
python3 scripts/frames_to_tiff.py --clip take.mp4 --range 10.0 11.0 --outdir ./frames
```

Output files are named `frame_t<seconds>.tiff` (e.g. `frame_t3.500.tiff`); range
mode names them `frame_r<start>_<index>.tiff`.

## What the script does per timestamp T

```
ffmpeg -y -ss T -i CLIP [-vf crop=W:H:X:Y] -frames:v 1 -pix_fmt rgb24 -compression_algo raw OUT_T.tiff
```

- `-ss T` goes **before** `-i` for a fast keyframe seek + decode-to-T.
- `-pix_fmt rgb24` forces an RGB TIFF; `-compression_algo raw` makes it truly
  uncompressed (ffmpeg otherwise defaults to lossless PackBits RLE) — the
  losslessness guarantee, byte-for-byte inspectable.
- The script probes real dimensions with `ffprobe`; nothing is hardcoded.

## Gotchas

- **`-ss` before `-i`** = fast seek (default here). If you need frame-accurate
  seeking on a clip with sparse keyframes, pass `--accurate` to move `-ss` after
  `-i` (slower, decodes from the start).
- **TIFF is lossless.** Do not "optimize" to JPEG/PNG-lossy for evidence — a
  provider inspecting pixels needs the encoder's exact output.
- **Color range (tv vs full):** most video is `tv`/limited range (16–235). The
  script prints the probed `color_range`, `color_space`, and `color_transfer` and
  writes them into a sidecar `<outdir>/frames_meta.json`. Always report the range
  alongside the TIFFs so the provider interprets levels correctly — a limited-range
  clip decoded as full range shifts every pixel value.
- **No colorspace conversion is applied** — pixels come out as decoded. If the
  provider needs a specific working space, tell them the probed tags rather than
  re-tagging here.
- Timestamps are seconds (float ok). Frame counts in range mode use the probed
  `avg_frame_rate`.

## Requirements

`ffmpeg`, `ffprobe`, `python3` (stdlib only; numpy optional and not required).
Verify: `ffmpeg -version && ffprobe -version && python3 --version`.
