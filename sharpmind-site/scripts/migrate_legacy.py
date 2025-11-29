# scripts/migrate_legacy.py
import re
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional

from scripts.utils import BASE_DIR, ensure, save_file

DEST_DIR = BASE_DIR / "content" / "en" / "posts"
IMG_DEST = BASE_DIR / "public" / "assets" / "legacy"

CANDIDATE_DIRS = [
    "content/en/posts",
    "posts",
    "build/en/posts",
    "blog",
]

MD_EXTS = {".md", ".markdown", ".mdx"}
HTML_EXTS = {".html", ".htm"}

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-{2,}", "-", text)
    return text[:120].strip("-")

def parse_frontmatter(md: str) -> Tuple[dict, str]:
    """Ritorna (frontmatter_dict, body_md). Se non presente, fm vuoto."""
    if md.startswith("---"):
        parts = md.split("\n---", 1)
        if len(parts) == 2:
            head = parts[0].strip("-\n")
            body = parts[1].lstrip("\n")
            fm = {}
            for line in head.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm[k.strip()] = v.strip().strip('"').strip("'")
            return fm, body
    return {}, md

def _clean(s: Optional[str]) -> str:
    """Sostituisce i doppi apici per evitare escape in YAML."""
    if not s:
        return ""
    return s.replace('"', "'").strip()

def build_frontmatter(title: str, subtitle: Optional[str], description: Optional[str], date_str: str, slug: str) -> str:
    safe_title = _clean(title)
    safe_subtitle = _clean(subtitle)
    safe_desc = _clean(description)
    lines = ["---"]
    lines.append(f'title: "{safe_title}"')
    if safe_subtitle:
        lines.append(f'subtitle: "{safe_subtitle}"')
    lines.append(f"date: {date_str}")
    lines.append(f"slug: {slug}")
    if safe_desc:
        lines.append(f'description: "{safe_desc}"')
    lines.append("lang: en")
    lines.append("tags: [ai, data, tech]")
    lines.append("---\n")
    return "\n".join(lines)

def infer_title_from_md(md: str) -> Optional[str]:
    for line in md.splitlines():
        if line.strip().startswith("#"):
            return line.lstrip("#").strip()
    return None

def html_to_md(html: str) -> str:
    # fallback molto semplice: conserva il testo base
    text = re.sub(r"<\s*br\s*/?>", "\n", html, flags=re.I)
    text = re.sub(r"</\s*p\s*>", "\n\n", text, flags=re.I)
    text = re.sub(r"<\s*h1\s*>", "# ", text, flags=re.I)
    text = re.sub(r"<\s*h2\s*>", "## ", text, flags=re.I)
    text = re.sub(r"<\s*h3\s*>", "### ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)  # rimuove il resto dei tag
    return re.sub(r"\n{3,}", "\n\n", text).strip()

IMG_MD_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
def rewrite_and_copy_images(md: str, legacy_root: Path) -> str:
    ensure(IMG_DEST)
    def _rep(m):
        url = m.group(1).strip()
        # lascia remote
        if re.match(r"^https?://", url):
            return m.group(0)
        # copia locale se esiste
        src = (legacy_root / url.lstrip("/")).resolve()
        if not src.exists():
            return m.group(0)
        target = IMG_DEST / src.name
        try:
            if src.is_file():
                shutil.copy2(src, target)
                return m.group(0).replace(url, f"/assets/legacy/{src.name}")
        except Exception:
            return m.group(0)
        return m.group(0)
    return IMG_MD_RE.sub(_rep, md)

def ensure_frontmatter(md: str, fallback_date: str) -> str:
    fm, body = parse_frontmatter(md)
    title = fm.get("title") or infer_title_from_md(body) or "Untitled"
    subtitle = fm.get("subtitle")
    description = fm.get("description")
    slug = fm.get("slug") or slugify(title)
    date = fm.get("date") or fallback_date
    new_fm = build_frontmatter(title, subtitle, description, date, slug)
    if not body.startswith("\n"):
        body = "\n" + body
    return new_fm + body.lstrip("\n")

def pick_sources(legacy_root: Path):
    found = []
    for rel in CANDIDATE_DIRS:
        p = (legacy_root / rel)
        if p.exists():
            found.append(p)
    if not found:
        for p in legacy_root.rglob("*"):
            if p.suffix.lower() in (MD_EXTS | HTML_EXTS):
                found.append(p.parent)
                break
    return list(dict.fromkeys(found))  # unique, order-preserving

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="Root del progetto legacy (es. ~/social_media_agent/blog_deploy)")
    args = ap.parse_args()

    legacy_root = Path(args.src).expanduser().resolve()
    if not legacy_root.exists():
        print(f"❌ Sorgente non trovata: {legacy_root}")
        sys.exit(1)

    sources = pick_sources(legacy_root)
    if not sources:
        print("❌ Nessuna directory candidata trovata (posts/md/html).")
        sys.exit(1)

    ensure(DEST_DIR)
    imported = 0
    skipped = 0
    today = datetime.utcnow().strftime("%Y-%m-%d")

    for src_dir in sources:
        for f in src_dir.rglob("*"):
            if not f.is_file():
                continue
            ext = f.suffix.lower()
            if ext not in (MD_EXTS | HTML_EXTS):
                continue

            try:
                raw = f.read_text(encoding="utf-8", errors="ignore")
                body_md = html_to_md(raw) if ext in HTML_EXTS else raw
                body_md = rewrite_and_copy_images(body_md, legacy_root)
                md = ensure_frontmatter(body_md, fallback_date=today)

                fm, _ = parse_frontmatter(md)
                title = fm.get("title", "Untitled")
                slug = fm.get("slug") or slugify(title)
                date = fm.get("date") or today

                out = DEST_DIR / f"{date}-{slug}.md"
                if out.exists():
                    alt = DEST_DIR / f"{date}-{slug}-2.md"
                    out = alt if not alt.exists() else None
                if out is None:
                    skipped += 1
                    continue

                save_file(out, md)
                imported += 1

            except Exception as e:
                print(f"⚠️  Skip {f}: {e}")
                skipped += 1

    print(f"✅ Import completato. Importati: {imported}, Skippati: {skipped}")
    print(f"📁 Destinazione: {DEST_DIR}")
    print("Suggerito: npm run build && npm run deploy")

if __name__ == "__main__":
    main()
