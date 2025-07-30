#!/usr/bin/env python3
"""
End-to-End Test Script for Telegram AI Bot

This script tests the bot functionality by simulating real user interactions
without actually connecting to Telegram or external APIs.
"""
import os
import sys
import json
import asyncio
import tempfile
import logging
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from telegram_ai_bot.core.bot import TelegramAIBot
from telegram_ai_bot.core.config import Config
from telegram_ai_bot.utils.user_manager import UserManager
from telegram_ai_bot.utils.ai_service import AIService
from telegram import Update, Message, User, Voice, Bot

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BotE2ETest:
    """End-to-end bot testing class"""
    
    def __init__(self):
        self.temp_dir = None
        self.bot = None
        self.test_results = []
        
    def setup_test_environment(self):
        """Set up test environment"""
        logger.info("🔧 Setting up test environment...")
        
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        logger.info(f"Created temp directory: {self.temp_dir}")
        
        # Mock environment variables
        os.environ.update({
            'TELEGRAM_BOT_TOKEN': '123456789:ABCdefGHIjklMNOpqrsTUVwxyz123456789',
            'OPENAI_API_KEY': 'sk-test-key-12345',
            'ADMIN_USER_ID': '123456789',
            'LOG_LEVEL': 'INFO'
        })
        
        # Override config paths to use temp directory
        Config.DATA_DIR = Path(self.temp_dir) / 'data'
        Config.LOGS_DIR = Path(self.temp_dir) / 'logs'
        
        logger.info("✅ Test environment set up successfully")
        
    def cleanup_test_environment(self):
        """Clean up test environment"""
        if self.temp_dir:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            logger.info("🧹 Cleaned up test environment")
            
    def create_mock_update(self, user_id, message_text=None, voice_file=None, first_name="TestUser"):
        """Create a mock Telegram update"""
        user = Mock(spec=User)
        user.id = user_id
        user.first_name = first_name
        
        message = Mock(spec=Message)
        message.from_user = user
        message.reply_text = AsyncMock()
        
        if message_text:
            message.text = message_text
            
        if voice_file:
            voice = Mock(spec=Voice)
            voice.get_file = AsyncMock(return_value=voice_file)
            message.voice = voice
            
        update = Mock(spec=Update)
        update.effective_user = user
        update.message = message
        
        return update
        
    def create_mock_context(self):
        """Create a mock context"""
        from telegram.ext import ContextTypes
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.bot = Mock(spec=Bot)
        context.bot.get_me = AsyncMock()
        context.bot.get_me.return_value.username = "test_bot"
        return context
        
    async def test_bot_initialization(self):
        """Test bot initialization"""
        logger.info("🤖 Testing bot initialization...")
        
        try:
            with patch('telegram_ai_bot.core.bot.Application') as mock_app:
                # Mock application builder
                mock_app_instance = AsyncMock()
                mock_bot = AsyncMock()
                mock_app_instance.bot = mock_bot
                
                mock_builder = Mock()
                mock_builder.token.return_value = mock_builder
                mock_builder.build.return_value = mock_app_instance
                mock_app.builder.return_value = mock_builder
                
                # Create and initialize bot
                self.bot = TelegramAIBot()
                await self.bot.initialize()
                
                # Verify initialization
                assert self.bot.application is not None
                assert self.bot.user_manager is not None
                
                self.test_results.append(("Bot Initialization", "✅ PASS"))
                logger.info("✅ Bot initialization test passed")
                
        except Exception as e:
            self.test_results.append(("Bot Initialization", f"❌ FAIL: {e}"))
            logger.error(f"❌ Bot initialization test failed: {e}")
            
    async def test_user_authorization_flow(self):
        """Test complete user authorization flow"""
        logger.info("👤 Testing user authorization flow...")
        
        try:
            # Create user manager
            users_file = Path(self.temp_dir) / 'data' / 'authorized_users.json'
            user_manager = UserManager(users_file)
            
            # Test scenarios
            test_user_id = 12345
            admin_id = 123456789
            
            # Test 1: Unauthorized user
            assert not user_manager.is_authorized(test_user_id)
            
            # Test 2: Add user
            assert user_manager.add_user(test_user_id)
            assert user_manager.is_authorized(test_user_id)
            
            # Test 3: Admin auto-authorization
            assert user_manager.add_user(admin_id)
            assert user_manager.is_authorized(admin_id)
            
            # Test 4: Remove user
            assert user_manager.remove_user(test_user_id)
            assert not user_manager.is_authorized(test_user_id)
            
            self.test_results.append(("User Authorization", "✅ PASS"))
            logger.info("✅ User authorization test passed")
            
        except Exception as e:
            self.test_results.append(("User Authorization", f"❌ FAIL: {e}"))
            logger.error(f"❌ User authorization test failed: {e}")
            
    async def test_command_handlers(self):
        """Test command handlers"""
        logger.info("💬 Testing command handlers...")
        
        try:
            from telegram_ai_bot.handlers.command_handlers import get_start_handler, get_help_handler
            
            # Set up user manager
            users_file = Path(self.temp_dir) / 'data' / 'authorized_users.json'
            user_manager = UserManager(users_file)
            user_manager.add_user(12345)  # Add test user
            
            # Mock config
            mock_config = Mock()
            mock_config.ADMIN_USER_ID = '123456789'
            
            # Test start command for authorized user
            start_handler = get_start_handler(user_manager, mock_config)
            update = self.create_mock_update(12345)
            context = self.create_mock_context()
            
            await start_handler.callback(update, context)
            
            # Verify welcome message was sent
            update.message.reply_text.assert_called_once()
            welcome_message = update.message.reply_text.call_args[0][0]
            assert "Welcome" in welcome_message
            
            # Test help command
            help_handler = get_help_handler()
            update = self.create_mock_update(12345)
            update.message.reply_text.reset_mock()
            
            await help_handler.callback(update, context)
            
            # Verify help message was sent
            update.message.reply_text.assert_called_once()
            help_message = update.message.reply_text.call_args[0][0]
            assert "Available Commands" in help_message
            
            self.test_results.append(("Command Handlers", "✅ PASS"))
            logger.info("✅ Command handlers test passed")
            
        except Exception as e:
            self.test_results.append(("Command Handlers", f"❌ FAIL: {e}"))
            logger.error(f"❌ Command handlers test failed: {e}")
            
    async def test_voice_message_processing(self):
        """Test voice message processing pipeline"""
        logger.info("🎤 Testing voice message processing...")
        
        try:
            from telegram_ai_bot.handlers.message_handlers import get_voice_handler
            
            # Set up components
            users_file = Path(self.temp_dir) / 'data' / 'authorized_users.json'
            user_manager = UserManager(users_file)
            user_manager.add_user(12345)
            
            mock_config = Mock()
            mock_config.OPENAI_API_KEY = 'test_key'
            mock_config.GPT_MODEL = 'gpt-4'
            
            # Mock AI service
            with patch('telegram_ai_bot.handlers.message_handlers.AIService') as mock_ai_service:
                # Mock AI responses
                mock_ai_instance = Mock()
                mock_ai_instance.transcribe_audio = AsyncMock(
                    return_value="This is a test voice message about scheduling a meeting tomorrow at 3 PM"
                )
                mock_ai_instance.analyze_text = AsyncMock(return_value={
                    "summary": "User wants to schedule a meeting for tomorrow at 3 PM",
                    "action_items": [
                        {
                            "task": "Schedule meeting",
                            "deadline": "tomorrow at 3 PM",
                            "priority": "high"
                        }
                    ],
                    "topics": ["meeting", "schedule"]
                })
                mock_ai_service.return_value = mock_ai_instance
                
                # Mock voice file and temporary file
                with patch('tempfile.NamedTemporaryFile') as mock_tempfile:
                    with patch('os.unlink') as mock_unlink:
                        mock_temp = Mock()
                        mock_temp.name = '/tmp/test_audio.ogg'
                        mock_tempfile.return_value.__enter__.return_value = mock_temp
                        
                        mock_voice_file = Mock()
                        mock_voice_file.download_to_drive = AsyncMock()
                        
                        # Create handler and test
                        handler = get_voice_handler(user_manager, mock_config)
                        update = self.create_mock_update(12345, voice_file=mock_voice_file)
                        context = self.create_mock_context()
                        
                        # Mock processing message
                        processing_msg = Mock()
                        processing_msg.edit_text = AsyncMock()
                        update.message.reply_text = AsyncMock(return_value=processing_msg)
                        
                        # Execute handler
                        await handler.callback(update, context)
                        
                        # Verify the flow
                        mock_voice_file.download_to_drive.assert_called_once()
                        mock_ai_instance.transcribe_audio.assert_called_once()
                        mock_ai_instance.analyze_text.assert_called_once()
                        
                        # Verify processing messages were updated
                        assert processing_msg.edit_text.call_count >= 2
                        
                        # Verify cleanup
                        mock_unlink.assert_called_once()
                        
            self.test_results.append(("Voice Processing", "✅ PASS"))
            logger.info("✅ Voice message processing test passed")
            
        except Exception as e:
            self.test_results.append(("Voice Processing", f"❌ FAIL: {e}"))
            logger.error(f"❌ Voice message processing test failed: {e}")
            
    async def test_calendar_integration(self):
        """Test calendar integration"""
        logger.info("📅 Testing calendar integration...")
        
        try:
            from telegram_ai_bot.utils.calendar_utils import (
                generate_calendar_link, 
                parse_deadline,
                format_action_items_for_calendar
            )
            
            # Test calendar link generation
            link = generate_calendar_link(
                title="Test Meeting",
                description="Test meeting description"
            )
            assert "calendar.google.com" in link
            assert "Test%20Meeting" in link
            
            # Test deadline parsing
            deadline = parse_deadline("meeting at 3 PM")
            assert deadline is not None
            assert deadline.hour == 15
            
            # Test action item formatting
            action_items = [
                {
                    "task": "Schedule meeting",
                    "deadline": "tomorrow at 3 PM",
                    "priority": "high"
                }
            ]
            
            formatted = format_action_items_for_calendar(action_items)
            assert len(formatted) == 1
            assert "calendar_link" in formatted[0]
            assert "calendar.google.com" in formatted[0]["calendar_link"]
            
            self.test_results.append(("Calendar Integration", "✅ PASS"))
            logger.info("✅ Calendar integration test passed")
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.test_results.append(("Calendar Integration", f"❌ FAIL: {e}"))
            logger.error(f"❌ Calendar integration test failed: {e}")
            logger.error(f"Full traceback: {error_details}")
            
    async def test_error_handling(self):
        """Test error handling scenarios"""
        logger.info("⚠️ Testing error handling...")
        
        try:
            from telegram_ai_bot.handlers.message_handlers import get_voice_handler
            
            # Set up components
            users_file = Path(self.temp_dir) / 'data' / 'authorized_users.json'
            user_manager = UserManager(users_file)
            
            mock_config = Mock()
            mock_config.OPENAI_API_KEY = 'test_key'
            mock_config.GPT_MODEL = 'gpt-4'
            
            # Test unauthorized user
            handler = get_voice_handler(user_manager, mock_config)
            update = self.create_mock_update(99999)  # Unauthorized user
            context = self.create_mock_context()
            
            await handler.callback(update, context)
            
            # Verify unauthorized message
            update.message.reply_text.assert_called_once()
            error_message = update.message.reply_text.call_args[0][0]
            assert "not authorized" in error_message
            
            # Test AI service error handling
            user_manager.add_user(12345)  # Add authorized user
            
            with patch('telegram_ai_bot.handlers.message_handlers.AIService') as mock_ai_service:
                # Mock AI service to raise exception
                mock_ai_instance = Mock()
                mock_ai_instance.transcribe_audio = AsyncMock(side_effect=Exception("API Error"))
                mock_ai_service.return_value = mock_ai_instance
                
                with patch('tempfile.NamedTemporaryFile'):
                    mock_voice_file = Mock()
                    mock_voice_file.download_to_drive = AsyncMock()
                    
                    update = self.create_mock_update(12345, voice_file=mock_voice_file)
                    processing_msg = Mock()
                    processing_msg.edit_text = AsyncMock()
                    update.message.reply_text = AsyncMock(return_value=processing_msg)
                    
                    await handler.callback(update, context)
                    
                    # Verify error message was sent
                    final_call = processing_msg.edit_text.call_args_list[-1]
                    error_text = final_call[0][0]
                    assert "couldn't process" in error_text
                    
            self.test_results.append(("Error Handling", "✅ PASS"))
            logger.info("✅ Error handling test passed")
            
        except Exception as e:
            self.test_results.append(("Error Handling", f"❌ FAIL: {e}"))
            logger.error(f"❌ Error handling test failed: {e}")
            
    def print_test_results(self):
        """Print comprehensive test results"""
        logger.info("📊 Test Results Summary:")
        print("\n" + "="*60)
        print("🧪 TELEGRAM AI BOT - END-TO-END TEST RESULTS")
        print("="*60)
        
        passed = 0
        failed = 0
        
        for test_name, result in self.test_results:
            print(f"{result:<20} {test_name}")
            if "✅ PASS" in result:
                passed += 1
            else:
                failed += 1
                
        print("="*60)
        print(f"📈 SUMMARY: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED!")
            print("✅ Your bot is ready for deployment!")
        else:
            print("⚠️ Some tests failed. Please review the errors above.")
            
        print("="*60)
        
        return failed == 0

async def main():
    """Main test execution function"""
    print("🚀 Starting Telegram AI Bot End-to-End Tests...")
    
    tester = BotE2ETest()
    
    try:
        # Set up test environment
        tester.setup_test_environment()
        
        # Run all tests
        await tester.test_bot_initialization()
        await tester.test_user_authorization_flow()
        await tester.test_command_handlers()
        await tester.test_voice_message_processing()
        await tester.test_calendar_integration()
        await tester.test_error_handling()
        
        # Print results
        success = tester.print_test_results()
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"❌ Test execution failed: {e}")
        return 1
        
    finally:
        # Clean up
        tester.cleanup_test_environment()

if __name__ == "__main__":
    import sys
    
    # Handle Python 3.13 compatibility
    if sys.version_info >= (3, 13):
        import warnings
        warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    # Run tests
    exit_code = asyncio.run(main())
    sys.exit(exit_code)