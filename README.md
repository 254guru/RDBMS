# PesaPal RDBMS Challenge

A concise reference for the PesaPal RDBMS implementation. This file documents the system, key features, and how to use the project; for step-by-step tutorials and examples see `GUIDE.md`.

Quick commands
--------------

Make scripts executable and run the interactive menu:

```bash
chmod +x *.sh
./verify.sh    # optional health check
./launch.sh
```

What this project provides
--------------------------

- Simple RDBMS implemented in Python with:
  - JSON-backed persistence
  - HashIndex for PRIMARY KEY / UNIQUE enforcement
  - Regex-based SQL parser (CREATE/INSERT/SELECT/UPDATE/DELETE/DROP)
  - Nested-loop JOIN support
  - Interactive REPL and a small Flask web demo

Key files
---------

- `rdbms/` — core engine modules (`types.py`, `storage.py`, `parser.py`, `engine.py`, `repl.py`)
- `web_app/` — Flask demo (`app.py`, `templates/`, `static/`)
- `example.py` — short demo script
- `launch.sh` / `verify.sh` — convenience scripts

Minimal examples
----------------

Create a table:

```sql
CREATE TABLE users (id INT PRIMARY KEY, name TEXT, active BOOLEAN)
```

Insert a row:

```sql
INSERT INTO users (id, name, active) VALUES (1, 'Alice', true)
```

Select rows:

```sql
SELECT * FROM users
SELECT name FROM users WHERE active = true
```

Update and delete:

```sql
UPDATE users SET active = false WHERE id = 1
DELETE FROM users WHERE id = 1
```

Join example:

```sql
SELECT m.name, t.amount
FROM merchants m
JOIN transactions t ON m.id = t.merchant_id
```

Constraints and behavior
------------------------

- PRIMARY KEY and UNIQUE are enforced via a HashIndex and persist across runs.
- NOT NULL checks and type casting are applied on INSERT/UPDATE.

Limitations
-----------

- No transactions or multi-statement atomicity
- No aggregates (COUNT/SUM/AVG) or ORDER BY
- Simplified SQL grammar (not full SQL92)

Contributing and next steps
---------------------------

- Add unit tests if you expand features.
- Run `./verify.sh` before submitting or pushing changes.


## Troubleshooting

### Issue: Module import errors
**Solution**: Run `./verify.sh` to check all imports

### Issue: Database not persisting
**Solution**: Check `./db/` directory exists and has write permissions

### Issue: Web app won't start
**Solution**: Ensure port 5000 is available, run `cd web_app && python3 app.py`

### Issue: SQL errors
**Solution**: Check syntax in examples and review error message carefully

**Key Files**:
- `rdbms/storage.py` - Largest module (324 lines) with storage engine
- `rdbms/parser.py` - SQL parsing logic (379 lines)
- `web_app/static/style.css` - UI styling (446 lines)

## Support

- Check `GUIDE.md` for getting started
- Review test examples in verify.sh
- Examine example.py for feature demonstrations
- Run `./launch.sh` for interactive menu
- Check code comments for implementation details

## Project Status

✅ **COMPLETE** - All requirements implemented and tested

- All core modules functional
- All SQL operations working
- Constraints properly enforced
- Both interfaces (REPL and Web) operational
- Comprehensive documentation
- Ready for PesaPal JDEV26 submission
