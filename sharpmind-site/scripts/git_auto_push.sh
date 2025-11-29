#!/usr/bin/env bash
set -euo pipefail

REPO="/Users/gabrieletanzi/sharpmind-site"

cd "$REPO"

# Config git (solo la prima volta; non sovrascrive se già settati)
git config user.name "Gabriele Tanzi" 2>/dev/null || true
git config user.email "gabriele@tanzitech.com" 2>/dev/null || true

# Commit solo se ci sono modifiche
if [ -n "$(git status --porcelain)" ]; then
    git add .
    git commit -m "Auto-update $(date +%Y-%m-%d_%H:%M:%S)"
    git push
    echo "[GIT] Auto-push completed"
else
    echo "[GIT] No changes to commit"
fi
