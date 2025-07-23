"""
SQLite database operations for the AI Agent Observability Tool.
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

from .models import (
    AgentSession, 
    Conversation, 
    Message,
    PerformanceMetrics,
    SystemEvent,
    AgentConfiguration
)

DATABASE_PATH = Path("data/observability.db")


def init_database():
    """Initialize the SQLite database with required tables."""
    DATABASE_PATH.parent.mkdir(exist_ok=True)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Agent sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_sessions (
                id TEXT PRIMARY KEY,
                agent_name TEXT NOT NULL,
                status TEXT NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                configuration TEXT,
                metadata TEXT
            )
        """)
        
        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                context TEXT,
                token_usage TEXT,
                FOREIGN KEY (session_id) REFERENCES agent_sessions (id)
            )
        """)
        
        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                metadata TEXT,
                tool_calls TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        """)
        
        # Performance metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                conversation_id TEXT,
                response_time_ms REAL NOT NULL,
                token_count_input INTEGER DEFAULT 0,
                token_count_output INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 1.0,
                error_count INTEGER DEFAULT 0,
                timestamp TIMESTAMP NOT NULL,
                resource_usage TEXT,
                quality_score REAL,
                FOREIGN KEY (session_id) REFERENCES agent_sessions (id),
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        """)
        
        # System events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_events (
                id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                session_id TEXT,
                conversation_id TEXT,
                message TEXT NOT NULL,
                details TEXT,
                timestamp TIMESTAMP NOT NULL,
                stack_trace TEXT,
                FOREIGN KEY (session_id) REFERENCES agent_sessions (id),
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        """)
        
        # Agent configurations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_configurations (
                id TEXT PRIMARY KEY,
                agent_name TEXT NOT NULL,
                model_parameters TEXT,
                system_prompt TEXT,
                tools TEXT,
                environment_variables TEXT,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_agent ON agent_sessions(agent_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_status ON agent_sessions(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_session ON performance_metrics(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_session ON system_events(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON system_events(event_type)")
        
        conn.commit()


@contextmanager
def get_connection():
    """Get database connection with proper context management."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


class DatabaseManager:
    """Database manager for handling CRUD operations."""
    
    # Agent Sessions
    def create_session(self, session: AgentSession) -> str:
        """Create a new agent session."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO agent_sessions 
                (id, agent_name, status, start_time, end_time, configuration, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session.id,
                session.agent_name,
                session.status.value if hasattr(session.status, 'value') else session.status,
                session.start_time,
                session.end_time,
                json.dumps(session.configuration),
                json.dumps(session.metadata)
            ))
            conn.commit()
            return session.id
    
    def get_session(self, session_id: str) -> Optional[AgentSession]:
        """Get session by ID."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agent_sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            
            if row:
                return AgentSession(
                    id=row['id'],
                    agent_name=row['agent_name'],
                    status=row['status'],
                    start_time=datetime.fromisoformat(row['start_time']),
                    end_time=datetime.fromisoformat(row['end_time']) if row['end_time'] else None,
                    configuration=json.loads(row['configuration']) if row['configuration'] else {},
                    metadata=json.loads(row['metadata']) if row['metadata'] else {}
                )
            return None
    
    def get_active_sessions(self) -> List[AgentSession]:
        """Get all active sessions."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agent_sessions WHERE status = 'active'")
            rows = cursor.fetchall()
            
            sessions = []
            for row in rows:
                sessions.append(AgentSession(
                    id=row['id'],
                    agent_name=row['agent_name'],
                    status=row['status'],
                    start_time=datetime.fromisoformat(row['start_time']),
                    end_time=datetime.fromisoformat(row['end_time']) if row['end_time'] else None,
                    configuration=json.loads(row['configuration']) if row['configuration'] else {},
                    metadata=json.loads(row['metadata']) if row['metadata'] else {}
                ))
            return sessions
    
    # Conversations
    def create_conversation(self, conversation: Conversation) -> str:
        """Create a new conversation."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversations 
                (id, session_id, start_time, end_time, context, token_usage)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                conversation.id,
                conversation.session_id,
                conversation.start_time,
                conversation.end_time,
                json.dumps(conversation.context),
                json.dumps(conversation.token_usage)
            ))
            conn.commit()
            return conversation.id
    
    def add_message(self, message: Message, conversation_id: str) -> str:
        """Add a message to a conversation."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages 
                (id, conversation_id, role, content, timestamp, metadata, tool_calls)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                message.id,
                conversation_id,
                message.role.value if hasattr(message.role, 'value') else message.role,
                message.content,
                message.timestamp,
                json.dumps(message.metadata),
                json.dumps(message.tool_calls) if message.tool_calls else None
            ))
            conn.commit()
            return message.id
    
    # Performance Metrics
    def add_metrics(self, metrics: PerformanceMetrics) -> str:
        """Add performance metrics."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO performance_metrics 
                (id, session_id, conversation_id, response_time_ms, token_count_input,
                 token_count_output, success_rate, error_count, timestamp,
                 resource_usage, quality_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.id,
                metrics.session_id,
                metrics.conversation_id,
                metrics.response_time_ms,
                metrics.token_count_input,
                metrics.token_count_output,
                metrics.success_rate,
                metrics.error_count,
                metrics.timestamp,
                json.dumps(metrics.resource_usage),
                metrics.quality_score
            ))
            conn.commit()
            return metrics.id
    
    def get_metrics_summary(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get performance metrics summary."""
        with get_connection() as conn:
            cursor = conn.cursor()
            
            where_clause = "WHERE session_id = ?" if session_id else ""
            params = (session_id,) if session_id else ()
            
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_requests,
                    AVG(response_time_ms) as avg_response_time,
                    AVG(success_rate) as avg_success_rate,
                    SUM(token_count_input) as total_input_tokens,
                    SUM(token_count_output) as total_output_tokens,
                    AVG(quality_score) as avg_quality_score
                FROM performance_metrics
                {where_clause}
            """, params)
            
            row = cursor.fetchone()
            return dict(row) if row else {}
    
    # System Events
    def add_event(self, event: SystemEvent) -> str:
        """Add a system event."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO system_events 
                (id, event_type, session_id, conversation_id, message, details,
                 timestamp, stack_trace)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.id,
                event.event_type.value if hasattr(event.event_type, 'value') else event.event_type,
                event.session_id,
                event.conversation_id,
                event.message,
                json.dumps(event.details),
                event.timestamp,
                event.stack_trace
            ))
            conn.commit()
            return event.id
    
    def get_recent_events(self, limit: int = 100) -> List[SystemEvent]:
        """Get recent system events."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM system_events 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            events = []
            for row in cursor.fetchall():
                events.append(SystemEvent(
                    id=row['id'],
                    event_type=row['event_type'],
                    session_id=row['session_id'],
                    conversation_id=row['conversation_id'],
                    message=row['message'],
                    details=json.loads(row['details']) if row['details'] else {},
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    stack_trace=row['stack_trace']
                ))
            return events


# Global database manager instance
db = DatabaseManager()