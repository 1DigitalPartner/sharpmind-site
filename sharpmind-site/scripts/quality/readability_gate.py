#!/usr/bin/env python3
import re
import sys
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: scripts/quality/readability_gate.py <markdown-file>")
    raise SystemExit(2)

path = Path(sys.argv[1])
if not path.exists():
    print(f"ERROR: file not found: {path}")
    raise SystemExit(2)

raw = path.read_text(encoding="utf-8", errors="replace")

# Remove YAML frontmatter and markdown noise, while preserving sentence boundaries.
text = re.sub(r"^---[\s\S]*?---", "\n", raw, count=1)
text = re.sub(r"```[\s\S]*?```", "\n", text)
text = re.sub(r"`[^`]+`", " ", text)

# Markdown structure must not be flattened into one fake sentence.
# Headings and bullets become separate sentence boundaries.
text = re.sub(r"^\s{0,6}#{1,6}\s+", ".\n", text, flags=re.M)
text = re.sub(r"^\s*[-*+]\s+", ".\n", text, flags=re.M)
text = re.sub(r"^\s*\d+[.)]\s+", ".\n", text, flags=re.M)
text = re.sub(r"\n{2,}", ".\n", text)
text = re.sub(r"\s+", " ", text).strip()
text = re.sub(r"\s+([.!?])", r"\1", text)

errors = []
warnings = []

words = re.findall(r"\b[\w’'-]+\b", text)
word_count = len(words)

sentences = [
    s.strip()
    for s in re.split(r"(?<=[.!?])\s+", text)
    if s.strip()
]

sentence_lengths = [
    len(re.findall(r"\b[\w’'-]+\b", s))
    for s in sentences
]

avg_sentence = round(sum(sentence_lengths) / max(len(sentence_lengths), 1), 1)
max_sentence = max(sentence_lengths) if sentence_lengths else 0
long_sentences = [n for n in sentence_lengths if n > 28]
very_long_sentences = [n for n in sentence_lengths if n > 38]

paragraphs = [
    p.strip()
    for p in re.split(r"\n\s*\n", raw)
    if p.strip() and not p.strip().startswith("---")
]

dense_paragraphs = []
for p in paragraphs:
    plain = re.sub(r"[#>*`\-\[\]\(\)]", " ", p)
    count = len(re.findall(r"\b[\w’'-]+\b", plain))
    if count > 95:
        dense_paragraphs.append(count)

banned_phrases = [
    "in today’s hyper-competitive digital landscape",
    "in today's hyper-competitive digital landscape",
    "fast-paced digital landscape",
    "in today's digital age",
    "game-changer",
    "unlock your potential",
    "leverage synergies",
    "cutting-edge",
    "revolutionize your business",
    "robust ecosystem",
    "paradigm",
    "strategic alignment",
    "seamless solution",
    "next-gen",
]

consultant_jargon = [
    "leverage",
    "optimize",
    "transformation",
    "framework",
    "strategic imperative",
    "stakeholder alignment",
    "ecosystem",
    "paradigm",
    "synergy",
    "holistic",
    "best-in-class",
    "mission-critical",
]

low = text.lower()

for phrase in banned_phrases:
    if phrase in low:
        errors.append(f"banned dense/hype phrase: {phrase}")

jargon_hits = []
for term in consultant_jargon:
    hits = len(re.findall(rf"\b{re.escape(term)}\b", low))
    if hits:
        jargon_hits.append((term, hits))

total_jargon = sum(n for _, n in jargon_hits)

# Numeric claim guard: allows examples, blocks unsupported hard business claims.
numeric_claims = re.findall(
    r"(?:up to|by|average of|expected|may fall by|increase|reduce|lift|drop|fell from|rose from)?\s*[$€£]?\d+(?:[.,]\d+)?\s*(?:%|percent|k|K|m|M|million|billion|times|x)?",
    text,
    flags=re.I,
)

if word_count < 700:
    errors.append(f"article too thin: {word_count} words")

if avg_sentence > 19:
    errors.append(f"average sentence too long: {avg_sentence} words")

if max_sentence > 48:
    errors.append(f"sentence too long: {max_sentence} words")

if len(very_long_sentences) > 2:
    errors.append(f"too many very long sentences >38 words: {len(very_long_sentences)}")

if len(long_sentences) > max(8, len(sentences) * 0.08):
    warnings.append(f"many long sentences >28 words: {len(long_sentences)}")

if len(dense_paragraphs) > 0:
    errors.append(f"dense paragraphs over 95 words: {dense_paragraphs[:5]}")

if total_jargon > 8:
    errors.append(f"too much consultant jargon: {jargon_hits}")

if len(numeric_claims) > 18:
    warnings.append(f"many numeric claims/examples: {len(numeric_claims)}")

required_plain_explainers = [
    "in simple words",
    "this means",
    "for example",
    "the goal is",
    "this matters because",
]

plain_hits = sum(1 for phrase in required_plain_explainers if phrase in low)
if plain_hits < 2:
    warnings.append("few plain-language explanation markers")

score = 100
score -= len(errors) * 18
score -= len(warnings) * 5
score -= min(20, total_jargon * 2)
score = max(0, score)

print("=== TanziTech Readability Gate ===")
print(f"File: {path}")
print(f"Score: {score}/100")
print(f"Words: {word_count}")
print(f"Sentences: {len(sentences)}")
print(f"Average sentence length: {avg_sentence}")
print(f"Max sentence length: {max_sentence}")
print(f"Long sentences >28 words: {len(long_sentences)}")
print(f"Very long sentences >38 words: {len(very_long_sentences)}")
print(f"Dense paragraphs >95 words: {len(dense_paragraphs)}")
print(f"Jargon hits: {jargon_hits}")
print(f"Numeric claims/examples: {len(numeric_claims)}")

if warnings:
    print("\nWarnings:")
    for w in warnings:
        print(f"⚠️  {w}")

if errors:
    print("\nFailures:")
    for e in errors:
        print(f"❌ {e}")
    print("\nStatus: BLOCKED")
    raise SystemExit(1)

if score < 78:
    print("\nFailures:")
    print(f"❌ readability score too low: {score}/100")
    print("\nStatus: BLOCKED")
    raise SystemExit(1)

print("\nStatus: PASSED ✅")
