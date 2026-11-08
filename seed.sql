-- ============================================================
-- Sample data so the app and report have content to show.
-- (AI assisted in generating this sample data; values reviewed.)
-- ============================================================

INSERT INTO student (name, email) VALUES
    ('Alice Johnson', 'alice@purdue.edu'),
    ('Bob Smith',     'bob@purdue.edu'),
    ('Carla Nguyen',  'carla@purdue.edu'),
    ('David Lee',     'david@purdue.edu'),
    ('Emma Garcia',   'emma@purdue.edu'),
    ('Frank Miller',  'frank@purdue.edu');

INSERT INTO club (name, address, description) VALUES
    ('Robotics Club',       'EE Building',  'Builds and competes with robots'),
    ('Chess Club',          'Union 210',    'Weekly chess meetups and tournaments'),
    ('Data Science Society', 'LWSN 1142',   'Talks and workshops on data science'),
    ('Hiking Club',         'CoRec',        'Organizes weekend hikes');

INSERT INTO room (building, number, max_capacity) VALUES
    ('LWSN', '1142', 80),
    ('EE',   '129',  40),
    ('Union','210',  25),
    ('WALC', '1055', 120);

-- Meetings: (date, time, duration, description, club_id, room_id,
--            invited, accepted, attended)
INSERT INTO meeting
    (meeting_date, meeting_time, duration, description, club_id, room_id,
     invited_count, accepted_count, attended_count) VALUES
    ('2026-09-10', '18:00', 60,  'Kickoff meeting',          1, 2, 30, 24, 20),
    ('2026-09-17', '18:00', 90,  'Build session 1',          1, 2, 30, 18, 15),
    ('2026-09-12', '19:00', 45,  'Casual chess night',       2, 3, 20, 15, 14),
    ('2026-10-01', '17:30', 75,  'Intro to pandas workshop', 3, 1, 60, 45, 38),
    ('2026-10-08', '17:30', 120, 'ML guest speaker',         3, 4, 100, 70, 55),
    ('2026-10-04', '08:00', 300, 'Fall trail hike',          4, 1, 40, 30, 28),
    ('2026-11-05', '18:00', 60,  'Build session 2',          1, 2, 30, 22, 19);

-- Organizers for each meeting (meeting_id, student_id).
INSERT INTO meeting_organizer (meeting_id, student_id) VALUES
    (1, 1), (1, 2),
    (2, 1),
    (3, 3),
    (4, 4), (4, 5),
    (5, 4),
    (6, 6),
    (7, 2), (7, 1);
