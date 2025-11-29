from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from .utils import ensure

# Font di sistema "SF Pro"/"Inter" possono non esserci ovunque: fallback
def _pick_font(size=56):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/SFNS.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/Library/Fonts/Arial.ttf"
    ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size=size)
        except Exception:
            continue
    return ImageFont.load_default()

def _gradient(w, h, c1=(59,0,255), c2=(139,92,246)):
    img = Image.new("RGB", (w, h), c1)
    top = Image.new("RGB", (w, h), c2)
    mask = Image.linear_gradient("L").resize((w, h))
    return Image.composite(top, img, mask)

def draw_title(img: Image.Image, title: str):
    draw = ImageDraw.Draw(img)
    W, H = img.size
    font = _pick_font(56)
    # wrap rudimentale
    words = title.split()
    lines, line = [], ""
    for w in words:
        test = (line + " " + w).strip()
        if draw.textlength(test, font=font) < W - 120:
            line = test
        else:
            lines.append(line)
            line = w
    if line: lines.append(line)
    y = H//2 - (len(lines)*64)//2
    for l in lines[:5]:
        draw.text((60, y), l, font=font, fill=(255,255,255))
        y += 64

def generate_pair(title: str, slug: str, out_dir: Path):
    og_path = out_dir / "assets" / "og" / f"{slug}.png"
    th_path = out_dir / "assets" / "thumbs" / f"{slug}.jpg"
    ensure(og_path.parent); ensure(th_path.parent)

    base = _gradient(1200, 630)
    draw_title(base, title or "SharpMind Insight")
    base.save(og_path, format="PNG", optimize=True)

    thumb = base.resize((800, 420))
    thumb.save(th_path, format="JPEG", quality=88, optimize=True)
    return str(og_path), str(th_path)
