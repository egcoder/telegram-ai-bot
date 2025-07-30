# 📁 Project Structure

This document describes the reorganized project structure following Python best practices.

## 🗂️ Directory Structure

```
telegram-ai-bot/
├── 📁 src/                          # Source code
│   └── telegram_ai_bot/             # Main package
│       ├── __init__.py
│       ├── __main__.py              # Entry point
│       ├── 📁 core/                 # Core functionality
│       │   ├── __init__.py
│       │   ├── bot.py               # Main bot class
│       │   └── config.py            # Configuration management
│       ├── 📁 handlers/             # Message & command handlers
│       │   ├── __init__.py
│       │   ├── command_handlers.py  # /start, /help, /invite commands
│       │   └── message_handlers.py  # Voice message processing
│       └── 📁 utils/                # Utility modules
│           ├── __init__.py
│           ├── ai_service.py        # OpenAI/Anthropic integration
│           ├── calendar_utils.py    # Google Calendar links
│           └── user_manager.py      # User authorization
├── 📁 tests/                        # Test suite
│   ├── __init__.py
│   ├── 📁 unit/                     # Unit tests
│   │   ├── __init__.py
│   │   ├── test_user_manager.py
│   │   └── test_calendar_utils.py
│   └── 📁 integration/              # Integration tests
│       └── __init__.py
├── 📁 config/                       # Configuration files
│   └── .env.example                 # Environment template
├── 📁 data/                         # Application data
│   └── authorized_users.json        # User storage
├── 📁 logs/                         # Log files (created at runtime)
├── 📁 docs/                         # Documentation
│   ├── ARCHITECTURE.md              # System architecture
│   └── DEVELOPMENT.md               # Development guide
├── 📁 scripts/                      # Utility scripts
│   └── test_setup.py                # Environment testing
├── 📁 venv/                         # Virtual environment (ignored in git)
├── main.py                          # Main entry point
├── setup.py                         # Package configuration
├── requirements.txt                 # Dependencies
├── test_plan.md                     # Testing instructions
├── README.md                        # Project documentation
└── .env                            # Environment variables (git ignored)
```

## 🏗️ Architecture Benefits

### ✅ **Best Practices Implemented**

1. **Separation of Concerns**
   - Core logic separated from handlers
   - Utilities isolated in their own modules
   - Configuration centralized

2. **Testability**
   - Unit tests for individual components
   - Integration tests for full workflows
   - Mock-friendly architecture

3. **Maintainability**
   - Clear module boundaries
   - Consistent naming conventions
   - Comprehensive documentation

4. **Scalability**
   - Modular design allows easy feature addition
   - Handler pattern supports multiple message types
   - Plugin-ready architecture

### 🔧 **Key Components**

#### **Core Module** (`src/telegram_ai_bot/core/`)
- `bot.py`: Main bot orchestration and lifecycle
- `config.py`: Environment variables and settings

#### **Handlers Module** (`src/telegram_ai_bot/handlers/`)
- `command_handlers.py`: Bot commands (/start, /help, etc.)
- `message_handlers.py`: Voice and text message processing

#### **Utils Module** (`src/telegram_ai_bot/utils/`)
- `ai_service.py`: AI provider integrations
- `calendar_utils.py`: Google Calendar functionality
- `user_manager.py`: User authorization system

## 🚀 **Running the Bot**

### **Development Mode**
```bash
# Method 1: Using main.py
python main.py

# Method 2: Using module
python -m telegram_ai_bot

# Method 3: Using setup.py entry point (after pip install -e .)
telegram-ai-bot
```

### **Testing Environment**
```bash
# Run environment test
python scripts/test_setup.py

# Run unit tests
pytest tests/unit/

# Run all tests with coverage
pytest --cov=telegram_ai_bot
```

## 📦 **Installation**

### **For Development**
```bash
# Clone repository
git clone <repository-url>
cd telegram-ai-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-asyncio pytest-cov black flake8
```

### **For Production**
```bash
# Install from source
pip install git+<repository-url>

# Or from local directory
pip install .
```

## 🔄 **Migration from Old Structure**

The old structure had all files in the root directory:
```
Old Structure:
├── bot.py                    # Monolithic bot file
├── bot_simple.py            # Python 3.13 version
├── test_env.py              # Environment test
└── authorized_users.json    # User data
```

**Migration Benefits:**
1. **Modularity**: Code split into logical components
2. **Testing**: Dedicated test structure with proper imports
3. **Configuration**: Centralized settings management
4. **Documentation**: Comprehensive guides and architecture docs
5. **Deployment**: Package-ready with setup.py

## 🛠️ **Development Workflow**

1. **Feature Development**
   ```bash
   git checkout -b feature/new-feature
   # Edit files in src/telegram_ai_bot/
   pytest tests/
   git commit -m "feat: Add new feature"
   ```

2. **Adding Commands**
   - Add handler in `handlers/command_handlers.py`
   - Register in `core/bot.py`
   - Add tests in `tests/unit/`

3. **Adding Utilities**
   - Create module in `utils/`
   - Add tests in `tests/unit/`
   - Import in relevant handlers

## 📊 **Quality Assurance**

### **Code Quality Tools**
```bash
# Format code
black src/ tests/

# Check style
flake8 src/ tests/

# Type checking
mypy src/

# Security check
bandit -r src/
```

### **Testing Strategy**
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Environment Tests**: Configuration validation

This structure provides a solid foundation for scaling the bot while maintaining code quality and developer productivity.