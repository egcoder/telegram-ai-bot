# Development Guide

## Setting Up Development Environment

### Prerequisites
- Python 3.8+ (3.12 recommended)
- FFmpeg for audio processing
- Git for version control

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd telegram-ai-bot
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
pip install -e .  # Install package in development mode
```

4. **Install development dependencies**
```bash
pip install pytest pytest-asyncio pytest-cov black flake8 mypy
```

5. **Set up pre-commit hooks** (optional)
```bash
pip install pre-commit
pre-commit install
```

## Configuration

1. **Copy environment template**
```bash
cp config/.env.example .env
```

2. **Edit `.env` with your values**
```bash
TELEGRAM_BOT_TOKEN=your_bot_token
OPENAI_API_KEY=your_openai_key
ADMIN_USER_ID=your_telegram_id
```

## Running the Bot

### Development Mode
```bash
# Using main.py
python main.py

# Or using module
python -m telegram_ai_bot

# With specific log level
LOG_LEVEL=DEBUG python main.py
```

### Testing

#### Run all tests
```bash
pytest
```

#### Run with coverage
```bash
pytest --cov=telegram_ai_bot --cov-report=html
```

#### Run specific test file
```bash
pytest tests/unit/test_user_manager.py
```

#### Run tests with verbose output
```bash
pytest -v
```

## Code Style

### Format code with Black
```bash
black src/ tests/
```

### Check with flake8
```bash
flake8 src/ tests/
```

### Type checking with mypy
```bash
mypy src/
```

## Project Structure Guidelines

### Adding New Features

1. **Create feature branch**
```bash
git checkout -b feature/your-feature-name
```

2. **Add handler** (if needed)
   - Create new file in `src/telegram_ai_bot/handlers/`
   - Import and register in `core/bot.py`

3. **Add utilities** (if needed)
   - Create new file in `src/telegram_ai_bot/utils/`
   - Add appropriate tests

4. **Update configuration** (if needed)
   - Add new variables to `core/config.py`
   - Update `.env.example`

### Writing Tests

#### Unit Test Example
```python
# tests/unit/test_your_feature.py
import unittest
from telegram_ai_bot.utils.your_module import YourClass

class TestYourFeature(unittest.TestCase):
    def setUp(self):
        self.instance = YourClass()
    
    def test_functionality(self):
        result = self.instance.method()
        self.assertEqual(result, expected_value)
```

#### Async Test Example
```python
# tests/unit/test_async_feature.py
import pytest
from telegram_ai_bot.utils.ai_service import AIService

@pytest.mark.asyncio
async def test_async_method():
    service = AIService("test_key")
    result = await service.async_method()
    assert result == expected_value
```

## Debugging

### Enable Debug Logging
```python
# In your code
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

### Using Python Debugger
```python
import pdb; pdb.set_trace()  # Add breakpoint
```

### Telegram Bot Debugging
1. Use @BotFather to check bot settings
2. Enable debug mode in `.env`: `LOG_LEVEL=DEBUG`
3. Check webhook status (if using webhooks)

## Common Development Tasks

### Adding a New Command
1. Add handler in `command_handlers.py`:
```python
def get_newcommand_handler():
    async def newcommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Command response")
    return CommandHandler('newcommand', newcommand)
```

2. Register in `bot.py`:
```python
self.application.add_handler(
    command_handlers.get_newcommand_handler()
)
```

### Adding a New AI Provider
1. Create new class in `ai_service.py`:
```python
class NewAIService:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def analyze_text(self, text: str) -> Dict:
        # Implementation
        pass
```

2. Update configuration in `config.py`
3. Add provider selection logic

### Database Migration (Future)
When moving from JSON to database:
1. Create migration script in `scripts/`
2. Update `UserManager` to use database
3. Add database configuration
4. Update deployment documentation

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Ensure you're in the virtual environment
which python  # Should show venv path

# Reinstall in development mode
pip install -e .
```

#### Async Errors
- Ensure all async functions are awaited
- Use `asyncio.run()` for top-level async calls
- Check for missing `async` keywords

#### API Rate Limits
- Implement exponential backoff
- Add rate limiting to handlers
- Cache responses where appropriate

## Performance Optimization

### Profiling
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
# Your code here
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats()
```

### Memory Usage
```python
import tracemalloc

tracemalloc.start()
# Your code here
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 10**6}MB")
tracemalloc.stop()
```

## Contributing

### Before Submitting PR
1. Run all tests: `pytest`
2. Format code: `black src/ tests/`
3. Check style: `flake8 src/ tests/`
4. Update documentation if needed
5. Add tests for new features
6. Update CHANGELOG.md

### Commit Message Format
```
feat: Add voice message queue
fix: Handle timeout in transcription
docs: Update installation guide
test: Add calendar utils tests
refactor: Simplify user manager
```