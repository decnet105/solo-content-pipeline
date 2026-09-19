#!/usr/bin/env python3
# Spec-JSON driven vertical short-video pipeline (one command, fully automated).
# ============================================================================
# Usage:  python3 scripts/make_short.py examples/example-spec.json
# One command: read the shot spec -> for any missing asset call
# gen_image / gen_video / gen_music / gen_voice -> assemble the finished MP4.
# Assets that already exist on disk are reused at $0. Swap the spec = swap the
# topic and get a new video, no code changes.
#
# Spec schema (see examples/example-spec.json for a runnable example):
#   name, out (output path),
#   music:   {prompt|file, start(sec, align the energy peak to a key shot), instrumental,
#             carve?(default on: keep the BGM out of the voice band; false = legacy flat ducking),
#             gain_db?(static bed level, default -1.4)}
#   intro:   {title, subtitle, dur, logo?}          # generic text hook card
#   outro:   {title, subtitle?, tagline?, cta?, dur, logo?}   # generic text end card
#   end_logo:{logo?, cta?}                           # OPTIONAL corner branding (image + CTA)
#   transitions: [[type,dur],...]  (optional, a default set is used otherwise)
#   shots: [ {key, dur, primary, secondary,          # primary/secondary = same-frame subtitles
#             say,                                     # per-shot narration line (see below)
#             image:{src:<existing> | gen:<image prompt>},
#             clip:<existing motion mp4> | seedance:{prompt,face_free},
#             clip_ss:<clip start offset>, motion:in|out|panL|punchin, mode:cover|fit,
#             number_card:{label, number, unit?, source?, animate?:splitflap|static,   # exact figure, drawn locally
#                          at_word?, at_word_nth?, at_mode?:settle|start} } ]          # at_word: land it on a spoken word
#
# Notes: image-to-video models hard-block clear faces -> a face shot with
#   face_free=false automatically falls back to Ken Burns on a still.
#   Subtitles are same-frame bilingual (primary larger, secondary smaller).
#   Final encode is BT.709 for playback safety. No bundled branding: intro/outro
#   are plain text cards from the spec; the optional corner logo reads a
#   user-supplied image path + CTA text from the spec (omit to run brand-free).
# ============================================================================
import os, sys, json, math, subprocess
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
BW, BH = 2160, 3840
# ---- example palette — customize for your brand ----
PAPER = (245, 241, 232)     # warm off-white card background
NAVY  = (18, 54, 94)        # primary ink color for text
GOLD  = (167, 122, 45)      # accent color (divider / CTA)
GOLD_L = (211, 176, 100)    # lighter accent (unused by default; kept for gradients)
CREAM = (245, 241, 232)     # subtitle fill on dark video
DARKHEX = "0x141210"
# Serif font for cards + subtitles. The default is a neutral system serif that
# renders Latin; for CJK / bilingual subtitles set VIDEOGEN_FONT to a font that
# has CJK glyphs (e.g. a Noto Serif CJK). Falls back to PIL's built-in font.
_FONT_CANDIDATES = [
    os.environ.get("VIDEOGEN_FONT", ""),
    "/System/Library/Fonts/Supplemental/Georgia.ttf",    # macOS
    "/Library/Fonts/Georgia.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",  # Linux
    "C:/Windows/Fonts/georgia.ttf",                      # Windows
]
_W2IDX = {"black": 0, "bold": 1, "light": 3, "regular": 6}   # face index within a .ttc collection; ignored for single-face fonts
def vfont(size, weight="black"):
    for path in _FONT_CANDIDATES:
        if not path or not os.path.exists(path):
            continue
        try:
            return ImageFont.truetype(path, size, index=_W2IDX.get(weight, 0))
        except Exception:
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()

REVEAL_HOLD = 0.10   # fraction of an intro/outro card held before text fades in
DEFAULT_XF = [["zoomin",.28],["smoothleft",.20],["smoothright",.20],["zoomin",.22],
              ["fadewhite",.14],["smoothup",.20],["hblur",.22],["fadewhite",.14],["zoomin",.30]]

# API caller scripts live next to this file, so make_short.py works from any cwd.
_HERE = os.path.dirname(os.path.abspath(__file__))
GEN_IMAGE = os.path.join(_HERE, "gen_image.mjs")
GEN_VIDEO = os.path.join(_HERE, "gen_video.mjs")
GEN_MUSIC = os.path.join(_HERE, "gen_music.mjs")
GEN_VOICE = os.path.join(_HERE, "gen_voice.mjs")
GEN_NUMBER_CARD = os.path.join(_HERE, "gen_number_card.py")
GEN_SPLITFLAP_CARD = os.path.join(_HERE, "gen_splitflap_card.py")

# ---------------------------------------------------------------- text helpers
# Closing punctuation that must not begin a wrapped line (Latin + CJK line-break
# rule, aka kinsoku). Keeps CJK subtitles from wrapping onto a stray comma/quote.
NO_HEAD = set("。，、；：！？」）】》.,!?:;")
def _has_cjk(s): return any(ord(c) > 0x2E7F for c in s)
def wrap_chars(draw, text, font, mw):
    # character-wrap (for CJK / no-space scripts)
    lines, cur = [], ""
    for ch in text:
        if draw.textlength(cur+ch, font=font) <= mw: cur += ch
        elif ch in NO_HEAD and cur: cur += ch; lines.append(cur); cur = ""
        else: lines.append(cur); cur = ch
    if cur: lines.append(cur)
    return lines
def wrap_words(draw, text, font, mw):
    # word-wrap (for space-delimited scripts, e.g. English)
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur+" "+w).strip()
        if draw.textlength(t, font=font) <= mw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines
def wrap(draw, text, font, mw):
    # auto-pick: CJK -> character wrap, otherwise word wrap
    return wrap_chars(draw, text, font, mw) if _has_cjk(text) else wrap_words(draw, text, font, mw)

def draw_center(draw, lines, font, y, lh, fill, stroke=5, sf=(14,12,10), shadow=True):
    for ln in lines:
        w = draw.textlength(ln, font=font); x = (W-w)/2
        if shadow: draw.text((x, y+3), ln, font=font, fill=(0,0,0,110))
        draw.text((x, y), ln, font=font, fill=fill, stroke_width=stroke, stroke_fill=sf)
        y += lh
    return y
def bottom_scrim(cv, top=1080, amax=185):
    ov = Image.new("RGBA",(W,H),(0,0,0,0)); od = ImageDraw.Draw(ov)
    for i, y in enumerate(range(top, H)): od.line([(0,y),(W,y)], fill=(8,6,4, int(amax*(i/(H-top)))))
    return Image.alpha_composite(cv, ov)
def _smooth(t): t = max(0.,min(1.,t)); return t*t*(3-2*t)

def _paste_pop(cv, lines, font, cy, lh, scale, alpha, fill, stroke=4):
    pad = 48
    layer = Image.new("RGBA", (W, len(lines)*lh+pad*2), (0,0,0,0))
    draw_center(ImageDraw.Draw(layer), lines, font, pad, lh, fill, stroke=stroke, shadow=bool(stroke))
    if scale != 1.0: layer = layer.resize((int(W*scale), int(layer.height*scale)), Image.LANCZOS)
    if alpha < 1.0: layer.putalpha(layer.getchannel("A").point(lambda v, a=alpha: int(v*a)))
    cv.alpha_composite(layer, ((W-layer.width)//2, int(cy-layer.height/2)))

def _build_end_logo(cfg):
    """Optional corner branding for a content shot: a user-supplied logo image
    and/or a CTA line, both taken from the spec. Returns an RGBA W×H layer that
    is faded in over the second half of the shot, or None if nothing was given
    (so the pipeline runs perfectly with branding omitted). No bundled asset."""
    logo_path = cfg.get("logo"); cta = cfg.get("cta", "")
    has_logo = bool(logo_path) and os.path.exists(logo_path)
    if not has_logo and not cta:
        return None
    layer = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(layer)
    RM = W - 85          # right-align baseline
    ly = 95; bottom = ly
    if has_logo:
        lg = Image.open(logo_path).convert("RGBA")
        MW = 128; scl = MW/lg.width; mh = round(lg.height*scl)
        lg = lg.resize((MW, mh), Image.LANCZOS)
        layer.alpha_composite(lg, (RM-MW, ly)); bottom = ly + mh
    if cta:
        ctf = vfont(27, "regular")
        cw = d.textlength(cta, font=ctf); cy = bottom + 20
        d.text((RM-cw, cy), cta, font=ctf, fill=GOLD + (255,))
        d.line([(RM-cw, cy+44), (RM, cy+44)], fill=GOLD + (255,), width=2)
    return layer

def make_overlay_seq(primary, secondary, prefix, frames, end_logo=None):
    cf = vfont(60, "bold"); ef = vfont(37, "regular")
    td = ImageDraw.Draw(Image.new("RGBA",(W,H)))
    pl, sl = [], []
    for p in primary.split("\n"): pl += wrap(td, p, cf, W-150)
    for p in secondary.split("\n"): sl += wrap(td, p, ef, W-150)
    clh, elh, gap = 80, 50, 16
    cb, eb = len(pl)*clh, len(sl)*elh; total = cb+gap+eb
    top = H-175-total; p_cy, s_cy = top+cb/2, top+cb+gap+eb/2
    pop = max(2, int(0.20*FPS)); stag = 4
    scrim = bottom_scrim(Image.new("RGBA",(W,H),(0,0,0,0)), top=max(1000, top-90)); sa = scrim.getchannel("A")
    logo_img, lstart = None, int(frames * 0.55)
    if end_logo:
        logo_img = _build_end_logo(end_logo)
    for i in range(frames):
        ac = _smooth(min(1., i/pop)); sc = 1.12-0.12*ac
        ae = _smooth(min(1., max(0, i-stag)/pop)); se = 1.12-0.12*ae
        cv = Image.new("RGBA",(W,H),(0,0,0,0)); scr = scrim.copy()
        if ac < 1.0: scr.putalpha(sa.point(lambda v, a=ac: int(v*a)))
        cv = Image.alpha_composite(cv, scr)
        if ac > 0: _paste_pop(cv, pl, cf, p_cy, clh, sc, ac, CREAM, stroke=5)
        if ae > 0: _paste_pop(cv, sl, ef, s_cy, elh, se, ae, (226,221,209), stroke=3)
        if logo_img is not None and i >= lstart:
            la = _smooth(min(1., (i-lstart)/max(1, int(frames*0.3))))
            ll = logo_img.copy(); ll.putalpha(ll.getchannel("A").point(lambda v, a=la: int(v*a)))
            cv = Image.alpha_composite(cv, ll)
        cv.save(f"{prefix}_{i:03d}.png")

# ---------------------------------------------------------------- intro/outro text cards
def _card_logo(path):
    """Optional centered logo for a full-screen card. All from the spec; no bundled asset."""
    if not (path and os.path.exists(path)): return None
    lg = Image.open(path).convert("RGBA"); MW = 360
    scl = MW/lg.width; mh = round(lg.height*scl)
    return lg.resize((MW, mh), Image.LANCZOS), MW, mh
def render_card_frames(seg, prefix):
    """Generic full-screen text card (intro 'hook' or 'outro'). Paper
    background, centered title + subtitle (+ optional tagline / CTA for outro),
    fade-in, an accent divider, and an optional spec-supplied logo image.
    Every string comes from the spec — there is no built-in branding."""
    n = round(seg["dur"]*FPS)
    logo = _card_logo(seg.get("logo"))
    def place_logo(cv):
        if logo: cv.alpha_composite(logo[0], ((W-logo[1])//2, 250))
    if seg["style"] == "hook":
        title, sub = seg.get("title",""), seg.get("subtitle","")
        tf = vfont(80,"black"); sf = vfont(42,"regular")
        td = ImageDraw.Draw(Image.new("RGBA",(W,H))); tl, sl = [], []
        for p in title.split("\n"): tl += wrap(td, p, tf, W-130)
        for p in sub.split("\n"): sl += wrap(td, p, sf, W-130)
        for i in range(n):
            cv = Image.new("RGBA",(W,H), PAPER+(255,)); place_logo(cv)
            ac = _smooth(max(0, i-int(n*REVEAL_HOLD))/max(1,int(n*0.20)))
            ae = _smooth(max(0, i-int(n*(REVEAL_HOLD+0.10)))/max(1,int(n*0.20)))
            if ac > 0: _paste_pop(cv, tl, tf, 1010, 112, 1.12-0.12*ac, ac, NAVY, stroke=0)
            if ae > 0: _paste_pop(cv, sl, sf, 1230, 60, 1.10-0.10*ae, ae, NAVY, stroke=0)
            cv.convert("RGB").save(f"{prefix}_{i:03d}.png")
    else:  # outro
        title = seg.get("title",""); sub = seg.get("subtitle","")
        tag = seg.get("tagline",""); cta = seg.get("cta","")
        bf = vfont(84,"black"); tf = vfont(40,"regular"); ef = vfont(34,"regular"); cf2 = vfont(34,"regular")
        for i in range(n):
            cv = Image.new("RGBA",(W,H), PAPER+(255,)); place_logo(cv)
            d = ImageDraw.Draw(cv); fa = _smooth(max(0, i-int(n*REVEAL_HOLD))/max(1,int(n*0.3)))
            if fa > 0:
                A = int(255*fa)
                if title:
                    w = d.textlength(title, font=bf); d.text(((W-w)/2, 940), title, font=bf, fill=NAVY+(A,))
                    d.line([(W/2-70,1050),(W/2+70,1050)], fill=GOLD+(int(230*fa),), width=3)
                if sub:
                    w = d.textlength(sub, font=tf); d.text(((W-w)/2, 1080), sub, font=tf, fill=NAVY+(int(210*fa),))
                if tag:
                    w = d.textlength(tag, font=ef); d.text(((W-w)/2, 1150), tag, font=ef, fill=NAVY+(int(150*fa),))
                if cta:
                    w = d.textlength(cta, font=cf2); d.text(((W-w)/2, 1560), cta, font=cf2, fill=GOLD+(int(230*fa),))
            cv.convert("RGB").save(f"{prefix}_{i:03d}.png")
    return n

# ---------------------------------------------------------------- encoding
BT709 = ["-colorspace","bt709","-color_primaries","bt709","-color_trc","bt709","-color_range","tv",
         "-x264-params","colorprim=bt709:transfer=bt709:colormatrix=bt709"]
def prep_filter(mode):
    if mode == "cover": return f"scale={BW}:{BH}:force_original_aspect_ratio=increase,crop={BW}:{BH}"
    if mode == "fit": return f"scale={BW}:{BH}:force_original_aspect_ratio=decrease,pad={BW}:{BH}:(ow-iw)/2:(oh-ih)/2:color={DARKHEX}"
    return f"scale={BW}:{BH}"
def zoom_expr(motion, frames):
    f = max(2, frames); cx, cy = "'iw/2-(iw/zoom/2)'","'ih/2-(ih/zoom/2)'"
    if motion == "in":  return "'min(1.0+%.6f*on,1.12)'"%(0.12/(f-1)), cx, cy
    if motion == "out": return "'max(1.12-%.6f*on,1.0)'"%(0.12/(f-1)), cx, cy
    if motion == "panL":return "'1.10'","'(iw-iw/zoom)*on/%d'"%(f-1), cy
    if motion == "punchin":
        pf = max(2, int(0.16*f))
        return "'min(1.16, if(lt(on,%d), 1.16-0.16*on/%d, 1.0+%.6f*(on-%d)))'"%(pf,pf,0.06/(f-pf),pf), cx, cy
    return "'1.0'", cx, cy
def _enc(fc, inputs, out, frames):
    subprocess.run(["ffmpeg","-y",*inputs,"-filter_complex",fc,"-map","[v]","-frames:v",str(frames),
        "-r",str(FPS),"-c:v","libx264","-preset","medium","-crf","19",*BT709,"-pix_fmt","yuv420p",out],
        check=True, capture_output=True)
def build_kenburns(seg, ovp, out):
    fr = round(seg["dur"]*FPS); z,x,y = zoom_expr(seg["motion"], fr)
    fc = (f"[0:v]{prep_filter(seg['mode'])},zoompan=z={z}:x={x}:y={y}:d={fr}:s={W}x{H}:fps={FPS},setsar=1[bg];"
          f"[bg][1:v]overlay=0:0,format=yuv420p[v]")
    _enc(fc, ["-i",seg["src"],"-framerate",str(FPS),"-i",f"{ovp}_%03d.png"], out, fr)
def build_clip(seg, ovp, out):
    fr = round(seg["dur"]*FPS); ss = seg.get("clip_ss",0.0)
    cliplen = ffprobe_dur(seg["clip"]); avail = max(0.1, cliplen - ss)
    if seg["dur"] > avail + 0.05:          # narration longer than clip -> setpts stretch to fill (good for held/gaze shots)
        factor = seg["dur"]/avail; in_t = avail
    else:
        factor = 1.0; in_t = seg["dur"]
    sp = f"setpts={factor:.4f}*PTS," if abs(factor-1.0) > 1e-3 else ""
    fc = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},{sp}fps={FPS},setsar=1,setpts=PTS-STARTPTS[bg];"
          f"[bg][1:v]overlay=0:0,format=yuv420p[v]")
    _enc(fc, ["-ss",f"{ss}","-t",f"{in_t}","-i",seg["clip"],"-framerate",str(FPS),"-i",f"{ovp}_%03d.png"], out, fr)
def build_card(seg, out):
    prefix = f"{seg['tmp']}/{seg['key']}"; render_card_frames(seg, prefix)
    subprocess.run(["ffmpeg","-y","-framerate",str(FPS),"-i",f"{prefix}_%03d.png","-r",str(FPS),
        "-c:v","libx264","-preset","medium","-crf","19",*BT709,"-pix_fmt","yuv420p",out], check=True, capture_output=True)

def assemble(seg_files, durs, xf, total, master):
    inputs = []
    for f in seg_files: inputs += ["-i", f]
    inputs += ["-f","lavfi","-t",f"{total:.2f}","-i","anullsrc=r=44100:cl=stereo"]
    chain = []; off = durs[0]-xf[0][1]; prev = "0"
    for k in range(len(seg_files)-1):
        trans, td = xf[k]; lbl = f"x{k+1}"
        chain.append(f"[{prev}][{k+1}]xfade=transition={trans}:duration={td}:offset={off:.3f}[{lbl}]")
        prev = lbl
        if k+1 < len(seg_files)-1: off += durs[k+1]-xf[k+1][1]
    grade = "eq=contrast=1.04:saturation=1.03,vignette=PI/7,format=yuv420p"
    fc = ";".join(chain) + f";[{prev}]{grade}[v]"; na = len(seg_files)
    subprocess.run(["ffmpeg","-y",*inputs,"-filter_complex",fc,"-map","[v]","-map",f"{na}:a",
        "-r",str(FPS),"-c:v","libx264","-preset","slow","-crf","19",*BT709,"-pix_fmt","yuv420p",
        "-c:a","aac","-shortest","-movflags","+faststart", master], check=True, capture_output=True)
def mux_music(master, final, total, music, start):
    if music and os.path.exists(music):
        af = f"afade=t=in:d=0.3,afade=t=out:st={max(0.4, total-2.0):.2f}:d=2.0,volume=0.9"
        subprocess.run(["ffmpeg","-y","-i",master,"-ss",str(start),"-i",music,"-map","0:v","-map","1:a",
            "-t",f"{total:.3f}","-af",af,"-c:v","copy","-c:a","aac","-b:a","192k","-movflags","+faststart", final], check=True, capture_output=True)
    else:
        subprocess.run(["ffmpeg","-y","-i",master,"-c","copy","-movflags","+faststart", final], check=True, capture_output=True)

# ---------------------------------------------------------------- BGM under narration
# Flat ducking (the legacy path) lowers EVERY frequency of the BGM by the same amount. But speech is understood
# in roughly the 500 Hz - 3 kHz band, so a BGM that is only "somewhat quieter" overall can still be as loud as
# the narrator exactly where it matters — worst for older viewers. "Voice carve" instead splits the BGM into
# low / mid / high with a 4th-order Linkwitz-Riley crossover, compresses the MID band hard against the narration
# (sidechain) and the low/high bands only lightly, so the bed keeps its warmth and air but leaves the voice band
# clear. The BGM is delayed 30 ms so the compressor is already closing when a syllable starts (lookahead).
# Default ON (spec: music.carve = false -> legacy flat ducking, where bgm_ducking_db applies; true or a dict of
# overrides of CARVE_DEFAULTS). Measure the effect on your own render with scripts/measure_voice_band.py.
BED_GAIN_DB = 20 * math.log10(0.85)      # the starter's fixed bed level (~ -1.4 dB); override with music.gain_db
CARVE_DEFAULTS = dict(lo_hz=250, hi_hz=4200, mid_thr=0.02, mid_ratio=12, mid_att=6, mid_rel=380,
                      edge_thr=0.05, edge_ratio=1.5, edge_att=20, edge_rel=350, lookahead_ms=30)
CARVE_DEFAULT_ON = True

def carve_params(carve):
    c = dict(CARVE_DEFAULTS)
    if isinstance(carve, dict):
        bad = sorted(set(carve) - set(CARVE_DEFAULTS))
        if bad:
            raise RuntimeError(f"music.carve: unknown parameter(s) {bad}; allowed: {sorted(CARVE_DEFAULTS)}")
        c.update(carve)
    return c

def music_carve_setting(spec):
    """spec -> None (carve off, legacy flat ducking) | True | dict (on). Omitted/null = CARVE_DEFAULT_ON; false = off."""
    m = spec.get("music") if isinstance(spec.get("music"), dict) else {}
    v = m.get("carve")
    if v is None:
        v = CARVE_DEFAULT_ON
    return None if v is False else v

def carve_bed_filters(bg_in, keys, g, total, carve, out="duckbg"):
    """BGM from `bg_in` -> static gain + tail fade + lookahead + 3-band split + per-band sidechain compression -> [out].
    `keys` are three already-split copies of the narration used as sidechain inputs."""
    c = carve_params(carve)
    la = f"adelay={c['lookahead_ms']}|{c['lookahead_ms']}," if c["lookahead_ms"] else ""
    k0, k1, k2 = keys
    return (f"{bg_in}volume={g:.2f}dB,afade=t=out:st={max(0.4, total - 2.0):.2f}:d=2.0,{la}"
            f"acrossover=split={c['lo_hz']} {c['hi_hz']}:order=4th[lo][mid][hi];"
            f"[lo]{k0}sidechaincompress=threshold={c['edge_thr']}:ratio={c['edge_ratio']}:attack={c['edge_att']}:release={c['edge_rel']}[lod];"
            f"[mid]{k1}sidechaincompress=threshold={c['mid_thr']}:ratio={c['mid_ratio']}:attack={c['mid_att']}:release={c['mid_rel']}[midd];"
            f"[hi]{k2}sidechaincompress=threshold={c['edge_thr']}:ratio={c['edge_ratio']}:attack={c['edge_att']}:release={c['edge_rel']}[hid];"
            f"[lod][midd][hid]amix=inputs=3:duration=longest:normalize=0[{out}]")

def narration_bed_graph(total, duck_db=-12, gain_db=None, carve=None):
    """Filter graph over input 1 = BGM and input 2 = narration; leaves [duckbg] (ducked BGM) and [nmix] (narration).
    Shared by mux_narration and scripts/measure_voice_band.py so the measurement uses the production mix."""
    if carve is not None and carve is not False:
        g = BED_GAIN_DB if gain_db is None else float(gain_db)
        return ("[2:a]asplit=4[k0][k1][k2][nmix];"
                + carve_bed_filters("[1:a]", ["[k0]", "[k1]", "[k2]"], g, total, carve))
    duck_ratio = max(2, min(20, int(10 ** (abs(duck_db) / 20.0))))   # -12 dB -> ratio 3
    vol = "0.85" if gain_db is None else f"{float(gain_db):.2f}dB"
    return ("[2:a]asplit=2[nsc][nmix];"
            f"[1:a]volume={vol},afade=t=out:st={max(0.4, total - 2.0):.2f}:d=2.0[bg];"
            f"[bg][nsc]sidechaincompress=threshold=0.05:ratio={duck_ratio}:attack=20:release=350[duckbg]")

def mux_narration(master, final, total, music, start, narration, duck_db=-12, gain_db=None, carve=None):
    """Narration is the lead track; the BGM sits under it and is pushed down by the narration via sidechain
    compression — flat (carve=None, legacy) or per-band voice carve (see above)."""
    if music and os.path.exists(music):
        # 0=video(+silent track) · 1=BGM(cut from start) · 2=narration
        vin = ["-i", master, "-ss", str(start), "-i", music, "-i", narration]
        fc = (narration_bed_graph(total, duck_db, gain_db, carve)
              + ";[duckbg][nmix]amix=inputs=2:duration=longest:dropout_transition=0.5:normalize=0[aout]")
        subprocess.run(["ffmpeg","-y",*vin,"-filter_complex",fc,"-map","0:v","-map","[aout]",
            "-t",f"{total:.3f}","-c:v","copy","-c:a","aac","-b:a","192k","-movflags","+faststart", final],
            check=True, capture_output=True)
    else:
        subprocess.run(["ffmpeg","-y","-i",master,"-i",narration,"-map","0:v","-map","1:a",
            "-t",f"{total:.3f}","-c:v","copy","-c:a","aac","-b:a","192k","-movflags","+faststart", final],
            check=True, capture_output=True)

# ---------------------------------------------------------------- asset resolver (generate if missing, reuse if present)
def run_node(script, args, label):
    print(f"  > {label} ...")
    subprocess.run(["node", script, *args], check=True)
def run_py(script, args, label):
    print(f"  > {label} ...")
    subprocess.run([sys.executable, script, *args], check=True)
def resolve_image(shot, tmp):
    img = shot.get("image", {})
    if img.get("src"): return img["src"]
    if img.get("gen"):
        out = f"{tmp}/img_{shot['key']}.png"
        if not os.path.exists(out):
            run_node(GEN_IMAGE, ["--prompt", img["gen"], "--out", out,
                     "--size", img.get("size","1024x1536"), "--quality","high"], f"gen_image {shot['key']}")
        return out
    return None
def resolve_clip(shot, img_path, tmp):
    if shot.get("clip"): return shot["clip"]
    sd = shot.get("seedance")
    if not sd: return None
    if not sd.get("face_free", False):
        print(f"  ! {shot['key']}: seedance.face_free=false (has a face; blocked by the portrait filter) -> fall back to Ken Burns"); return None
    if not img_path: print(f"  ! {shot['key']}: no first frame image -> skip image-to-video"); return None
    out = f"{tmp}/clip_{shot['key']}.mp4"
    if not os.path.exists(out):
        crop = f"{tmp}/seed_{shot['key']}.jpg"; _cover_jpg(img_path, crop, 720, 1280)
        pf = f"{tmp}/seed_{shot['key']}.prompt.txt"; open(pf,"w").write(sd["prompt"])
        run_node(GEN_VIDEO, ["--model","bytedance/seedance-2.5/image-to-video","--image-file",crop,
                 "--prompt-file",pf,"--resolution","720p","--duration","4","--aspect-ratio","auto",
                 "--generate-audio","false","--out",out], f"gen_video(i2v) {shot['key']}")
    return out
def resolve_music(music, tmp):
    if not music: return None, 0.0
    start = music.get("start", 0.0)
    if music.get("file") and os.path.exists(music["file"]): return music["file"], start
    if music.get("prompt"):
        out = f"{tmp}/bgm.mp3"
        if not os.path.exists(out):
            pf = f"{tmp}/bgm.prompt.txt"; open(pf,"w").write(music["prompt"])
            args = ["--prompt-file",pf,"--out",out]
            if music.get("vocals"): args.append("--vocals")
            run_node(GEN_MUSIC, args, "gen_music")
        return out, start
    return None, 0.0
def resolve_narration(nar, tmp):
    """A single whole-track narration -> gen_voice -> (path, dur seconds)."""
    if not nar: return None, 0.0
    out = f"{tmp}/narration.mp3"
    if not os.path.exists(out):
        tf = nar.get("text_file")
        if not tf and nar.get("text"):
            tf = f"{tmp}/narration.txt"; open(tf, "w", encoding="utf-8").write(nar["text"])
        if not tf: return None, 0.0
        a = ["--text-file", tf, "--voice-id", nar.get("voice_id", "audiobook_male_2"),
             "--speed", str(nar.get("speed", 1.0)), "--out", out]
        if nar.get("emotion"): a += ["--emotion", nar["emotion"]]
        if nar.get("pitch") is not None: a += ["--pitch", str(nar["pitch"])]
        run_node(GEN_VOICE, a, "gen_voice")
    d = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=noprint_wrappers=1:nokey=1", out], capture_output=True, text=True)
    return out, float(d.stdout.strip() or 0)
def ffprobe_dur(path):
    d = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=noprint_wrappers=1:nokey=1", path], capture_output=True, text=True)
    try: return float(d.stdout.strip())
    except Exception: return 0.0
def resolve_shot_voice(shot, vcfg, tmp):
    """Per-shot narration: each shot's `say` -> its own gen_voice clip -> (path, dur).
    voice_id / speed / emotion / pitch may be overridden per shot over the top-level voice."""
    say = shot.get("say")
    if not say: return None, 0.0
    out = f"{tmp}/say_{shot['key']}.mp3"
    if not os.path.exists(out):
        tf = f"{tmp}/say_{shot['key']}.txt"; open(tf, "w", encoding="utf-8").write(say)
        vid = shot.get("voice_id", vcfg.get("voice_id", "audiobook_male_2"))
        a = ["--text-file", tf, "--voice-id", vid,
             "--speed", str(shot.get("speed", vcfg.get("speed", 1.0))), "--out", out]
        emo = shot.get("emotion", vcfg.get("emotion"))
        if emo: a += ["--emotion", emo]
        pit = shot.get("pitch", vcfg.get("pitch"))
        if pit is not None: a += ["--pitch", str(pit)]
        run_node(GEN_VOICE, a, f"gen_voice {shot['key']}({vid})")
    return out, ffprobe_dur(out)
NUMBER_CARD_DEFAULT_ANIMATE = "splitflap"    # a `number_card` without `animate` uses the split-flap reveal; "static" opts out
def anchor_word_time(shot, nc, tmp, vcfg):
    """number_card.at_word -> (start of that word on THIS shot's timeline in seconds | None, voice duration).
    Shot timeline = voice start (say_lead) + the word's start inside the voice clip. Needs per-shot narration (`say`).
    Alignment tooling missing / clip not alignable -> (None, ...) so the caller falls back to the default timing;
    a word that is not in the script raises AnchorSpecError (a spec mistake)."""
    if not shot.get("say"):
        raise RuntimeError(f"{shot.get('key')}: number_card.at_word needs a per-shot narration line (`say`) on the same shot")
    voice, vd = resolve_shot_voice(shot, vcfg or {}, tmp)
    import word_anchor as WA               # lives next to this file; heavy imports only happen if at_word is used
    say = shot["say"]
    try:
        data = WA.align_chars(voice, say, tmp, nc.get("at_lang", vcfg.get("language", "en") if vcfg else "en"))
        t_word, _ = WA.find_word(say, data["pred"], nc["at_word"], nc.get("at_word_nth", 1))
    except WA.AlignmentUnavailable as e:
        print(f"  ! {shot['key']}: at_word alignment unavailable ({e}); using the default flip timing")
        return None, vd
    lead = shot.get("say_lead", 0.12)
    print(f"  at_word {nc['at_word']!r} @{shot['key']}: {t_word:.2f}s into the voice -> {lead + t_word:.2f}s into the shot "
          f"({'cached' if data['cached'] else 'freshly aligned'}, coverage {data['coverage']})")
    return lead + t_word, vd

def resolve_number_card(shot, tmp, vcfg=None):
    """shot.number_card -> shot["clip"] (split-flap mp4) or shot["image"]["src"] (static PNG); the normal
    resolve_image/resolve_clip/build_* path then handles it like any other shot. Rendered locally with PIL + ffmpeg
    (zero API cost) on every run, so it always matches the current spec.
    at_word (split-flap only): the last digit locks in at the moment the narrator starts that word
    (at_mode "settle", default) or the flip starts there ("start"). Falls back to default timing if alignment is unavailable."""
    nc = shot.get("number_card")
    if not nc:
        return
    if shot.get("image") or shot.get("clip"):
        raise RuntimeError(f"{shot.get('key')}: number_card cannot be combined with a hand-written image/clip on the same shot")
    animate = nc.get("animate", NUMBER_CARD_DEFAULT_ANIMATE)
    if animate not in ("splitflap", "static"):
        raise RuntimeError(f"{shot.get('key')}: number_card.animate must be splitflap|static, got {animate!r}")
    if nc.get("at_word") and animate != "splitflap":
        print(f"  ! {shot.get('key')}: at_word only applies to the splitflap animation (static has nothing to time); ignored")
    label, number = nc.get("label", ""), str(nc["number"])
    unit, source = nc.get("unit", ""), nc.get("source", "")
    if animate == "splitflap":
        out = f"{tmp}/numcard_{shot['key']}.mp4"
        # Shot length = its voice clip + tail pad in per-shot mode (the voice is cached, so this costs nothing extra
        # later); otherwise the shot's declared dur.
        vd = resolve_shot_voice(shot, vcfg or {}, tmp)[1] if shot.get("say") else 0.0
        dur_hint = (vd + shot.get("pad", 0.5)) if vd else (shot.get("dur") or 2.5)
        hold_end = max(dur_hint, 2.0) + 1.0                      # the clip must outlast the shot; build_clip trims it
        # The flip must finish on the exact figure well inside the shot: cap flip time at 60% of the shot (1-3 s).
        timing = ["--max-anim", f"{min(3.0, max(1.0, dur_hint * 0.6)):.2f}"]
        if nc.get("at_word"):
            mode = nc.get("at_mode", "settle")
            if mode not in ("settle", "start"):      # validate before the (slow) alignment
                raise RuntimeError(f"{shot.get('key')}: number_card.at_mode must be settle|start, got {mode!r}")
            t_seg, vd = anchor_word_time(shot, nc, tmp, vcfg)
            if t_seg is not None:
                timing = ["--settle-at" if mode == "settle" else "--hold-start", f"{t_seg:.3f}"]
                need = vd + shot.get("say_lead", 0.12) + shot.get("pad", 0.5)
                hold_end = max(need - t_seg, 1.0) + 1.5
        run_py(GEN_SPLITFLAP_CARD, [out, "--label", label, "--number", number, "--unit", unit, "--source", source,
               "--num-size", str(nc.get("num_size", 260)), "--hold-end", f"{hold_end:.3f}", *timing],
               f"splitflap {shot['key']}")
        shot["clip"] = out
    else:
        out = f"{tmp}/numcard_{shot['key']}.png"
        run_py(GEN_NUMBER_CARD, ["--out", out, "--label", label, "--number", number, "--unit", unit,
               "--source", source, "--num-size", str(nc.get("num_size", 300))], f"number_card {shot['key']}")
        shot["image"] = {"src": out}
def build_shot_narration(segs, starts, sfx, tmp):
    """Position each shot's voice clip on the finished timeline by absolute
    offset (adelay), layer in the SFX, and mix into a single narration track
    that lines up with the picture."""
    inputs, filt, labels, idx = [], [], [], 0
    for k, s in enumerate(segs):
        if s.get("voice"):
            inputs += ["-i", s["voice"]]
            delay = int(max(0.0, starts[k] + s.get("say_lead", 0.12)) * 1000)
            filt.append(f"[{idx}:a]adelay={delay}|{delay},apad=pad_dur=0.06[n{idx}]")
            labels.append(f"[n{idx}]"); idx += 1
    for fx in sfx:
        inputs += ["-i", fx["file"]]
        delay = int(max(0.0, fx["at"]) * 1000)
        filt.append(f"[{idx}:a]volume={fx.get('vol', 0.8)},adelay={delay}|{delay}[n{idx}]")
        labels.append(f"[n{idx}]"); idx += 1
    if not labels: return None
    filt.append("".join(labels) + f"amix=inputs={len(labels)}:duration=longest:normalize=0[nar]")
    out = f"{tmp}/narration_mix.wav"
    subprocess.run(["ffmpeg","-y",*inputs,"-filter_complex",";".join(filt),"-map","[nar]", out],
                   check=True, capture_output=True)
    return out
def _cover_jpg(src, out, tw, th):
    im = Image.open(src).convert("RGB"); r = max(tw/im.width, th/im.height)
    im = im.resize((round(im.width*r), round(im.height*r)), Image.LANCZOS)
    x, y = (im.width-tw)//2, (im.height-th)//2; im.crop((x,y,x+tw,y+th)).save(out,"JPEG",quality=90)

# ---------------------------------------------------------------- publish package
def write_publish_md(spec, final):
    """After rendering, write a generic publish package <name>.publish.md
    (title candidates / description / tags / upload options). spec.publish
    overrides; defaults are derived from intro.title + narration.text."""
    pub = spec.get("publish", {}) or {}
    intro_title = (spec.get("intro", {}) or {}).get("title", "").replace("\n", " ")
    nar = (spec.get("narration") or {}).get("text", "")
    titles = pub.get("title") or ([intro_title] if intro_title else [spec["name"]])
    if isinstance(titles, str): titles = [titles]
    desc = pub.get("description") or (
        (nar + "\n\n" if nar else "") + "What do you think? Tell me in the comments.")
    hashtags = pub.get("hashtags", "#Shorts")
    tags = pub.get("tags", [])
    rows = [
        ("Type", pub.get("kind", "Shorts (vertical, <3min, #Shorts)")),
        ("Category", pub.get("category", "Education")),
        ("Language", pub.get("language", "English")),
        ("Subtitles", pub.get("subtitles", "Burned-in; optional SRT")),
        ("Made for kids", pub.get("made_for_kids", "No")),
        ("Visibility", pub.get("visibility", "Public (or unlisted preview)")),
        ("Playlist", pub.get("playlist", "")),
        ("Thumbnail", pub.get("thumbnail", "Auto from a frame")),
    ]
    L = [f"# Publish package · {spec['name']} ({os.path.basename(final)})", "", "## Title candidates"]
    L += [f"{i}. {t}" for i, t in enumerate(titles, 1)]
    L += ["", "## Description", "```", desc.rstrip(), "", hashtags, "```", ""]
    if tags:
        L += ["## Tags", "```", ", ".join(tags), "```", ""]
    L += ["## Upload options", "| Option | Value |", "|---|---|"] + [f"| {k} | {v} |" for k, v in rows]
    L += ["", "> Review anything before it goes public."]
    p = final.rsplit(".", 1)[0] + ".publish.md"
    open(p, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"  publish package -> {p}")

# ---------------------------------------------------------------- main
def main(spec_path):
    spec = json.load(open(spec_path, encoding="utf-8"))
    name = spec["name"]; tmp = f"tmp/videogen/spec-{name}"; os.makedirs(tmp, exist_ok=True)
    final = spec["out"]; os.makedirs(os.path.dirname(final) or ".", exist_ok=True)
    music, mstart = resolve_music(spec.get("music"), tmp)

    shots = spec["shots"]
    per_shot = any(sh.get("say") for sh in shots)     # per-shot mode: each shot's `say` is its own subtitle + voice (naturally aligned)
    vcfg = spec.get("voice") or spec.get("narration") or {}
    narration, ndur = (None, 0.0) if per_shot else resolve_narration(spec.get("narration"), tmp)

    segs = []
    intro = spec.get("intro")
    if intro and spec.get("brand_intro", True):   # brand_intro=false -> no intro card, shot 1 is the cold-open hook
        segs.append(dict(key="intro", mode="card", style="hook", dur=intro["dur"],
                         title=intro.get("title",""), subtitle=intro.get("subtitle",""),
                         logo=intro.get("logo"), tmp=tmp))
    for sh in shots:
        resolve_number_card(sh, tmp, vcfg)   # number_card -> sh['clip'] (split-flap) or sh['image'] (static)
        img = resolve_image(sh, tmp); clip = resolve_clip(sh, img, tmp)
        seg = dict(key=sh["key"], mode=sh.get("mode","cover"), style="lower",
                   dur=sh.get("dur", 0.0),
                   primary=sh.get("primary", sh.get("say","")), secondary=sh.get("secondary",""),
                   motion=sh.get("motion","in"), src=img, clip=clip,
                   clip_ss=sh.get("clip_ss",0.0), tmp=tmp)
        if per_shot:
            v, vd = resolve_shot_voice(sh, vcfg, tmp)
            if v:
                seg["voice"] = v; seg["vdur"] = vd
                seg["dur"] = round(vd + sh.get("pad", 0.5), 2)   # picture duration = voice duration + tail pad
                seg["say_lead"] = sh.get("say_lead", 0.12)
        segs.append(seg)

    o = spec.get("outro"); bo = spec.get("brand_outro", True)
    # optional corner branding config (logo image + CTA text) — all from the spec, no bundled asset
    end_logo_cfg = spec.get("end_logo") or (o if isinstance(o, dict) and (o.get("logo") or o.get("cta")) else None)
    if bo == "minimal":
        # minimal outro: no separate end card; fade the corner logo/CTA onto the last content shot
        for s in reversed(segs):
            if s["mode"] != "card":
                if end_logo_cfg: s["end_logo"] = end_logo_cfg
                break
    elif o and bo:
        segs.append(dict(key="outro", mode="card", style="outro", dur=o["dur"],
            title=o.get("title",""), subtitle=o.get("subtitle",""),
            tagline=o.get("tagline",""), cta=o.get("cta",""), logo=o.get("logo"), tmp=tmp))
    elif end_logo_cfg:
        # no outro card but a corner logo requested -> put it on the last content shot
        for s in reversed(segs):
            if s["mode"] != "card": s["end_logo"] = end_logo_cfg; break

    # whole-track narration mode: slow the still shots down to fit the narration
    # (per-shot mode already sizes each shot to its own voice clip, so skip)
    if ndur > 0 and not per_shot:
        brand_dur = sum(s["dur"] for s in segs if s["mode"] == "card")
        content = [s for s in segs if s["mode"] != "card"]
        flex = [s for s in content if not s.get("clip")]
        fixed_clip = sum(s["dur"] for s in content if s.get("clip"))
        cur = sum(s["dur"] for s in flex)
        if cur > 0:
            target = max(cur, ndur + 3.6 - brand_dur - fixed_clip)
            k = target / cur
            for s in flex: s["dur"] = round(s["dur"] * k, 2)
            print(f"  narration {ndur:.1f}s -> stills x{k:.2f} (clip fixed {fixed_clip:.1f}s, cards {brand_dur:.1f}s, total ~{sum(s['dur'] for s in segs):.1f}s)")

    xf = [list(t) for t in spec.get("transitions", DEFAULT_XF)]
    while len(xf) < len(segs)-1: xf += [list(t) for t in DEFAULT_XF]   # cycle the defaults if short
    xf = xf[:len(segs)-1]

    seg_files, durs = [], []
    for s in segs:
        out = f"{tmp}/seg_{s['key']}.mp4"
        if s["mode"] == "card":
            build_card(s, out)
        else:
            ovp = f"{tmp}/ov_{s['key']}"; make_overlay_seq(s["primary"], s["secondary"], ovp, round(s["dur"]*FPS), s.get("end_logo"))
            (build_clip if (s.get("clip") and os.path.exists(s["clip"])) else build_kenburns)(s, ovp, out)
        seg_files.append(out); durs.append(s["dur"]); print(f"  seg {s['key']:8s} {s['dur']}s ok")

    total = sum(durs) - sum(t[1] for t in xf)
    master = f"{tmp}/master.mp4"
    assemble(seg_files, durs, xf, total, master)

    if per_shot:   # position each shot's voice + SFX on the finished timeline, mix into one narration track
        starts = [0.0]
        for k in range(1, len(segs)):
            starts.append(starts[k-1] + durs[k-1] - xf[k-1][1])
        idx_of = {s["key"]: k for k, s in enumerate(segs)}
        sfx = []
        for fx in spec.get("sfx", []):
            k = idx_of.get(fx.get("at_shot"))
            if k is not None:
                sfx.append(dict(file=fx["file"], at=starts[k] + fx.get("offset", 0.0), vol=fx.get("vol", 0.8)))
        narration = build_shot_narration(segs, starts, sfx, tmp)

    if narration:
        duck = (spec.get("narration") or spec.get("voice") or {}).get("bgm_ducking_db", spec.get("bgm_ducking_db", -12))
        mcfg = spec.get("music") if isinstance(spec.get("music"), dict) else {}
        mux_narration(master, final, total, music, mstart, narration, duck, mcfg.get("gain_db"), music_carve_setting(spec))
    else:
        mux_music(master, final, total, music, mstart)
    print(f"\nRENDER CANDIDATE: {final}  (~{total:.1f}s){'  music:'+os.path.basename(music) if music else '  (silent)'}")
    write_publish_md(spec, final)
    subprocess.run(["ffprobe","-v","error","-show_entries",
        "stream=codec_type,width,height,pix_fmt,color_space,color_primaries:format=duration",
        "-of","default=noprint_wrappers=1", final])

if __name__ == "__main__":
    if len(sys.argv) < 2: print("usage: python3 scripts/make_short.py examples/example-spec.json"); sys.exit(2)
    main(sys.argv[1])
