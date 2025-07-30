"""Message handlers for voice and text processing"""
import logging
import tempfile
import os
from pathlib import Path
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import MessageHandler, filters, ContextTypes

from ..utils.ai_service import AIService
from ..utils.calendar_utils import format_action_items_for_calendar

logger = logging.getLogger(__name__)

def get_voice_handler(user_manager, config):
    """Create voice message handler"""
    
    async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        user_id = user.id
        
        # Check authorization
        if not user_manager.is_authorized(user_id):
            await update.message.reply_text(
                "❌ You are not authorized to use this bot."
            )
            return
            
        # Send processing message
        processing_msg = await update.message.reply_text(
            "🎤 Processing your voice message..."
        )
        
        try:
            # Download voice file
            voice_file = await update.message.voice.get_file()
            
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(
                suffix='.ogg', 
                delete=False
            ) as tmp_file:
                audio_path = Path(tmp_file.name)
                await voice_file.download_to_drive(audio_path)
                
            # Initialize AI service
            ai_service = AIService(config.OPENAI_API_KEY, config.GPT_MODEL)
            
            # Transcribe audio
            await processing_msg.edit_text("📝 Transcribing audio...")
            transcript = await ai_service.transcribe_audio(audio_path)
            
            # Analyze content
            await processing_msg.edit_text("🧠 Analyzing content...")
            analysis = await ai_service.analyze_text(
                transcript, 
                user.first_name or "User"
            )
            
            # Format action items with calendar links
            if 'action_items' in analysis:
                analysis['action_items'] = format_action_items_for_calendar(
                    analysis['action_items']
                )
            
            # Create response message
            response = _format_analysis_response(
                user.first_name or "User",
                transcript,
                analysis
            )
            
            # Create inline keyboard for action items
            keyboard = _create_action_items_keyboard(analysis.get('action_items', []))
            
            # Send final response
            await processing_msg.edit_text(
                response,
                parse_mode='Markdown',
                reply_markup=keyboard if keyboard else None,
                disable_web_page_preview=True
            )
            
            # Clean up temporary file
            os.unlink(audio_path)
            
        except Exception as e:
            logger.error(f"Error processing voice message: {e}")
            await processing_msg.edit_text(
                "❌ Sorry, I couldn't process your voice message. "
                "Please try again or contact support if the issue persists."
            )
            
    return MessageHandler(filters.VOICE, handle_voice)

def _format_analysis_response(user_name: str, transcript: str, analysis: dict) -> str:
    """Format the analysis response message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    response = f"""📊 **Voice Note Analysis**
👤 From: {user_name}
🕐 Time: {timestamp}

**📝 Transcript:**
_{transcript}_

**📋 Summary:**
{analysis.get('summary', 'No summary available')}
"""
    
    # Add action items if present
    action_items = analysis.get('action_items', [])
    if action_items:
        response += "\n**✅ Action Items:**\n"
        for i, item in enumerate(action_items, 1):
            priority_emoji = {
                'high': '🔴',
                'medium': '🟡', 
                'low': '🟢'
            }.get(item.get('priority', 'medium').lower(), '🟡')
            
            response += f"\n{i}. {priority_emoji} {item['task']}"
            if item.get('deadline'):
                response += f"\n   📅 Deadline: {item['deadline']}"
                
    # Add topics if present
    topics = analysis.get('topics', [])
    if topics:
        response += f"\n\n**🏷️ Topics:** {', '.join(topics)}"
        
    return response

def _create_action_items_keyboard(action_items: list) -> InlineKeyboardMarkup:
    """Create inline keyboard for action items"""
    if not action_items:
        return None
        
    keyboard = []
    
    for i, item in enumerate(action_items):
        if item.get('calendar_link'):
            keyboard.append([
                InlineKeyboardButton(
                    f"📅 Schedule: {item['task'][:30]}...",
                    url=item['calendar_link']
                )
            ])
            
    return InlineKeyboardMarkup(keyboard) if keyboard else None

def get_text_handler(user_manager, config):
    """Create text message handler for non-voice messages"""
    
    async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # For now, just inform users to send voice messages
        await update.message.reply_text(
            "🎤 Please send voice messages for processing.\n"
            "I can transcribe and analyze voice notes in Arabic, English, and French."
        )
        
    return MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_text
    )