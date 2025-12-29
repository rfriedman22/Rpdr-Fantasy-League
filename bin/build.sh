#!/bin/bash
# This script creates a league and builds the website into the specified publish directory.
set -ueo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <publish_dir>"
  exit 1
fi

PUBLISH_DIR="$1"
rm -rf "${PUBLISH_DIR}"
cp -r site-template "${PUBLISH_DIR}"

python3 bin/create_league.py --season-config season-configs/17.yml  --output_dir "${PUBLISH_DIR}"
