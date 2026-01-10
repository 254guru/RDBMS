#!/usr/bin/env python3
"""
Example usage of the PesaPal RDBMS.
Demonstrates all major features with a sample merchant management system.
"""

from rdbms.storage import Database
from rdbms.parser import SQLParser
from rdbms.engine import ExecutionEngine


def print_header(title):
    """Print a section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def execute_query(engine, parser, sql, description=""):
    """Execute a query and print results."""
    if description:
        print(f"▶ {description}")
    print(f"SQL: {sql}")

    try:
        stmt = parser.parse(sql)
        result = engine.execute(stmt)

        if result.success:
            print(f"✓ {result.message}")
            if result.data:
                print("\nResults:")
                for row in result.data:
                    for key, value in row.items():
                        print(f"  {key}: {value}")
                    print()

            if result.stats:
                print(f"Statistics:")
                print(f"  Rows scanned: {result.stats.rows_scanned}")
                print(f"  Rows returned: {result.stats.rows_returned}")
        else:
            print(f"✗ {result.message}")

    except Exception as e:
        print(f"✗ Error: {e}")

    print()


def main():
    """Run example queries."""

    # Initialize database
    db = Database("./example_db")
    engine = ExecutionEngine(db)
    parser = SQLParser()

    print("\n")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║  PesaPal RDBMS - Example Demonstration                         ║")
    print("╚════════════════════════════════════════════════════════════════╝")

    # ==================== TABLE CREATION ====================
    print_header("1. CREATE TABLES")

    execute_query(
        engine,
        parser,
        "CREATE TABLE merchants (id INT PRIMARY KEY, name TEXT UNIQUE, category TEXT, active BOOLEAN)",
        "Create merchants table with primary key and unique constraint",
    )

    execute_query(
        engine,
        parser,
        "CREATE TABLE transactions (id INT PRIMARY KEY, merchant_id INT, amount INT)",
        "Create transactions table with foreign key relationship",
    )

    # ==================== INSERT DATA ====================
    print_header("2. INSERT DATA")

    merchants = [
        ("1", "'Alice Electronics'", "'Electronics'", "true"),
        ("2", "'Bob Groceries'", "'Groceries'", "true"),
        ("3", "'Charlie Fashion'", "'Fashion'", "true"),
        ("4", "'Diana Services'", "'Services'", "false"),
    ]

    for mid, name, category, active in merchants:
        sql = f"INSERT INTO merchants (id, name, category, active) VALUES ({mid}, {name}, {category}, {active})"
        execute_query(engine, parser, sql)

    transactions = [
        ("1", "1", "5000"),
        ("2", "1", "3000"),
        ("3", "2", "2000"),
        ("4", "3", "1500"),
        ("5", "1", "2500"),
    ]

    for tid, mid, amount in transactions:
        sql = f"INSERT INTO transactions (id, merchant_id, amount) VALUES ({tid}, {mid}, {amount})"
        execute_query(engine, parser, sql)

    # ==================== BASIC QUERIES ====================
    print_header("3. BASIC QUERIES")

    execute_query(
        engine,
        parser,
        "SELECT * FROM merchants",
        "Select all merchants",
    )

    execute_query(
        engine,
        parser,
        "SELECT * FROM merchants WHERE category = 'Electronics'",
        "Filter merchants by category",
    )

    execute_query(
        engine,
        parser,
        "SELECT * FROM merchants WHERE active = true",
        "Filter active merchants only",
    )

    # ==================== UPDATE OPERATIONS ====================
    print_header("4. UPDATE OPERATIONS")

    execute_query(
        engine,
        parser,
        "UPDATE merchants SET active = false WHERE id = 1",
        "Deactivate a merchant",
    )

    execute_query(
        engine,
        parser,
        "SELECT * FROM merchants WHERE id = 1",
        "Verify the update",
    )

    # ==================== JOIN OPERATIONS ====================
    print_header("5. JOIN OPERATIONS (Nested Loop Join)")

    execute_query(
        engine,
        parser,
        "SELECT * FROM merchants JOIN transactions ON merchants.id = transactions.merchant_id",
        "Join merchants with their transactions",
    )

    execute_query(
        engine,
        parser,
        "SELECT * FROM merchants JOIN transactions ON merchants.id = transactions.merchant_id WHERE merchants.category = 'Electronics'",
        "Join with WHERE clause to filter results",
    )

    # ==================== DELETE OPERATIONS ====================
    print_header("6. DELETE OPERATIONS")

    execute_query(
        engine,
        parser,
        "DELETE FROM transactions WHERE id = 1",
        "Delete a specific transaction",
    )

    execute_query(
        engine,
        parser,
        "SELECT * FROM transactions",
        "Verify deletion",
    )

    # ==================== SCHEMA INSPECTION ====================
    print_header("7. DATABASE INTROSPECTION")

    # List tables
    tables = db.list_tables()
    print(f"Tables in database: {', '.join(tables)}\n")

    # Show schema
    for table_name in tables:
        table = db.get_table(table_name)
        print(f"Schema for '{table_name}':")
        for col in table.schema.columns:
            attrs = []
            if col.primary_key:
                attrs.append("PRIMARY KEY")
            if col.unique:
                attrs.append("UNIQUE")
            if not col.nullable:
                attrs.append("NOT NULL")

            attr_str = f" [{', '.join(attrs)}]" if attrs else ""
            print(f"  - {col.name}: {col.data_type.value}{attr_str}")
        print()

    # ==================== PERFORMANCE DEMO ====================
    print_header("8. PERFORMANCE FEATURES")

    print("Primary Key Index Demo:")
    print("- Looking up merchant by primary key (O(1) operation)")
    merchant = db.get_table("merchants").get_by_primary_key(2)
    if merchant:
        print(f"  Found: {merchant.to_dict()}\n")

    # ==================== SUMMARY ====================
    print_header("EXAMPLE COMPLETED")
    print("This demonstration showed:")
    print("  ✓ Table creation with constraints")
    print("  ✓ CRUD operations (Create, Read, Update, Delete)")
    print("  ✓ WHERE clause filtering")
    print("  ✓ JOIN operations between tables")
    print("  ✓ Database introspection")
    print("  ✓ Indexing and primary key lookups\n")

    print("For interactive use, run: python main.py")
    print("For web interface, run: cd web_app && python app.py\n")


if __name__ == "__main__":
    main()
