#!/usr/bin/env python3
"""Create a non-looping long-grain sleep texture from a project-owned reference WAV."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path

os.environ.setdefault("NUMBA_CACHE_DIR", str(Path(tempfile.gettempdir()) / "mystory-numba-cache"))

import librosa
import numpy as np
import soundfile as sf
from scipy import signal


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def equal_power_envelope(frames: int, fade_fraction: float = 0.36) -> np.ndarray:
    fade = max(1, min(frames // 2, round(frames * fade_fraction)))
    env = np.ones(frames, dtype=np.float64)
    phase = np.linspace(0.0, np.pi / 2.0, fade, endpoint=False)
    env[:fade] = np.sin(phase) ** 2
    env[-fade:] = env[:fade][::-1]
    return env


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--seconds", type=float, default=90.0)
    parser.add_argument("--seed", type=int, default=9142026)
    parser.add_argument("--side-width", type=float, default=0.63)
    parser.add_argument("--lowpass-hz", type=float, default=1800.0)
    parser.add_argument("--grain-min-seconds", type=float, default=7.5)
    parser.add_argument("--grain-max-seconds", type=float, default=14.0)
    parser.add_argument("--rate-min", type=float, default=0.54)
    parser.add_argument("--rate-max", type=float, default=0.82)
    parser.add_argument("--pitch-min-semitones", type=float, default=-0.55)
    parser.add_argument("--pitch-max-semitones", type=float, default=0.55)
    parser.add_argument("--advance-min-fraction", type=float, default=0.20)
    parser.add_argument("--advance-max-fraction", type=float, default=0.34)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    ranges = [
        ("grain seconds", args.grain_min_seconds, args.grain_max_seconds),
        ("rate", args.rate_min, args.rate_max),
        ("pitch", args.pitch_min_semitones, args.pitch_max_semitones),
        ("advance fraction", args.advance_min_fraction, args.advance_max_fraction),
    ]
    for label, lower, upper in ranges:
        if lower <= 0 and label != "pitch":
            raise SystemExit(f"{label} minimum must be positive")
        if lower > upper:
            raise SystemExit(f"{label} minimum must not exceed maximum")
    if args.advance_max_fraction >= 1:
        raise SystemExit("advance fraction maximum must be below 1")

    audio, sr = sf.read(args.input, always_2d=True, dtype="float64")
    if sr != 44_100:
        raise SystemExit("input must be 44.1 kHz WAV")
    if audio.shape[1] != 2:
        raise SystemExit("input must be stereo")
    if len(audio) < 8 * sr:
        raise SystemExit("input must be at least 8 seconds")

    rng = np.random.default_rng(args.seed)
    target_frames = round(args.seconds * sr)
    output = np.zeros((target_frames, 2), dtype=np.float64)
    contribution = np.zeros(target_frames, dtype=np.float64)
    grains: list[dict[str, float | int | bool]] = []
    cursor = -round(2.0 * sr)

    while cursor < target_frames:
        source_seconds = float(
            rng.uniform(args.grain_min_seconds, args.grain_max_seconds)
        )
        source_frames = min(round(source_seconds * sr), len(audio))
        source_start = int(rng.integers(0, max(1, len(audio) - source_frames + 1)))
        grain = audio[source_start : source_start + source_frames].T

        rate = float(rng.uniform(args.rate_min, args.rate_max))
        grain = librosa.effects.time_stretch(grain, rate=rate)
        semitones = float(
            rng.uniform(args.pitch_min_semitones, args.pitch_max_semitones)
        )
        grain = librosa.effects.pitch_shift(grain, sr=sr, n_steps=semitones)
        grain = grain.T

        mid = (grain[:, 0] + grain[:, 1]) * 0.5
        side = (grain[:, 0] - grain[:, 1]) * 0.5
        side_gain = float(rng.uniform(0.86, 1.18))
        grain[:, 0] = mid + side * side_gain
        grain[:, 1] = mid - side * side_gain

        envelope = equal_power_envelope(len(grain))
        gain = float(10 ** (rng.uniform(-4.0, -1.2) / 20.0))
        grain *= envelope[:, None] * gain

        start = max(0, cursor)
        grain_offset = max(0, -cursor)
        end = min(target_frames, cursor + len(grain))
        if end > start:
            used = end - start
            output[start:end] += grain[grain_offset : grain_offset + used]
            contribution[start:end] += envelope[grain_offset : grain_offset + used] * gain

        grains.append(
            {
                "source_start_seconds": round(source_start / sr, 4),
                "source_seconds": round(source_frames / sr, 4),
                "rate": round(rate, 6),
                "pitch_semitones": round(semitones, 6),
                "side_gain": round(side_gain, 6),
                "gain": round(gain, 8),
                "timeline_start_seconds": round(cursor / sr, 4),
            }
        )
        advance = round(
            len(grain)
            * float(
                rng.uniform(args.advance_min_fraction, args.advance_max_fraction)
            )
        )
        cursor += max(round(2.5 * sr), advance)

    # Equalise changing overlap density without boosting near-silent edge tails.
    # This removes grain-count level jumps while preserving the reference's
    # own micro-dynamics inside every long grain.
    safe = contribution > 1e-8
    output[safe] /= np.maximum(0.35, contribution[safe, None])

    control_times = [0]
    while control_times[-1] < target_frames:
        control_times.append(control_times[-1] + round(float(rng.uniform(9.0, 19.0)) * sr))
    control_times[-1] = target_frames - 1
    control_db = rng.uniform(-1.3, 0.6, len(control_times))
    slow_gain = np.interp(np.arange(target_frames), control_times, 10 ** (control_db / 20.0))
    output *= slow_gain[:, None]

    # Correct only long-window overlap-density drift. Two-second target points
    # are interpolated sample-by-sample, so this is not compression and cannot
    # introduce an attack or a rhythmic pump.
    block = 2 * sr
    centers: list[int] = []
    block_rms: list[float] = []
    for start in range(0, target_frames, block):
        stop = min(target_frames, start + block)
        centers.append((start + stop - 1) // 2)
        block_rms.append(float(np.sqrt(np.mean(output[start:stop] ** 2) + 1e-12)))
    target_rms = float(np.median(block_rms))
    correction_db = np.clip(
        20.0 * np.log10(target_rms / np.maximum(block_rms, 1e-12)), -4.0, 4.0
    )
    correction = np.interp(
        np.arange(target_frames), centers, 10 ** (correction_db / 20.0)
    )
    output *= correction[:, None]

    mid = (output[:, 0] + output[:, 1]) * 0.5
    side = (output[:, 0] - output[:, 1]) * 0.5 * args.side_width
    output[:, 0] = mid + side
    output[:, 1] = mid - side

    sos = signal.butter(3, args.lowpass_hz, btype="lowpass", fs=sr, output="sos")
    output = signal.sosfiltfilt(sos, output, axis=0)

    reference_rms = float(np.sqrt(np.mean(audio**2)))
    output_rms = float(np.sqrt(np.mean(output**2)))
    if output_rms > 0:
        output *= reference_rms / output_rms
    peak = float(np.max(np.abs(output)))
    peak_ceiling = 10 ** (-5.0 / 20.0)
    if peak > peak_ceiling:
        output *= peak_ceiling / peak

    args.output.parent.mkdir(parents=True, exist_ok=True)
    sf.write(args.output, output, sr, subtype="PCM_24")
    receipt_path = args.receipt or args.output.with_suffix(".receipt.json")
    receipt = {
        "schema_version": "1.0",
        "method": "non_looping_long_grain_reference_resynthesis",
        "input": str(args.input),
        "input_sha256": sha256(args.input),
        "output": str(args.output),
        "output_sha256": sha256(args.output),
        "sample_rate": sr,
        "channels": 2,
        "seconds": args.seconds,
        "seed": args.seed,
        "grain_count": len(grains),
        "grain_seconds_range": [args.grain_min_seconds, args.grain_max_seconds],
        "rate_range": [args.rate_min, args.rate_max],
        "pitch_semitones_range": [
            args.pitch_min_semitones,
            args.pitch_max_semitones,
        ],
        "advance_fraction_range": [
            args.advance_min_fraction,
            args.advance_max_fraction,
        ],
        "grains": grains,
        "slow_gain_control_seconds": [round(v / sr, 4) for v in control_times],
        "slow_gain_control_db": [round(float(v), 4) for v in control_db],
        "two_second_level_correction_db": [round(float(v), 4) for v in correction_db],
        "final_side_width": args.side_width,
        "lowpass_hz": args.lowpass_hz,
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
