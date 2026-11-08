"""
CS 348 Project — Flask application.
Application: Student Clubs / Meetings Management.

Requirement 1 : Add / Edit / Delete a MEETING (main table), including
                choosing one or more organizers, which adds/edits/deletes
                rows in the supporting `meeting_organizer` table.

Requirement 2 : A report that filters meetings by a DATE RANGE + CLUB +
                ROOM (drop-downs built DYNAMICALLY from the database) and
                shows matching meetings plus statistics (avg duration,
                avg invited, avg accepted, avg attendance rate).

Security : every SQL statement that uses user input is a PARAMETERIZED
           query ("?" placeholders) — the driver binds the values, so
           input can never be interpreted as SQL (SQL-injection
           protection, Stage 3 deliverable 1.a).

Transactions : multi-step writes (a meeting + its organizer rows) are
               wrapped in a single explicit transaction with
               commit()/rollback(), so a partial failure leaves the
               database unchanged (Stage 3 deliverable 1.c).
"""

from flask import Flask, render_template, request, redirect, url_for, flash

import db

app = Flask(__name__)
app.config["SECRET_KEY"] = "cs348-dev-secret"  # needed for flash() messages
db.init_app(app)


# ---------------------------------------------------------------------------
# Home — list all meetings (landing page for Requirement 1).
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    conn = db.get_db()
    # Join to club/room so the list shows names, not raw IDs.
    meetings = conn.execute(
        "SELECT m.meeting_id, m.meeting_date, m.meeting_time, m.duration, "
        "       m.description, c.name AS club_name, "
        "       r.building || ' ' || r.number AS room_name "
        "FROM meeting m "
        "JOIN club c ON c.club_id = m.club_id "
        "JOIN room r ON r.room_id = m.room_id "
        "ORDER BY m.meeting_date, m.meeting_time"
    ).fetchall()
    return render_template("index.html", meetings=meetings)


# ---------------------------------------------------------------------------
# Helpers: fetch drop-down data from the DB (used by the meeting form).
# ---------------------------------------------------------------------------
def _form_choices(conn):
    clubs = conn.execute(
        "SELECT club_id, name FROM club ORDER BY name"
    ).fetchall()
    rooms = conn.execute(
        "SELECT room_id, building, number FROM room ORDER BY building, number"
    ).fetchall()
    students = conn.execute(
        "SELECT student_id, name FROM student ORDER BY name"
    ).fetchall()
    return clubs, rooms, students


# ---------------------------------------------------------------------------
# Requirement 1 — CREATE a meeting (+ its organizer rows).
# ---------------------------------------------------------------------------
@app.route("/meetings/add", methods=["GET", "POST"])
def add_meeting():
    conn = db.get_db()

    if request.method == "POST":
        form = request.form
        # request.form.getlist -> all checked organizer student_ids.
        organizer_ids = form.getlist("organizers")

        try:
            # One transaction for the meeting AND its organizer rows.
            cur = conn.execute(
                "INSERT INTO meeting "
                "(meeting_date, meeting_time, duration, description, "
                " club_id, room_id, invited_count, accepted_count, "
                " attended_count) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    form["meeting_date"], form["meeting_time"],
                    form["duration"], form["description"].strip(),
                    form["club_id"], form["room_id"],
                    form.get("invited_count", 0),
                    form.get("accepted_count", 0),
                    form.get("attended_count", 0),
                ),
            )
            meeting_id = cur.lastrowid
            for sid in organizer_ids:
                conn.execute(
                    "INSERT INTO meeting_organizer (meeting_id, student_id) "
                    "VALUES (?, ?)",
                    (meeting_id, sid),
                )
            conn.commit()  # commit meeting + organizers together
            flash("Meeting created.", "success")
        except Exception as exc:
            conn.rollback()  # undo the whole thing on any error
            flash(f"Could not create meeting: {exc}", "error")
        return redirect(url_for("index"))

    clubs, rooms, students = _form_choices(conn)
    return render_template(
        "meeting_form.html",
        meeting=None, clubs=clubs, rooms=rooms, students=students,
        selected_organizers=set(),
    )


# ---------------------------------------------------------------------------
# Requirement 1 — UPDATE a meeting (+ replace its organizer rows).
# ---------------------------------------------------------------------------
@app.route("/meetings/<int:meeting_id>/edit", methods=["GET", "POST"])
def edit_meeting(meeting_id):
    conn = db.get_db()

    if request.method == "POST":
        form = request.form
        organizer_ids = form.getlist("organizers")
        try:
            conn.execute(
                "UPDATE meeting SET "
                " meeting_date = ?, meeting_time = ?, duration = ?, "
                " description = ?, club_id = ?, room_id = ?, "
                " invited_count = ?, accepted_count = ?, attended_count = ? "
                "WHERE meeting_id = ?",
                (
                    form["meeting_date"], form["meeting_time"],
                    form["duration"], form["description"].strip(),
                    form["club_id"], form["room_id"],
                    form.get("invited_count", 0),
                    form.get("accepted_count", 0),
                    form.get("attended_count", 0),
                    meeting_id,
                ),
            )
            # Replace organizers: delete old rows, insert the new set.
            conn.execute(
                "DELETE FROM meeting_organizer WHERE meeting_id = ?",
                (meeting_id,),
            )
            for sid in organizer_ids:
                conn.execute(
                    "INSERT INTO meeting_organizer (meeting_id, student_id) "
                    "VALUES (?, ?)",
                    (meeting_id, sid),
                )
            conn.commit()
            flash("Meeting updated.", "success")
        except Exception as exc:
            conn.rollback()
            flash(f"Could not update meeting: {exc}", "error")
        return redirect(url_for("index"))

    meeting = conn.execute(
        "SELECT * FROM meeting WHERE meeting_id = ?", (meeting_id,)
    ).fetchone()
    if meeting is None:
        flash("Meeting not found.", "error")
        return redirect(url_for("index"))

    selected = {
        row["student_id"]
        for row in conn.execute(
            "SELECT student_id FROM meeting_organizer WHERE meeting_id = ?",
            (meeting_id,),
        ).fetchall()
    }
    clubs, rooms, students = _form_choices(conn)
    return render_template(
        "meeting_form.html",
        meeting=meeting, clubs=clubs, rooms=rooms, students=students,
        selected_organizers=selected,
    )


# ---------------------------------------------------------------------------
# Requirement 1 — DELETE a meeting (organizer rows cascade away).
# ---------------------------------------------------------------------------
@app.route("/meetings/<int:meeting_id>/delete", methods=["POST"])
def delete_meeting(meeting_id):
    conn = db.get_db()
    try:
        conn.execute("DELETE FROM meeting WHERE meeting_id = ?", (meeting_id,))
        conn.commit()
        flash("Meeting deleted.", "success")
    except Exception as exc:
        conn.rollback()
        flash(f"Could not delete meeting: {exc}", "error")
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Requirement 2 — FILTER + REPORT with statistics.
#   Filters: date range (from/to), club, room.
#   Drop-downs for club & room are built from the DB (point c).
# ---------------------------------------------------------------------------
@app.route("/report")
def report():
    conn = db.get_db()

    # Dynamic drop-down data — queried from the DB every request.
    clubs = conn.execute(
        "SELECT club_id, name FROM club ORDER BY name"
    ).fetchall()
    rooms = conn.execute(
        "SELECT room_id, building, number FROM room ORDER BY building, number"
    ).fetchall()

    # Filter inputs (empty string = no filter on that field).
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")
    club_id = request.args.get("club_id", "")
    room_id = request.args.get("room_id", "")

    # Build WHERE clause dynamically but ALWAYS with placeholders.
    where = []
    params = []
    if date_from:
        where.append("m.meeting_date >= ?")
        params.append(date_from)
    if date_to:
        where.append("m.meeting_date <= ?")
        params.append(date_to)
    if club_id:
        where.append("m.club_id = ?")
        params.append(club_id)
    if room_id:
        where.append("m.room_id = ?")
        params.append(room_id)
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    # Detail rows for the report.
    results = conn.execute(
        "SELECT m.meeting_id, m.meeting_date, m.meeting_time, m.duration, "
        "       m.description, c.name AS club_name, "
        "       r.building || ' ' || r.number AS room_name, "
        "       m.invited_count, m.accepted_count, m.attended_count "
        "FROM meeting m "
        "JOIN club c ON c.club_id = m.club_id "
        "JOIN room r ON r.room_id = m.room_id "
        f"{where_sql} "
        "ORDER BY m.meeting_date, m.meeting_time",
        params,
    ).fetchall()

    # Statistics (computed in SQL with the same filters/params).
    stats = conn.execute(
        "SELECT COUNT(*) AS n, "
        "       AVG(m.duration)       AS avg_duration, "
        "       AVG(m.invited_count)  AS avg_invited, "
        "       AVG(m.accepted_count) AS avg_accepted, "
        "       AVG(CASE WHEN m.invited_count > 0 "
        "                THEN 1.0 * m.attended_count / m.invited_count END) "
        "           AS avg_attendance_rate "
        "FROM meeting m "
        f"{where_sql}",
        params,
    ).fetchone()

    return render_template(
        "report.html",
        clubs=clubs, rooms=rooms, results=results, stats=stats,
        filters={
            "date_from": date_from, "date_to": date_to,
            "club_id": club_id, "room_id": room_id,
        },
    )


if __name__ == "__main__":
    app.run(debug=True)
