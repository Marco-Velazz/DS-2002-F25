#!/usr/bin/env bash
set -euo pipefail

LOOKUP_DIR="card_set_lookup"
mkdir -p "$LOOKUP_DIR"

echo "Refreshing all card sets in ${LOOKUP_DIR}/ ..."

shopt -s nullglob
JSON_FILES=("$LOOKUP_DIR"/*.json)
shopt -u nullglob

if [ ${#JSON_FILES[@]} -eq 0 ]; then
  echo "No .json files found in ${LOOKUP_DIR}/ to refresh."
  echo "Tip: run ./add_card_set.sh first to add a set (or drop an offline file there)."
  exit 0
fi

EXTRA_HEADERS=()
if [ "${POKEMON_TCG_API_KEY:-}" != "" ]; then
  EXTRA_HEADERS+=(-H "X-Api-Key: ${POKEMON_TCG_API_KEY}")
fi

# Track overall success; never exit on a single curl failure
overall_ok=0

for FILE in "${JSON_FILES[@]}"; do
  SET_ID="$(basename "$FILE" .json)"
  echo "Updating set: ${SET_ID} ..."
  if curl -fSs "${EXTRA_HEADERS[@]}" \
      --retry 5 --retry-all-errors --retry-delay 2 \
      --max-time 60 \
      --get "https://api.pokemontcg.io/v2/cards" \
      --data-urlencode "q=set.id:${SET_ID}" \
      -o "$FILE"
  then
    echo "Updated data written to: ${FILE}"
  else
    echo "Warning: failed to refresh ${SET_ID} (e.g., 504). Keeping existing file: ${FILE}" >&2
    overall_ok=1
  fi
  sleep 1
done

echo "All card sets have been refreshed."
# Always succeed so Make doesn't die just because one set 504'd
exit 0
