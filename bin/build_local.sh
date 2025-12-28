#!/bin/bash
# This script builds the website and launches a local server to preview it.
set -ueo pipefail
PUBLISH_DIR="site-build"
sh bin/build.sh "${PUBLISH_DIR}"
BUNDLE_GEMFILE="${PUBLISH_DIR}/Gemfile" bundle exec jekyll serve --source "${PUBLISH_DIR}"