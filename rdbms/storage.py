"""
Storage engine for persisting tables to disk and managing indexing.
"""

import json
import os
import logging
from typing import Dict, List, Optional, Set, Tuple, Any
from pathlib import Path
from rdbms.types import Schema, Row, Column, DataType

logger = logging.getLogger(__name__)


class Index:
    """Base index class for efficient lookups."""

    def add(self, key: Any, row_id: int):
        """Add a key-row mapping."""
        raise NotImplementedError

    def remove(self, key: Any, row_id: int):
        """Remove a key-row mapping."""
        raise NotImplementedError

    def lookup(self, key: Any) -> List[int]:
        """Lookup row IDs by key."""
        raise NotImplementedError

    def range_lookup(self, start: Any, end: Any) -> List[int]:
        """Range lookup (for future optimization)."""
        raise NotImplementedError


class HashIndex(Index):
    """Hash-based index for O(1) lookups on primary and unique keys."""

    def __init__(self):
        self.index: Dict[Any, Set[int]] = {}

    def add(self, key: Any, row_id: int):
        """Add a key-row mapping."""
        if key not in self.index:
            self.index[key] = set()
        self.index[key].add(row_id)

    def remove(self, key: Any, row_id: int):
        """Remove a key-row mapping."""
        if key in self.index:
            self.index[key].discard(row_id)
            if not self.index[key]:
                del self.index[key]

    def lookup(self, key: Any) -> List[int]:
        """Lookup row IDs by key."""
        if key in self.index:
            return list(self.index[key])
        return []

    def to_dict(self) -> Dict:
        """Serialize index to dictionary."""
        return {key: list(row_ids) for key, row_ids in self.index.items()}

    @classmethod
    def from_dict(cls, data: Dict) -> "HashIndex":
        """Deserialize index from dictionary."""
        index = cls()
        for key, row_ids in data.items():
            try:
                # Try to convert string keys back to original types
                if key.isdigit():
                    key = int(key)
                elif key.lower() in ("true", "false"):
                    key = key.lower() == "true"
            except (AttributeError, ValueError):
                pass

            for row_id in row_ids:
                index.add(key, row_id)
        return index


class Table:
    """Represents a table in the database."""

    def __init__(self, schema: Schema, storage_dir: str):
        self.schema = schema
        self.storage_dir = storage_dir
        self.rows: List[Row] = []
        self.next_row_id = 0

        # Indexes for primary and unique keys
        self.primary_key_index: Optional[HashIndex] = None
        self.unique_indexes: Dict[str, HashIndex] = {}

        # Setup indexes if needed
        pk_col = schema.get_primary_key_column()
        if pk_col:
            self.primary_key_index = HashIndex()

        for col in schema.columns:
            if col.unique:
                self.unique_indexes[col.name] = HashIndex()

    def insert(self, values: Dict[str, Any]) -> int:
        """
        Insert a row into the table. Returns the row ID.
        Raises ValueError if validation fails or constraints are violated.
        """
        row = Row(values=values, schema=self.schema)

        if not row.validate():
            # Provide detailed validation error message
            missing_columns = []
            for col in self.schema.columns:
                if col.name not in values and not col.nullable:
                    missing_columns.append(f"{col.name} ({col.data_type.value})")
            
            if missing_columns:
                logger.error(f"INSERT into {self.schema.table_name} failed: Missing columns {missing_columns}")
                raise ValueError(
                    f"Missing required column(s): {', '.join(missing_columns)}"
                )
            
            # Check for type mismatches
            for col in self.schema.columns:
                if col.name in values:
                    if not col.validate(values[col.name]):
                        logger.error(f"INSERT into {self.schema.table_name} failed: Type mismatch in column '{col.name}'")
                        raise ValueError(
                            f"Invalid type for column '{col.name}': expected {col.data_type.value}, got {type(values[col.name]).__name__}"
                        )

        # Check primary key constraint
        pk_col = self.schema.get_primary_key_column()
        if pk_col and pk_col.name in values:
            pk_value = values[pk_col.name]
            existing = self.primary_key_index.lookup(pk_value)
            if existing:
                logger.warning(f"INSERT into {self.schema.table_name} failed: Duplicate primary key {pk_col.name}={pk_value}")
                raise ValueError(
                    f"Primary key {pk_col.name}={pk_value} already exists"
                )

        # Check unique constraints
        for col_name, index in self.unique_indexes.items():
            if col_name in values:
                value = values[col_name]
                existing = index.lookup(value)
                if existing:
                    logger.warning(f"INSERT into {self.schema.table_name} failed: Unique constraint violation on {col_name}={value}")
                    raise ValueError(f"Unique constraint violated on {col_name}")

        # Add row
        row_id = self.next_row_id
        self.next_row_id += 1
        self.rows.append(row)

        # Update indexes
        if pk_col and pk_col.name in values:
            self.primary_key_index.add(values[pk_col.name], row_id)

        for col_name, index in self.unique_indexes.items():
            if col_name in values:
                index.add(values[col_name], row_id)

        return row_id

    def get_by_primary_key(self, key: Any) -> Optional[Row]:
        """Get a row by primary key."""
        if not self.primary_key_index:
            return None

        row_ids = self.primary_key_index.lookup(key)
        if row_ids:
            return self.rows[row_ids[0]]
        return None

    def scan(self) -> List[Row]:
        """Scan all rows (full table scan)."""
        return self.rows.copy()

    def filter(self, column_name: str, operator: str, value: Any) -> List[Row]:
        """Filter rows by column condition."""
        result = []
        for row in self.rows:
            row_value = row.get(column_name)
            if self._evaluate_condition(row_value, operator, value):
                result.append(row)
        return result

    def _evaluate_condition(self, row_value: Any, operator: str, value: Any) -> bool:
        """Evaluate a condition."""
        if operator == "=":
            return row_value == value
        elif operator == "!=":
            return row_value != value
        elif operator == "<":
            return row_value < value
        elif operator == ">":
            return row_value > value
        elif operator == "<=":
            return row_value <= value
        elif operator == ">=":
            return row_value >= value
        return False

    def update(self, row_index: int, updates: Dict[str, Any]):
        """Update a row."""
        if row_index < 0 or row_index >= len(self.rows):
            raise ValueError("Row not found")

        row = self.rows[row_index]
        old_values = row.values.copy()

        # Update values
        for key, value in updates.items():
            col = self.schema.get_column(key)
            if not col:
                raise ValueError(f"Column {key} not found")
            if not col.validate(value):
                raise ValueError(f"Invalid value for column {key}")

            row.values[key] = value

        # Update indexes
        pk_col = self.schema.get_primary_key_column()
        if pk_col and pk_col.name in updates:
            old_pk = old_values.get(pk_col.name)
            new_pk = updates[pk_col.name]
            if old_pk != new_pk:
                self.primary_key_index.remove(old_pk, row_index)
                self.primary_key_index.add(new_pk, row_index)

        for col_name, index in self.unique_indexes.items():
            if col_name in updates:
                old_val = old_values.get(col_name)
                new_val = updates[col_name]
                if old_val != new_val:
                    index.remove(old_val, row_index)
                    index.add(new_val, row_index)

    def delete(self, row_index: int):
        """Delete a row."""
        if row_index < 0 or row_index >= len(self.rows):
            raise ValueError("Row not found")

        row = self.rows[row_index]

        # Remove from indexes
        pk_col = self.schema.get_primary_key_column()
        if pk_col:
            pk_value = row.get(pk_col.name)
            self.primary_key_index.remove(pk_value, row_index)

        for col_name, index in self.unique_indexes.items():
            value = row.get(col_name)
            index.remove(value, row_index)

        # Mark as deleted by removing from list
        del self.rows[row_index]

    def save(self):
        """Save table to disk."""
        table_file = Path(self.storage_dir) / f"{self.schema.table_name}.json"
        data = {
            "schema": self.schema.to_dict(),
            "rows": [row.to_dict() for row in self.rows],
            "next_row_id": self.next_row_id,
        }
        with open(table_file, "w") as f:
            json.dump(data, f, indent=2, default=str)

    @classmethod
    def load(cls, storage_dir: str, table_name: str) -> "Table":
        """Load table from disk."""
        table_file = Path(storage_dir) / f"{table_name}.json"
        if not table_file.exists():
            raise FileNotFoundError(f"Table file not found: {table_file}")

        with open(table_file, "r") as f:
            data = json.load(f)

        schema = Schema.from_dict(data["schema"])
        table = cls(schema, storage_dir)
        table.next_row_id = data.get("next_row_id", 0)

        for row_data in data["rows"]:
            table.rows.append(Row(values=row_data, schema=schema))

        # Rebuild indexes
        pk_col = schema.get_primary_key_column()
        for i, row in enumerate(table.rows):
            if pk_col:
                pk_value = row.get(pk_col.name)
                if pk_value is not None:
                    table.primary_key_index.add(pk_value, i)

            for col_name in table.unique_indexes:
                value = row.get(col_name)
                if value is not None:
                    table.unique_indexes[col_name].add(value, i)

        return table


class Database:
    """Represents a database containing multiple tables."""

    def __init__(self, db_dir: str):
        self.db_dir = db_dir
        Path(db_dir).mkdir(parents=True, exist_ok=True)
        self.tables: Dict[str, Table] = {}
        self._load_existing_tables()

    def _load_existing_tables(self):
        """Load existing tables from disk."""
        db_path = Path(self.db_dir)
        for table_file in db_path.glob("*.json"):
            table_name = table_file.stem
            try:
                self.tables[table_name] = Table.load(self.db_dir, table_name)
            except Exception as e:
                print(f"Warning: Could not load table {table_name}: {e}")

    def create_table(self, schema: Schema) -> Table:
        """Create a new table."""
        if schema.table_name in self.tables:
            raise ValueError(f"Table {schema.table_name} already exists")

        table = Table(schema, self.db_dir)
        self.tables[schema.table_name] = table
        table.save()
        return table

    def get_table(self, table_name: str) -> Optional[Table]:
        """Get a table by name."""
        return self.tables.get(table_name)

    def list_tables(self) -> List[str]:
        """List all table names."""
        return list(self.tables.keys())

    def save_all(self):
        """Save all tables to disk."""
        for table in self.tables.values():
            table.save()
