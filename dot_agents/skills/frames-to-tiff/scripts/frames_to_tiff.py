#!/usr/bin/env python3
"""Export lossless TIFF frames from a video clip at given timestamps.

Pure ffmpeg/ffprobe wrapper. No repo, DB, or hardcoded-dimension assumptions:
real width/height/fps/color tags are probed at runtime.
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def die(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def probe(clip: str) -> dict:
    """Return dict of the first video stream's key properties."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries",
        "stream=width,height,avg_frame_rate,pix_fmt,color_range,color_space,color_transfer,color_primaries",
        "-of", "json", clip,
    ]
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        die(f"ffprobe failed: {out.stderr.strip()}")
    streams = json.loads(out.stdout).get("streams", [])
    if not streams:
        die("no video stream found in clip")
    return streams[0]


def parse_fps(avg_frame_rate: str) -> float:
    try:
        num, den = avg_frame_rate.split("/")
        den = float(den)
        return float(num) / den if den else 0.0
    except Exception:
        return 0.0


def extract(clip: str, t: float, out_path: Path, crop: str | None, accurate: bool) -> None:
    seek = ["-ss", f"{t}"]
    cmd = ["ffmpeg", "-y", "-v", "error"]
    if accurate:
        cmd += ["-i", clip] + seek
    else:
        cmd += seek + ["-i", clip]
    if crop:
        cmd += ["-vf", f"crop={crop}"]
    # -compression_algo raw = truly uncompressed TIFF (ffmpeg defaults to
    # lossless PackBits RLE otherwise; raw is safest for pixel inspection).
    cmd += ["-frames:v", "1", "-pix_fmt", "rgb24",
            "-compression_algo", "raw", str(out_path)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 or not out_path.exists():
        die(f"ffmpeg failed at t={t}: {res.stderr.strip()}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Export lossless TIFF frames at timestamps.")
    ap.add_argument("--clip", required=True, help="input video path")
    ap.add_argument("--times", nargs="+", type=float, help="timestamps in seconds")
    ap.add_argument("--range", nargs=2, type=float, metavar=("START", "END"),
                    help="export every frame between START and END seconds")
    ap.add_argument("--crop", help="ffmpeg crop region W:H:X:Y")
    ap.add_argument("--outdir", default=".", help="output directory")
    ap.add_argument("--accurate", action="store_true",
                    help="put -ss after -i for frame-accurate (slower) seek")
    args = ap.parse_args()

    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            die(f"{tool} not found on PATH")
    if not args.times and not args.range:
        die("provide --times or --range")
    if not Path(args.clip).exists():
        die(f"clip not found: {args.clip}")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    info = probe(args.clip)
    fps = parse_fps(info.get("avg_frame_rate", "0/0"))
    meta = {
        "clip": args.clip,
        "width": info.get("width"),
        "height": info.get("height"),
        "fps": fps,
        "src_pix_fmt": info.get("pix_fmt"),
        "color_range": info.get("color_range", "unknown"),
        "color_space": info.get("color_space", "unknown"),
        "color_transfer": info.get("color_transfer", "unknown"),
        "color_primaries": info.get("color_primaries", "unknown"),
        "output_pix_fmt": "rgb24 (lossless TIFF)",
        "crop": args.crop,
        "frames": [],
    }
    print(f"probed: {meta['width']}x{meta['height']} @ {fps:.4f}fps "
          f"range={meta['color_range']} space={meta['color_space']} "
          f"transfer={meta['color_transfer']}")

    written = []
    if args.times:
        for t in args.times:
            name = f"frame_t{t:.3f}.tiff"
            path = outdir / name
            extract(args.clip, t, path, args.crop, args.accurate)
            written.append({"t": t, "file": str(path.resolve())})
            print(f"wrote {path}")
    if args.range:
        start, end = args.range
        if fps <= 0:
            die("cannot determine fps for --range; use --times")
        n = int(round((end - start) * fps))
        for i in range(n + 1):
            t = start + i / fps
            if t > end + 1e-9:
                break
            name = f"frame_r{start:.3f}_{i:04d}.tiff"
            path = outdir / name
            extract(args.clip, t, path, args.crop, args.accurate)
            written.append({"t": round(t, 6), "file": str(path.resolve())})
            print(f"wrote {path}")

    meta["frames"] = written
    meta_path = outdir / "frames_meta.json"
    meta_path.write_text(json.dumps(meta, indent=2))
    print(f"wrote {meta_path} ({len(written)} frame(s))")
    print(f"NOTE color_range={meta['color_range']} — report this to the provider.")


if __name__ == "__main__":
    main()
