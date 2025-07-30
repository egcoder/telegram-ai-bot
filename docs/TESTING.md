# 🧪 Testing Guide

This document provides comprehensive information about testing the Telegram AI Bot.

## 📋 Test Structure

```
tests/
├── unit/                           # Unit tests
│   ├── test_bot_core.py           # Bot core functionality
│   ├── test_user_manager.py       # User management
│   ├── test_calendar_utils.py     # Calendar utilities
│   └── test_ai_services.py        # AI service mocking
├── integration/                    # Integration tests
│   └── test_message_handlers.py   # Handler integration
├── test_bot_e2e.py                # End-to-end tests
└── test_performance.py            # Performance tests
```

## 🚀 Quick Start

### Run All Tests
```bash
# Complete test suite
python run_tests.py

# Quick unit tests only
python scripts/run_specific_tests.py quick
```

### Run Specific Test Categories
```bash
# Unit tests only
python scripts/run_specific_tests.py unit

# Integration tests only
python scripts/run_specific_tests.py integration

# End-to-end tests
python scripts/run_specific_tests.py e2e

# Performance tests
python scripts/run_specific_tests.py performance
```

### Run Individual Test Files
```bash
# Specific test file
python scripts/run_specific_tests.py --file tests/unit/test_user_manager.py

# With verbose output
python scripts/run_specific_tests.py --file tests/unit/test_user_manager.py -v
```

## 🔍 Test Categories

### 1. Unit Tests (`tests/unit/`)

**Purpose**: Test individual components in isolation

**Features Tested**:
- Bot core initialization and configuration
- User authorization and management
- Calendar utility functions
- AI service mocking and error handling

**Run Command**:
```bash
python -m pytest tests/unit/ -v
```

**Key Test Files**:
- `test_bot_core.py` - Bot class, config validation, async operations
- `test_user_manager.py` - User CRUD operations, file persistence
- `test_calendar_utils.py` - Calendar link generation, deadline parsing
- `test_ai_services.py` - Mocked AI service responses, error handling

### 2. Integration Tests (`tests/integration/`)

**Purpose**: Test component interactions and message flow

**Features Tested**:
- Command handler registration and execution
- Message handler pipeline
- Handler authorization checks
- Response formatting

**Run Command**:
```bash
python -m pytest tests/integration/ -v
```

**Key Test Files**:
- `test_message_handlers.py` - Complete message processing pipeline

### 3. End-to-End Tests (`tests/test_bot_e2e.py`)

**Purpose**: Simulate complete user workflows

**Features Tested**:
- Full bot initialization
- User authorization flow
- Voice message processing pipeline
- Error handling scenarios
- Calendar integration

**Run Command**:
```bash
python tests/test_bot_e2e.py
```

**Test Scenarios**:
- New user registration
- Voice message transcription and analysis
- Calendar link generation
- Unauthorized access attempts
- API error handling

### 4. Performance Tests (`tests/test_performance.py`)

**Purpose**: Measure system performance under load

**Features Tested**:
- User management scalability
- Calendar utility performance
- Concurrent user operations
- Memory usage patterns

**Run Command**:
```bash
python tests/test_performance.py
```

**Metrics Measured**:
- Response times for various operations
- Memory usage with large datasets
- Concurrent user throughput
- System resource utilization

## 🔧 Test Configuration

### Environment Variables
Tests use mock environment variables by default:
```bash
TELEGRAM_BOT_TOKEN=123456789:test_token
OPENAI_API_KEY=sk-test-key
ADMIN_USER_ID=123456789
LOG_LEVEL=WARNING
```

### Pytest Configuration (`pytest.ini`)
```ini
[tool:pytest]
testpaths = tests
addopts = --verbose --tb=short --asyncio-mode=auto
markers = 
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    performance: Performance tests
```

### Test Markers
```bash
# Run only unit tests
python -m pytest -m unit

# Run only integration tests
python -m pytest -m integration

# Skip slow tests
python -m pytest -m "not slow"
```

## 📊 Coverage Reports

### Generate Coverage Report
```bash
# HTML coverage report
python scripts/run_specific_tests.py coverage

# Terminal coverage report
python -m pytest --cov=telegram_ai_bot --cov-report=term-missing

# Coverage with specific threshold
python -m pytest --cov=telegram_ai_bot --cov-fail-under=80
```

### View Coverage Report
```bash
# Open HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## 🐛 Debugging Tests

### Run Tests with Debug Output
```bash
# Verbose output
python -m pytest tests/unit/test_user_manager.py -v -s

# Stop on first failure
python -m pytest tests/unit/ -x

# Run specific test method
python -m pytest tests/unit/test_user_manager.py::TestUserManager::test_add_user
```

### Debug Async Tests
```bash
# Enable asyncio debug mode
PYTHONASYNCIODEBUG=1 python -m pytest tests/integration/
```

### Test Logging
```bash
# Enable logging during tests
python -m pytest tests/ --log-cli-level=INFO
```

## 🚨 Common Issues and Solutions

### 1. Import Errors
```bash
# Ensure src is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Or use the test runners which handle this automatically
python run_tests.py
```

### 2. Async Test Issues
```bash
# Install pytest-asyncio
pip install pytest-asyncio

# Use proper async test decorators
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == expected
```

### 3. Mock Issues
```bash
# Install required packages
pip install pytest pytest-mock

# Use proper patching
with patch('module.function') as mock_func:
    mock_func.return_value = "test_value"
    # Test code here
```

### 4. Environment Issues
```bash
# Clean test environment
python scripts/test_setup.py

# Check dependencies
python -c "import telegram, openai, aiohttp; print('All imports OK')"
```

## 📈 Performance Benchmarks

### Expected Performance Metrics
- **User Management**: < 1ms per operation for 1000 users
- **Calendar Utils**: < 0.1ms per link generation
- **Concurrent Operations**: > 10 users/second throughput
- **Memory Usage**: < 100MB for 10,000 users

### Performance Test Output Example
```
📊 PERFORMANCE TEST REPORT
═══════════════════════════
👤 USER MANAGER PERFORMANCE (1000 users):
  Add User:      0.15ms avg, 2.34ms max
  Check Auth:    0.05ms avg, 0.89ms max
  Remove User:   0.12ms avg, 1.76ms max

📅 CALENDAR UTILS PERFORMANCE (1000 operations):
  Link Gen:      0.08ms avg, 1.23ms max
  Parse Deadline:0.06ms avg, 0.95ms max

⚡ CONCURRENT OPERATIONS (10 users):
  Total Time:    2.45s
  Throughput:    4.08 users/sec
```

## 🎯 Test Writing Guidelines

### Unit Test Template
```python
import unittest
from unittest.mock import Mock, patch

class TestYourComponent(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.component = YourComponent()
    
    def tearDown(self):
        """Clean up after tests"""
        pass
    
    def test_basic_functionality(self):
        """Test basic functionality"""
        result = self.component.method()
        self.assertEqual(result, expected_value)
```

### Async Test Template
```python
import unittest
from unittest.mock import AsyncMock

class TestAsyncComponent(unittest.IsolatedAsyncioTestCase):
    async def test_async_functionality(self):
        """Test async functionality"""
        result = await self.component.async_method()
        self.assertEqual(result, expected_value)
```

### Integration Test Template
```python
from unittest.mock import Mock, AsyncMock, patch

class TestIntegration(unittest.IsolatedAsyncioTestCase):
    async def test_component_integration(self):
        """Test component interaction"""
        with patch('module.external_service') as mock_service:
            mock_service.return_value = mock_response
            result = await integrated_function()
            self.assertIsNotNone(result)
```

## 🔄 Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov
    - name: Run tests
      run: python run_tests.py
```

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Manual run
pre-commit run --all-files
```

## 📚 Additional Resources

### Useful Commands
```bash
# List all available tests
python scripts/run_specific_tests.py --list

# Run tests matching pattern
python -m pytest -k "test_user"

# Run tests in parallel (with pytest-xdist)
python -m pytest -n auto

# Generate JUnit XML report
python -m pytest --junitxml=test-results.xml
```

### Test Data Management
```bash
# Clean test data
rm -rf /tmp/telegram_bot_test_*

# Reset test database
python scripts/reset_test_data.py
```

This comprehensive testing setup ensures your Telegram AI Bot is reliable, performant, and ready for production deployment.