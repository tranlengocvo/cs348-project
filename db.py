"""
db.py — Database connection + initialization helpers.

Uses the official Flask pattern for SQLite: open a connection lazily,
store it on the request-scoped `g` object, and close it when the app
context tears down.
Ref: https://flask.palletsprojects.com/en/stable/patterns/sqlite3/
"""

import os
import sqlite3

from flask import g

# Database file lives next to this script.
DATABASE = os.path.join(os.path.dirname(__file__), "clubs.db")


def get_db():
    """Return the request's SQLite connection, creating it on first use."""
    if "db" not in g:
        # isolation_level="DEFERRED" keeps Python's default behavior:
        # a transaction is opened automatically before INSERT/UPDATE/DELETE
        # so we can commit() / rollback() explicitly (see app.py
        # transactions).
        g.db = sqlite3.connect(DATABASE, isolation_level="DEFERRED")
        # Rows behave like dicts: row["first_name"] instead of row[0].
        g.db.row_factory = sqlite3.Row
        # Foreign keys are OFF by default in SQLite; turn them ON per
        # connection so ON DELETE CASCADE and FK checks actually work.
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db


def close_db(exception=None):
    """Close the connection at the end of the request, if one was opened."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """(Re)create all tables from schema.sql and load seed.sql sample data."""
    here = os.path.dirname(__file__)
    # Use a standalone connection — init runs outside a request context.
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON;")
    with open(os.path.join(here, "schema.sql"), "r") as f:
        conn.executescript(f.read())
    with open(os.path.join(here, "seed.sql"), "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def init_app(app):
    """Register close_db with the app and add a `flask init-db` CLI command."""
    app.teardown_appcontext(close_db)

    @app.cli.command("init-db")
    def init_db_command():
        init_db()
        print("Initialized the database (clubs.db).")
