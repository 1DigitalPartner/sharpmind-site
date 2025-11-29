import os, io
from pathlib import Path
from base64 import b64decode
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI
from .utils import ensure_dir, POST_ASSETS_DIR

def _placeholder(size, title, subtitle, out_path: Path):
    ensure_dir(out_path.parent)
    w,h = size
    img = Image.new("RGB", size, "#0f0d1a")
    draw = ImageDraw.Draw(img)
    # semplice gradiente
    for y in range(h):
        shade = int(30 + 60*(y/h))
        draw.line([(0,y),(w,y)], fill=(39, 24, shade))
    # testo
    try:
        font_big = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", 48)
        font_small = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", 24)
    except:
        font_big = font_small = None
    draw.text((60, h*0.35), title[:60], fill="#ffffff", font=font_big, anchor=None)
    if subtitle:
        draw.text((60, h*0.35+60), subtitle[:80], fill="#cfc8ff", font=font_small, anchor=None)
    img.save(out_path, "JPEG", quality=88)

def _gen_with_openai(prompt: str, size_str: str, out_path: Path) -> bool:
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        r = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size=size_str,
            quality="high",
            style="vivid"
        )
        b64 = r.data[0].b64_json
        ensure_dir(out_path.parent)
        with open(out_path, "wb") as f:
            f.write(b64decode(b64))
        return True
    except Exception:
        return False

def generate_all(slug: str, title: str, subtitle: str = ""):
    """
    Crea hero (1280x720), og (1200x630), thumb (640x360) in build/assets/posts/
    Ritorna dict con path pubblici.
    """
    base = POST_ASSETS_DIR
    hero_path = base / f"{slug}-hero.jpg"
    og_path   = base / f"{slug}-og.jpg"
    th_path   = base / f"{slug}-thumb.jpg"

    prompt = (
        f"Photorealistic editorial hero image for a premium tech/AI article titled '{title}'. "
        f"Clean minimal composition, cinematic lighting, subtle gradient background, "
        f"no text, no watermark. Style: modern SaaS brand."
    )

    ok1 = _gen_with_openai(prompt, "1280x720", hero_path)
    ok2 = _gen_with_openai(prompt, "1200x630", og_path)
    ok3 = _gen_with_openai(prompt, "640x360", th_path)

    if not ok1: _placeholder((1280,720), title, subtitle, hero_path)
    if not ok2: _placeholder((1200,630), title, subtitle, og_path)
    if not ok3: _placeholder((640,360), title, subtitle, th_path)

    pub = {
        "hero": f"/assets/posts/{hero_path.name}",
        "og":   f"/assets/posts/{og_path.name}",
        "thumb":f"/assets/posts/{th_path.name}",
    }
    return pub
