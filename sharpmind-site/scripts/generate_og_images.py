from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from textwrap import wrap
from .utils import BASE_DIR, parse_frontmatter, read_file, slugify

CONTENT_DIR = BASE_DIR / "content" / "en" / "posts"
OG_DIR      = BASE_DIR / "public"  / "assets" / "og"
OG_DIR.mkdir(parents=True, exist_ok=True)

def _pick_font(size: int = 72) -> ImageFont.FreeTypeFont:
    # Prova vari font comuni su macOS, poi fallback
    candidates = [
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def _text_wh(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont):
    # Pillow >=10: usa textbbox
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return right - left, bottom - top

def draw_card(path: Path, title: str):
    W, H = 1200, 630
    # gradiente semplice
    im = Image.new("RGB", (W, H))
    for y in range(H):
        c = int(59 + (139 - 59) * (y / H))  # da #3b00ff verso #8b5cf6
        im.paste((c, 0, 255), (0, y, W, y + 1))

    d = ImageDraw.Draw(im)
    font = _pick_font(72)

    # Wrapping del titolo
    lines = wrap(title, width=20)
    # calcola altezza totale
    line_hs = []
    max_w = 0
    for ln in lines[:5]:
        w, h = _text_wh(d, ln, font)
        line_hs.append((w, h))
        max_w = max(max_w, w)
    total_h = sum(h for _, h in line_hs) + (len(line_hs) - 1) * 10

    y = (H - total_h) // 2
    for (ln, (w, h)) in zip(lines[:5], line_hs):
        d.text(((W - w) // 2, y), ln, fill="white", font=font)
        y += h + 10

    im.save(path, "JPEG", quality=90, optimize=True)

def main():
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    for md in sorted(CONTENT_DIR.glob("*.md")):
        raw = read_file(md)
        meta, _ = parse_frontmatter(raw)
        title = meta.get("title") or md.stem
        slug = slugify(meta.get("slug") or md.stem.split(".", 1)[0])
        out  = OG_DIR / f"{slug}.jpg"
        if not out.exists():
            draw_card(out, title)
            print("🖼  created", out)
        else:
            print("✔ already exists", out)

if __name__ == "__main__":
    main()
