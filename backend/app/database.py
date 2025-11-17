"""
Database connection management using MySQL Connector/Python
"""
import os
from contextlib import contextmanager
from typing import Generator
import mysql.connector
from mysql.connector import pooling, Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "camerascasas.no-ip.info"),
    "port": int(os.getenv("DB_PORT", 3308)),
    "user": os.getenv("DB_USER", "producao"),
    "password": os.getenv("DB_PASSWORD", "112358123"),
    "database": os.getenv("DB_NAME", "langnet"),
    "charset": "utf8mb4",
    "collation": "utf8mb4_unicode_ci",
    "autocommit": False,
    "raise_on_warnings": True
}

# Connection pool configuration
POOL_CONFIG = {
    **DB_CONFIG,
    "pool_name": "langnet_pool",
    "pool_size": 10,
    "pool_reset_session": True
}

# Global connection pool
connection_pool = None


def init_db_pool():
    """Initialize the database connection pool"""
    global connection_pool
    try:
        connection_pool = pooling.MySQLConnectionPool(**POOL_CONFIG)
        print(f"✅ Database pool initialized: {DB_CONFIG['database']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}")
        return connection_pool
    except Error as e:
        print(f"❌ Error initializing database pool: {e}")
        raise


def get_db_pool():
    """Get the database connection pool"""
    global connection_pool
    if connection_pool is None:
        connection_pool = init_db_pool()
    return connection_pool


@contextmanager
def get_db_connection() -> Generator:
    """
    Context manager for database connections from pool

    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
    """
    pool = get_db_pool()
    connection = None
    try:
        connection = pool.get_connection()
        yield connection
    except Error as e:
        if connection:
            connection.rollback()
        print(f"❌ Database error: {e}")
        raise
    finally:
        if connection and connection.is_connected():
            connection.close()


@contextmanager
def get_db_cursor(dictionary=True, buffered=True):
    """
    Context manager for database cursor with automatic connection handling

    Args:
        dictionary: If True, return rows as dictionaries (default: True)
        buffered: If True, fetch all rows immediately (default: True)

    Usage:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
    """
    with get_db_connection() as connection:
        cursor = connection.cursor(dictionary=dictionary, buffered=buffered)
        try:
            yield cursor
            connection.commit()
        except Error as e:
            connection.rollback()
            raise
        finally:
            cursor.close()


def execute_query(query: str, params: tuple = None, fetch_one=False, fetch_all=False):
    """
    Execute a SELECT query and return results

    Args:
        query: SQL query string
        params: Query parameters tuple
        fetch_one: Return single row
        fetch_all: Return all rows

    Returns:
        Single row (dict) if fetch_one=True
        List of rows (list[dict]) if fetch_all=True
        None otherwise
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, params or ())

        if fetch_one:
            return cursor.fetchone()
        elif fetch_all:
            return cursor.fetchall()

        return None


def execute_insert(query: str, params: tuple = None) -> int:
    """
    Execute an INSERT query and return the last inserted ID

    Args:
        query: SQL INSERT query
        params: Query parameters tuple

    Returns:
        Last inserted row ID
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, params or ())
        return cursor.lastrowid


def execute_update(query: str, params: tuple = None) -> int:
    """
    Execute an UPDATE query and return the number of affected rows

    Args:
        query: SQL UPDATE query
        params: Query parameters tuple

    Returns:
        Number of affected rows
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, params or ())
        return cursor.rowcount


def execute_delete(query: str, params: tuple = None) -> int:
    """
    Execute a DELETE query and return the number of deleted rows

    Args:
        query: SQL DELETE query
        params: Query parameters tuple

    Returns:
        Number of deleted rows
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, params or ())
        return cursor.rowcount


def test_connection():
    """Test database connection"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT VERSION() as version, DATABASE() as database")
            result = cursor.fetchone()
            print(f"✅ Database connection successful!")
            print(f"   MySQL Version: {result['version']}")
            print(f"   Database: {result['database']}")
            return True
    except Error as e:
        print(f"❌ Database connection failed: {e}")
        return False


# Initialize pool on module import
try:
    init_db_pool()
except Exception as e:
    print(f"⚠️  Database pool initialization deferred: {e}")
