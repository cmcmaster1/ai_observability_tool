"""
Example implementation showing how to integrate the observability tool 
with CrewAI agents processing sensitive EHR data.

This example demonstrates:
1. Setting up monitoring for CrewAI agents
2. Automatic data sanitization for HIPAA compliance
3. Real-time observability of EHR processing workflows
4. Local-only data storage for privacy
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.crewai_integration import CrewAIObserver, monitor_crewai_task, EHRCrewAIWrapper
import time
import random

def simulate_ehr_processing():
    """
    Simulate a CrewAI workflow processing EHR data.
    Replace with your actual CrewAI implementation.
    """
    print("🏥 Starting EHR Processing with CrewAI + Observability")
    print("="*60)
    
    # Initialize the observer
    observer = CrewAIObserver("EHR Clinical Analysis Project")
    
    # Define your CrewAI agents and tasks
    crew_name = "Clinical_Analysis_Crew"
    agents = [
        "Medical_Data_Extractor",
        "Clinical_Analyzer", 
        "Report_Generator",
        "Compliance_Checker"
    ]
    
    tasks = [
        "Extract patient demographics and medical history from EHR",
        "Analyze clinical data for patterns and insights",
        "Generate clinical summary report",
        "Validate HIPAA compliance and data accuracy"
    ]
    
    # Start monitoring the CrewAI session
    session_id = observer.start_crew_session(
        crew_name=crew_name,
        agents=agents,
        tasks=tasks,
        metadata={
            "hospital": "General Hospital",
            "department": "Cardiology",
            "analysis_type": "risk_assessment",
            "patient_cohort_size": 150
        }
    )
    
    print(f"✅ Started monitoring session: {session_id[:8]}...")
    
    # Simulate processing each task with different agents
    sample_ehr_data = [
        "Patient presents with chest pain, history of hypertension...",
        "Lab results show elevated cardiac enzymes...", 
        "Imaging reveals coronary artery narrowing...",
        "Medication list includes ACE inhibitors..."
    ]
    
    for i, (agent, task) in enumerate(zip(agents, tasks)):
        print(f"\n🤖 {agent} processing: {task[:50]}...")
        
        # Simulate task execution with monitoring
        start_time = time.time()
        
        try:
            # This is where your actual CrewAI agent would execute
            # For demonstration, we'll simulate processing
            input_data = sample_ehr_data[i % len(sample_ehr_data)]
            
            # Simulate processing time
            processing_time = random.uniform(0.5, 3.0)
            time.sleep(processing_time / 10)  # Speed up for demo
            
            # Simulate agent response
            if "Extract" in task:
                response = "Extracted: Patient demographics, medical history, current medications"
            elif "Analyze" in task:
                response = "Analysis: High cardiovascular risk, recommend intervention"
            elif "Generate" in task:
                response = "Report: Clinical summary generated with recommendations"
            else:
                response = "Compliance: HIPAA requirements validated, data secure"
            
            execution_time = (time.time() - start_time) * 1000
            
            # Log the interaction (automatically sanitizes sensitive data)
            observer.log_agent_interaction(
                crew_name=crew_name,
                agent_name=agent,
                task=task,
                input_data=input_data,
                response=response,
                execution_time_ms=execution_time,
                token_usage={"input": random.randint(100, 500), "output": random.randint(50, 300)}
            )
            
            print(f"   ⏱️  Completed in {execution_time:.1f}ms")
            
            # Simulate occasional errors for demonstration
            if random.random() < 0.1:  # 10% chance of error
                raise Exception(f"Simulated processing error in {agent}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            observer.log_error(crew_name, agent, e, {"task": task})
    
    # Complete the session
    observer.end_crew_session(
        crew_name=crew_name, 
        success=True,
        summary="Successfully analyzed EHR data for 150 patients, generated clinical insights"
    )
    
    print(f"\n✅ CrewAI session completed! Session ID: {session_id[:8]}...")
    print("\n📊 View results in the observability dashboard at: http://localhost:7860")
    print("   - Go to 'Live Dashboard' tab to see real-time metrics")
    print("   - Check 'Debug Console' for detailed logs")
    print("   - All sensitive data has been automatically sanitized")


def demonstrate_context_manager():
    """Demonstrate using the context manager for task monitoring."""
    print("\n🔧 Demonstrating Context Manager Usage")
    print("="*40)
    
    observer = CrewAIObserver("EHR Data Pipeline")
    
    # Start a session
    session_id = observer.start_crew_session(
        crew_name="Data_Pipeline",
        agents=["ETL_Agent"],
        tasks=["Process patient data batch"]
    )
    
    # Use context manager for automatic error handling
    try:
        with monitor_crewai_task(observer, "Data_Pipeline", "ETL_Agent", "Process batch"):
            print("   🔄 Processing EHR data batch...")
            time.sleep(0.1)  # Simulate work
            print("   ✅ Batch processed successfully")
    except Exception as e:
        print(f"   ❌ Error caught and logged: {e}")
    
    observer.end_crew_session("Data_Pipeline", success=True)
    print("   📝 All activities logged to observability tool")


if __name__ == "__main__":
    # Ensure the observability database is initialized
    from core.database import init_database
    init_database()
    
    # Run the demonstrations
    simulate_ehr_processing()
    demonstrate_context_manager()
    
    print("\n🎉 Integration demo complete!")
    print("💡 Next steps:")
    print("   1. Replace simulation code with your actual CrewAI agents")
    print("   2. Customize data sanitization rules for your EHR format")
    print("   3. Run your observability tool: uv run python app.py")
    print("   4. Process EHR data while monitoring in real-time")
    print("\n🔒 Privacy: All data remains local, no external connections made")