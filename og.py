"""Share images (1200x630 PNG) for each page. Cached in og-cache/ so a build only draws new titles."""
import hashlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
CACHE = ROOT / "og-cache"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
REG = "/System/Library/Fonts/Supplemental/Arial.ttf"
NAVY, GOLD, WHITE, MUTED = "#12233f", "#f4b740", "#ffffff", "#c3cde0"


def _wrap(draw, text, font, width):
    lines, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if draw.textlength(trial, font=font) <= width:
            line = trial
        else:
            lines.append(line)
            line = word
    return lines + [line]


def make(slug, title, label):
    CACHE.mkdir(exist_ok=True)
    key = hashlib.sha1(f"v1|{title}|{label}".encode()).hexdigest()[:10]
    out = CACHE / f"{slug}-{key}.png"
    if out.exists():
        return out
    for old in CACHE.glob(f"{slug}-*.png"):
        if len(old.stem) == len(slug) + 11:
            old.unlink()
    img = Image.new("RGB", (1200, 630), NAVY)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((80, 70, 136, 126), radius=14, fill=GOLD)
    d.line((94, 100, 106, 112, 124, 86), fill=NAVY, width=7, joint="curve")
    d.text((156, 76), "Worth the Fee", font=ImageFont.truetype(BOLD, 40), fill=WHITE)
    d.text((80, 180), label.upper(), font=ImageFont.truetype(BOLD, 26), fill=GOLD)
    size = 68
    while size > 40:
        font = ImageFont.truetype(BOLD, size)
        lines = _wrap(d, title, font, 1040)
        if len(lines) * (size + 14) <= 300:
            break
        size -= 4
    y = 230
    for ln in lines:
        d.text((80, y), ln, font=font, fill=WHITE)
        y += size + 14
    d.text((80, 540), "itsworththefee.com  ·  sourced, dated, and honest about who should skip it",
           font=ImageFont.truetype(REG, 26), fill=MUTED)
    img.save(out, optimize=True)
    return out
