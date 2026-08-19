#!/usr/bin/env python3
"""Make a subtle difference between two FRAME-ALIGNED clips pop by rapidly
alternating A,B,A,B in time (a "jumpy toggle" / flicker A/B).

Output frame i shows source A or B at the SAME index i (identical timestamps),
switching every `hold` frames so a static difference flickers while everything
that is truly identical stays rock-still.

Deps: ffmpeg, ffprobe, python3, numpy. No hardcoded resolution.
"""
import argparse
import json
import subprocess
import sys

import numpy as np


def probe(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate",
        "-of", "json", path,
    ])
    s = json.loads(out)["streams"][0]
    w, h = int(s["width"]), int(s["height"])
    num, den = s["r_frame_rate"].split("/")
    fps = float(num) / float(den) if float(den) else float(num)
    return w, h, fps


def frames(path, w, h):
    """Yield rgb24 frames as (h,w,3) uint8 arrays."""
    n = w * h * 3
    p = subprocess.Popen([
        "ffmpeg", "-v", "error", "-i", path,
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
    ], stdout=subprocess.PIPE)
    try:
        while True:
            buf = p.stdout.read(n)
            if len(buf) < n:
                break
            yield np.frombuffer(buf, np.uint8).reshape(h, w, 3).copy()
    finally:
        p.stdout.close()
        p.wait()


def stamp(img, color):
    """Burn a labelled corner block so the viewer can see which source is live."""
    h, w = img.shape[:2]
    b = max(8, h // 18)
    img[0:b, 0:b] = color
    return img


def main():
    ap = argparse.ArgumentParser(description="Alternate two frame-aligned clips (A/B flicker).")
    ap.add_argument("clip_a")
    ap.add_argument("clip_b")
    ap.add_argument("out")
    ap.add_argument("--hz", type=float, default=5.0, help="toggle frequency, 3-6 Hz sweet spot (default 5)")
    ap.add_argument("--crf", type=int, default=16)
    ap.add_argument("--no-label", action="store_true", help="do not burn A/B corner markers")
    args = ap.parse_args()

    wa, ha, fa = probe(args.clip_a)
    wb, hb, fb = probe(args.clip_b)
    if (wa, ha) != (wb, hb):
        sys.exit(f"ERROR: size mismatch A={wa}x{ha} B={wb}x{hb}. Clips must be identical geometry.")
    if abs(fa - fb) > 1e-3:
        print(f"WARN: fps differ A={fa} B={fb}; using A ({fa}). Ensure clips are frame-aligned.", file=sys.stderr)
    w, h, fps = wa, ha, fa

    hold = max(1, round(fps / (2.0 * args.hz)))
    eff_hz = fps / (2.0 * hold)
    print(f"{w}x{h} @ {fps:.3f}fps  hold={hold} frames/source  effective toggle={eff_hz:.2f}Hz", file=sys.stderr)

    GREEN = np.array([0, 220, 0], np.uint8)   # A
    RED = np.array([220, 0, 0], np.uint8)     # B

    enc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", f"{fps}", "-i", "-",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", str(args.crf), args.out,
    ], stdin=subprocess.PIPE)

    ga, gb = frames(args.clip_a, w, h), frames(args.clip_b, w, h)
    i = 0
    for a, b in zip(ga, gb):
        use_a = (i // hold) % 2 == 0
        img = (a if use_a else b)
        if not args.no_label:
            img = stamp(img.copy(), GREEN if use_a else RED)
        enc.stdin.write(img.tobytes())
        i += 1
    enc.stdin.close()
    if enc.wait() != 0:
        sys.exit("ffmpeg encode failed")
    print(f"wrote {args.out}  ({i} frames)  A=green corner  B=red corner", file=sys.stderr)


if __name__ == "__main__":
    main()
