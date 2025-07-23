"""
CrewAI integration for the AI Agent Observability Tool.
This module provides seamless integration with CrewAI agents for EHR data processing.
"""
import uuid
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from contextlib import contextmanager

from core.database import db
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


class CrewAIObserver:
    """
    Observer class to monitor CrewAI agents and log to the observability tool.
    Designed for sensitive EHR data - all data stays local.
    """
    
    def __init__(self, project_name: str = "EHR Processing"):
        self.project_name = project_name
        self.active_sessions: Dict[str, str] = {}  # crew_id -> session_id
        self.conversation_contexts: Dict[str, str] = {}  # crew_id -> conversation_id
        
    def start_crew_session(self, 
                          crew_name: str,
                          agents: List[str],
                          tasks: List[str],
                          metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Start monitoring a CrewAI session.
        
        Args:
            crew_name: Name of the crew
            agents: List of agent names in the crew
            tasks: List of task descriptions
            metadata: Additional metadata (sanitized)
        
        Returns:
            Session ID for tracking
        """
        session_id = str(uuid.uuid4())
        crew_id = f"crew_{crew_name}_{int(time.time())}"
        
        # Sanitize metadata to remove any PII/PHI
        safe_metadata = self._sanitize_metadata(metadata or {})
        safe_metadata.update({
            "project": self.project_name,
            "agent_count": len(agents),
            "task_count": len(tasks),
            "agents": agents,  # Agent names should be safe
            "data_type": "EHR",
            "privacy_level": "HIPAA_COMPLIANT"
        })
        
        session = AgentSession(
            id=session_id,
            agent_name=f"CrewAI: {crew_name}",
            status=AgentStatus.ACTIVE,
            configuration={
                "framework": "CrewAI",
                "agents": agents,
                "task_descriptions": [self._sanitize_task_description(task) for task in tasks]
            },
            metadata=safe_metadata
        )
        
        db.create_session(session)
        self.active_sessions[crew_id] = session_id
        
        # Log start event
        self._log_event(
            session_id, 
            EventType.INFO, 
            f"Started CrewAI session: {crew_name}",
            {"agents": agents, "tasks_count": len(tasks)}
        )
        
        return session_id
    
    def log_agent_interaction(self,
                             crew_name: str,
                             agent_name: str,
                             task: str,
                             input_data: str,
                             response: str,
                             execution_time_ms: float,
                             token_usage: Optional[Dict[str, int]] = None):
        """
        Log an agent interaction (automatically sanitizes sensitive data).
        
        Args:
            crew_name: Name of the crew
            agent_name: Name of the specific agent
            task: Task description
            input_data: Input to the agent (will be sanitized)
            response: Agent response (will be sanitized)
            execution_time_ms: Execution time in milliseconds
            token_usage: Token usage statistics
        """
        session_id = self._get_session_id(crew_name)
        if not session_id:
            return
        
        # Create or get conversation
        conversation_id = self._get_or_create_conversation(session_id, agent_name, task)
        
        # Sanitize input and response for logging
        safe_input = self._sanitize_ehr_content(input_data)
        safe_response = self._sanitize_ehr_content(response)
        
        # Log user message (task input)
        user_message = Message(
            id=str(uuid.uuid4()),
            role=MessageRole.USER,
            content=f"Task: {self._sanitize_task_description(task)}\nInput: {safe_input}",
            metadata={
                "agent": agent_name,
                "task_type": self._classify_task(task),
                "data_classification": "SANITIZED_EHR"
            }
        )
        db.add_message(user_message, conversation_id)
        
        # Log agent response
        agent_message = Message(
            id=str(uuid.uuid4()),
            role=MessageRole.ASSISTANT,
            content=safe_response,
            metadata={
                "agent": agent_name,
                "execution_time_ms": execution_time_ms,
                "data_classification": "SANITIZED_EHR"
            }
        )
        db.add_message(agent_message, conversation_id)
        
        # Log performance metrics
        metrics = PerformanceMetrics(
            id=str(uuid.uuid4()),
            session_id=session_id,
            conversation_id=conversation_id,
            response_time_ms=execution_time_ms,
            token_count_input=token_usage.get('input', 0) if token_usage else 0,
            token_count_output=token_usage.get('output', 0) if token_usage else 0,
            success_rate=1.0,  # Assume success if we got here
            resource_usage={"agent": agent_name, "task_category": self._classify_task(task)}
        )
        db.add_metrics(metrics)
    
    def log_error(self, crew_name: str, agent_name: str, error: Exception, context: Dict[str, Any] = None):
        """Log an error that occurred during CrewAI execution."""
        session_id = self._get_session_id(crew_name)
        if not session_id:
            return
        
        safe_context = self._sanitize_metadata(context or {})
        
        error_event = SystemEvent(
            id=str(uuid.uuid4()),
            event_type=EventType.ERROR,
            session_id=session_id,
            message=f"Error in agent {agent_name}: {str(error)[:200]}...",
            details={
                "agent": agent_name,
                "error_type": type(error).__name__,
                "context": safe_context
            },
            stack_trace=str(error)[:1000]  # Truncate stack trace
        )
        db.add_event(error_event)
    
    def end_crew_session(self, crew_name: str, success: bool = True, summary: str = ""):
        """End a CrewAI session."""
        session_id = self._get_session_id(crew_name)
        if not session_id:
            return
        
        # Update session status
        session = db.get_session(session_id)
        if session:
            session.status = AgentStatus.IDLE if success else AgentStatus.ERROR
            session.end_time = datetime.utcnow()
            # Note: In a real implementation, you'd update the session in the database
        
        # Log completion event
        self._log_event(
            session_id,
            EventType.INFO if success else EventType.ERROR,
            f"Completed CrewAI session: {crew_name}",
            {
                "success": success,
                "summary": self._sanitize_ehr_content(summary)[:500]
            }
        )
        
        # Clean up tracking
        crew_id = f"crew_{crew_name}_{int(time.time())}"
        if crew_id in self.active_sessions:
            del self.active_sessions[crew_id]
    
    # Private helper methods
    
    def _get_session_id(self, crew_name: str) -> Optional[str]:
        """Get session ID for a crew name."""
        for crew_id, session_id in self.active_sessions.items():
            if crew_name in crew_id:
                return session_id
        return None
    
    def _get_or_create_conversation(self, session_id: str, agent_name: str, task: str) -> str:
        """Get or create a conversation for this agent and task."""
        conversation_key = f"{session_id}_{agent_name}_{self._classify_task(task)}"
        
        if conversation_key not in self.conversation_contexts:
            conversation_id = str(uuid.uuid4())
            conversation = Conversation(
                id=conversation_id,
                session_id=session_id,
                context={
                    "agent": agent_name,
                    "task_category": self._classify_task(task),
                    "data_type": "EHR_SANITIZED"
                }
            )
            db.create_conversation(conversation)
            self.conversation_contexts[conversation_key] = conversation_id
        
        return self.conversation_contexts[conversation_key]
    
    def _sanitize_ehr_content(self, content: str) -> str:
        """
        Sanitize EHR content by removing/masking sensitive information.
        This is a basic implementation - enhance based on your specific needs.
        """
        if not content:
            return ""
        
        # Basic patterns for common PHI/PII in EHR data
        import re
        
        # Patient identifiers
        content = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', content)  # SSN
        content = re.sub(r'\b\d{10,12}\b', '[MRN]', content)  # Medical record numbers
        content = re.sub(r'\b\d{1,2}/\d{1,2}/\d{4}\b', '[DATE]', content)  # Dates
        
        # Names (basic pattern - enhance as needed)
        content = re.sub(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', '[PATIENT_NAME]', content)
        
        # Phone numbers
        content = re.sub(r'\b\d{3}-\d{3}-\d{4}\b', '[PHONE]', content)
        
        # Email addresses
        content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', content)
        
        # Truncate if too long
        if len(content) > 500:
            content = content[:500] + "...[TRUNCATED]"
        
        return content
    
    def _sanitize_task_description(self, task: str) -> str:
        """Sanitize task descriptions to remove sensitive information."""
        # Remove specific patient references but keep task structure
        sanitized = self._sanitize_ehr_content(task)
        return sanitized[:200]  # Limit length
    
    def _classify_task(self, task: str) -> str:
        """Classify the type of task for categorization."""
        task_lower = task.lower()
        if 'analyze' in task_lower or 'review' in task_lower:
            return 'ANALYSIS'
        elif 'extract' in task_lower or 'parse' in task_lower:
            return 'EXTRACTION'
        elif 'summarize' in task_lower or 'summary' in task_lower:
            return 'SUMMARIZATION'
        elif 'validate' in task_lower or 'check' in task_lower:
            return 'VALIDATION'
        else:
            return 'GENERAL'
    
    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize metadata to remove sensitive information."""
        safe_metadata = {}
        for key, value in metadata.items():
            if key.lower() in ['patient_id', 'ssn', 'name', 'email', 'phone']:
                safe_metadata[key] = '[REDACTED]'
            elif isinstance(value, str):
                safe_metadata[key] = self._sanitize_ehr_content(value)
            else:
                safe_metadata[key] = value
        return safe_metadata
    
    def _log_event(self, session_id: str, event_type: EventType, message: str, details: Dict[str, Any]):
        """Log a system event."""
        event = SystemEvent(
            id=str(uuid.uuid4()),
            event_type=event_type,
            session_id=session_id,
            message=message,
            details=details
        )
        db.add_event(event)


@contextmanager
def monitor_crewai_task(observer: CrewAIObserver, crew_name: str, agent_name: str, task: str):
    """
    Context manager for monitoring a specific CrewAI task.
    
    Usage:
        observer = CrewAIObserver("EHR Analysis Project")
        with monitor_crewai_task(observer, "medical_crew", "analyzer", "Analyze patient data"):
            # Your CrewAI task execution here
            result = agent.execute(task)
    """
    start_time = time.time()
    try:
        yield
        execution_time = (time.time() - start_time) * 1000
        # Note: In actual usage, you'd log the successful completion here
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        observer.log_error(crew_name, agent_name, e, {"execution_time_ms": execution_time})
        raise


# Example usage class for CrewAI integration
class EHRCrewAIWrapper:
    """
    Wrapper class that demonstrates how to integrate with your CrewAI agents.
    """
    
    def __init__(self):
        self.observer = CrewAIObserver("EHR Processing Project")
    
    def start_ehr_analysis_crew(self, patient_data_refs: List[str]):
        """Start a CrewAI session for EHR analysis."""
        agents = ["Data Extractor", "Clinical Analyzer", "Report Generator"]
        tasks = [
            "Extract key medical information from EHR data",
            "Analyze extracted data for clinical insights", 
            "Generate summary report for clinical review"
        ]
        
        session_id = self.observer.start_crew_session(
            crew_name="EHR_Analysis_Crew",
            agents=agents,
            tasks=tasks,
            metadata={
                "patient_count": len(patient_data_refs),
                "analysis_type": "clinical_summary",
                "compliance": "HIPAA"
            }
        )
        
        return session_id
    
    def process_with_monitoring(self, crew_name: str, agent_name: str, task: str, input_data: str):
        """
        Example of how to process data with monitoring.
        Replace with your actual CrewAI execution logic.
        """
        start_time = time.time()
        
        try:
            # This is where you'd call your actual CrewAI agent
            # For example:
            # result = your_crewai_agent.execute(input_data)
            
            # Simulated processing
            result = f"Processed {len(input_data)} characters of EHR data"
            execution_time = (time.time() - start_time) * 1000
            
            # Log the interaction
            self.observer.log_agent_interaction(
                crew_name=crew_name,
                agent_name=agent_name,
                task=task,
                input_data=input_data,
                response=result,
                execution_time_ms=execution_time,
                token_usage={"input": 150, "output": 50}  # Your actual token counts
            )
            
            return result
            
        except Exception as e:
            self.observer.log_error(crew_name, agent_name, e)
            raise