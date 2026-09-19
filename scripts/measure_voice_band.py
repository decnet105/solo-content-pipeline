#!/usr/bin/env python3
"""Voice-band balance check — how much louder is the narration than the music where speech is understood?

Speech intelligibility depends mostly on roughly 500 Hz - 3 kHz. Whole-signal loudness meters and flat
ducking say nothing about that band, so a bed that is "12 dB ducked" can still sit right on top of the
narrator there. This read-only tool measures the gap directly on an already-rendered spec:

  * takes the intermediate files make_short.py leaves in tmp/videogen/spec-<name>/
    (narration_mix.wav or narration.mp3, plus the spec's music file),
  * re-mixes them twice with the production filter graph — the legacy flat ducking (`music.carve: false`)
    and the voice-carve mix (the default) — using the spec's own music.start / gain_db / bgm_ducking_db,
  * prints, for each, the median over speech frames of
        (narration level in 500 Hz-3 kHz) - (ducked-music level in 500 Hz-3 kHz)   [dB].

Rules of thumb from our own renders: above about +10 dB is comfortable; below about +6 dB the bed is
competing with the voice (turn carve on, or lower music.gain_db). It is a band-RMS ratio — a proxy, not a
formal intelligibility index (STI/STOI) and not a substitute for listening.

Usage (needs numpy, scipy, soundfile):
    python3 scripts/measure_voice_band.py path/to/spec.json [more specs ...]
Writes only temporary WAVs; changes nothing in the repo.
"""
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
import soundfile as sf
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_short as ms  # noqa: E402  (reuse narration_bed_graph so the measurement uses the production mix)

SR = 48000
VOICE_BAND = (500, 3000)


def _ff(args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def _load(path):
    x, sr = sf.read(path, dtype="float64")
    assert sr == SR
    return x if x.ndim == 1 else x.mean(1)


def _band(x, lo, hi):
    return signal.sosfiltfilt(signal.butter(4, [lo, hi], "bandpass", fs=SR, output="sos"), x)


def _frame_db(x, hop=0.1):
    n = int(hop * SR)
    m = len(x) // n
    return 20 * np.log10(np.sqrt((x[: m * n].reshape(m, n) ** 2).mean(1) + 1e-14) + 1e-9)


def _speech_mask(nar, hop=0.1):
    d = _frame_db(nar, hop)
    m = d > (d.max() - 32)
    k = int(0.25 / hop)   # gaps shorter than 250 ms inside a sentence still count as speaking
    return np.array([m[max(0, i - k): i + k + 1].any() for i in range(len(m))])


def measure(spec_path, work):
    spec = json.load(open(spec_path, encoding="utf-8"))
    tmp = f"tmp/videogen/spec-{spec['name']}"
    m = spec.get("music") if isinstance(spec.get("music"), dict) else {}
    bgm = m.get("file") if m.get("file") and os.path.exists(m["file"]) else (
        f"{tmp}/bgm.mp3" if os.path.exists(f"{tmp}/bgm.mp3") else None)
    nar = next((p for p in (f"{tmp}/narration_mix.wav", f"{tmp}/narration.mp3") if os.path.exists(p)), None)
    if not (bgm and nar):
        return None, f"no intermediates under {tmp}/ (render the spec first, from the repo root)"
    duck = (spec.get("narration") or spec.get("voice") or {}).get("bgm_ducking_db", spec.get("bgm_ducking_db", -12))
    start = m.get("start", 0.0)
    total = min(ms.ffprobe_dur(nar), 40.0)
    if total < 8:
        return None, "narration shorter than 8 s"

    carve = ms.music_carve_setting(spec)
    carve = True if carve is None else carve          # even if the spec turned carve off, show what turning it on would do
    graphs = {
        "flat": ms.narration_bed_graph(total, duck, m.get("gain_db"), None),
        "carve": ms.narration_bed_graph(total, duck, m.get("gain_db"), carve),
    }

    def stems(tag, graph):
        graph = graph.replace(f"afade=t=out:st={max(0.4, total - 2.0):.2f}:d=2.0", "anull") + ";[nmix]anull[nout]"
        pm, pn = f"{work}/{tag}_m.wav", f"{work}/{tag}_n.wav"
        _ff(["-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-ss", str(start), "-i", bgm, "-i", nar,
             "-filter_complex", graph, "-map", "[duckbg]", "-t", f"{total:.3f}", "-ac", "1", "-ar", str(SR), pm,
             "-map", "[nout]", "-t", f"{total:.3f}", "-ac", "1", "-ar", str(SR), pn])
        return pm, pn

    def gap_db(music_wav, nar_wav):
        mu, na = _load(music_wav), _load(nar_wav)
        n = min(len(mu), len(na))
        mask = _speech_mask(na[:n])
        d = (_frame_db(_band(na[:n], *VOICE_BAND)) - _frame_db(_band(mu[:n], *VOICE_BAND)))[: len(mask)]
        return float(np.median(d[mask[: len(d)]]))

    return dict(name=spec["name"], flat=gap_db(*stems("flat", graphs["flat"])),
                carve=gap_db(*stems("carve", graphs["carve"])), bed=os.path.basename(bgm)), None


if __name__ == "__main__":
    paths = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not paths:
        print(__doc__)
        sys.exit(2)
    rows = []
    with tempfile.TemporaryDirectory(prefix="voiceband-") as work:
        for p in paths:
            r, why = measure(p, work)
            if r is None:
                print(f"{os.path.basename(p):36s} skipped: {why}")
                continue
            rows.append(r)
            print(f"{r['name']:30s} narration above music in 500Hz-3kHz:  flat ducking {r['flat']:+6.1f} dB  ->  voice carve {r['carve']:+6.1f} dB   ({r['bed'][:24]})")
    if len(rows) > 1:
        f = np.array([r["flat"] for r in rows]); c = np.array([r["carve"] for r in rows])
        print(f"\n{len(rows)} specs: flat median {np.median(f):+.1f} dB (worst {f.min():+.1f}, {int((f < 6).sum())} below +6); "
              f"carve median {np.median(c):+.1f} dB (worst {c.min():+.1f}, {int((c < 6).sum())} below +6)")
