from pathlib import Path
import re, html

BASE = Path(__file__).resolve().parent.parent
POSTS_DIR = BASE / "build" / "en" / "posts"
OG_DIRS = [BASE / "build" / "assets" / "og", BASE / "public" / "assets" / "og"]

SITE_ORIGIN = "https://tanzitech.com"

def pick_og(slug:str, title:str)->str:
    # rimuovi data iniziale se presente
    m = re.match(r'^\\d{4}-\\d{2}-\\d{2}-(.+)$', slug)
    base = m.group(1) if m else slug
    candidates = [
        f"{slug}.jpg", f"{base}.jpg",
        f"{base}.png", f"{base}.webp",
        "default-og.png"
    ]
    for name in candidates:
        for d in OG_DIRS:
            if (d / name).exists():
                return name
    return "default-og.png"

def ensure_meta_block(head_html:str, title:str, desc:str, slug:str, og_name:str)->str:
    og_abs = f"{SITE_ORIGIN}/assets/og/{og_name}"
    canon  = f"{SITE_ORIGIN}/en/posts/{slug}/"
    # se già presenti, non duplicare
    if 'property="og:image"' in head_html:
        return head_html
    block = f"""
    <meta property="og:type" content="article">
    <meta property="og:title" content="{html.escape(title)}">
    <meta property="og:description" content="{html.escape(desc)}">
    <meta property="og:url" content="{canon}">
    <meta property="og:image" content="{og_abs}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{html.escape(title)}">
    <meta name="twitter:description" content="{html.escape(desc)}">
    <meta name="twitter:image" content="{og_abs}">
    <link rel="canonical" href="{canon}">
    """
    # prova anche a inserire <title> se manca
    if "<title>" not in head_html:
        head_html = head_html.replace("<head>", f"<head>\n<title>{html.escape(title)} — SharpMind</title>")
    return head_html.replace("</head>", block + "\n</head>")

def inject_hero(body_html:str, title:str, og_name:str)->str:
    if 'class="hero"' in body_html:
        return body_html
    hero = (
        f'<figure class="hero" style="margin:16px 0 24px 0;">'
        f'<img src="/assets/og/{og_name}" alt="{html.escape(title)}" '
        f'style="width:100%;max-height:420px;object-fit:cover;border-radius:12px">'
        f'</figure>'
    )
    # dopo il primo <h1>, altrimenti subito dopo <body>
    m = re.search(r'(<h1[^>]*>.*?</h1>)', body_html, flags=re.IGNORECASE|re.DOTALL)
    if m:
        return body_html.replace(m.group(1), m.group(1) + "\n" + hero, 1)
    mb = re.search(r'<body[^>]*>', body_html, flags=re.IGNORECASE)
    if mb:
        idx = mb.end()
        return body_html[:idx] + "\n" + hero + body_html[idx:]
    return hero + body_html

def extract_title(html_text:str)->str:
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html_text, flags=re.IGNORECASE|re.DOTALL)
    if m:
        return re.sub(r'<[^>]+>', '', m.group(1)).strip()
    # fallback: prima riga significativa
    for line in html_text.splitlines():
        s=line.strip()
        if s: return re.sub(r'<[^>]+>', '', s)
    return "SharpMind Article"

def extract_desc(html_text:str)->str:
    # usa meta description se presente
    m = re.search(r'<meta\\s+name="description"\\s+content="([^"]*)"', html_text, flags=re.IGNORECASE)
    if m: return m.group(1).strip()
    # altrimenti prima <p> decente
    m = re.search(r'<p[^>]*>(.*?)</p>', html_text, flags=re.IGNORECASE|re.DOTALL)
    if m:
        t = re.sub(r'<[^>]+>', '', m.group(1))
        t = re.sub(r'\\s+', ' ', t).strip()
        return (t[:157] + '…') if len(t)>160 else t
    return "Premium insights by SharpMind."

def process_file(fpath:Path):
    html_text = fpath.read_text(encoding="utf-8")
    slug = fpath.parent.name  # .../posts/<slug>/index.html
    title = extract_title(html_text)
    desc  = extract_desc(html_text)
    og    = pick_og(slug, title)

    # head
    html_text = re.sub(
        r'(<head[^>]*>.*?</head>)',
        lambda m: ensure_meta_block(m.group(1), title, desc, slug, og),
        html_text, flags=re.IGNORECASE|re.DOTALL, count=1
    )
    # hero
    html_text = inject_hero(html_text, title, og)

    fpath.write_text(html_text, encoding="utf-8")

def main():
    count=0
    for idx in POSTS_DIR.glob("*/index.html"):
        process_file(idx); count+=1
    print(f"✔ post meta+hero patched: {count} → {POSTS_DIR}")

if __name__ == "__main__":
    main()
