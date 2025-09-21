# SQL Prettifier & Bracketizer Setup

Revision: September 2025

**keywords**: code-quality, data engineering, RDBMS

*contacts*: Markus von Steht

## Description

This README explains how to enforce consistent T-SQL formatting and mandatory bracketing of schema, table, and column identifiers in your repository using a Python script with `sqlglot` and SQLFluff, integrated via `pre-commit`.

---

## Folder Structure

```config
├─ .pre-commit-config.yaml
├─ requirements.txt
├─ scripts/
│  └─ bracketize_sql.py
└─ sql/
   └─ your_sql_files.sql
```

- `scripts/bracketize_sql.py`: Python script that brackets schema, table, and column names.
- `.pre-commit-config.yaml`: Pre-commit configuration to run the Python script and SQLFluff.
- `requirements.txt`: Python environment dependencies, including `sqlglot` and `sqlfluff`.
- `sql/`: Folder containing SQL files in your project.

---

## Step 1: Set up a Python environment

It is recommended to use a virtual environment to isolate dependencies.

```bash
# Create a virtual environment
python -m venv venv

# Activate the environment (macOS/Linux)
source venv/bin/activate

# Activate the environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

Ensure that `requirements.txt` includes at least:

```config
sqlglot
sqlfluff
pre-commit
```

---

## Step 2: Configure `.pre-commit-config.yaml`

Example configuration:

```yaml
repos:
  - repo: local
    hooks:
      - id: bracketize-sql
        name: Bracketize SQL Identifiers
        entry: python scripts/bracketize_sql.py
        language: python
        types: [sql]
        pass_filenames: true

      - id: sqlfluff-fix
        name: SQLFluff Auto-Fix
        entry: sqlfluff fix
        language: system
        types: [sql]
        pass_filenames: true
```

- The first hook brackets identifiers using the Python script.
- The second hook runs `sqlfluff fix` to enforce other formatting rules.

---

## Step 3: SQLFluff configuration

A sample `.sqlfluff` configuration file might look like:

```ini
[sqlfluff]
dialect = tsql
templater = jinja
exclude_rules = ambiguous.column_count, structure.column_order
max_line_length = 120
processes = -1

[sqlfluff:layout:type:comma]
line_position = leading

[sqlfluff:indentation]
allow_implicit_indents = True
indented_joins = True
indented_using_on = False

[sqlfluff:rules:aliasing.length]
min_alias_length = 3

[sqlfluff:rules:capitalisation.keywords]
capitalisation_policy = upper
[sqlfluff:rules:capitalisation.identifiers]
extended_capitalisation_policy = upper
[sqlfluff:rules:capitalisation.functions]
extended_capitalisation_policy = upper
[sqlfluff:rules:capitalisation.literals]
capitalisation_policy = lower
[sqlfluff:rules:capitalisation.types]
extended_capitalisation_policy = upper

[sqlfluff:rules:convention.not_equal]
preferred_not_equal_style = c_style

[sqlfluff:rules:references.quoting]
prefer_quoted_identifiers = False
prefer_quoted_keywords = False
```

This ensures SQLFluff runs with T-SQL dialect, your preferred capitalization, line lengths, and rule exclusions.

---

## Step 4: Install the pre-commit hooks

```bash
pre-commit install
```

This sets up Git to run the hooks automatically before each commit.

---

## Step 5: Test hooks manually (optional)

```bash
pre-commit run --all-files
```

Runs all hooks on all files in the repository, not just staged files.

---

## Step 6: Commit workflow

1. Stage SQL files:

    ```bash
    git add sql/my_script.sql
    ```

2. Commit changes:

    ```bash
    git commit -m "Add new view"
    ```

- Hooks run automatically:
  1. `bracketize_sql.py` brackets schema, table, and column identifiers.
  2. `sqlfluff fix` formats the SQL according to your SQLFluff configuration.
- If any files are modified by the hooks, Git will stop the commit. Re-add the modified files and commit again.

---

## Step 7: Skipping hooks (optional)

If necessary, skip pre-commit hooks for a commit:

```bash
git commit -m "Skip hooks" --no-verify
```

Use only when intentional.

---

## Notes

- The Python script preserves table/column aliases (e.g., `u`, `r`, `c`) unbracketed.
- Brackets are applied to schema names, table names, and column names.
- CTEs are handled correctly.
- Dynamic SQL inside strings is not parsed automatically.
- Ensure `sqlfluff` is installed in the same environment (`pip install sqlfluff`).
- You can adjust SQLFluff rules and preferences via `.sqlfluff` for capitalization, line length, and other style conventions.

---

This setup ensures your SQL code is consistent, readable, and follows SSMS-style bracketing conventions automatically.
