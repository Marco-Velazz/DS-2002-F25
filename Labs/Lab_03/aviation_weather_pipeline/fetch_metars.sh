#!/usr/bin/env bash
set -euo pipefail

# Variables
API_URL="https://aviationweather.gov/api/data/metar"
OUTPUT_DIR="raw_metars"
AIRPORT_CODES_FILE="airport_codes.txt"

# Make sure output directory exists
mkdir -p "$OUTPUT_DIR"

echo "Fetching METAR data for airports..."

while read -r airport_code; do
    # Skip empty lines
    if [ -z "$airport_code" ]; then
        continue
    fi

    URL="$API_URL?ids=$airport_code&format=json"
    OUTPUT_FILE="$OUTPUT_DIR/${airport_code}.json"

    echo "  -> Fetching data for $airport_code..."

    curl -s "$URL" -o "$OUTPUT_FILE" 2>&1
    if [ $? -ne 0 ]; then
        echo "Error: curl failed for $airport_code." >&2
        exit 1
    fi

    if [ ! -s "$OUTPUT_FILE" ] || [ "$(jq 'length' "$OUTPUT_FILE")" -eq 0 ]; then
        echo "Warning: No METAR data found for $airport_code. The API returned an empty response." >&2
    else
        echo "  -> Data for $airport_code saved successfully."
    fi

done < "$AIRPORT_CODES_FILE"

echo "Data fetching complete. Check the '$OUTPUT_DIR' directory."
