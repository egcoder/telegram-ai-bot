#!/usr/bin/env python3
"""
Simplified Telegram AI Assistant Bot - Python 3.13 Compatible
"""

import os
import json
import logging
import tempfile
from datetime import datetime, timedelta
from urllib.parse import quote

from dotenv import load_dotenv
import openai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', '0'))

# Initialize OpenAI
if OPENAI_API_KEY:
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Authorized users storage
authorized_users = {ADMIN_USER_ID} if ADMIN_USER_ID else set()

def load_authorized_users():
    """Load authorized users from file"""
    global authorized_users
    try:
        if os.path.exists('authorized_users.json'):
            with open('authorized_users.json', 'r') as f:
                data = json.load(f)
                authorized_users = set(data.get('users', []))
                if ADMIN_USER_ID:
                    authorized_users.add(ADMIN_USER_ID)
    except Exception as e:
        logger.error(f"Error loading authorized users: {e}")

def save_authorized_users():
    """Save authorized users to file"""
    try:
        with open('authorized_users.json', 'w') as f:
            json.dump({'users': list(authorized_users)}, f)
    except Exception as e:
        logger.error(f"Error saving authorized users: {e}")

def is_authorized(user_id: int) -> bool:
    """Check if user is authorized"""
    return user_id in authorized_users

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text(
            "🔒 Access denied. This bot is invitation-only.\n"
            "Please contact the administrator for access."
        )
        return
    
    welcome_message = """
🤖 **AI Personal Assistant Bot**

Welcome! I can help you with:

📝 **Voice Note Analysis**
- Send voice notes in Arabic, English, or French
- I'll extract action items and summaries
- Get direct Google Calendar links for tasks

**Commands:**
/start - Show this message
/invite - Generate invitation link (admin only)
/help - Get help

Just send me a voice note to get started!
    """
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    if not is_authorized(update.effective_user.id):
        return
        
    help_text = """
🔧 **How to use the AI Assistant:**

1️⃣ **Send Voice Notes**
   - Record in Arabic, English, or French
   - I'll transcribe and analyze automatically

2️⃣ **Action Items**
   - Click calendar links to add to Google Calendar
   - Items are formatted with timestamps

3️⃣ **Summaries**
   - Get concise summaries of your voice notes
   - Perfect for meeting notes and reminders

💡 **Tips:**
- Speak clearly for better transcription
- Mention specific dates/times for calendar events
- Use keywords like "remind me", "schedule", "deadline"
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def invite_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /invite command (admin only)"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("❌ Only administrators can generate invitations.")
        return
    
    await update.message.reply_text(
        "To add a new user:\n"
        "1. Ask them to get their Telegram User ID from @userinfobot\n"
        "2. Add their ID to the authorized_users.json file\n"
        "3. Or modify the code to add them to the authorized_users set"
    )

async def transcribe_audio(audio_file_path: str) -> str:
    """Transcribe audio using OpenAI Whisper"""
    try:
        with open(audio_file_path, 'rb') as audio_file:
            response = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=None  # Auto-detect language
            )
            return response.text
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return None

async def analyze_with_ai(transcript: str) -> dict:
    """Analyze transcript using AI"""
    prompt = f"""
Analyze the following transcript and extract:
1. Action items with specific details
2. A concise summary
3. Detect the language (Arabic, English, or French)

Format your response as JSON:
{{
    "language": "detected language",
    "summary": "concise summary",
    "action_items": [
        {{
            "task": "specific task description",
            "deadline": "deadline if mentioned (YYYY-MM-DD format)",
            "priority": "high/medium/low"
        }}
    ]
}}

Transcript: {transcript}
"""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant that analyzes voice transcripts. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
        
    except Exception as e:
        logger.error(f"AI analysis error: {e}")
        return {
            "language": "unknown",
            "summary": "Could not analyze transcript",
            "action_items": []
        }

def generate_calendar_link(task: str, deadline: str = None) -> str:
    """Generate Google Calendar link for task"""
    base_url = "https://calendar.google.com/calendar/render?action=TEMPLATE"
    
    if deadline:
        try:
            start_date = datetime.strptime(deadline, '%Y-%m-%d')
        except:
            start_date = datetime.now() + timedelta(days=1)
    else:
        start_date = datetime.now() + timedelta(days=1)
    
    end_date = start_date + timedelta(hours=1)
    
    params = {
        'text': task,
        'dates': f"{start_date.strftime('%Y%m%dT%H%M%S')}/{end_date.strftime('%Y%m%dT%H%M%S')}",
        'details': f"Action item from AI Assistant\nCreated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    }
    
    param_string = '&'.join([f"{key}={quote(str(value))}" for key, value in params.items()])
    return f"{base_url}&{param_string}"

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice messages"""
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text("🔒 Access denied. Contact admin for invitation.")
        return
    
    try:
        # Send processing message
        processing_msg = await update.message.reply_text("🎤 Processing voice note...")
        
        # Download voice file
        voice_file = await context.bot.get_file(update.message.voice.file_id)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_file:
            await voice_file.download_to_drive(temp_file.name)
            temp_file_path = temp_file.name
        
        # Transcribe audio
        await processing_msg.edit_text("🔄 Transcribing audio...")
        transcript = await transcribe_audio(temp_file_path)
        
        if not transcript:
            await processing_msg.edit_text("❌ Could not transcribe audio. Please try again.")
            return
        
        # Analyze with AI
        await processing_msg.edit_text("🧠 Analyzing content...")
        analysis = await analyze_with_ai(transcript)
        
        # Format response
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        user_name = update.effective_user.first_name or "User"
        
        response = f"📋 **Analysis for {user_name}**\n"
        response += f"🕐 {timestamp}\n"
        response += f"🌐 Language: {analysis.get('language', 'Unknown')}\n\n"
        
        # Add summary
        if analysis.get('summary'):
            response += f"📝 **Summary:**\n{analysis['summary']}\n\n"
        
        # Add action items
        action_items = analysis.get('action_items', [])
        if action_items:
            response += "✅ **Action Items:**\n"
            for i, item in enumerate(action_items, 1):
                task = item.get('task', 'Unknown task')
                deadline = item.get('deadline')
                priority = item.get('priority', 'medium')
                
                priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(priority, '🟡')
                
                response += f"{i}. {priority_emoji} {task}"
                
                if deadline:
                    response += f" (Due: {deadline})"
                
                response += "\n"
            
            # Create inline keyboard with calendar links
            keyboard = []
            for i, item in enumerate(action_items):
                task = item.get('task', 'Unknown task')
                deadline = item.get('deadline')
                calendar_link = generate_calendar_link(task, deadline)
                
                keyboard.append([
                    InlineKeyboardButton(
                        f"📅 Add Item {i+1} to Calendar",
                        url=calendar_link
                    )
                ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            response += "ℹ️ No action items detected."
            reply_markup = None
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        # Delete processing message and send final response
        await processing_msg.delete()
        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error processing voice: {e}")
        await update.message.reply_text(
            "❌ Error processing voice note. Please try again."
        )

def main():
    """Main function"""
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
    
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    # Load authorized users
    load_authorized_users()
    
    # Create application
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("invite", invite_command))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    
    # Start the bot
    print("🤖 AI Assistant Bot is starting...")
    print("📡 Using OPENAI for AI processing")
    
    # Run with error handling
    try:
        app.run_polling(drop_pending_updates=True)
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        print(f"❌ Bot failed to start: {e}")

if __name__ == '__main__':
    main()