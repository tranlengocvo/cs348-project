-- ============================================================
-- Sample data so the app and report have content to show.
-- (AI assisted in generating this sample data; values reviewed.)
-- ============================================================

INSERT INTO employee (name, email, department) VALUES
    ('Alice Johnson', 'alice@acme.com',  'Engineering'),
    ('Bob Smith',     'bob@acme.com',    'Sales'),
    ('Carla Nguyen',  'carla@acme.com',  'Engineering'),
    ('David Lee',     'david@acme.com',  'Marketing'),
    ('Emma Garcia',   'emma@acme.com',   'Finance');

INSERT INTO category (name) VALUES
    ('Laptop'),
    ('Monitor'),
    ('Mouse'),
    ('Keyboard'),
    ('Docking Station'),
    ('Phone');

INSERT INTO tag (name) VALUES
    ('remote'),
    ('loaner'),
    ('under_warranty'),
    ('high_value'),
    ('needs_repair');

-- Assets: (asset_name, serial, category_id, assigned_to, purchase_date,
--          price, status)
INSERT INTO asset
    (asset_name, serial_number, category_id, assigned_to,
     purchase_date, price, status) VALUES
    ('Dell XPS 13',        'SN-LT-0001', 1, 1, '2024-01-15', 1399.00, 'in_use'),
    ('MacBook Pro 14',     'SN-LT-0002', 1, 3, '2025-03-10', 2199.00, 'in_use'),
    ('Lenovo ThinkPad',    'SN-LT-0003', 1, NULL, '2023-06-01', 1250.00, 'in_stock'),
    ('Dell U2723QE 27"',   'SN-MN-0001', 2, 1, '2024-02-20',  589.00, 'in_use'),
    ('LG 24" Monitor',     'SN-MN-0002', 2, 2, '2022-11-05',  199.00, 'in_use'),
    ('Logitech MX Master', 'SN-MS-0001', 3, 3, '2025-01-08',  99.00,  'in_use'),
    ('Keychron K2',        'SN-KB-0001', 4, 4, '2024-09-12',  89.00,  'in_use'),
    ('CalDigit TS4 Dock',  'SN-DK-0001', 5, 1, '2025-05-01',  379.00, 'in_use'),
    ('iPhone 15',          'SN-PH-0001', 6, 2, '2024-10-18',  999.00, 'in_use'),
    ('Old Dell Latitude',  'SN-LT-0004', 1, NULL, '2019-04-22', 800.00, 'retired');

-- Tags per asset (asset_id, tag_id).
INSERT INTO asset_tag (asset_id, tag_id) VALUES
    (1, 1), (1, 3),            -- XPS 13: remote, under_warranty
    (2, 3), (2, 4),            -- MacBook: under_warranty, high_value
    (3, 2),                    -- ThinkPad: loaner
    (4, 4),                    -- U2723QE: high_value
    (6, 1),                    -- MX Master: remote
    (9, 1), (9, 4),            -- iPhone: remote, high_value
    (10, 5);                   -- Old Latitude: needs_repair
