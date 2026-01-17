"""
SQL parser for basic RDBMS commands.
Supports simplified SQL syntax for CRUD operations and table creation.
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from rdbms.types import Column, DataType

logger = logging.getLogger(__name__)

class ParseError(Exception):
    """Raised when parsing fails."""
    pass


@dataclass
class CreateTableStmt:
    """Represents a CREATE TABLE statement."""
    table_name: str
    columns: List[Column]


@dataclass
class InsertStmt:
    """Represents an INSERT statement."""
    table_name: str
    columns: List[str]
    values: List[Any]


@dataclass
class SelectStmt:
    """Represents a SELECT statement."""
    table_name: str
    columns: List[str]  # Empty list means SELECT *
    where_clause: Optional[Tuple[str, str, Any]] = None  # (column, operator, value)
    join_table: Optional[str] = None
    join_on: Optional[Tuple[str, str]] = None  # (left_col, right_col)


@dataclass
class UpdateStmt:
    """Represents an UPDATE statement."""
    table_name: str
    updates: Dict[str, Any]
    where_clause: Optional[Tuple[str, str, Any]] = None


@dataclass
class DeleteStmt:
    """Represents a DELETE statement."""
    table_name: str
    where_clause: Optional[Tuple[str, str, Any]] = None


@dataclass
class DropTableStmt:
    """Represents a DROP TABLE statement."""
    table_name: str


@dataclass
class ExplainStmt:
    """Represents an EXPLAIN statement."""
    query: str


class SQLParser:
    """Parser for simplified SQL."""

    def __init__(self):
        self.tokens = []
        self.pos = 0

    def parse(self, sql: str):
        """Parse a SQL statement."""
        sql = sql.strip()
        if not sql:
            logger.warning("Empty SQL statement attempted")
            raise ParseError("Empty query")

        # Normalize whitespace
        sql = re.sub(r"\s+", " ", sql)
        logger.debug(f"Parsing SQL: {sql[:100]}")

        # Check command type
        if sql.upper().startswith("CREATE TABLE"):
            logger.debug("Parsing CREATE TABLE statement")
            return self._parse_create_table(sql)
        elif sql.upper().startswith("INSERT"):
            logger.debug("Parsing INSERT statement")
            return self._parse_insert(sql)
        elif sql.upper().startswith("SELECT"):
            logger.debug("Parsing SELECT statement")
            return self._parse_select(sql)
        elif sql.upper().startswith("UPDATE"):
            logger.debug("Parsing UPDATE statement")
            return self._parse_update(sql)
        elif sql.upper().startswith("DELETE"):
            logger.debug("Parsing DELETE statement")
            return self._parse_delete(sql)
        elif sql.upper().startswith("DROP TABLE"):
            logger.debug("Parsing DROP TABLE statement")
            return self._parse_drop_table(sql)
        elif sql.upper().startswith("EXPLAIN"):
            return self._parse_explain(sql)
        else:
            raise ParseError(f"Unknown command: {sql}")

    def _parse_create_table(self, sql: str) -> CreateTableStmt:
        """Parse CREATE TABLE statement."""
        # CREATE TABLE users (id INT PRIMARY KEY, name TEXT, active BOOLEAN)
        match = re.match(
            r"CREATE\s+TABLE\s+(\w+)\s*\((.*)\)",
            sql,
            re.IGNORECASE,
        )
        if not match:
            raise ParseError("Invalid CREATE TABLE syntax")

        table_name = match.group(1)
        columns_str = match.group(2)

        columns = []
        for col_def in self._split_by_comma(columns_str):
            col_def = col_def.strip()
            parts = col_def.split()

            if len(parts) < 2:
                raise ParseError(f"Invalid column definition: {col_def}")

            col_name = parts[0]
            data_type_str = parts[1].upper()

            try:
                data_type = DataType[data_type_str]
            except KeyError:
                raise ParseError(f"Unknown data type: {data_type_str}")

            primary_key = "PRIMARY" in col_def.upper() and "KEY" in col_def.upper()
            unique = "UNIQUE" in col_def.upper()
            nullable = "NOT" not in col_def.upper() or "NULL" not in col_def.upper()

            columns.append(
                Column(
                    name=col_name,
                    data_type=data_type,
                    primary_key=primary_key,
                    unique=unique,
                    nullable=nullable,
                )
            )

        return CreateTableStmt(table_name=table_name, columns=columns)

    def _parse_insert(self, sql: str) -> InsertStmt:
        """Parse INSERT statement."""
        # INSERT INTO users (id, name) VALUES (1, 'John')
        match = re.match(
            r"INSERT\s+INTO\s+(\w+)\s*\((.*?)\)\s+VALUES\s*\((.*)\)",
            sql,
            re.IGNORECASE,
        )
        if not match:
            raise ParseError("Invalid INSERT syntax")

        table_name = match.group(1)
        columns_str = match.group(2)
        values_str = match.group(3)

        columns = [col.strip() for col in self._split_by_comma(columns_str)]
        values = self._parse_values(values_str)

        if len(columns) != len(values):
            raise ParseError("Column and value count mismatch")

        return InsertStmt(table_name=table_name, columns=columns, values=values)

    def _parse_select(self, sql: str) -> SelectStmt:
        """Parse SELECT statement."""
        # SELECT * FROM users WHERE id = 1
        # SELECT id, name FROM users
        # SELECT * FROM users JOIN orders ON users.id = orders.user_id

        match = re.match(
            r"SELECT\s+(.*?)\s+FROM\s+(\w+)(?:\s+(.*))?",
            sql,
            re.IGNORECASE,
        )
        if not match:
            raise ParseError("Invalid SELECT syntax")

        columns_str = match.group(1)
        table_name = match.group(2)
        rest = match.group(3) or ""

        # Parse columns
        if columns_str.strip() == "*":
            columns = []
        else:
            columns = [col.strip() for col in self._split_by_comma(columns_str)]

        # Parse WHERE clause
        where_clause = None
        where_match = re.search(
            r"WHERE\s+(\w+)\s*(=|!=|<|>|<=|>=)\s*(.+?)(?:\s+JOIN|\s*$)",
            rest,
            re.IGNORECASE,
        )
        if where_match:
            col_name = where_match.group(1)
            operator = where_match.group(2)
            value_str = where_match.group(3).strip()
            # Remove trailing content if JOIN is present
            if 'JOIN' in rest[where_match.end():].upper():
                value_str = value_str.split('JOIN')[0].strip()
            value = self._parse_value(value_str)
            where_clause = (col_name, operator, value)

        # Parse JOIN clause
        join_table = None
        join_on = None
        join_match = re.search(
            r"JOIN\s+(\w+)\s+ON\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)",
            rest,
            re.IGNORECASE,
        )
        if join_match:
            join_table = join_match.group(1)
            left_table = join_match.group(2)
            left_col = join_match.group(3)
            right_table = join_match.group(4)
            right_col = join_match.group(5)
            join_on = (f"{left_table}.{left_col}", f"{right_table}.{right_col}")

        return SelectStmt(
            table_name=table_name,
            columns=columns,
            where_clause=where_clause,
            join_table=join_table,
            join_on=join_on,
        )

    def _parse_update(self, sql: str) -> UpdateStmt:
        """Parse UPDATE statement."""
        # UPDATE users SET name = 'Jane' WHERE id = 1
        match = re.match(
            r"UPDATE\s+(\w+)\s+SET\s+(.+?)(?:\s+WHERE\s+(.*))?$",
            sql,
            re.IGNORECASE,
        )
        if not match:
            raise ParseError("Invalid UPDATE syntax")

        table_name = match.group(1)
        set_clause = match.group(2)
        where_clause_str = match.group(3)

        # Parse SET clause
        updates = {}
        for assignment in self._split_by_comma(set_clause):
            parts = assignment.split("=", 1)
            if len(parts) != 2:
                raise ParseError(f"Invalid SET clause: {assignment}")

            col_name = parts[0].strip()
            value = self._parse_value(parts[1].strip())
            updates[col_name] = value

        # Parse WHERE clause
        where_clause = None
        if where_clause_str:
            match = re.match(
                r"(\w+)\s*(=|!=|<|>|<=|>=)\s*(.*)",
                where_clause_str,
            )
            if match:
                col_name = match.group(1)
                operator = match.group(2)
                value = self._parse_value(match.group(3))
                where_clause = (col_name, operator, value)

        return UpdateStmt(
            table_name=table_name, updates=updates, where_clause=where_clause
        )

    def _parse_delete(self, sql: str) -> DeleteStmt:
        """Parse DELETE statement."""
        # DELETE FROM users WHERE id = 1
        match = re.match(
            r"DELETE\s+FROM\s+(\w+)(?:\s+WHERE\s+(.*))?",
            sql,
            re.IGNORECASE,
        )
        if not match:
            raise ParseError("Invalid DELETE syntax")

        table_name = match.group(1)
        where_clause_str = match.group(2)

        where_clause = None
        if where_clause_str:
            match = re.match(
                r"(\w+)\s*(=|!=|<|>|<=|>=)\s*(.*)",
                where_clause_str,
            )
            if match:
                col_name = match.group(1)
                operator = match.group(2)
                value = self._parse_value(match.group(3))
                where_clause = (col_name, operator, value)

        return DeleteStmt(table_name=table_name, where_clause=where_clause)

    def _parse_drop_table(self, sql: str) -> DropTableStmt:
        """Parse DROP TABLE statement."""
        match = re.match(r"DROP\s+TABLE\s+(\w+)", sql, re.IGNORECASE)
        if not match:
            raise ParseError("Invalid DROP TABLE syntax")

        return DropTableStmt(table_name=match.group(1))

    def _parse_explain(self, sql: str) -> ExplainStmt:
        """Parse EXPLAIN statement."""
        match = re.match(r"EXPLAIN\s+(.*)", sql, re.IGNORECASE)
        if not match:
            raise ParseError("Invalid EXPLAIN syntax")

        return ExplainStmt(query=match.group(1))

    def _parse_value(self, value_str: str) -> Any:
        """Parse a single value."""
        value_str = value_str.strip()

        # Check for string literal
        if (value_str.startswith("'") and value_str.endswith("'")) or (
            value_str.startswith('"') and value_str.endswith('"')
        ):
            return value_str[1:-1]

        # Check for boolean
        if value_str.upper() in ("TRUE", "FALSE"):
            return value_str.upper() == "TRUE"

        # Check for number
        try:
            if "." in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            pass

        # Return as string if no match
        return value_str

    def _parse_values(self, values_str: str) -> List[Any]:
        """Parse a list of values."""
        values = []
        for val in self._split_by_comma(values_str):
            values.append(self._parse_value(val.strip()))
        return values

    def _split_by_comma(self, text: str) -> List[str]:
        """Split by comma, respecting quoted strings."""
        parts = []
        current = ""
        in_quotes = False
        quote_char = None

        for char in text:
            if char in ("'", '"') and (not in_quotes or char == quote_char):
                in_quotes = not in_quotes
                quote_char = char if in_quotes else None
                current += char
            elif char == "," and not in_quotes:
                if current.strip():
                    parts.append(current.strip())
                current = ""
            else:
                current += char

        if current.strip():
            parts.append(current.strip())

        return parts
