# CS 348 Project — Database Design (Stage 2, Deliverable 1)

**Application:** Student Clubs / Meetings Management
**Database system:** SQLite (relational; supports SQL, transactions, and indexes)

An ERD is not required. The full DDL is in [`schema.sql`](schema.sql).

## Tables, primary keys, and foreign keys

| Table | Primary key | Foreign keys | Purpose |
|-------|-------------|--------------|---------|
| `student` | `student_id` | — | People who organize or are invited to meetings. |
| `club` | `club_id` | — | Clubs that organize meetings. Populates the club drop-down. |
| `room` | `room_id` | — | Rooms where meetings are held. Populates the room drop-down. |
| `meeting` | `meeting_id` | `club_id → club`, `room_id → room` | **Main table** (Requirement 1). Holds invited/accepted/attended counts used by the report statistics. |
| `meeting_organizer` | `(meeting_id, student_id)` composite | `meeting_id → meeting` (CASCADE), `student_id → student` (CASCADE) | Junction table: many-to-many between meetings and their organizers (the "supporting table" in Requirement 1). |

### Key design decisions (be ready to justify these in the demo)

- **Junction table `meeting_organizer`** models the many-to-many relationship (a meeting can have several organizers; a student can organize many meetings). Its **composite primary key** `(meeting_id, student_id)` prevents listing the same organizer on a meeting twice.
- **`ON DELETE CASCADE`** on the junction table's foreign keys means deleting a meeting (or a student) automatically removes the related organizer rows, so there are never orphaned rows. (SQLite needs `PRAGMA foreign_keys = ON` per connection for this — see `db.py`.)
- **`CHECK` constraints** keep data valid: `duration > 0`, `max_capacity > 0`, and the count columns `>= 0`.
- **Denormalized counts** (`invited_count`, `accepted_count`, `attended_count`) on `meeting` let the report compute statistics (averages, attendance rate) without extra tables, matching the Stage 1 sample schema.

## Indexes (detailed in STAGE3.md)

- `idx_meeting_date` on `meeting(meeting_date)`
- `idx_meeting_club` on `meeting(club_id)`
- `idx_meeting_room` on `meeting(room_id)`
- `idx_organizer_student` on `meeting_organizer(student_id)`
