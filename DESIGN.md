# CS 348 Project — Database Design (Stage 2, Deliverable 1)

**Application:** IT Asset Management — tracking company digital assets
(laptops, monitors, mice, etc.) and which employee each is assigned to.
**Database system:** SQLite (relational; supports SQL, transactions, and indexes)

An ERD is not required. The full DDL is in [`schema.sql`](schema.sql).

## Tables, primary keys, and foreign keys

| Table | Primary key | Foreign keys | Purpose |
|-------|-------------|--------------|---------|
| `employee` | `employee_id` | — | Staff an asset can be assigned to. Populates the "assigned to" drop-down. |
| `category` | `category_id` | — | Asset type (Laptop, Monitor, ...). Populates the category drop-down. |
| `tag` | `tag_id` | — | Free-form labels (remote, loaner, high_value, ...). |
| `asset` | `asset_id` | `category_id → category`, `assigned_to → employee` | **Main table** (Requirement 1). `purchase_date` and `price` feed the report statistics. `assigned_to` may be NULL (asset in stock). |
| `asset_tag` | `(asset_id, tag_id)` composite | `asset_id → asset` (CASCADE), `tag_id → tag` (CASCADE) | Junction table: many-to-many between assets and tags (the "supporting table" in Requirement 1). |

### Key design decisions (be ready to justify these in the demo)

- **Junction table `asset_tag`** models the many-to-many relationship (an asset can have several tags; a tag can apply to many assets). Its **composite primary key** `(asset_id, tag_id)` prevents attaching the same tag twice.
- **`ON DELETE CASCADE`** on the junction table's foreign keys means deleting an asset (or a tag) automatically removes the related `asset_tag` rows, so there are never orphaned rows. (SQLite needs `PRAGMA foreign_keys = ON` per connection for this — see `db.py`.)
- **Nullable `assigned_to`** lets an asset exist without an owner (in stock / retired), modeled with a nullable foreign key.
- **`CHECK` constraints** keep data valid: `price >= 0` and `status IN ('in_use','in_stock','retired')`.

## Indexes (detailed in STAGE3.md)

- `idx_asset_purchase_date` on `asset(purchase_date)`
- `idx_asset_category` on `asset(category_id)`
- `idx_asset_assigned` on `asset(assigned_to)`
- `idx_asset_tag_tag` on `asset_tag(tag_id)`
