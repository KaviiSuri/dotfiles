#!/usr/bin/env python3
"""Stack 2+ videos side-by-side (hstack) or stacked (vstack) into one clip, with a
white divider strip between panels and optional per-panel drawtext labels.

Usage:
  video_stack.py [--axis h|v] [--width 1900] [--labels "in|out|diff"] -o OUT.mp4 A B [C ...]

Generic: probes fps/size with ffprobe; never hardcodes resolution. hstack needs equal
heights, vstack needs equal widths -> every input is scaled to the first input's height
(h) or width (v). -shortest handles unequal lengths. Pure ffmpeg. No repo/DB deps.
"""
import argparse
import subprocess
import sys


def probe_wh(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height",
         "-of", "csv=s=x:p=0", path],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    w, h = out.split("x")
    return int(w), int(h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--axis", choices=["h", "v"], default="h")
    ap.add_argument("--width", type=int, default=1900, help="final combo width (0 = none)")
    ap.add_argument("--labels", default="", help="pipe-separated panel labels, e.g. in|out|diff")
    ap.add_argument("inputs", nargs="+")
    a = ap.parse_args()
    n = len(a.inputs)
    if n < 2:
        sys.exit("need >= 2 inputs")

    w0, h0 = probe_wh(a.inputs[0])
    labels = a.labels.split("|") if a.labels else []
    DIV = 10  # divider px

    cmd = ["ffmpeg", "-y"]
    for p in a.inputs:
        cmd += ["-i", p]

    fc = []  # normalise each panel to a common cross-axis size, optional label
    for i in range(n):
        scale = f"scale=-2:{h0}" if a.axis == "h" else f"scale={w0}:-2"
        chain = f"[{i}:v]{scale},setsar=1"
        if i < len(labels) and labels[i]:
            txt = labels[i].replace(":", r"\:").replace("'", r"\'")
            chain += (f",drawtext=text='{txt}':x=10:y=10:fontcolor=white:fontsize=28:"
                      f"box=1:boxcolor=black@0.5:boxborderw=6")
        fc.append(chain + f"[p{i}]")

    # build a color divider source matching the cross-axis size
    if a.axis == "h":
        stack = "hstack"
        fc.append(f"color=c=white:s={DIV}x{h0}[div]")
    else:
        stack = "vstack"
        fc.append(f"color=c=white:s={w0}x{DIV}[div]")

    # interleave panels with dividers: p0 div p1 div p2 ...
    order = []
    for i in range(n):
        if i:
            order.append("[div]")  # NOTE: a color src can only feed one input;
        order.append(f"[p{i}]")
    # color source reused across taps -> split it
    ndiv = n - 1
    if ndiv > 1:
        fc[-1] = fc[-1].replace("[div]", "[divsrc]")
        fc.append("[divsrc]split=%d%s" % (ndiv, "".join(f"[div{i}]" for i in range(ndiv))))
        di = 0
        order = []
        for i in range(n):
            if i:
                order.append(f"[div{di}]"); di += 1
            order.append(f"[p{i}]")

    # shortest=1: stop at the shortest input so the infinite color divider
    # source (and unequal-length clips) can't run the output forever.
    fc.append("".join(order) + f"{stack}=inputs={n * 2 - 1}:shortest=1[st]")
    last = "[st]"
    if a.width:
        fc.append(f"{last}scale={a.width}:-2[out]")
        last = "[out]"

    cmd += ["-filter_complex", ";".join(fc), "-map", last,
            "-shortest", "-pix_fmt", "yuv420p", a.out]
    subprocess.run(cmd, check=True)
    print(a.out)


if __name__ == "__main__":
    main()
