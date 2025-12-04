import fs from "fs";
import path from "path";
import matter from "gray-matter";

const ROOT = process.cwd();
const CONTENT_DIR = path.join(ROOT, "content");

function* walk(dir) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      yield* walk(full);
    } else if (entry.isFile() && full.endsWith(".md")) {
      yield full;
    }
  }
}

let hasError = false;

for (const file of walk(CONTENT_DIR)) {
  const raw = fs.readFileSync(file, "utf8");
  try {
    matter(raw); // prova a parsare il front-matter
  } catch (err) {
    hasError = true;
    console.error("\n[ERROR] Front-matter non valido in:", file);
    console.error("Message:", err.message);
  }
}

if (!hasError) {
  console.log("✅ Tutti i file .md hanno front-matter valido.");
}
