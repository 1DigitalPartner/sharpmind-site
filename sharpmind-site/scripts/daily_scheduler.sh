#!/usr/bin/env bash
set -euo pipefail

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$BASE_DIR/.." && pwd)"
if [ -x "$PROJECT_ROOT/.venv/bin/python" ]; then
    PY="$PROJECT_ROOT/.venv/bin/python"
else
    PY="$(command -v python3)"
fi

export PYTHONPATH="$PROJECT_ROOT"

# Load local environment for cron runs.
# This keeps OPENAI_API_KEY and other private values out of crontab.
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    # shellcheck disable=SC1090
    source "$PROJECT_ROOT/.env"
    set +a
fi

if [ -f "$PROJECT_ROOT/.env.local" ]; then
    set -a
    # shellcheck disable=SC1090
    source "$PROJECT_ROOT/.env.local"
    set +a
fi

if [ -f "$PROJECT_ROOT/.dev.vars" ]; then
    set -a
    # shellcheck disable=SC1090
    source "$PROJECT_ROOT/.dev.vars"
    set +a
fi

if [ -z "${OPENAI_API_KEY:-}" ]; then
    echo "[ERROR] OPENAI_API_KEY missing after env load"
    exit 1
fi

LOG="$PROJECT_ROOT/cron.log"

run() {
    if ! "$PY" "$BASE_DIR/generate_post.py"; then
        echo "[ERROR] Post generation failed"
        return 1
    fi

    latest="$(find "$PROJECT_ROOT/content/en" "$PROJECT_ROOT/content/en/posts" -type f -name "*.md" -size +0c 2>/dev/null | xargs ls -t 2>/dev/null | head -1)"

    if [ -z "$latest" ]; then
        echo "[ERROR] No generated markdown file found for readability gate"
        return 1
    fi

    echo "[QUALITY] Running readability gate on: $latest"
    "$PY" "$PROJECT_ROOT/scripts/quality/readability_gate.py" "$latest"
}

{
    echo "----- RUN $(date) -----"
    if run; then
        echo "[OK] Post generated successfully"
        "$BASE_DIR/git_auto_push.sh"
        exit 0
    else
        echo "[WARN] First attempt failed, retrying in 5 seconds..."
        sleep 5
        if run; then
            echo "[OK] Recovered on second attempt"
            "$BASE_DIR/git_auto_push.sh"
            exit 0
        else
            echo "[ERROR] FAILED after 2 attempts - $(date)"
            exit 1
        fi
    fi
} >> "$LOG" 2>&1
