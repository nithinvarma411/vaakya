# Vaakya - Intelligent Voice Assistant & AI Agent Platform

🎙️ **Advanced voice transcription and AI-powered task automation platform** with cross-platform capabilities, local processing, and intelligent function calling.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com)
[![Ruff](https://img.shields.io/badge/Code%20Quality-Ruff-orange.svg)](https://github.com/astral-sh/ruff)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 What Vaakya Can Do

### 🎤 **Voice Transcription**
- **Local Speech-to-Text**: Powered by Faster-Whisper with no internet dependency
- **Real-time Processing**: Live audio recording and transcription via web interface
- **Multilingual Support**: Automatic language detection and translation
- **High Accuracy**: Optimized models with int8 quantization for performance

### 🤖 **Intelligent AI Agent**
- **Natural Language Understanding**: Interprets user requests and executes appropriate actions
- **Cross-Platform Operations**: Works seamlessly on macOS, Windows, and Linux
- **Function Calling**: Automatically chooses the right tools based on user intent
- **Context Awareness**: Maintains conversation history with 8K token context window

### 🌐 **Web Search & Information Retrieval**
- **DuckDuckGo Integration**: Search web, news, images, and videos
- **Smart Results**: Formatted search results with snippets and quick answers
- **Privacy-First**: No tracking or data collection from search queries

### 📁 **File & Folder Management**
- **Directory Operations**: List, create, read, write, copy, move files and folders
- **Cross-Platform Paths**: Intelligent path handling across operating systems
- **Safe Operations**: Built-in security restrictions for system protection
- **Batch Processing**: Handle multiple file operations efficiently

### 🚀 **Application Launching**
- **Fuzzy App Matching**: Launch apps with approximate names ("notepad" → finds TextEdit on macOS)
- **Cross-Platform Discovery**: Automatically discovers installed applications
- **Smart Suggestions**: Intelligent app matching with 40+ threshold for flexibility
- **System Integration**: Native OS integration for app launching

### 🔧 **System Operations**
- **Audio Processing**: Advanced audio handling with ffmpeg integration
- **Resource Management**: Proper cleanup and memory leak prevention
- **Configuration Management**: Centralized settings with 9+ specialized configuration classes
- **Performance Optimization**: Optimized for both CPU and memory usage

## 🏗️ **Architecture Overview**

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│     Web Browser     │◄──►│   FastAPI Server    │◄──►│      AI Agent       │
│  (Live Recording)   │    │   (API Gateway)     │    │  (Function Calling) │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
                                   ▲                          ▲
                                   │                          │
                       ┌───────────▼───────────┐    ┌─────────▼─────────┐
                       │     Transcription     │    │    Operations     │
                       │        Service        │    │      Modules      │
                       │   (Faster-Whisper)    │    │  • Web Search     │
                       └───────────────────────┘    │  • File Ops       │
                                                    │  • App Launch     │
                                                    └───────────────────┘
```

## 📋 **Prerequisites**

- **Python 3.8+** (3.10+ recommended)
- **uv** (for fast dependency management)
- **ffmpeg** (for audio processing)
- **4GB RAM** minimum (8GB+ recommended for larger models)

## ⚡ **Quick Start**

### 1. **Clone & Setup**
```bash
git clone https://github.com/nithinvarma411/vaakya
cd vaakya
```

### 2. **Install Dependencies**
```bash
# Create virtual environment
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install all dependencies
uv pip install -r requirements.txt
```

### 3. **Install System Dependencies**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
winget install Gyan.FFmpeg
```

### 4. **Launch the Platform**
```bash
# Start the complete platform
./start.sh

# Or start components individually:
./run_server.sh  # API server only
```

### 5. **Access the Interface**
- **Web Interface**: Open `index.html` in your browser
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/

## 🎯 **Usage Examples**

### **Voice Commands**
```
🎤 "Search for latest Python news"
   → Executes web search and displays results

🎤 "List files in the current directory"
   → Shows directory contents with file/folder indicators

🎤 "Open calculator app"
   → Launches calculator (cross-platform compatible)

🎤 "Create a file called notes.txt with my meeting notes"
   → Creates file with specified content

🎤 "Search for machine learning tutorials and save results"
   → Searches web and creates file with results
```

### **API Usage**
```bash
# Transcribe audio file
curl -X POST "http://localhost:8000/transcribe" \
     -F "audio=@recording.wav"

# Chat with AI agent
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "search for AI news"}'
```

### **Python Integration**
```python
from src.app.agent.working_agent import create_working_agent

# Create agent instance
agent = await create_working_agent()

# Natural language interaction
async for message in agent.full_round("list files and open calculator"):
    print(f"Agent: {message.content}")
```

## 🔧 **Configuration**

### **Model Configuration**
Customize AI models in `src/app/config/settings.py`:

```python
class ModelSettings:
    DEFAULT_MODEL_NAME = "qwen2.5-1.5b-instruct"  # Change model
    MAX_CONTEXT_SIZE = 8192                        # Context window
    WHISPER_MODEL_SIZE = "base"                    # Transcription model
```

### **Operation Settings**
```python
class AppOperationsSettings:
    FUZZY_THRESHOLD = 40        # App matching sensitivity
    MAX_APPS_LIMIT = 50         # Max apps to discover

class WebOperationsSettings:
    DEFAULT_MAX_RESULTS = 5     # Search results limit
    SNIPPET_LENGTH = 200        # Result snippet length
```

## 🧪 **Testing & Quality Assurance**

### **Run Comprehensive Tests**
```bash
# Full test suite (11 test scenarios)
python src/tests/test_modular_agent.py

# Basic functionality tests
python src/tests/test_agent.py

# Code quality checks
./check_quality.sh
```

### **Quality Metrics**
- ✅ **Ruff**: 100% compliance (0 errors)
- ✅ **Test Coverage**: 11/11 tests passing (100%)
- ✅ **Type Safety**: Comprehensive type annotations
- ✅ **Performance**: Optimized for production use

## 📊 **Performance Specifications**

### **Response Times**
- **Voice Transcription**: ~2-5 seconds (base model)
- **AI Agent Response**: ~2.4 seconds average
- **Web Search**: ~3-6 seconds
- **File Operations**: ~1-2 seconds
- **App Launching**: ~1.5 seconds

### **Resource Usage**
- **Memory**: 2-4GB (depending on model size)
- **CPU**: Optimized for multi-core processing
- **Storage**: ~1GB for models and dependencies
- **Network**: Optional (only for web search)

## 🛠️ **Development**

### **Project Structure**
```
vaakya/
├── 📄 index.html                    # Web interface
├── 🔧 requirements.txt              # Dependencies
├── ⚙️ pyproject.toml               # Project config
├── 🧪 check_quality.sh             # Quality assurance
├── 🚀 start.sh                     # Launch script
├── 📁 src/
│   ├── 🎯 main.py                   # CLI entry point
│   ├── 📁 app/
│   │   ├── 🤖 agent/                # AI Agent System
│   │   │   ├── working_agent.py     # Main agent
│   │   │   ├── model_utils.py       # Model management
│   │   │   ├── qwen_parser.py       # Function parser
│   │   │   └── 📁 operations/       # Modular operations
│   │   │       ├── app_operations.py    # App launching
│   │   │       ├── file_operations.py   # File management
│   │   │       └── web_operations.py    # Web search
│   │   ├── 🌐 api/                  # FastAPI Server
│   │   │   └── server.py            # API endpoints
│   │   ├── ⚙️ config/               # Configuration
│   │   │   └── settings.py          # Centralized settings
│   │   └── 🔧 services/             # Core Services
│   │       ├── transcription_service.py  # Speech-to-text
│   │       └── audio_processor.py        # Audio handling
│   └── 📁 tests/                    # Test Suite
│       ├── test_modular_agent.py    # Comprehensive tests
│       └── test_agent.py            # Basic tests
```

### **Code Quality Standards**
```bash
# Automated quality checks
./check_quality.sh

# Manual development workflow
ruff check src/          # Linting
ruff format src/         # Formatting
mypy src/               # Type checking
pytest src/tests/       # Testing
```

### **Adding New Operations**
1. Create operation class in `src/app/agent/operations/`
2. Add AI function decorators for agent integration
3. Update configuration in `src/app/config/settings.py`
4. Add tests in `src/tests/`

## 🚀 **Production Deployment**

### **Environment Setup**
```bash
# Production dependencies only
uv pip install --no-dev -r requirements.txt

# Set environment variables
export ENVIRONMENT=production
export DEBUG=false
```

### **Performance Optimization**
- Use **larger Whisper models** (`medium`, `large`) for better accuracy
- Enable **GPU acceleration** with `device="cuda"` if available
- Increase **context window** to 16K+ for longer conversations
- Configure **load balancing** for high-traffic scenarios

### **Security Considerations**
- Built-in **path restrictions** prevent access to system directories
- **File extension filtering** for safe file operations
- **Command allowlist** for secure app launching
- **Local processing** ensures data privacy

## 🤝 **Contributing**

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Run quality checks**: `./check_quality.sh`
4. **Commit changes**: `git commit -m 'Add amazing feature'`
5. **Push to branch**: `git push origin feature/amazing-feature`
6. **Open Pull Request**

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Faster-Whisper** for efficient speech recognition
- **Kani** for AI agent framework
- **FastAPI** for high-performance web framework
- **DuckDuckGo** for privacy-focused search
- **Qwen** for intelligent language models

---

**Built with ❤️ for intelligent automation and voice interaction**
