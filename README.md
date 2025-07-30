# 🤖 Telegram AI Personal Assistant Bot

A sophisticated Telegram bot that serves as an AI-powered personal assistant for business teams. The bot processes voice messages in multiple languages, extracts action items using AI, and provides direct Google Calendar integration for seamless task management.

## 🎯 **Project Overview**

This project creates a private, invitation-only Telegram bot that acts as an intelligent assistant for business teams. Users can send voice notes in Arabic, English, or French, and the bot will:

- **Transcribe** voice messages using OpenAI Whisper
- **Analyze** content using GPT-4 or Claude
- **Extract** action items with priorities and deadlines
- **Generate** summaries with timestamps
- **Create** Google Calendar links for immediate task scheduling
- **Manage** access through invitation-only system

## ✨ **Key Features**

### 🔐 **Security & Access Control**
- **Invitation-only access** - Only authorized users can interact with the bot
- **Admin controls** - Designated admin can manage user permissions
- **Secure storage** - Environment variables for sensitive API keys

### 🎤 **Voice Processing**
- **Multi-language support** - Arabic, English, and French transcription
- **Auto-language detection** - Automatically identifies spoken language
- **High-quality transcription** - Powered by OpenAI Whisper API

### 🧠 **AI Analysis**
- **Intelligent parsing** - Extracts actionable items from conversations
- **Priority classification** - Categorizes tasks as high, medium, or low priority
- **Deadline detection** - Identifies and formats mentioned dates
- **Contextual summaries** - Creates concise, relevant summaries

### 📅 **Calendar Integration**
- **Direct Google Calendar links** - One-click task addition
- **Smart scheduling** - Automatically sets appropriate dates and times
- **Formatted events** - Includes context and creation timestamps

### 👥 **Team Collaboration**
- **Shared workspace** - All team members see processed content
- **Timestamped responses** - Every analysis includes user and timestamp
- **Formatted output** - Clean, readable message formatting

## 🏗️ **Architecture**

### **Core Components**

```
├── bot.py                 # Full-featured bot (Python 3.12+)
├── bot_simple.py         # Simplified bot (Python 3.13 compatible)
├── requirements.txt      # Python dependencies
├── .env                  # Environment configuration
├── authorized_users.json # User access management
└── README.md            # This documentation
```

### **Technology Stack**
- **Python 3.8+** (3.12 recommended, 3.13 with simple version)
- **python-telegram-bot** - Telegram Bot API wrapper
- **OpenAI API** - Whisper transcription + GPT-4 analysis
- **Anthropic API** - Alternative Claude analysis (optional)
- **FFmpeg** - Audio processing
- **aiohttp** - Async HTTP requests

### **External APIs**
- **Telegram Bot API** - Message handling and bot interface
- **OpenAI Whisper** - Voice transcription ($0.006/minute)
- **OpenAI GPT-4** - Content analysis ($0.03/1K tokens)
- **Google Calendar** - Task scheduling (free web interface)

## 🚀 **Quick Start**

### **Prerequisites**
1. Python 3.8+ installed
2. Telegram account
3. OpenAI API account (or Anthropic)
4. FFmpeg installed

### **Installation**
```bash
# Clone the repository
git clone <repository-url>
cd telegram-ai-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (system dependency)
# macOS: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
# Windows: Download from ffmpeg.org
```

### **Configuration**
1. **Create Telegram Bot**
   - Message @BotFather on Telegram
   - Create new bot with `/newbot`
   - Save the bot token

2. **Get API Keys**
   - OpenAI: platform.openai.com → API Keys
   - Get your Telegram User ID from @userinfobot

3. **Environment Setup**
   ```bash
   # Create .env file
   cp .env.template .env
   
   # Edit with your values
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   OPENAI_API_KEY=your_openai_key_here
   ADMIN_USER_ID=your_telegram_user_id
   ```

### **Running the Bot**
```bash
# For Python 3.12 and below
python bot.py

# For Python 3.13
python bot_simple.py
```

## 📱 **Usage Guide**

### **Admin Commands**
- `/start` - Initialize bot and show welcome message
- `/help` - Display usage instructions
- `/invite` - Generate invitation links for new users

### **User Workflow**
1. **Send voice note** - Record message in any supported language
2. **Receive analysis** - Bot transcribes and analyzes content
3. **Review results** - See summary and extracted action items
4. **Add to calendar** - Click buttons to schedule tasks

### **Voice Note Best Practices**
- Speak clearly at normal pace
- Mention specific dates for better deadline detection
- Use action words: "remind me", "schedule", "deadline"
- Structure content: main topic, then action items

## ⚙️ **Configuration**

### **Environment Variables**
```bash
# Required
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
OPENAI_API_KEY=sk-proj-abcd1234...
ADMIN_USER_ID=987654321

# Optional
ANTHROPIC_API_KEY=sk-ant-api03-abcd...  # Alternative to OpenAI
```

### **User Management**
Users are stored in `authorized_users.json`:
```json
{
  "users": [123456789, 987654321, 456789123]
}
```

### **Bot Settings**
- **Auto-language detection** enabled
- **GPT-4 model** for analysis (configurable)
- **Drop pending updates** on restart
- **Error logging** to console

## 🔧 **Development**

### **Project Structure**
```
telegram-ai-bot/
├── bot.py                    # Main bot implementation
├── bot_simple.py            # Python 3.13 compatible version
├── requirements.txt         # Dependencies
├── .env.template           # Environment template
├── authorized_users.json   # User storage
├── README.md              # Documentation
└── deployment_guide.md    # Deployment instructions
```

### **Key Classes and Functions**
- `TelegramAIBot` - Main bot class
- `transcribe_audio()` - Voice-to-text conversion
- `analyze_with_ai()` - AI content analysis
- `generate_calendar_link()` - Google Calendar integration
- `handle_voice()` - Voice message processing pipeline

### **Adding Features**
1. **New commands** - Add handlers in `run()` method
2. **AI providers** - Extend `analyze_with_ai()` function
3. **Languages** - Modify Whisper language settings
4. **Storage** - Replace JSON with database for production

## 🚀 **Deployment**

### **Local Development**
```bash
python bot.py  # or bot_simple.py for Python 3.13
```

### **Production Options**

#### **VPS/Cloud Server**
```bash
# Install on Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip ffmpeg
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create systemd service
sudo nano /etc/systemd/system/telegram-ai-bot.service
sudo systemctl enable telegram-ai-bot
sudo systemctl start telegram-ai-bot
```

#### **Docker**
```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

#### **Heroku**
```bash
# Procfile
worker: python bot.py

# Add buildpacks
heroku buildpacks:add https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
heroku buildpacks:add heroku/python
```

## 💰 **Cost Analysis**

### **API Usage Costs**
- **Whisper Transcription**: $0.006 per minute of audio
- **GPT-4 Analysis**: $0.03 per 1K tokens (~750 words)
- **Typical voice note**: 1-2 minutes = ~$0.01-0.05 per message

### **Monthly Estimates**
- **Light usage** (100 voice notes): $5-15
- **Medium usage** (500 voice notes): $25-50
- **Heavy usage** (1000+ voice notes): $50-100

### **Infrastructure Costs**
- **VPS**: $5-20/month
- **Heroku**: $7-25/month
- **Local hosting**: Electricity costs only

## 🐛 **Troubleshooting**

### **Common Issues**

#### **Python 3.13 Compatibility**
```bash
# Use the simple bot version
python bot_simple.py

# Or install Python 3.12
brew install python@3.12
python3.12 -m venv venv
```

#### **FFmpeg Not Found**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# Download from ffmpeg.org and add to PATH
```

#### **API Key Issues**
```bash
# Test environment variables
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('Bot token:', bool(os.getenv('TELEGRAM_BOT_TOKEN')))
print('OpenAI key:', bool(os.getenv('OPENAI_API_KEY')))
"
```

#### **Voice Processing Errors**
- Check audio format (OGG supported)
- Verify FFmpeg installation
- Ensure sufficient OpenAI credits
- Check internet connection for API calls

## 🔒 **Security Considerations**

### **API Key Protection**
- Never commit `.env` files to version control
- Use environment variables in production
- Regularly rotate API keys
- Monitor API usage for anomalies

### **User Access Control**
- Implement proper invitation system
- Regular audit of authorized users
- Consider database storage for user management
- Add rate limiting for API protection

### **Data Privacy**
- Voice files are temporarily stored and deleted
- No persistent audio storage
- API calls to OpenAI (review their privacy policy)
- Consider on-premise solutions for sensitive data

## 📊 **Monitoring & Analytics**

### **Logging**
- Error logging to console/files
- API usage tracking
- User activity monitoring
- Performance metrics

### **Health Checks**
```bash
# Check bot status (systemd)
sudo systemctl status telegram-ai-bot

# Check logs
sudo journalctl -u telegram-ai-bot -f

# Monitor API usage
# Check OpenAI dashboard for usage stats
```

## 🤝 **Contributing**

### **Development Setup**
1. Fork the repository
2. Create feature branch
3. Install development dependencies
4. Make changes with tests
5. Submit pull request

### **Code Style**
- Follow PEP 8 Python style guide
- Use type hints where applicable
- Add docstrings for functions
- Include error handling

### **Testing**
```bash
# Test environment setup
python test_env.py

# Test bot functionality
# Send test voice messages
# Verify API integrations
```

## 📄 **License**

This project is open source and available under the [MIT License](LICENSE).

## 🆘 **Support**

### **Documentation**
- Full deployment guide included
- Configuration examples provided
- Troubleshooting section comprehensive

### **Getting Help**
- Review troubleshooting section
- Check environment variable setup
- Verify API key configuration
- Test with simple bot version first

### **Known Limitations**
- Python 3.13 requires simple bot version
- Voice file size limits (Telegram: 50MB)
- API rate limits (OpenAI: varies by plan)
- Internet connection required for all operations

---

**Built with ❤️ for efficient team collaboration and productivity.**