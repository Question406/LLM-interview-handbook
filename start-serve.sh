#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is not installed. Install Node.js (>=22.13.0) first." >&2
  exit 1
fi

if [[ ! -d node_modules ]]; then
  echo "Dependencies not found. Running npm install..."
  npm install
fi

# content:build walks ~1200 markdown files and is very slow on Dropbox.
# Reuse an existing build unless FORCE_REBUILD=1 or artifacts are missing.
if [[ "${FORCE_REBUILD:-}" == "1" ]] || [[ ! -f content/generated/catalog.json ]] || [[ ! -f public/content/catalog.json ]]; then
  echo "Building content (can take several minutes on Dropbox)..."
  npm run content:build
else
  echo "Using existing content build. Set FORCE_REBUILD=1 to rebuild."
fi

npm run assets:build
echo "Starting dev server..."
WRANGLER_LOG_PATH=.wrangler/wrangler.log npm exec -- vinext dev
