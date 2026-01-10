# PesaPal RDBMS - Getting Started Guide

## Quick Start

### Step 1: Verify Installation
```bash
cd /home/ggonza/Projects/PesaPal
chmod +x *.sh
./verify.sh
```

You should see all Checks are OK

### Step 2: Launch the System
```bash
./launch.sh
```

### Step 3: Choose Your Mode

#### Option 1: Interactive REPL (Recommended for First-Time)
```
1) Run Interactive REPL (CLI)
2) Run Web Application (Flask)
3) Run Example Demo
4) Run System Tests
5) View Documentation
6) Exit

Enter your choice (1-6): 1
```

Try these commands:
```sql
CREATE TABLE products (id INT PRIMARY KEY, name TEXT UNIQUE, price INT)
INSERT INTO products (id, name, price) VALUES (1, 'Laptop', 1000)
INSERT INTO products (id, name, price) VALUES (2, 'Mouse', 50)
SELECT * FROM products
SELECT * FROM products WHERE price > 60
UPDATE products SET price = 45 WHERE id = 2
TABLES
SCHEMA products
DELETE FROM products WHERE id = 1
EXIT
```

#### Option 2: Web Application
```
Enter your choice (1-6): 2

📍 Open your browser at: http://localhost:5000
```

Features:
- **Merchants Tab**: View all merchants
- **Add Merchant**: Create new merchant entries
- **Categories Tab**: Browse categories
- **SQL Query Tab**: Run custom SQL queries

#### Option 3: Example Demo
```
Enter your choice (1-6): 3
```

Shows a complete working example with:
- Table creation
- Data insertion
- Querying
- Filtering
- Joins
- Performance metrics

---

## Common SQL Operations

### Creating Tables

```sql
-- Simple table
CREATE TABLE users (id INT PRIMARY KEY, name TEXT)

-- Table with constraints
CREATE TABLE accounts (
    id INT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    balance INT,
    active BOOLEAN
)

-- Multiple unique constraints
CREATE TABLE transactions (
    id INT PRIMARY KEY,
    from_user INT,
    to_user INT,
    amount INT NOT NULL,
    timestamp TEXT
)
```

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

**Ready to get started?** Run `./launch.sh` now! 🚀
