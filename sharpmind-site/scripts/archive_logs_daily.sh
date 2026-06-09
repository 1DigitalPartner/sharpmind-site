#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ARCHIVE="$ROOT/logs/daily"

mkdir -p "$ARCHIVE"

cp "$ROOT/cron.log" "$ARCHIVE/cron-$(date +%Y-%m-%d).log" 2>/dev/null || true
