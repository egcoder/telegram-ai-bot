#!/usr/bin/env python3
"""
Simple Railway entry point for Telegram AI Bot
Direct environment variable access for Railway compatibility
"""
import os
import sys
import asyncio
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def validate_environment():
    """Validate required environment variables"""
    required_vars = {
        'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'), 
        'ADMIN_USER_ID': os.getenv('ADMIN_USER_ID')
    }
    
    logger.info(f"🔍 Checking environment variables...")
    for var_name, var_value in required_vars.items():
        if var_value:
            logger.info(f"✅ {var_name}: Set (length: {len(var_value)})")
        else:
            logger.error(f"❌ {var_name}: Missing or empty")
    
    missing = [name for name, value in required_vars.items() if not value]
    if missing:
        raise ValueError(f"Missing required environment variables: {missing}")
    
    return required_vars

async def main():
    """Main entry point for Railway deployment"""
    try:
        logger.info("🚂 Starting Telegram AI Bot on Railway...")
        
        # Validate environment variables first
        env_vars = validate_environment()
        logger.info("✅ All environment variables validated")
        
        # Import after validation to avoid config loading issues
        from telegram_ai_bot.core.bot import TelegramAIBot
        
        # Create directories
        os.makedirs('data', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # Initialize bot
        logger.info("🤖 Initializing bot...")
        bot = TelegramAIBot()
        
        # Check if running on Railway (has PORT environment variable)
        port = os.getenv('PORT')
        
        if port:
            # Railway deployment with webhook
            railway_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN')
            railway_static = os.getenv('RAILWAY_STATIC_URL')
            
            if railway_domain:
                webhook_url = f"https://{railway_domain}"
            elif railway_static:
                webhook_url = f"https://{railway_static}"
            else:
                webhook_url = f"https://web-production-938f0.up.railway.app"
            
            logger.info(f"🌐 Starting with webhook mode on Railway")
            logger.info(f"📡 Webhook URL: {webhook_url}")
            logger.info(f"🔌 Port: {port}")
            
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
            
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot failed to start: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # Railway environment detection
    if os.getenv('RAILWAY_ENVIRONMENT'):
        logger.info("🚂 Running on Railway")
    elif os.getenv('PORT'):
        logger.info("🌐 Running in container environment")
    else:
        logger.info("💻 Running locally")
    
    # Run the bot
    asyncio.run(main())