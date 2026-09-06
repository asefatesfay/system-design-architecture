"""
SQLite-based session manager for Strands agents.

This provides persistent session storage using SQLite database instead of files.
Benefits: queryable, atomic transactions, better performance, single file.
"""

import json
import sqlite3
from pathlib import Path
from typing import Any
from strands.session.repository_session_manager import RepositorySessionManager
from strands.session.session_repository import (
    SessionRepository,
    Session,
    SessionAgent,
    SessionMessage,
)


class SQLiteSessionManager(RepositorySessionManager, SessionRepository):
    """SQLite-based session manager implementation."""

    def __init__(
        self,
        session_id: str,
        db_path: str | None = None,
        **kwargs: Any
    ):
        """
        Initialize SQLite session manager.

        Args:
            session_id: Unique session identifier
            db_path: Path to SQLite database file. Defaults to ~/.strands/sessions.db
            **kwargs: Additional arguments for future extensibility
        """
        if db_path is None:
            db_dir = Path.home() / ".strands"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(db_dir / "sessions.db")

        self.db_path = db_path
        self._init_database()

        # Initialize parent with self as the repository
        super().__init__(session_id=session_id, session_repository=self, **kwargs)

    def _init_database(self):
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    session_id TEXT,
                    agent_id TEXT,
                    system_prompt TEXT,
                    state TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (session_id, agent_id),
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    session_id TEXT,
                    agent_id TEXT,
                    message_id INTEGER,
                    role TEXT,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (session_id, agent_id, message_id),
                    FOREIGN KEY (session_id, agent_id) REFERENCES agents(session_id, agent_id) ON DELETE CASCADE
                )
            """)

            # Index for faster queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_lookup
                ON messages(session_id, agent_id)
            """)

            conn.commit()

    # Session operations
    def create_session(self, session: Session, **kwargs: Any) -> Session:
        """Create a new session in the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO sessions (session_id, metadata) VALUES (?, ?)",
                (session.session_id, json.dumps(session.metadata or {}))
            )
            conn.commit()
        return session

    def read_session(self, session_id: str, **kwargs: Any) -> Session | None:
        """Read session data from database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT session_id, metadata FROM sessions WHERE session_id = ?",
                (session_id,)
            )
            row = cursor.fetchone()

            if row:
                return Session(
                    session_id=row[0],
                    metadata=json.loads(row[1]) if row[1] else {}
                )
        return None

    def delete_session(self, session_id: str, **kwargs: Any) -> None:
        """Delete session and all associated data."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            conn.commit()

    # Agent operations
    def create_agent(self, session_id: str, session_agent: SessionAgent, **kwargs: Any) -> None:
        """Create a new agent in the session."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT OR REPLACE INTO agents
                   (session_id, agent_id, system_prompt, state, metadata)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    session_id,
                    session_agent.agent_id,
                    session_agent.system_prompt,
                    json.dumps(session_agent.state),
                    json.dumps(session_agent.metadata or {})
                )
            )
            conn.commit()

    def read_agent(self, session_id: str, agent_id: str, **kwargs: Any) -> SessionAgent | None:
        """Read agent data from database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """SELECT agent_id, system_prompt, state, metadata
                   FROM agents
                   WHERE session_id = ? AND agent_id = ?""",
                (session_id, agent_id)
            )
            row = cursor.fetchone()

            if row:
                return SessionAgent(
                    agent_id=row[0],
                    system_prompt=row[1],
                    state=json.loads(row[2]) if row[2] else {},
                    metadata=json.loads(row[3]) if row[3] else {}
                )
        return None

    def update_agent(self, session_id: str, session_agent: SessionAgent, **kwargs: Any) -> None:
        """Update agent data in database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """UPDATE agents
                   SET system_prompt = ?, state = ?, metadata = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE session_id = ? AND agent_id = ?""",
                (
                    session_agent.system_prompt,
                    json.dumps(session_agent.state),
                    json.dumps(session_agent.metadata or {}),
                    session_id,
                    session_agent.agent_id
                )
            )
            conn.commit()

    # Message operations
    def create_message(
        self,
        session_id: str,
        agent_id: str,
        session_message: SessionMessage,
        **kwargs: Any
    ) -> None:
        """Create a new message for the agent."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO messages
                   (session_id, agent_id, message_id, role, content)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    session_id,
                    agent_id,
                    session_message.message_id,
                    session_message.role,
                    json.dumps(session_message.content)
                )
            )
            conn.commit()

    def read_message(
        self,
        session_id: str,
        agent_id: str,
        message_id: int,
        **kwargs: Any
    ) -> SessionMessage | None:
        """Read a specific message."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """SELECT message_id, role, content
                   FROM messages
                   WHERE session_id = ? AND agent_id = ? AND message_id = ?""",
                (session_id, agent_id, message_id)
            )
            row = cursor.fetchone()

            if row:
                return SessionMessage(
                    message_id=row[0],
                    role=row[1],
                    content=json.loads(row[2]) if row[2] else []
                )
        return None

    def update_message(
        self,
        session_id: str,
        agent_id: str,
        session_message: SessionMessage,
        **kwargs: Any
    ) -> None:
        """Update message data."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """UPDATE messages
                   SET role = ?, content = ?
                   WHERE session_id = ? AND agent_id = ? AND message_id = ?""",
                (
                    session_message.role,
                    json.dumps(session_message.content),
                    session_id,
                    agent_id,
                    session_message.message_id
                )
            )
            conn.commit()

    def list_messages(
        self,
        session_id: str,
        agent_id: str,
        limit: int | None = None,
        offset: int = 0,
        **kwargs: Any
    ) -> list[SessionMessage]:
        """List messages for an agent with pagination."""
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT message_id, role, content
                FROM messages
                WHERE session_id = ? AND agent_id = ?
                ORDER BY message_id
            """
            params: list[Any] = [session_id, agent_id]

            if limit is not None:
                query += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])

            cursor = conn.execute(query, params)
            return [
                SessionMessage(
                    message_id=row[0],
                    role=row[1],
                    content=json.loads(row[2]) if row[2] else []
                )
                for row in cursor.fetchall()
            ]

    # Multi-agent operations (optional, can return None if not needed)
    def create_multi_agent(self, session_id: str, multi_agent: Any, **kwargs: Any) -> None:
        """Create multi-agent state (not implemented)."""
        pass

    def read_multi_agent(self, session_id: str, multi_agent_id: str, **kwargs: Any) -> dict[str, Any] | None:
        """Read multi-agent state (not implemented)."""
        return None

    def update_multi_agent(self, session_id: str, multi_agent: Any, **kwargs: Any) -> None:
        """Update multi-agent state (not implemented)."""
        pass
