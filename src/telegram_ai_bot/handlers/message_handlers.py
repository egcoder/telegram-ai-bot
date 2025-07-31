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
from ..version import DEPLOY_VERSION

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
            logger.info(f"Voice file info - File ID: {voice_file.file_id}, Size: {voice_file.file_size}")
            
            # Create temporary file for audio - try .wav extension for better compatibility
            with tempfile.NamedTemporaryFile(
                suffix='.wav', 
                delete=False
            ) as tmp_file:
                audio_path = Path(tmp_file.name)
                await voice_file.download_to_drive(audio_path)
                
            # Verify file was downloaded
            if not audio_path.exists():
                raise Exception(f"Failed to download voice file to {audio_path}")
                
            file_size = audio_path.stat().st_size
            logger.info(f"Downloaded voice file: {audio_path}, Size: {file_size} bytes")
            
            if file_size == 0:
                raise Exception("Downloaded voice file is empty")
                
            # Initialize AI service
            ai_service = config.get_ai_service()
            
            # Transcribe audio
            await processing_msg.edit_text("📝 Transcribing audio...")
            logger.info(f"About to transcribe file: {audio_path}")
            transcript = await ai_service.transcribe_audio(audio_path)
            logger.info(f"Transcription completed. Length: {len(transcript) if transcript else 0} chars")
            
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
            try:
                os.unlink(audio_path)
                logger.info(f"Cleaned up temporary file: {audio_path}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp file: {cleanup_error}")
            
        except Exception as e:
            logger.error(f"Error processing voice message: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Clean up temp file even on error
            try:
                if 'audio_path' in locals():
                    os.unlink(audio_path)
                    logger.info(f"Cleaned up temporary file after error: {audio_path}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp file after error: {cleanup_error}")
            
            # Safely get OpenAI version
            openai_version = "checking..."
            try:
                import openai as openai_module
                openai_version = openai_module.__version__
            except Exception as import_err:
                openai_version = f"import error: {import_err}"
            
            # Check if it's the specific response_format error
            error_str = str(e)
            if "response_format" in error_str and "json_object" in error_str:
                error_msg = "Whisper API received invalid response_format parameter"
            else:
                error_msg = str(e)[:300]
            
            error_message = (
                f"❌ Sorry, I couldn't process your voice message.\n"
                f"Error: {error_msg}\n\n"
                f"Debug info:\n"
                f"- Bot version: v{DEPLOY_VERSION}\n"
                f"- OpenAI lib: v{openai_version}\n"
                f"- Error type: {type(e).__name__}\n"
                f"- Deploy time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
                f"Please try again or contact support if the issue persists."
            )
            await processing_msg.edit_text(error_message)
            
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
        user_id = update.effective_user.id
        
        # Check user access
        if not user_manager.is_user_allowed(user_id):
            await update.message.reply_text(
                "❌ You don't have access to this bot.\n"
                "Please contact the administrator for access."
            )
            return
            
        try:
            # Get the user's message
            user_message = update.message.text
            user_name = update.effective_user.first_name or "User"
            
            # Send typing indicator
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action="typing"
            )
            
            # Get AI service from config
            ai_service = config.get_ai_service()
            
            # For text messages, we'll use the AI to respond directly
            response = await ai_service.get_chat_response(user_message, user_name)
            
            # Send the response
            await update.message.reply_text(response)
            
        except AttributeError:
            # If get_chat_response doesn't exist, fall back to analyze_text
            try:
                analysis = await ai_service.analyze_text(user_message, user_name)
                
                # Format the analysis
                response = f"📝 **Analysis:**\n\n"
                response += f"**Summary:** {analysis.get('summary', 'No summary available')}\n\n"
                
                if analysis.get('action_items'):
                    response += "**Action Items:**\n"
                    for item in analysis['action_items']:
                        response += f"• {item}\n"
                
                await update.message.reply_text(response, parse_mode='Markdown')
                
            except Exception as e:
                logger.error(f"Error processing text message: {e}")
                await update.message.reply_text(
                    "I'm sorry, I couldn't process your message. Please try again."
                )
        except Exception as e:
            logger.error(f"Error processing text message: {e}")
            await update.message.reply_text(
                "❌ Sorry, I couldn't process your message. Please try again."
            )
        
    return MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_text
    )