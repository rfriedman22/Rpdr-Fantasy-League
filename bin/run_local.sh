#!/bin/bash
# One-liner to run the local server
set -ueo pipefail
if [[ $# -eq 0 ]]; then
  PUBLISH_DIR="site-build"
elif [[ $# -eq 1 ]]; then
  PUBLISH_DIR="$1"
else
    echo "Usage: $0 [publish_dir]"
    exit 1
fi

echo "Starting local server with publish directory: ${PUBLISH_DIR}"
BUNDLE_GEMFILE="${PUBLISH_DIR}/Gemfile" bundle exec jekyll serve --source "${PUBLISH_DIR}"