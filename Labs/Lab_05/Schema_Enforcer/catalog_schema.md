This schema documents `clean_course_catalog.csv` created via `pd.json_normalize(..., record_path=['instructors'], meta=['course_id','title','level','section'])`.

| Column Name | Required Data Type | Brief Description |
| :--- | :--- | :--- |
| `course_id` | `VARCHAR(16)` | Course identifier (e.g., `DS2002`). |
| `title`     | `VARCHAR(100)` | Official course title. |
| `level`     | `INT` | Catalog level number (e.g., 100/200/300). |
| `section`   | `VARCHAR(10)` | Section code (e.g., `001`). May be empty for some rows. |
| `name`      | `VARCHAR(100)` | Instructor’s full name for this course/section row. |
| `role`      | `VARCHAR(20)`  | Instructor role for this row (e.g., `Primary`, `TA`). |