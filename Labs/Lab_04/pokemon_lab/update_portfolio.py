#!/usr/bin/env python3
"""
update_portfolio.py
Step 2: ETL for Pokemon card prices + your inventory.

- _load_lookup_data(lookup_dir):     read *.json from API/lookup, flatten prices, keep highest market price per card
- _load_inventory_data(inventory_dir): read *.csv inventory, synthesize card_id if needed
- update_portfolio(...):             merge, clean, export CSV
- main():                            run on production dirs
- test():                            run on test dirs

Default: runs test() when executed directly.
"""

from __future__ import annotations
import os
import sys
import json
import glob
from typing import List

import pandas as pd


# ---------------------------
# Function 1: Load JSON Prices
# ---------------------------
def _load_lookup_data(lookup_dir: str) -> pd.DataFrame:
    """
    Reads every JSON file in lookup_dir, flattens, and extracts:
      id,name,number,set.id,set.name, and highest available market price (holofoil>normal>0.0)
    Returns a DataFrame with columns:
      card_id, card_name, card_number, set_id, set_name, card_market_value
    """
    all_lookup_df: List[pd.DataFrame] = []

    json_paths = sorted(glob.glob(os.path.join(lookup_dir, "*.json")))
    if not json_paths:
        # Return an empty but correctly-shaped DataFrame
        return pd.DataFrame(
            columns=[
                "card_id",
                "card_name",
                "card_number",
                "set_id",
                "set_name",
                "card_market_value",
            ]
        )

    for path in json_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[lookup] Warning: failed to read {path}: {e}", file=sys.stderr)
            continue

        if "data" not in data or not isinstance(data["data"], list):
            print(f"[lookup] Warning: no 'data' array in {path}", file=sys.stderr)
            continue

        # Flatten JSON
        df = pd.json_normalize(data["data"])

        # Create market value with priority: holofoil -> normal -> 0.0
        # Missing columns will be auto-filled with NaN and then handled by fillna.
        holo_col = "tcgplayer.prices.holofoil.market"
        norm_col = "tcgplayer.prices.normal.market"
        df["card_market_value"] = (
            df.get(holo_col)
            .fillna(df.get(norm_col))
            .fillna(0.0)
            .astype(float)
        )

        # Standardize column names
        rename_map = {
            "id": "card_id",
            "name": "card_name",
            "number": "card_number",
            "set.id": "set_id",
            "set.name": "set_name",
        }
        df = df.rename(columns=rename_map)

        required_cols = [
            "card_id",
            "card_name",
            "card_number",
            "set_id",
            "set_name",
            "card_market_value",
        ]
        # Keep only what we need; missing columns become NaN – fill wisely later if needed
        df_subset = df.reindex(columns=required_cols)
        all_lookup_df.append(df_subset.copy())

    if not all_lookup_df:
        return pd.DataFrame(
            columns=[
                "card_id",
                "card_name",
                "card_number",
                "set_id",
                "set_name",
                "card_market_value",
            ]
        )

    lookup_df = pd.concat(all_lookup_df, ignore_index=True)

    # Deduplicate cards by highest price (sort descending first)
    lookup_df = lookup_df.sort_values("card_market_value", ascending=False)
    lookup_df = lookup_df.drop_duplicates(subset=["card_id"], keep="first")

    # Tidy types
    for c in ["card_id", "card_name", "card_number", "set_id", "set_name"]:
        if c in lookup_df.columns:
            lookup_df[c] = lookup_df[c].astype(str)

    return lookup_df.reset_index(drop=True)


# ------------------------------------
# Function 2: Load CSV Inventory (local)
# ------------------------------------
def _load_inventory_data(inventory_dir: str) -> pd.DataFrame:
    """
    Reads all *.csv in inventory_dir and concatenates them.
    If 'card_id' is missing, synthesize it from set_id + '-' + card_number.
    We also try to ensure location fields exist for index (binder_name, page_number, slot_number).
    """
    csv_paths = sorted(glob.glob(os.path.join(inventory_dir, "*.csv")))
    if not csv_paths:
        return pd.DataFrame()

    frames: List[pd.DataFrame] = []
    for path in csv_paths:
        try:
            df = pd.read_csv(path)
            frames.append(df)
        except Exception as e:
            print(f"[inventory] Warning: failed to read {path}: {e}", file=sys.stderr)

    if not frames:
        return pd.DataFrame()

    inventory_df = pd.concat(frames, ignore_index=True)

    # Normalize column names (strip spaces, lower-case-ish consistency)
    inventory_df.columns = [c.strip() for c in inventory_df.columns]

    # If card_id not present, try to build from set_id + '-' + card_number
    if "card_id" not in inventory_df.columns:
        missing = [c for c in ["set_id", "card_number"] if c not in inventory_df.columns]
        if missing:
            print(
                "[inventory] Error: inventory CSVs must contain 'card_id' OR both 'set_id' and 'card_number'.",
                file=sys.stderr,
            )
            return pd.DataFrame()
        # Build card_id key
        inventory_df["card_id"] = (
            inventory_df["set_id"].astype(str).str.strip()
            + "-"
            + inventory_df["card_number"].astype(str).str.strip()
        )

    # Ensure quantity exists (default to 1 if missing)
    if "quantity" not in inventory_df.columns:
        inventory_df["quantity"] = 1

    # Ensure location fields exist (helpful for index column)
    if "binder_name" not in inventory_df.columns:
        inventory_df["binder_name"] = "Binder"
    if "page_number" not in inventory_df.columns:
        inventory_df["page_number"] = ""
    if "slot_number" not in inventory_df.columns:
        inventory_df["slot_number"] = ""

    # Cast important columns to string for clean joins/index creation
    for c in ["card_id", "binder_name", "page_number", "slot_number"]:
        inventory_df[c] = inventory_df[c].astype(str)

    return inventory_df


# ---------------------------------------------------
# Function 3: Main ETL / Merge / Export (single entry)
# ---------------------------------------------------
def update_portfolio(inventory_dir: str, lookup_dir: str, output_file: str) -> None:
    """
    Orchestrates the ETL:
    - load lookup (JSON) + inventory (CSV)
    - left-merge on card_id
    - fill missing values
    - create location index
    - write output CSV
    """
    lookup_df = _load_lookup_data(lookup_dir)
    inventory_df = _load_inventory_data(inventory_dir)

    # Prepare the output columns we want to emit
    final_cols = [
        "index",              # binder/page/slot combined
        "card_id",
        "card_name",
        "card_number",
        "set_id",
        "set_name",
        "quantity",
        "card_market_value",
        "portfolio_line_value",  # quantity * market
    ]

    # If inventory is empty, write headers and bail
    if inventory_df.empty:
        print("[ETL] Error: inventory is empty; writing empty portfolio with headers.", file=sys.stderr)
        pd.DataFrame(columns=final_cols).to_csv(output_file, index=False)
        return

    # Select necessary lookup columns (some may be missing if lookup empty)
    keep_lookup_cols = [
        "card_id", "card_name", "card_number", "set_id", "set_name", "card_market_value"
    ]
    lookup_df = lookup_df.reindex(columns=keep_lookup_cols)

    merged = pd.merge(
        inventory_df,
        lookup_df,
        on="card_id",
        how="left",
    )

        # Final cleaning — ensure expected columns exist first
    expected_cols = ["card_name", "card_number", "set_id", "set_name", "card_market_value"]
    for c in expected_cols:
        if c not in merged.columns:
            merged[c] = pd.NA

    # Normalize market value and set name fallbacks
    merged["card_market_value"] = merged["card_market_value"].astype(float).fillna(0.0)
    merged["set_name"] = merged["set_name"].astype(str).fillna("NOT_FOUND").replace({"<NA>": "NOT_FOUND"})

    # Prefer lookup values; backfill from inventory if present
    for backup_col in ["card_name", "card_number", "set_id"]:
        if backup_col in inventory_df.columns:
            # If the column exists in merged (it does now), fill only missing entries
            merged[backup_col] = merged[backup_col].astype("string")
            merged[backup_col] = merged[backup_col].fillna(inventory_df[backup_col].astype(str))

    # Create human-readable location index
    merged["index"] = (
        merged["binder_name"].astype(str).str.strip()
        + "_"
        + merged["page_number"].astype(str).str.strip()
        + "_"
        + merged["slot_number"].astype(str).str.strip()
    )

    # Portfolio line value (per row)
    merged["portfolio_line_value"] = merged["quantity"].astype(float) * merged["card_market_value"]

    # Reorder/limit to final columns (create any missing ones to keep write stable)
    for col in final_cols:
        if col not in merged.columns:
            merged[col] = "" if col != "card_market_value" else 0.0

    merged = merged[final_cols]

    # Write
    merged.to_csv(output_file, index=False)
    print(f"[ETL] Success: wrote {output_file} ({len(merged)} rows)")


# -------------------------------
# Public interface / convenience
# -------------------------------
def main() -> None:
    """Run on production folders by default."""
    update_portfolio(
        inventory_dir="./card_inventory/",
        lookup_dir="./card_set_lookup/",
        output_file="card_portfolio.csv",
    )


def test() -> None:
    """Run on test folders and produce a test CSV."""
    update_portfolio(
        inventory_dir="./card_inventory_test/",
        lookup_dir="./card_set_lookup_test/",
        output_file="test_card_portfolio.csv",
    )


if __name__ == "__main__":
    print("[Runner] Starting update_portfolio.py in Test Mode...", file=sys.stderr)
    test()
