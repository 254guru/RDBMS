# Quick Reference: Running Tests & Improvements

## Test Suite Quick Start

### Run All Tests
```bash
cd /home/ggonza/Projects/PesaPal
python -m pytest tests/ -v
```

### Run with Coverage Report
```bash
python -m pytest tests/ --cov=rdbms --cov-report=term-missing --cov-report=html
# View coverage: open htmlcov/index.html
```

### Run Specific Test Category
```bash
# Unit tests for a module
pytest tests/test_types.py -v
pytest tests/test_parser.py -v
pytest tests/test_storage.py -v
pytest tests/test_engine.py -v

# Integration tests
pytest tests/test_integration.py -v
```

### Run Specific Test
```bash
pytest tests/test_storage.py::TestTable::test_table_insert -v
pytest tests/test_parser.py::TestSelectParsing::test_parse_select_all -v
```

---

## Web App Improvements

### Running the Web App with Improvements
```bash
cd /home/ggonza/Projects/PesaPal/web_app

# Development mode (with debug logging)
FLASK_DEBUG=True python app.py

# Production mode (with info logging only)
python app.py
```

### Environment Variables
```bash
# Set database directory
export RDBMS_DB_DIR="/path/to/db"

# Enable debug mode
export FLASK_DEBUG=True
```

### Logging Output Examples

**Successful merchant creation:**
```
INFO - Merchant added successfully: id=1, name=Store A
```

**Validation error:**
```
WARNING - Invalid merchant input: ["'id' must be a valid integer", "'name' must be a string"]
```

**Parse error in SQL:**
```
WARNING - Parse error in SQL statement: SELECT * FROM users W... - Unexpected character
```

**Server error:**
```
ERROR - Error updating merchant 1: [full stack trace]
```

---

## Code Coverage

Current coverage by module:
- `rdbms/types.py`: 96% (3 statements missing)
- `rdbms/parser.py`: 87% (27 statements missing)
- `rdbms/storage.py`: 80% (44 statements missing)
- `rdbms/engine.py`: 68% (61 statements missing)
- **Overall**: 69% (252 statements missing)

The untested code is primarily:
- Error paths (covered by exception handling)
- Advanced query optimization (not yet implemented)
- REPL interactive commands (requires manual testing)

---

## Validation Examples

### Merchant Input Validation
Valid:
```python
data = {
    "id": 1,
    "name": "Store A",
    "category": "Retail",
    "active": True
}
```

Invalid (will return 400):
```python
# Missing required field
data = {"id": 1, "name": "Store A"}

# Invalid type
data = {"id": "not-an-int", "name": "Store A", "category": "Retail"}

# Empty string
data = {"id": 1, "name": "", "category": "Retail"}
```

---

## API Error Responses

### 400 Bad Request
```json
{
    "error": "Invalid input",
    "details": ["'id' must be a valid integer"]
}
```

### 404 Not Found
```json
{
    "error": "Merchant not found"
}
```

### 500 Internal Server Error
```json
{
    "error": "An unexpected error occurred"
}
```

---

## Adding New Tests

### Structure
```python
class TestFeatureName:
    """Tests for feature description."""
    
    @pytest.fixture
    def setup(self, temp_db_dir):
        """Set up test fixtures."""
        # Setup code here
        yield result
    
    def test_feature_case_1(self, setup):
        """Test description."""
        # Arrange
        # Act
        # Assert
        assert result == expected
```

### Common Patterns

**Database testing:**
```python
def test_something(self, database_instance):
    db = database_instance
    # ... test code ...
```

**Parser testing:**
```python
def test_parsing(self, parser_instance):
    parser = parser_instance
    stmt = parser.parse("SELECT * FROM users")
    # ... assertions ...
```

**Engine testing:**
```python
def test_execution(self, engine_instance, parser_instance):
    engine = engine_instance
    parser = parser_instance
    stmt = parser.parse("CREATE TABLE test (...)")
    result = engine.execute(stmt)
    assert result.success
```

---

## Continuous Integration Checklist

Before committing code:

- [ ] Run `pytest tests/ -q` - all tests pass
- [ ] Check coverage: `pytest tests/ --cov=rdbms`
- [ ] Lint: `python -m py_compile web_app/app.py`
- [ ] Import check: `python -c "from web_app.app import app"`
- [ ] Manual integration test (if applicable)

---

## Known Limitations & Future Work

### Current Limitations
- No transaction support (atomic operations only)
- No JOINs beyond simple nested loops
- No aggregate functions (COUNT, SUM, etc.)
- Multi-character operators (<=, >=) not fully supported
- JSON-based storage (not scalable to large datasets)

### High Priority Next Steps
1. Add API endpoint tests using `pytest-flask`
2. Implement transaction support
3. Add query optimization with index usage
4. Create deployment documentation (Docker, gunicorn)

### See Also
- `IMPROVEMENTS.md` - Detailed improvement summary
- `tests/` - All test files with examples
- `web_app/app.py` - Improved implementation with logging
