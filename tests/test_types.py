"""Unit tests for rdbms.types module."""

import pytest
from rdbms.types import DataType, Column, Schema, Row


class TestDataType:
    """Tests for DataType enum."""

    def test_data_types_exist(self):
        """Test that all required data types exist."""
        assert DataType.INT.value == "INT"
        assert DataType.TEXT.value == "TEXT"
        assert DataType.BOOLEAN.value == "BOOLEAN"

    def test_data_type_equality(self):
        """Test data type comparisons."""
        assert DataType.INT == DataType.INT
        assert DataType.TEXT != DataType.INT


class TestColumn:
    """Tests for Column class."""

    def test_column_creation_basic(self):
        """Test basic column creation."""
        col = Column(name="id", data_type=DataType.INT)
        assert col.name == "id"
        assert col.data_type == DataType.INT
        assert col.primary_key is False
        assert col.unique is False
        assert col.nullable is True

    def test_column_creation_with_constraints(self):
        """Test column creation with constraints."""
        col = Column(
            name="id",
            data_type=DataType.INT,
            primary_key=True,
            nullable=False
        )
        assert col.primary_key is True
        assert col.nullable is False

    def test_column_validate_int(self):
        """Test INT validation."""
        col = Column(name="age", data_type=DataType.INT)
        
        assert col.validate(42) is True
        assert col.validate(0) is True
        assert col.validate(-100) is True
        assert col.validate("42") is False
        assert col.validate(3.14) is False
        assert col.validate(None) is True  # nullable=True by default

    def test_column_validate_int_not_nullable(self):
        """Test INT validation when not nullable."""
        col = Column(name="age", data_type=DataType.INT, nullable=False)
        
        assert col.validate(42) is True
        assert col.validate(None) is False

    def test_column_validate_text(self):
        """Test TEXT validation."""
        col = Column(name="name", data_type=DataType.TEXT)
        
        assert col.validate("Alice") is True
        assert col.validate("") is True
        assert col.validate(42) is False
        assert col.validate(None) is True

    def test_column_validate_boolean(self):
        """Test BOOLEAN validation."""
        col = Column(name="active", data_type=DataType.BOOLEAN)
        
        assert col.validate(True) is True
        assert col.validate(False) is True
        assert col.validate("true") is False
        assert col.validate(1) is False
        assert col.validate(None) is True

    def test_column_cast_int(self):
        """Test INT casting."""
        col = Column(name="age", data_type=DataType.INT)
        
        assert col.cast(42) == 42
        assert col.cast("42") == 42
        assert col.cast(None) is None

    def test_column_cast_text(self):
        """Test TEXT casting."""
        col = Column(name="name", data_type=DataType.TEXT)
        
        assert col.cast("Alice") == "Alice"
        assert col.cast(42) == "42"
        assert col.cast(None) is None

    def test_column_cast_boolean(self):
        """Test BOOLEAN casting."""
        col = Column(name="active", data_type=DataType.BOOLEAN)
        
        assert col.cast(True) is True
        assert col.cast(False) is False
        assert col.cast(1) is True
        assert col.cast(0) is False
        assert col.cast("true") is True
        assert col.cast(None) is None


class TestSchema:
    """Tests for Schema class."""

    def test_schema_creation(self, sample_schema):
        """Test schema creation."""
        assert sample_schema.table_name == "test_table"
        assert len(sample_schema.columns) == 3
        assert sample_schema.columns[0].name == "id"

    def test_get_primary_key_column(self, sample_schema):
        """Test retrieving primary key column."""
        pk_col = sample_schema.get_primary_key_column()
        assert pk_col is not None
        assert pk_col.name == "id"
        assert pk_col.primary_key is True

    def test_get_primary_key_column_none(self):
        """Test getting primary key when none exists."""
        schema = Schema(
            table_name="test",
            columns=[
                Column(name="name", data_type=DataType.TEXT),
            ]
        )
        assert schema.get_primary_key_column() is None

    def test_get_column_by_name(self, sample_schema):
        """Test retrieving column by name."""
        col = sample_schema.get_column("name")
        assert col is not None
        assert col.name == "name"
        assert col.unique is True

    def test_get_column_by_name_not_found(self, sample_schema):
        """Test retrieving non-existent column."""
        col = sample_schema.get_column("nonexistent")
        assert col is None

    def test_schema_serialization(self, sample_schema):
        """Test schema serialization to dict."""
        schema_dict = sample_schema.to_dict()
        assert schema_dict["table_name"] == "test_table"
        assert len(schema_dict["columns"]) == 3
        assert schema_dict["columns"][0]["primary_key"] is True

    def test_schema_deserialization(self):
        """Test schema deserialization from dict."""
        schema_dict = {
            "table_name": "test_table",
            "columns": [
                {"name": "id", "data_type": "INT", "primary_key": True, "unique": False, "nullable": False},
                {"name": "name", "data_type": "TEXT", "primary_key": False, "unique": True, "nullable": False},
            ]
        }
        schema = Schema.from_dict(schema_dict)
        assert schema.table_name == "test_table"
        assert len(schema.columns) == 2
        assert schema.get_primary_key_column().name == "id"

    def test_schema_column_lookup(self, sample_schema):
        """Test looking up columns in schema."""
        col = sample_schema.get_column("active")
        assert col is not None
        assert col.nullable is True
        
        col_none = sample_schema.get_column("nonexistent")
        assert col_none is None


class TestRow:
    """Tests for Row class."""

    def test_row_creation(self, sample_schema):
        """Test row creation."""
        row = Row(values={"id": 1, "name": "Alice", "active": True}, schema=sample_schema)
        assert row.values["id"] == 1
        assert row.values["name"] == "Alice"

    def test_row_get(self, sample_schema):
        """Test row data access."""
        row = Row(values={"id": 1, "name": "Alice", "active": True}, schema=sample_schema)
        assert row.get("id") == 1
        assert row.get("name") == "Alice"
        assert row.get("nonexistent") is None

    def test_row_validate(self, sample_schema):
        """Test row validation against schema."""
        # Valid row
        row1 = Row(values={"id": 1, "name": "Alice", "active": True}, schema=sample_schema)
        assert row1.validate() is True
        
        # Invalid row - missing required field
        row2 = Row(values={"id": 1, "active": True}, schema=sample_schema)
        assert row2.validate() is False

    def test_row_to_dict(self, sample_schema):
        """Test row conversion to dictionary."""
        row = Row(values={"id": 1, "name": "Alice", "active": True}, schema=sample_schema)
        result = row.to_dict()
        assert result == {"id": 1, "name": "Alice", "active": True}

    def test_row_without_schema(self):
        """Test row without schema."""
        row = Row(values={"id": 1, "name": "Alice"})
        assert row.validate() is True  # No schema, so validation passes
        assert row.get("name") == "Alice"
