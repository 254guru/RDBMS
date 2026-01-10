#!/bin/bash
# PesaPal RDBMS - Quick Launch Script
# This script helps you quickly run the RDBMS in different modes

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

clear

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                   PesaPal RDBMS - Launch Menu                      ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "\n${YELLOW}Choose how you want to use the RDBMS:${NC}\n"
echo "1) Run Interactive REPL (CLI)"
echo "2) Run Web Application (Flask)"
echo "3) Run Example Demo"
echo "4) Run System Tests"
echo "5) View Documentation"
echo "6) Exit"

read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        echo -e "\n${GREEN}Starting Interactive REPL...${NC}\n"
        python3 main.py
        ;;
    2)
        echo -e "\n${GREEN}Starting Web Application...${NC}\n"
        echo "Open your browser at: http://localhost:5000"
        echo "Press Ctrl+C to stop\n"
        cd web_app && python3 app.py
        ;;
    3)
        echo -e "\n${GREEN}Running Example Demo...${NC}\n"
        python3 example.py
        ;;
    4)
        echo -e "\n${GREEN}Running System Tests...${NC}\n"
        python3 -c "
from rdbms.storage import Database
from rdbms.parser import SQLParser
from rdbms.engine import ExecutionEngine

db = Database('./test_db')
engine = ExecutionEngine(db)
parser = SQLParser()

print('Running system tests...\n')

# Test basic operations
tests_passed = 0

# CREATE TABLE
r = engine.execute(parser.parse('CREATE TABLE test (id INT PRIMARY KEY, name TEXT)'))
if r.success:
    tests_passed += 1
    print('CREATE TABLE')

# INSERT
r = engine.execute(parser.parse('INSERT INTO test (id, name) VALUES (1, \"Alice\")'))
if r.success:
    tests_passed += 1
    print('INSERT')

# SELECT
r = engine.execute(parser.parse('SELECT * FROM test'))
if r.success:
    tests_passed += 1
    print('SELECT')

# UPDATE
r = engine.execute(parser.parse('UPDATE test SET name = \"Bob\" WHERE id = 1'))
if r.success:
    tests_passed += 1
    print('UPDATE')

# DELETE
r = engine.execute(parser.parse('DELETE FROM test WHERE id = 1'))
if r.success:
    tests_passed += 1
    print('DELETE')

print(f'\n{tests_passed}/5 tests passed!')

import shutil
shutil.rmtree('./test_db', ignore_errors=True)
"
        ;;
    5)
        echo -e "\n${GREEN}Documentation Files:${NC}\n"
        echo "1. README.md - Full feature documentation"
        echo "2. QUICKSTART.md - Get started in 5 minutes"
        echo "3. ARCHITECTURE.md - System design"
        echo "4. INDEXING.md - Performance analysis"
        echo "5. TESTING.md - Test scenarios"
        echo "6. GETTING_STARTED.md - Quick summary"
        echo ""
        read -p "Which file to view? (1-6, or 'q' to skip): " doc_choice
        case $doc_choice in
            1) cat README.md | less ;;
            2) cat QUICKSTART.md | less ;;
            3) cat ARCHITECTURE.md | less ;;
            4) cat INDEXING.md | less ;;
            5) cat TESTING.md | less ;;
            6) cat GETTING_STARTED.md | less ;;
            q) echo "Skipped" ;;
        esac
        ;;
    6)
        echo -e "\n${GREEN}Goodbye!${NC}\n"
        exit 0
        ;;
    *)
        echo -e "\n${YELLOW}Invalid choice. Please run the script again.${NC}\n"
        exit 1
        ;;
esac
