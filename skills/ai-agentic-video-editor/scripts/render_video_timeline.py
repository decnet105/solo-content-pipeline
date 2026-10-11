#!/usr/bin/env python3
"""
render_video_timeline.py
Automated video pipeline engine supporting multi-track editing, speed adjustments,
cross-dissolve transitions, dynamic callout captions, and BGM mixing via FFmpeg.
"""

import argparse
import json
import subprocess
import sys
import os

def build_ffmpeg_command(config, output_path):
    v_clips = config.get("v1_clips", [])
    callouts = config.get("v2_callouts", [])
    bgm = config.get("a2_bgm", None)
    
    inputs = []
    filter_chains = []
    
    for clip in v_clips:
        inputs.extend(["-i", clip["path"]])
    
    if bgm and "path" in bgm:
        inputs.extend(["-i", bgm["path"]])
        bgm_input_idx = len(v_clips)
    else:
        bgm_input_idx = None
        
    filter_chains.append(f"[0:v]setpts=PTS/{v_clips[0].get("speed", 1.0)}[v0]")
    
    if len(v_clips) > 1:
        for idx in range(1, len(v_clips)):
            speed = v_clips[idx].get("speed", 1.0)
            filter_chains.append(f"[{idx}:v]setpts=PTS/{speed}[v{idx}]")
        
        offset = config.get("transition_offset", 65.8)
        dur = config.get("transition_duration", 0.67)
        filter_chains.append(f"[v0][v1]xfade=transition=fade:duration={dur}:offset={offset}[v_merged]")
        current_v = "[v_merged]"
    else:
        current_v = "[v0]"
        
    for c_idx, c in enumerate(callouts):
        st = c.get("start_s", 0)
        ed = st + c.get("duration_s", 3.0)
        txt = c.get("text", "")
        next_v = f"[v_callout_{c_idx}]"
        draw_filter = (
            f"{current_v}drawbox=x=40:y=ih-120:w=320:h=70:color=black@0.75:t=fill:enable='between(t,{st},{ed})',"
            f"drawtext=text='{txt}':x=60:y=ih-95:fontsize=28:fontcolor=white:enable='between(t,{st},{ed})'{next_v}"
        )
        filter_chains.append(draw_filter)
        current_v = next_v
        
    audio_map = []
    if bgm_input_idx is not None:
        gain = bgm.get("volume_gain_db", -12.0)
        f_in = bgm.get("fade_in_s", 1.0)
        f_out = bgm.get("fade_out_s", 2.5)
        total_dur = config.get("total_duration_s", 87.3)
        st_out = max(0, total_dur - f_out)
        
        filter_chains.append(
            f"[{bgm_input_idx}:a]volume={gain}dB,afade=t=in:st=0:d={f_in},afade=t=out:st={st_out}:d={f_out}[a_bgm]"
        )
        audio_map = ["-map", "[a_bgm]"]
    else:
        audio_map = ["-map", "0:a?"]
        
    full_filter = ";".join(filter_chains)
    
    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", full_filter,
        "-map", current_v,
        *audio_map,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "19",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_path
    ]
    return cmd

def main():
    parser = argparse.ArgumentParser(description="Render video timeline from JSON config.")
    parser.add_argument("--config", required=True, help="Path to timeline JSON config")
    parser.add_argument("--output", required=True, help="Output MP4 file path")
    parser.add_argument("--dry-run", action="store_true", help="Print FFmpeg command without executing")
    args = parser.parse_args()
    
    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)
        
    cmd = build_ffmpeg_command(config, args.output)
    print("Executing FFmpeg command:")
    print(" ".join(cmd))
    
    if not args.dry_run:
        subprocess.run(cmd, check=True)
        print(f"Successfully generated: {args.output}")

if __name__ == "__main__":
    main()
