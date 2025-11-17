"""
Agent Memory Service - Standardized Memory System for All Agents

This service provides a unified interface for agent memory management across
the entire application. It integrates with:
- Database persistence (MySQL)
- Framework memory systems (LangChain, CrewAI adapters)
- Conversation management
- Project context tracking

Usage:
    memory_service = AgentMemoryService()

    # Create conversation
    conv_id = memory_service.create_conversation(
        project_id="uuid",
        agent_id="document_analyst_agent",
        conversation_type="document_analysis"
    )

    # Store messages
    memory_service.store_message(conv_id, "user", "Analyze this document")

    # Get history
    history = memory_service.get_conversation_history(conv_id, limit=10)
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import sys

# Database connection
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Framework memory (will integrate later)
framework_path = Path(__file__).parent.parent.parent / "framework"
sys.path.insert(0, str(framework_path))


load_dotenv()


class AgentMemoryService:
    """
    Unified memory service for all agents in the application.
    Handles conversations, messages, agent memory, and project context.
    """

    def __init__(self, db_config: Optional[Dict[str, Any]] = None):
        """
        Initialize memory service with database connection.

        Args:
            db_config: Database configuration. If None, loads from environment.
        """
        if db_config is None:
            db_config = {
                "host": os.getenv("DB_HOST", "localhost"),
                "port": int(os.getenv("DB_PORT", 3306)),
                "user": os.getenv("DB_USER", "root"),
                "password": os.getenv("DB_PASSWORD", ""),
                "database": os.getenv("DB_NAME", "langnet_db"),
            }

        self.db_config = db_config
        self._connection = None

    def _get_connection(self):
        """Get database connection (creates if doesn't exist)"""
        if self._connection is None or not self._connection.is_connected():
            try:
                self._connection = mysql.connector.connect(**self.db_config)
            except Error as e:
                raise Exception(f"Error connecting to database: {e}")
        return self._connection

    def _execute_query(
        self, query: str, params: Optional[Tuple] = None, fetch: bool = False
    ) -> Optional[List[Dict]]:
        """Execute SQL query with parameters"""
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(query, params or ())

            if fetch:
                result = cursor.fetchall()
                cursor.close()
                return result
            else:
                conn.commit()
                cursor.close()
                return None
        except Error as e:
            conn.rollback()
            raise Exception(f"Database error: {e}")

    # ========================================================================
    # CONVERSATION MANAGEMENT
    # ========================================================================

    def create_conversation(
        self,
        project_id: str,
        agent_id: str,
        conversation_type: str = "chat",
        context_data: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> str:
        """
        Create a new conversation with an agent.

        Args:
            project_id: Project UUID
            agent_id: Agent identifier (e.g., "document_analyst_agent")
            conversation_type: Type of conversation (chat, document_analysis, etc.)
            context_data: Optional context data (document_id, execution_id, etc.)
            user_id: Optional user UUID

        Returns:
            conversation_id: UUID of created conversation
        """
        conversation_id = str(uuid.uuid4())
        context_json = json.dumps(context_data) if context_data else None

        query = """
            INSERT INTO conversations
            (id, project_id, agent_id, user_id, conversation_type, context_data, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'active')
        """
        params = (
            conversation_id,
            project_id,
            agent_id,
            user_id,
            conversation_type,
            context_json,
        )

        self._execute_query(query, params)
        return conversation_id

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation by ID"""
        query = "SELECT * FROM conversations WHERE id = %s"
        result = self._execute_query(query, (conversation_id,), fetch=True)

        if result:
            conv = result[0]
            if conv.get("context_data"):
                conv["context_data"] = json.loads(conv["context_data"])
            return conv
        return None

    def end_conversation(self, conversation_id: str) -> bool:
        """Mark conversation as completed"""
        query = """
            UPDATE conversations
            SET status = 'completed', ended_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        self._execute_query(query, (conversation_id,))
        return True

    def get_project_conversations(
        self,
        project_id: str,
        conversation_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get all conversations for a project"""
        query = "SELECT * FROM conversations WHERE project_id = %s"
        params = [project_id]

        if conversation_type:
            query += " AND conversation_type = %s"
            params.append(conversation_type)

        if status:
            query += " AND status = %s"
            params.append(status)

        query += " ORDER BY started_at DESC LIMIT %s"
        params.append(limit)

        result = self._execute_query(query, tuple(params), fetch=True)
        return result or []

    # ========================================================================
    # MESSAGE MANAGEMENT
    # ========================================================================

    def store_message(
        self,
        conversation_id: str,
        sender: str,
        content: str,
        message_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None,
    ) -> str:
        """
        Store a message in the conversation.

        Args:
            conversation_id: Conversation UUID
            sender: 'user', 'agent', or 'system'
            content: Message text
            message_type: Type of message (text, command, error, result, etc.)
            metadata: Optional metadata (tokens, cost, tool_calls, etc.)
            agent_id: Agent that sent the message (if sender='agent')

        Returns:
            message_id: UUID of stored message
        """
        message_id = str(uuid.uuid4())
        metadata_json = json.dumps(metadata) if metadata else None

        query = """
            INSERT INTO messages
            (id, conversation_id, agent_id, sender, content, message_type, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            message_id,
            conversation_id,
            agent_id,
            sender,
            content,
            message_type,
            metadata_json,
        )

        self._execute_query(query, params)
        return message_id

    def get_conversation_history(
        self, conversation_id: str, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get conversation message history.

        Args:
            conversation_id: Conversation UUID
            limit: Maximum number of messages to return
            offset: Number of messages to skip

        Returns:
            List of messages (oldest first)
        """
        query = """
            SELECT * FROM messages
            WHERE conversation_id = %s
            ORDER BY timestamp ASC
            LIMIT %s OFFSET %s
        """
        result = self._execute_query(query, (conversation_id, limit, offset), fetch=True)

        if result:
            for msg in result:
                if msg.get("metadata"):
                    msg["metadata"] = json.loads(msg["metadata"])
        return result or []

    def get_recent_messages(
        self, conversation_id: str, count: int = 10
    ) -> List[Dict[str, Any]]:
        """Get N most recent messages from conversation"""
        query = """
            SELECT * FROM messages
            WHERE conversation_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """
        result = self._execute_query(query, (conversation_id, count), fetch=True)

        if result:
            result.reverse()  # Return in chronological order
            for msg in result:
                if msg.get("metadata"):
                    msg["metadata"] = json.loads(msg["metadata"])
        return result or []

    def get_message_count(self, conversation_id: str) -> int:
        """Get total message count for conversation"""
        query = "SELECT message_count FROM conversations WHERE id = %s"
        result = self._execute_query(query, (conversation_id,), fetch=True)
        return result[0]["message_count"] if result else 0

    # ========================================================================
    # AGENT MEMORY (short-term, long-term, context, entities)
    # ========================================================================

    def store_memory(
        self,
        agent_id: str,
        project_id: str,
        memory_type: str,
        key: str,
        value: Any,
        importance: float = 1.0,
        conversation_id: Optional[str] = None,
        expires_in_hours: Optional[int] = None,
    ) -> str:
        """
        Store a memory item for an agent.

        Args:
            agent_id: Agent identifier
            project_id: Project UUID
            memory_type: 'short_term', 'long_term', 'context', 'entity'
            key: Memory key
            value: Memory value (will be JSON encoded if dict/list)
            importance: Importance score (0.0-100.0) for pruning
            conversation_id: Optional conversation link
            expires_in_hours: Expiration time for short-term memory

        Returns:
            memory_id: UUID of stored memory
        """
        memory_id = str(uuid.uuid4())

        # Encode value as JSON if needed
        if isinstance(value, (dict, list)):
            value_str = json.dumps(value)
        else:
            value_str = str(value)

        # Calculate expiration
        expires_at = None
        if expires_in_hours:
            expires_at = datetime.now() + timedelta(hours=expires_in_hours)

        # Use INSERT ... ON DUPLICATE KEY UPDATE to handle unique constraint
        query = """
            INSERT INTO agent_memory
            (id, agent_id, project_id, conversation_id, memory_type, key_name, value,
             importance_score, expires_at, access_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 0)
            ON DUPLICATE KEY UPDATE
                value = VALUES(value),
                importance_score = VALUES(importance_score),
                expires_at = VALUES(expires_at),
                updated_at = CURRENT_TIMESTAMP
        """
        params = (
            memory_id,
            agent_id,
            project_id,
            conversation_id,
            memory_type,
            key,
            value_str,
            importance,
            expires_at,
        )

        self._execute_query(query, params)
        return memory_id

    def recall_memory(
        self,
        agent_id: str,
        project_id: str,
        key: str,
        memory_type: Optional[str] = None,
    ) -> Optional[Any]:
        """
        Recall a memory item by key.

        Args:
            agent_id: Agent identifier
            project_id: Project UUID
            key: Memory key
            memory_type: Optional memory type filter

        Returns:
            Memory value (parsed from JSON if applicable) or None
        """
        query = """
            SELECT value FROM agent_memory
            WHERE agent_id = %s AND project_id = %s AND key_name = %s
        """
        params = [agent_id, project_id, key]

        if memory_type:
            query += " AND memory_type = %s"
            params.append(memory_type)

        query += " AND (expires_at IS NULL OR expires_at > NOW())"

        result = self._execute_query(query, tuple(params), fetch=True)

        if result:
            # Update access stats
            self._update_memory_access(agent_id, project_id, key)

            value_str = result[0]["value"]
            try:
                return json.loads(value_str)
            except json.JSONDecodeError:
                return value_str

        return None

    def _update_memory_access(self, agent_id: str, project_id: str, key: str):
        """Update access timestamp and count for memory item"""
        query = """
            UPDATE agent_memory
            SET last_accessed = CURRENT_TIMESTAMP
            WHERE agent_id = %s AND project_id = %s AND key_name = %s
        """
        self._execute_query(query, (agent_id, project_id, key))

    def search_memory(
        self,
        agent_id: str,
        project_id: str,
        query_string: str,
        memory_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search memory items by content (basic text search).

        Args:
            agent_id: Agent identifier
            project_id: Project UUID
            query_string: Search query
            memory_type: Optional memory type filter
            limit: Maximum results

        Returns:
            List of matching memory items
        """
        query = """
            SELECT key_name, value, memory_type, importance_score, created_at
            FROM agent_memory
            WHERE agent_id = %s AND project_id = %s
            AND (key_name LIKE %s OR value LIKE %s)
        """
        params = [agent_id, project_id, f"%{query_string}%", f"%{query_string}%"]

        if memory_type:
            query += " AND memory_type = %s"
            params.append(memory_type)

        query += " AND (expires_at IS NULL OR expires_at > NOW())"
        query += " ORDER BY importance_score DESC, last_accessed DESC LIMIT %s"
        params.append(limit)

        result = self._execute_query(query, tuple(params), fetch=True)
        return result or []

    def prune_memory(
        self,
        agent_id: str,
        project_id: str,
        memory_type: str = "short_term",
        retention_policy: str = "importance",
        keep_count: int = 100,
    ) -> int:
        """
        Prune (remove) old/low-importance memory items.

        Args:
            agent_id: Agent identifier
            project_id: Project UUID
            memory_type: Type of memory to prune
            retention_policy: 'importance', 'recency', 'hybrid'
            keep_count: Number of items to keep

        Returns:
            Number of items deleted
        """
        # First, delete expired items
        query_expired = """
            DELETE FROM agent_memory
            WHERE agent_id = %s AND project_id = %s AND memory_type = %s
            AND expires_at IS NOT NULL AND expires_at < NOW()
        """
        self._execute_query(query_expired, (agent_id, project_id, memory_type))

        # Then prune based on policy
        if retention_policy == "importance":
            order_by = "importance_score DESC, last_accessed DESC"
        elif retention_policy == "recency":
            order_by = "last_accessed DESC"
        else:  # hybrid
            order_by = "(importance_score * 0.7 + access_count * 0.3) DESC"

        # Get IDs to keep
        query_keep = f"""
            SELECT id FROM agent_memory
            WHERE agent_id = %s AND project_id = %s AND memory_type = %s
            AND (expires_at IS NULL OR expires_at > NOW())
            ORDER BY {order_by}
            LIMIT %s
        """
        keep_result = self._execute_query(
            query_keep, (agent_id, project_id, memory_type, keep_count), fetch=True
        )

        if not keep_result:
            return 0

        keep_ids = [row["id"] for row in keep_result]
        placeholders = ",".join(["%s"] * len(keep_ids))

        # Delete items not in keep list
        query_delete = f"""
            DELETE FROM agent_memory
            WHERE agent_id = %s AND project_id = %s AND memory_type = %s
            AND id NOT IN ({placeholders})
        """
        params = [agent_id, project_id, memory_type] + keep_ids
        self._execute_query(query_delete, tuple(params))

        # Return count deleted (approximate)
        return max(0, self.get_memory_count(agent_id, project_id, memory_type) - keep_count)

    def get_memory_count(
        self, agent_id: str, project_id: str, memory_type: Optional[str] = None
    ) -> int:
        """Get count of memory items"""
        query = "SELECT COUNT(*) as count FROM agent_memory WHERE agent_id = %s AND project_id = %s"
        params = [agent_id, project_id]

        if memory_type:
            query += " AND memory_type = %s"
            params.append(memory_type)

        query += " AND (expires_at IS NULL OR expires_at > NOW())"

        result = self._execute_query(query, tuple(params), fetch=True)
        return result[0]["count"] if result else 0

    # ========================================================================
    # PROJECT CONTEXT
    # ========================================================================

    def store_project_context(
        self,
        project_id: str,
        context_type: str,
        key: str,
        value: Any,
        source: Optional[str] = None,
    ) -> str:
        """
        Store project-level context (requirements, architecture, decisions, etc.)

        Args:
            project_id: Project UUID
            context_type: Type of context (requirements, architecture, decisions, glossary)
            key: Context key (e.g., FR-001, entity:User)
            value: Context value
            source: Source of context (document_analysis, chat, manual)

        Returns:
            context_id: UUID of stored context
        """
        context_id = str(uuid.uuid4())

        # Encode value
        if isinstance(value, (dict, list)):
            value_str = json.dumps(value)
        else:
            value_str = str(value)

        query = """
            INSERT INTO project_context
            (id, project_id, context_type, context_key, context_value, source, version)
            VALUES (%s, %s, %s, %s, %s, %s, 1)
            ON DUPLICATE KEY UPDATE
                context_value = VALUES(context_value),
                source = VALUES(source),
                version = version + 1,
                updated_at = CURRENT_TIMESTAMP
        """
        params = (context_id, project_id, context_type, key, value_str, source)

        self._execute_query(query, params)
        return context_id

    def get_project_context(
        self, project_id: str, context_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get all context for a project (optionally filtered by type).

        Args:
            project_id: Project UUID
            context_type: Optional filter by context type

        Returns:
            Dict mapping context_key to parsed values
        """
        query = "SELECT context_key, context_value FROM project_context WHERE project_id = %s"
        params = [project_id]

        if context_type:
            query += " AND context_type = %s"
            params.append(context_type)

        result = self._execute_query(query, tuple(params), fetch=True)

        if not result:
            return {}

        context_dict = {}
        for row in result:
            key = row["context_key"]
            value_str = row["context_value"]
            try:
                context_dict[key] = json.loads(value_str)
            except json.JSONDecodeError:
                context_dict[key] = value_str

        return context_dict

    def update_project_context(
        self, project_id: str, context_type: str, key: str, value: Any
    ) -> bool:
        """Update existing project context (increments version)"""
        return self.store_project_context(project_id, context_type, key, value) is not None

    # ========================================================================
    # FRAMEWORK MEMORY INTEGRATION
    # ========================================================================

    def create_agent_memory_system(
        self,
        agent_id: str,
        project_id: str,
        conversation_id: Optional[str] = None,
        short_term_capacity: int = 100,
        long_term_capacity: int = 1000,
    ):
        """
        Create a framework memory system instance for an agent.
        This returns a TaskMemorySystem that uses database persistence.

        Args:
            agent_id: Agent identifier
            project_id: Project UUID
            conversation_id: Optional conversation ID for context
            short_term_capacity: Max short-term memory items
            long_term_capacity: Max long-term memory items

        Returns:
            TaskMemorySystem instance configured with database backend
        """
        # Import framework memory (will implement in next step)
        from frameworkmemorylcf import AiTeamMemorySystemFactory

        # Create memory system with database persistence
        memory_system = AiTeamMemorySystemFactory.create_memory_system(
            implementation="database",  # New implementation we'll add
            task_name=f"{agent_id}_{project_id}",
            memory_service=self,  # Pass this service instance
            agent_id=agent_id,
            project_id=project_id,
            conversation_id=conversation_id,
            short_term_capacity=short_term_capacity,
            long_term_capacity=long_term_capacity,
        )

        return memory_system

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def close(self):
        """Close database connection"""
        if self._connection and self._connection.is_connected():
            self._connection.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================


def get_memory_service() -> AgentMemoryService:
    """Get a configured AgentMemoryService instance"""
    return AgentMemoryService()


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example usage
    with AgentMemoryService() as memory:
        # Create a conversation
        conv_id = memory.create_conversation(
            project_id="test-project-123",
            agent_id="document_analyst_agent",
            conversation_type="document_analysis",
            context_data={"document_id": "doc-456", "execution_id": "exec-789"},
        )

        print(f"Created conversation: {conv_id}")

        # Store messages
        memory.store_message(conv_id, "user", "Please analyze this document")
        memory.store_message(
            conv_id,
            "agent",
            "I will analyze the document for requirements",
            agent_id="document_analyst_agent",
        )

        # Get history
        history = memory.get_conversation_history(conv_id)
        print(f"Conversation has {len(history)} messages")

        # Store memory
        memory.store_memory(
            agent_id="document_analyst_agent",
            project_id="test-project-123",
            memory_type="long_term",
            key="domain_knowledge",
            value={"domain": "healthcare", "regulations": ["HIPAA", "GDPR"]},
            importance=8.5,
        )

        # Recall memory
        domain_knowledge = memory.recall_memory(
            agent_id="document_analyst_agent",
            project_id="test-project-123",
            key="domain_knowledge",
        )
        print(f"Recalled knowledge: {domain_knowledge}")

        # Store project context
        memory.store_project_context(
            project_id="test-project-123",
            context_type="requirements",
            key="FR-001",
            value={"description": "User login", "priority": "high"},
            source="document_analysis",
        )

        # Get project context
        requirements = memory.get_project_context(
            project_id="test-project-123", context_type="requirements"
        )
        print(f"Project requirements: {requirements}")
