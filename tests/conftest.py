"""Shared test fixtures and configuration."""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_db_dir():
    """Create a temporary directory for database testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_schema():
    """Create a sample schema for testing."""
    from rdbms.types import Schema, Column, DataType
    
    return Schema(
        table_name="test_table",
        columns=[
            Column(name="id", data_type=DataType.INT, primary_key=True, nullable=False),
            Column(name="name", data_type=DataType.TEXT, unique=True, nullable=False),
            Column(name="active", data_type=DataType.BOOLEAN, nullable=True),
        ]
    )


@pytest.fixture
def database_instance(temp_db_dir):
    """Create a database instance for testing."""
    from rdbms.storage import Database
    return Database(temp_db_dir)


@pytest.fixture
def parser_instance():
    """Create a parser instance for testing."""
    from rdbms.parser import SQLParser
    return SQLParser()


@pytest.fixture
def engine_instance(database_instance):
    """Create an execution engine for testing."""
    from rdbms.engine import ExecutionEngine
    return ExecutionEngine(database_instance)
