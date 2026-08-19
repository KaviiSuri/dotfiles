#!/usr/bin/env python3
"""Low-pass luma diff map between two frame-aligned clips.

Extracts the Y (luma) plane from one frame of each clip, computes a
box-blurred signed difference that reveals broad luma shifts while
suppressing re-encode noise and high-frequency motion (e.g. a moving
mouth), and writes a grayscale map, a hot-colormap magnitude map, and a
[input | output | diffmap] panel.

Usage:
    luma_diff_map.py IN_CLIP OUT_CLIP -t SECONDS -o OUTDIR
                     [-k BLUR] [-a AMP] [--min-luma N]

Deps: ffmpeg, ffprobe, python3, numpy. No repo/DB dependencies.
"""
import argparse, subprocess, sys, os
import numpy as np


def probe_wh(path):
    """Return (width, height) of the first video stream via ffprobe."""
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=s=x:p=0", path,
    ]).decode().strip()
    w, h = out.split("x")
    return int(w), int(h)


def extract_Y(path, t, w, h):
    """Grab one frame at time t and return its Y plane as a HxW float array.

    We decode to raw yuv444p (Y, U, V each full-res, one byte per pixel)
    and keep only the FIRST w*h bytes = the Y plane. This is
    tag/colorspace-independent: we never rely on ffmpeg's 'gray'
    conversion, which applies colorspace matrices that vary with stream
    tags and would inject fake differences.
    """
    raw = subprocess.check_output([
        "ffmpeg", "-nostdin", "-v", "error",
        "-ss", str(t), "-i", path, "-frames:v", "1",
        "-pix_fmt", "yuv444p", "-f", "rawvideo", "pipe:1",
    ])
    y = np.frombuffer(raw[: w * h], dtype=np.uint8).astype(np.float64)
    return y.reshape(h, w)


def boxblur(a, k=25):
    o = k + 1; p = np.pad(a, o, mode='edge'); ii = p.cumsum(0).cumsum(1)
    Y0 = np.arange(a.shape[0])[:, None]; X0 = np.arange(a.shape[1])[None, :]
    return (ii[Y0+o+k, X0+o+k] - ii[Y0+o-k-1, X0+o+k] - ii[Y0+o+k, X0+o-k-1] + ii[Y0+o-k-1, X0+o-k-1]) / ((2*k+1)**2)


def hot_colormap(mag):
    """Map [0,1] magnitude to a black->red->yellow->white 'hot' RGB image."""
    m = np.clip(mag, 0, 1)
    r = np.clip(m * 3, 0, 1)
    g = np.clip(m * 3 - 1, 0, 1)
    b = np.clip(m * 3 - 2, 0, 1)
    return (np.stack([r, g, b], axis=-1) * 255).astype(np.uint8)


def write_png(path, arr):
    """Write a HxW (gray) or HxWx3 (RGB) uint8 array to PNG via ffmpeg."""
    arr = np.ascontiguousarray(arr.astype(np.uint8))
    if arr.ndim == 2:
        h, w = arr.shape; pix = "gray"
    else:
        h, w, _ = arr.shape; pix = "rgb24"
    subprocess.run([
        "ffmpeg", "-nostdin", "-v", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", pix, "-s", f"{w}x{h}",
        "-i", "pipe:0", path,
    ], input=arr.tobytes(), check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("in_clip"); ap.add_argument("out_clip")
    ap.add_argument("-t", "--time", type=float, default=0.0,
                    help="timestamp (s) to sample; same frame in both clips")
    ap.add_argument("-o", "--outdir", default=".")
    ap.add_argument("-k", "--blur", type=int, default=25,
                    help="box-blur half-width; larger = lower frequency")
    ap.add_argument("-a", "--amp", type=float, default=7.0,
                    help="signed-diff amplification for the gray map")
    ap.add_argument("--min-luma", type=int, default=16,
                    help="mask out input pixels darker than this")
    args = ap.parse_args()

    w0, h0 = probe_wh(args.in_clip)
    w1, h1 = probe_wh(args.out_clip)
    if (w0, h0) != (w1, h1):
        sys.exit(f"dimension mismatch: in={w0}x{h0} out={w1}x{h1} "
                 "(clips must be frame-aligned and same size)")

    inY = extract_Y(args.in_clip, args.time, w0, h0)
    outY = extract_Y(args.out_clip, args.time, w0, h0)

    diff = outY - inY
    low = boxblur(diff, args.blur)
    mask = boxblur((inY > args.min_luma).astype(np.float64), args.blur) > 0.5

    gray = np.clip(128 + low * args.amp, 0, 255)
    gray = np.where(mask, gray, 128)

    mag = np.abs(low) * args.amp / 128.0
    hot = hot_colormap(mag)
    hot[~mask] = 0

    os.makedirs(args.outdir, exist_ok=True)
    gray_p = os.path.join(args.outdir, "diff_gray.png")
    hot_p = os.path.join(args.outdir, "diff_hot.png")
    panel_p = os.path.join(args.outdir, "panel.png")
    write_png(gray_p, gray)
    write_png(hot_p, hot)

    inRGB = np.repeat(inY[..., None], 3, axis=-1)
    outRGB = np.repeat(outY[..., None], 3, axis=-1)
    panel = np.concatenate([inRGB, outRGB, hot.astype(np.float64)], axis=1)
    write_png(panel_p, panel)

    print(f"peak |low-pass diff| = {np.abs(low).max():.2f} luma levels")
    print(f"wrote {gray_p}\nwrote {hot_p}\nwrote {panel_p}")


if __name__ == "__main__":
    main()
