"""Integration tests for message handlers"""
import unittest
import asyncio
import tempfile
import os
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from telegram import Update, Message, User, Voice, Bot
from telegram.ext import ContextTypes
from telegram_ai_bot.handlers.message_handlers import get_voice_handler
from telegram_ai_bot.handlers.command_handlers import get_start_handler, get_help_handler
from telegram_ai_bot.utils.user_manager import UserManager
from telegram_ai_bot.core.config import Config

class TestMessageHandlers(unittest.IsolatedAsyncioTestCase):
    """Test message handlers integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.users_file = Path(self.temp_dir) / 'test_users.json'
        
        # Create test user manager
        self.user_manager = UserManager(self.users_file)
        
        # Mock config
        self.mock_config = Mock()
        self.mock_config.OPENAI_API_KEY = 'test_key'
        self.mock_config.GPT_MODEL = 'gpt-4'
        self.mock_config.ADMIN_USER_ID = '123456789'
        
        # Mock environment
        self.env_patcher = patch.dict(os.environ, {
            'TELEGRAM_BOT_TOKEN': 'test_token:test_value',
            'OPENAI_API_KEY': 'test_openai_key',
            'ADMIN_USER_ID': '123456789'
        })
        self.env_patcher.start()
        
    def tearDown(self):
        """Clean up test environment"""
        self.env_patcher.stop()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def create_mock_update(self, user_id=12345, message_text=None, voice_file=None):
        """Create a mock Telegram update"""
        # Create mock user
        user = Mock(spec=User)
        user.id = user_id
        user.first_name = "TestUser"
        
        # Create mock message
        message = Mock(spec=Message)
        message.from_user = user
        message.reply_text = AsyncMock()
        
        if message_text:
            message.text = message_text
            
        if voice_file:
            voice = Mock(spec=Voice)
            voice.get_file = AsyncMock(return_value=voice_file)
            message.voice = voice
            
        # Create mock update
        update = Mock(spec=Update)
        update.effective_user = user
        update.message = message
        
        return update
        
    def create_mock_context(self):
        """Create a mock context"""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.bot = Mock(spec=Bot)
        return context

    async def test_start_command_authorized_user(self):
        """Test start command for authorized user"""
        user_id = 12345
        self.user_manager.add_user(user_id)
        
        # Get handler
        handler = get_start_handler(self.user_manager, self.mock_config)
        
        # Create mocks
        update = self.create_mock_update(user_id)
        context = self.create_mock_context()
        
        # Execute handler
        await handler.callback(update, context)
        
        # Verify welcome message was sent
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args[0][0]
        self.assertIn("Welcome", call_args)
        
    async def test_start_command_unauthorized_user(self):
        """Test start command for unauthorized user"""
        user_id = 99999  # Not in authorized users
        
        # Get handler
        handler = get_start_handler(self.user_manager, self.mock_config)
        
        # Create mocks
        update = self.create_mock_update(user_id)
        context = self.create_mock_context()
        
        # Execute handler
        await handler.callback(update, context)
        
        # Verify access denied message
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args[0][0]
        self.assertIn("Access denied", call_args)
        
    async def test_start_command_admin_auto_add(self):
        """Test admin user auto-addition on start"""
        admin_id = 123456789  # From mock config
        
        # Ensure admin not initially in list
        self.assertFalse(self.user_manager.is_authorized(admin_id))
        
        # Get handler
        handler = get_start_handler(self.user_manager, self.mock_config)
        
        # Create mocks
        update = self.create_mock_update(admin_id)
        context = self.create_mock_context()
        
        # Execute handler
        await handler.callback(update, context)
        
        # Verify admin was auto-added
        self.assertTrue(self.user_manager.is_authorized(admin_id))
        
        # Verify welcome message was sent
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args[0][0]
        self.assertIn("Welcome", call_args)

    async def test_help_command(self):
        """Test help command"""
        handler = get_help_handler()
        
        # Create mocks
        update = self.create_mock_update()
        context = self.create_mock_context()
        
        # Execute handler
        await handler.callback(update, context)
        
        # Verify help message
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args[0][0]
        self.assertIn("Available Commands", call_args)
        
    @patch('telegram_ai_bot.handlers.message_handlers.AIService')
    @patch('tempfile.NamedTemporaryFile')
    @patch('os.unlink')
    async def test_voice_message_processing(self, mock_unlink, mock_tempfile, mock_ai_service):
        """Test voice message processing flow"""
        # Set up authorized user
        user_id = 12345
        self.user_manager.add_user(user_id)
        
        # Mock temporary file
        mock_temp = Mock()
        mock_temp.name = '/tmp/test_audio.ogg'
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        
        # Mock voice file
        mock_voice_file = Mock()
        mock_voice_file.download_to_drive = AsyncMock()
        
        # Mock AI service
        mock_ai_instance = Mock()
        mock_ai_instance.transcribe_audio = AsyncMock(return_value="Test transcript")
        mock_ai_instance.analyze_text = AsyncMock(return_value={
            "summary": "Test summary",
            "action_items": [
                {"task": "Test task", "deadline": "tomorrow", "priority": "high"}
            ],
            "topics": ["test", "topic"]
        })
        mock_ai_service.return_value = mock_ai_instance
        
        # Get handler
        handler = get_voice_handler(self.user_manager, self.mock_config)
        
        # Create mocks
        update = self.create_mock_update(user_id, voice_file=mock_voice_file)
        context = self.create_mock_context()
        
        # Mock the processing message
        processing_msg = Mock()
        processing_msg.edit_text = AsyncMock()
        update.message.reply_text = AsyncMock(return_value=processing_msg)
        
        # Execute handler
        await handler.callback(update, context)
        
        # Verify flow
        mock_voice_file.download_to_drive.assert_called_once()
        mock_ai_instance.transcribe_audio.assert_called_once()
        mock_ai_instance.analyze_text.assert_called_once()
        
        # Verify processing messages
        self.assertEqual(processing_msg.edit_text.call_count, 3)  # Processing, transcribing, analyzing
        
        # Verify cleanup
        mock_unlink.assert_called_once()
        
    async def test_voice_message_unauthorized(self):
        """Test voice message from unauthorized user"""
        user_id = 99999  # Not authorized
        
        # Mock voice file
        mock_voice_file = Mock()
        
        # Get handler
        handler = get_voice_handler(self.user_manager, self.mock_config)
        
        # Create mocks
        update = self.create_mock_update(user_id, voice_file=mock_voice_file)
        context = self.create_mock_context()
        
        # Execute handler
        await handler.callback(update, context)
        
        # Verify unauthorized message
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args[0][0]
        self.assertIn("not authorized", call_args)

class TestHandlerRegistration(unittest.TestCase):
    """Test handler registration and configuration"""
    
    def test_command_handler_creation(self):
        """Test command handler creation"""
        temp_dir = tempfile.mkdtemp()
        users_file = Path(temp_dir) / 'test_users.json'
        user_manager = UserManager(users_file)
        
        mock_config = Mock()
        mock_config.ADMIN_USER_ID = '123456789'
        
        try:
            # Test handler creation
            start_handler = get_start_handler(user_manager, mock_config)
            help_handler = get_help_handler()
            
            # Verify handlers are created
            self.assertIsNotNone(start_handler)
            self.assertIsNotNone(help_handler)
            
            # Verify handler commands
            self.assertEqual(start_handler.commands, {'start'})
            self.assertEqual(help_handler.commands, {'help'})
            
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    def test_voice_handler_creation(self):
        """Test voice handler creation"""
        temp_dir = tempfile.mkdtemp()
        users_file = Path(temp_dir) / 'test_users.json'
        user_manager = UserManager(users_file)
        
        mock_config = Mock()
        mock_config.OPENAI_API_KEY = 'test_key'
        mock_config.GPT_MODEL = 'gpt-4'
        
        try:
            # Test handler creation
            voice_handler = get_voice_handler(user_manager, mock_config)
            
            # Verify handler is created
            self.assertIsNotNone(voice_handler)
            
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == '__main__':
    unittest.main()