"""Core bot class and initialization"""
import logging
import json
from pathlib import Path
from typing import Set, Optional

from telegram.ext import Application
from telegram import BotCommand

from .config import Config
from ..handlers import command_handlers, message_handlers
from ..utils.user_manager import UserManager

logger = logging.getLogger(__name__)

class TelegramAIBot:
    """Main bot class that orchestrates all functionality"""
    
    def __init__(self):
        self.config = Config()
        self.config.validate()
        Config.ensure_directories()
        
        self.user_manager = UserManager(self.config.AUTHORIZED_USERS_FILE)
        self.application: Optional[Application] = None
        
    async def initialize(self):
        """Initialize the bot application"""
        self.application = (
            Application.builder()
            .token(self.config.TELEGRAM_BOT_TOKEN)
            .build()
        )
        
        # Set up commands
        await self._setup_commands()
        
        # Register handlers
        self._register_handlers()
        
        logger.info("Bot initialized successfully")
        
    async def _setup_commands(self):
        """Set up bot commands visible in Telegram"""
        commands = [
            BotCommand("start", "Start the bot and check access"),
            BotCommand("help", "Show help information"),
            BotCommand("invite", "Generate invitation link (admin only)"),
            BotCommand("stats", "Show bot statistics (admin only)"),
        ]
        
        await self.application.bot.set_my_commands(commands)
        
    def _register_handlers(self):
        """Register all message and command handlers"""
        # Command handlers
        self.application.add_handler(
            command_handlers.get_start_handler(self.user_manager, self.config)
        )
        self.application.add_handler(
            command_handlers.get_help_handler()
        )
        self.application.add_handler(
            command_handlers.get_invite_handler(self.user_manager, self.config)
        )
        
        # Message handlers
        self.application.add_handler(
            message_handlers.get_voice_handler(self.user_manager, self.config)
        )
        
        # Callback query handler for invitation links
        self.application.add_handler(
            command_handlers.get_callback_handler(self.user_manager)
        )
        
    async def run_polling(self):
        """Run the bot with polling (for development)"""
        if not self.application:
            await self.initialize()
            
        logger.info("Starting bot with polling...")
        
        # Start the bot
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(drop_pending_updates=True)
        
        logger.info("Bot is running with polling. Press Ctrl+C to stop.")
        
        # Keep the bot running
        try:
            import asyncio
            await asyncio.create_task(asyncio.sleep(float('inf')))
        except KeyboardInterrupt:
            logger.info("Stopping bot...")
            await self.shutdown()
            
    async def run_webhook(self, webhook_url: str, port: int = 8000, host: str = '0.0.0.0'):
        """Run the bot with webhook (for production)"""
        if not self.application:
            await self.initialize()
            
        logger.info(f"Starting bot with webhook: {webhook_url}:{port}")
        
        # Start the bot
        await self.application.initialize()
        await self.application.start()
        
        # Start webhook
        await self.application.updater.start_webhook(
            listen=host,
            port=port,
            webhook_url=webhook_url,
            drop_pending_updates=True
        )
        
        logger.info(f"Bot is running with webhook on {host}:{port}")
        
        # Keep the bot running
        try:
            import asyncio
            await asyncio.create_task(asyncio.sleep(float('inf')))
        except KeyboardInterrupt:
            logger.info("Stopping bot...")
            await self.shutdown()
            
    async def run(self):
        """Run the bot (legacy method - uses polling)"""
        await self.run_polling()
            
    async def shutdown(self):
        """Gracefully shutdown the bot"""
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            logger.info("Bot stopped successfully")