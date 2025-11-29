#!/usr/bin/env bash
set -euo pipefail

REPO="/Users/gabrieletanzi/sharpmind-site"
BRANCH="content-backup"

cd "$REPO"

git fetch origin

# Crea branch se non esiste
if ! git show-ref --verify --quiet refs/heads/$BRANCH; then
    git checkout -b $BRANCH
else
    git checkout $BRANCH
    git pull origin $BRANCH || true
fi

# Copia solo la directory content
git add content/

if [ -n "$(git status --porcelain)" ]; then
    git commit -m "Daily content backup $(date +%Y-%m-%d_%H:%M)"
    git push -u origin $BRANCH
    echo "[BACKUP] Content pushed"
else
    echo "[BACKUP] No content changes"
fi

# Torna al ramo precedente
git checkout -
