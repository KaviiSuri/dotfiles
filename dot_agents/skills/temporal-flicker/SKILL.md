---
name: temporal-flicker
description: Scans ONE video clip along its own time axis for brightness flicker by tracking a per-frame mean-luma series and flagging large frame-to-frame luma jumps, reporting WHEN each pop occurs (with optional checks at known segment-boundary timestamps). Use for a single clip that visibly pulses, throbs, flickers, strobes, flashes, or pops in brightness — "this clip seems to pulse in brightness, find the flicker", "detect frame-to-frame brightness pops in this video", "when does it flash", or confirming a suspicious frame is a real scene cut vs a flicker artifact. Single-clip temporal only: NOT a two-clip comparison (luma-diff-map / region-shift measure where/how-much two clips differ), NOT sharpness (sharpness-diff), and NOT an A/B toggle video (jumpy-toggle).
---

# Temporal Flicker Detection

Finds brightness flicker/pops in a video clip. Works by decoding
**downscaled grayscale** frames (fast), computing each frame's mean luma
(0-255), then looking at `abs(diff)` between consecutive frames. A steady clip
has tiny jumps; a flicker pop is a moderate isolated jump; a real scene cut is a
huge jump.

## Quick start

```bash
# Basic scan — reports fps, frame count, and the largest luma jumps
python3 scripts/detect_flicker.py /path/to/clip.mp4

# Check specific segment-boundary blend times (seconds). Exits 1 if a POP
# lands on any boundary; prints JSON with --json.
python3 scripts/detect_flicker.py /path/to/clip.mp4 --boundaries 2.5,4.0 --json
```

Dependencies: `ffmpeg`, `ffprobe`, `python3`, `numpy`. No repo/DB deps.
Dimensions and fps are probed with ffprobe — nothing is hardcoded.

## Interpreting the output (thresholds are on the 0-255 luma scale)

- **smooth** — jump `<= 0.5`: imperceptible, normal.
- **minor** — jump `0.5–2.0`: usually fine.
- **pop** — jump `~2–5`: a visible brightness flicker. This is the artifact
  you're hunting, especially when it lands exactly on a segment boundary.
- **cut** — jump `>= 15`: almost certainly a real hard scene change. A big
  isolated jump NOT at a boundary is normal content, not a bug.

Key distinction: **a huge isolated jump is a scene CUT (expected); a moderate
jump (~2–5) sitting exactly on a known blend/stitch time is a flicker POP
(bug).** Always pass `--boundaries` when you know where segments were joined —
that's how the script tells a pop apart from ordinary content motion.

## How it works (under the hood)

```
ffmpeg -i CLIP -vf scale=192:108 -pix_fmt gray -f rawvideo pipe:1
  -> np.frombuffer(uint8).reshape(nf, 108, 192)
  -> per-frame mean over H,W  = luma series (nf,)
  -> np.abs(np.diff(luma))    = frame-to-frame jumps
  -> report max + top-N jumps; map boundary time -> frame via fps
```

- The 192x108 downscale keeps decode fast while preserving global brightness;
  you're measuring average luma, so spatial detail doesn't matter.
- `jump[i]` is the change arriving **at** frame `i+1`, i.e.
  `|luma[i+1] - luma[i]|`. Boundary time `t` maps to frame `round(t*fps)` and is
  checked against the jump arriving at that frame.

## Options

- `--boundaries T1,T2,...` — comma-separated seconds; each is classified and
  any `pop` is reported under `flicker_pops_at_boundaries`.
- `--top N` — how many largest jumps to list (default 5).
- `--json` — machine-readable output.

Exit code is `1` if a pop was detected at a supplied boundary, else `0` — usable
as a CI/gate check.

## Tuning

If a clip is very dark/bright or heavily compressed, adjust the thresholds
(`SMOOTH_MAX`, `POP_MIN`, `CUT_MIN`) at the top of `scripts/detect_flicker.py`.
The defaults suit normally-exposed footage.
