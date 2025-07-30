"""Main entry point for the Telegram AI Bot"""
import sys
import asyncio
import logging

from .core.bot import TelegramAIBot
from .core.config import Config

# Configure logging
logging.basicConfig(
    format=Config.LOG_FORMAT,
    level=getattr(logging, Config.LOG_LEVEL)
)

logger = logging.getLogger(__name__)

async def main():
    """Main function to run the bot"""
    try:
        # Create and run the bot
        bot = TelegramAIBot()
        await bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Python 3.13 compatibility
    if sys.version_info >= (3, 13):
        import warnings
        warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    # Run the bot
    asyncio.run(main())