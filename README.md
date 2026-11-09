# CS 348 Project — IT Asset Management

A database-backed Flask web app for tracking company digital assets (laptops, monitors, mice, etc.) and which employee each asset is assigned to.

**Stack:** Python + Flask + SQLite.

## Requirements

- **Requirement 1** — Add, edit, and delete an *asset* (main table) and its *tags* (supporting junction table).

  Pages:
  - `/`
  - `/assets/add`
  - `/assets/<id>/edit`
  - `/assets/<id>/delete`

- **Requirement 2** — A *report* at `/report` that filters assets by:
  - Purchase-date range
  - Price range
  - Category (drop-down dynamically populated from the database)

  The report displays matching assets and statistics:
  - Asset count
  - Average price
  - Total value
  - Average age in years

## Project Layout

```text
app.py              Flask routes (CRUD + report). Parameterized queries + transactions.
db.py               Connection handling (Flask g pattern) + init-db command.
schema.sql          Tables, primary keys, foreign keys, indexes.
seed.sql            Sample data.
templates/          HTML (base, index, asset_form, report).
DESIGN.md           Stage 2 database-design writeup.
STAGE3.md           Stage 3: SQL injection, indexes, transactions, AI Usage.
```

## Run It

```bash
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize the database
flask --app app init-db

# Run the application
flask --app app run --debug
```

Open the application at: http://127.0.0.1:5000

**Note:** `flask --app app init-db` drops and recreates the tables, so you can reset the database to a known state before the demo (e.g., to show a report before and after changing data).

## Demo Checklist (Maps to the Rubric)

1. **DB Design** — Walk through `schema.sql` and `DESIGN.md`.

2. **Requirement 1: Asset CRUD** — Add an asset with tags, edit it, and delete it. Show the corresponding rows in the `asset` and `asset_tag` tables.

3. **Requirement 2: Report** — Run the report and show its statistics. Change an asset's price (or add/retire an asset), rerun the report, and demonstrate that the report updates accordingly (before/after comparison).

4. **Dynamic UI (Point C)** — Show that the category, employee, and tag options come from database queries in `app.py` (`_form_choices` and the `report` view), rather than hard-coded HTML.

5. **Stage 3** — Walk through `STAGE3.md`, covering:
   - SQL injection prevention
   - Indexes using `EXPLAIN QUERY PLAN`
   - Transactions and isolation
   - AI Usage