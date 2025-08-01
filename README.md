# AI Agent Observability Tool

A comprehensive local AI agent observability tool built with Gradio for monitoring, debugging, and analyzing AI agent interactions in healthcare environments.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ai_observability_tool
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Run the application**:
   ```bash
   uv run python app.py
   ```

4. **Open your browser** to: http://localhost:7860

## ✨ Features

### 📊 Live Dashboard
- Real-time monitoring of active AI agents
- Performance metrics visualization with interactive charts
- Session status distribution and analytics
- Recent system events log with filtering capabilities

### 📈 Analytics
- Historical data analysis interface (coming soon)
- Performance trends over time with customizable date ranges
- Token usage analytics and cost tracking (coming soon)
- Conversation history export in multiple formats (coming soon)

### ⚙️ Configuration
- Agent settings management and validation
- Model parameter tuning and optimization
- System prompt configuration and versioning
- Tool and function management with dependency tracking

### 🐛 Debug Console
- System logs with advanced filtering and search
- Agent testing interface with custom scenarios
- Error simulation tools for testing resilience
- Quick diagnostic actions and health checks

## 📁 Project Structure

```
ai_observability_tool/
├── app.py                 # Main Gradio application
├── sample_data.py         # Sample data generator
├── run_test.py           # Test runner
├── test_app.py           # Application tests
├── pyproject.toml        # Project configuration
├── uv.lock              # Dependency lock file
├── README.md             # This file
├── CREWAI_INTEGRATION.md # CrewAI integration guide
├── QWEN.md              # QWEN model documentation
├── core/                 # Core functionality
│   ├── __init__.py
│   ├── models.py         # Data models and schemas
│   ├── database.py       # SQLite operations
│   ├── metrics.py        # Performance analytics (placeholder)
│   └── monitoring.py     # Real-time monitoring (placeholder)
├── ui/                   # User interface components
│   ├── __init__.py
│   ├── dashboard.py      # Live dashboard
│   ├── analytics.py      # Analytics interface
│   ├── config.py         # Configuration interface
│   └── debug.py          # Debug console
├── utils/                # Utility functions (placeholder)
│   ├── __init__.py
│   ├── logging.py        # Logging utilities (placeholder)
│   ├── security.py       # Security functions (placeholder)
│   └── export.py         # Data export tools (placeholder)
├── integrations/         # Third-party integrations
│   ├── __init__.py
│   └── crewai_integration.py
├── examples/             # Usage examples
│   ├── crewai_ehr_example.py
│   └── real_crewai_integration.py
└── tests/                # Test suite (placeholder)
    └── __init__.py
```

## 🔧 Sample Data

The tool comes with sample data for testing and demonstration. To regenerate sample data:

```bash
uv run python sample_data.py
```

This will populate the database with:
- Sample agent sessions
- Performance metrics
- Conversation histories
- System events

## 🔌 Integration

### With CrewAI

The tool provides seamless integration with CrewAI agents:

```python
from core.database import db
from core.models import AgentSession, PerformanceMetrics

# Track your CrewAI agent sessions
session = AgentSession(
    id="crew_session_123",
    agent_name="CrewAI Agent",
    status="active"
)
db.create_session(session)

# Log performance metrics
metrics = PerformanceMetrics(
    id="metrics_123",
    session_id="crew_session_123",
    response_time_ms=2500.0,
    token_count_input=500,
    token_count_output=1000,
    success_rate=0.95
)
db.add_metrics(metrics)
```

### With Custom Agents

The tool is framework-agnostic and can be integrated with any AI agent system. Simply use the database API to log:

- **Agent sessions**: Track agent lifecycle and status
- **Conversations and messages**: Store interaction history
- **Performance metrics**: Monitor response times, token usage, and success rates
- **System events**: Log errors, warnings, and informational events

## 🧪 Development

### Running Tests

```bash
uv run python run_test.py
```

### Development Dependencies

```bash
uv sync --dev
```

### Code Quality

The project follows Python best practices and includes:
- Type hints throughout the codebase
- Comprehensive error handling
- Security-focused design for healthcare environments
- Modular architecture for easy extension

## 🔒 Security

This project is built for healthcare AI observability and follows security best practices for clinical environments:

- **Data Encryption**: All sensitive data is encrypted at rest
- **Access Control**: Role-based access control for different user types
- **Audit Logging**: Comprehensive audit trails for compliance
- **HIPAA Compliance**: Designed with healthcare privacy regulations in mind

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📞 Support

If you encounter any issues or have questions, please:

1. Check the [Issues](https://github.com/your-repo/issues) page
2. Create a new issue with detailed information
3. Include logs and error messages when applicable

---

**Built with ❤️ for healthcare AI observability**