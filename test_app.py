"""
Test script to validate the Gradio application can start.
"""
import gradio as gr
from ui.dashboard import create_dashboard
from ui.analytics import create_analytics
from ui.config import create_config
from ui.debug import create_debug
from core.database import init_database

def test_gradio_app():
    """Test that the Gradio app can be created without errors."""
    print("Initializing database...")
    init_database()
    print("Database initialized successfully!")
    
    print("Creating Gradio interface...")
    
    with gr.Blocks(title="AI Agent Observability Tool", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# AI Agent Observability Tool")
        gr.Markdown("Monitor, debug, and analyze AI agent interactions locally")
        
        with gr.Tabs():
            with gr.Tab("Live Dashboard"):
                create_dashboard()
            
            with gr.Tab("Analytics"):
                create_analytics()
            
            with gr.Tab("Configuration"):
                create_config()
            
            with gr.Tab("Debug Console"):
                create_debug()
    
    print("Gradio interface created successfully!")
    print("Interface components:")
    print(f"- Blocks: {len(demo.blocks)} components")
    print("Test completed successfully!")
    
    return demo

if __name__ == "__main__":
    demo = test_gradio_app()
    print("All tests passed! App is ready to run.")