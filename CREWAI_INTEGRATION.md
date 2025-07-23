# CrewAI Integration Guide for EHR Data Processing

## 🏥 Overview

This guide shows you how to integrate the AI Agent Observability Tool with your CrewAI agents processing sensitive EHR data. Everything stays **100% local** - no data leaves your environment.

## 🔒 Privacy & Security Features

- **Local-only**: All data stored in local SQLite database
- **Automatic sanitization**: PHI/PII automatically masked in logs
- **HIPAA-compliant**: Designed for healthcare data processing
- **No external connections**: Zero risk of data exposure

## 🚀 Quick Integration

### 1. Basic Setup

```python
from integrations.crewai_integration import CrewAIObserver

# Initialize observer for your EHR project
observer = CrewAIObserver("Your EHR Project Name")

# Start monitoring a CrewAI crew
session_id = observer.start_crew_session(
    crew_name="medical_analysis_crew",
    agents=["data_extractor", "clinical_analyzer", "report_generator"],
    tasks=["Extract EHR data", "Analyze patterns", "Generate reports"],
    metadata={"department": "cardiology", "patient_count": 100}
)
```

### 2. Monitor Agent Interactions

```python
# Before each agent execution
start_time = time.time()

# Your CrewAI agent execution
result = your_crewai_agent.execute(patient_data)

# Log the interaction (automatically sanitizes sensitive data)
execution_time = (time.time() - start_time) * 1000
observer.log_agent_interaction(
    crew_name="medical_analysis_crew",
    agent_name="clinical_analyzer", 
    task="Analyze patient vitals",
    input_data=patient_data,  # Will be sanitized automatically
    response=result,          # Will be sanitized automatically  
    execution_time_ms=execution_time,
    token_usage={"input": 150, "output": 75}
)
```

### 3. Error Handling

```python
try:
    result = your_crewai_agent.execute(data)
except Exception as e:
    # Automatically log errors with context
    observer.log_error("medical_analysis_crew", "clinical_analyzer", e)
    raise
```

### 4. Session Cleanup

```python
# When your CrewAI work is complete
observer.end_crew_session(
    crew_name="medical_analysis_crew",
    success=True,
    summary="Processed 100 patient records successfully"
)
```

## 🔧 Advanced Integration

### Context Manager for Tasks

```python
from integrations.crewai_integration import monitor_crewai_task

with monitor_crewai_task(observer, "crew_name", "agent_name", "task"):
    # Your CrewAI task execution
    result = agent.execute(task_data)
    # Errors automatically logged if they occur
```

### Custom Data Sanitization

Customize the sanitization rules for your specific EHR format:

```python
class MyEHRObserver(CrewAIObserver):
    def _sanitize_ehr_content(self, content: str) -> str:
        """Custom sanitization for your EHR format."""
        content = super()._sanitize_ehr_content(content)
        
        # Add your specific patterns
        content = re.sub(r'Patient ID: \d+', 'Patient ID: [REDACTED]', content)
        content = re.sub(r'Room: \d+[A-Z]', 'Room: [ROOM]', content)
        
        return content
```

## 📊 Real-time Monitoring

### 1. Start the Observability Tool

```bash
cd ai_observability_tool
uv run python app.py
```

### 2. Open Dashboard

Navigate to: http://localhost:7860

### 3. Monitor Your CrewAI Agents

- **Live Dashboard**: See active sessions, performance metrics
- **Debug Console**: View logs, test agents, simulate errors
- **Analytics**: Historical analysis of your EHR processing

## 🏥 Example: Medical Records Processing

```python
# Complete example for EHR processing
import time
from integrations.crewai_integration import CrewAIObserver

# Initialize for medical project
observer = CrewAIObserver("Medical Records Analysis")

# Start crew for patient data analysis
session_id = observer.start_crew_session(
    crew_name="patient_analysis_crew",
    agents=["record_parser", "clinical_analyzer", "risk_assessor"],
    tasks=[
        "Parse patient medical records",
        "Analyze clinical indicators", 
        "Assess risk factors"
    ],
    metadata={
        "department": "Emergency Medicine",
        "shift": "night_shift",
        "urgency": "routine_analysis"
    }
)

# Process each patient record
for patient_record in patient_records:
    start_time = time.time()
    
    try:
        # Your CrewAI processing
        parsed_data = record_parser.execute(patient_record)
        clinical_analysis = clinical_analyzer.execute(parsed_data)
        risk_assessment = risk_assessor.execute(clinical_analysis)
        
        execution_time = (time.time() - start_time) * 1000
        
        # Log the complete workflow
        observer.log_agent_interaction(
            crew_name="patient_analysis_crew",
            agent_name="workflow_complete",
            task="Complete patient analysis pipeline",
            input_data=str(patient_record),
            response=f"Risk Score: {risk_assessment.score}",
            execution_time_ms=execution_time,
            token_usage={"input": 200, "output": 100}
        )
        
    except Exception as e:
        observer.log_error("patient_analysis_crew", "workflow", e)

# Complete the session
observer.end_crew_session(
    crew_name="patient_analysis_crew",
    success=True,
    summary=f"Analyzed {len(patient_records)} patient records"
)
```

## 🔍 Data Sanitization Features

The integration automatically sanitizes:

- **SSNs**: `123-45-6789` → `[SSN]`
- **Dates**: `01/15/2024` → `[DATE]`
- **Names**: `John Smith` → `[PATIENT_NAME]`
- **Phone**: `555-123-4567` → `[PHONE]`
- **Email**: `patient@email.com` → `[EMAIL]`
- **Medical Record Numbers**: `MRN12345` → `[MRN]`

## 📈 Monitoring Dashboard Features

### Live Dashboard
- Active CrewAI sessions
- Real-time performance metrics
- Token usage tracking
- Error rate monitoring

### Debug Console  
- Filtered log viewing
- Agent testing interface
- Error simulation
- Performance analysis

### Analytics
- Historical performance trends
- Agent efficiency comparison
- Task completion patterns
- Resource utilization

## 🚨 Compliance Notes

- **HIPAA-Ready**: Automatic PHI sanitization
- **Local Storage**: No cloud dependencies
- **Audit Trail**: Complete activity logging
- **Access Control**: Local-only access
- **Data Retention**: Configurable retention policies

## 🔧 Testing the Integration

Run the example to see it in action:

```bash
cd ai_observability_tool
uv run python examples/crewai_ehr_example.py
```

This demonstrates:
- CrewAI session monitoring
- Automatic data sanitization
- Error handling
- Real-time observability

## 📋 Integration Checklist

- [ ] Install observability tool: `uv sync`
- [ ] Import CrewAI integration: `from integrations.crewai_integration import CrewAIObserver`
- [ ] Initialize observer with project name
- [ ] Wrap CrewAI agents with monitoring calls
- [ ] Test data sanitization with sample EHR data
- [ ] Start observability dashboard: `uv run python app.py`
- [ ] Verify all data stays local (check network connections)
- [ ] Customize sanitization rules for your EHR format
- [ ] Set up error handling and logging

## 💡 Best Practices

1. **Session Management**: Start/end sessions for each CrewAI workflow
2. **Error Logging**: Always log exceptions for debugging
3. **Data Classification**: Tag sensitive vs. non-sensitive operations
4. **Performance Tracking**: Monitor execution times and token usage
5. **Regular Monitoring**: Check dashboard during EHR processing
6. **Custom Sanitization**: Adapt rules to your specific data format

## 🆘 Troubleshooting

**Q: Data not appearing in dashboard?**
A: Ensure `init_database()` is called and check session IDs match

**Q: Sensitive data visible in logs?**
A: Review and enhance `_sanitize_ehr_content()` method for your data format

**Q: Performance issues?**
A: Check database indexes and consider batch logging for high-volume processing

**Q: Integration with existing CrewAI code?**
A: Use the context manager approach for minimal code changes