This schema documents the columns in `clean_survey_data.csv` after enforcing types.

| Column Name | Required Data Type | Brief Description |
| :--- | :--- | :--- |
| `student_id`   | `INT`           | Unique identifier for the student. |
| `major`        | `VARCHAR(50)`   | Student’s declared major. (Free-text; sized for typical multi-word majors.) |
| `GPA`          | `FLOAT`         | Cumulative grade point average on a 0–4 scale. |
| `is_cs_major`  | `BOOL`          | Whether the student is a Computer Science major (`TRUE`/`FALSE`). |
| `credits_taken`| `FLOAT`         | Total academic credits completed/taken to date. |