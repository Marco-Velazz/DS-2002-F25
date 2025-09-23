#!/usr/bin/env python3
import sys
import json
import csv

# Read JSON from stdin and validate
try:
    raw = sys.stdin.read()
    data = json.loads(raw)
except json.JSONDecodeError:
    print("Error: Invalid JSON received from the pipe.", file=sys.stderr)
    sys.exit(1)

# Prepare CSV writer
fieldnames = ['card_id', 'card_name', 'set_name', 'rarity', 'market_price']
writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, restval="N/A")
writer.writeheader()

# Pull only the card data array
cards = data.get('data', [])

# Emit rows (fallback to N/A when fields are missing)
for card in cards:
    writer.writerow({
        'card_id': card.get('id', 'N/A'),
        'card_name': card.get('name', 'N/A'),
        'set_name': (card.get('set') or {}).get('name', 'N/A'),
        'rarity': card.get('rarity', 'N/A'),
        # Choose a market price if present; falls back to holofoil like your spec
        'market_price': (
            (card.get('tcgplayer') or {})
            .get('prices', {})
            .get('holofoil', {})
            .get('market', 'N/A')
        ),
    })
