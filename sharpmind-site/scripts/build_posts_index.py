from pathlib import Path
from .utils import BASE_DIR, ensure, parse_frontmatter, md_to_html, excerpt
from .render_posts import pick_hero

POSTS_MD = BASE_DIR / "content" / "en" / "posts"
OUT_DIR  = BASE_DIR / "build" / "en" / "posts"

PAGE_HDR = """<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>All Insights — SharpMind</title>
<link rel="canonical" href="https://tanzitech.com/en/posts/">
<meta property="og:title" content="All Insights — SharpMind">
<meta property="og:description" content="All the latest SharpMind articles and playbooks.">
<link rel="stylesheet" href="/assets/style.css">
</head><body><main class="container">
<h1>All Insights</h1>
<div class="grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:18px;">
"""

PAGE_FTR = """</div></main></body></html>"""

def load(md_path: Path):
    raw = md_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(raw)
    title = meta.get("title") or md_path.stem
    slug  = md_path.stem
    seo   = meta.get("seo") or meta.get("description") or excerpt(body, 28)
    og    = pick_hero(slug, meta)
    return slug, title, seo, og

def build():
    ensure(OUT_DIR)
    cards = []
    for md in sorted(POSTS_MD.glob("*.md"), reverse=True):
        try:
            cards.append(load(md))
        except Exception as e:
            print(f"⚠️  Skip {md.name}: {e}")
    html = [PAGE_HDR]
    for slug, title, seo, og in cards:
        url = f"/en/posts/{slug}/"
        html.append(
            f'<a href="{url}" style="text-decoration:none;color:inherit;display:block">'
            f'  <img src="{og}" alt="{title}" style="width:100%;height:160px;object-fit:cover;border-radius:12px">'
            f'  <h3 style="margin:10px 0 4px">{title}</h3>'
            f'  <p class="small" style="opacity:.8">{seo}</p>'
            f'</a>'
        )
    html.append(PAGE_FTR)
    (OUT_DIR / "index.html").write_text("".join(html), encoding="utf-8")
    print(f"✔ Posts index → {OUT_DIR}/index.html, items={len(cards)}")

if __name__ == "__main__":
    build()
