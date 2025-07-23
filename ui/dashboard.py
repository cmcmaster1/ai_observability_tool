"""
Live dashboard interface for real-time agent monitoring.
"""
import gradio as gr
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any

from core.database import db
from core.models import AgentStatus

def get_active_sessions_count() -> int:
    """Get count of active sessions."""
    sessions = db.get_active_sessions()
    return len(sessions)

def get_session_status_distribution() -> Dict[str, int]:
    """Get distribution of session statuses."""
    from core.database import get_connection
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM agent_sessions 
            GROUP BY status
        """)
        return {row['status']: row['count'] for row in cursor.fetchall()}

def create_metrics_chart():
    """Create performance metrics chart."""
    metrics_summary = db.get_metrics_summary()
    
    if not metrics_summary or not metrics_summary.get('total_requests'):
        # Return empty chart if no data
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color="gray")
        )
        fig.update_layout(
            title="Performance Metrics",
            xaxis_title="",
            yaxis_title="",
            height=400
        )
        return fig
    
    # Create metrics chart
    labels = ['Avg Response Time (ms)', 'Success Rate (%)', 'Total Requests']
    values = [
        metrics_summary.get('avg_response_time', 0) or 0,
        (metrics_summary.get('avg_success_rate', 0) or 0) * 100,
        metrics_summary.get('total_requests', 0) or 0
    ]
    
    fig = go.Figure(data=[
        go.Bar(x=labels, y=values, 
               marker_color=['lightblue', 'lightgreen', 'lightcoral'])
    ])
    
    fig.update_layout(
        title="Performance Metrics Overview",
        xaxis_title="Metrics",
        yaxis_title="Values",
        height=400
    )
    
    return fig

def create_session_status_chart():
    """Create session status distribution chart."""
    status_dist = get_session_status_distribution()
    
    if not status_dist:
        fig = go.Figure()
        fig.add_annotation(
            text="No sessions found",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color="gray")
        )
        fig.update_layout(title="Session Status Distribution", height=400)
        return fig
    
    fig = go.Figure(data=[
        go.Pie(labels=list(status_dist.keys()), 
               values=list(status_dist.values()),
               hole=0.3)
    ])
    
    fig.update_layout(
        title="Session Status Distribution",
        height=400
    )
    
    return fig

def get_recent_events_table():
    """Get recent events for display."""
    events = db.get_recent_events(limit=10)
    
    if not events:
        return pd.DataFrame({
            'Timestamp': [],
            'Type': [],
            'Message': [],
            'Session ID': []
        })
    
    data = []
    for event in events:
        data.append({
            'Timestamp': event.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'Type': event.event_type.upper(),
            'Message': event.message[:100] + '...' if len(event.message) > 100 else event.message,
            'Session ID': event.session_id[:8] + '...' if event.session_id else 'N/A'
        })
    
    return pd.DataFrame(data)

def refresh_dashboard():
    """Refresh dashboard data."""
    active_count = get_active_sessions_count()
    metrics_chart = create_metrics_chart()
    status_chart = create_session_status_chart()
    events_df = get_recent_events_table()
    
    return active_count, metrics_chart, status_chart, events_df

def create_dashboard():
    """Create the main dashboard interface."""
    with gr.Column():
        gr.Markdown("## Live Agent Monitoring")
        
        with gr.Row():
            active_sessions_display = gr.Number(
                label="Active Sessions", 
                value=0, 
                interactive=False
            )
            
            refresh_btn = gr.Button("Refresh Dashboard", variant="primary")
        
        with gr.Row():
            with gr.Column(scale=1):
                metrics_plot = gr.Plot(label="Performance Metrics")
            
            with gr.Column(scale=1):
                status_plot = gr.Plot(label="Session Status")
        
        gr.Markdown("### Recent Events")
        events_table = gr.Dataframe(
            label="System Events",
            headers=['Timestamp', 'Type', 'Message', 'Session ID'],
            interactive=False,
            wrap=True
        )
        
        # Set up refresh functionality
        refresh_btn.click(
            fn=refresh_dashboard,
            outputs=[active_sessions_display, metrics_plot, status_plot, events_table]
        )