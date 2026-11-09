-- ============================================================
-- CS 348 Project — Database Schema (Stage 2 Deliverable #1)
-- Application: IT Asset Management (company digital assets
--              such as laptops, mice, monitors assigned to
--              employees).
-- Database system: SQLite (relational; supports SQL,
-- transactions, and indexes — satisfies the FAQ requirements).
-- ============================================================

PRAGMA foreign_keys = ON;

-- Drop in dependency order (children before parents) for clean re-init.
DROP TABLE IF EXISTS asset_tag;
DROP TABLE IF EXISTS asset;
DROP TABLE IF EXISTS employee;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS tag;

-- ------------------------------------------------------------
-- employee: staff an asset can be assigned to.
-- Populates the "assigned employee" drop-down.
-- ------------------------------------------------------------
CREATE TABLE employee (
    employee_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT    NOT NULL,
    email        TEXT    NOT NULL UNIQUE,
    department   TEXT    NOT NULL
);

-- ------------------------------------------------------------
-- category: type of asset (Laptop, Monitor, Mouse, ...).
-- Populates the category drop-down (report + asset form).
-- ------------------------------------------------------------
CREATE TABLE category (
    category_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT    NOT NULL UNIQUE
);

-- ------------------------------------------------------------
-- tag: free-form labels (e.g. 'remote', 'loaner', 'warranty').
-- Many-to-many with asset via asset_tag.
-- ------------------------------------------------------------
CREATE TABLE tag (
    tag_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT    NOT NULL UNIQUE
);

-- ------------------------------------------------------------
-- asset: the MAIN table for Requirement 1 (add/edit/delete).
-- purchase_date + price feed the report statistics.
-- assigned_to may be NULL (an asset can be unassigned / in stock).
-- ------------------------------------------------------------
CREATE TABLE asset (
    asset_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_name     TEXT    NOT NULL,               -- e.g. 'Dell XPS 13'
    serial_number  TEXT    NOT NULL UNIQUE,
    category_id    INTEGER NOT NULL,
    assigned_to    INTEGER,                         -- NULL = in stock
    purchase_date  TEXT    NOT NULL,                -- ISO 'YYYY-MM-DD'
    price          REAL    NOT NULL CHECK (price >= 0),
    status         TEXT    NOT NULL DEFAULT 'in_use'
                    CHECK (status IN ('in_use', 'in_stock', 'retired')),
    FOREIGN KEY (category_id) REFERENCES category(category_id),
    FOREIGN KEY (assigned_to) REFERENCES employee(employee_id)
);

-- ------------------------------------------------------------
-- asset_tag: junction table (many-to-many asset <-> tag).
-- Editing an asset's tags adds/removes rows here — this is the
-- "supporting table" part of Requirement 1.
-- Composite PK prevents attaching the same tag twice.
-- ------------------------------------------------------------
CREATE TABLE asset_tag (
    asset_id  INTEGER NOT NULL,
    tag_id    INTEGER NOT NULL,
    PRIMARY KEY (asset_id, tag_id),
    FOREIGN KEY (asset_id) REFERENCES asset(asset_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id)   REFERENCES tag(tag_id)     ON DELETE CASCADE
);

-- ============================================================
-- INDEXES (discussed in Stage 3, deliverable 1.b)
-- ============================================================

-- The report filters assets by a purchase-date range -> index the
-- date so "purchase_date BETWEEN ? AND ?" can seek, not full-scan.
CREATE INDEX idx_asset_purchase_date ON asset (purchase_date);

-- The report filters by category (drop-down) -> index supports the
-- equality filter and the FK join to category.
CREATE INDEX idx_asset_category ON asset (category_id);

-- Listing/looking up assets by the employee they're assigned to.
CREATE INDEX idx_asset_assigned ON asset (assigned_to);

-- When editing/deleting a tag we look up its asset rows; index tag_id
-- (the PK already covers asset_id first) for the cascade and lookups.
CREATE INDEX idx_asset_tag_tag ON asset_tag (tag_id);
