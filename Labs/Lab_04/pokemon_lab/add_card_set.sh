#!/usr/bin/env bash
set -euo pipefail


LOOKUP_DIR="card_set_lookup"
mkdir -p "$LOOKUP_DIR"

# Prompt for set ID
read -rp "Enter TCG Card Set ID (e.g., base1, base4): " SET_ID

# Validate
if [ -z "$SET_ID" ]; then
  echo "Error: Set ID cannot be empty." >&2
  exit 1
fi

OUTFILE="$LOOKUP_DIR/${SET_ID}.json"

echo "Fetching card data for set: $SET_ID ..."
# If you have an API key, export POKEMON_TCG_API_KEY first and the header below will be included
EXTRA_HEADERS=()
if [ "${POKEMON_TCG_API_KEY:-}" != "" ]; then
  EXTRA_HEADERS+=(-H "X-Api-Key: ${POKEMON_TCG_API_KEY}")
fi

# Pokemon TCG API v2: query by set.id
# Example query parameter: q=set.id:base1
curl -fSs "${EXTRA_HEADERS[@]}" \
  --get "https://api.pokemontcg.io/v2/cards" \
  --data-urlencode "q=set.id:${SET_ID}" \
  -o "$OUTFILE"

echo "Wrote data to: $OUTFILE"
