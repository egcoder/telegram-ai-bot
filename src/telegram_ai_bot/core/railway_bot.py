"""
Railway-specific bot implementation with health check support
"""
import asyncio
import logging
from aiohttp import web
from telegram.ext import Application
from telegram_ai_bot.core.bot import TelegramAIBot

logger = logging.getLogger(__name__)

class RailwayBot(TelegramAIBot):
    """Extended bot class with Railway health check support"""
    
    async def health_handler(self, request):
        """Health check endpoint for Railway"""
        return web.json_response({
            'status': 'healthy',
            'service': 'telegram-ai-bot',
            'bot_running': self.application is not None
        })
    
    async def webhook_handler(self, request):
        """Handle incoming webhook updates"""
        if not self.application:
            return web.Response(status=503, text="Bot not initialized")
        
        # Get the update data
        data = await request.read()
        
        # Process the update through the bot
        await self.application.update_queue.put(
            await self.application.bot.de_json(data, self.application.bot)
        )
        
        return web.Response(text="OK")
    
    async def run_webhook_with_health(self, webhook_url: str, port: int = 8000, host: str = '0.0.0.0'):
        """Run webhook with integrated health check endpoint"""
        if not self.application:
            await self.initialize()
        
        # Initialize the application
        await self.application.initialize()
        await self.application.start()
        
        # Create web app for both webhook and health check
        app = web.Application()
        app.router.add_post('/', self.webhook_handler)
        app.router.add_get('/health', self.health_handler)
        
        # Set the webhook
        await self.application.bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True
        )
        
        logger.info(f"Bot running with webhook at {webhook_url}")
        logger.info(f"Health check available at http://{host}:{port}/health")
        
        # Start the web server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        # Keep running
        try:
            await asyncio.Event().wait()
        finally:
            await runner.cleanup()
            await self.shutdown()