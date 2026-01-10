"""
Execution engine for executing parsed SQL statements.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from rdbms.parser import (
    CreateTableStmt,
    InsertStmt,
    SelectStmt,
    UpdateStmt,
    DeleteStmt,
    DropTableStmt,
    ExplainStmt,
)
from rdbms.storage import Database, Table
from rdbms.types import Schema, Column


@dataclass
class ExecutionStats:
    """Statistics about query execution."""
    rows_scanned: int = 0
    rows_returned: int = 0
    index_used: Optional[str] = None
    execution_time_ms: float = 0.0


@dataclass
class QueryResult:
    """Result of query execution."""
    success: bool
    data: List[Dict[str, Any]] = None
    message: str = ""
    stats: ExecutionStats = None

    def __post_init__(self):
        if self.data is None:
            self.data = []
        if self.stats is None:
            self.stats = ExecutionStats()


class ExecutionEngine:
    """Executes parsed SQL statements."""

    def __init__(self, database: Database):
        self.database = database
        self.last_stats = ExecutionStats()

    def execute(self, stmt) -> QueryResult:
        """Execute a statement."""
        try:
            if isinstance(stmt, CreateTableStmt):
                return self._execute_create_table(stmt)
            elif isinstance(stmt, InsertStmt):
                return self._execute_insert(stmt)
            elif isinstance(stmt, SelectStmt):
                return self._execute_select(stmt)
            elif isinstance(stmt, UpdateStmt):
                return self._execute_update(stmt)
            elif isinstance(stmt, DeleteStmt):
                return self._execute_delete(stmt)
            elif isinstance(stmt, DropTableStmt):
                return self._execute_drop_table(stmt)
            elif isinstance(stmt, ExplainStmt):
                return self._execute_explain(stmt)
            else:
                return QueryResult(success=False, message="Unknown statement type")
        except Exception as e:
            return QueryResult(success=False, message=f"Error: {str(e)}")

    def _execute_create_table(self, stmt: CreateTableStmt) -> QueryResult:
        """Execute CREATE TABLE."""
        try:
            schema = Schema(table_name=stmt.table_name, columns=stmt.columns)
            self.database.create_table(schema)
            return QueryResult(
                success=True,
                message=f"Table {stmt.table_name} created successfully",
            )
        except Exception as e:
            return QueryResult(success=False, message=str(e))

    def _execute_insert(self, stmt: InsertStmt) -> QueryResult:
        """Execute INSERT."""
        table = self.database.get_table(stmt.table_name)
        if not table:
            return QueryResult(
                success=False, message=f"Table {stmt.table_name} not found"
            )

        try:
            values = {col: val for col, val in zip(stmt.columns, stmt.values)}
            row_id = table.insert(values)
            self.database.save_all()
            return QueryResult(
                success=True, message=f"1 row inserted (ID: {row_id})"
            )
        except Exception as e:
            return QueryResult(success=False, message=str(e))

    def _execute_select(self, stmt: SelectStmt) -> QueryResult:
        """Execute SELECT."""
        table = self.database.get_table(stmt.table_name)
        if not table:
            return QueryResult(
                success=False, message=f"Table {stmt.table_name} not found"
            )

        stats = ExecutionStats()
        rows = []

        # Step 1: Get rows from main table
        if stmt.where_clause:
            col_name, operator, value = stmt.where_clause
            rows = table.filter(col_name, operator, value)
            stats.rows_scanned = len(table.rows)
        else:
            rows = table.scan()
            stats.rows_scanned = len(rows)

        # Step 2: Handle JOIN if present
        if stmt.join_table:
            rows = self._execute_join(table, rows, stmt, stats)

        # Step 3: Select specific columns
        stats.rows_returned = len(rows)
        result_data = []

        for row in rows:
            if stmt.columns:
                # Select specific columns
                row_dict = {}
                for col in stmt.columns:
                    if "." in col:
                        # Handle table-qualified columns (from JOIN)
                        row_dict[col] = row.get(col)
                    else:
                        row_dict[col] = row.get(col)
            else:
                # Select all columns
                row_dict = row.to_dict()

            result_data.append(row_dict)

        self.last_stats = stats
        return QueryResult(
            success=True,
            data=result_data,
            message=f"Query returned {len(result_data)} row(s)",
            stats=stats,
        )

    def _execute_join(
        self,
        left_table: Table,
        left_rows: List,
        stmt: SelectStmt,
        stats: ExecutionStats,
    ) -> List:
        """Execute a JOIN (Nested Loop Join)."""
        right_table = self.database.get_table(stmt.join_table)
        if not right_table:
            raise ValueError(f"Table {stmt.join_table} not found")

        right_rows = right_table.scan()
        result = []

        # Parse join condition
        left_col_full, right_col_full = stmt.join_on
        left_table_name, left_col = left_col_full.split(".")
        right_table_name, right_col = right_col_full.split(".")

        # Nested loop join
        for left_row in left_rows:
            for right_row in right_rows:
                left_val = left_row.get(left_col)
                right_val = right_row.get(right_col)

                if left_val == right_val:
                    # Merge rows
                    merged = {}
                    for k, v in left_row.to_dict().items():
                        merged[f"{left_table_name}.{k}"] = v
                    for k, v in right_row.to_dict().items():
                        merged[f"{right_table_name}.{k}"] = v

                    # Create a wrapper object that supports both qualified and unqualified column access
                    result.append(_JoinedRow(merged, left_table_name, right_table_name))

        stats.rows_scanned += len(right_rows)
        return result

    def _execute_update(self, stmt: UpdateStmt) -> QueryResult:
        """Execute UPDATE."""
        table = self.database.get_table(stmt.table_name)
        if not table:
            return QueryResult(
                success=False, message=f"Table {stmt.table_name} not found"
            )

        try:
            updated = 0
            if stmt.where_clause:
                col_name, operator, value = stmt.where_clause
                # Collect indices of rows to update (iterate in reverse to handle deletion safely)
                indices_to_update = []
                for i, row in enumerate(table.rows):
                    row_value = row.get(col_name)
                    if table._evaluate_condition(row_value, operator, value):
                        indices_to_update.append(i)
                
                # Update in reverse order to maintain consistency
                for i in reversed(indices_to_update):
                    table.update(i, stmt.updates)
                    updated += 1
            else:
                for i in range(len(table.rows)):
                    table.update(i, stmt.updates)
                    updated += 1

            self.database.save_all()
            return QueryResult(
                success=True, message=f"{updated} row(s) updated"
            )
        except Exception as e:
            return QueryResult(success=False, message=str(e))

    def _execute_delete(self, stmt: DeleteStmt) -> QueryResult:
        """Execute DELETE."""
        table = self.database.get_table(stmt.table_name)
        if not table:
            return QueryResult(
                success=False, message=f"Table {stmt.table_name} not found"
            )

        try:
            deleted = 0
            if stmt.where_clause:
                col_name, operator, value = stmt.where_clause
                rows_to_delete = table.filter(col_name, operator, value)
                # Delete in reverse order to avoid index issues
                for i in range(len(table.rows) - 1, -1, -1):
                    if table.rows[i] in rows_to_delete:
                        table.delete(i)
                        deleted += 1
            else:
                # Delete all
                deleted = len(table.rows)
                table.rows.clear()

            self.database.save_all()
            return QueryResult(
                success=True, message=f"{deleted} row(s) deleted"
            )
        except Exception as e:
            return QueryResult(success=False, message=str(e))

    def _execute_drop_table(self, stmt: DropTableStmt) -> QueryResult:
        """Execute DROP TABLE."""
        table_name = stmt.table_name
        if table_name not in self.database.tables:
            return QueryResult(
                success=False, message=f"Table {table_name} not found"
            )

        try:
            import os
            from pathlib import Path

            del self.database.tables[table_name]
            table_file = Path(self.database.db_dir) / f"{table_name}.json"
            if table_file.exists():
                os.remove(table_file)

            return QueryResult(
                success=True, message=f"Table {table_name} dropped successfully"
            )
        except Exception as e:
            return QueryResult(success=False, message=str(e))

    def _execute_explain(self, stmt: ExplainStmt) -> QueryResult:
        """Execute EXPLAIN (for performance analysis)."""
        # This would parse and show execution plan
        return QueryResult(
            success=True,
            message=f"EXPLAIN: Analysis of query '{stmt.query}' would be shown here",
        )


class _JoinedRow:
    """Helper class for joined rows that supports both qualified and unqualified column access."""

    def __init__(self, data: Dict, left_table: str, right_table: str):
        self.data = data
        self.left_table = left_table
        self.right_table = right_table

    def get(self, col_name: str) -> Any:
        """Get a value, supporting both qualified and unqualified names."""
        if col_name in self.data:
            return self.data[col_name]

        # Try qualified names
        qualified_left = f"{self.left_table}.{col_name}"
        qualified_right = f"{self.right_table}.{col_name}"

        if qualified_left in self.data:
            return self.data[qualified_left]
        if qualified_right in self.data:
            return self.data[qualified_right]

        return None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return self.data.copy()
