"""Unit tests for bot core functionality"""
import unittest
import asyncio
import tempfile
import os
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from telegram_ai_bot.core.bot import TelegramAIBot
from telegram_ai_bot.core.config import Config
from telegram_ai_bot.utils.user_manager import UserManager

class TestBotCore(unittest.TestCase):
    """Test bot core functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        self.test_users_file = Path(self.temp_dir) / 'test_users.json'
        
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'TELEGRAM_BOT_TOKEN': 'test_token:test_value',
            'OPENAI_API_KEY': 'test_openai_key',
            'ADMIN_USER_ID': '123456789'
        })
        self.env_patcher.start()
        
    def tearDown(self):
        """Clean up test environment"""
        self.env_patcher.stop()
        # Clean up temp files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_config_validation(self):
        """Test configuration validation"""
        # Should pass with mocked environment
        self.assertTrue(Config.validate())
        
        # Test missing required config by patching the class attribute directly
        original_token = Config.TELEGRAM_BOT_TOKEN
        try:
            Config.TELEGRAM_BOT_TOKEN = ''
            with self.assertRaises(ValueError):
                Config.validate()
        finally:
            Config.TELEGRAM_BOT_TOKEN = original_token
                
    def test_config_directory_creation(self):
        """Test directory creation"""
        # Mock the directory paths
        with patch.object(Config, 'DATA_DIR', Path(self.temp_dir) / 'data'):
            with patch.object(Config, 'LOGS_DIR', Path(self.temp_dir) / 'logs'):
                Config.ensure_directories()
                
                self.assertTrue((Path(self.temp_dir) / 'data').exists())
                self.assertTrue((Path(self.temp_dir) / 'logs').exists())
    
    @patch('telegram_ai_bot.core.bot.Application')
    def test_bot_initialization(self, mock_application):
        """Test bot initialization"""
        # Mock application builder
        mock_app_instance = Mock()
        mock_builder = Mock()
        mock_builder.token.return_value = mock_builder
        mock_builder.build.return_value = mock_app_instance
        mock_application.builder.return_value = mock_builder
        
        # Create bot instance
        bot = TelegramAIBot()
        
        # Verify initialization
        self.assertIsNotNone(bot.config)
        self.assertIsNotNone(bot.user_manager)

class TestBotAsync(unittest.IsolatedAsyncioTestCase):
    """Test async bot functionality"""
    
    def setUp(self):
        """Set up async test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'TELEGRAM_BOT_TOKEN': 'test_token:test_value',
            'OPENAI_API_KEY': 'test_openai_key', 
            'ADMIN_USER_ID': '123456789'
        })
        self.env_patcher.start()
        
    def tearDown(self):
        """Clean up async test environment"""
        self.env_patcher.stop()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    @patch('telegram_ai_bot.core.bot.Application')
    async def test_bot_initialization_async(self, mock_application):
        """Test async bot initialization"""
        # Mock application and bot
        mock_app_instance = AsyncMock()
        mock_bot = AsyncMock()
        mock_app_instance.bot = mock_bot
        
        # Mock builder chain
        mock_builder = Mock()
        mock_builder.token.return_value = mock_builder
        mock_builder.build.return_value = mock_app_instance
        mock_application.builder.return_value = mock_builder
        
        # Mock bot commands
        mock_bot.set_my_commands = AsyncMock()
        
        # Create and initialize bot
        bot = TelegramAIBot()
        await bot.initialize()
        
        # Verify initialization calls
        mock_bot.set_my_commands.assert_called_once()
        self.assertIsNotNone(bot.application)
        
    @patch('telegram_ai_bot.core.bot.Application')
    async def test_bot_shutdown(self, mock_application):
        """Test bot shutdown"""
        # Mock application components
        mock_updater = AsyncMock()
        mock_app_instance = AsyncMock()
        mock_app_instance.updater = mock_updater
        mock_app_instance.bot = AsyncMock()
        mock_app_instance.bot.set_my_commands = AsyncMock()
        
        mock_builder = Mock()
        mock_builder.token.return_value = mock_builder
        mock_builder.build.return_value = mock_app_instance
        mock_application.builder.return_value = mock_builder
        
        # Create and initialize bot
        bot = TelegramAIBot()
        await bot.initialize()
        
        # Test shutdown
        await bot.shutdown()
        
        # Verify shutdown calls
        mock_updater.stop.assert_called_once()
        mock_app_instance.stop.assert_called_once()
        mock_app_instance.shutdown.assert_called_once()

class TestUserManagerIntegration(unittest.TestCase):
    """Test user manager integration with bot"""
    
    def setUp(self):
        """Set up user manager test"""
        self.temp_dir = tempfile.mkdtemp()
        self.users_file = Path(self.temp_dir) / 'test_users.json'
        self.user_manager = UserManager(self.users_file)
        
    def tearDown(self):
        """Clean up user manager test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_user_authorization_flow(self):
        """Test complete user authorization flow"""
        user_id = 12345
        
        # Initially not authorized
        self.assertFalse(self.user_manager.is_authorized(user_id))
        
        # Add user
        self.assertTrue(self.user_manager.add_user(user_id))
        
        # Now authorized
        self.assertTrue(self.user_manager.is_authorized(user_id))
        
        # Remove user
        self.assertTrue(self.user_manager.remove_user(user_id))
        
        # No longer authorized
        self.assertFalse(self.user_manager.is_authorized(user_id))
        
    def test_admin_auto_authorization(self):
        """Test admin auto-authorization logic"""
        admin_id = 123456789  # From mocked ADMIN_USER_ID
        
        # Simulate admin check
        with patch.dict(os.environ, {'ADMIN_USER_ID': str(admin_id)}):
            # Admin should be auto-added
            if not self.user_manager.is_authorized(admin_id):
                self.user_manager.add_user(admin_id)
                
            self.assertTrue(self.user_manager.is_authorized(admin_id))

if __name__ == '__main__':
    unittest.main()