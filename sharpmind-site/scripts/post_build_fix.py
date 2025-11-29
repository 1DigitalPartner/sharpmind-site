from pathlib import Path
import re, html

ROOT = Path("build/en/posts")
BASE = "https://tanzitech.com"

def _strip_html(s: str) -> str:
    s = re.sub(r'<script.*?</script>', '', s, flags=re.I|re.S)
    s = re.sub(r'<style.*?</style>',  '', s, flags=re.I|re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def _fix_one(h: str):
    changed, reasons = False, []

    # og:image / twitter:image → assoluti
    new, n = re.subn(r'(<meta[^>]+property="og:image"[^>]+content=")(/[^"]+)"',
                     r'\1' + BASE + r'\2"', h, flags=re.I)
    if n: reasons.append(f'og:image abs x{n}')
    h, changed = new, changed or n>0

    new, n = re.subn(r'(<meta[^>]+name="twitter:image"[^>]+content=")(/[^"]+)"',
                     r'\1' + BASE + r'\2"', h, flags=re.I)
    if n: reasons.append(f'twitter:image abs x{n}')
    h, changed = new, changed or n>0

    # og:description ripulita se contaminata
    m = re.search(r'(<meta[^>]+property="og:description"[^>]+content=")([^"]*)(")', h, flags=re.I)
    if m and re.search(r'(dataLayer|gtag\s*\()', html.unescape(m.group(2)), flags=re.I):
        body = re.search(r'<article[^>]*>(.*?)</article>', h, flags=re.I|re.S)
        text = _strip_html(body.group(1) if body else h)
        newdesc = html.escape(text[:180])
        h = h[:m.start(2)] + newdesc + h[m.end(2):]
        changed = True
        reasons.append('og:description cleaned')

    # Rimuovi GA ovunque
    patt = r'(window\s*\.\s*dataLayer\s*=.*?;|dataLayer\s*\.\s*push\([^)]*\)\s*;|gtag\s*\([^)]*\)\s*;?)'
    new, n = re.subn(patt, '', h, flags=re.I|re.S)
    if n: reasons.append(f'GA removed x{n}')
    h, changed = new, changed or n>0

    return h, changed, reasons

def main():
    if not ROOT.exists():
        print("Nessuna cartella build/en/posts trovata.")
        return
    total = touched = 0
    for idx in sorted(ROOT.glob("*/index.html")):
        total += 1
        raw = idx.read_text(encoding="utf-8")
        fixed, changed, reasons = _fix_one(raw)
        if changed:
            idx.write_text(fixed, encoding="utf-8")
            touched += 1
            print(f"✔ {idx.parent.name}: " + "; ".join(reasons))
    print(f"✓ post_build_fix: {touched}/{total} file aggiornati")

if __name__ == "__main__":
    main()
