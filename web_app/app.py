"""
Web application demonstrating the RDBMS with a Merchant Directory.
"""

from flask import Flask, render_template, request, jsonify
import os
import sys
import logging
from pathlib import Path

# Add parent directory to path to import rdbms
sys.path.insert(0, str(Path(__file__).parent.parent))

from rdbms.storage import Database
from rdbms.parser import SQLParser, ParseError
from rdbms.engine import ExecutionEngine
from rdbms.types import Schema, Column, DataType
from rdbms.security import InputValidator, SQLInjectionDetector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize database
DB_DIR = os.environ.get("RDBMS_DB_DIR", "./db")
try:
    database = Database(DB_DIR)
    engine = ExecutionEngine(database)
    parser = SQLParser()
    logger.info(f"Database initialized at {DB_DIR}")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    raise


def init_database():
    """Initialize the database with tables if they don't exist."""
    try:
        # Create merchants table if it doesn't exist
        if "merchants" not in database.tables:
            merchants_schema = Schema(
                table_name="merchants",
                columns=[
                    Column(name="id", data_type=DataType.INT, primary_key=True, nullable=False),
                    Column(name="name", data_type=DataType.TEXT, unique=True, nullable=False),
                    Column(name="category", data_type=DataType.TEXT, nullable=False),
                    Column(name="active", data_type=DataType.BOOLEAN, nullable=False),
                ]
            )
            database.create_table(merchants_schema)
            logger.info("Created merchants table")
        
        # Create categories table if it doesn't exist
        if "categories" not in database.tables:
            categories_schema = Schema(
                table_name="categories",
                columns=[
                    Column(name="id", data_type=DataType.INT, primary_key=True, nullable=False),
                    Column(name="name", data_type=DataType.TEXT, unique=True, nullable=False),
                    Column(name="description", data_type=DataType.TEXT, nullable=True),
                ]
            )
            database.create_table(categories_schema)
            logger.info("Created categories table")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


init_database()


@app.route("/")
def index():
    """Home page - list all merchants."""
    merchants = []
    categories = []
    
    try:
        merchants_table = database.get_table("merchants")
        if merchants_table:
            merchants = [row.to_dict() for row in merchants_table.scan()]
    except Exception as e:
        logger.error(f"Error retrieving merchants: {e}")
    
    try:
        categories_table = database.get_table("categories")
        if categories_table:
            categories = [row.to_dict() for row in categories_table.scan()]
    except Exception as e:
        logger.error(f"Error retrieving categories: {e}")
    
    return render_template("index.html", merchants=merchants, categories=categories)


def validate_merchant_input(data):
    """Validate merchant input data using security validators."""
    errors = []
    
    if not data:
        errors.append("Request data is required")
        return errors
    
    # Validate ID
    if "id" not in data:
        errors.append("'id' field is required")
    else:
        is_valid, error = InputValidator.validate_integer(data.get("id"), "id")
        if not is_valid:
            errors.append(error)
    
    # Validate name
    if "name" not in data:
        errors.append("'name' field is required")
    else:
        is_valid, error = InputValidator.validate_string(data.get("name"), "name", min_length=1, max_length=255)
        if not is_valid:
            errors.append(error)
    
    # Validate category
    if "category" not in data:
        errors.append("'category' field is required")
    else:
        is_valid, error = InputValidator.validate_string(data.get("category"), "category", min_length=1, max_length=255)
        if not is_valid:
            errors.append(error)
    
    return errors


@app.route("/api/merchants", methods=["GET", "POST"])
def merchants_api():
    """API endpoint for merchants."""
    if request.method == "POST":
        try:
            data = request.get_json()
            
            # Validate input
            validation_errors = validate_merchant_input(data)
            if validation_errors:
                logger.warning(f"Invalid merchant input: {validation_errors}")
                return jsonify({"error": "Invalid input", "details": validation_errors}), 400
            
            merchants_table = database.get_table("merchants")
            if not merchants_table:
                logger.error("Merchants table not found")
                return jsonify({"error": "Merchants table not found"}), 500
            
            # Check if ID already exists
            merchant_id = int(data.get("id"))
            existing = merchants_table.get_by_primary_key(merchant_id)
            if existing:
                logger.warning(f"Attempt to insert duplicate merchant ID: {merchant_id}")
                return jsonify({"error": "Merchant ID already exists"}), 400
            
            # Insert merchant
            merchants_table.insert({
                "id": merchant_id,
                "name": data.get("name").strip(),
                "category": data.get("category").strip(),
                "active": data.get("active", True) == "true" or data.get("active") is True,
            })
            
            database.save_all()
            logger.info(f"Merchant added successfully: id={merchant_id}, name={data.get('name')}")
            return jsonify({"success": True, "message": "Merchant added successfully"}), 201
        
        except ValueError as e:
            logger.error(f"Validation error while adding merchant: {e}")
            return jsonify({"error": f"Validation error: {str(e)}"}), 400
        except Exception as e:
            logger.error(f"Unexpected error while adding merchant: {e}", exc_info=True)
            return jsonify({"error": "An unexpected error occurred"}), 500
    
    else:  # GET
        try:
            merchants_table = database.get_table("merchants")
            if not merchants_table:
                return jsonify([])
            merchants = [row.to_dict() for row in merchants_table.scan()]
            return jsonify(merchants)
        except Exception as e:
            logger.error(f"Error retrieving merchants: {e}", exc_info=True)
            return jsonify({"error": "Error retrieving merchants"}), 500


@app.route("/api/merchants/<int:merchant_id>", methods=["GET", "PUT", "DELETE"])
def merchant_detail(merchant_id):
    """API endpoint for individual merchant."""
    try:
        merchants_table = database.get_table("merchants")
        if not merchants_table:
            logger.error("Merchants table not found")
            return jsonify({"error": "Merchants table not found"}), 500
        
        if request.method == "GET":
            merchant = merchants_table.get_by_primary_key(merchant_id)
            if merchant:
                return jsonify(merchant.to_dict())
            logger.warning(f"Merchant not found: id={merchant_id}")
            return jsonify({"error": "Merchant not found"}), 404
        
        elif request.method == "PUT":
            try:
                data = request.get_json()
                merchant = merchants_table.get_by_primary_key(merchant_id)
                
                if not merchant:
                    logger.warning(f"Attempt to update non-existent merchant: id={merchant_id}")
                    return jsonify({"error": "Merchant not found"}), 404
                
                # Find the row index
                for i, row in enumerate(merchants_table.rows):
                    if row.get("id") == merchant_id:
                        updates = {}
                        if "name" in data:
                            if not isinstance(data["name"], str) or not data["name"].strip():
                                return jsonify({"error": "'name' must be a non-empty string"}), 400
                            updates["name"] = data["name"].strip()
                        if "category" in data:
                            if not isinstance(data["category"], str) or not data["category"].strip():
                                return jsonify({"error": "'category' must be a non-empty string"}), 400
                            updates["category"] = data["category"].strip()
                        if "active" in data:
                            updates["active"] = data["active"]
                        
                        merchants_table.update(i, updates)
                        database.save_all()
                        logger.info(f"Merchant updated: id={merchant_id}")
                        return jsonify({"success": True, "message": "Merchant updated"})
                
                logger.warning(f"Merchant row not found: id={merchant_id}")
                return jsonify({"error": "Merchant not found"}), 404
            
            except ValueError as e:
                logger.error(f"Validation error updating merchant {merchant_id}: {e}")
                return jsonify({"error": f"Validation error: {str(e)}"}), 400
            except Exception as e:
                logger.error(f"Error updating merchant {merchant_id}: {e}", exc_info=True)
                return jsonify({"error": "Error updating merchant"}), 500
        
        elif request.method == "DELETE":
            try:
                merchant = merchants_table.get_by_primary_key(merchant_id)
                
                if not merchant:
                    logger.warning(f"Attempt to delete non-existent merchant: id={merchant_id}")
                    return jsonify({"error": "Merchant not found"}), 404
                
                # Find and delete the row
                for i in range(len(merchants_table.rows) - 1, -1, -1):
                    if merchants_table.rows[i].get("id") == merchant_id:
                        merchants_table.delete(i)
                        database.save_all()
                        logger.info(f"Merchant deleted: id={merchant_id}")
                        return jsonify({"success": True, "message": "Merchant deleted"})
                
                logger.warning(f"Merchant row not found for deletion: id={merchant_id}")
                return jsonify({"error": "Merchant not found"}), 404
            
            except Exception as e:
                logger.error(f"Error deleting merchant {merchant_id}: {e}", exc_info=True)
                return jsonify({"error": "Error deleting merchant"}), 500
    
    except Exception as e:
        logger.error(f"Unexpected error in merchant_detail: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred"}), 500


@app.route("/api/categories", methods=["GET"])
def categories_api():
    """API endpoint for categories."""
    try:
        categories_table = database.get_table("categories")
        if not categories_table:
            return jsonify([])
        categories = [row.to_dict() for row in categories_table.scan()]
        return jsonify(categories)
    except Exception as e:
        logger.error(f"Error retrieving categories: {e}", exc_info=True)
        return jsonify({"error": "Error retrieving categories"}), 500


@app.route("/api/merchants/by-category/<category>", methods=["GET"])
def merchants_by_category(category):
    """Get merchants in a specific category."""
    try:
        if not category or not isinstance(category, str):
            logger.warning(f"Invalid category parameter: {category}")
            return jsonify({"error": "Invalid category"}), 400
        
        merchants_table = database.get_table("merchants")
        if not merchants_table:
            return jsonify([])
        
        merchants = merchants_table.filter("category", "=", category.strip())
        return jsonify([row.to_dict() for row in merchants])
    except Exception as e:
        logger.error(f"Error filtering merchants by category '{category}': {e}", exc_info=True)
        return jsonify({"error": "Error filtering merchants"}), 500


@app.route("/api/tables", methods=["GET"])
def list_tables():
    """Get list of all tables with their schemas."""
    try:
        tables = []
        for table_name, table in database.tables.items():
            table_info = {
                "name": table_name,
                "row_count": len(table.rows),
                "columns": []
            }
            
            # Add column information
            for col in table.schema.columns:
                table_info["columns"].append({
                    "name": col.name,
                    "data_type": col.data_type.value,
                    "primary_key": col.primary_key,
                    "unique": col.unique,
                    "nullable": col.nullable
                })
            
            tables.append(table_info)
        
        return jsonify(tables)
    except Exception as e:
        logger.error(f"Error listing tables: {e}", exc_info=True)
        return jsonify({"error": "Error listing tables"}), 500


@app.route("/api/query", methods=["POST"])
def execute_query():
    """Execute a custom SQL query or multiple queries separated by semicolons."""
    try:
        data = request.get_json()
        if not data:
            logger.warning("Empty request body for query execution")
            return jsonify({
                "success": False,
                "message": "Request data is required",
                "data": [],
                "affected_table": None
            }), 400
        
        sql = data.get("sql", "").strip()
        
        if not sql:
            logger.warning("No SQL provided in query request")
            return jsonify({
                "success": False,
                "message": "No SQL provided",
                "data": [],
                "affected_table": None
            }), 400
        
        # Split multiple statements by semicolon
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        
        if not statements:
            logger.warning("No valid SQL statements found")
            return jsonify({
                "success": False,
                "message": "No valid SQL statements found",
                "data": [],
                "affected_table": None
            }), 400
        
        # Validate SQL for injection attempts before executing
        for statement in statements:
            is_valid, error = InputValidator.validate_sql_statement(statement)
            if not is_valid:
                logger.warning(f"SQL injection attempt detected: {error} - SQL: {statement[:50]}")
                return jsonify({
                    "success": False,
                    "message": f"Security validation failed: {error}",
                    "data": [],
                    "affected_table": None
                }), 400
        
        # Execute each statement
        all_results = []
        affected_tables = set()
        
        for statement in statements:
            try:
                stmt = parser.parse(statement)
                result = engine.execute(stmt)
                
                # Track affected tables
                if hasattr(stmt, 'table_name'):
                    affected_tables.add(stmt.table_name)
                
                # Store each result
                all_results.append({
                    "statement": statement,
                    "success": result.success,
                    "message": result.message,
                    "data": result.data,
                    "table": stmt.table_name if hasattr(stmt, 'table_name') else None
                })
                
                logger.debug(f"Query executed: {statement[:50]}... - Success: {result.success}")
            
            except ParseError as e:
                logger.warning(f"Parse error in SQL statement: {statement[:50]}... - {e}")
                all_results.append({
                    "statement": statement,
                    "success": False,
                    "message": f"Parse error: {str(e)}",
                    "data": [],
                    "table": None
                })
            except Exception as e:
                logger.error(f"Error executing statement: {statement[:50]}... - {e}", exc_info=True)
                all_results.append({
                    "statement": statement,
                    "success": False,
                    "message": f"Error: {str(e)}",
                    "data": [],
                    "table": None
                })
        
        # Get the last result for primary response
        last_result = all_results[-1] if all_results else None
        affected_table = list(affected_tables)[0] if affected_tables else None
        
        # If multiple statements, fetch final table contents and show summary
        if len(all_results) > 1:
            summary_message = f"Executed {len(all_results)} statements"
            
            # Fetch final contents of affected tables
            table_contents = {}
            for table_name in affected_tables:
                try:
                    table = database.get_table(table_name)
                    if table:
                        table_contents[table_name] = [row.to_dict() for row in table.scan()]
                except Exception as e:
                    logger.error(f"Error fetching contents of table {table_name}: {e}")
            
            # Add table contents to results with labels
            results_with_tables = all_results.copy()
            for table_name, contents in table_contents.items():
                if contents:  # Only add if table has data
                    results_with_tables.append({
                        "statement": f"-- Final contents of {table_name}",
                        "success": True,
                        "message": f"Table '{table_name}' has {len(contents)} row(s)",
                        "data": contents,
                        "table": table_name,
                        "is_table_contents": True
                    })
            
            return jsonify({
                "success": all(r["success"] for r in all_results),
                "message": summary_message,
                "data": results_with_tables,
                "affected_table": affected_table
            })
        
        # Single statement - return normal result
        return jsonify({
            "success": last_result["success"] if last_result else False,
            "message": last_result["message"] if last_result else "No result",
            "data": last_result["data"] if last_result else [],
            "affected_table": affected_table
        })
    
    except Exception as e:
        logger.error(f"Unexpected error executing query: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "message": "An unexpected error occurred",
            "data": [],
            "affected_table": None
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    logger.warning(f"404 error: {request.path}")
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"500 error: {error}", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "False") == "True"
    app.run(debug=debug_mode, port=5000)
