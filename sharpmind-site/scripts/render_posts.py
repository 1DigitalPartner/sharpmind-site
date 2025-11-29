from __future__ import annotations
from pathlib import Path
from datetime import datetime
from .utils import BASE_DIR, ensure, read_file, save_file, slugify, parse_frontmatter, md_to_html, excerpt, today

POSTS_SRC = BASE_DIR / "content" / "en" / "posts"
OUT_DIR   = BASE_DIR / "build"   / "en" / "posts"
ASSETS    = "/assets"

def load_post(md_path: Path) -> dict:
    raw = read_file(md_path)
    meta, body = parse_frontmatter(raw)
    title = meta.get("title") or _first_heading(body) or md_path.stem.replace("-", " ").title()
    sub   = meta.get("subtitle", "")
    date_ = meta.get("date") or today()
    slug  = slugify(meta.get("slug") or md_path.stem)
    cover = meta.get("image") or f"{ASSETS}/og/default-og.png"
    seo   = meta.get("seo") or meta.get("description") or excerpt(body, 28)
    html  = md_to_html(body)
    return {
        "slug": slug, "title": title, "subtitle": sub, "date": date_,
        "cover": cover, "seo": seo, "html": html
    }

def _first_heading(body: str) -> str|None:
    for line in body.splitlines():
        line=line.strip()
        if line.startswith("#"):
            return line.lstrip("# ").strip()
    return None

def render_post_page(p: dict) -> str:
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{p['title']} — SharpMind</title>
<meta name="description" content="{p['seo']}"/>
<link rel="stylesheet" href="/assets/style.css">
<meta property="og:title" content="{p['title']}"/>
<meta property="og:description" content="{p['seo']}"/>
<meta property="og:image" content="{p['cover']}"/>
</head>
<body>
<header class="hero"><div class="hero-content">
  <h1>{p['title']}</h1>
  <p class="subtitle">{p['subtitle']}</p>
  <a href="/en/posts/" class="cta">← Back to Insights</a>
</div></header>
<main class="section">
  <img src="{p['cover']}" alt="" style="width:100%;max-width:980px;display:block;margin:0 auto 24px;border-radius:12px"/>
  <article class="post-body" style="max-width:980px;margin:0 auto;">{p['html']}</article>
</main>
<footer>© 2025 SharpMind — AI Insights & Analytics</footer>
</body></html>"""

def render_index(posts: list[dict]) -> str:
    cards = []
    for p in posts:
        cards.append(f"""
  <a class="card tool-card" href="/en/posts/{p['slug']}.html">
    <div class="tool-thumb t1" style="background-image:linear-gradient(135deg,#1d4ed8,#7c3aed);display:flex;align-items:flex-end;justify-content:flex-start;padding:14px;font-weight:800;">
      <span style="color:#fff;">{p['title'][:48]}</span>
    </div>
    <h3>{p['title']}</h3>
    <p>{p['seo']}</p>
    <span class="card-link">Read →</span>
  </a>
""")
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Latest Insights — SharpMind</title>
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<header class="hero"><div class="hero-content">
  <h1>Latest Insights</h1>
  <p class="subtitle">Premium, data-driven analysis. One post a day.</p>
</div></header>
<section class="cards" style="max-width:1200px;margin:32px auto">{''.join(cards)}</section>
<footer>© 2025 SharpMind — AI Insights & Analytics</footer>
</body></html>"""

def render_all() -> None:
    ensure(OUT_DIR)
    posts = []
    for md in sorted(POSTS_SRC.glob("*.md")):
        p = load_post(md)
        posts.append(p)
        html = render_post_page(p)
        save_file(OUT_DIR / f"{p['slug']}.html", html)
    # ordine per data (se presente) discendente
    posts.sort(key=lambda x: x.get("date","1970-01-01"), reverse=True)
    save_file(OUT_DIR / "index.html", render_index(posts))
