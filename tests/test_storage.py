"""Unit tests for rdbms.storage module."""

import pytest
import os
import json
from rdbms.storage import Database, Table, HashIndex
from rdbms.types import Schema, Column, DataType, Row


class TestHashIndex:
    """Tests for HashIndex class."""

    def test_index_creation(self):
        """Test hash index creation."""
        index = HashIndex()
        assert index.index == {}

    def test_index_add(self):
        """Test adding entries to index."""
        index = HashIndex()
        index.add("key1", 1)
        
        assert "key1" in index.index
        assert 1 in index.index["key1"]

    def test_index_add_multiple_rows(self):
        """Test adding multiple rows for same key."""
        index = HashIndex()
        index.add("key1", 1)
        index.add("key1", 2)
        
        assert len(index.index["key1"]) == 2

    def test_index_lookup(self):
        """Test looking up values in index."""
        index = HashIndex()
        index.add("key1", 1)
        index.add("key1", 2)
        
        result = index.lookup("key1")
        assert 1 in result
        assert 2 in result

    def test_index_lookup_not_found(self):
        """Test lookup for non-existent key."""
        index = HashIndex()
        result = index.lookup("nonexistent")
        assert result == []

    def test_index_remove(self):
        """Test removing entries from index."""
        index = HashIndex()
        index.add("key1", 1)
        index.add("key1", 2)
        index.remove("key1", 1)
        
        result = index.lookup("key1")
        assert 1 not in result
        assert 2 in result

    def test_index_remove_last_entry(self):
        """Test removing the last entry for a key."""
        index = HashIndex()
        index.add("key1", 1)
        index.remove("key1", 1)
        
        assert "key1" not in index.index

    def test_index_serialization(self):
        """Test index serialization to dict."""
        index = HashIndex()
        index.add("key1", 1)
        index.add("key1", 2)
        
        serialized = index.to_dict()
        assert "key1" in serialized
        assert set(serialized["key1"]) == {1, 2}

    def test_index_deserialization(self):
        """Test index deserialization from dict."""
        data = {"1": [1, 2], "2": [3]}
        index = HashIndex.from_dict(data)
        
        assert 1 in index.lookup(1)
        assert 2 in index.lookup(1)


class TestTable:
    """Tests for Table class."""

    @pytest.fixture
    def schema(self):
        """Create a test schema."""
        return Schema(
            table_name="test_table",
            columns=[
                Column(name="id", data_type=DataType.INT, primary_key=True, nullable=False),
                Column(name="name", data_type=DataType.TEXT, unique=True, nullable=False),
                Column(name="active", data_type=DataType.BOOLEAN, nullable=True),
            ]
        )

    @pytest.fixture
    def table(self, schema, temp_db_dir):
        """Create a test table."""
        return Table(schema, temp_db_dir)

    def test_table_creation(self, table):
        """Test table instantiation."""
        assert table.schema.table_name == "test_table"
        assert len(table.rows) == 0
        assert table.primary_key_index is not None
        assert "name" in table.unique_indexes

    def test_table_insert(self, table):
        """Test inserting a row into table."""
        row_id = table.insert({"id": 1, "name": "Alice", "active": True})
        
        assert row_id == 0  # Internal row ID starts at 0
        assert len(table.rows) == 1
        assert table.rows[0].get("id") == 1

    def test_table_insert_increments_id(self, table):
        """Test that row IDs are incremented."""
        id1 = table.insert({"id": 1, "name": "Alice", "active": True})
        id2 = table.insert({"id": 2, "name": "Bob", "active": False})
        
        assert id1 == 0  # Internal row IDs start at 0
        assert id2 == 1

    def test_table_insert_duplicate_primary_key(self, table):
        """Test that duplicate primary keys are rejected."""
        table.insert({"id": 1, "name": "Alice", "active": True})
        
        with pytest.raises(Exception):
            table.insert({"id": 1, "name": "Bob", "active": True})

    def test_table_insert_duplicate_unique(self, table):
        """Test that duplicate unique values are rejected."""
        table.insert({"id": 1, "name": "Alice", "active": True})
        
        with pytest.raises(Exception):
            table.insert({"id": 2, "name": "Alice", "active": False})

    def test_table_get_by_primary_key(self, table):
        """Test retrieving row by primary key."""
        table.insert({"id": 1, "name": "Alice", "active": True})
        
        row = table.get_by_primary_key(1)
        assert row is not None
        assert row.get("name") == "Alice"

    def test_table_get_by_primary_key_not_found(self, table):
        """Test retrieving non-existent row by primary key."""
        row = table.get_by_primary_key(999)
        assert row is None

    def test_table_scan_all_rows(self, table):
        """Test scanning all rows."""
        table.insert({"id": 1, "name": "Alice", "active": True})
        table.insert({"id": 2, "name": "Bob", "active": False})
        
        rows = table.scan()
        assert len(rows) == 2

    def test_table_filter(self, table):
        """Test filtering rows."""
        table.insert({"id": 1, "name": "Alice", "active": True})
        table.insert({"id": 2, "name": "Bob", "active": True})
        table.insert({"id": 3, "name": "Charlie", "active": False})
        
        active_rows = table.filter("active", "=", True)
        assert len(active_rows) == 2

    def test_table_update(self, table):
        """Test updating a row."""
        table.insert({"id": 1, "name": "Alice", "active": True})
        
        table.update(0, {"active": False})
        
        row = table.get_by_primary_key(1)
        assert row.get("active") is False

    def test_table_delete(self, table):
        """Test deleting a row."""
        table.insert({"id": 1, "name": "Alice", "active": True})
        table.insert({"id": 2, "name": "Bob", "active": False})
        
        table.delete(0)
        
        assert len(table.rows) == 1
        assert table.rows[0].get("id") == 2


class TestDatabase:
    """Tests for Database class."""

    def test_database_creation(self, temp_db_dir):
        """Test database instantiation."""
        db = Database(temp_db_dir)
        assert db.db_dir == temp_db_dir
        assert len(db.tables) == 0

    def test_database_create_table(self, temp_db_dir, sample_schema):
        """Test creating a table in database."""
        db = Database(temp_db_dir)
        db.create_table(sample_schema)
        
        assert "test_table" in db.tables
        assert db.tables["test_table"] is not None

    def test_database_get_table(self, temp_db_dir, sample_schema):
        """Test retrieving a table from database."""
        db = Database(temp_db_dir)
        db.create_table(sample_schema)
        
        table = db.get_table("test_table")
        assert table is not None
        assert table.schema.table_name == "test_table"

    def test_database_get_nonexistent_table(self, temp_db_dir):
        """Test retrieving non-existent table."""
        db = Database(temp_db_dir)
        table = db.get_table("nonexistent")
        assert table is None

    def test_database_list_tables(self, temp_db_dir, sample_schema):
        """Test listing tables in database."""
        db = Database(temp_db_dir)
        db.create_table(sample_schema)
        
        tables = db.list_tables()
        assert "test_table" in tables

    def test_database_save_and_load(self, temp_db_dir, sample_schema):
        """Test database persistence."""
        # Create and populate database
        db1 = Database(temp_db_dir)
        db1.create_table(sample_schema)
        table1 = db1.get_table("test_table")
        table1.insert({"id": 1, "name": "Alice", "active": True})
        db1.save_all()
        
        # Load database
        db2 = Database(temp_db_dir)
        assert "test_table" in db2.tables
        table2 = db2.get_table("test_table")
        rows = table2.scan()
        assert len(rows) == 1
        assert rows[0].get("name") == "Alice"

    def test_database_persistence_multiple_operations(self, temp_db_dir, sample_schema):
        """Test persistence across multiple operations."""
        db1 = Database(temp_db_dir)
        db1.create_table(sample_schema)
        table1 = db1.get_table("test_table")
        
        table1.insert({"id": 1, "name": "Alice", "active": True})
        table1.insert({"id": 2, "name": "Bob", "active": False})
        db1.save_all()
        
        # Reload and verify
        db2 = Database(temp_db_dir)
        table2 = db2.get_table("test_table")
        rows = table2.scan()
        
        assert len(rows) == 2
        names = {row.get("name") for row in rows}
        assert "Alice" in names
        assert "Bob" in names

    def test_database_file_creation(self, temp_db_dir, sample_schema):
        """Test that JSON files are created for tables."""
        db = Database(temp_db_dir)
        db.create_table(sample_schema)
        table = db.get_table("test_table")
        table.insert({"id": 1, "name": "Alice", "active": True})
        db.save_all()
        
        table_file = os.path.join(temp_db_dir, "test_table.json")
        assert os.path.exists(table_file)
        
        # Verify file content
        with open(table_file, 'r') as f:
            data = json.load(f)
            assert "schema" in data
            assert "rows" in data
