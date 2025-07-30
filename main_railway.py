#!/usr/bin/env python3
"""
Railway-optimized entry point for Telegram AI Bot
Supports both webhook and polling modes
"""
import os
import sys
import asyncio
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from telegram_ai_bot.core.bot import TelegramAIBot
from telegram_ai_bot.core.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/bot.log') if Path('logs').exists() else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    """Main entry point for Railway deployment"""
    try:
        # Validate configuration
        Config.validate()
        Config.ensure_directories()
        
        # Initialize bot
        logger.info("🤖 Starting Telegram AI Bot on Railway...")
        bot = TelegramAIBot()
        
        # Check if running on Railway (has PORT environment variable)
        port = os.getenv('PORT')
        railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN')
        
        if port:
            # Railway deployment with webhook
            railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN')
            if railway_url:
                webhook_url = f"https://{railway_url}"
            else:
                # Fallback for Railway auto-generated URL
                webhook_url = f"https://{os.getenv('RAILWAY_STATIC_URL', 'localhost')}"
            
            logger.info(f"🌐 Starting with webhook mode on Railway: {webhook_url}")
            
            # Start with webhook
            await bot.run_webhook(
                webhook_url=webhook_url,
                port=int(port),
                host='0.0.0.0'
            )
        else:
            # Local development or fallback to polling
            logger.info("🔄 Starting with polling mode (development)")
            await bot.run_polling()
            
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Handle Railway's environment
    if os.getenv('RAILWAY_ENVIRONMENT'):
        logger.info("🚂 Running on Railway")
    
    # Run the bot
    asyncio.run(main())