import sys
from scripts.generate_post import generate_article

n = int(sys.argv[1]) if len(sys.argv) > 1 else 3

for i in range(n):
    slug, path = generate_article()
    print(f"[{i+1}/{n}] → {slug}")
