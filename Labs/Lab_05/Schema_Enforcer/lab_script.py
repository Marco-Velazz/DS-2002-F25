#!/usr/bin/env python3
# DS-2002 Lab 05 — Parts 1 & 2

from pathlib import Path
import csv
import json
import pandas as pd

# --- Paths ---
CSV_PATH = Path("raw_survey_data.csv")
JSON_PATH = Path("raw_course_catalog.json")
CSV_CLEAN_OUT = Path("clean_survey_data.csv")
JSON_NORM_OUT = Path("clean_course_catalog.csv")


# -------------------------------
# Part 1 (your existing code)
# -------------------------------
def create_tabular_csv():
    rows = [
        # student_id, major, GPA, is_cs_major, credits_taken
        [1001, "Computer Science", 3,   "Yes", "15.0"],
        [1002, "Data Science",     3.5, "Yes", "12.5"],
        [1003, "Biology",          2,   "No",  "10.5"],
        [1004, "Economics",        3.9, "No",  "18"],
        [1005, "Psychology",       3,   "No",  "9.0"],
    ]
    headers = ["student_id", "major", "GPA", "is_cs_major", "credits_taken"]

    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    print(f"[OK] Wrote tabular data with intentional issues -> {CSV_PATH.resolve()}")


def create_hierarchical_json():
    courses = [
        {
            "course_id": "DS2002",
            "section": "001",
            "title": "Data Science Systems",
            "level": 200,
            "instructors": [
                {"name": "Austin Rivera", "role": "Primary"},
                {"name": "Heywood Williams-Tracy", "role": "TA"},
            ],
        },
        {
            "course_id": "DS2003",
            "section": "002",
            "title": "Data Science: Data Visualization",
            "level": 200,
            "instructors": [
                {"name": "Antonios Mamalakis", "role": "Primary"},
            ],
        },
        {
            "course_id": "CS3710",
            # section intentionally omitted to create a small schema diff
            "title": "Introduction to Cybersecurity",
            "level": 300,
            "instructors": [
                {"name": "Angela Orebaugh", "role": "Primary"},
            ],
        },
    ]
    with JSON_PATH.open("w", encoding="utf-8") as f:
        json.dump(courses, f, indent=2, ensure_ascii=False)

    print(f"[OK] Wrote hierarchical JSON (needs normalization) -> {JSON_PATH.resolve()}")


# -------------------------------
# Part 2 — Task 3: Clean/validate CSV
# -------------------------------
def clean_and_validate_csv():
    # Load
    df = pd.read_csv(CSV_PATH)

    # Enforce Boolean type for is_cs_major ('Yes'/'No' -> True/False)
    df["is_cs_major"] = (
        df["is_cs_major"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map({"yes": True, "no": False})
    )

    # Enforce numeric for GPA and credits_taken as float
    # GPA can be int or float in raw — cast to float explicitly
    df["GPA"] = pd.to_numeric(df["GPA"], errors="coerce").astype("float64")

    # credits_taken are strings in raw — cast to float explicitly
    df["credits_taken"] = pd.to_numeric(df["credits_taken"], errors="coerce").astype("float64")

    # (Optional) enforce dtypes for the other columns
    # student_id int, major string
    # Using pandas' nullable dtypes where appropriate is fine too
    df = df.astype({
        "student_id": "int64",
        "major": "string",
        "GPA": "float64",
        "is_cs_major": "bool",
        "credits_taken": "float64",
    })

    # Save
    df.to_csv(CSV_CLEAN_OUT, index=False)
    print(f"[OK] Cleaned CSV -> {CSV_CLEAN_OUT.resolve()}")

    # Quick schema echo
    print("\n[Schema] clean_survey_data.csv dtypes:")
    print(df.dtypes)


# -------------------------------
# Part 2 — Task 4: Normalize JSON
# -------------------------------
def normalize_json():
    with JSON_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    norm = pd.json_normalize(
        data,
        record_path=["instructors"],
        meta=["course_id", "title", "level", "section"],
        errors="ignore",  # <- this allows rows without 'section' (fills NaN)
    )

    cols_order = ["course_id", "title", "level", "section", "name", "role"]
    norm = norm.reindex(columns=cols_order)

    norm.to_csv(JSON_NORM_OUT, index=False)
    print(f"[OK] Normalized JSON -> {JSON_NORM_OUT.resolve()}")
    print("\n[Preview] clean_course_catalog.csv head():")
    print(norm.head())


def main():
    # Part 1
    create_tabular_csv()
    create_hierarchical_json()

    # Part 2
    clean_and_validate_csv()
    normalize_json()

    print("\nDone. Part 1 and Part 2 artifacts are ready.")


if __name__ == "__main__":
    main()