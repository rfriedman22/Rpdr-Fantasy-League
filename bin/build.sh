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

CONFIG_DIR="season-configs"
for config_file in "${CONFIG_DIR}"/*.yml; do
  echo "Building league for config: ${config_file}"
  python3 bin/create_league.py --season-config "${config_file}" --output_dir "${PUBLISH_DIR}"
done