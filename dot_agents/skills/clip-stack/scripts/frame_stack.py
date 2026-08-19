#!/usr/bin/env python3
"""Extract one frame per input at time T and stack them with white divider strips,
then downscale the combo to a target width.

Usage:
  frame_stack.py -t T [--axis h|v] [--width 1900] -o OUT.png IN1 IN2 [IN3 ...]

Generic: probes each input's WxH with ffprobe; never hardcodes resolution.
Panels are resized (nearest-neighbour, numpy) to the first input's dimensions so
concatenation is always valid. Pure ffmpeg + python3 + numpy. No repo/DB deps.
"""
import argparse
import subprocess
import sys
import numpy as np

DIVIDER = 10  # px white strip between panels


def probe_wh(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height",
         "-of", "csv=s=x:p=0", path],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    w, h = out.split("x")
    return int(w), int(h)


def read_frame(path, t, w, h):
    """Grab one RGB24 frame at time t as (h, w, 3) uint8."""
    raw = subprocess.run(
        ["ffmpeg", "-y", "-ss", str(t), "-i", path,
         "-frames:v", "1", "-pix_fmt", "rgb24", "-f", "rawvideo", "pipe:1"],
        capture_output=True, check=True,
    ).stdout
    return np.frombuffer(raw, np.uint8)[: w * h * 3].reshape(h, w, 3)


def resize_nn(img, tw, th):
    h, w = img.shape[:2]
    ys = (np.arange(th) * h / th).astype(int)
    xs = (np.arange(tw) * w / tw).astype(int)
    return img[ys][:, xs]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-t", "--time", default="0", help="timestamp, e.g. 3.5 or 00:00:03.5")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--axis", choices=["h", "v"], default="h")
    ap.add_argument("--width", type=int, default=1900, help="final combo width (0 = no scale)")
    ap.add_argument("inputs", nargs="+")
    a = ap.parse_args()
    if len(a.inputs) < 2:
        sys.exit("need >= 2 inputs")

    tw, th = probe_wh(a.inputs[0])  # target panel size

    frames = []
    for p in a.inputs:
        w, h = probe_wh(p)
        img = read_frame(p, a.time, w, h)
        if (w, h) != (tw, th):
            img = resize_nn(img, tw, th)
        frames.append(img)

    axis = 1 if a.axis == "h" else 0
    div = (np.full((th, DIVIDER, 3), 255, np.uint8) if axis == 1
           else np.full((DIVIDER, tw, 3), 255, np.uint8))
    parts = []
    for i, fr in enumerate(frames):
        if i:
            parts.append(div)
        parts.append(fr)
    combo = np.concatenate(parts, axis=axis)

    H, W = combo.shape[:2]
    vf = f"scale={a.width}:-1" if a.width else "scale=iw:ih"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-i", "pipe:0", "-vf", vf, a.out],
        input=combo.tobytes(), check=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    print(a.out)


if __name__ == "__main__":
    main()
