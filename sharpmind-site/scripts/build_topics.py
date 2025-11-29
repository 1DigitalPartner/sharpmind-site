from pathlib import Path
from scripts.utils import parse_frontmatter, excerpt, slugify

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "content" / "en" / "posts"
OUT_DIR = ROOT / "build" / "en" / "topics"

PAGE_HDR = """<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><link rel="stylesheet" href="/assets/style.css">
<style>.wrap{{max-width:980px;margin:40px auto;padding:0 16px}}.card{{background:#fff;border-radius:14px;padding:16px;box-shadow:0 6px 16px rgba(0,0,0,.07);margin:12px 0}}</style>
</head><body><div class="wrap"><h1>{title}</h1>
"""
PAGE_FTR = "</div></body></html>"

def collect():
    tags = {}
    for p in POSTS.glob("*.md"):
        text = p.read_text(encoding="utf-8", errors="ignore")
        meta, body = parse_frontmatter(text)
        tgs = meta.get("tags") or []
        for t in tgs:
            tags.setdefault(t, []).append((p.stem, meta.get("title") or p.stem, excerpt(body, 40)))
    return tags

def build():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tags = collect()

    # index dei topic
    idx = [("All Topics", "/en/topics/")] + [(k, f"/en/topics/{slugify(k)}/") for k in sorted(tags.keys())]
    index_html = PAGE_HDR.format(title="Topics — SharpMind") + "<ul>" + "".join(
        f'<li><a href="{href}">{name}</a></li>' for name, href in idx[1:]
    ) + "</ul>" + PAGE_FTR
    (OUT_DIR / "index.html").write_text(index_html, encoding="utf-8")

    # pagine per singolo topic
    for tag, posts in tags.items():
        html = [PAGE_HDR.format(title=f"Topic: {tag}")]
        for slug, title, ex in posts:
            url = f"/en/posts/{slug}/"
            html.append(f'<div class="card"><a href="{url}"><b>{title}</b></a><p>{ex}</p></div>')
        html.append(PAGE_FTR)
        (OUT_DIR / slugify(tag) / "index.html").write_text("".join(html), encoding="utf-8")

    print(f"✔ topics built: {len(tags)} tags → {OUT_DIR}")

if __name__ == "__main__":
    build()
