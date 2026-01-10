"""
Data types and schema definitions for the RDBMS.
"""

from enum import Enum
from typing import Any, List, Optional, Dict
from dataclasses import dataclass, field, asdict
import json


class DataType(Enum):
    """Supported data types in the RDBMS."""
    INT = "INT"
    TEXT = "TEXT"
    BOOLEAN = "BOOLEAN"


@dataclass
class Column:
    """Represents a column in a table schema."""
    name: str
    data_type: DataType
    primary_key: bool = False
    unique: bool = False
    nullable: bool = True

    def validate(self, value: Any) -> bool:
        """Validate a value against this column's type."""
        if value is None and self.nullable:
            return True
        if value is None:
            return False

        if self.data_type == DataType.INT:
            return isinstance(value, int)
        elif self.data_type == DataType.TEXT:
            return isinstance(value, str)
        elif self.data_type == DataType.BOOLEAN:
            return isinstance(value, bool)

        return False

    def cast(self, value: Any) -> Any:
        """Cast a value to this column's type."""
        if value is None:
            return None

        if self.data_type == DataType.INT:
            return int(value)
        elif self.data_type == DataType.TEXT:
            return str(value)
        elif self.data_type == DataType.BOOLEAN:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ("true", "1", "yes")
            return bool(value)

        return value


@dataclass
class Schema:
    """Represents the schema of a table."""
    table_name: str
    columns: List[Column] = field(default_factory=list)

    def get_column(self, name: str) -> Optional[Column]:
        """Get a column by name."""
        for col in self.columns:
            if col.name == name:
                return col
        return None

    def get_primary_key_column(self) -> Optional[Column]:
        """Get the primary key column if exists."""
        for col in self.columns:
            if col.primary_key:
                return col
        return None

    def to_dict(self) -> Dict:
        """Convert schema to dictionary for serialization."""
        return {
            "table_name": self.table_name,
            "columns": [
                {
                    "name": col.name,
                    "data_type": col.data_type.value,
                    "primary_key": col.primary_key,
                    "unique": col.unique,
                    "nullable": col.nullable,
                }
                for col in self.columns
            ],
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Schema":
        """Create schema from dictionary."""
        columns = [
            Column(
                name=col["name"],
                data_type=DataType[col["data_type"]],
                primary_key=col.get("primary_key", False),
                unique=col.get("unique", False),
                nullable=col.get("nullable", True),
            )
            for col in data["columns"]
        ]
        return cls(table_name=data["table_name"], columns=columns)


@dataclass
class Row:
    """Represents a row in a table."""
    values: Dict[str, Any]
    schema: Schema = field(default=None)

    def get(self, column_name: str) -> Any:
        """Get a value by column name."""
        return self.values.get(column_name)

    def validate(self) -> bool:
        """Validate row against schema."""
        if not self.schema:
            return True

        for col in self.schema.columns:
            if col.name not in self.values:
                if not col.nullable:
                    return False
            else:
                if not col.validate(self.values[col.name]):
                    return False

        return True

    def to_dict(self) -> Dict:
        """Convert row to dictionary."""
        return self.values.copy()
