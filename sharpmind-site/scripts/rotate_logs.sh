#!/usr/bin/env bash
set -euo pipefail

LOG="/Users/gabrieletanzi/sharpmind-site/cron.log"
ARCHIVE="/Users/gabrieletanzi/sharpmind-site/logs"

mkdir -p "$ARCHIVE"

if [ -f "$LOG" ]; then
    SIZE=$(stat -f%z "$LOG")
    MAX=$((5 * 1024 * 1024))  # 5 MB

    if [ $SIZE -gt $MAX ]; then
        mv "$LOG" "$ARCHIVE/cron-$(date +%Y%m%d-%H%M%S).log"
        touch "$LOG"
        echo "[INFO] Rotated cron log at $(date)" >> "$LOG"
    fi
fi
