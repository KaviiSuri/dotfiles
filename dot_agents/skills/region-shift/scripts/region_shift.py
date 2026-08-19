#!/usr/bin/env python3
"""Quantify per-region mean luma (and optional R/G/B) shift between two clips.

Pure ffmpeg + ffprobe + numpy. No repo/DB deps. Dimensions probed, never hardcoded.

Method:
  - Decode ONE input frame at index N, and output frames N-scan..N+scan.
  - Y plane extracted via yuv444p (first W*H bytes) => tag-independent raw luma.
  - Frame-align: pick the output frame d in [-scan,+scan] minimising full-frame
    mean|Yout-Yin|, then report per-region (out - in) at that alignment.
  - Report PER REGION (shifts are content-dependent; a whole-frame average cancels).

Region syntax: name:x,y,w,h   (pixels). Use name:full or omit -r for whole frame.
"""
import argparse, json, subprocess, sys
import numpy as np


def probe_dims(clip):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", clip],
        capture_output=True, text=True, check=True).stdout.strip()
    w, h = out.split("x")
    return int(w), int(h)


def read_frames(clip, start, count, w, h, pix):
    """Return numpy array (count, H, W[, 3]) for the given pixel format."""
    bpp = 3  # both yuv444p and rgb24 emit 3 bytes/pixel
    vf = f"select='between(n\\,{start}\\,{start + count - 1})'"
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", clip, "-vf", vf, "-vsync", "0",
         "-pix_fmt", pix, "-f", "rawvideo", "-"],
        capture_output=True, check=True).stdout
    fsize = w * h * bpp
    n = len(raw) // fsize
    if n == 0:
        sys.exit(f"error: no frames decoded from {clip} at index {start}")
    buf = np.frombuffer(raw[: n * fsize], dtype=np.uint8)
    if pix == "yuv444p":
        # planar: Y plane is first W*H bytes of each frame
        buf = buf.reshape(n, bpp, h, w)
        return buf[:, 0, :, :].astype(np.float64)  # Y only
    else:  # rgb24 interleaved
        return buf.reshape(n, h, w, 3).astype(np.float64)


def region_mean(frame, rect, w, h):
    x, y, rw, rh = rect
    if rect == (0, 0, 0, 0):
        x, y, rw, rh = 0, 0, w, h
    x2, y2 = min(x + rw, w), min(y + rh, h)
    sub = frame[y:y2, x:x2] if frame.ndim == 2 else frame[y:y2, x:x2, :]
    axes = (0, 1)
    return sub.mean(axis=axes)


def parse_region(s):
    if ":" in s:
        name, spec = s.split(":", 1)
    else:
        name, spec = s, "full"
    if spec == "full":
        return name, (0, 0, 0, 0)
    x, y, rw, rh = (int(v) for v in spec.split(","))
    return name, (x, y, rw, rh)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--frame", type=int, default=0, help="frame index in INPUT")
    ap.add_argument("--scan", type=int, default=3, help="+-frames to search for alignment")
    ap.add_argument("-r", "--region", action="append", default=[],
                    help="name:x,y,w,h (repeatable). Default: whole frame.")
    ap.add_argument("--rgb", action="store_true", help="also report R/G/B shifts")
    args = ap.parse_args()

    regions = [parse_region(r) for r in args.region] or [("full", (0, 0, 0, 0))]

    wi, hi = probe_dims(args.input)
    wo, ho = probe_dims(args.output)
    if (wi, hi) != (wo, ho):
        sys.exit(f"error: dimension mismatch {wi}x{hi} vs {wo}x{ho}; res-align first")
    w, h = wi, hi

    yin = read_frames(args.input, args.frame, 1, w, h, "yuv444p")[0]
    lo = max(0, args.frame - args.scan)
    yout_all = read_frames(args.output, lo, args.scan * 2 + 1, w, h, "yuv444p")

    # frame-align on full-frame mean abs luma delta; tie-break toward d=0
    costs = [(np.abs(yo - yin).mean(), abs((lo + i) - args.frame), i)
             for i, yo in enumerate(yout_all)]
    best = min(costs)[2]
    d = (lo + best) - args.frame

    result = {"input_frame": args.frame, "aligned_output_frame": lo + best,
              "frame_shift": d, "regions": {}}

    rin = rout = None
    if args.rgb:
        rin = read_frames(args.input, args.frame, 1, w, h, "rgb24")[0]
        rout = read_frames(args.output, lo + best, 1, w, h, "rgb24")[0]

    for name, rect in regions:
        ent = {"luma_out_minus_in": round(
            float(region_mean(yout_all[best], rect, w, h) - region_mean(yin, rect, w, h)), 3)}
        if args.rgb:
            din = region_mean(rin, rect, w, h)
            dout = region_mean(rout, rect, w, h)
            ent["rgb_out_minus_in"] = [round(float(v), 3) for v in (dout - din)]
        result["regions"][name] = ent

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
