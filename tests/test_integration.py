"""Integration tests for complete workflows."""

import pytest
from rdbms.storage import Database
from rdbms.parser import SQLParser
from rdbms.engine import ExecutionEngine


class TestIntegrationBasicWorkflow:
    """Integration tests for basic RDBMS workflows."""

    @pytest.fixture
    def system(self, temp_db_dir):
        """Set up complete RDBMS system."""
        db = Database(temp_db_dir)
        parser = SQLParser()
        engine = ExecutionEngine(db)
        return db, parser, engine

    def test_merchant_management_workflow(self, system):
        """Test complete merchant management workflow."""
        db, parser, engine = system
        
        # Create merchants table
        engine.execute(parser.parse(
            "CREATE TABLE merchants (id INT PRIMARY KEY, name TEXT UNIQUE, category TEXT, active BOOLEAN)"
        ))
        
        # Insert merchants
        engine.execute(parser.parse(
            "INSERT INTO merchants (id, name, category, active) VALUES (1, 'Store A', 'Retail', true)"
        ))
        engine.execute(parser.parse(
            "INSERT INTO merchants (id, name, category, active) VALUES (2, 'Store B', 'Retail', true)"
        ))
        engine.execute(parser.parse(
            "INSERT INTO merchants (id, name, category, active) VALUES (3, 'Cafe C', 'Food', true)"
        ))
        
        # Select all
        result = engine.execute(parser.parse("SELECT * FROM merchants"))
        assert len(result.data) == 3
        
        # Update merchant
        engine.execute(parser.parse(
            "UPDATE merchants SET category = 'Restaurant' WHERE id = 3"
        ))
        result = engine.execute(parser.parse("SELECT * FROM merchants WHERE id = 3"))
        assert result.data[0]["category"] == "Restaurant"
        
        # Delete merchant
        engine.execute(parser.parse("DELETE FROM merchants WHERE id = 2"))
        result = engine.execute(parser.parse("SELECT * FROM merchants"))
        assert len(result.data) == 2

    def test_multiple_tables_workflow(self, system):
        """Test managing multiple tables."""
        db, parser, engine = system
        
        # Create users table
        engine.execute(parser.parse(
            "CREATE TABLE users (id INT PRIMARY KEY, name TEXT UNIQUE, email TEXT)"
        ))
        
        # Create categories table
        engine.execute(parser.parse(
            "CREATE TABLE categories (id INT PRIMARY KEY, name TEXT UNIQUE, description TEXT)"
        ))
        
        # Insert data into users
        engine.execute(parser.parse(
            "INSERT INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com')"
        ))
        
        # Insert data into categories
        engine.execute(parser.parse(
            "INSERT INTO categories (id, name, description) VALUES (1, 'Retail', 'Retail stores')"
        ))
        
        # Verify both tables exist and have data
        users = engine.execute(parser.parse("SELECT * FROM users"))
        categories = engine.execute(parser.parse("SELECT * FROM categories"))
        
        assert len(users.data) == 1
        assert len(categories.data) == 1
        assert users.data[0]["name"] == "Alice"
        assert categories.data[0]["name"] == "Retail"

    def test_constraint_enforcement(self, system):
        """Test PRIMARY KEY and UNIQUE constraint enforcement."""
        db, parser, engine = system
        
        engine.execute(parser.parse(
            "CREATE TABLE users (id INT PRIMARY KEY, email TEXT UNIQUE)"
        ))
        
        # Insert first record
        result1 = engine.execute(parser.parse(
            "INSERT INTO users (id, email) VALUES (1, 'alice@example.com')"
        ))
        assert result1.success is True
        
        # Try duplicate primary key
        result2 = engine.execute(parser.parse(
            "INSERT INTO users (id, email) VALUES (1, 'bob@example.com')"
        ))
        assert result2.success is False
        
        # Try duplicate unique email
        result3 = engine.execute(parser.parse(
            "INSERT INTO users (id, email) VALUES (2, 'alice@example.com')"
        ))
        assert result3.success is False

    def test_filtering_workflow(self, system):
        """Test complex filtering scenarios."""
        db, parser, engine = system
        
        engine.execute(parser.parse(
            "CREATE TABLE transactions (id INT PRIMARY KEY, amount INT, type TEXT, status TEXT)"
        ))
        
        # Insert transactions
        transactions = [
            (1, 100, "payment", "completed"),
            (2, 200, "refund", "completed"),
            (3, 150, "payment", "pending"),
            (4, 75, "payment", "completed"),
        ]
        
        for tid, amount, ttype, status in transactions:
            engine.execute(parser.parse(
                f"INSERT INTO transactions (id, amount, type, status) VALUES ({tid}, {amount}, '{ttype}', '{status}')"
            ))
        
        # Filter by type
        payments = engine.execute(parser.parse("SELECT * FROM transactions WHERE type = 'payment'"))
        assert len(payments.data) == 3
        
        # Filter by status
        completed = engine.execute(parser.parse("SELECT * FROM transactions WHERE status = 'completed'"))
        assert len(completed.data) == 3
        
        # Filter by amount (using > operator)
        large = engine.execute(parser.parse("SELECT * FROM transactions WHERE amount > 100"))
        assert len(large.data) == 2

    def test_data_persistence(self, system):
        """Test data persistence across sessions."""
        db, parser, engine = system
        temp_dir = db.db_dir
        
        # Create and populate table
        engine.execute(parser.parse(
            "CREATE TABLE sessions (id INT PRIMARY KEY, user_id INT, token TEXT)"
        ))
        engine.execute(parser.parse(
            "INSERT INTO sessions (id, user_id, token) VALUES (1, 100, 'abc123')"
        ))
        
        # Verify data
        result1 = engine.execute(parser.parse("SELECT * FROM sessions"))
        assert len(result1.data) == 1
        
        # Create new database instance from same directory
        db2 = Database(temp_dir)
        engine2 = ExecutionEngine(db2)
        
        # Verify data persisted
        result2 = engine2.execute(parser.parse("SELECT * FROM sessions"))
        assert len(result2.data) == 1
        assert result2.data[0]["token"] == "abc123"

    def test_comprehensive_crud_operations(self, system):
        """Test all CRUD operations in sequence."""
        db, parser, engine = system
        
        # CREATE
        create_result = engine.execute(parser.parse(
            "CREATE TABLE items (id INT PRIMARY KEY, title TEXT, qty INT)"
        ))
        assert create_result.success is True
        
        # CREATE (INSERT)
        insert1 = engine.execute(parser.parse(
            "INSERT INTO items (id, title, qty) VALUES (1, 'Item 1', 10)"
        ))
        assert insert1.success is True
        
        insert2 = engine.execute(parser.parse(
            "INSERT INTO items (id, title, qty) VALUES (2, 'Item 2', 20)"
        ))
        assert insert2.success is True
        
        # READ
        read_all = engine.execute(parser.parse("SELECT * FROM items"))
        assert len(read_all.data) == 2
        
        read_one = engine.execute(parser.parse("SELECT * FROM items WHERE id = 1"))
        assert len(read_one.data) == 1
        assert read_one.data[0]["title"] == "Item 1"
        
        # UPDATE
        update_result = engine.execute(parser.parse(
            "UPDATE items SET qty = 15 WHERE id = 1"
        ))
        assert update_result.success is True
        
        verify_update = engine.execute(parser.parse("SELECT * FROM items WHERE id = 1"))
        assert verify_update.data[0]["qty"] == 15
        
        # DELETE
        delete_result = engine.execute(parser.parse("DELETE FROM items WHERE id = 2"))
        assert delete_result.success is True
        
        verify_delete = engine.execute(parser.parse("SELECT * FROM items"))
        assert len(verify_delete.data) == 1

    def test_error_recovery_workflow(self, system):
        """Test system behavior during error conditions."""
        db, parser, engine = system
        
        engine.execute(parser.parse(
            "CREATE TABLE products (id INT PRIMARY KEY, name TEXT)"
        ))
        
        # Insert valid data
        engine.execute(parser.parse(
            "INSERT INTO products (id, name) VALUES (1, 'Product A')"
        ))
        
        # Try invalid operation (should fail gracefully)
        invalid = engine.execute(parser.parse(
            "INSERT INTO products (id, name) VALUES (1, 'Product B')"  # Duplicate ID
        ))
        assert invalid.success is False
        
        # Verify original data still intact
        verify = engine.execute(parser.parse("SELECT * FROM products"))
        assert len(verify.data) == 1
        assert verify.data[0]["name"] == "Product A"
        
        # Continue with valid operation
        valid = engine.execute(parser.parse(
            "INSERT INTO products (id, name) VALUES (2, 'Product B')"
        ))
        assert valid.success is True
        
        # Verify both records
        verify2 = engine.execute(parser.parse("SELECT * FROM products"))
        assert len(verify2.data) == 2
