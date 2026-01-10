# PesaPal RDBMS - Getting Started Guide


# GUIDE — Quickstart & Examples

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

Open `http://localhost:5000` to interact with the UI. The demo exposes a small REST API:

- `GET /api/merchants`
- `POST /api/merchants`
- `POST /api/query` — execute SQL

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
- For debugging and examples, see `example.py`.

Next steps
----------

- Want deeper docs? I can add a developer walkthrough for the parser or storage internals.
- Want me to run the project verification now and report results? I can run `./verify.sh` and show the output.

### Inserting Data

```sql
-- Single row
INSERT INTO users (id, name) VALUES (1, 'Alice')

-- Multiple rows (run separately)
INSERT INTO users (id, name) VALUES (2, 'Bob')
INSERT INTO users (id, name) VALUES (3, 'Charlie')

-- Boolean values
INSERT INTO accounts (id, email, balance, active) 
VALUES (1, 'alice@example.com', 1000, true)
```

### Querying Data

```sql
-- Get all rows
SELECT * FROM users

-- Get specific columns
SELECT id, name FROM users

-- Filter with WHERE
SELECT * FROM users WHERE id = 1

-- Multiple conditions (one at a time)
SELECT * FROM accounts WHERE balance > 500
SELECT * FROM accounts WHERE active = true

-- Comparison operators
SELECT * FROM transactions WHERE amount > 100
SELECT * FROM transactions WHERE amount >= 50
SELECT * FROM transactions WHERE amount < 200
SELECT * FROM transactions WHERE amount != 0
```

### Updating Data

```sql
-- Update specific row
UPDATE users SET name = 'Alice Smith' WHERE id = 1

-- Update boolean
UPDATE accounts SET active = false WHERE id = 5

-- Update multiple columns (one at a time)
UPDATE transactions SET amount = 150 WHERE id = 1
```

### Deleting Data

```sql
-- Delete specific row
DELETE FROM users WHERE id = 1

-- Delete by condition
DELETE FROM accounts WHERE balance < 100
DELETE FROM transactions WHERE amount = 0
```

### Joining Tables

```sql
-- Join two tables
SELECT u.name, t.amount 
FROM users u 
JOIN transactions t ON u.id = t.from_user

-- Filter after join
SELECT u.name, a.email, a.balance
FROM users u
JOIN accounts a ON u.id = a.id
WHERE a.balance > 500
```

### Schema Inspection

```sql
-- List all tables
TABLES

-- View table structure
SCHEMA users

-- Show execution plan
EXPLAIN SELECT * FROM users WHERE id = 1
```

---

## Step-by-Step Tutorial

### Part 1: Create Your First Table (2 minutes)

```sql
pesapal> CREATE TABLE stores (
    id INT PRIMARY KEY,
    name TEXT UNIQUE,
    city TEXT
)
✓ Table 'stores' created successfully
```

### Part 2: Add Some Data (2 minutes)

```sql
pesapal> INSERT INTO stores (id, name, city) VALUES (1, 'Downtown Store', 'Nairobi')
✓ 1 row inserted

pesapal> INSERT INTO stores (id, name, city) VALUES (2, 'Westlands Store', 'Nairobi')
✓ 1 row inserted

pesapal> INSERT INTO stores (id, name, city) VALUES (3, 'Kisumu Store', 'Kisumu')
✓ 1 row inserted
```

### Part 3: Query Your Data (1 minute)

```sql
pesapal> SELECT * FROM stores
┌────┬─────────────────┬─────────┐
│ id │ name            │ city    │
├────┼─────────────────┼─────────┤
│ 1  │ Downtown Store  │ Nairobi │
│ 2  │ Westlands Store │ Nairobi │
│ 3  │ Kisumu Store    │ Kisumu  │
└────┴─────────────────┴─────────┘
Executed in 3ms | 3 rows scanned | 3 rows returned
```

### Part 4: Filter Your Data

```sql
pesapal> SELECT * FROM stores WHERE city = 'Nairobi'
┌────┬─────────────────┬─────────┐
│ id │ name            │ city    │
├────┼─────────────────┼─────────┤
│ 1  │ Downtown Store  │ Nairobi │
│ 2  │ Westlands Store │ Nairobi │
└────┴─────────────────┴─────────┘
Executed in 2ms | 3 rows scanned | 2 rows returned
```

### Part 5: Update Your Data

```sql
pesapal> UPDATE stores SET city = 'Nairobi Metro' WHERE id = 1
✓ 1 row updated

pesapal> SELECT * FROM stores WHERE id = 1
┌────┬────────────────┬────────────────┐
│ id │ name           │ city           │
├────┼────────────────┼────────────────┤
│ 1  │ Downtown Store │ Nairobi Metro  │
└────┴────────────────┴────────────────┘
```

### Part 6: Delete Your Data

```sql
pesapal> DELETE FROM stores WHERE id = 3
✓ 1 row deleted

pesapal> SELECT * FROM stores
┌────┬─────────────────┬────────────────┐
│ id │ name            │ city           │
├────┼─────────────────┼────────────────┤
│ 1  │ Downtown Store  │ Nairobi Metro  │
│ 2  │ Westlands Store │ Nairobi        │
└────┴─────────────────┴────────────────┘
```

---

## Web App Tutorial

### Step 1: Start the Web App
```bash
cd web_app
python3 app.py
# Open http://localhost:5000
```

### Step 2: Browse Merchants Tab
- Shows all merchants in a grid layout
- Click on a merchant to view details
- See real-time database queries

### Step 3: Add Merchant
1. Click "Add Merchant" tab
2. Enter Merchant ID (integer)
3. Enter Name (text)
4. Select Category from dropdown
5. Check/uncheck Active status
6. Click "Add Merchant"

### Step 4: View Categories
- Click "Categories" tab
- See all available categories
- Filter merchants by category

### Step 5: Execute SQL Query
1. Click "SQL Query" tab
2. Type any SQL command in the textarea
3. Click "Execute Query"
4. See results in formatted table

Example queries to try:
```sql
SELECT * FROM merchants
SELECT * FROM merchants WHERE active = true
SELECT COUNT(*) as total FROM merchants
UPDATE merchants SET active = false WHERE id = 1
SELECT * FROM categories
```

---

## Data Types Reference

### INT
- Integer numbers
- Range: -2,147,483,648 to 2,147,483,647
- Example: `123`, `-45`, `0`

### TEXT
- String/text values
- Enclosed in single quotes
- Example: `'Hello'`, `'Nairobi'`, `'merchant@example.com'`

### BOOLEAN
- True/False values
- Values: `true`, `false`
- Case-insensitive in many contexts

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
CREATE TABLE accounts (
    id INT PRIMARY KEY,
    email TEXT UNIQUE
)
INSERT INTO accounts (id, email) VALUES (1, 'alice@example.com')  -- OK
INSERT INTO accounts (id, email) VALUES (2, 'alice@example.com')  -- ERROR
```

### NOT NULL
```sql
-- Name cannot be null/empty
CREATE TABLE products (
    id INT PRIMARY KEY,
    name TEXT NOT NULL
)
INSERT INTO products (id, name) VALUES (1, 'Product A')  -- OK
INSERT INTO products (id, name) VALUES (2, NULL)        -- ERROR
```

---

## REPL Commands Reference

```sql
-- SQL Operations
CREATE TABLE ...
INSERT INTO ...
SELECT ...
UPDATE ...
DELETE ...
DROP TABLE ...

-- Utility Commands
TABLES                -- List all tables
SCHEMA tablename      -- Show table structure
EXPLAIN query         -- Show execution plan
HELP                  -- Show this help
CLEAR                 -- Clear screen
EXIT                  -- Exit REPL
```

---

## Performance Tips

### Use WHERE Clause Effectively
```sql
-- GOOD: Filters 99% of rows
SELECT * FROM transactions WHERE amount > 1000

-- OK: Scans all rows then filters
SELECT * FROM transactions
```

### Use PRIMARY KEY for Lookups
```sql
-- VERY FAST (O(1) index lookup)
SELECT * FROM users WHERE id = 123

-- SLOWER (full table scan)
SELECT * FROM users WHERE name = 'Alice'
```

### Keep Tables Organized
```sql
-- Create intentional schema
CREATE TABLE merchants (
    id INT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL
)

-- vs. unstructured
CREATE TABLE data (col1 INT, col2 TEXT, col3 TEXT)
```

---

## Troubleshooting

### "Table already exists"
```
Error: Table 'users' already exists

Solution: Use DROP TABLE first or use different name
```

### "Duplicate value in UNIQUE column"
```
Error: UNIQUE constraint violated for column 'email'

Solution: Use different value or update existing row
```

### "Column not found"
```
Error: Column 'nam' not found in table 'users'

Solution: Check spelling - was it 'name'?
```

### "Syntax error in query"
```
Error: Unexpected token

Solution: Check SQL syntax, review examples above
```

---

## Next Steps

1. **Explore the Code**: Look at `rdbms/` directory for implementation
2. **Read Full Documentation**: Check README.md for architecture details
3. **Run Examples**: Execute `python3 example.py` to see all features
4. **Experiment**: Try different SQL queries and operations
5. **Deploy**: Consider extending with additional features

---

## Feature Summary

✅ **Fully Functional RDBMS**:
- Create, read, update, delete operations
- Primary key and unique constraints
- WHERE clause filtering
- Table joins
- Data persistence
- Interactive REPL
- Web application

⚠️ **Not Implemented** (by design for challenge scope):
- Aggregates (COUNT, SUM, AVG)
- Sorting (ORDER BY)
- Transactions
- Subqueries
- User authentication

---

## Additional Resources

- **Code**: Located in `rdbms/` directory with inline comments
- **Examples**: Run `python3 example.py` for feature demo
- **Tests**: Run `./verify.sh` for system validation
- **Architecture**: See README.md for detailed design
- **Full Documentation**: Check README.md for comprehensive reference

---

**Ready to get started?** Run `./launch.sh` now!
