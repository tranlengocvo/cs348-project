# CS 348 Project — Student Clubs & Meetings

A database-backed Flask web app. **Stack:** Python + Flask + SQLite.

- **Requirement 1** — add / edit / delete a *meeting* (main table) and its
  *organizers* (supporting junction table). Pages: `/`, `/meetings/add`,
  `/meetings/<id>/edit`, `/meetings/<id>/delete`.
- **Requirement 2** — a *report* at `/report` that filters meetings by date
  range, club, and room (drop-downs built dynamically from the DB) and shows
  matching meetings plus statistics (avg duration, avg invited, avg accepted,
  avg attendance rate).

## Project layout

```
app.py              Flask routes (CRUD + report). Parameterized queries + transactions.
db.py               Connection handling (Flask g pattern) + init-db command.
schema.sql          Tables, primary keys, foreign keys, indexes.
seed.sql            Sample data.
templates/          HTML (base, index, meeting_form, report).
DESIGN.md           Stage 2 database-design writeup.
STAGE3.md           Stage 3: SQL injection, indexes, transactions, AI Usage.
```

## Run it

```bash
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt

flask --app app init-db              # create clubs.db from schema.sql + seed.sql
flask --app app run --debug          # http://127.0.0.1:5000
```

`flask --app app init-db` drops and recreates the tables, so you can reset to
a known state before the demo (e.g. to show a report "before" and "after"
changing data).

## Demo checklist (maps to the rubric)

1. **DB design** — walk through `schema.sql` / `DESIGN.md`.
2. **Requirement 1** — create a meeting with organizers, edit it, delete it;
   show the rows in `meeting` and `meeting_organizer`.
3. **Requirement 2** — run the report, show statistics; change a meeting's
   counts, re-run, and point out the report updated (before/after).
4. **Dynamic UI (point c)** — show that the club/room/organizer options come
   from DB queries in `app.py` (`_form_choices`, the `report` view), not
   hard-coded HTML.
5. **Stage 3** — walk through `STAGE3.md` (SQL injection, indexes with
   `EXPLAIN QUERY PLAN`, transactions/isolation, AI Usage).
