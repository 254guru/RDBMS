# PesaPal SQL Query Examples

Quick reference for SQL queries that work with PesaPal's secured web app.

## 🟢 WORKING QUERIES

### Read Data (SELECT)
```sql
-- Get all merchants
SELECT * FROM merchants;

-- Get specific merchant
SELECT * FROM merchants WHERE id = 1;

-- Get by name
SELECT * FROM merchants WHERE name = 'Safaricom';

-- Get active merchants
SELECT * FROM merchants WHERE active = 1;

-- Count merchants
SELECT COUNT(*) FROM merchants;

-- Get columns
SELECT id, name, email FROM merchants;

-- Limit results
SELECT * FROM merchants LIMIT 10;

-- Order by name
SELECT * FROM merchants ORDER BY name ASC;

-- Complex query
SELECT id, name, email FROM merchants 
WHERE active = 1 AND name LIKE 'Safe%' 
ORDER BY name LIMIT 5;
```

### Create Data (INSERT)
```sql
-- Basic insert
INSERT INTO merchants (name, email, phone) 
VALUES ('New Merchant', 'contact@merchant.com', '254123456789');

-- Insert with all fields
INSERT INTO merchants (id, name, email, phone, active) 
VALUES (1, 'Shop Name', 'shop@email.com', '254123456789', 1);

-- Multiple inserts (one at a time!)
INSERT INTO merchants (name, email) VALUES ('Merchant1', 'merchant1@test.com');
INSERT INTO merchants (name, email) VALUES ('Merchant2', 'merchant2@test.com');
```

### Update Data (UPDATE)
```sql
-- Update one field
UPDATE merchants SET active = 0 WHERE id = 1;

-- Update multiple fields
UPDATE merchants 
SET name = 'Updated Name', email = 'newemail@test.com' 
WHERE id = 1;

-- Update with conditions
UPDATE merchants SET active = 1 WHERE name = 'Safaricom';
```

### Delete Data (DELETE)
```sql
-- Delete specific row
DELETE FROM merchants WHERE id = 1;

-- Delete inactive
DELETE FROM merchants WHERE active = 0;

-- Delete by name
DELETE FROM merchants WHERE name = 'Old Merchant';
```

### Create Tables (CREATE TABLE)
```sql
-- Create merchants table
CREATE TABLE merchants (
    id INT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    phone TEXT,
    active BOOLEAN
);

-- Create transactions table
CREATE TABLE transactions (
    id INT PRIMARY KEY,
    merchant_id INT,
    amount INT,
    status TEXT
);

-- Create users table
CREATE TABLE users (
    id INT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    created_at TEXT
);
```

---

## 🔴 BLOCKED QUERIES

These will return error 400 with security warning.

```sql
-- ❌ DROP TABLE (destructive)
DROP TABLE merchants;

-- ❌ UNION SELECT (injection pattern)
SELECT * FROM merchants UNION SELECT * FROM users;

-- ❌ OR 1=1 (bypass logic)
SELECT * FROM merchants WHERE id = 1 OR '1'='1';

-- ❌ SQL Comments (injection vector)
SELECT * FROM merchants; -- comment

-- ❌ Multi-line comments
SELECT * FROM merchants /* comment */;

-- ❌ Stacked queries
SELECT * FROM merchants; DELETE FROM merchants;

-- ❌ System procedures
EXEC xp_cmdshell 'dir';

-- ❌ EXECUTE function
EXECUTE sp_executesql;

-- ❌ Script injection
SELECT * FROM merchants WHERE name = '<script>alert(1)</script>';
```

---

## 📝 Using with cURL

### Simple SELECT
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query":"SELECT * FROM merchants LIMIT 5"}'
```

### INSERT New Merchant
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "INSERT INTO merchants (name, email, phone) VALUES ('"'"'M-Pesa'"'"', '"'"'mpesa@safaricom.com'"'"', '"'"'254123456789'"'"')"
  }'
```

### UPDATE Active Status
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query":"UPDATE merchants SET active = 1 WHERE id = 1"}'
```

### DELETE Merchant
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query":"DELETE FROM merchants WHERE id = 1"}'
```

---

## 🧪 Test Cases by Type

### Case 1: Read Performance
```sql
SELECT id, name, email FROM merchants LIMIT 100;
```
**Expected**: Returns up to 100 merchants ✅

### Case 2: Write Safety
```sql
INSERT INTO merchants (name, email) VALUES ('Test', 'test@test.com');
```
**Expected**: Creates new merchant ✅

### Case 3: Injection Protection
```sql
SELECT * FROM merchants WHERE email = 'admin@test.com' OR '1'='1';
```
**Expected**: Returns 400 error ❌

### Case 4: Comment Blocking
```sql
SELECT * FROM merchants WHERE id = 1; -- bypass
```
**Expected**: Returns 400 error ❌

### Case 5: Destructive Blocking
```sql
DROP TABLE merchants;
```
**Expected**: Returns 400 error ❌

---

## 📊 Query Complexity Examples

### Simple (1 table)
```sql
SELECT * FROM merchants;
```

### Moderate (conditions)
```sql
SELECT * FROM merchants 
WHERE active = 1 AND name LIKE 'Safe%';
```

### Complex (multiple conditions)
```sql
SELECT id, name, email FROM merchants 
WHERE active = 1 
  AND phone IS NOT NULL 
  AND email LIKE '%@%.%' 
ORDER BY name ASC 
LIMIT 20;
```

### Very Complex (if supported)
```sql
SELECT merchant_id, COUNT(*) as transaction_count 
FROM transactions 
GROUP BY merchant_id 
HAVING COUNT(*) > 5 
ORDER BY transaction_count DESC;
```

---

## ⚠️ Common Mistakes

### ❌ Wrong: Using OR 1=1
```sql
SELECT * FROM merchants WHERE active = 1 OR 1=1;
```
**Error**: "Classic OR 1=1 injection pattern" ❌

### ✅ Right: Use proper conditions
```sql
SELECT * FROM merchants WHERE active = 1;
```

---

### ❌ Wrong: Using UNION
```sql
SELECT id FROM merchants UNION SELECT id FROM users;
```
**Error**: "UNION SELECT in statement (potential injection)" ❌

### ✅ Right: Query each table separately
```sql
SELECT id FROM merchants;
SELECT id FROM users;
```

---

### ❌ Wrong: Stacking queries
```sql
SELECT * FROM merchants; DELETE FROM merchants;
```
**Error**: "DELETE command in statement" ❌

### ✅ Right: One query at a time
```sql
SELECT * FROM merchants;
```
Then:
```sql
DELETE FROM merchants WHERE id = 1;
```

---

### ❌ Wrong: Using comments
```sql
SELECT * FROM merchants; -- get all
```
**Error**: Dangerous keyword '--' detected ❌

### ✅ Right: No comments in API queries
```sql
SELECT * FROM merchants;
```

---

## 🎯 Recommended Workflow

1. **Test with SELECT first**
   ```sql
   SELECT * FROM merchants LIMIT 1;
   ```

2. **Then INSERT new data**
   ```sql
   INSERT INTO merchants (name) VALUES ('My Merchant');
   ```

3. **Verify with SELECT**
   ```sql
   SELECT * FROM merchants WHERE name = 'My Merchant';
   ```

4. **Update if needed**
   ```sql
   UPDATE merchants SET active = 1 WHERE name = 'My Merchant';
   ```

5. **Delete when done**
   ```sql
   DELETE FROM merchants WHERE name = 'My Merchant';
   ```

---

## 📋 Quick Reference Table

| Operation | Syntax | Status |
|-----------|--------|--------|
| SELECT all | `SELECT * FROM table;` | ✅ |
| SELECT filtered | `SELECT * FROM table WHERE id = 1;` | ✅ |
| SELECT limited | `SELECT * FROM table LIMIT 10;` | ✅ |
| INSERT | `INSERT INTO table VALUES (...);` | ✅ |
| UPDATE | `UPDATE table SET col = val WHERE id = 1;` | ✅ |
| DELETE | `DELETE FROM table WHERE id = 1;` | ✅ |
| CREATE | `CREATE TABLE name (...);` | ✅ |
| ALTER | `ALTER TABLE name ADD COLUMN ...;` | ✅ |
| DROP | `DROP TABLE name;` | ❌ |
| UNION | `SELECT ... UNION SELECT ...;` | ❌ |
| Comments | `... -- comment` | ❌ |
| Stacked | `...; ...;` | ❌ |

---

**For detailed information, see [SQL_QUERY_GUIDE.md](SQL_QUERY_GUIDE.md)**
