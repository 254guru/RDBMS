# PesaPal RDBMS - Getting Started Guide

Step-by-step usage, short examples, and pointers for the PesaPal RDBMS. For a concise system reference, see `README.md`.

Prerequisites
-------------

- Python 3.8+ (validated with 3.12)
- Install Flask if you plan to run the web demo: `pip install flask`

Prepare
-------

```bash
chmod +x *.sh
./verify.sh        # optional health check
./launch.sh        # interactive menu and shortcuts
```

REPL (CLI)
----------

Start the REPL:

```bash
python3 main.py
```

Common SQL commands supported:

- `CREATE TABLE name (col INT PRIMARY KEY, ...)`
- `INSERT INTO name (cols) VALUES (values)`
- `SELECT * FROM name WHERE ...`
- `UPDATE name SET col = val WHERE ...`
- `DELETE FROM name WHERE ...`
- `SCHEMA <table>` — show schema
- `TABLES` — list tables

Example session:

```
CREATE TABLE merchants (id INT PRIMARY KEY, name TEXT UNIQUE, category TEXT)
INSERT INTO merchants (id, name, category) VALUES (1, 'Store A', 'Retail')
SELECT * FROM merchants
UPDATE merchants SET category = 'Retail Plus' WHERE id = 1
DELETE FROM merchants WHERE id = 1
```

Web Demo
--------

Run the Flask demo:

```bash
cd web_app && python3 app.py
```

Open `http://localhost:5000` to interact with the dynamic UI. The demo exposes a REST API:

- `GET /api/merchants` — list all merchants
- `GET /api/categories` — list all categories
- `POST /api/merchants` — add a merchant
- `GET /api/tables` — view database schema
- `POST /api/query` — execute custom SQL

### Web App Features

- **Merchants Tab**: View all merchants in a responsive grid. Click edit/delete buttons to modify or remove merchants.
- **Categories Tab**: Browse all available categories for organizing merchants.
- **SQL Query Tab**: Execute custom SQL queries with real-time result display. View database schema in a collapsible section.
- **Add Merchant Modal**: Click "Add Merchant" to open a modal form. Fill in merchant details and submit to add to database.
- **Edit Merchant Modal**: Click edit on any merchant card to update its details in a modal.
- **Delete Merchant Modal**: Click delete to confirm removal with a confirmation modal.
- **Real-time Refresh**: After adding/editing/deleting merchants, the list updates automatically within 500ms.

Programmatic usage
-------------------

Use the engine and parser in other Python scripts:

```python
from rdbms.storage import Database
from rdbms.parser import SQLParser
from rdbms.engine import ExecutionEngine

db = Database('./my_db')
parser = SQLParser()
engine = ExecutionEngine(db)

engine.execute(parser.parse('CREATE TABLE users (id INT PRIMARY KEY, name TEXT)'))
engine.execute(parser.parse('INSERT INTO users (id, name) VALUES (1, "Alice")'))
res = engine.execute(parser.parse('SELECT * FROM users'))
```

Notes & files
-------------

- Persistent JSON files are stored under `db/` and `web_app/db/` (ignored by `.gitignore`).
- Core modules: `rdbms/types.py`, `rdbms/storage.py`, `rdbms/parser.py`, `rdbms/engine.py`, `rdbms/repl.py`.
- Web app frontend: `web_app/static/script.js` (all client-side logic), `web_app/static/style.css` (modals and animations).
- For debugging and examples, see `example.py`.

---

## SQL Quick Reference

### Creating Tables

```sql
-- Basic table
CREATE TABLE merchants (id INT PRIMARY KEY, name TEXT)

-- With constraints
CREATE TABLE categories (
    id INT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT
)
```

### Inserting Data

```sql
-- Single row
INSERT INTO merchants (id, name) VALUES (1, 'Store A')

-- Multiple rows (run separately)
INSERT INTO merchants (id, name) VALUES (2, 'Store B')
INSERT INTO merchants (id, name) VALUES (3, 'Store C')

-- With boolean
INSERT INTO merchants (id, name, active) VALUES (4, 'Store D', true)
```

### Querying Data

```sql
-- Get all rows
SELECT * FROM merchants

-- Get specific columns
SELECT id, name FROM merchants

-- Filter with WHERE
SELECT * FROM merchants WHERE id = 1
SELECT * FROM merchants WHERE active = true

-- Comparison operators
SELECT * FROM merchants WHERE id > 5
SELECT * FROM merchants WHERE id != 10
```

### Updating Data

```sql
-- Update specific row
UPDATE merchants SET name = 'Updated Store' WHERE id = 1

-- Update boolean
UPDATE merchants SET active = false WHERE id = 5

-- Update multiple columns (separately)
UPDATE merchants SET name = 'New Name' WHERE id = 2
UPDATE merchants SET active = true WHERE id = 2
```

### Deleting Data

```sql
-- Delete specific row
DELETE FROM merchants WHERE id = 1

-- Delete by condition
DELETE FROM merchants WHERE active = false
```

### Joining Tables

```sql
-- Join two tables
SELECT m.name, c.description 
FROM merchants m
JOIN categories c ON m.category = c.name

-- With filter
SELECT m.name 
FROM merchants m
JOIN categories c ON m.category = c.name
WHERE c.id = 1
```

### Schema Inspection

```sql
-- List all tables
TABLES

-- View table structure
SCHEMA merchants

-- Show table details
EXPLAIN SELECT * FROM merchants WHERE id = 1
```

## Data Types Reference

### INT
- Integer numbers
- Example: `123`, `-45`, `0`

### TEXT
- String/text values
- Enclosed in single quotes
- Example: `'Store A'`, `'Nairobi'`, `'Retail'`

### BOOLEAN
- True/False values
- Values: `true`, `false`
- Example: `INSERT INTO merchants (active) VALUES (true)`

---

## Constraint Examples

### PRIMARY KEY
```sql
-- Each ID must be unique
CREATE TABLE users (id INT PRIMARY KEY, name TEXT)
INSERT INTO users (id, name) VALUES (1, 'Alice')  -- OK
INSERT INTO users (id, name) VALUES (1, 'Bob')    -- ERROR: Duplicate
```

### UNIQUE
```sql
-- Email must be unique (but can be null)
CREATE TABLE accounts (id INT PRIMARY KEY, email TEXT UNIQUE)
INSERT INTO accounts (id, email) VALUES (1, 'alice@example.com')  -- OK
INSERT INTO accounts (id, email) VALUES (2, 'alice@example.com')  -- ERROR
```

### NOT NULL
```sql
-- Name cannot be null/empty
CREATE TABLE merchants (id INT PRIMARY KEY, name TEXT NOT NULL)
INSERT INTO merchants (id, name) VALUES (1, 'Store A')  -- OK
INSERT INTO merchants (id, name) VALUES (2, NULL)      -- ERROR
```

---

## Common Troubleshooting

### "Table already exists"
```
Error: Table 'merchants' already exists

Solution: Use DROP TABLE first or use different name
```

### "Duplicate value in UNIQUE column"
```
Error: UNIQUE constraint violated for column 'name'

Solution: Use different value or update existing row
```

### "Column not found"
```
Error: Column 'nam' not found in table 'merchants'

Solution: Check spelling - was it 'name'?
```

### "Syntax error in query"
```
Error: Unexpected token

Solution: Check SQL syntax, review examples above
```
