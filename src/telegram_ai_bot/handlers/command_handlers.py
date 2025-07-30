"""Command handlers for the bot"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes

logger = logging.getLogger(__name__)

def get_start_handler(user_manager, config):
    """Create start command handler"""
    
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        user_id = user.id
        
        # Check if user is admin
        is_admin = str(user_id) == config.ADMIN_USER_ID
        
        # Auto-add admin if not already in the list
        if is_admin and not user_manager.is_authorized(user_id):
            user_manager.add_user(user_id)
            
        # Check authorization
        if user_manager.is_authorized(user_id):
            welcome_message = f"""
🤖 Welcome {user.first_name}!

I'm your AI-powered personal assistant. Here's what I can do:

🎤 **Voice Processing**: Send me voice notes in Arabic, English, or French
📝 **Smart Analysis**: I'll extract action items and key points
📅 **Calendar Integration**: One-click scheduling to Google Calendar
🔒 **Secure Access**: Invitation-only system for your team

**How to use:**
1. Send me a voice message
2. I'll transcribe and analyze it
3. Click calendar links to schedule tasks

Type /help for more commands.
"""
            await update.message.reply_text(welcome_message)
        else:
            await update.message.reply_text(
                "❌ Access denied. This bot is invitation-only.\n"
                "Please contact an administrator for access."
            )
            
    return CommandHandler('start', start_command)

def get_help_handler():
    """Create help command handler"""
    
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """
📚 **Available Commands:**

/start - Initialize bot and check access
/help - Show this help message
/invite - Generate invitation link (admin only)
/stats - Show bot statistics (admin only)

**Voice Note Tips:**
• Speak clearly at a normal pace
• Mention specific dates for deadlines
• Use action words like "remind me", "schedule"
• Say "high priority" for urgent tasks

**Supported Languages:**
🇬🇧 English
🇸🇦 Arabic
🇫🇷 French

Need help? Contact your administrator.
"""
        await update.message.reply_text(help_text)
        
    return CommandHandler('help', help_command)

def get_invite_handler(user_manager, config):
    """Create invite command handler"""
    
    async def invite_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        # Check if user is admin
        if str(user_id) != config.ADMIN_USER_ID:
            await update.message.reply_text("❌ Only administrators can generate invitation links.")
            return
            
        # Generate invitation token
        token = user_manager.generate_invite_token(user_id)
        
        # Create deep link
        bot_username = (await context.bot.get_me()).username
        invite_link = f"https://t.me/{bot_username}?start=invite_{token}"
        
        # Create inline keyboard with the link
        keyboard = [[InlineKeyboardButton("🔗 Share Invitation Link", url=invite_link)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"📨 **Invitation Link Generated**\n\n"
            f"Share this link with new team members:\n"
            f"`{invite_link}`\n\n"
            f"This link will grant access to the bot.",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    return CommandHandler('invite', invite_command)

def get_callback_handler(user_manager):
    """Create callback query handler for invitation links"""
    
    async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        # Handle invitation acceptance
        if query.data.startswith('accept_invite_'):
            user_id = update.effective_user.id
            
            if user_manager.add_user(user_id):
                await query.message.edit_text(
                    "✅ Welcome! You now have access to the bot.\n"
                    "Send /start to begin."
                )
            else:
                await query.message.edit_text(
                    "You already have access to the bot."
                )
                
    return CallbackQueryHandler(handle_callback)