from pathlib import Path
from datetime import datetime, timezone
from scripts.utils import parse_frontmatter, excerpt
import json

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "content" / "en" / "posts"
OUT   = ROOT / "build" / "api" / "search.json"

def main():
    items=[]
    for p in sorted(POSTS.glob("*.md")):
        text = p.read_text(encoding="utf-8", errors="ignore")
        meta, body = parse_frontmatter(text)
        title = meta.get("title") or p.stem
        date  = meta.get("date") or p.stem[:10]
        tags  = meta.get("tags") or []
        url   = f"/en/posts/{p.stem.replace('.md','')}/"
        items.append({
            "title": title, "url": url, "date": date, "tags": tags,
            "excerpt": excerpt(body, 40)
        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"generated": datetime.now(timezone.utc).isoformat(), "items": items}, ensure_ascii=False), encoding="utf-8")
    print(f"✔ search index: {OUT} ({len(items)} items)")

if __name__ == "__main__":
    main()
