#!/bin/bash
while getopts s:e: flag; do
  case "${flag}" in
    s) SEASON=${OPTARG};;
    e) EPISODE=${OPTARG};;
  esac
done
if [ -z "$SEASON" ] || [ -z "$EPISODE" ]; then
  echo "Usage: bin/make_episode.sh -s <season> -e <episode>" >&2
  exit 1
fi

EPISODE_FILE="assets/seasons/${SEASON}/episodes/$(printf '%02d' ${EPISODE}).json"


cp schemas/episode.json "${EPISODE_FILE}"
echo "Created season ${SEASON} episode ${EPISODE} at ${EPISODE_FILE}"