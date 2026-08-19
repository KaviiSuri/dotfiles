#!/usr/bin/env python3
"""Detect detail/texture (sharpness) loss between two video clips.

Texture metric: local high-frequency energy per column, computed as
    texture[x] = mean_over_rows( |I[x+2] - I[x-2]| )
on a grayscale frame. Higher = more fine detail; softening lowers it.

WHY WITHIN-FRAME, NOT RAW CROSS-CLIP:
Comparing the raw mean texture of clip A vs clip B is unreliable. The clips
usually differ in content, motion blur, and re-encode, so an absolute mean
gap does NOT prove softening. This tool therefore reports BOTH:
  - the raw cross-clip means (informational only, flagged as weak), and
  - a robust WITHIN-FRAME signal: the texture RATIO across a known edge/split
    inside each frame, compared between clips. A ratio that collapses in one
    clip but not the other is real evidence of softening on that side.

Dimensions are always probed with ffprobe; nothing is hardcoded.
"""
import argparse
import json
import subprocess
import sys

import numpy as np


def probe_dims(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height",
         "-of", "csv=p=0:s=x", path],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    w, h = out.split("x")
    return int(w), int(h)


def load_gray(path, w, h, start, nframes):
    """Return a float32 (h, w) frame: average of nframes starting at `start` sec."""
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", str(start), "-i", path,
         "-frames:v", str(nframes), "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        capture_output=True, check=True,
    ).stdout
    frames = np.frombuffer(raw, dtype=np.uint8)
    got = frames.size // (w * h)
    if got == 0:
        sys.exit(f"ERROR: no frames decoded from {path} at t={start}s")
    frames = frames[: got * w * h].reshape(got, h, w).astype(np.float32)
    return frames.mean(axis=0)


def texture_profile(img):
    """Per-column texture: mean over rows of |I[x+2]-I[x-2]|. Length = width."""
    diff = np.abs(img[:, 4:] - img[:, :-4])          # |I[x+2]-I[x-2]|, valid cols
    prof = np.zeros(img.shape[1], dtype=np.float64)
    prof[2:-2] = diff.mean(axis=0)
    return prof


def region_texture(img, box):
    x0, y0, x1, y1 = box
    return float(texture_profile(img[y0:y1, x0:x1]).mean())


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clip_a")
    ap.add_argument("clip_b")
    ap.add_argument("--time", type=float, default=0.0, help="start seconds (default 0)")
    ap.add_argument("--frames", type=int, default=1, help="frames to average (default 1)")
    ap.add_argument("--split", type=int, default=None,
                    help="column x to split each frame into left/right; "
                         "reports within-frame right/left texture ratio per clip")
    ap.add_argument("--region", nargs=4, type=int, metavar=("X0", "Y0", "X1", "Y1"),
                    default=None, help="restrict analysis to this box")
    ap.add_argument("--json", action="store_true", help="emit JSON only")
    args = ap.parse_args()

    wa, ha = probe_dims(args.clip_a)
    wb, hb = probe_dims(args.clip_b)
    if (wa, ha) != (wb, hb):
        sys.exit(f"ERROR: dimension mismatch {wa}x{ha} vs {wb}x{hb}; "
                 "scale to a common size before comparing.")
    w, h = wa, ha

    a = load_gray(args.clip_a, w, h, args.time, args.frames)
    b = load_gray(args.clip_b, w, h, args.time, args.frames)

    if args.region:
        x0, y0, x1, y1 = args.region
        a, b = a[y0:y1, x0:x1], b[y0:y1, x0:x1]

    mean_a = float(texture_profile(a).mean())
    mean_b = float(texture_profile(b).mean())

    result = {
        "dims": [w, h],
        "raw_mean_texture": {"a": round(mean_a, 4), "b": round(mean_b, 4),
                             "b_over_a": round(mean_b / mean_a, 4) if mean_a else None},
        "raw_mean_note": "WEAK signal: absolute cross-clip means differ due to "
                         "content/motion-blur/re-encode. Do NOT declare softening "
                         "from this alone.",
    }

    if args.split is not None:
        sx = args.split - (args.region[0] if args.region else 0)
        la, ra = a[:, :sx], a[:, sx:]
        lb, rb = b[:, :sx], b[:, sx:]
        ratio_a = texture_profile(ra).mean() / max(texture_profile(la).mean(), 1e-6)
        ratio_b = texture_profile(rb).mean() / max(texture_profile(lb).mean(), 1e-6)
        result["within_frame_ratio"] = {
            "a_right_over_left": round(float(ratio_a), 4),
            "b_right_over_left": round(float(ratio_b), 4),
            "ratio_shift_b_vs_a": round(float(ratio_b / ratio_a), 4) if ratio_a else None,
            "note": "ROBUST signal. If one clip's across-edge ratio collapses "
                    "relative to the other, that side softened. ~1.0 shift = no change.",
        }

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print(f"dims: {w}x{h}")
    print(f"[weak] raw mean texture   A={mean_a:.3f}  B={mean_b:.3f}  "
          f"B/A={mean_b / mean_a:.3f}" if mean_a else "raw mean A=0")
    print("       (cross-clip absolute mean is unreliable; see within-frame ratio)")
    if "within_frame_ratio" in result:
        r = result["within_frame_ratio"]
        print(f"[robust] across-edge texture ratio (right/left):")
        print(f"         A={r['a_right_over_left']}  B={r['b_right_over_left']}  "
              f"shift(B/A)={r['ratio_shift_b_vs_a']}")
        print("         shift <<1 => right side softened in B; >>1 => softened in A; "
              "~1 => no relative change")


if __name__ == "__main__":
    main()
