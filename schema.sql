-- ============================================================
-- CS 348 Project — Database Schema (Stage 2 Deliverable #1)
-- Application: Student Clubs / Meetings Management
-- Database system: SQLite (relational; supports queries,
-- transactions, and indexes — satisfies the FAQ requirements).
--
-- Design follows the Stage 1 sample schema:
--   Students, Clubs, Rooms, Meetings, MeetingOrganizers
-- ============================================================

PRAGMA foreign_keys = ON;

-- Drop in dependency order (children before parents) for clean re-init.
DROP TABLE IF EXISTS meeting_organizer;
DROP TABLE IF EXISTS meeting;
DROP TABLE IF EXISTS student;
DROP TABLE IF EXISTS club;
DROP TABLE IF EXISTS room;

-- ------------------------------------------------------------
-- student: people who can organize meetings or be invited.
-- ------------------------------------------------------------
CREATE TABLE student (
    student_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    email       TEXT    NOT NULL UNIQUE
);

-- ------------------------------------------------------------
-- club: organizes meetings. Populates the club drop-down.
-- ------------------------------------------------------------
CREATE TABLE club (
    club_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    address     TEXT,
    description TEXT
);

-- ------------------------------------------------------------
-- room: where a meeting is held. Populates the room drop-down.
-- ------------------------------------------------------------
CREATE TABLE room (
    room_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    building      TEXT    NOT NULL,
    number        TEXT    NOT NULL,
    max_capacity  INTEGER NOT NULL CHECK (max_capacity > 0),
    UNIQUE (building, number)
);

-- ------------------------------------------------------------
-- meeting: the MAIN table for Requirement 1 (add/edit/delete).
-- invited_count / accepted_count / attended_count feed the
-- report statistics in Requirement 2 (attendance rate, etc.).
-- ------------------------------------------------------------
CREATE TABLE meeting (
    meeting_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_date   TEXT    NOT NULL,                 -- ISO 'YYYY-MM-DD'
    meeting_time   TEXT    NOT NULL,                 -- 'HH:MM'
    duration       INTEGER NOT NULL CHECK (duration > 0),   -- minutes
    description    TEXT    NOT NULL,
    club_id        INTEGER NOT NULL,
    room_id        INTEGER NOT NULL,
    invited_count  INTEGER NOT NULL DEFAULT 0 CHECK (invited_count  >= 0),
    accepted_count INTEGER NOT NULL DEFAULT 0 CHECK (accepted_count >= 0),
    attended_count INTEGER NOT NULL DEFAULT 0 CHECK (attended_count >= 0),
    FOREIGN KEY (club_id) REFERENCES club(club_id),
    FOREIGN KEY (room_id) REFERENCES room(room_id)
);

-- ------------------------------------------------------------
-- meeting_organizer: junction table (many-to-many meeting<->student).
-- Editing a meeting's organizers adds/removes rows here — this is
-- the "supporting table" part of Requirement 1.
-- Composite PK prevents listing the same organizer twice.
-- ------------------------------------------------------------
CREATE TABLE meeting_organizer (
    meeting_id  INTEGER NOT NULL,
    student_id  INTEGER NOT NULL,
    PRIMARY KEY (meeting_id, student_id),
    FOREIGN KEY (meeting_id) REFERENCES meeting(meeting_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE
);

-- ============================================================
-- INDEXES (discussed in Stage 3, deliverable 1.b)
-- ============================================================

-- The report filters meetings by a date range -> index the date so
-- "meetings BETWEEN start AND end" can seek instead of full-scan.
CREATE INDEX idx_meeting_date ON meeting (meeting_date);

-- The report also filters by club and by room (drop-downs). These
-- indexes support those equality filters and the FK joins.
CREATE INDEX idx_meeting_club ON meeting (club_id);
CREATE INDEX idx_meeting_room ON meeting (room_id);

-- When editing/deleting a meeting we look up its organizers by
-- student; index student_id so ON DELETE CASCADE and organizer
-- lookups are fast (the PK already covers meeting_id first).
CREATE INDEX idx_organizer_student ON meeting_organizer (student_id);
