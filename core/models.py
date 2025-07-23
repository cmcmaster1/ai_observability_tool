"""
Pydantic data models for the AI Agent Observability Tool.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    """Agent status enumeration."""
    ACTIVE = "active"
    IDLE = "idle"
    ERROR = "error"
    OFFLINE = "offline"


class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class EventType(str, Enum):
    """Event type enumeration."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"


class AgentSession(BaseModel):
    """Agent session data model."""
    id: str = Field(..., description="Unique session identifier")
    agent_name: str = Field(..., description="Name of the agent")
    status: AgentStatus = Field(default=AgentStatus.ACTIVE)
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    configuration: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


class Message(BaseModel):
    """Individual message within a conversation."""
    id: str = Field(..., description="Unique message identifier")
    role: MessageRole = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tool_calls: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        use_enum_values = True


class Conversation(BaseModel):
    """Conversation data model."""
    id: str = Field(..., description="Unique conversation identifier")
    session_id: str = Field(..., description="Associated session ID")
    messages: List[Message] = Field(default_factory=list)
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    token_usage: Dict[str, int] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


class PerformanceMetrics(BaseModel):
    """Performance metrics data model."""
    id: str = Field(..., description="Unique metrics identifier")
    session_id: str = Field(..., description="Associated session ID")
    conversation_id: Optional[str] = None
    response_time_ms: float = Field(..., description="Response time in milliseconds")
    token_count_input: int = Field(default=0)
    token_count_output: int = Field(default=0)
    success_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    error_count: int = Field(default=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    resource_usage: Dict[str, Any] = Field(default_factory=dict)
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class SystemEvent(BaseModel):
    """System event data model."""
    id: str = Field(..., description="Unique event identifier")
    event_type: EventType = Field(..., description="Type of event")
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None
    message: str = Field(..., description="Event message")
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    stack_trace: Optional[str] = None
    
    class Config:
        use_enum_values = True


class AgentConfiguration(BaseModel):
    """Agent configuration data model."""
    id: str = Field(..., description="Unique configuration identifier")
    agent_name: str = Field(..., description="Name of the agent")
    model_parameters: Dict[str, Any] = Field(default_factory=dict)
    system_prompt: Optional[str] = None
    tools: List[str] = Field(default_factory=list)
    environment_variables: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)


class ExportRequest(BaseModel):
    """Data export request model."""
    format: str = Field(..., description="Export format (csv, json, pdf)")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    session_ids: Optional[List[str]] = None
    include_conversations: bool = Field(default=True)
    include_metrics: bool = Field(default=True)
    include_events: bool = Field(default=True)
    anonymize_data: bool = Field(default=False)