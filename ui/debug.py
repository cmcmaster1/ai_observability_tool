"""
Debug console interface for troubleshooting and testing.
"""
import gradio as gr
import json
from datetime import datetime

from core.database import db
from core.models import SystemEvent, EventType

def create_debug():
    """Create the debug console interface."""
    with gr.Column():
        gr.Markdown("## Debug Console")
        
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("### System Logs")
                
                log_level_filter = gr.Dropdown(
                    label="Log Level Filter",
                    choices=["ALL", "ERROR", "WARNING", "INFO", "DEBUG"],
                    value="ALL"
                )
                
                log_output = gr.Textbox(
                    label="Log Output",
                    lines=15,
                    interactive=False,
                    max_lines=50
                )
                
                with gr.Row():
                    refresh_logs_btn = gr.Button("Refresh Logs", variant="primary")
                    clear_logs_btn = gr.Button("Clear Logs", variant="secondary")
            
            with gr.Column(scale=1):
                gr.Markdown("### Test Agent")
                
                test_prompt = gr.Textbox(
                    label="Test Prompt",
                    lines=5,
                    placeholder="Enter test prompt for agent..."
                )
                
                test_agent_btn = gr.Button("Send Test Message", variant="primary")
                
                test_result = gr.Textbox(
                    label="Response",
                    lines=8,
                    interactive=False
                )
                
                gr.Markdown("### Quick Actions")
                
                with gr.Column():
                    simulate_error_btn = gr.Button("Simulate Error", variant="stop")
                    create_test_session_btn = gr.Button("Create Test Session")
                    export_debug_btn = gr.Button("Export Debug Data")
        
        def refresh_logs(level_filter):
            """Refresh the log display."""
            events = db.get_recent_events(limit=50)
            
            if not events:
                return "No logs available"
            
            log_lines = []
            for event in events:
                if level_filter != "ALL" and event.event_type.upper() != level_filter:
                    continue
                
                timestamp = event.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                level = event.event_type.upper()
                message = event.message
                session_info = f" [Session: {event.session_id[:8]}...]" if event.session_id else ""
                
                log_lines.append(f"[{timestamp}] {level}: {message}{session_info}")
            
            return "\n".join(log_lines) if log_lines else f"No {level_filter} logs found"
        
        def clear_logs():
            """Clear the log display."""
            return "Logs cleared (display only - database logs preserved)"
        
        def test_agent(prompt):
            """Test the agent with a prompt."""
            if not prompt.strip():
                return "Please enter a test prompt"
            
            # Simulate agent response (placeholder)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return f"[{timestamp}] Test response to: {prompt}\n\nThis is a simulated response. In a real implementation, this would connect to your AI agent."
        
        def simulate_error():
            """Simulate an error for testing."""
            # Create a test error event
            error_event = SystemEvent(
                id=f"debug_error_{datetime.now().timestamp()}",
                event_type=EventType.ERROR,
                message="Simulated error for debugging purposes",
                details={"source": "debug_console", "test": True},
                stack_trace="Traceback (simulated):\n  File 'debug.py', line 42, in simulate_error\n    raise Exception('Test error')"
            )
            
            db.add_event(error_event)
            return "Error event simulated and logged"
        
        def create_test_session():
            """Create a test session."""
            from core.models import AgentSession, AgentStatus
            import uuid
            
            test_session = AgentSession(
                id=str(uuid.uuid4()),
                agent_name="Debug Test Agent",
                status=AgentStatus.ACTIVE,
                metadata={"created_by": "debug_console", "test": True}
            )
            
            db.create_session(test_session)
            return f"Test session created: {test_session.id[:8]}..."
        
        def export_debug_data():
            """Export debug data."""
            return "Debug data export feature coming soon"
        
        # Event handlers
        refresh_logs_btn.click(
            fn=refresh_logs,
            inputs=[log_level_filter],
            outputs=[log_output]
        )
        
        clear_logs_btn.click(
            fn=clear_logs,
            outputs=[log_output]
        )
        
        test_agent_btn.click(
            fn=test_agent,
            inputs=[test_prompt],
            outputs=[test_result]
        )
        
        simulate_error_btn.click(
            fn=simulate_error,
            outputs=[test_result]
        )
        
        create_test_session_btn.click(
            fn=create_test_session,
            outputs=[test_result]
        )
        
        export_debug_btn.click(
            fn=export_debug_data,
            outputs=[test_result]
        )
        
        # Initial log load
        log_output.value = refresh_logs("ALL")