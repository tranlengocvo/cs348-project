# CS 348 Project — Stage 3 Discussion

Talking points for the Stage 3 recorded demo. Every claim below is backed
by real code or by reproducible output.
Application: **IT Asset Management**.

---

## 1.a — SQL Injection protection

**Method: parameterized queries (bound parameters / "prepared statements").**

Every SQL statement that includes user input uses `?` placeholders, and
the values are passed as a separate tuple to `execute()`. The SQLite
driver binds the values, so user input is treated strictly as *data* and
can never be parsed as SQL.

Example — creating an asset (`app.py`, `add_asset`):

```python
conn.execute(
    "INSERT INTO asset (asset_name, serial_number, category_id, ...) "
    "VALUES (?, ?, ?, ?, ?, ?, ?)",
    (form["asset_name"].strip(), form["serial_number"].strip(), ...),
)
```

Example — the report filters, built dynamically but still parameterized
(`app.py`, `report`):

```python
where, params = [], []
if category_id:
    where.append("a.category_id = ?")   # placeholder, not the value
    params.append(category_id)          # value bound separately
...
conn.execute(f"SELECT ... {where_sql} ...", params)
```

Only the *static* SQL fragment (`"a.category_id = ?"`) is ever
concatenated — never the user value itself.

**Proof (reproducible):** sending a malicious `category_id` such as
`1); DROP TABLE asset;--` to `/report` does **not** drop the table — the
string is bound as a value and the `asset` table still exists.

---

## 1.b — Indexes

Indexes are declared in `schema.sql`. For each one, here is the query it
supports and where that query runs.

| Index | Column(s) | Supports | Used by |
|-------|-----------|----------|---------|
| `idx_asset_purchase_date` | `asset(purchase_date)` | Date-range filter `purchase_date BETWEEN ? AND ?` | **Report** (Requirement 2), "Purchased from / to" filter |
| `idx_asset_category` | `asset(category_id)` | Equality filter `category_id = ?` and the category join | **Report** category drop-down filter; asset-list join to `category` |
| `idx_asset_assigned` | `asset(assigned_to)` | Looking up assets by the employee they're assigned to | Asset list / future "assets per employee" lookups |
| `idx_asset_tag_tag` | `asset_tag(tag_id)` | Finding a tag's asset rows / `ON DELETE CASCADE` from `tag` | Editing/deleting tags in **Requirement 1** |

**Justification:** the report is the most frequent read and filters on
purchase date, price, and category — the date and category columns are
indexed. The tag index backs the cascade and tag lookups on every edit.

**Proof (reproducible):** `EXPLAIN QUERY PLAN` shows the planner choosing
the indexes, e.g.:

```
SELECT * FROM asset WHERE purchase_date BETWEEN ? AND ?
  -> SEARCH asset USING INDEX idx_asset_purchase_date (purchase_date>? AND purchase_date<?)

SELECT * FROM asset WHERE category_id = ?
  -> SEARCH asset USING INDEX idx_asset_category (category_id=?)
```

(Without the index the plan would say `SCAN asset`, i.e. a full scan.)

---

## 1.c — Transactions, concurrency, and isolation level

**Where transactions matter:** creating or editing an asset is a
*multi-statement* write — one `asset` row **plus** several `asset_tag`
rows. These must all succeed or all fail; an asset with only half its
tags saved would be inconsistent.

**Implementation** (`app.py`, `add_asset` / `edit_asset`):

```python
try:
    cur = conn.execute("INSERT INTO asset ...")      # statement 1
    for tid in tag_ids:
        conn.execute("INSERT INTO asset_tag ...")    # statements 2..n
    conn.commit()        # make all changes permanent together
except Exception:
    conn.rollback()      # on any failure, discard the whole batch
```

Python's `sqlite3` is configured with `isolation_level=""` (in `db.py`),
keeping the DB-API default: a transaction opens automatically before the
first `INSERT`/`UPDATE`/`DELETE`, and nothing is persisted until
`commit()`. The loop above therefore runs in one transaction and
`rollback()` undoes every statement on error.

**Isolation level and concurrency:** SQLite serializes writers with a
database-level lock, so every transaction effectively runs at the
**SERIALIZABLE** isolation level — the strongest level, with no dirty
reads, non-repeatable reads, or phantoms. To scale to many concurrent
users, the natural next step is to open write transactions with
`BEGIN IMMEDIATE` (acquire the write lock up front) to avoid
"database is locked" errors, and/or enable WAL mode
(`PRAGMA journal_mode=WAL`) so readers don't block the writer.

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
  end-to-end test (create → edit → delete an asset, confirming the
  `asset_tag` rows and the `ON DELETE CASCADE` behavior), ran the report
  with filters, and ran a SQL-injection probe to confirm the table
  survives. I confirmed the indexes are actually used with
  `EXPLAIN QUERY PLAN`, and I cross-checked the Flask SQLite pattern and
  the `sqlite3` transaction/isolation behavior against the official
  documentation. I can explain and justify every design decision, index,
  the SQL-injection protection, and the transaction/isolation choices
  myself.
