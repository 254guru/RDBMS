"""
Interactive REPL (Read-Eval-Print Loop) for the RDBMS.
"""

import os
import time
from rdbms.storage import Database
from rdbms.parser import SQLParser, ParseError
from rdbms.engine import ExecutionEngine


class REPL:
    """Interactive command-line interface for the RDBMS."""

    def __init__(self, db_dir: str = "./db"):
        self.db_dir = db_dir
        self.database = Database(db_dir)
        self.engine = ExecutionEngine(self.database)
        self.parser = SQLParser()
        self.running = True

    def run(self):
        """Start the REPL."""
        print("╔════════════════════════════════════════════════════════════════╗")
        print("║  PesaPal RDBMS - Simple Relational Database Management System  ║")
        print("║  Type 'HELP' for commands, 'EXIT' to quit                      ║")
        print("╚════════════════════════════════════════════════════════════════╝\n")

        while self.running:
            try:
                user_input = input("rdbms> ").strip()

                if not user_input:
                    continue

                self._handle_input(user_input)

            except KeyboardInterrupt:
                print("\n\nExiting...")
                self.running = False
            except Exception as e:
                print(f"Error: {e}")

    def _handle_input(self, user_input: str):
        """Handle user input."""
        upper_input = user_input.upper()

        if upper_input == "EXIT" or upper_input == "QUIT":
            self.running = False
            print("Goodbye!")
            return

        if upper_input == "HELP":
            self._print_help()
            return

        if upper_input == "TABLES":
            self._list_tables()
            return

        if upper_input.startswith("SCHEMA "):
            table_name = user_input[7:].strip()
            self._show_schema(table_name)
            return

        if upper_input.startswith("CLEAR"):
            os.system("clear" if os.name == "posix" else "cls")
            return

        # Execute as SQL
        self._execute_sql(user_input)

    def _execute_sql(self, sql: str):
        """Parse and execute SQL."""
        try:
            stmt = self.parser.parse(sql)
            start_time = time.time()
            result = self.engine.execute(stmt)
            elapsed_ms = (time.time() - start_time) * 1000

            if result.success:
                print(f"\n✓ {result.message}")

                if result.data:
                    self._print_results(result.data)

                if result.stats and (result.stats.rows_scanned > 0 or result.stats.index_used):
                    self._print_stats(result.stats, elapsed_ms)
            else:
                print(f"\n✗ {result.message}")

            print()

        except ParseError as e:
            print(f"\n✗ Parse Error: {str(e)}\n")

    def _print_results(self, data: list):
        """Print query results in a table format."""
        if not data:
            return

        # Get column names
        columns = list(data[0].keys())

        # Calculate column widths
        col_widths = {}
        for col in columns:
            max_width = len(str(col))
            for row in data:
                max_width = max(max_width, len(str(row.get(col, ""))))
            col_widths[col] = min(max_width + 2, 30)

        # Print header
        header = " | ".join(
            str(col).ljust(col_widths[col]) for col in columns
        )
        print(f"\n{header}")
        print("-" * len(header))

        # Print rows
        for row in data:
            row_str = " | ".join(
                str(row.get(col, "")).ljust(col_widths[col]) for col in columns
            )
            print(row_str)

    def _print_stats(self, stats, elapsed_ms: float):
        """Print execution statistics."""
        print(f"\nExecution Plan:")
        print(f"  • Rows scanned: {stats.rows_scanned}")
        print(f"  • Rows returned: {stats.rows_returned}")
        if stats.index_used:
            print(f"  • Index used: {stats.index_used}")
        print(f"  • Time: {elapsed_ms:.2f}ms")

    def _list_tables(self):
        """List all tables in the database."""
        tables = self.database.list_tables()
        if not tables:
            print("\nNo tables found.\n")
            return

        print(f"\nTables ({len(tables)}):")
        for table_name in sorted(tables):
            print(f"  • {table_name}")
        print()

    def _show_schema(self, table_name: str):
        """Show the schema of a table."""
        table = self.database.get_table(table_name)
        if not table:
            print(f"\n✗ Table '{table_name}' not found\n")
            return

        print(f"\nSchema for table '{table_name}':")
        print("-" * 60)

        for col in table.schema.columns:
            attrs = []
            if col.primary_key:
                attrs.append("PRIMARY KEY")
            if col.unique:
                attrs.append("UNIQUE")
            if not col.nullable:
                attrs.append("NOT NULL")

            attr_str = f" ({', '.join(attrs)})" if attrs else ""
            print(f"  {col.name}: {col.data_type.value}{attr_str}")

        print()

    def _print_help(self):
        """Print help information."""
        help_text = """
╔═══════════════════════════════════════════════════════════════════════╗
║                          AVAILABLE COMMANDS                           ║
╚═══════════════════════════════════════════════════════════════════════╝

SQL Commands:
  CREATE TABLE name (col1 TYPE, col2 TYPE, ...)
  INSERT INTO name (col1, col2) VALUES (val1, val2)
  SELECT * FROM name [WHERE col = value] [JOIN table ON ...]
  UPDATE name SET col = val [WHERE col = value]
  DELETE FROM name [WHERE col = value]
  DROP TABLE name

Meta Commands:
  TABLES                    - List all tables
  SCHEMA table_name         - Show table schema
  CLEAR                     - Clear screen
  HELP                      - Show this help
  EXIT / QUIT               - Exit the REPL

Data Types:
  INT                       - Integer values
  TEXT                      - Text/string values
  BOOLEAN                   - True/False values

Constraints:
  PRIMARY KEY               - Unique identifier for rows
  UNIQUE                    - Ensure unique values
  NOT NULL                  - Disallow null values

Example Usage:
  CREATE TABLE merchants (id INT PRIMARY KEY, name TEXT, category TEXT)
  INSERT INTO merchants (id, name, category) VALUES (1, 'Alice Store', 'Electronics')
  SELECT * FROM merchants WHERE category = 'Electronics'
  UPDATE merchants SET name = 'New Name' WHERE id = 1
  DELETE FROM merchants WHERE id = 1

"""
        print(help_text)
