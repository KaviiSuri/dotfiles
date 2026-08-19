#!/usr/bin/env python3
"""Detect brightness flicker/pops across frames in a video clip.

Decodes downscaled grayscale frames via ffmpeg, computes a per-frame mean-luma
series, and reports the largest frame-to-frame jumps. Optionally classifies
jumps at provided boundary timestamps (segment blend points) as pops.

Usage:
    detect_flicker.py CLIP [--boundaries T1,T2,...] [--top N] [--json]

Dimensions are probed with ffprobe; nothing is hardcoded.
"""
import argparse
import json
import subprocess
import sys

import numpy as np

# Luma jumps (0-255 scale): below SMOOTH = imperceptible; at/above POP = a
# visible brightness pop. A real hard scene CUT is a huge isolated jump.
SMOOTH_MAX = 0.5
POP_MIN = 2.0
CUT_MIN = 15.0
DW, DH = 192, 108  # downscale target for fast decode


def probe_fps(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=r_frame_rate",
         "-of", "default=nk=1:nw=1", path],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    num, den = out.split("/") if "/" in out else (out, "1")
    den = float(den) or 1.0
    return float(num) / den


def load_luma(path):
    """Return per-frame mean luma as a float array (0-255)."""
    proc = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path,
         "-vf", f"scale={DW}:{DH}", "-pix_fmt", "gray",
         "-f", "rawvideo", "pipe:1"],
        capture_output=True, check=True,
    )
    buf = np.frombuffer(proc.stdout, dtype=np.uint8)
    frame_px = DW * DH
    nf = buf.size // frame_px
    if nf == 0:
        raise SystemExit("error: decoded 0 frames")
    frames = buf[: nf * frame_px].reshape(nf, DH, DW).astype(np.float32)
    return frames.reshape(nf, -1).mean(axis=1)


def classify(jump):
    if jump >= CUT_MIN:
        return "cut"
    if jump >= POP_MIN:
        return "pop"
    if jump <= SMOOTH_MAX:
        return "smooth"
    return "minor"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clip")
    ap.add_argument("--boundaries", default="",
                    help="comma-separated boundary timestamps in seconds")
    ap.add_argument("--top", type=int, default=5,
                    help="how many largest jumps to report")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    fps = probe_fps(args.clip)
    luma = load_luma(args.clip)
    diffs = np.abs(np.diff(luma))  # jump[i] = |luma[i+1]-luma[i]| at frame i+1

    def t(frame_idx):
        return frame_idx / fps

    order = np.argsort(diffs)[::-1]
    top = []
    for i in order[: args.top]:
        j = float(diffs[i])
        top.append({"frame": int(i + 1), "time": round(t(i + 1), 3),
                    "jump": round(j, 3), "kind": classify(j)})

    boundaries = []
    bad = []
    if args.boundaries.strip():
        for b in args.boundaries.split(","):
            bt = float(b)
            fidx = int(round(bt * fps))
            # jump landing on this boundary frame is diffs[fidx-1]
            k = min(max(fidx - 1, 0), len(diffs) - 1)
            j = float(diffs[k])
            rec = {"boundary_time": bt, "frame": k + 1,
                   "jump": round(j, 3), "kind": classify(j)}
            boundaries.append(rec)
            if rec["kind"] == "pop":
                bad.append(rec)

    result = {
        "fps": round(fps, 4),
        "frames": int(luma.size),
        "max_jump": round(float(diffs.max()), 3) if diffs.size else 0.0,
        "top_jumps": top,
        "boundaries": boundaries,
        "thresholds": {"smooth_max": SMOOTH_MAX, "pop_min": POP_MIN,
                       "cut_min": CUT_MIN},
        "flicker_pops_at_boundaries": bad,
    }

    if args.json:
        print(json.dumps(result, indent=2))
        return 1 if bad else 0

    print(f"fps={result['fps']} frames={result['frames']} "
          f"max_jump={result['max_jump']}")
    print("Top jumps:")
    for r in top:
        print(f"  frame {r['frame']:>5}  t={r['time']:>8.3f}s  "
              f"jump={r['jump']:>7.3f}  [{r['kind']}]")
    if boundaries:
        print("Boundaries:")
        for r in boundaries:
            print(f"  t={r['boundary_time']:>8.3f}s  frame {r['frame']:>5}  "
                  f"jump={r['jump']:>7.3f}  [{r['kind']}]")
    if bad:
        print(f"\nFLICKER: {len(bad)} pop(s) at segment boundary(ies).")
    else:
        print("\nNo boundary pops detected.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
