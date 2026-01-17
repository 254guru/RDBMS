"""Unit tests for rdbms.engine module."""

import pytest
from rdbms.engine import ExecutionEngine, QueryResult
from rdbms.storage import Database
from rdbms.parser import SQLParser
from rdbms.types import Schema, Column, DataType


class TestExecutionEngine:
    """Tests for ExecutionEngine class."""

    @pytest.fixture
    def setup(self, temp_db_dir):
        """Set up engine with database and parser."""
        db = Database(temp_db_dir)
        engine = ExecutionEngine(db)
        parser = SQLParser()
        return engine, parser, db

    def test_engine_creation(self, setup):
        """Test engine instantiation."""
        engine, _, _ = setup
        assert engine is not None

    def test_engine_create_table(self, setup):
        """Test CREATE TABLE execution."""
        engine, parser, _ = setup
        
        sql = "CREATE TABLE users (id INT PRIMARY KEY, name TEXT)"
        stmt = parser.parse(sql)
        result = engine.execute(stmt)
        
        assert result.success is True
        assert "created successfully" in result.message.lower()

    def test_engine_insert(self, setup):
        """Test INSERT execution."""
        engine, parser, db = setup
        
        # Create table first
        create_sql = "CREATE TABLE users (id INT PRIMARY KEY, name TEXT)"
        create_stmt = parser.parse(create_sql)
        engine.execute(create_stmt)
        
        # Insert data
        insert_sql = "INSERT INTO users (id, name) VALUES (1, 'Alice')"
        insert_stmt = parser.parse(insert_sql)
        result = engine.execute(insert_stmt)
        
        assert result.success is True
        assert "1 row inserted" in result.message

    def test_engine_select_all(self, setup):
        """Test SELECT * execution."""
        engine, parser, db = setup
        
        # Create and populate table
        create_sql = "CREATE TABLE users (id INT PRIMARY KEY, name TEXT)"
        create_stmt = parser.parse(create_sql)
        engine.execute(create_stmt)
        
        insert_sql = "INSERT INTO users (id, name) VALUES (1, 'Alice')"
        insert_stmt = parser.parse(insert_sql)
        engine.execute(insert_stmt)
        
        # Select all
        select_sql = "SELECT * FROM users"
        select_stmt = parser.parse(select_sql)
        result = engine.execute(select_stmt)
        
        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0]["name"] == "Alice"

    def test_engine_select_with_where(self, setup):
        """Test SELECT with WHERE clause."""
        engine, parser, db = setup
        
        # Create and populate table
        create_sql = "CREATE TABLE users (id INT PRIMARY KEY, name TEXT, age INT)"
        create_stmt = parser.parse(create_sql)
        engine.execute(create_stmt)
        
        engine.execute(parser.parse("INSERT INTO users (id, name, age) VALUES (1, 'Alice', 30)"))
        engine.execute(parser.parse("INSERT INTO users (id, name, age) VALUES (2, 'Bob', 25)"))
        
        # Select with where
        select_sql = "SELECT * FROM users WHERE age > 25"
        select_stmt = parser.parse(select_sql)
        result = engine.execute(select_stmt)
        
        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0]["name"] == "Alice"

    def test_engine_select_specific_columns(self, setup):
        """Test SELECT with specific columns."""
        engine, parser, db = setup
        
        create_sql = "CREATE TABLE users (id INT PRIMARY KEY, name TEXT, email TEXT)"
        engine.execute(parser.parse(create_sql))
        engine.execute(parser.parse("INSERT INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com')"))
        
        select_sql = "SELECT name FROM users"
        result = engine.execute(parser.parse(select_sql))
        
        assert result.success is True
        assert "id" not in result.data[0]
        assert "name" in result.data[0]

    def test_engine_update(self, setup):
        """Test UPDATE execution."""
        engine, parser, db = setup
        
        create_sql = "CREATE TABLE users (id INT PRIMARY KEY, name TEXT, active BOOLEAN)"
        engine.execute(parser.parse(create_sql))
        engine.execute(parser.parse("INSERT INTO users (id, name, active) VALUES (1, 'Alice', true)"))
        
        update_sql = "UPDATE users SET active = false WHERE id = 1"
        result = engine.execute(parser.parse(update_sql))
        
        assert result.success is True
        
        # Verify update
        select_result = engine.execute(parser.parse("SELECT * FROM users WHERE id = 1"))
        assert select_result.data[0]["active"] is False

    def test_engine_delete(self, setup):
        """Test DELETE execution."""
        engine, parser, db = setup
        
        create_sql = "CREATE TABLE users (id INT PRIMARY KEY, name TEXT)"
        engine.execute(parser.parse(create_sql))
        engine.execute(parser.parse("INSERT INTO users (id, name) VALUES (1, 'Alice')"))
        engine.execute(parser.parse("INSERT INTO users (id, name) VALUES (2, 'Bob')"))
        
        delete_sql = "DELETE FROM users WHERE id = 1"
        result = engine.execute(parser.parse(delete_sql))
        
        assert result.success is True
        
        # Verify deletion
        select_result = engine.execute(parser.parse("SELECT * FROM users"))
        assert len(select_result.data) == 1
        assert select_result.data[0]["name"] == "Bob"

    def test_engine_drop_table(self, setup):
        """Test DROP TABLE execution."""
        engine, parser, db = setup
        
        engine.execute(parser.parse("CREATE TABLE users (id INT PRIMARY KEY, name TEXT)"))
        
        drop_sql = "DROP TABLE users"
        result = engine.execute(parser.parse(drop_sql))
        
        assert result.success is True
        assert db.get_table("users") is None

    def test_engine_nonexistent_table(self, setup):
        """Test error handling for non-existent table."""
        engine, parser, db = setup
        
        select_sql = "SELECT * FROM nonexistent"
        result = engine.execute(parser.parse(select_sql))
        
        assert result.success is False
        assert "not found" in result.message.lower()

    def test_query_result_data_structure(self):
        """Test QueryResult structure."""
        result = QueryResult(success=True, message="Test", data=[{"id": 1}])
        
        assert result.success is True
        assert result.message == "Test"
        assert len(result.data) == 1
        assert result.stats is not None

    def test_engine_multiple_inserts_and_select(self, setup):
        """Test multiple inserts followed by select."""
        engine, parser, db = setup
        
        engine.execute(parser.parse("CREATE TABLE products (id INT PRIMARY KEY, name TEXT, price INT)"))
        
        for i in range(1, 4):
            sql = f"INSERT INTO products (id, name, price) VALUES ({i}, 'Product{i}', {i*100})"
            engine.execute(parser.parse(sql))
        
        result = engine.execute(parser.parse("SELECT * FROM products"))
        
        assert result.success is True
        assert len(result.data) == 3
