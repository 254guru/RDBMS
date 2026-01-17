"""Unit tests for rdbms.parser module."""

import pytest
from rdbms.parser import (
    SQLParser,
    ParseError,
    CreateTableStmt,
    InsertStmt,
    SelectStmt,
    UpdateStmt,
    DeleteStmt,
    DropTableStmt,
)
from rdbms.types import DataType


class TestSQLParser:
    """Tests for SQLParser class."""

    @pytest.fixture
    def parser(self):
        """Create a parser instance."""
        return SQLParser()

    def test_parser_creation(self, parser):
        """Test parser instantiation."""
        assert parser is not None
        assert parser.tokens == []
        assert parser.pos == 0

    def test_parse_empty_query(self, parser):
        """Test parsing empty query raises error."""
        with pytest.raises(ParseError):
            parser.parse("")

    def test_parse_whitespace_only(self, parser):
        """Test parsing whitespace-only query."""
        with pytest.raises(ParseError):
            parser.parse("   \n  \t  ")


class TestCreateTableParsing:
    """Tests for CREATE TABLE parsing."""

    @pytest.fixture
    def parser(self):
        return SQLParser()

    def test_parse_create_table_basic(self, parser):
        """Test parsing basic CREATE TABLE statement."""
        sql = "CREATE TABLE users (id INT PRIMARY KEY, name TEXT)"
        stmt = parser.parse(sql)
        
        assert isinstance(stmt, CreateTableStmt)
        assert stmt.table_name == "users"
        assert len(stmt.columns) == 2
        assert stmt.columns[0].name == "id"
        assert stmt.columns[0].data_type == DataType.INT
        assert stmt.columns[0].primary_key is True

    def test_parse_create_table_with_constraints(self, parser):
        """Test parsing CREATE TABLE with multiple constraints."""
        sql = "CREATE TABLE products (id INT PRIMARY KEY, name TEXT UNIQUE, price INT)"
        stmt = parser.parse(sql)
        
        assert stmt.table_name == "products"
        assert len(stmt.columns) == 3
        assert stmt.columns[1].unique is True
        assert stmt.columns[0].primary_key is True

    def test_parse_create_table_with_nullable(self, parser):
        """Test parsing CREATE TABLE with nullable columns."""
        sql = "CREATE TABLE items (id INT PRIMARY KEY, description TEXT)"
        stmt = parser.parse(sql)
        
        assert stmt.columns[1].nullable is True

    def test_parse_create_table_case_insensitive(self, parser):
        """Test that parsing is case-insensitive."""
        sql = "create table Users (id int primary key, name text)"
        stmt = parser.parse(sql)
        
        assert stmt.table_name == "Users"
        assert stmt.columns[0].data_type == DataType.INT


class TestInsertParsing:
    """Tests for INSERT parsing."""

    @pytest.fixture
    def parser(self):
        return SQLParser()

    def test_parse_insert_basic(self, parser):
        """Test parsing basic INSERT statement."""
        sql = "INSERT INTO users (id, name) VALUES (1, 'Alice')"
        stmt = parser.parse(sql)
        
        assert isinstance(stmt, InsertStmt)
        assert stmt.table_name == "users"
        assert stmt.columns == ["id", "name"]
        assert stmt.values == [1, "Alice"]

    def test_parse_insert_multiple_values(self, parser):
        """Test parsing INSERT with multiple rows."""
        sql = "INSERT INTO users (id, name, active) VALUES (1, 'Alice', true)"
        stmt = parser.parse(sql)
        
        assert len(stmt.values) == 3
        assert stmt.values[2] is True

    def test_parse_insert_string_values(self, parser):
        """Test parsing INSERT with string values."""
        sql = "INSERT INTO users (id, name) VALUES (1, 'Alice')"
        stmt = parser.parse(sql)
        
        assert stmt.values[1] == "Alice"

    def test_parse_insert_numeric_values(self, parser):
        """Test parsing INSERT with numeric values."""
        sql = "INSERT INTO users (id, age) VALUES (1, 25)"
        stmt = parser.parse(sql)
        
        assert stmt.values[0] == 1
        assert stmt.values[1] == 25


class TestSelectParsing:
    """Tests for SELECT parsing."""

    @pytest.fixture
    def parser(self):
        return SQLParser()

    def test_parse_select_all(self, parser):
        """Test parsing SELECT * statement."""
        sql = "SELECT * FROM users"
        stmt = parser.parse(sql)
        
        assert isinstance(stmt, SelectStmt)
        assert stmt.table_name == "users"
        assert stmt.columns == []  # Empty means SELECT *

    def test_parse_select_specific_columns(self, parser):
        """Test parsing SELECT with specific columns."""
        sql = "SELECT id, name FROM users"
        stmt = parser.parse(sql)
        
        assert stmt.columns == ["id", "name"]

    def test_parse_select_with_where(self, parser):
        """Test parsing SELECT with WHERE clause."""
        sql = "SELECT * FROM users WHERE id = 1"
        stmt = parser.parse(sql)
        
        assert stmt.where_clause is not None
        column, operator, value = stmt.where_clause
        assert column == "id"
        assert operator == "="
        assert value == 1

    def test_parse_select_where_text(self, parser):
        """Test parsing SELECT WHERE with text values."""
        sql = "SELECT * FROM users WHERE name = 'Alice'"
        stmt = parser.parse(sql)
        
        column, operator, value = stmt.where_clause
        assert value == "Alice"

    def test_parse_select_where_operators(self, parser):
        """Test SELECT WHERE with basic operators."""
        # Note: Parser supports single-character operators
        operators = ["=", "!=", "<", ">"]
        
        for op in operators:
            sql = f"SELECT * FROM users WHERE age {op} 25"
            stmt = parser.parse(sql)
            assert stmt.where_clause is not None
            assert stmt.where_clause[0] == "age"


class TestUpdateParsing:
    """Tests for UPDATE parsing."""

    @pytest.fixture
    def parser(self):
        return SQLParser()

    def test_parse_update_basic(self, parser):
        """Test parsing basic UPDATE statement."""
        sql = "UPDATE users SET name = 'Bob' WHERE id = 1"
        stmt = parser.parse(sql)
        
        assert isinstance(stmt, UpdateStmt)
        assert stmt.table_name == "users"
        assert "name" in stmt.updates
        assert stmt.updates["name"] == "Bob"
        assert stmt.where_clause[0] == "id"

    def test_parse_update_multiple_columns(self, parser):
        """Test parsing UPDATE with multiple columns."""
        sql = "UPDATE users SET name = 'Bob', age = 30 WHERE id = 1"
        stmt = parser.parse(sql)
        
        assert len(stmt.updates) == 2
        assert stmt.updates["name"] == "Bob"
        assert stmt.updates["age"] == 30


class TestDeleteParsing:
    """Tests for DELETE parsing."""

    @pytest.fixture
    def parser(self):
        return SQLParser()

    def test_parse_delete_basic(self, parser):
        """Test parsing basic DELETE statement."""
        sql = "DELETE FROM users WHERE id = 1"
        stmt = parser.parse(sql)
        
        assert isinstance(stmt, DeleteStmt)
        assert stmt.table_name == "users"
        assert stmt.where_clause[0] == "id"
        assert stmt.where_clause[2] == 1


class TestDropTableParsing:
    """Tests for DROP TABLE parsing."""

    @pytest.fixture
    def parser(self):
        return SQLParser()

    def test_parse_drop_table(self, parser):
        """Test parsing DROP TABLE statement."""
        sql = "DROP TABLE users"
        stmt = parser.parse(sql)
        
        assert isinstance(stmt, DropTableStmt)
        assert stmt.table_name == "users"


class TestParsingEdgeCases:
    """Tests for edge cases in parsing."""

    @pytest.fixture
    def parser(self):
        return SQLParser()

    def test_parse_with_extra_whitespace(self, parser):
        """Test parsing with extra whitespace."""
        sql = "  SELECT   *   FROM   users  WHERE  id  =  1  "
        stmt = parser.parse(sql)
        
        assert stmt.table_name == "users"

    def test_parse_with_newlines(self, parser):
        """Test parsing with newlines."""
        sql = """SELECT *
                 FROM users
                 WHERE id = 1"""
        stmt = parser.parse(sql)
        
        assert stmt.table_name == "users"

    def test_parse_invalid_statement(self, parser):
        """Test parsing invalid statement."""
        sql = "INVALID COMMAND"
        with pytest.raises(ParseError):
            parser.parse(sql)
