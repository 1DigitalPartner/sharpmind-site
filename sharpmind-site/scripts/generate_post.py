import os
import json
from textwrap import dedent

from openai import OpenAI

from scripts.utils import slugify, today, save_file, ensure_dir


def call_openai(prompt: str) -> str:
    """
    Chiama OpenAI e ritorna il testo di output.
    Usa il campo .output_text per semplicità.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    resp = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
    )
    return resp.output_text


def generate_article_json() -> dict:
    """
    Chiede a OpenAI di restituire SOLO JSON con schema fisso,
    così poi possiamo parsare in modo robusto.
    """
    prompt = dedent(
        """
        You are SharpMind, a strategic AI & data insights writer.

        Write ONE high–quality article about AI / data / agentic systems / analytics
        for senior operators and founders.

        Return ONLY a single JSON object, no prose, no explanation.

        JSON schema:
        {
          "title": "string (<= 120 chars, sharp, specific)",
          "subtitle": "string (<= 180 chars, contextual, no hype)",
          "seo_description": "string (<= 155 chars, meta description style)",
          "tags": ["ai", "data", "agents", ...],
          "key_insights": [
            "bullet 1 (concise, insight, not generic)",
            "bullet 2",
            "bullet 3"
          ],
          "body_markdown": "Full article in GitHub-flavored Markdown. Use headings, bullets, examples. 1000-1600 words."
        }

        Rules:
        - Language: English.
        - Tone: analytical, senior, data-informed, no buzzword salad.
        - Avoid generic intros like "In today's fast-paced world".
        - Focus on one strong topic, not a vague overview.
        """
    )

    raw = call_openai(prompt)

    # Prendiamo la prima { ... } valida nel testo
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("OpenAI response does not contain JSON object")

    json_str = raw[start : end + 1]
    data = json.loads(json_str)

    # Normalizzazione minima
    data.setdefault("tags", [])
    data.setdefault("key_insights", [])
    data.setdefault("seo_description", "")
    data.setdefault("subtitle", "")

    return data


def build_markdown(data: dict) -> str:
    """
    Costruisce markdown finale con frontmatter + corpo.
    """
    title = data["title"].strip()
    subtitle = data.get("subtitle", "").strip()
    seo_desc = data.get("seo_description", "").strip()
    tags = data.get("tags") or []
    key_insights = data.get("key_insights") or []
    body_md = data.get("body_markdown", "").strip()

    # YAML frontmatter
    lines = ["---"]
    safe_title = title.replace('"', "'")
    lines.append(f'title: "{safe_title}"')
    if subtitle:
        lines.append(f'subtitle: "{subtitle.replace("\"", "\'")}"')
    lines.append(f"date: {today()}")
    lines.append(f'seo_description: "{seo_desc.replace("\"", "\'")}"')
    if tags:
        lines.append("tags:")
        for t in tags:
            t_clean = str(t).strip()
            if t_clean:
                lines.append(f"  - {t_clean}")
    else:
        lines.append("tags: []")

    lines.append("---")
    lines.append("")

    # Key insights section
    if key_insights:
        lines.append("## Key Insights")
        lines.append("")
        for ki in key_insights:
            ki_clean = str(ki).strip()
            if ki_clean:
                lines.append(f"- {ki_clean}")
        lines.append("")

    # Full article
    if body_md:
        lines.append("## Full Article")
        lines.append("")
        lines.append(body_md)

    return "\n".join(lines)


def generate_and_save_article() -> str:
    """
    Genera un articolo, lo salva in content/en/YYYY-MM-DD-slug.md
    e ritorna il path.
    """
    data = generate_article_json()
    title = data["title"]
    slug = slugify(title)

    filename = f"{today()}-{slug}.md"
    rel_dir = os.path.join("content", "en")
    rel_path = os.path.join(rel_dir, filename)

    ensure_dir(rel_dir)
    markdown = build_markdown(data)
    save_file(rel_path, markdown)

    return rel_path


if __name__ == "__main__":
    path = generate_and_save_article()
    print(f"✔ Post saved to {path}")
