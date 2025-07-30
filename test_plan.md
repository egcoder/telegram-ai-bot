# Telegram AI Bot Testing Plan

## Test Environment Setup ✅

### Prerequisites Completed:
- ✅ Python 3.13.1 installed
- ✅ Virtual environment created and activated
- ✅ Dependencies installed (requirements.txt)
- ✅ Environment variables configured (.env file)
- ✅ authorized_users.json created
- ⚠️  FFmpeg not installed (required for voice processing)

### Environment Variables Verified:
- TELEGRAM_BOT_TOKEN: ✅ Set (starts with 8426133279...)
- OPENAI_API_KEY: ✅ Set
- ADMIN_USER_ID: ✅ Set

## Testing Steps

### 1. Install FFmpeg (Required)
```bash
# For macOS:
brew install ffmpeg

# For Ubuntu/Debian:
sudo apt update && sudo apt install ffmpeg

# Verify installation:
ffmpeg -version
```

### 2. Start the Bot
```bash
# Activate virtual environment
source venv/bin/activate

# Run the bot (Python 3.13 compatible version)
python bot_simple.py
```

### 3. Telegram Bot Testing

#### A. Basic Commands Test
1. Open Telegram and search for your bot
2. Start conversation with `/start`
   - Expected: Welcome message and authorization check
3. Test `/help` command
   - Expected: Usage instructions
4. Test `/invite` command (admin only)
   - Expected: Generate invitation link

#### B. Voice Message Testing
1. **Test Language Detection**
   - Send voice message in English
   - Send voice message in Arabic
   - Send voice message in French
   - Expected: Bot should transcribe and analyze each correctly

2. **Test Action Item Extraction**
   - Send voice: "Remind me to call John tomorrow at 3 PM"
   - Expected: Bot extracts action item with deadline

3. **Test Priority Detection**
   - Send voice: "Urgent: Need to submit report by end of day"
   - Expected: Bot marks as high priority

4. **Test Calendar Integration**
   - Click on generated calendar links
   - Expected: Opens Google Calendar with pre-filled event

#### C. Authorization Testing
1. **Test Unauthorized User**
   - Use different Telegram account
   - Send `/start` command
   - Expected: Access denied message

2. **Test Invitation System**
   - Admin generates invite link
   - New user clicks link
   - Expected: User added to authorized list

### 4. API Integration Testing

#### A. OpenAI API Tests
```python
# Test script for API connectivity
import os
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Test Whisper API
print("Testing Whisper API...")
# (Requires actual audio file)

# Test GPT-4 API
print("Testing GPT-4...")
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello, this is a test"}]
)
print("GPT-4 Response:", response.choices[0].message.content)
```

### 5. Error Handling Tests

1. **Large Audio File**
   - Send voice message > 10 minutes
   - Expected: Graceful error handling

2. **Network Issues**
   - Disconnect internet during processing
   - Expected: Timeout and error message

3. **Invalid Audio Format**
   - Send non-audio file
   - Expected: Format error message

### 6. Performance Testing

1. **Concurrent Users**
   - Multiple users send voice messages simultaneously
   - Monitor response times

2. **Processing Time**
   - Measure time from voice send to response
   - Target: < 30 seconds for 2-minute audio

### 7. Bot Monitoring

```bash
# Check bot logs
tail -f bot.log  # If logging to file

# Monitor system resources
top | grep python

# Check API usage
# Visit OpenAI dashboard for usage statistics
```

## Test Checklist

- [ ] FFmpeg installed and verified
- [ ] Bot starts without errors
- [ ] Admin can use all commands
- [ ] Voice transcription works
- [ ] AI analysis provides action items
- [ ] Calendar links generated correctly
- [ ] Unauthorized users blocked
- [ ] Invitation system works
- [ ] Error handling functional
- [ ] Multi-language support verified

## Common Issues & Solutions

### Bot Not Responding
1. Check bot token in .env
2. Verify internet connection
3. Check Telegram Bot API status

### Voice Processing Fails
1. Install FFmpeg
2. Check audio file format
3. Verify OpenAI API credits

### Authorization Issues
1. Check ADMIN_USER_ID in .env
2. Verify authorized_users.json format
3. Use @userinfobot to get correct user ID

## Testing Commands Summary

```bash
# Environment test
python test_env.py

# Start bot
python bot_simple.py

# Check processes
ps aux | grep bot_simple

# Kill bot if needed
pkill -f bot_simple.py
```

## Next Steps

1. Install FFmpeg to enable voice processing
2. Run the bot using `python bot_simple.py`
3. Test all features systematically
4. Monitor logs for any errors
5. Document any issues found