#!/usr/bin/env python3
"""
generate_summary.py
Step 3: Reporting tool for the final portfolio CSV produced by update_portfolio.py.

- generate_summary(portfolio_file): loads CSV, prints total value and most valuable card
- main():  uses 'card_portfolio.csv'   (production)
- test():  uses 'test_card_portfolio.csv' (test)
Default: runs test() when executed directly.
"""

import os
import sys
import pandas as pd


def generate_summary(portfolio_file: str) -> None:
    """Read portfolio CSV and print summary stats."""
    # 1) Exists?
    if not os.path.exists(portfolio_file):
        print(f"[Summary] Error: file not found: {portfolio_file}", file=sys.stderr)
        sys.exit(1)

    # 2) Load
    try:
        df = pd.read_csv(portfolio_file)
    except Exception as e:
        print(f"[Summary] Error reading {portfolio_file}: {e}", file=sys.stderr)
        sys.exit(1)

    # 3) Empty?
    if df.empty:
        print(f"[Summary] {portfolio_file} is empty. Nothing to report.")
        return

    # Verify required columns exist
    required_cols = ["card_market_value", "card_id", "card_name"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        print(f"[Summary] Error: missing required columns {missing} in {portfolio_file}", file=sys.stderr)
        sys.exit(1)

    # 4) Total value (per instructions: sum of card_market_value)
    total_portfolio_value = float(df["card_market_value"].fillna(0.0).sum())

    # (Optional: if you want to sum by quantity instead, uncomment the line below)
    # if "portfolio_line_value" in df.columns:
    #     total_portfolio_value = float(df["portfolio_line_value"].fillna(0.0).sum())

    # 5) Most valuable card (by single-card market value)
    max_idx = df["card_market_value"].idxmax()
    most_valuable_card = df.loc[max_idx]

    # 6) Print report
    print("=== Portfolio Summary ===")
    print(f"Total Portfolio Value (sum of card_market_value): ${total_portfolio_value:,.2f}")
    print("--- Most Valuable Card ---")
    print(f"Name:  {most_valuable_card.get('card_name', 'N/A')}")
    print(f"ID:    {most_valuable_card.get('card_id', 'N/A')}")
    print(f"Value: ${float(most_valuable_card.get('card_market_value', 0.0)):,.2f}")


def main() -> None:
    """Production: summarize the main portfolio."""
    generate_summary("card_portfolio.csv")


def test() -> None:
    """Test: summarize the test portfolio."""
    generate_summary("test_card_portfolio.csv")


if __name__ == "__main__":
    # Default to Test Mode per lab instructions / Makefile target
    print("[Runner] Starting generate_summary.py in Test Mode...", file=sys.stderr)
    test()