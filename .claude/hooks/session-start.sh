#!/bin/bash
# Installs ffmpeg and yt-dlp for the Watch plugin in Claude Code cloud sessions.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  apt-get install -y -qq ffmpeg >/dev/null 2>&1 \
    || { apt-get update -qq >/dev/null 2>&1 && apt-get install -y -qq ffmpeg >/dev/null 2>&1; }
fi

if ! command -v yt-dlp >/dev/null 2>&1 && ! [ -x "$HOME/.local/bin/yt-dlp" ]; then
  command -v uv >/dev/null 2>&1 || pip install -q uv
  uv tool install -q "yt-dlp[default,curl-cffi]"
fi

if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export PATH=\"$HOME/.local/bin:\$PATH\"" >> "$CLAUDE_ENV_FILE"
fi
