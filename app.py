"""
Main Gradio application for AI Agent Observability Tool.
"""
import gradio as gr
from ui.dashboard import create_dashboard
from ui.analytics import create_analytics
from ui.config import create_config
from ui.debug import create_debug
from core.database import init_database

def main():
    """Initialize and launch the Gradio application."""
    print("🚀 Starting AI Agent Observability Tool...")
    
    # Initialize database
    print("📊 Initializing database...")
    init_database()
    print("✅ Database ready!")
    
    print("🎨 Creating user interface...")
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
    
    print("✅ Interface ready!")
    print("🌐 Launching application...")
    print("📱 Access your tool at: http://localhost:7860")
    print("⏹️  Press Ctrl+C to stop the server")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=False,
        show_error=True
    )

if __name__ == "__main__":
    main()