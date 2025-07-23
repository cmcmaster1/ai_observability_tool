"""
Script to add sample data for testing the observability tool.
"""
import uuid
from datetime import datetime, timedelta

from core.database import init_database, db
from core.models import (
    AgentSession, 
    AgentStatus, 
    Conversation, 
    Message, 
    MessageRole,
    PerformanceMetrics,
    SystemEvent,
    EventType
)

def create_sample_data():
    """Create sample data for testing."""
    print("Creating sample data...")
    
    # Initialize database
    init_database()
    
    # Create sample sessions
    session1 = AgentSession(
        id=str(uuid.uuid4()),
        agent_name="Healthcare Assistant",
        status=AgentStatus.ACTIVE,
        start_time=datetime.now() - timedelta(hours=2),
        configuration={
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2048
        },
        metadata={"environment": "production", "version": "1.0"}
    )
    
    session2 = AgentSession(
        id=str(uuid.uuid4()),
        agent_name="Document Analyzer",
        status=AgentStatus.IDLE,
        start_time=datetime.now() - timedelta(hours=1),
        end_time=datetime.now() - timedelta(minutes=30),
        configuration={
            "model": "claude-3",
            "temperature": 0.5,
            "max_tokens": 4096
        },
        metadata={"environment": "staging", "version": "1.1"}
    )
    
    session3 = AgentSession(
        id=str(uuid.uuid4()),
        agent_name="Data Processor",
        status=AgentStatus.ERROR,
        start_time=datetime.now() - timedelta(minutes=45),
        configuration={
            "model": "gpt-3.5-turbo",
            "temperature": 0.3,
            "max_tokens": 1024
        },
        metadata={"environment": "development", "version": "0.9"}
    )
    
    # Save sessions
    db.create_session(session1)
    db.create_session(session2)
    db.create_session(session3)
    print(f"Created sessions: {session1.id[:8]}, {session2.id[:8]}, {session3.id[:8]}")
    
    # Create sample conversations
    conv1 = Conversation(
        id=str(uuid.uuid4()),
        session_id=session1.id,
        start_time=datetime.now() - timedelta(hours=1, minutes=30),
        context={"user_id": "user123", "topic": "medical_consultation"},
        token_usage={"input": 150, "output": 200}
    )
    
    conv2 = Conversation(
        id=str(uuid.uuid4()),
        session_id=session2.id,
        start_time=datetime.now() - timedelta(minutes=50),
        end_time=datetime.now() - timedelta(minutes=35),
        context={"document_type": "medical_report", "analysis_type": "summary"},
        token_usage={"input": 500, "output": 300}
    )
    
    db.create_conversation(conv1)
    db.create_conversation(conv2)
    print(f"Created conversations: {conv1.id[:8]}, {conv2.id[:8]}")
    
    # Add sample messages
    messages = [
        Message(
            id=str(uuid.uuid4()),
            role=MessageRole.USER,
            content="What are the common symptoms of hypertension?",
            timestamp=datetime.now() - timedelta(hours=1, minutes=25),
            metadata={"source": "web_interface"}
        ),
        Message(
            id=str(uuid.uuid4()),
            role=MessageRole.ASSISTANT,
            content="Common symptoms of hypertension include headaches, shortness of breath, nosebleeds, and dizziness. However, many people with high blood pressure have no symptoms at all.",
            timestamp=datetime.now() - timedelta(hours=1, minutes=24),
            metadata={"model_used": "gpt-4", "confidence": 0.95}
        ),
        Message(
            id=str(uuid.uuid4()),
            role=MessageRole.USER,
            content="Can you analyze this medical report for key findings?",
            timestamp=datetime.now() - timedelta(minutes=48),
            metadata={"file_uploaded": "report_123.pdf"}
        )
    ]
    
    for i, msg in enumerate(messages):
        conv_id = conv1.id if i < 2 else conv2.id
        db.add_message(msg, conv_id)
    print(f"Added {len(messages)} sample messages")
    
    # Add performance metrics
    metrics = [
        PerformanceMetrics(
            id=str(uuid.uuid4()),
            session_id=session1.id,
            conversation_id=conv1.id,
            response_time_ms=1250.5,
            token_count_input=150,
            token_count_output=200,
            success_rate=1.0,
            quality_score=0.92,
            resource_usage={"cpu_usage": 15.2, "memory_mb": 128}
        ),
        PerformanceMetrics(
            id=str(uuid.uuid4()),
            session_id=session2.id,
            conversation_id=conv2.id,
            response_time_ms=890.2,
            token_count_input=500,
            token_count_output=300,
            success_rate=1.0,
            quality_score=0.88,
            resource_usage={"cpu_usage": 22.1, "memory_mb": 256}
        ),
        PerformanceMetrics(
            id=str(uuid.uuid4()),
            session_id=session3.id,
            response_time_ms=5000.0,
            token_count_input=50,
            token_count_output=0,
            success_rate=0.0,
            error_count=1,
            resource_usage={"cpu_usage": 45.8, "memory_mb": 512}
        )
    ]
    
    for metric in metrics:
        db.add_metrics(metric)
    print(f"Added {len(metrics)} performance metrics")
    
    # Add system events
    events = [
        SystemEvent(
            id=str(uuid.uuid4()),
            event_type=EventType.INFO,
            session_id=session1.id,
            message="Agent session started successfully",
            details={"startup_time_ms": 450}
        ),
        SystemEvent(
            id=str(uuid.uuid4()),
            event_type=EventType.WARNING,
            session_id=session2.id,
            message="High token usage detected",
            details={"token_count": 800, "threshold": 500}
        ),
        SystemEvent(
            id=str(uuid.uuid4()),
            event_type=EventType.ERROR,
            session_id=session3.id,
            message="Connection timeout to external API",
            details={"api_endpoint": "https://api.example.com", "timeout_ms": 5000},
            stack_trace="TimeoutError: Request timed out after 5000ms"
        ),
        SystemEvent(
            id=str(uuid.uuid4()),
            event_type=EventType.DEBUG,
            message="System health check completed",
            details={"memory_usage": "512MB", "cpu_usage": "15%", "active_connections": 3}
        )
    ]
    
    for event in events:
        db.add_event(event)
    print(f"Added {len(events)} system events")
    
    print("Sample data creation completed!")

if __name__ == "__main__":
    create_sample_data()