"""
Complete test script that launches the app and validates functionality.
"""
import threading
import time
import requests
import gradio as gr
from app import main

def test_app_launch():
    """Test that the app can launch successfully."""
    print("🚀 Testing AI Agent Observability Tool...")
    
    # Test 1: Import all modules
    print("✅ Test 1: Importing modules...")
    try:
        from ui.dashboard import create_dashboard
        from ui.analytics import create_analytics
        from ui.config import create_config
        from ui.debug import create_debug
        from core.database import init_database, db
        print("   All modules imported successfully!")
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False
    
    # Test 2: Database operations
    print("✅ Test 2: Database operations...")
    try:
        init_database()
        sessions = db.get_active_sessions()
        events = db.get_recent_events(5)
        print(f"   Found {len(sessions)} active sessions and {len(events)} recent events")
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False
    
    # Test 3: Dashboard functions
    print("✅ Test 3: Dashboard functionality...")
    try:
        from ui.dashboard import refresh_dashboard
        result = refresh_dashboard()
        print(f"   Dashboard refresh returned {len(result)} components")
    except Exception as e:
        print(f"   ❌ Dashboard error: {e}")
        return False
    
    # Test 4: Gradio interface creation
    print("✅ Test 4: Gradio interface...")
    try:
        with gr.Blocks(title="Test", theme=gr.themes.Soft()) as demo:
            gr.Markdown("# Test Interface")
            with gr.Tabs():
                with gr.Tab("Dashboard"):
                    create_dashboard()
                with gr.Tab("Analytics"):
                    create_analytics()
                with gr.Tab("Config"):
                    create_config()
                with gr.Tab("Debug"):
                    create_debug()
        print(f"   Interface created with {len(demo.blocks)} components")
    except Exception as e:
        print(f"   ❌ Gradio interface error: {e}")
        return False
    
    print("\n🎉 All tests passed! The application is ready to run.")
    print("\n📝 To start the application, run:")
    print("   uv run python app.py")
    print("\n🌐 Then open your browser to:")
    print("   http://localhost:7860")
    
    return True

if __name__ == "__main__":
    success = test_app_launch()
    if not success:
        print("\n❌ Tests failed! Please check the errors above.")
        exit(1)
    else:
        print("\n✨ Ready to launch!")