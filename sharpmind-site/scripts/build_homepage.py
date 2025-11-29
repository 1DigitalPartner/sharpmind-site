import json
from pathlib import Path
from .utils import BASE_DIR, ensure, save_file

TPL = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>SharpMind — AI Insights & Analytics</title>
  <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<header class="hero">
  <div class="hero-content">
    <h1>SharpMind</h1>
    <p class="subtitle">Strategic AI Insights. Premium. Data-Driven. Daily.</p>
    <a href="/en/posts/" class="cta">Explore Insights</a>
  </div>
</header>

<section class="section">
  <h2>AI Insights</h2>
  <p class="section-desc">Daily premium articles on AI, data, technology, business growth, and advanced analytics.</p>
</section>

<section class="grid">
{cards}
</section>

<section class="cards">
  <div class="card">
    <h3>Sharp Tools</h3>
    <ul>
      <li><a href="/tools/trend-analyzer/">AI Trend Analyzer</a></li>
      <li><a href="/tools/data-navigator/">Data Science Navigator</a></li>
      <li><a href="/tools/marketing-intel/">Marketing Intelligence Toolkit</a></li>
    </ul>
    <a class="card-link" href="/tools/">Open Tools →</a>
  </div>
</section>

<footer>© 2025 SharpMind — AI Insights & Analytics</footer>
</body>
</html>
"""

CARD = """<a class="card" href="{url}">
  <div class="card-img" style="background-image:url('{thumb}')"></div>
  <div class="card-body">
    <h3>{title}</h3>
    <p>{seo}</p>
    <span class="read">Read →</span>
  </div>
</a>"""

def build_homepage():
    meta = BASE_DIR / "build" / "meta.json"
    posts = []
    if meta.exists():
        posts = json.loads(meta.read_text(encoding="utf-8"))[:8]
    cards = "\n".join(CARD.format(**p) for p in posts)
    out = BASE_DIR / "build" / "index.html"
    save_file(out, TPL.format(cards=cards))
    print("✔ Homepage aggiornata.")
