"""
CS 348 Project — Flask application.
Application: IT Asset Management (company digital assets such as
             laptops, monitors, and mice assigned to employees).

Requirement 1 : Add / Edit / Delete an ASSET (main table), including
                attaching one or more tags, which adds/edits/deletes
                rows in the supporting `asset_tag` table.

Requirement 2 : A report that filters assets by a PURCHASE-DATE RANGE +
                PRICE RANGE + CATEGORY (drop-down built DYNAMICALLY from
                the database) and shows matching assets plus statistics
                (count, average price, total value, average age in years).

Security : every SQL statement that uses user input is a PARAMETERIZED
           query ("?" placeholders) — the driver binds the values, so
           input can never be interpreted as SQL (SQL-injection
           protection, Stage 3 deliverable 1.a).

Transactions : multi-step writes (an asset + its tag rows) are wrapped
               in a single explicit transaction with commit()/rollback(),
               so a partial failure leaves the database unchanged
               (Stage 3 deliverable 1.c).
"""

# pyright: reportMissingImports=false
from flask import Flask, render_template, request, redirect, url_for, flash

import db

app = Flask(__name__)
app.config["SECRET_KEY"] = "cs348-dev-secret"  # needed for flash() messages
db.init_app(app)

# ---------------------------------------------------------------------------
# Home — list all assets (landing page for Requirement 1).
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    conn = db.get_db()
    # Join to category/employee so the list shows names, not raw IDs.
    assets = conn.execute(
        "SELECT a.asset_id, a.asset_name, a.serial_number, "
        "       a.purchase_date, a.price, a.status, "
        "       c.name AS category_name, "
        "       e.name AS employee_name "
        "FROM asset a "
        "JOIN category c ON c.category_id = a.category_id "
        "LEFT JOIN employee e ON e.employee_id = a.assigned_to "
        "ORDER BY a.asset_name"
    ).fetchall()
    return render_template("index.html", assets=assets)

# ---------------------------------------------------------------------------
# Helpers: fetch drop-down data from the DB (used by the asset form).
# ---------------------------------------------------------------------------
def _form_choices(conn):
    categories = conn.execute(
        "SELECT category_id, name FROM category ORDER BY name"
    ).fetchall()
    employees = conn.execute(
        "SELECT employee_id, name, department FROM employee ORDER BY name"
    ).fetchall()
    tags = conn.execute(
        "SELECT tag_id, name FROM tag ORDER BY name"
    ).fetchall()
    return categories, employees, tags

# ---------------------------------------------------------------------------
# Requirement 1 — CREATE an asset (+ its tag rows).
# ---------------------------------------------------------------------------
@app.route("/assets/add", methods=["GET", "POST"])
def add_asset():
    conn = db.get_db()

    if request.method == "POST":
        form = request.form
        # request.form.getlist -> all checked tag ids.
        tag_ids = form.getlist("tags")
        # An empty "assigned_to" means the asset is in stock (NULL).
        assigned_to = form.get("assigned_to") or None

        try:
            # One transaction for the asset AND its tag rows.
            cur = conn.execute(
                "INSERT INTO asset "
                "(asset_name, serial_number, category_id, assigned_to, "
                " purchase_date, price, status) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    form["asset_name"].strip(),
                    form["serial_number"].strip(),
                    form["category_id"], assigned_to,
                    form["purchase_date"], form["price"],
                    form["status"],
                ),
            )
            asset_id = cur.lastrowid
            for tid in tag_ids:
                conn.execute(
                    "INSERT INTO asset_tag (asset_id, tag_id) VALUES (?, ?)",
                    (asset_id, tid),
                )
            conn.commit()  # commit asset + tags together
            flash("Asset created.", "success")
        except Exception as exc:
            conn.rollback()  # undo the whole thing on any error
            flash(f"Could not create asset: {exc}", "error")
        return redirect(url_for("index"))

    categories, employees, tags = _form_choices(conn)
    return render_template(
        "asset_form.html",
        asset=None, categories=categories, employees=employees, tags=tags,
        selected_tags=set(),
    )

# ---------------------------------------------------------------------------
# Requirement 1 — UPDATE an asset (+ replace its tag rows).
# ---------------------------------------------------------------------------
@app.route("/assets/<int:asset_id>/edit", methods=["GET", "POST"])
def edit_asset(asset_id):
    conn = db.get_db()

    if request.method == "POST":
        form = request.form
        tag_ids = form.getlist("tags")
        assigned_to = form.get("assigned_to") or None
        try:
            conn.execute(
                "UPDATE asset SET "
                " asset_name = ?, serial_number = ?, category_id = ?, "
                " assigned_to = ?, purchase_date = ?, price = ?, status = ? "
                "WHERE asset_id = ?",
                (
                    form["asset_name"].strip(),
                    form["serial_number"].strip(),
                    form["category_id"], assigned_to,
                    form["purchase_date"], form["price"],
                    form["status"], asset_id,
                ),
            )
            # Replace tags: delete old rows, insert the new set.
            conn.execute(
                "DELETE FROM asset_tag WHERE asset_id = ?", (asset_id,)
            )
            for tid in tag_ids:
                conn.execute(
                    "INSERT INTO asset_tag (asset_id, tag_id) VALUES (?, ?)",
                    (asset_id, tid),
                )
            conn.commit()
            flash("Asset updated.", "success")
        except Exception as exc:
            conn.rollback()
            flash(f"Could not update asset: {exc}", "error")
        return redirect(url_for("index"))

    asset = conn.execute(
        "SELECT * FROM asset WHERE asset_id = ?", (asset_id,)
    ).fetchone()
    if asset is None:
        flash("Asset not found.", "error")
        return redirect(url_for("index"))

    selected = {
        row["tag_id"]
        for row in conn.execute(
            "SELECT tag_id FROM asset_tag WHERE asset_id = ?", (asset_id,)
        ).fetchall()
    }
    categories, employees, tags = _form_choices(conn)
    return render_template(
        "asset_form.html",
        asset=asset, categories=categories, employees=employees, tags=tags,
        selected_tags=selected,
    )

# ---------------------------------------------------------------------------
# Requirement 1 — DELETE an asset (tag rows cascade away).
# ---------------------------------------------------------------------------
@app.route("/assets/<int:asset_id>/delete", methods=["POST"])
def delete_asset(asset_id):
    conn = db.get_db()
    try:
        conn.execute("DELETE FROM asset WHERE asset_id = ?", (asset_id,))
        conn.commit()
        flash("Asset deleted.", "success")
    except Exception as exc:
        conn.rollback()
        flash(f"Could not delete asset: {exc}", "error")
    return redirect(url_for("index"))

# ---------------------------------------------------------------------------
# Requirement 2 — FILTER + REPORT with statistics.
#   Filters: purchase-date range (from/to), price range (min/max), category.
#   The category drop-down is built from the DB (point c).
# ---------------------------------------------------------------------------
@app.route("/report")
def report():
    conn = db.get_db()

    # Dynamic drop-down data — queried from the DB every request.
    categories = conn.execute(
        "SELECT category_id, name FROM category ORDER BY name"
    ).fetchall()

    # Filter inputs (empty string = no filter on that field).
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")
    min_price = request.args.get("min_price", "")
    max_price = request.args.get("max_price", "")
    category_id = request.args.get("category_id", "")

    # Build WHERE clause dynamically but ALWAYS with placeholders.
    where = []
    params = []
    if date_from:
        where.append("a.purchase_date >= ?")
        params.append(date_from)
    if date_to:
        where.append("a.purchase_date <= ?")
        params.append(date_to)
    if min_price:
        where.append("a.price >= ?")
        params.append(min_price)
    if max_price:
        where.append("a.price <= ?")
        params.append(max_price)
    if category_id:
        where.append("a.category_id = ?")
        params.append(category_id)
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    # Detail rows for the report.
    results = conn.execute(
        "SELECT a.asset_id, a.asset_name, a.serial_number, "
        "       a.purchase_date, a.price, a.status, "
        "       c.name AS category_name, "
        "       e.name AS employee_name "
        "FROM asset a "
        "JOIN category c ON c.category_id = a.category_id "
        "LEFT JOIN employee e ON e.employee_id = a.assigned_to "
        f"{where_sql} "
        "ORDER BY a.purchase_date DESC",
        params,
    ).fetchall()

    # Statistics (computed in SQL with the same filters/params).
    # Average age in years uses julianday() to compare against today.
    stats = conn.execute(
        "SELECT COUNT(*) AS n, "
        "       AVG(a.price)  AS avg_price, "
        "       SUM(a.price)  AS total_value, "
        "       AVG((julianday('now') - julianday(a.purchase_date)) / 365.0) "
        "           AS avg_age_years "
        "FROM asset a "
        f"{where_sql}",
        params,
    ).fetchone()

    return render_template(
        "report.html",
        categories=categories, results=results, stats=stats,
        filters={
            "date_from": date_from, "date_to": date_to,
            "min_price": min_price, "max_price": max_price,
            "category_id": category_id,
        },
    )

if __name__ == "__main__":
    app.run(debug=True)
