# CS 348 Project — Stage 3 Discussion

These are the talking points for the Stage 3 recorded demo. Every claim
below is backed by real code or by output you can reproduce.

---

## 1.a — SQL Injection protection

**Method: parameterized queries (bound parameters / "prepared statements").**

Every SQL statement that includes user input uses `?` placeholders, and
the values are passed as a separate tuple to `execute()`. The SQLite
driver binds the values, so user input is treated strictly as *data* and
can never be parsed as SQL.

Example — creating a meeting (`app.py`, `add_meeting`):

```python
conn.execute(
    "INSERT INTO meeting (meeting_date, meeting_time, duration, ...) "
    "VALUES (?, ?, ?, ?)",
    (form["meeting_date"], form["meeting_time"], form["duration"], ...),
)
```

Example — the report filters, built dynamically but still parameterized
(`app.py`, `report`):

```python
where, params = [], []
if club_id:
    where.append("m.club_id = ?")   # placeholder, not the value
    params.append(club_id)          # value bound separately
...
conn.execute(f"SELECT ... {where_sql} ...", params)
```

Note that we only ever concatenate the *static* SQL fragment
(`"m.club_id = ?"`), never the user value itself.

**Proof (reproducible):** sending a malicious `club_id` such as
`1); DROP TABLE meeting;--` to `/report` does **not** drop the table —
the string is bound as a value and the `meeting` table still exists.
This is demonstrated by the SQL-injection probe in the test run.

---

## 1.b — Indexes

Indexes are declared in `schema.sql`. For each one, here is the query it
supports and where that query runs.

| Index | Column(s) | Supports | Used by |
|-------|-----------|----------|---------|
| `idx_meeting_date` | `meeting(meeting_date)` | Date-range filter `meeting_date BETWEEN ? AND ?` | **Report** (Requirement 2), "From date / To date" filter |
| `idx_meeting_club` | `meeting(club_id)` | Equality filter `club_id = ?` and the club join | **Report** club drop-down filter; meeting-list join to `club` |
| `idx_meeting_room` | `meeting(room_id)` | Equality filter `room_id = ?` and the room join | **Report** room drop-down filter; meeting-list join to `room` |
| `idx_organizer_student` | `meeting_organizer(student_id)` | Finding a student's organizer rows / `ON DELETE CASCADE` from `student` | Editing/deleting organizers in **Requirement 1** |

**Justification:** the report is the most frequent read and filters on
exactly date, club, and room — the three indexed columns. The organizer
index backs the cascade and organizer lookups done on every meeting edit.

**Proof (reproducible):** `EXPLAIN QUERY PLAN` shows the planner choosing
the indexes, e.g.:

```
SELECT * FROM meeting WHERE meeting_date BETWEEN ? AND ?
  -> SEARCH meeting USING INDEX idx_meeting_date (meeting_date>? AND meeting_date<?)

SELECT * FROM meeting WHERE club_id = ?
  -> SEARCH meeting USING INDEX idx_meeting_club (club_id=?)

SELECT * FROM meeting WHERE room_id = ?
  -> SEARCH meeting USING INDEX idx_meeting_room (room_id=?)
```

(Without the index the plan would say `SCAN meeting`, i.e. a full scan.)

---

## 1.c — Transactions, concurrency, and isolation level

**Where transactions matter:** creating or editing a meeting is a
*multi-statement* write — one `meeting` row **plus** several
`meeting_organizer` rows. These must all succeed or all fail; a meeting
with half its organizers saved would be inconsistent.

**Implementation** (`app.py`, `add_meeting` / `edit_meeting`):

```python
try:
    cur = conn.execute("INSERT INTO meeting ...")   # statement 1
    for sid in organizer_ids:
        conn.execute("INSERT INTO meeting_organizer ...")  # statements 2..n
    conn.commit()        # make all changes permanent together
except Exception:
    conn.rollback()      # on any failure, discard the whole batch
```

Python's `sqlite3` is configured with `isolation_level=""` (in `db.py`),
which keeps the DB-API default: a transaction is opened automatically
before the first `INSERT`/`UPDATE`/`DELETE`, and nothing is persisted
until `commit()`. So the loop above runs inside one transaction and
`rollback()` undoes every statement if an error occurs.

**Isolation level and concurrency:** SQLite serializes writers with a
database-level lock, so every transaction effectively runs at the
**SERIALIZABLE** isolation level — the strongest level, with no dirty
reads, non-repeatable reads, or phantoms. If this app were extended to
many concurrent users, the natural next step would be to open the write
transactions with `BEGIN IMMEDIATE` (acquire the write lock up front) to
avoid "database is locked" errors under contention, and/or enable WAL
mode (`PRAGMA journal_mode=WAL`) so readers don't block the writer.

*Verified against the Python `sqlite3` documentation and SQLite's
documentation on transaction/locking behavior.*

---

## AI Usage

(Required disclosure — discuss this in the recorded demo.)

- **Tool used:** an AI coding assistant.
- **Tasks it assisted with:** scaffolding the Flask routes and HTML
  templates, drafting the SQL schema and sample seed data, and drafting
  this documentation.
- **How I verified / modified the output:** I ran the app and a full
  end-to-end test (create → edit → delete a meeting, confirming the
  organizer rows and the `ON DELETE CASCADE` behavior), ran the report
  with filters, and ran a SQL-injection probe to confirm the table
  survives. I confirmed the indexes are actually used with
  `EXPLAIN QUERY PLAN`, and I cross-checked the Flask SQLite pattern and
  the `sqlite3` transaction/isolation behavior against the official
  documentation. I can explain and justify every design decision,
  index, the SQL-injection protection, and the transaction/isolation
  choices myself.
