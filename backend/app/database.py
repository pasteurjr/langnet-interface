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


# ============================================================
# CHAT MESSAGES CRUD OPERATIONS
# ============================================================

def save_chat_message(
    session_id: str,
    sender_type: str,
    message_text: str,
    message_type: str = "chat",
    task_execution_id: str = None,
    agent_id: str = None,
    sender_name: str = None,
    parent_message_id: str = None,
    metadata: dict = None
) -> str:
    """
    Save a chat message to the database

    Args:
        session_id: ID of the execution session
        sender_type: Type of sender (user, agent, system, assistant)
        message_text: Content of the message
        message_type: Type of message (chat, status, progress, result, error, warning, info, document)
        task_execution_id: Optional task execution ID
        agent_id: Optional agent ID
        sender_name: Optional sender name
        parent_message_id: Optional parent message ID for threading
        metadata: Optional metadata dictionary

    Returns:
        ID of the created message
    """
    import json
    import uuid

    message_id = str(uuid.uuid4())
    metadata_json = json.dumps(metadata) if metadata else None

    query = """
        INSERT INTO chat_messages (
            id, session_id, task_execution_id, agent_id, sender_type,
            sender_name, message_text, message_type, parent_message_id, metadata
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    params = (
        message_id, session_id, task_execution_id, agent_id, sender_type,
        sender_name, message_text, message_type, parent_message_id, metadata_json
    )

    with get_db_cursor() as cursor:
        cursor.execute(query, params)

    return message_id


def save_specification_chat_message(
    session_id: str,
    sender_type: str,
    message_text: str,
    message_type: str = "chat",
    sender_name: str = None,
    parent_message_id: str = None,
    metadata: dict = None
) -> str:
    """
    Save a chat message for specification sessions (uses specification_chat_messages table)
    """
    import uuid
    import json

    message_id = str(uuid.uuid4())

    metadata_json = json.dumps(metadata) if metadata else None

    query = """
        INSERT INTO specification_chat_messages (
            id, session_id, sender_type, sender_name, message_text,
            message_type, parent_message_id, metadata
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    params = (
        message_id, session_id, sender_type, sender_name, message_text,
        message_type, parent_message_id, metadata_json
    )

    with get_db_cursor() as cursor:
        cursor.execute(query, params)

    return message_id


def get_specification_chat_messages(session_id: str, limit: int = 50) -> list:
    """Get chat messages for a specification session"""
    import json

    query = """
        SELECT * FROM specification_chat_messages
        WHERE session_id = %s
        ORDER BY timestamp ASC LIMIT %s
    """

    messages = execute_query(query, (session_id, limit), fetch_all=True)

    for msg in messages:
        if msg.get('metadata') and isinstance(msg['metadata'], str):
            try:
                msg['metadata'] = json.loads(msg['metadata'])
            except:
                msg['metadata'] = None

    return messages


def get_specification_chat_message(message_id: str) -> dict:
    """Get a single specification chat message by ID"""
    import json

    query = "SELECT * FROM specification_chat_messages WHERE id = %s"
    msg = execute_query(query, (message_id,), fetch_one=True)

    if msg and msg.get('metadata') and isinstance(msg['metadata'], str):
        try:
            msg['metadata'] = json.loads(msg['metadata'])
        except:
            msg['metadata'] = None

    return msg


def update_specification_chat_message(
    message_id: str,
    message_text: str = None,
    metadata: dict = None
) -> int:
    """Update a specification chat message"""
    import json

    updates = []
    params = []

    if message_text is not None:
        updates.append("message_text = %s")
        params.append(message_text)

    if metadata is not None:
        updates.append("metadata = %s")
        params.append(json.dumps(metadata))

    if not updates:
        return 0

    query = f"UPDATE specification_chat_messages SET {', '.join(updates)} WHERE id = %s"
    params.append(message_id)

    return execute_update(query, tuple(params))


def get_chat_messages(
    session_id: str,
    limit: int = 50,
    offset: int = 0,
    include_deleted: bool = False,
    message_type: str = None
) -> list:
    """
    Get chat messages for a session

    Args:
        session_id: ID of the execution session
        limit: Maximum number of messages to return
        offset: Number of messages to skip
        include_deleted: Include soft-deleted messages
        message_type: Filter by message type

    Returns:
        List of message dictionaries
    """
    import json

    query = """
        SELECT * FROM chat_messages
        WHERE session_id = %s
    """
    params = [session_id]

    if not include_deleted:
        query += " AND is_deleted = 0"

    if message_type:
        query += " AND message_type = %s"
        params.append(message_type)

    query += " ORDER BY timestamp ASC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    messages = execute_query(query, tuple(params), fetch_all=True)

    # Convert metadata from JSON string to dict
    for msg in messages:
        if msg.get('metadata') and isinstance(msg['metadata'], str):
            try:
                msg['metadata'] = json.loads(msg['metadata'])
            except:
                msg['metadata'] = None

    return messages


def get_chat_message(message_id: str) -> dict:
    """
    Get a single chat message by ID

    Args:
        message_id: ID of the message

    Returns:
        Message dictionary or None
    """
    import json

    query = "SELECT * FROM chat_messages WHERE id = %s"
    msg = execute_query(query, (message_id,), fetch_one=True)

    # Convert metadata from JSON string to dict
    if msg and msg.get('metadata') and isinstance(msg['metadata'], str):
        try:
            msg['metadata'] = json.loads(msg['metadata'])
        except:
            msg['metadata'] = None

    return msg


def get_previous_refinements(session_id: str, limit: int = 10) -> list:
    """
    Get previous user refinement messages for context building

    Args:
        session_id: ID of the execution session
        limit: Maximum number of previous refinements to return

    Returns:
        List of user message dictionaries ordered by timestamp ASC
    """
    query = """
        SELECT message_text, timestamp, sender_type
        FROM chat_messages
        WHERE session_id = %s
          AND sender_type = 'user'
          AND message_type = 'chat'
          AND is_deleted = 0
        ORDER BY timestamp ASC
        LIMIT %s
    """

    messages = execute_query(query, (session_id, limit), fetch_all=True)
    return messages if messages else []


def update_chat_message(
    message_id: str,
    message_text: str = None,
    is_read: bool = None,
    is_pinned: bool = None,
    metadata: dict = None
) -> int:
    """
    Update a chat message

    Args:
        message_id: ID of the message
        message_text: Updated message text
        is_read: Mark as read/unread
        is_pinned: Mark as pinned/unpinned
        metadata: Updated metadata

    Returns:
        Number of affected rows
    """
    import json

    updates = []
    params = []

    if message_text is not None:
        updates.append("message_text = %s")
        params.append(message_text)

    if is_read is not None:
        updates.append("is_read = %s")
        params.append(int(is_read))

    if is_pinned is not None:
        updates.append("is_pinned = %s")
        params.append(int(is_pinned))

    if metadata is not None:
        updates.append("metadata = %s")
        params.append(json.dumps(metadata))

    if not updates:
        return 0

    query = f"UPDATE chat_messages SET {', '.join(updates)} WHERE id = %s"
    params.append(message_id)

    return execute_update(query, tuple(params))


def delete_chat_message(message_id: str, soft_delete: bool = True) -> int:
    """
    Delete a chat message (soft or hard delete)

    Args:
        message_id: ID of the message
        soft_delete: If True, mark as deleted. If False, permanently delete.

    Returns:
        Number of affected rows
    """
    if soft_delete:
        query = """
            UPDATE chat_messages
            SET is_deleted = 1, deleted_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        return execute_update(query, (message_id,))
    else:
        query = "DELETE FROM chat_messages WHERE id = %s"
        return execute_delete(query, (message_id,))


def get_chat_message_count(session_id: str, include_deleted: bool = False) -> int:
    """
    Get total count of messages in a session

    Args:
        session_id: ID of the execution session
        include_deleted: Include soft-deleted messages

    Returns:
        Total count of messages
    """
    query = "SELECT COUNT(*) as count FROM chat_messages WHERE session_id = %s"
    params = [session_id]

    if not include_deleted:
        query += " AND is_deleted = 0"

    result = execute_query(query, tuple(params), fetch_one=True)
    return result['count'] if result else 0


def get_chat_threads(parent_message_id: str) -> list:
    """
    Get all messages in a thread (replies to a parent message)

    Args:
        parent_message_id: ID of the parent message

    Returns:
        List of message dictionaries
    """
    import json

    query = """
        SELECT * FROM chat_messages
        WHERE parent_message_id = %s AND is_deleted = 0
        ORDER BY timestamp ASC
    """
    messages = execute_query(query, (parent_message_id,), fetch_all=True)

    # Convert metadata from JSON string to dict
    for msg in messages:
        if msg.get('metadata') and isinstance(msg['metadata'], str):
            try:
                msg['metadata'] = json.loads(msg['metadata'])
            except:
                msg['metadata'] = None

    return messages


# ════════════════════════════════════════════════════════════════
# AGENT TASK SPECIFICATION SESSIONS
# ════════════════════════════════════════════════════════════════

def create_agent_task_spec_session(session_data: dict) -> str:
    """Create a new agent task specification session"""
    import json

    # Convert execution_metadata dict to JSON string if present
    if 'execution_metadata' in session_data and isinstance(session_data['execution_metadata'], dict):
        session_data['execution_metadata'] = json.dumps(session_data['execution_metadata'])

    query = """
        INSERT INTO agent_task_specification_sessions (
            id, project_id, user_id, specification_session_id, specification_version,
            session_name, status, execution_metadata
        ) VALUES (
            %(id)s, %(project_id)s, %(user_id)s, %(specification_session_id)s, %(specification_version)s,
            %(session_name)s, %(status)s, %(execution_metadata)s
        )
    """

    with get_db_cursor() as cursor:
        cursor.execute(query, session_data)

    return session_data["id"]


def get_agent_task_spec_session(session_id: str) -> dict:
    """Get a specific agent task specification session"""
    import json

    query = "SELECT * FROM agent_task_specification_sessions WHERE id = %s"
    session = execute_query(query, (session_id,), fetch_one=True)

    if session and session.get('execution_metadata') and isinstance(session['execution_metadata'], str):
        try:
            session['execution_metadata'] = json.loads(session['execution_metadata'])
        except:
            session['execution_metadata'] = None

    return session


def update_agent_task_spec_session(session_id: str, updates: dict) -> int:
    """Update an agent task specification session"""
    import json

    # Convert execution_metadata dict to JSON string if present
    if 'execution_metadata' in updates and isinstance(updates['execution_metadata'], dict):
        updates['execution_metadata'] = json.dumps(updates['execution_metadata'])

    set_clauses = []
    params = []

    for key, value in updates.items():
        set_clauses.append(f"{key} = %s")
        params.append(value)

    params.append(session_id)

    query = f"""
        UPDATE agent_task_specification_sessions
        SET {', '.join(set_clauses)}
        WHERE id = %s
    """

    with get_db_cursor() as cursor:
        cursor.execute(query, tuple(params))
        return cursor.rowcount


def list_agent_task_spec_sessions(project_id: str) -> list:
    """List all agent task specification sessions for a project"""
    import json

    query = """
        SELECT * FROM agent_task_specification_sessions
        WHERE project_id = %s
        ORDER BY created_at DESC
    """

    sessions = execute_query(query, (project_id,), fetch_all=True)

    # Parse execution_metadata JSON
    for session in sessions:
        if session.get('execution_metadata') and isinstance(session['execution_metadata'], str):
            try:
                session['execution_metadata'] = json.loads(session['execution_metadata'])
            except:
                session['execution_metadata'] = None

    return sessions


# ════════════════════════════════════════════════════════════════
# AGENT TASK SPEC VERSION HISTORY
# ════════════════════════════════════════════════════════════════

def create_agent_task_spec_version(version_data: dict) -> None:
    """Create a new version of agent task specification document"""
    import json

    # Convert section_changes dict to JSON string if present
    if 'section_changes' in version_data and isinstance(version_data['section_changes'], dict):
        version_data['section_changes'] = json.dumps(version_data['section_changes'])

    query = """
        INSERT INTO agent_task_spec_version_history (
            session_id, version, agent_task_spec_document,
            created_by, change_type, doc_size
        ) VALUES (
            %(session_id)s, %(version)s, %(agent_task_spec_document)s,
            %(created_by)s, %(change_type)s, %(doc_size)s
        )
    """

    with get_db_cursor() as cursor:
        cursor.execute(query, version_data)


def get_agent_task_spec_versions(session_id: str) -> list:
    """Get version history for an agent task specification session"""
    import json

    query = """
        SELECT * FROM agent_task_spec_version_history
        WHERE session_id = %s
        ORDER BY version DESC
    """

    versions = execute_query(query, (session_id,), fetch_all=True)

    # Parse section_changes JSON
    for version in versions:
        if version.get('section_changes') and isinstance(version['section_changes'], str):
            try:
                version['section_changes'] = json.loads(version['section_changes'])
            except:
                version['section_changes'] = None

    return versions


# ════════════════════════════════════════════════════════════════
# AGENT TASK SPEC CHAT MESSAGES
# ════════════════════════════════════════════════════════════════

def save_agent_task_spec_chat_message(message_data: dict) -> str:
    """Save a chat message for agent task specification sessions"""
    import uuid
    import json

    message_id = str(uuid.uuid4())

    # Convert metadata dict to JSON string if present
    if 'metadata' in message_data and isinstance(message_data['metadata'], dict):
        message_data['metadata'] = json.dumps(message_data['metadata'])

    query = """
        INSERT INTO agent_task_spec_chat_messages (
            id, session_id, sender_type, sender_name, message_text,
            message_type, parent_message_id, metadata
        ) VALUES (
            %(id)s, %(session_id)s, %(sender_type)s, %(sender_name)s, %(message_text)s,
            %(message_type)s, %(parent_message_id)s, %(metadata)s
        )
    """

    # Add message_id to data
    params = {**message_data, 'id': message_id}

    # Set defaults
    params.setdefault('sender_name', None)
    params.setdefault('parent_message_id', None)
    params.setdefault('metadata', None)
    params.setdefault('message_type', 'chat')

    with get_db_cursor() as cursor:
        cursor.execute(query, params)

    return message_id


def get_agent_task_spec_chat_messages(session_id: str, limit: int = 50) -> list:
    """Get chat messages for an agent task specification session"""
    import json

    query = """
        SELECT * FROM agent_task_spec_chat_messages
        WHERE session_id = %s
        ORDER BY timestamp DESC
        LIMIT %s
    """

    messages = execute_query(query, (session_id, limit), fetch_all=True)

    # Parse metadata JSON and reverse to chronological order
    for msg in messages:
        if msg.get('metadata') and isinstance(msg['metadata'], str):
            try:
                msg['metadata'] = json.loads(msg['metadata'])
            except:
                msg['metadata'] = None

    return list(reversed(messages))  # Return in chronological order


def get_previous_agent_task_spec_refinements(session_id: str, limit: int = 10) -> list:
    """
    Busca últimos N refinamentos de um documento de especificação de agentes/tarefas

    Retorna mensagens de usuário do tipo 'chat' para incluir como contexto em refinamentos
    """
    query = """
        SELECT message_text, timestamp, sender_type
        FROM agent_task_spec_chat_messages
        WHERE session_id = %s
          AND sender_type = 'user'
          AND message_type = 'chat'
        ORDER BY timestamp DESC
        LIMIT %s
    """

    messages = execute_query(query, (session_id, limit), fetch_all=True)
    return list(reversed(messages))  # Return in chronological order


# Initialize pool on module import
try:
    init_db_pool()
except Exception as e:
    print(f"⚠️  Database pool initialization deferred: {e}")
