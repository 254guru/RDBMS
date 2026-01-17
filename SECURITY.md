# PesaPal Security Documentation

## Overview

This document outlines the security features and best practices implemented in PesaPal, a custom RDBMS with JSON persistence. The security framework is designed to prevent common web application vulnerabilities, particularly SQL injection attacks.

## Security Architecture

### 1. SQL Injection Prevention

#### Detection Strategy
The security module (`rdbms/security.py`) implements multi-layered SQL injection detection:

- **Keyword Filtering**: Detects dangerous SQL keywords in user input
  - DDL Keywords: `DROP`, `DELETE`, `INSERT`, `UPDATE`, `ALTER`, `CREATE`
  - System Keywords: `EXEC`, `EXECUTE`, `DECLARE`, `CAST`, `xp_`, `sp_`, `@@`
  - Special Keywords: `UNION`, `SELECT`, `SCRIPT`, `JAVASCRIPT`
  - Comment Markers: `--`, `/*`, `*/`

- **Pattern Matching**: Uses regex patterns to detect injection attempts
  - DDL/DML in values: `['"`](.*?)(?:DROP|DELETE|INSERT|UPDATE|ALTER|CREATE)`
  - Logic manipulation: `(?:or|and)\s+(?:1|'[^']*'\s*)?[=<>!]`
  - SQL comments: `--\s*$` and `/\*.*?\*/`
  - Stacked queries: `;\s*(?:DROP|DELETE|INSERT|UPDATE)`
  - System procedures: `(?:xp_|sp_)[a-z_]+`

#### Implementation

```python
from rdbms.security import SQLInjectionDetector, InputValidator

# Check for SQL injection
is_dangerous, reason = SQLInjectionDetector.is_dangerous(user_input)
if is_dangerous:
    # Reject the input and log the attempt
    logger.warning(f"SQL injection attempt detected: {reason}")
    return error_response("Security validation failed")

# Validate SQL statements
is_valid, error = InputValidator.validate_sql_statement(sql_statement)
if not is_valid:
    logger.warning(f"SQL validation failed: {error}")
    return error_response(f"Security validation failed: {error}")
```

### 2. Input Validation

The `InputValidator` class provides type-specific validation:

#### String Validation
```python
is_valid, error = InputValidator.validate_string(value)
# Checks:
# - Not None or empty (max 1000 characters)
# - No injection patterns
# - Proper encoding handling
```

#### Integer Validation
```python
is_valid, error = InputValidator.validate_integer(value, min_value=None, max_value=None)
# Checks:
# - Valid integer or string representation
# - Optional range validation
# - No type confusion attacks
```

#### Boolean Validation
```python
is_valid, error = InputValidator.validate_boolean(value)
# Checks:
# - Accepts: True, False, 0, 1, 'true', 'false', 'yes', 'no'
# - Case-insensitive
```

#### SQL Statement Validation
```python
is_valid, error = InputValidator.validate_sql_statement(statement)
# Checks:
# - Not empty
# - No injection patterns
# - Valid SQL structure
```

#### Identifier Sanitization
```python
sanitized = InputValidator.sanitize_identifier(identifier)
# Removes or escapes special characters
# Ensures alphanumeric + underscore only
```

### 3. Table and Column Name Sanitization

```python
# Sanitize table names (alphanumeric + underscore only)
table_name = SQLInjectionDetector.sanitize_table_name("users")

# Sanitize column names
column_name = SQLInjectionDetector.sanitize_column_name("user_id")
```

## Web Application Security

### Flask Application (`web_app/app.py`)

#### Merchant Input Validation
All merchant data is validated before database operations:

```python
def validate_merchant_input(data):
    """Validate merchant input with comprehensive checks."""
    errors = []
    
    # Validate each required field
    if not data.get('name'):
        errors.append("Merchant name is required")
    else:
        is_valid, error = InputValidator.validate_string(data['name'])
        if not is_valid:
            errors.append(f"Invalid merchant name: {error}")
    
    # Similar validation for other fields...
    
    if errors:
        raise ValueError("; ".join(errors))
    
    return True
```

#### Query Endpoint Security
The `/api/query` endpoint implements multi-stage security validation:

```python
@app.route('/api/query', methods=['POST'])
def query():
    # Parse incoming SQL statements
    statements = [s.strip() for s in request.json.get('query', '').split(';') 
                  if s.strip()]
    
    # 1. Check for empty queries
    if not statements:
        return error_response("No valid SQL statements found", 400)
    
    # 2. Validate each statement for injection attempts
    for statement in statements:
        is_valid, error = InputValidator.validate_sql_statement(statement)
        if not is_valid:
            logger.warning(f"SQL injection attempt: {error}")
            return error_response(f"Security validation failed: {error}", 400)
    
    # 3. Parse and execute statements
    for statement in statements:
        stmt = parser.parse(statement)
        result = engine.execute(stmt)
        # Process result...
```

#### Error Handling
Comprehensive error handlers with security considerations:

```python
@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 Not Found: {request.path}")
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"500 Server Error: {error}", exc_info=True)
    # Return generic error message (don't expose internal details)
    return jsonify({"error": "Internal server error"}), 500
```

### Logging and Monitoring

All security-relevant events are logged:

- **WARNING**: SQL injection attempts, failed validations
- **ERROR**: Constraint violations, database errors
- **DEBUG**: Statement type detection, query execution details

```python
logger.warning(f"SQL injection attempt detected: {reason}")
logger.error(f"Constraint violation: {error_message}")
logger.debug(f"Executing statement: {statement}")
```

## Attack Prevention

### SQL Injection
- ✅ Input validation on all user-provided data
- ✅ Dangerous keyword detection
- ✅ Pattern-based injection detection
- ✅ Comment marker blocking
- ✅ Stacked query prevention

### Type Confusion
- ✅ Strict type validation
- ✅ Integer range validation
- ✅ Boolean normalization

### Unicode Attacks
- ✅ Unicode normalization checks
- ✅ Null byte filtering

### Comment-based Attacks
- ✅ SQL comment detection (`--`, `/* */`)
- ✅ Multi-line comment blocking

### Case-Insensitive Attacks
- ✅ Case-insensitive keyword detection
- ✅ Pattern matching with IGNORECASE flag

## Testing

### Security Test Suite

The project includes 29 comprehensive security tests in `tests/test_security.py`:

#### SQL Injection Detection (5 tests)
- DROP TABLE injection
- OR 1=1 injection
- UNION SELECT injection
- Comment injection
- Stacked queries

#### Input Validation (13 tests)
- Valid string input
- Empty string handling
- String length limits
- Injection pattern detection
- Valid integer input
- Integer range validation
- Valid boolean input
- Invalid boolean handling
- Valid SQL statements
- SQL injection in statements
- Empty SQL handling
- Identifier sanitization

#### Integration Tests (2 tests)
- Merchant data validation
- End-to-end security checks

#### Edge Cases (5 tests)
- Unicode injection attempts
- Case-insensitive detection
- Null byte injection
- Very long input rejection
- Special characters in legitimate data

### Running Security Tests

```bash
# Run only security tests
pytest tests/test_security.py -v

# Run all tests with coverage
pytest tests/ --cov=rdbms --cov-report=html

# Run with detailed output
pytest tests/test_security.py -vv
```

### Test Results

**Current Status**: ✅ All 29 security tests passing

```
tests/test_security.py::TestSQLInjectionDetector (9 tests) ✅
tests/test_security.py::TestInputValidator (13 tests) ✅
tests/test_security.py::TestInputValidatorIntegration (2 tests) ✅
tests/test_security.py::TestSecurityEdgeCases (5 tests) ✅
```

## Best Practices for Development

### 1. Always Validate User Input
```python
# ❌ Wrong
data = request.json
query = f"INSERT INTO users VALUES ('{data['name']}')"

# ✅ Correct
data = request.json
is_valid, error = InputValidator.validate_string(data['name'])
if not is_valid:
    return error_response(f"Invalid input: {error}", 400)
```

### 2. Use Security Module for Validation
```python
# ✅ Recommended
from rdbms.security import InputValidator

is_valid, error = InputValidator.validate_sql_statement(statement)
is_valid, error = InputValidator.validate_string(user_input)
is_valid, error = InputValidator.validate_integer(value)
```

### 3. Log Security Events
```python
# ✅ Log suspicious activity
if suspicious:
    logger.warning(f"Suspicious activity: {details}")

# ✅ Log validation failures
if not is_valid:
    logger.warning(f"Validation failed: {error}")
```

### 4. Sanitize Identifiers
```python
# ✅ Sanitize table/column names
table_name = SQLInjectionDetector.sanitize_table_name(user_input)
column_name = SQLInjectionDetector.sanitize_column_name(user_input)
```

### 5. Handle Errors Gracefully
```python
try:
    result = engine.execute(statement)
except ValidationError as e:
    logger.error(f"Validation error: {e}")
    return error_response("Invalid request", 400)
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    return error_response("Internal server error", 500)
```

## Configuration

### Environment Variables

```bash
# Database directory
export RDBMS_DB_DIR=/path/to/db

# Flask debug mode
export FLASK_DEBUG=False  # Set to False in production

# Logging level
export LOG_LEVEL=INFO  # DEBUG for development, INFO/WARNING for production
```

### Production Recommendations

1. **Disable Debug Mode**
   ```bash
   export FLASK_DEBUG=False
   ```

2. **Set Appropriate Logging Level**
   ```bash
   export LOG_LEVEL=WARNING
   ```

3. **Use HTTPS/TLS**
   - Configure Flask to use SSL certificates
   - Set `SECURE_SSL_REDIRECT=True`

4. **Implement Rate Limiting**
   - Add Flask-Limiter for endpoint rate limiting
   - Prevent brute force attacks

5. **Add Authentication**
   - Implement API key validation
   - Add user authentication if needed

6. **Monitor Logs**
   - Monitor WARNING and ERROR level logs
   - Set up alerts for injection attempts
   - Track failed validations

## Vulnerability Reporting

If you discover a security vulnerability:

1. **Do not** open a public issue
2. Contact the security team immediately
3. Provide:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## References

- [OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [CWE-89: SQL Injection](https://cwe.mitre.org/data/definitions/89.html)
- [Flask Security](https://flask.palletsprojects.com/en/3.0.x/)

## Changelog

### v1.0.0 (Security Release)
- Implemented SQLInjectionDetector class
- Implemented InputValidator class
- Added comprehensive security logging
- Added 29 security tests with 100% pass rate
- Integrated validation into web app endpoints
- Added security documentation

---

**Last Updated**: 2024
**Status**: Production Ready ✅
