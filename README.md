
---

# 📄 `README.md`
```markdown
# CS 348 Project — IT Asset Management

A database-backed Flask web app for tracking company digital assets
(laptops, monitors, mice, etc.) and which employee each is assigned to.
**Stack:** Python + Flask + SQLite.

- **Requirement 1** — add / edit / delete an *asset* (main table) and its
  *tags* (supporting junction table). Pages: `/`, `/assets/add`,
  `/assets/<id>/edit`, `/assets/<id>/delete`.
- **Requirement 2** — a *report* at `/report` that filters assets by
  purchase-date range, price range, and category (category drop-down built
  dynamically from the DB) and shows matching assets plus statistics
  (count, average price, total value, average age in years).

## Project layout

\```
app.py              Flask routes (CRUD + report). Parameterized queries + transactions.
db.py               Connection handling (Flask g pattern) + init-db command.
schema.sql          Tables, primary keys, foreign keys, indexes.
seed.sql            Sample data.
templates/          HTML (base, index, asset_form, report).
DESIGN.md           Stage 2 database-design writeup.
STAGE3.md           Stage 3: SQL injection, indexes, transactions, AI Usage.
\```

## Run it

\```bash
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt

flask --app app init-db              # create assets.db from schema.sql + seed.sql
flask --app app run --debug          # http://127.0.0.1:5000
\```

`flask --app app init-db` drops and recreates the tables, so you can reset to
a known state before the demo (e.g. to show a report "before" and "after"
changing data).

## Demo checklist (maps to the rubric)

1. **DB design** — walk through `schema.sql` / `DESIGN.md`.
2. **Requirement 1** — add an asset with tags, edit it, delete it;
   show the rows in `asset` and `asset_tag`.
3. **Requirement 2** — run the report, show statistics; change an asset's
   price (or add/retire an asset), re-run, and point out the report updated
   (before/after).
4. **Dynamic UI (point c)** — show that the category/employee/tag options come
   from DB queries in `app.py` (`_form_choices`, the `report` view), not
   hard-coded HTML.
5. **Stage 3** — walk through `STAGE3.md` (SQL injection, indexes with
   `EXPLAIN QUERY PLAN`, transactions/isolation, AI Usage).
