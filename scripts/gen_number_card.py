#!/usr/bin/env python3
# Precise number / info card renderer (never let an image model draw digits —
# it garbles them). The PNG is fed to make_short.py as a shot background via
# image.src. Paper background + large accent number + ink label + small source
# credit. Content sits in the upper-middle; the lower band is left clear for
# make_short.py's subtitles.
#
# Usage:
#   python3 scripts/gen_number_card.py --out output/cards/depth.png \
#     --label "Deepest point" --number "11" --unit "km down" \
#     --source "NOAA" [--num-size 340]
import os, argparse
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
# ---- example palette — customize for your brand ----
PAPER = (245, 241, 232); NAVY = (18, 54, 94); GOLD = (167, 122, 45)
SUBTLE = (117, 110, 99)
# Serif font; the default is a neutral system serif. For CJK set VIDEOGEN_FONT
# to a font with CJK glyphs. Falls back to PIL's built-in font.
_FONT_CANDIDATES = [
    os.environ.get("VIDEOGEN_FONT", ""),
    "/System/Library/Fonts/Supplemental/Georgia.ttf",    # macOS
    "/Library/Fonts/Georgia.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",  # Linux
    "C:/Windows/Fonts/georgia.ttf",                      # Windows
]
_W = {"black": 0, "bold": 1, "light": 3, "regular": 6}
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
    w = d.textlength(txt, font=font); d.text(((W - w) / 2, y), txt, font=font, fill=fill); return w

def card(out, label, number, unit="", source="", num_size=300):
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    lf = vfont(48, "regular"); nf = vfont(num_size, "black")
    uf = vfont(60, "regular"); sf = vfont(30, "regular")
    cx = W / 2
    y = 500
    if label:
        _center(d, label, lf, y, NAVY); y += 96
    d.line([(cx - 64, y), (cx + 64, y)], fill=GOLD, width=3); y += 70
    # big number (accent color)
    nb = d.textbbox((0, 0), number, font=nf)
    nh = nb[3] - nb[1]
    _center(d, number, nf, y - nb[1], GOLD); y += nh + 40
    if unit:
        _center(d, unit, uf, y, NAVY); y += 96
    if source:
        _center(d, source, sf, 1300, SUBTLE)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    im.save(out)
    print("saved", out)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Render a precise number/info card PNG for make_short.py.")
    ap.add_argument("--out", required=True, help="output PNG path")
    ap.add_argument("--label", default="", help="small label above the number")
    ap.add_argument("--number", required=True, help="the exact figure to display (e.g. 11 or 75pct)")
    ap.add_argument("--unit", default="", help="unit / caption under the number")
    ap.add_argument("--source", default="", help="small source credit at the bottom")
    ap.add_argument("--num-size", type=int, default=300, help="point size of the big number")
    a = ap.parse_args()
    card(a.out, a.label, a.number, a.unit, a.source, a.num_size)
