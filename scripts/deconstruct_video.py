#!/usr/bin/env python3
# Reference-video sampler for the video-deconstruct skill. Fetches a source
# (yt-dlp for a URL, or a local file used as-is), then produces dense-but-bounded
# frame samples, a single contact sheet, and a timestamped frame manifest so an
# agent (or you) can review a video's rhythm at a glance before doing a
# dimension-by-dimension teardown. Zero third-party Python deps — just ffmpeg,
# ffprobe, and yt-dlp on PATH.
#
# This script only gathers evidence. It draws no conclusions about hooks,
# pacing, color, or anything else — that's the skill's job, done by reading the
# contact sheet, key frames, and manifest against
# skills/video-deconstruct/references/deconstruct-framework.md.
#
# Usage:
#   python3 scripts/deconstruct_video.py <url-or-file> --out output/deconstruct/<name> \
#     [--fps 2] [--max-frames 120] [--width 768] [--extract-audio]
#
# Respect the source's own access controls: this script does not bypass a
# login, paywall, CAPTCHA, or anti-bot protection, and a URL you cannot legally
# view is not a valid input.
import os, sys, json, csv, glob, shutil, argparse, tempfile, subprocess

def run(cmd, quiet=True):
    kw = dict(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) if quiet else {}
    subprocess.run(cmd, check=True, **kw)

def fetch(source, tmp):
    """A local path is used directly; a URL is pulled with yt-dlp and remuxed to mp4."""
    if os.path.exists(source):
        return source
    out = os.path.join(tmp, "src.%(ext)s")
    run(["yt-dlp", "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
         "--merge-output-format", "mp4", "-o", out, source], quiet=False)
    got = glob.glob(os.path.join(tmp, "src.*"))
    if not got:
        sys.exit("download failed")
    return got[0]

def probe_dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except Exception:
        return 0.0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="video URL or local file path")
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--fps", type=float, default=2.0, help="sampling density (default 2fps)")
    ap.add_argument("--max-frames", type=int, default=120,
                     help="frame cap (default 120 — fps is reduced automatically for long videos)")
    ap.add_argument("--width", type=int, default=768, help="sampled-frame width")
    ap.add_argument("--extract-audio", action="store_true",
                     help="also extract 16kHz mono audio (for transcription)")
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    framedir = os.path.join(a.out, "frames"); os.makedirs(framedir, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="deconstruct-")
    try:
        src = fetch(a.source, tmp)
        dur = probe_dur(src)
        fps = a.fps
        if dur > 0 and dur * fps > a.max_frames:      # keep the total under the cap
            fps = a.max_frames / dur
        run(["ffmpeg", "-y", "-i", src, "-vf", f"fps={fps:.4f},scale={a.width}:-2",
             "-q:v", "3", os.path.join(framedir, "f_%04d.jpg")])
        frames = sorted(glob.glob(os.path.join(framedir, "f_*.jpg")))

        manifest = []
        for i, f in enumerate(frames):
            ts = i / fps
            manifest.append({"frame": i + 1, "t_sec": round(ts, 2),
                             "t_str": f"{int(ts // 60):02d}:{ts % 60:05.2f}",
                             "path": os.path.relpath(f, a.out)})
        with open(os.path.join(a.out, "frames.json"), "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, ensure_ascii=False, indent=2)
        with open(os.path.join(a.out, "frames.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["frame", "t_sec", "t_str", "path"])
            w.writeheader(); w.writerows(manifest)

        # Contact sheet — every sampled frame tiled into one image, so pacing
        # and rhythm are visible before reading anything frame-by-frame.
        if frames:
            cols = 6; rows = (len(frames) + cols - 1) // cols
            run(["ffmpeg", "-y", "-i", os.path.join(framedir, "f_%04d.jpg"),
                 "-vf", f"scale=320:-2,tile={cols}x{rows}:padding=6:color=0x1a1a1a",
                 "-frames:v", "1", os.path.join(a.out, "contact-sheet.jpg")])

        if a.extract_audio:
            run(["ffmpeg", "-y", "-i", src, "-vn", "-ac", "1", "-ar", "16000",
                 os.path.join(a.out, "audio.mp3")])

        print(f"Sampling complete -> {a.out}")
        print(f"  duration {dur:.1f}s -> {len(frames)} frames (fps={fps:.3f}) at width {a.width}")
        print("  contact-sheet.jpg, frames.json / frames.csv"
              + (", audio.mp3" if a.extract_audio else ""))
        print("  Next: read the contact sheet + key frames + manifest and work through "
              "skills/video-deconstruct/references/deconstruct-framework.md dimension by dimension.")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    main()
