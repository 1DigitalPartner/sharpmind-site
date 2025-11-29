import fs from "fs";
import path from "path";
import matter from "gray-matter";
import { marked } from "marked";

const ROOT = process.cwd();
const CONTENT_DIR = path.join(ROOT, "content", "en");
const BUILD_DIR = path.join(ROOT, "build");
const POSTS_OUT_DIR = path.join(BUILD_DIR, "en", "posts");

function ensureDir(p) {
  fs.mkdirSync(p, { recursive: true });
}

function loadPosts() {
  if (!fs.existsSync(CONTENT_DIR)) return [];

  const files = fs
    .readdirSync(CONTENT_DIR)
    .filter((f) => f.endsWith(".md"));

  const posts = [];

  for (const file of files) {
    const full = path.join(CONTENT_DIR, file);
    const raw = fs.readFileSync(full, "utf8");
    const { data, content } = matter(raw);

    if (!data.title) continue;

    const slug = data.slug
      || file.replace(/\.md$/, "")
      || "post";

    posts.push({
      slug,
      title: data.title,
      subtitle: data.subtitle || "",
      date: data.date || file.slice(0, 10),
      seo_description: data.seo_description || "",
      tags: data.tags || [],
      contentHtml: marked.parse(content),
    });
  }

  // Ordina per data desc
  posts.sort((a, b) => {
    const da = new Date(a.date || "1970-01-01");
    const db = new Date(b.date || "1970-01-01");
    return db - da;
  });

  return posts;
}

function layout({ title, body }) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>${title}</title>
  <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
${body}
</body>
</html>`;
}

function renderHome(posts) {
  const latest = posts.slice(0, 3);

  const cards =
    latest.length === 0
      ? `<p class="section-desc">No reports yet. First premium insights are being generated.</p>`
      : `<div class="cards">
  ${latest
    .map(
      (p) => `
    <div class="card">
      <h3>${p.title}</h3>
      <p>${p.subtitle || p.seo_description || ""}</p>
      <a href="/en/posts/${p.slug}/" class="card-link">Read report →</a>
    </div>`
    )
    .join("\n")}
</div>`;

  const body = `
<header class="hero">
  <div class="hero-content">
    <h1>SharpMind</h1>
    <p class="subtitle">Strategic AI Insights. Premium. Data-Driven. Daily.</p>
    <a href="/en/posts/" class="cta">Explore Insights</a>
  </div>
</header>

<section class="section">
  <h2>AI Insights</h2>
  <p class="section-desc">
    Daily premium articles on AI, data, technology, business growth, and advanced analytics.
  </p>
</section>

<section class="section">
  <h2>Latest Deep Dives</h2>
  ${cards}
</section>

<section class="cards">
  <div class="card">
    <h3>Sharp Tools</h3>
    <ul>
      <li>AI Trend Analyzer</li>
      <li>Data Science Navigator</li>
      <li>Marketing Intelligence Toolkit</li>
    </ul>
    <a href="/tools/" class="card-link">Open Tools →</a>
  </div>
  <div class="card">
    <h3>Admin Dashboard</h3>
    <p>Internal view of all posts & metadata.</p>
    <a href="/admin/" class="card-link">Open Admin →</a>
  </div>
</section>

<footer>
  © 2025 SharpMind — AI Insights & Analytics
</footer>
`;

  return layout({ title: "SharpMind — AI Insights & Analytics", body });
}

function renderPostsIndex(posts) {
  const cards =
    posts.length === 0
      ? `<p class="section-desc">No posts available yet. Come back soon.</p>`
      : `<div class="cards">
  ${posts
    .map(
      (p) => `
    <div class="card">
      <h3>${p.title}</h3>
      <p>${p.subtitle || p.seo_description || ""}</p>
      <p><small>${p.date}</small></p>
      <a href="/en/posts/${p.slug}/" class="card-link">Open →</a>
    </div>`
    )
    .join("\n")}
</div>`;

  const body = `
<header class="hero">
  <div class="hero-content">
    <h1>All Insights</h1>
    <p class="subtitle">Full archive of SharpMind reports.</p>
    <a href="/" class="cta">Back to Home</a>
  </div>
</header>

<section class="section">
  <h2>Reports</h2>
  ${cards}
</section>

<footer>
  © 2025 SharpMind — AI Insights & Analytics
</footer>
`;

  return layout({ title: "All Insights — SharpMind", body });
}

function renderPostPage(post) {
  const tags =
    post.tags && post.tags.length
      ? `<p><strong>Tags:</strong> ${post.tags.join(", ")}</p>`
      : "";

  const body = `
<header class="hero">
  <div class="hero-content">
    <h1>${post.title}</h1>
    <p class="subtitle">${post.subtitle || ""}</p>
    <a href="/en/posts/" class="cta">← Back to Insights</a>
  </div>
</header>

<section class="section">
  <p><small>${post.date}</small></p>
  ${tags}
</section>

<section class="section">
  ${post.contentHtml}
</section>

<footer>
  © 2025 SharpMind — AI Insights & Analytics
</footer>
`;

  return layout({ title: `${post.title} — SharpMind`, body });
}

function renderToolsPage() {
  const body = `
<header class="hero">
  <div class="hero-content">
    <h1>Sharp Tools</h1>
    <p class="subtitle">Internal and public tools for AI, data & growth.</p>
    <a href="/" class="cta">← Back to Home</a>
  </div>
</header>

<section class="section">
  <h2>Available Tooling</h2>
  <div class="cards">
    <div class="card">
      <h3>AI Trend Analyzer</h3>
      <p>Framework to track, cluster, and interpret AI ecosystem signals.</p>
      <p><small>Coming soon — connected to internal research pipeline.</small></p>
    </div>
    <div class="card">
      <h3>Data Science Navigator</h3>
      <p>Curated decision maps for data teams: stack choices, trade-offs, risks.</p>
      <p><small>Phase 1: static content. Phase 2: interactive playbooks.</small></p>
    </div>
    <div class="card">
      <h3>Marketing Intelligence Toolkit</h3>
      <p>Insights, prompts, and scorecards for performance & growth operators.</p>
      <p><small>Will be progressively enriched from SharpMind content.</small></p>
    </div>
  </div>
</section>

<footer>
  © 2025 SharpMind — AI Insights & Analytics
</footer>
`;

  return layout({ title: "Sharp Tools — SharpMind", body });
}

function renderAdminPage(posts) {
  const rows =
    posts.length === 0
      ? "<tr><td colspan='4'>No posts yet.</td></tr>"
      : posts
          .map(
            (p) => `
  <tr>
    <td>${p.date}</td>
    <td><a href="/en/posts/${p.slug}/">${p.title}</a></td>
    <td>${(p.tags || []).join(", ")}</td>
    <td>${p.seo_description || ""}</td>
  </tr>`
          )
          .join("\n");

  const body = `
<header class="hero">
  <div class="hero-content">
    <h1>Admin — SharpMind</h1>
    <p class="subtitle">Internal view of generated content.</p>
    <a href="/" class="cta">← Back to Home</a>
  </div>
</header>

<section class="section">
  <h2>Content Overview</h2>
  <p>Total posts: ${posts.length}</p>
  <div style="overflow-x:auto; padding: 10px;">
    <table style="width:100%; border-collapse: collapse; font-size: 0.9rem;">
      <thead>
        <tr>
          <th style="border-bottom:1px solid #ccc; text-align:left; padding:6px;">Date</th>
          <th style="border-bottom:1px solid #ccc; text-align:left; padding:6px;">Title</th>
          <th style="border-bottom:1px solid #ccc; text-align:left; padding:6px;">Tags</th>
          <th style="border-bottom:1px solid #ccc; text-align:left; padding:6px;">SEO Description</th>
        </tr>
      </thead>
      <tbody>
        ${rows}
      </tbody>
    </table>
  </div>
</section>

<footer>
  © 2025 SharpMind — Internal Dashboard
</footer>
`;

  return layout({ title: "Admin — SharpMind", body });
}

function main() {
  ensureDir(BUILD_DIR);
  ensureDir(POSTS_OUT_DIR);

  const posts = loadPosts();

  // Home
  fs.writeFileSync(path.join(BUILD_DIR, "index.html"), renderHome(posts), "utf8");

  // Posts index
  const postsIndexDir = path.join(BUILD_DIR, "en", "posts");
  ensureDir(postsIndexDir);
  fs.writeFileSync(
    path.join(postsIndexDir, "index.html"),
    renderPostsIndex(posts),
    "utf8"
  );

  // Each post
  for (const p of posts) {
    const dir = path.join(postsIndexDir, p.slug);
    ensureDir(dir);
    fs.writeFileSync(path.join(dir, "index.html"), renderPostPage(p), "utf8");
  }

  // Tools
  const toolsDir = path.join(BUILD_DIR, "tools");
  ensureDir(toolsDir);
  fs.writeFileSync(
    path.join(toolsDir, "index.html"),
    renderToolsPage(),
    "utf8"
  );

  // Admin
  const adminDir = path.join(BUILD_DIR, "admin");
  ensureDir(adminDir);
  fs.writeFileSync(
    path.join(adminDir, "index.html"),
    renderAdminPage(posts),
    "utf8"
  );

  console.log(`✔ Build complete. Posts: ${posts.length}`);
}

main();
