#!/usr/bin/env python3
"""Word-anchored timing: a narration clip -> the start time of every character/word, so an effect
(e.g. a split-flap number card locking in) can land exactly when the narrator says a chosen word.

Method (chosen from an accuracy experiment on real narration clips; numbers in docs/09):
  1. Whisper (medium) transcription — with your script as `initial_prompt` — and stable-ts (medium)
     forced alignment each produce word times; the two are averaged.
  2. Real pauses are detected from the audio energy, matched to the script's punctuation with a small
     dynamic-programming pass, and the FIRST character after every pause is snapped to the detected
     voiced onset (aligners are systematically late/early exactly there).
  On 40 real Mandarin clips (526 word onsets, 3 TTS voices): median error 22 ms, p95 ~106 ms, 94% within
  100 ms, none over 300 ms; predictions land on average ~18 ms AFTER the audible onset — the direction a
  viewer forgives most. English (neural TTS voices) was checked the same way; see docs/09 for the figures.

Things that are deliberately NOT done here:
  * Do not trust a TTS engine's own word-boundary events as anchors: the ones we measured fire ~65 ms
    BEFORE the audible onset. Everything here is computed from the waveform.
  * Do not use Whisper large-v3 *transcription* for this: on our clips 13.5% of words were >300 ms off
    (max 6 s) because it drops words and shifts everything after them. Forced alignment on `medium` was fine.

Results are cached as JSON keyed by audio-content hash + text hash + language + method version (never by
file name), so editing a script or swapping a voice can't pick up a stale alignment.

Errors:
  AlignmentUnavailable  the tools are missing / this clip could not be aligned -> callers should warn and
                        fall back to their default timing rather than abort the render.
  AnchorSpecError       the requested word is not in the script -> a spec mistake; report it.

Install (optional, only needed for word anchoring):  pip install openai-whisper stable-ts numpy
CLI:
  python3 scripts/word_anchor.py say_intro.mp3 "Your first paycheck, remember it?" --word paycheck --lang en
"""
import argparse
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
import warnings

import numpy as np

METHOD_VERSION = "v1-whisper-medium+stable-ts-medium+onset-snap"
PUNCT = "，。：；？！、—…「」《》“”\"'‘’（）()[]\t\n·,.?!:;~-–_/ "
BREAKS = "，。：；？！、—…,.?!;:"
HOP = 0.010
SR = 16000
WHISPER_MODEL = os.environ.get("WORD_ANCHOR_MODEL", "medium")   # measured on medium; see the large-v3 warning above


class AlignmentUnavailable(RuntimeError):
    """Tools missing, or this clip could not be aligned — callers may degrade."""


class AnchorSpecError(RuntimeError):
    """The anchor word is wrong (not found in the script) — report it to the author."""


def strip_text(s):
    return "".join(ch for ch in s if ch not in PUNCT)


# ---------------------------------------------------------------- audio + pause detection
def _decode16k(path):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                       capture_output=True)
    if r.returncode != 0 or not r.stdout:
        raise AlignmentUnavailable(f"could not decode {path}")
    return np.frombuffer(r.stdout, dtype=np.float32).astype(np.float64)


def _frames_db(x):
    n = int(HOP * SR)
    m = len(x) // n
    if m == 0:
        raise AlignmentUnavailable("audio too short")
    return 20 * np.log10(np.sqrt((x[: m * n].reshape(m, n) ** 2).mean(1) + 1e-14) + 1e-9)


def _voiced_segments(x, rel=-40, min_gap=0.07, min_seg=0.05):
    d = _frames_db(x)
    v = d > (d.max() + rel)
    segs, i, n = [], 0, len(v)
    while i < n:
        if v[i]:
            j = i
            while j < n and v[j]:
                j += 1
            segs.append([i * HOP, j * HOP])
            i = j
        else:
            i += 1
    merged = []
    for s in segs:
        if merged and s[0] - merged[-1][1] < min_gap:
            merged[-1][1] = s[1]
        else:
            merged.append(s)
    out = [s for s in merged if s[1] - s[0] >= min_seg]
    if not out:
        raise AlignmentUnavailable("no speech detected")
    return out


def _phrase_counts(text):
    counts, cur = [], 0
    for ch in text:
        if ch in BREAKS:
            if cur:
                counts.append(cur)
                cur = 0
        elif ch not in PUNCT:
            cur += 1
    if cur:
        counts.append(cur)
    return counts


def _phrase_blocks(x, text):
    """Match the script's punctuation-delimited phrases to the detected pauses (monotonic DP that may skip
    punctuation with no audible pause, or pauses with no punctuation).
    Returns [(first char index, one-past-last char index, first voiced onset of the block, last voiced end)]."""
    chars = strip_text(text)
    N = len(chars)
    segs = _voiced_segments(x)
    counts = _phrase_counts(text)
    C = np.cumsum(counts)[:-1] / N
    d = np.array([s[1] - s[0] for s in segs])
    V = np.cumsum(d)[:-1] / d.sum()
    nb, ng = len(C), len(V)
    A = B = 0.004
    dp = np.full((nb + 1, ng + 1), 1e9)
    back = {}
    dp[0, 0] = 0
    for i in range(nb + 1):
        for j in range(ng + 1):
            cur = dp[i, j]
            if cur >= 1e9:
                continue
            if i < nb and cur + A < dp[i + 1, j]:
                dp[i + 1, j] = cur + A
                back[(i + 1, j)] = (i, j, "skipB")
            if j < ng and cur + B < dp[i, j + 1]:
                dp[i, j + 1] = cur + B
                back[(i, j + 1)] = (i, j, "skipG")
            if i < nb and j < ng:
                c = (C[i] - V[j]) ** 2
                if cur + c < dp[i + 1, j + 1]:
                    dp[i + 1, j + 1] = cur + c
                    back[(i + 1, j + 1)] = (i, j, "match")
    i, j, pairs = nb, ng, []
    while (i, j) != (0, 0):
        pi, pj, kind = back[(i, j)]
        if kind == "match":
            pairs.append((pi, pj))
        i, j = pi, pj
    pairs.reverse()
    cb = np.concatenate([[0], np.cumsum(counts)])
    starts, ends = [(0, segs[0][0])], []
    for pi, pj in pairs:
        ends.append(segs[pj][1])
        starts.append((int(cb[pi + 1]), segs[pj + 1][0]))
    ends.append(segs[-1][1])
    blocks = []
    for k, (c0, T0) in enumerate(starts):
        c1 = starts[k + 1][0] if k + 1 < len(starts) else N
        blocks.append((c0, c1, T0, ends[k]))
    return blocks


def _snap_onsets(x, text, pred, min_char=0.05):
    """Snap only the first character after each pause to the detected voiced onset; later characters that would
    now sit before it are pushed forward, everything else keeps the model's time."""
    pred = list(pred)
    for c0, c1, T0, _ in _phrase_blocks(x, text):
        if c1 <= c0:
            continue
        pred[c0] = T0
        for c in range(c0 + 1, c1):
            if pred[c] < pred[c - 1] + min_char:
                pred[c] = pred[c - 1] + min_char
            else:
                break
    return pred


# ---------------------------------------------------------------- models (lazy, reused within the process)
_MODELS = {}


def _model(kind):
    if kind in _MODELS:
        return _MODELS[kind]
    warnings.filterwarnings("ignore")
    try:
        if kind == "whisper":
            import whisper
            _MODELS[kind] = whisper.load_model(WHISPER_MODEL, device="cpu")
        else:
            import stable_whisper
            _MODELS[kind] = stable_whisper.load_model(WHISPER_MODEL, device="cpu")
    except Exception as e:   # ImportError, missing weights, ...
        raise AlignmentUnavailable(f"{kind} unavailable: {type(e).__name__}: {str(e)[:80]}")
    return _MODELS[kind]


def _words_to_chars(words, text):
    """[(word, start, end)] -> start time of every character of the script (unmatched characters are interpolated).
    Returns (times, fraction of script characters matched exactly)."""
    chars = list(strip_text(text).lower())
    N = len(chars)
    rec_chars, rec_t = [], []
    for w, s, e in words:
        ww = strip_text(w).lower()
        for k, ch in enumerate(ww):
            rec_chars.append(ch)
            rec_t.append(s + (e - s) * k / max(1, len(ww)))
    sm = difflib.SequenceMatcher(None, chars, rec_chars, autojunk=False)
    pred, matched = [None] * N, 0
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            pred[a + k] = rec_t[b + k]
            matched += 1
    known = [(i, t) for i, t in enumerate(pred) if t is not None]
    if not known:
        return None, 0.0
    return list(np.interp(range(N), [k[0] for k in known], [k[1] for k in known])), matched / N


def _run_whisper(audio, text, language):
    r = _model("whisper").transcribe(audio, language=language, word_timestamps=True, initial_prompt=text,
                                      condition_on_previous_text=False, temperature=0.0, fp16=False, verbose=None)
    return _words_to_chars([(w["word"], w["start"], w["end"]) for s in r["segments"] for w in s.get("words", [])], text)


def _run_stable(audio, text, language):
    r = _model("stable").align(audio, text, language=language, verbose=None)
    return _words_to_chars([(w.word, w.start, w.end) for w in r.all_words()], text)


# ---------------------------------------------------------------- public API
def align_chars(audio_path, spoken_text, cache_dir=None, language="en"):
    """Return {"pred": [start second of every script character], "coverage": {...}, "cached": bool}.
    The script characters are strip_text(spoken_text) (punctuation and spaces removed). `language` is a Whisper
    language code ("en", "zh", ...); pass the language the narration is really in."""
    h_audio = hashlib.sha256(open(audio_path, "rb").read()).hexdigest()[:16]
    h_text = hashlib.sha256((language + "\0" + spoken_text).encode("utf-8")).hexdigest()[:12]
    cache = os.path.join(cache_dir, f"align_{h_audio}_{h_text}.json") if cache_dir else None
    if cache and os.path.exists(cache):
        try:
            data = json.load(open(cache, encoding="utf-8"))
            if data.get("method") == METHOD_VERSION:
                data["cached"] = True
                return data
        except (OSError, ValueError):
            pass
    x = _decode16k(audio_path)
    preds, coverage = [], {}
    for name, fn in (("whisper", _run_whisper), ("stable", _run_stable)):
        try:
            p, cov = fn(audio_path, spoken_text, language)
        except AlignmentUnavailable:
            raise
        except Exception as e:
            coverage[name] = f"failed:{type(e).__name__}"
            continue
        coverage[name] = round(cov, 3)
        if p is not None:
            preds.append(p)
    if not preds:
        raise AlignmentUnavailable(f"neither aligner produced a result: {coverage}")
    mean = [float(np.mean(v)) for v in zip(*preds)]
    try:
        pred = [float(v) for v in _snap_onsets(x, spoken_text, mean)]
    except (AlignmentUnavailable, KeyError, IndexError, ValueError):
        pred = mean          # pause/punctuation matching failed: keep the unsnapped average rather than abort
        coverage["snap"] = "skipped"
    data = dict(method=METHOD_VERSION, pred=pred, coverage=coverage, cached=False)
    if cache:
        os.makedirs(cache_dir, exist_ok=True)
        json.dump(data, open(cache, "w", encoding="utf-8"), ensure_ascii=False)
    return data


def _stripped_index(text, upto):
    return sum(1 for ch in text[:upto] if ch not in PUNCT)


def find_word(spoken, pred, word, nth=1):
    """Find the nth occurrence of `word` in the script and return (start second, character index).
    Latin-script words match whole words, case-insensitively ("ten" does not match inside "often");
    other scripts (Chinese, Japanese, ...) match as plain substrings of the punctuation-free script."""
    w = word.strip()
    if not strip_text(w):
        raise AnchorSpecError("at_word must not be empty")
    if w.isascii():
        pat = re.compile(r"(?<![A-Za-z0-9])" + re.escape(w) + r"(?![A-Za-z0-9])", re.IGNORECASE)
        hits = [_stripped_index(spoken, m.start()) for m in pat.finditer(spoken)]
    else:
        s, ww = strip_text(spoken), strip_text(w)
        hits, start = [], 0
        while True:
            i = s.find(ww, start)
            if i < 0:
                break
            hits.append(i)
            start = i + 1
    if len(hits) < int(nth):
        raise AnchorSpecError(f"at_word {word!r}: occurrence #{nth} not found in the script "
                              f"(found {len(hits)}; punctuation-free script: {strip_text(spoken)!r})")
    idx = hits[int(nth) - 1]
    if idx >= len(pred):
        raise AnchorSpecError("alignment length does not match the script")
    return float(pred[idx]), idx


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Print when a word is spoken in a narration clip (word-anchored timing).")
    ap.add_argument("audio")
    ap.add_argument("text", help="the script that was spoken (exactly what you sent to TTS)")
    ap.add_argument("--word", help="print the start time of this word; omit to dump every character's time")
    ap.add_argument("--nth", type=int, default=1, help="which occurrence of --word")
    ap.add_argument("--lang", default="en", help="Whisper language code of the narration (en, zh, ja, ...)")
    ap.add_argument("--cache-dir", default=None)
    a = ap.parse_args()
    try:
        data = align_chars(a.audio, a.text, a.cache_dir, a.lang)
        if a.word:
            t, i = find_word(a.text, data["pred"], a.word, a.nth)
            print(f"{a.word!r} (#{a.nth}) starts at {t:.3f}s  [char {i}, coverage {data['coverage']}]")
        else:
            for ch, t in zip(strip_text(a.text), data["pred"]):
                print(f"{t:7.3f}  {ch}")
    except (AlignmentUnavailable, AnchorSpecError) as e:
        print(f"word_anchor: {e}", file=sys.stderr)
        sys.exit(1)
