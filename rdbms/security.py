"""
SQL injection prevention and input validation utilities.
"""

import re
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)


class SQLInjectionDetector:
    """Detects potential SQL injection attempts."""
    
    # Dangerous SQL keywords that shouldn't appear in user values
    DANGEROUS_KEYWORDS = {
        'DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE',
        'EXEC', 'EXECUTE', 'UNION', 'SELECT', 'SCRIPT', 'JAVASCRIPT',
        '--', '/*', '*/', 'xp_', 'sp_', '@@', 'DECLARE', 'CAST'
    }
    
    # Patterns that might indicate injection attempts
    DANGEROUS_PATTERNS = [
        r"['\"`;].*?(?:DROP|DELETE|INSERT|UPDATE|ALTER|CREATE)",  # DDL/DML in values
        r"(?:or|and)\s+(?:1|'[^']*'\s*)?[=<>!]",  # Logic manipulation (or 1=1)
        r"--\s*$",  # SQL comment at end
        r"/\*.*?\*/",  # Multi-line comments
        r";\s*(?:DROP|DELETE|INSERT|UPDATE)",  # Stacked queries
        r"(?:xp_|sp_)[a-z_]+",  # System procedures
        r"@@[a-z_]+",  # System variables
    ]
    
    @classmethod
    def is_dangerous(cls, value: str) -> Tuple[bool, str]:
        """
        Check if a string contains potential SQL injection.
        
        Args:
            value: The string to check
            
        Returns:
            Tuple of (is_dangerous, reason)
        """
        if not isinstance(value, str):
            return False, ""
        
        value_upper = value.upper()
        
        # Check for dangerous keywords in value
        for keyword in cls.DANGEROUS_KEYWORDS:
            if keyword in value_upper:
                # Exceptions for legitimate uses
                if keyword == 'SCRIPT' and not any(c in value for c in [';', '--', '/*']):
                    continue
                logger.warning(f"Dangerous keyword detected: {keyword} in value: {value[:50]}")
                return True, f"Dangerous keyword '{keyword}' detected"
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Dangerous pattern detected: {pattern} in value: {value[:50]}")
                return True, f"Potentially malicious pattern detected"
        
        return False, ""
    
    @classmethod
    def sanitize_table_name(cls, name: str) -> str:
        """
        Sanitize table name to prevent injection.
        Table names should only contain alphanumeric and underscore.
        """
        if not isinstance(name, str):
            raise ValueError("Table name must be a string")
        
        # Allow only alphanumeric and underscore
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '', name)
        
        if not sanitized:
            raise ValueError("Table name contains invalid characters")
        
        if len(sanitized) > 64:
            sanitized = sanitized[:64]
        
        return sanitized
    
    @classmethod
    def sanitize_column_name(cls, name: str) -> str:
        """
        Sanitize column name to prevent injection.
        Column names should only contain alphanumeric and underscore.
        """
        if not isinstance(name, str):
            raise ValueError("Column name must be a string")
        
        # Allow only alphanumeric and underscore
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '', name)
        
        if not sanitized:
            raise ValueError("Column name contains invalid characters")
        
        if len(sanitized) > 64:
            sanitized = sanitized[:64]
        
        return sanitized


class InputValidator:
    """Validates user input for security and correctness."""
    
    @staticmethod
    def validate_string(value: Any, field_name: str, min_length: int = 1, 
                       max_length: int = 255, allow_empty: bool = False) -> Tuple[bool, str]:
        """
        Validate string input.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if value is None:
            if allow_empty:
                return True, ""
            return False, f"{field_name} cannot be None"
        
        if not isinstance(value, str):
            return False, f"{field_name} must be a string"
        
        if not allow_empty and not value.strip():
            return False, f"{field_name} cannot be empty"
        
        if len(value) < min_length:
            return False, f"{field_name} must be at least {min_length} characters"
        
        if len(value) > max_length:
            return False, f"{field_name} must be at most {max_length} characters"
        
        # Check for potential injection
        is_dangerous, reason = SQLInjectionDetector.is_dangerous(value)
        if is_dangerous:
            return False, f"{field_name} contains suspicious content: {reason}"
        
        return True, ""
    
    @staticmethod
    def validate_integer(value: Any, field_name: str, min_value: int = None,
                        max_value: int = None) -> Tuple[bool, str]:
        """Validate integer input."""
        if value is None:
            return False, f"{field_name} cannot be None"
        
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            return False, f"{field_name} must be a valid integer"
        
        if min_value is not None and int_value < min_value:
            return False, f"{field_name} must be at least {min_value}"
        
        if max_value is not None and int_value > max_value:
            return False, f"{field_name} must be at most {max_value}"
        
        return True, ""
    
    @staticmethod
    def validate_boolean(value: Any, field_name: str) -> Tuple[bool, str]:
        """Validate boolean input."""
        if value is None:
            return False, f"{field_name} cannot be None"
        
        if isinstance(value, bool):
            return True, ""
        
        if isinstance(value, str):
            if value.lower() in ('true', '1', 'yes', 'on'):
                return True, ""
            if value.lower() in ('false', '0', 'no', 'off'):
                return True, ""
        
        if isinstance(value, int) and value in (0, 1):
            return True, ""
        
        return False, f"{field_name} must be a boolean value"
    
    @staticmethod
    def validate_sql_statement(sql: str, max_length: int = 10000) -> Tuple[bool, str]:
        """
        Validate SQL statement for injection attempts.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(sql, str):
            return False, "SQL must be a string"
        
        if not sql.strip():
            return False, "SQL statement cannot be empty"
        
        if len(sql) > max_length:
            return False, f"SQL statement exceeds maximum length of {max_length}"
        
        # Check for obvious injection patterns
        suspicious_patterns = [
            (r";\s*drop\s+table", "DROP TABLE command in statement"),
            (r";\s*delete\s+from", "DELETE command in statement"),
            (r"union.*select", "UNION SELECT in statement (potential injection)"),
            (r"'\s*or\s*'?1'?\s*=\s*'1", "Classic OR 1=1 injection pattern"),
            (r"exec\s*\(", "EXEC() function call"),
            (r"script|javascript", "Script code in SQL"),
        ]
        
        sql_lower = sql.lower()
        for pattern, reason in suspicious_patterns:
            if re.search(pattern, sql_lower):
                logger.warning(f"Suspicious SQL pattern detected: {reason} in: {sql[:50]}")
                return False, f"Suspicious SQL: {reason}"
        
        return True, ""
    
    @staticmethod
    def sanitize_identifier(identifier: str, identifier_type: str = "column") -> str:
        """
        Sanitize SQL identifiers (table/column names).
        
        Args:
            identifier: The identifier to sanitize
            identifier_type: Type of identifier ('table', 'column', etc.)
            
        Returns:
            Sanitized identifier
        """
        if identifier_type == "table":
            return SQLInjectionDetector.sanitize_table_name(identifier)
        elif identifier_type == "column":
            return SQLInjectionDetector.sanitize_column_name(identifier)
        else:
            return re.sub(r'[^a-zA-Z0-9_]', '', identifier)
