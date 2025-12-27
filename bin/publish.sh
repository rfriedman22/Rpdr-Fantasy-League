#!/bin/bash
# This script builds the website and publishes it to GitHub Pages.
# Some code generated with ChatGPT
set -u

# Ensure clean working tree
if ! git diff --quiet; then
  echo "Working tree not clean. Commit or stash changes first."
  exit 1
fi

# Build the site
PUBLISH_DIR="site-build"
bin/build.sh "${PUBLISH_DIR}"

# Move the build into gh-pages branch
git checkout gh-pages
# The --delete flag gets rid of any old or stale files no longer present, but we need to keep the .git directory
rsync -av "${PUBLISH_DIR}"/ .
rm -rf "${PUBLISH_DIR}"

# Commit and push changes
git add .
git commit -m "Update the site"
git push

# Return to main
git checkout main