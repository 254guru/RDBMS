#!/bin/bash
# Final verification script - checks all components are working

set -e

echo "╔════════════════════════════════════════════════════════╗"
echo "║     PesaPal RDBMS - Final System Verification          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Check virtual environment
echo "Checking virtual environment..."
if [ -d ".venv" ]; then
    echo "Virtual environment found"
else
    echo "WARNING: Virtual environment not found"
fi

# Check required files
echo ""
echo "Checking required files..."
required_files=(
    "rdbms/types.py"
    "rdbms/storage.py"
    "rdbms/parser.py"
    "rdbms/engine.py"
    "rdbms/repl.py"
    "main.py"
    "example.py"
    "web_app/app.py"
    "web_app/templates/index.html"
    "web_app/static/style.css"
    "web_app/static/script.js"
    "README.md"
    "GUIDE.md"
    "launch.sh"
)

all_present=true
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "OK: $file"
    else
        echo "MISSING: $file"
        all_present=false
    fi
done

if [ "$all_present" = false ]; then
    echo ""
    echo "WARNING: Some files are missing!"
    exit 1
fi

# Check Python imports
echo ""
echo "Checking Python imports..."
python3 -c "from rdbms.types import DataType, Column, Schema, Row; print('types module')" 2>/dev/null || echo "types module failed"
python3 -c "from rdbms.storage import HashIndex, Table, Database; print('storage module')" 2>/dev/null || echo "storage module failed"
python3 -c "from rdbms.parser import SQLParser; print('parser module')" 2>/dev/null || echo "parser module failed"
python3 -c "from rdbms.engine import ExecutionEngine; print('engine module')" 2>/dev/null || echo "engine module failed"
python3 -c "from rdbms.repl import REPL; print('repl module')" 2>/dev/null || echo "repl module failed"

# Test basic functionality
echo ""
echo "Testing basic functionality..."
python3 << 'EOF'
from rdbms.storage import Database
from rdbms.parser import SQLParser
from rdbms.engine import ExecutionEngine
import tempfile
import shutil

# Create temporary database
tmpdir = tempfile.mkdtemp()
try:
    db = Database(tmpdir)
    parser = SQLParser()
    engine = ExecutionEngine(db)
    
    # Test CREATE
    result = engine.execute(parser.parse('CREATE TABLE test (id INT PRIMARY KEY, name TEXT)'))
    assert result.success, f"CREATE failed: {result.message}"
    print("CREATE TABLE")
    
    # Test INSERT
    result = engine.execute(parser.parse('INSERT INTO test (id, name) VALUES (1, "Alice")'))
    assert result.success, f"INSERT failed: {result.message}"
    print("INSERT")
    
    # Test SELECT
    result = engine.execute(parser.parse('SELECT * FROM test'))
    assert result.success, f"SELECT failed: {result.message}"
    assert len(result.data) == 1, f"Expected 1 row, got {len(result.data)}"
    print("SELECT")
    
    # Test WHERE
    result = engine.execute(parser.parse('SELECT * FROM test WHERE id = 1'))
    assert result.success, f"WHERE failed: {result.message}"
    assert len(result.data) == 1, f"WHERE returned wrong count"
    print("WHERE clause")
    
    # Test UPDATE
    result = engine.execute(parser.parse('UPDATE test SET name = "Bob" WHERE id = 1'))
    assert result.success, f"UPDATE failed: {result.message}"
    print("UPDATE")
    
    # Test DELETE
    result = engine.execute(parser.parse('DELETE FROM test WHERE id = 1'))
    assert result.success, f"DELETE failed: {result.message}"
    print("DELETE")

    print("\nAll core operations working!")
    
finally:
    shutil.rmtree(tmpdir, ignore_errors=True)
EOF

# Check documentation
echo ""
echo "Checking documentation..."
doc_files=(
    "README.md"
    "GUIDE.md"
)

total_lines=0
for doc in "${doc_files[@]}"; do
    lines=$(wc -l < "$doc")
    total_lines=$((total_lines + lines))
    echo "$doc ($lines lines)"
done
echo "Total documentation: $total_lines lines"

# Check code statistics
echo ""
echo "Code statistics..."
python_lines=$(find rdbms -name "*.py" | xargs wc -l | tail -1 | awk '{print $1}')
echo "RDBMS core: $python_lines lines"

web_lines=$(find web_app -name "*.py" -o -name "*.html" -o -name "*.css" -o -name "*.js" | xargs wc -l | tail -1 | awk '{print $1}')
echo "Web app: $web_lines lines"

# Final summary
echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║              SYSTEM VERIFICATION PASSED               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "Summary:"
echo "  • Python modules: 5 (types, storage, parser, engine, repl)"
echo "  • Core engine: $python_lines lines"
echo "  • Web application: $web_lines lines"
echo "  • Documentation: $total_lines lines"
echo "  • Total files: ${#required_files[@]} verified"
echo ""
echo "Ready to launch!"
echo ""
echo "Next steps:"
echo "  1. Run: ./launch.sh"
echo "  2. Choose: REPL (1), Web (2), or Demo (3)"
echo "  3. Follow instructions in each mode"
echo ""
