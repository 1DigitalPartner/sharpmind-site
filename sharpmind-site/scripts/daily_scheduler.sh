#!/usr/bin/env bash
set -euo pipefail

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$BASE_DIR/.." && pwd)"
PY="$PROJECT_ROOT/.venv/bin/python"

export PYTHONPATH="$PROJECT_ROOT"

LOG="/Users/gabrieletanzi/sharpmind-site/cron.log"

run() {
    "$PY" "$BASE_DIR/generate_post.py"
}

{
    echo "----- RUN $(date) -----"
    if run; then
        echo "[OK] Post generated successfully"
        /Users/gabrieletanzi/sharpmind-site/scripts/git_auto_push.sh
        exit 0
    else
        echo "[WARN] First attempt failed, retrying in 5 seconds..."
        sleep 5
        if run; then
            echo "[OK] Recovered on second attempt"
            /Users/gabrieletanzi/sharpmind-site/scripts/git_auto_push.sh
            exit 0
        else
            echo "[ERROR] FAILED after 2 attempts - $(date)"
            exit 1
        fi
    fi
} >> "$LOG" 2>&1
