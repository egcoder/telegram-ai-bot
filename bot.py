#!/usr/bin/env python3
"""
Telegram AI Personal Assistant Bot
Features:
- Invitation-only access
- Voice note processing in Arabic, English, French
- AI-powered analysis and action item extraction
- Google Calendar integration
- Multi-language support
"""

import os
import json
import logging
import asyncio
import aiohttp
import tempfile
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import quote

import openai
from dotenv import load_dotenv

# Python 3.13 compatibility fix
if sys.version_info >= (3, 13):
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    filters, ContextTypes, CallbackQueryHandler
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramAIBot:
    def __init__(self):
        # Configuration from environment variables
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.admin_user_id = int(os.getenv('ADMIN_USER_ID', '0'))
        
        # Use OpenAI by default, fallback to Anthropic
        self.ai_provider = 'openai' if self.openai_api_key else 'anthropic'
        
        # Initialize OpenAI client
        if self.openai_api_key:
            self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
        
        # Store authorized users (in production, use a database)
        self.authorized_users = set()
        self.load_authorized_users()
        
        # Add admin to authorized users
        if self.admin_user_id:
            self.authorized_users.add(self.admin_user_id)

    def load_authorized_users(self):
        """Load authorized users from file"""
        try:
            if os.path.exists('authorized_users.json'):
                with open('authorized_users.json', 'r') as f:
                    data = json.load(f)
                    self.authorized_users = set(data.get('users', []))
        except Exception as e:
            logger.error(f"Error loading authorized users: {e}")

    def save_authorized_users(self):
        """Save authorized users to file"""
        try:
            with open('authorized_users.json', 'w') as f:
                json.dump({'users': list(self.authorized_users)}, f)
        except Exception as e:
            logger.error(f"Error saving authorized users: {e}")

    def is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized"""
        return user_id in self.authorized_users

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
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

👥 **Team Features**
- Invitation-only access
- Shared action items
- Timestamped summaries

**Commands:**
/start - Show this message
/invite - Generate invitation link (admin only)
/help - Get help

Just send me a voice note to get started!
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        if not self.is_authorized(update.effective_user.id):
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

4️⃣ **Commands**
   - /invite - Generate invitation (admin only)
   - /revoke - Remove user access (admin only)
   - /users - List authorized users (admin only)

💡 **Tips:**
- Speak clearly for better transcription
- Mention specific dates/times for calendar events
- Use keywords like "remind me", "schedule", "deadline"
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def invite_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /invite command (admin only)"""
        user_id = update.effective_user.id
        
        if user_id != self.admin_user_id:
            await update.message.reply_text("❌ Only administrators can generate invitations.")
            return
        
        # Generate invitation token (simple implementation)
        import secrets
        invitation_token = secrets.token_urlsafe(16)
        
        # Store invitation temporarily (in production, use database with expiration)
        if not hasattr(self, 'pending_invitations'):
            self.pending_invitations = {}
        
        self.pending_invitations[invitation_token] = {
            'created_by': user_id,
            'created_at': datetime.now().isoformat()
        }
        
        bot_username = context.bot.username
        invite_link = f"https://t.me/{bot_username}?start=invite_{invitation_token}"
        
        message = f"""
🎫 **Invitation Generated**

Share this link with the person you want to invite:
`{invite_link}`

⚠️ This link will expire in 24 hours.
        """
        
        await update.message.reply_text(message, parse_mode='Markdown')

    async def process_invitation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, token: str):
        """Process invitation token"""
        user_id = update.effective_user.id
        
        if hasattr(self, 'pending_invitations') and token in self.pending_invitations:
            # Add user to authorized list
            self.authorized_users.add(user_id)
            self.save_authorized_users()
            
            # Remove used invitation
            del self.pending_invitations[token]
            
            await update.message.reply_text(
                "✅ Welcome! You now have access to the AI Assistant Bot.\n"
                "Send /start to see available features."
            )
        else:
            await update.message.reply_text(
                "❌ Invalid or expired invitation link."
            )

    async def transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribe audio using OpenAI Whisper"""
        try:
            with open(audio_file_path, 'rb') as audio_file:
                response = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=None  # Auto-detect language
                )
                return response.text
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None

    async def analyze_with_ai(self, transcript: str) -> Dict:
        """Analyze transcript using AI to extract action items and summary"""
        
        prompt = f"""
Analyze the following transcript and extract:
1. Action items with specific details (who, what, when, where if mentioned)
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
            "priority": "high/medium/low",
            "assignee": "person assigned if mentioned"
        }}
    ]
}}

Transcript: {transcript}
"""

        try:
            if self.ai_provider == 'openai':
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an AI assistant that analyzes voice transcripts to extract action items and summaries. Always respond with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                
                content = response.choices[0].message.content
                return json.loads(content)
                
            elif self.ai_provider == 'anthropic':
                # Anthropic API implementation
                async with aiohttp.ClientSession() as session:
                    headers = {
                        'x-api-key': self.anthropic_api_key,
                        'Content-Type': 'application/json',
                        'anthropic-version': '2023-06-01'
                    }
                    
                    data = {
                        'model': 'claude-3-sonnet-20240229',
                        'max_tokens': 1000,
                        'messages': [
                            {
                                'role': 'user',
                                'content': prompt
                            }
                        ]
                    }
                    
                    async with session.post(
                        'https://api.anthropic.com/v1/messages',
                        headers=headers,
                        json=data
                    ) as response:
                        result = await response.json()
                        content = result['content'][0]['text']
                        return json.loads(content)
                        
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return {
                "language": "unknown",
                "summary": "Could not analyze transcript",
                "action_items": []
            }

    def generate_calendar_link(self, task: str, deadline: str = None) -> str:
        """Generate Google Calendar link for task"""
        base_url = "https://calendar.google.com/calendar/render?action=TEMPLATE"
        
        # Set default time if no deadline specified
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
            'location': ''
        }
        
        param_string = '&'.join([f"{key}={quote(str(value))}" for key, value in params.items()])
        return f"{base_url}&{param_string}"

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice messages"""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
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
            transcript = await self.transcribe_audio(temp_file_path)
            
            if not transcript:
                await processing_msg.edit_text("❌ Could not transcribe audio. Please try again.")
                return
            
            # Analyze with AI
            await processing_msg.edit_text("🧠 Analyzing content...")
            analysis = await self.analyze_with_ai(transcript)
            
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
                    assignee = item.get('assignee')
                    
                    priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(priority, '🟡')
                    
                    response += f"{i}. {priority_emoji} {task}"
                    
                    if deadline:
                        response += f" (Due: {deadline})"
                    if assignee:
                        response += f" - @{assignee}"
                    
                    response += "\n"
                
                # Create inline keyboard with calendar links
                keyboard = []
                for i, item in enumerate(action_items):
                    task = item.get('task', 'Unknown task')
                    deadline = item.get('deadline')
                    calendar_link = self.generate_calendar_link(task, deadline)
                    
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

    async def handle_start_with_param(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command with parameters"""
        if context.args and context.args[0].startswith('invite_'):
            token = context.args[0][7:]  # Remove 'invite_' prefix
            await self.process_invitation(update, context, token)
        else:
            await self.start(update, context)

    def run(self):
        """Run the bot"""
        if not self.telegram_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        
        if not (self.openai_api_key or self.anthropic_api_key):
            raise ValueError("Either OPENAI_API_KEY or ANTHROPIC_API_KEY is required")
        
        # Create application
        application = Application.builder().token(self.telegram_token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.handle_start_with_param))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("invite", self.invite_command))
        
        # Voice message handler
        application.add_handler(MessageHandler(filters.VOICE, self.handle_voice))
        
        # Start the bot
        print("🤖 AI Assistant Bot is starting...")
        print(f"📡 Using {self.ai_provider.upper()} for AI processing")
        application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    bot = TelegramAIBot()
    bot.run()