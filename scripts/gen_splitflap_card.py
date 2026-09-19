#!/usr/bin/env python3
# Split-flap ("departure board") number card — an animated version of
# gen_number_card.py. Each digit rolls up 0 -> target and locks in, left to
# right; any non-digit character (unit, letter, symbol) flips once from a blank
# cassette; spaces stay as gaps. The exact figure is drawn locally with PIL —
# never by an image model, which garbles digits.
#
# Why bother: a static number card is the most reliable way to show a figure,
# but it is also the flattest beat in a short. An old mechanical flip-board
# rolling to a precise, modern number gives that beat some motion and contrast
# without spending a cent on generation.
#
# Output is an opaque full-frame libx264 mp4 (frames are piped from PIL into
# ffmpeg), so make_short.py can use it as a shot's `clip`. Usage:
#   python3 scripts/gen_splitflap_card.py output/cards/depth.mp4 \
#     --label "Deepest point" --number 10935 --unit "metres down" --source "NOAA"
#
# Safe for any input (this is the default renderer for `number_card`):
#   * a row wider than the canvas shrinks its font automatically
#     (--num-size is only an upper bound);
#   * --max-anim / --settle-at compress the flip so the card always lands on
#     the exact figure, however short the shot is — a card must never hold on
#     a half-flipped digit.
#
# Timing:
#   --hold-start S   still first frame for S seconds, then start flipping
#   --max-anim T     hold-start + flip time <= T (compress if longer)
#   --settle-at T    the LAST digit locks in at second T (start time is derived;
#                    the flip is compressed if it does not fit). Used by
#                    make_short.py's number_card.at_word to land the figure on a
#                    spoken word. Overrides --hold-start / --max-anim.
#
# Palette + font: example values — customize for your brand. The global grade in
# make_short.py is mild (contrast 1.04 / saturation 1.03), so colors here are
# used as-is. For CJK units/labels set VIDEOGEN_FONT to a font with those glyphs.
import argparse
import os
import subprocess

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
PAPER = (245, 241, 232)          # card background (same as gen_number_card.py)
NAVY = (18, 54, 94)              # label / unit ink
GOLD = (167, 122, 45)            # divider
SUBTLE = (117, 110, 99)          # source credit
CASING = (34, 28, 22)            # cassette body (warm near-black)
SEAM = (18, 14, 10)              # the hinge line across the middle
CASSETTE_GOLD = (214, 170, 92)   # digits on the cassette

SIDE_MARGIN = 0.08               # keep at least 8% of the canvas free on each side
MIN_SIZE = 40

_FONT_CANDIDATES = [
    os.environ.get("VIDEOGEN_FONT", ""),
    "/System/Library/Fonts/Supplemental/Georgia.ttf",    # macOS
    "/Library/Fonts/Georgia.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",  # Linux
    "C:/Windows/Fonts/georgia.ttf",                      # Windows
]
_W = {"black": 0, "bold": 1, "light": 3, "regular": 6}   # face index inside a .ttc; ignored for single-face fonts


def vfont(size, weight="black"):
    for path in _FONT_CANDIDATES:
        if not path or not os.path.exists(path):
            continue
        try:
            return ImageFont.truetype(path, size, index=_W.get(weight, 0))
        except Exception:
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _center(d, txt, font, y, fill):
    w = d.textlength(txt, font=font)
    d.text(((W - w) / 2, y), txt, font=font, fill=fill)
    return w


def render_cassette(font, char, cell_w, cell_h, radius):
    """One cassette: rounded dark body + centered gold glyph, transparent outside. A space is a blank cassette."""
    img = Image.new("RGBA", (cell_w, cell_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, cell_w - 1, cell_h - 1], radius=radius, fill=(*CASING, 255))
    if char.strip():
        bbox = d.textbbox((0, 0), char, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        d.text(((cell_w - tw) / 2 - bbox[0], (cell_h - th) / 2 - bbox[1]), char, font=font,
               fill=(*CASSETTE_GOLD, 255))
    return img


def _shade(img, amount):
    """Darken toward black as a flap turns edge-on (it stops catching light)."""
    if amount <= 0:
        return img
    black = Image.new("RGBA", img.size, (0, 0, 0, 255))
    r, g, b, _ = Image.blend(img.convert("RGBA"), black, amount).split()
    return Image.merge("RGBA", (r, g, b, img.split()[3]))   # keep the original alpha (outside the body stays transparent)


def flip_frame(imgs, old_ch, new_ch, cell_w, cell_h, phase):
    """One cassette flipping old_ch -> new_ch at phase 0..1. `imgs` maps char -> cassette image."""
    old_img, new_img = imgs[old_ch], imgs[new_ch]
    mid = cell_h // 2
    canvas = Image.new("RGBA", (cell_w, cell_h), (0, 0, 0, 0))
    if phase < 0.5:
        # top half: new glyph already underneath, old top flap folds down (hinged at the seam)
        canvas.paste(new_img.crop((0, 0, cell_w, mid)), (0, 0))
        scale = 1.0 - phase / 0.5
        flap_h = max(0, round(mid * scale))
        if flap_h > 0:
            flap = _shade(old_img.crop((0, 0, cell_w, mid)).resize((cell_w, flap_h)), (1.0 - scale) * 0.4)
            canvas.paste(flap, (0, mid - flap_h), flap)
        canvas.paste(old_img.crop((0, mid, cell_w, cell_h)), (0, mid))   # bottom half: still the old glyph
    else:
        canvas.paste(new_img.crop((0, 0, cell_w, mid)), (0, 0))          # top half has settled
        canvas.paste(new_img.crop((0, mid, cell_w, cell_h)), (0, mid))
        scale = 1.0 - (phase - 0.5) / 0.5
        flap_h = max(0, round((cell_h - mid) * scale))
        if flap_h > 0:
            flap = _shade(old_img.crop((0, mid, cell_w, cell_h)).resize((cell_w, flap_h)), (1.0 - scale) * 0.4)
            canvas.paste(flap, (0, mid), flap)
    ImageDraw.Draw(canvas).line([(0, mid), (cell_w, mid)], fill=(*SEAM, 255), width=2)
    return canvas


def plan_row(number, size):
    """Lay out one row of cassettes at a given font size. Each item is {"kind": "cell"|"gap", "w": width, "deck": [chars]}.
    Digits roll through '0'..target (deck), other characters flip once from blank, spaces are gaps.
    Returns (items, cell_h, gap, radius, row_w, font)."""
    font = vfont(size, "black")
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    digit_bb = probe.textbbox((0, 0), "0123456789", font=font)
    digit_w = max(probe.textbbox((0, 0), c, font=font)[2] for c in "0123456789")
    dig_cw = int(digit_w * 1.35)
    cell_h = int((digit_bb[3] - digit_bb[1]) * 1.55)
    for ch in set(number):
        if not ch.isdigit() and not ch.isspace():
            bb = probe.textbbox((0, 0), ch, font=font)
            cell_h = max(cell_h, int((bb[3] - bb[1]) * 1.35))
    radius = max(6, dig_cw // 10)
    gap = max(4, dig_cw // 14)
    items = []
    for ch in number:
        if ch.isspace():
            items.append({"kind": "gap", "w": int(dig_cw * 0.5)})
        elif ch.isdigit():
            items.append({"kind": "cell", "w": dig_cw, "deck": [str(k) for k in range(int(ch) + 1)]})
        else:
            bb = probe.textbbox((0, 0), ch, font=font)
            items.append({"kind": "cell", "w": max(int(dig_cw * 0.6), int(bb[2] * 1.35)), "deck": [" ", ch]})
    row_w = sum(it["w"] for it in items) + gap * max(0, len(items) - 1)
    return items, cell_h, gap, radius, row_w, font


def main():
    ap = argparse.ArgumentParser(description="Render a split-flap number card (animated) to an mp4 for make_short.py.")
    ap.add_argument("out", help="output .mp4")
    ap.add_argument("--label", default="", help="small label above the number")
    ap.add_argument("--number", required=True, help="the exact figure to show (digits roll; other characters flip once)")
    ap.add_argument("--unit", default="", help="unit / caption under the number")
    ap.add_argument("--source", default="", help="small source credit near the bottom")
    ap.add_argument("--num-size", type=int, default=260, help="font size upper bound; shrinks automatically if the row is too wide")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--flip-step", type=float, default=0.09, help="seconds for one flip")
    ap.add_argument("--stagger", type=float, default=0.16, help="delay between neighbouring digits starting to flip (seconds)")
    ap.add_argument("--hold-start", type=float, default=0.25, help="still first frame before flipping starts (seconds)")
    ap.add_argument("--hold-end", type=float, default=1.2, help="hold on the finished figure (seconds)")
    ap.add_argument("--max-anim", type=float, default=0.0,
                    help="cap on hold-start + flip time (seconds); longer flips are compressed proportionally. 0 = no cap")
    ap.add_argument("--settle-at", type=float, default=None,
                    help="second at which the LAST digit locks in; start time is derived and the flip is compressed if it "
                         "does not fit. Overrides --hold-start / --max-anim (used for word-anchored timing)")
    args = ap.parse_args()

    avail_w = W * (1 - 2 * SIDE_MARGIN)
    size = args.num_size
    for _ in range(4):
        items, cell_h, gap, radius, row_w, font = plan_row(args.number, size)
        if row_w <= avail_w or size <= MIN_SIZE:
            break
        size = max(MIN_SIZE, int(size * avail_w / row_w * 0.98))
    row_x0 = (W - row_w) / 2

    cells = [it for it in items if it["kind"] == "cell"]
    for it in cells:
        it["imgs"] = {c: render_cassette(font, c, it["w"], cell_h, radius) for c in set(it["deck"])}
    n = len(cells)

    flip_step, stagger = args.flip_step, args.stagger
    steps = [len(it["deck"]) - 1 for it in cells]

    def _max_finish(fs, st):
        # Only cassettes that actually flip count. A trailing 0 (1200, 3000) never flips — it only carries the stagger
        # delay — and must not be counted as "flip time", or --settle-at would land the last flip ~0.2 s early.
        return max((i * st + steps[i] * fs for i in range(n) if steps[i] > 0), default=0.0)

    max_finish = _max_finish(flip_step, stagger)
    hold_start = args.hold_start
    if args.settle_at is not None:
        room = max(0.05, args.settle_at - 0.05)        # keep at least 0.05 s of still first frame
        if max_finish > room and max_finish > 0:
            k = max(0.25, room / max_finish)
            flip_step = max(2.0 / args.fps, flip_step * k)   # a flip needs >= 2 frames to read as a flip
            stagger *= k
            max_finish = _max_finish(flip_step, stagger)
        hold_start = max(0.05, args.settle_at - max_finish)
    elif args.max_anim > 0 and args.hold_start + max_finish > args.max_anim and max_finish > 0:
        k = max(0.25, (args.max_anim - args.hold_start) / max_finish)
        flip_step = max(2.0 / args.fps, flip_step * k)
        stagger *= k
        max_finish = _max_finish(flip_step, stagger)
    delays = [i * stagger for i in range(n)]

    total_secs = hold_start + max_finish + args.hold_end
    total_frames = max(1, int(round(total_secs * args.fps)))

    lf, uf, sf = vfont(48, "regular"), vfont(60, "regular"), vfont(30, "regular")
    label_y = round(H * 0.26)
    line_y = label_y + 96
    row_y = line_y + 70
    unit_y = row_y + cell_h + max(24, round(H * 0.025))
    source_y = max(1300, unit_y + (90 if args.unit else 45))   # same spot as gen_number_card.py; the lower band stays free for subtitles

    xs, x = [], row_x0
    for it in items:
        xs.append(x)
        x += it["w"] + gap

    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-vcodec", "rawvideo", "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(args.fps), "-i", "-",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", "-preset", "medium", args.out]
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    for frame_idx in range(total_frames):
        t = min(max(0.0, frame_idx / args.fps - hold_start), max_finish)
        img = Image.new("RGB", (W, H), PAPER)
        d = ImageDraw.Draw(img)
        if args.label:
            _center(d, args.label, lf, label_y, NAVY)
        d.line([(W / 2 - 64, line_y), (W / 2 + 64, line_y)], fill=GOLD, width=3)

        ci = 0
        for it, x0 in zip(items, xs):
            if it["kind"] != "cell":
                continue
            deck, imgs = it["deck"], it["imgs"]
            local_t = t - delays[ci]
            if steps[ci] == 0 or local_t <= 0:
                cell_img = imgs[deck[0]]
            else:
                total_flip = steps[ci] * flip_step
                # Float tolerance: without it the last cassette can sit at phase ~0.999 forever and the whole final
                # hold would show a seam line across the middle of the digit.
                if local_t >= total_flip - 1e-6:
                    cell_img = imgs[deck[-1]]
                else:
                    step_idx = min(steps[ci] - 1, int(local_t // flip_step))
                    phase = (local_t % flip_step) / flip_step
                    cell_img = flip_frame(imgs, deck[step_idx], deck[step_idx + 1], it["w"], cell_h, phase)
            img.paste(cell_img, (int(x0), row_y), cell_img)
            ci += 1

        if args.unit:
            _center(d, args.unit, uf, unit_y, NAVY)
        if args.source:
            _center(d, args.source, sf, source_y, SUBTLE)
        p.stdin.write(img.tobytes())

    p.stdin.close()
    p.wait()
    print(f"[gen_splitflap_card] {total_frames} frames, {total_secs:.2f}s, {n} cassettes, font {size}px -> {args.out}")


if __name__ == "__main__":
    main()
