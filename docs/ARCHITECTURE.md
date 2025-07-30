# Architecture Overview

## Project Structure

```
telegram-ai-bot/
├── src/
│   └── telegram_ai_bot/
│       ├── __init__.py
│       ├── __main__.py          # Entry point
│       ├── core/
│       │   ├── __init__.py
│       │   ├── bot.py           # Main bot class
│       │   └── config.py        # Configuration management
│       ├── handlers/
│       │   ├── __init__.py
│       │   ├── command_handlers.py  # Command processing
│       │   └── message_handlers.py  # Voice/text processing
│       └── utils/
│           ├── __init__.py
│           ├── ai_service.py    # AI integration (OpenAI/Anthropic)
│           ├── calendar_utils.py # Google Calendar integration
│           └── user_manager.py   # User authorization management
├── tests/
│   ├── unit/                    # Unit tests
│   └── integration/             # Integration tests
├── config/
│   └── .env.example            # Environment configuration template
├── data/
│   └── authorized_users.json   # User storage
├── logs/                       # Application logs
├── docs/                       # Documentation
├── scripts/                    # Utility scripts
├── main.py                     # Main entry point
├── setup.py                    # Package configuration
├── requirements.txt            # Dependencies
└── README.md                   # Project documentation
```

## Core Components

### 1. Bot Core (`src/telegram_ai_bot/core/`)

#### `bot.py`
- Main `TelegramAIBot` class
- Handles bot initialization and lifecycle
- Registers all handlers
- Manages graceful shutdown

#### `config.py`
- Centralized configuration management
- Environment variable loading
- Path management
- Configuration validation

### 2. Handlers (`src/telegram_ai_bot/handlers/`)

#### `command_handlers.py`
- `/start` - User initialization and authorization check
- `/help` - Display usage information
- `/invite` - Admin-only invitation generation
- Callback query handling for invitations

#### `message_handlers.py`
- Voice message processing pipeline
- Audio download and temporary storage
- AI service integration
- Response formatting with calendar links

### 3. Utilities (`src/telegram_ai_bot/utils/`)

#### `ai_service.py`
- `AIService` class for OpenAI integration
  - Whisper API for transcription
  - GPT-4 for content analysis
- `AnthropicService` class for Claude integration (optional)
- Async execution for non-blocking operations

#### `calendar_utils.py`
- Google Calendar link generation
- Deadline parsing from natural language
- Action item formatting with calendar integration

#### `user_manager.py`
- User authorization management
- JSON-based persistence
- Invitation token generation
- User statistics

## Data Flow

### Voice Message Processing

1. **Message Reception**
   - User sends voice message
   - Bot checks authorization

2. **Audio Processing**
   - Download voice file to temporary storage
   - Convert OGG to format suitable for Whisper

3. **Transcription**
   - Send audio to OpenAI Whisper API
   - Receive text transcript

4. **Analysis**
   - Send transcript to GPT-4/Claude
   - Extract action items, priorities, deadlines

5. **Response Generation**
   - Format analysis results
   - Generate Google Calendar links
   - Create inline keyboard with actions

6. **Cleanup**
   - Delete temporary audio files
   - Log processing metrics

## Security Considerations

### Authentication & Authorization
- Invitation-only access system
- Admin user verification via environment variable
- User IDs stored in JSON file (consider database for production)

### API Key Management
- All sensitive keys in environment variables
- Never logged or exposed in responses
- Support for multiple AI providers

### Data Privacy
- Temporary audio files deleted after processing
- No persistent storage of voice content
- Minimal user data collection

## Scalability Considerations

### Current Design
- Single-process async architecture
- File-based user storage
- In-memory invitation tokens

### Production Improvements
- Database integration (PostgreSQL/MongoDB)
- Redis for caching and session management
- Horizontal scaling with load balancer
- Message queue for heavy processing

## Integration Points

### External Services
1. **Telegram Bot API**
   - Webhook support for production
   - Long polling for development

2. **OpenAI API**
   - Whisper for transcription
   - GPT-4 for analysis

3. **Anthropic API** (Optional)
   - Claude for alternative analysis

4. **Google Calendar**
   - Web-based event creation
   - No authentication required

## Error Handling

### Graceful Degradation
- Fallback messages for API failures
- Temporary file cleanup on errors
- User-friendly error messages

### Logging Strategy
- Structured logging with levels
- Separate logs for different components
- Performance metrics tracking

## Testing Strategy

### Unit Tests
- User management logic
- Calendar utility functions
- Configuration validation

### Integration Tests
- End-to-end voice processing
- API mock testing
- Handler interaction testing

## Deployment Considerations

### Development
- Local `.env` file
- SQLite for testing
- Debug logging enabled

### Production
- Environment variables from secrets manager
- PostgreSQL/MongoDB for data
- Structured logging to monitoring service
- Health check endpoints