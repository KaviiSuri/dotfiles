---
name: sharpness-diff
description: Measures sharpness/detail loss (softening, blur, focus loss) between two frame-aligned video clips by comparing per-column high-frequency texture energy, using within-frame edge-ratio signals that survive re-encode noise, and prints a single detail-loss number. Use when asking "is the output clip softer/blurrier than the input", "did this render lose texture/fine detail versus the source", to measure or quantify the detail/texture loss between two versions, or to validate a pipeline stage (lipsync, composite, upscale, re-encode) did not degrade sharpness in a face or region. This is the high-frequency/focus axis comparing TWO clips only; use luma-diff-map or region-shift for brightness/color/shading shifts, temporal-flicker for frame-to-frame brightness pops within one clip, jumpy-toggle to eyeball a subtle static difference, and clip-stack for a plain side-by-side panel.
---

# sharpness-diff

Compare fine-detail (texture) between two clips to decide if one is softer.

Texture metric = local high-frequency energy per column:
`texture[x] = mean_over_rows(|I[x+2] - I[x-2]|)` on a grayscale frame.
Higher = more detail; softening lowers it.

## CRITICAL GOTCHA — read before concluding anything

A raw ABSOLUTE texture comparison across two clips is **unreliable**. The clips
differ in content, motion blur, and re-encoding, so a lower mean texture in clip
B does **NOT** by itself prove softening. **Never declare softening from a raw
cross-clip mean alone.**

Prefer **within-frame** signals, which cancel out those confounds:
- **Texture RATIO across a known edge**, compared between clips. Split each
  frame at a column (or use a region containing a sharp edge). If clip B's
  across-edge ratio collapses relative to clip A's, that side really softened.
- **A texture step present in one clip but absent in the other** (e.g. a crisp
  jawline edge that is gone/smeared in the processed clip).

The script prints the raw mean (flagged as weak) AND the robust within-frame
ratio. Base your verdict on the ratio.

## Requirements

`ffmpeg`, `ffprobe`, `python3`, `numpy`. Dimensions are probed via ffprobe —
never hardcode resolution. Both clips must share dimensions (scale first if not).

## Quick start

```bash
S=~/.agents/skills/sharpness-diff/scripts/sharpness_diff.py

# Robust: split each frame at column x=960 (e.g. a face edge) and compare the
# across-edge texture ratio between the two clips.
python3 "$S" source.mp4 processed.mp4 --time 2.0 --frames 5 --split 960

# Sanity control: a clip vs itself must give shift(B/A) ~ 1.000.
python3 "$S" source.mp4 source.mp4 --frames 5 --split 960
```

Output:
```
dims: 1920x1080
[weak] raw mean texture   A=8.796  B=7.047  B/A=0.801
       (cross-clip absolute mean is unreliable; see within-frame ratio)
[robust] across-edge texture ratio (right/left):
         A=1.023  B=1.090  shift(B/A)=1.066
         shift <<1 => right side softened in B; >>1 => softened in A; ~1 => no relative change
```

Interpretation: here `B/A=0.80` on the raw mean looks like softening, but the
within-frame ratio shift is ~1.0 — so the drop is global (content/re-encode),
**not** localized detail loss. A real one-sided softening shows `shift(B/A)`
well below (or above) 1.0.

## Options

- `--time T` start seconds (default 0).
- `--frames N` average N frames from T to reduce motion-blur noise (default 1).
- `--split X` column to split frame into left/right for the within-frame ratio.
- `--region X0 Y0 X1 Y1` restrict all analysis to a box (e.g. just the face).
- `--json` machine-readable output.

## Recommended workflow

1. Pick a moment with a static, high-detail edge (jawline, text, hair).
2. Use `--region` to isolate it and `--split` at the edge column.
3. Average a few frames (`--frames 5`) to suppress per-frame motion blur.
4. Read `shift(B/A)`. Treat the raw mean as a hint only.
