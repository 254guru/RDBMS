"""
Web application demonstrating the RDBMS with a Merchant Directory.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
import sys
from pathlib import Path

# Add parent directory to path to import rdbms
sys.path.insert(0, str(Path(__file__).parent.parent))

from rdbms.storage import Database
from rdbms.parser import SQLParser
from rdbms.engine import ExecutionEngine
from rdbms.types import Schema, Column, DataType

app = Flask(__name__)

# Initialize database
DB_DIR = "./db"
database = Database(DB_DIR)
engine = ExecutionEngine(database)
parser = SQLParser()

# Initialize database with sample data if empty
def init_database():
    """Initialize the database with tables if they don't exist."""
    
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


init_database()


@app.route("/")
def index():
    """Home page - list all merchants."""
    merchants_table = database.get_table("merchants")
    merchants = [row.to_dict() for row in merchants_table.scan()]
    
    categories_table = database.get_table("categories")
    categories = [row.to_dict() for row in categories_table.scan()]
    
    return render_template("index.html", merchants=merchants, categories=categories)


@app.route("/api/merchants", methods=["GET", "POST"])
def merchants_api():
    """API endpoint for merchants."""
    if request.method == "POST":
        data = request.get_json()
        
        try:
            merchants_table = database.get_table("merchants")
            
            # Check if ID already exists
            existing = merchants_table.get_by_primary_key(int(data.get("id")))
            if existing:
                return jsonify({"error": "Merchant ID already exists"}), 400
            
            # Insert merchant
            merchants_table.insert({
                "id": int(data.get("id")),
                "name": data.get("name"),
                "category": data.get("category"),
                "active": data.get("active", True) == "true" or data.get("active") is True,
            })
            
            database.save_all()
            return jsonify({"success": True, "message": "Merchant added successfully"}), 201
        
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    else:
        # GET - return all merchants
        merchants_table = database.get_table("merchants")
        merchants = [row.to_dict() for row in merchants_table.scan()]
        return jsonify(merchants)


@app.route("/api/merchants/<int:merchant_id>", methods=["GET", "PUT", "DELETE"])
def merchant_detail(merchant_id):
    """API endpoint for individual merchant."""
    merchants_table = database.get_table("merchants")
    
    if request.method == "GET":
        merchant = merchants_table.get_by_primary_key(merchant_id)
        if merchant:
            return jsonify(merchant.to_dict())
        return jsonify({"error": "Merchant not found"}), 404
    
    elif request.method == "PUT":
        data = request.get_json()
        merchant = merchants_table.get_by_primary_key(merchant_id)
        
        if not merchant:
            return jsonify({"error": "Merchant not found"}), 404
        
        try:
            # Find the row index
            for i, row in enumerate(merchants_table.rows):
                if row.get("id") == merchant_id:
                    updates = {}
                    if "name" in data:
                        updates["name"] = data["name"]
                    if "category" in data:
                        updates["category"] = data["category"]
                    if "active" in data:
                        updates["active"] = data["active"]
                    
                    merchants_table.update(i, updates)
                    database.save_all()
                    return jsonify({"success": True, "message": "Merchant updated"})
            
            return jsonify({"error": "Merchant not found"}), 404
        
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    elif request.method == "DELETE":
        merchant = merchants_table.get_by_primary_key(merchant_id)
        
        if not merchant:
            return jsonify({"error": "Merchant not found"}), 404
        
        try:
            # Find and delete the row
            for i in range(len(merchants_table.rows) - 1, -1, -1):
                if merchants_table.rows[i].get("id") == merchant_id:
                    merchants_table.delete(i)
                    database.save_all()
                    return jsonify({"success": True, "message": "Merchant deleted"})
            
            return jsonify({"error": "Merchant not found"}), 404
        
        except Exception as e:
            return jsonify({"error": str(e)}), 400


@app.route("/api/categories", methods=["GET"])
def categories_api():
    """API endpoint for categories."""
    categories_table = database.get_table("categories")
    categories = [row.to_dict() for row in categories_table.scan()]
    return jsonify(categories)


@app.route("/api/merchants/by-category/<category>", methods=["GET"])
def merchants_by_category(category):
    """Get merchants in a specific category."""
    merchants_table = database.get_table("merchants")
    merchants = merchants_table.filter("category", "=", category)
    return jsonify([row.to_dict() for row in merchants])


@app.route("/api/tables", methods=["GET"])
def list_tables():
    """Get list of all tables with their schemas."""
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


@app.route("/api/query", methods=["POST"])
def execute_query():
    """Execute a custom SQL query or multiple queries separated by semicolons."""
    data = request.get_json()
    sql = data.get("sql", "").strip()
    
    if not sql:
        return jsonify({
            "success": False,
            "message": "No SQL provided",
            "data": [],
            "affected_table": None
        }), 400
    
    try:
        # Split multiple statements by semicolon
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        
        if not statements:
            return jsonify({
                "success": False,
                "message": "No valid SQL statements found",
                "data": [],
                "affected_table": None
            }), 400
        
        # Execute each statement
        last_result = None
        affected_tables = set()
        
        for statement in statements:
            stmt = parser.parse(statement)
            result = engine.execute(stmt)
            
            # Track affected tables
            if hasattr(stmt, 'table_name'):
                affected_tables.add(stmt.table_name)
            
            last_result = result
        
        # Return the result of the last statement
        affected_table = list(affected_tables)[0] if affected_tables else None
        
        return jsonify({
            "success": last_result.success,
            "message": last_result.message,
            "data": last_result.data,
            "affected_table": affected_table
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e),
            "data": [],
            "affected_table": None
        }), 400


if __name__ == "__main__":
    app.run(debug=True, port=5000)
