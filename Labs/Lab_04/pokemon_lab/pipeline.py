#!/usr/bin/env python3
"""
pipeline.py
Step 4: Master orchestration for the full production workflow.

- run_production_pipeline(): ETL (update_portfolio.main) -> Reporting (generate_summary.main)
Default: executes the full production workflow when run directly.
"""
import sys

import update_portfolio as update_portfolio
import generate_summary as generate_summary


def run_production_pipeline() -> None:
    """Run the full production pipeline: update -> summary."""
    print("[Pipeline] Starting production pipeline...", file=sys.stderr)

    print("[Pipeline] Step 1/2: Updating portfolio (ETL)...", file=sys.stderr)
    update_portfolio.main()  # writes card_portfolio.csv

    print("[Pipeline] Step 2/2: Generating summary report...", file=sys.stderr)
    generate_summary.main()  # reads card_portfolio.csv, prints summary

    print("[Pipeline] Pipeline completed successfully.", file=sys.stderr)


if __name__ == "__main__":
    run_production_pipeline()
