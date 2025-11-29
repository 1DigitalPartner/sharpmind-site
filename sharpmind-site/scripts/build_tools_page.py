from .utils import BASE_DIR, ensure, save_file

TPL = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Tools — SharpMind</title>
  <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<header class="hero hero-mini">
  <div class="hero-content">
    <h1>Tools</h1>
    <p class="subtitle">Actionable intelligence, not vanity dashboards.</p>
  </div>
</header>

<section class="grid">
  <a class="card" href="/tools/trend-analyzer/">
    <div class="card-img" style="background-image:linear-gradient(135deg,#3b00ff,#8b5cf6)"></div>
    <div class="card-body"><h3>AI Trend Analyzer</h3><p>Detect signal in AI news & launches.</p></div>
  </a>

  <a class="card" href="/tools/data-navigator/">
    <div class="card-img" style="background-image:linear-gradient(135deg,#111827,#0ea5e9)"></div>
    <div class="card-body"><h3>Data Science Navigator</h3><p>From question to pipeline—fast.</p></div>
  </a>

  <a class="card" href="/tools/marketing-intel/">
    <div class="card-img" style="background-image:linear-gradient(135deg,#1f2937,#16a34a)"></div>
    <div class="card-body"><h3>Marketing Intelligence Toolkit</h3><p>Move from clicks to revenue.</p></div>
  </a>
</section>

<footer>© 2025 SharpMind — AI Insights & Analytics</footer>
</body>
</html>
"""

def build_tools_page():
    out = BASE_DIR / "build" / "tools" / "index.html"
    ensure(out.parent)
    save_file(out, TPL)
    # pagine placeholder singole (per evitare redirect alla home)
    for slug, title in [
        ("trend-analyzer","AI Trend Analyzer"),
        ("data-navigator","Data Science Navigator"),
        ("marketing-intel","Marketing Intelligence Toolkit"),
    ]:
        p = BASE_DIR / "build" / "tools" / slug / "index.html"
        ensure(p.parent)
        save_file(p, f"<!doctype html><html><head><meta charset='utf-8'><title>{title}</title><link rel='stylesheet' href='/assets/style.css'></head><body><header class='hero hero-mini'><div class='hero-content'><h1>{title}</h1><p class='subtitle'>Coming soon.</p></div></header><main class='section'><p>Working prototype landing.</p></main></body></html>")
    print("✔ Tools page generata.")
