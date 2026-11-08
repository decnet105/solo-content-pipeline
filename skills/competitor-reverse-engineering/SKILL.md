---
name: competitor-reverse-engineering
description: Autonomous competitor benchmarking, multidimensional reverse-engineering, gap analysis, and closed-loop retention directive generation for YouTube automation channels.
---

# Competitor Reverse-Engineering & Closed-Loop Retention Skill

## Purpose
Establishes an automated reverse-engineering and benchmarking protocol to scan daily top competitors, deconstruct high-outlier videos across 6 core retention dimensions, calculate gap metrics against our current channel baseline, and inject concrete retention upgrade directives into the next video production cycle.

## 6-Dimension Reverse-Engineering Architecture

Every competitor outlier video (Outlier Multiple $\ge 2.0\times$) and our current episode are graded on a 10-point scale:

1. **Cold-Open Hook (0-30s Drop-off Prevention)**:
   - *Check*: First 2.0s visual motion, zero host greeting, counter-intuitive cognitive gap or emotional stake, immediate sensory hook.
   - *Target*: 30s retention rate $\ge 80\%$.
2. **Information Density & Cadence (WPM & Breathing Rhythm)**:
   - *Check*: Words Per Minute (WPM) modulation between fast-paced setup (140-155 WPM) and micro-pauses (0.3-0.6s) on key insights; zero verbal filler.
3. **Visual Cut Frequency & Motion Vector (Static Elimination)**:
   - *Check*: Average shot length (ASL) $\le 3.5\text{s}$, static frame ratio $\le 0.70$, first 30s visual transitions $\ge 4$, active motion (Ken Burns / dynamic crop / UI highlights).
4. **Narrative Tension Arc (Cognitive Dissonance to Resolution)**:
   - *Check*: Strong opening contradiction -> escalating mystery -> 3-step structured deconstruction -> delayed emotional/practical payoff.
5. **Sound Bed & Acoustic Engineering**:
   - *Check*: Voice-band carve (500Hz - 3kHz attenuation $\ge 10\text{dB}$), speech loudness $-14.0$ to $-19.5\text{ LUFS}$, 38-45Hz sub-bass transient punch on revelations, ambient environmental realism.
6. **Packaging & Outro Retention Shield (CTR & Loop Retention)**:
   - *Check*: Mobile feed thumbnail legibility $\ge 0.55$ at $168\times94\text{ px}$, cover word count $\le 8$ words, zero template fatigue, end-screen loop / passcode companion PDF asset retention.

---

## Daily Execution Protocol

```bash
# 1. Run competitor scan & gap analysis
python3 scripts/competitor_closed_loop_engine.py --channel tokyoflow_japanese --snapshot data/competitor_snapshots/tokyoflow_japanese/latest.json

# 2. Generate Next-Episode Retention Directive
python3 scripts/competitor_closed_loop_engine.py --channel tokyoflow_japanese --generate-directive --output-dir config/directives/
```

---

## Gap Attribution & Rectification Matrix

| Dimension | Typical Weakness in Automated Channels | Competitor Benchmark Standard | Automated Production Directive |
| :--- | :--- | :--- | :--- |
| **Cold-Open** | Host greeting ("Welcome back"), generic logo animation | 0.0s instant situational crisis or counter-intuitive paradox | Cut bumper; hard-code scene crisis in 0.0s; pose paradoxical premise in first 15 words |
| **Visuals** | Static slides or AI stills held for 15-30s | Continuous dynamic motion, Ken Burns zooms, dynamic highlighting | Enforce `static_ratio <= 0.70`, transition every $\le 3.5\text{s}$, Kara-oke word highlight |
| **Pacing** | Monotone synthesized speech with flat tempo | Dynamic prosody, calibrated micro-pauses after revelations | Snip pause markers, insert 0.4s silence buffers around punchlines, modulate WPM |
| **Thumbnail** | 20+ small words, text clipping on mobile | Bold 3-6 words, high contrast focal element, OCR clarity | Enforce `words <= 8`, `legibility >= 0.55`, distinct EN/ZH layout designs |
| **Assets** | Generic description with dead links | Free unencrypted 300 DPI companion PDF + locked passcode | Auto-generate Google Drive companion asset; pin direct HTTP 200 comment |

---

## Closed-Loop Self-Healing Standard

- If benchmark scores show our current episode lagging by $\ge 15$ points behind the competitor median, the production system **halts publishing** and auto-triggers re-cutting or visual injection.
- Memory registers (`ledger/arbitration_records.json` and `docs/playbook`) are dynamically updated with the winning competitor outlier attributes to ensure permanent learning across episodes.
