"""Unit tests for AI services with mocking"""
import unittest
import asyncio
import tempfile
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from telegram_ai_bot.utils.ai_service import AIService, AnthropicService

class TestAIService(unittest.IsolatedAsyncioTestCase):
    """Test OpenAI AI service with mocking"""
    
    def setUp(self):
        """Set up test environment"""
        self.api_key = "test_openai_key"
        self.model = "gpt-4"
        
    @patch('telegram_ai_bot.utils.ai_service.OpenAI')
    async def test_transcription_success(self, mock_openai_class):
        """Test successful audio transcription"""
        # Mock the OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        # Mock transcription response
        mock_client.audio.transcriptions.create.return_value = "Test transcription result"
        
        # Create service
        service = AIService(self.api_key, self.model)
        
        # Create temporary audio file
        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_file:
            temp_file.write(b"fake audio data")
            audio_path = Path(temp_file.name)
        
        try:
            # Test transcription
            result = await service.transcribe_audio(audio_path)
            
            # Verify result
            self.assertEqual(result, "Test transcription result")
            
            # Verify API call
            mock_client.audio.transcriptions.create.assert_called_once()
            call_kwargs = mock_client.audio.transcriptions.create.call_args[1]
            self.assertEqual(call_kwargs['model'], 'whisper-1')
            self.assertEqual(call_kwargs['response_format'], 'text')
            
        finally:
            audio_path.unlink()
            
    @patch('telegram_ai_bot.utils.ai_service.OpenAI')
    async def test_transcription_with_language(self, mock_openai_class):
        """Test transcription with specified language"""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.audio.transcriptions.create.return_value = "Arabic transcription"
        
        service = AIService(self.api_key, self.model)
        
        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_file:
            temp_file.write(b"fake audio data")
            audio_path = Path(temp_file.name)
            
        try:
            result = await service.transcribe_audio(audio_path, language='ar')
            
            # Verify language parameter was passed
            call_kwargs = mock_client.audio.transcriptions.create.call_args[1]
            self.assertEqual(call_kwargs['language'], 'ar')
            
        finally:
            audio_path.unlink()
            
    @patch('telegram_ai_bot.utils.ai_service.OpenAI')
    async def test_text_analysis_success(self, mock_openai_class):
        """Test successful text analysis"""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        # Mock analysis response
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = json.dumps({
            "summary": "Test summary",
            "action_items": [
                {"task": "Test task", "deadline": "tomorrow", "priority": "high"}
            ],
            "topics": ["test", "meeting"]
        })
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        
        service = AIService(self.api_key, self.model)
        
        # Test analysis
        result = await service.analyze_text("Test voice note content", "TestUser")
        
        # Verify result structure
        self.assertIn("summary", result)
        self.assertIn("action_items", result)
        self.assertIn("topics", result)
        self.assertEqual(result["summary"], "Test summary")
        
        # Verify API call
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_kwargs['model'], self.model)
        self.assertEqual(call_kwargs['response_format'], {"type": "json_object"})
        
    @patch('telegram_ai_bot.utils.ai_service.OpenAI')
    async def test_transcription_error_handling(self, mock_openai_class):
        """Test error handling in transcription"""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        # Mock API error
        mock_client.audio.transcriptions.create.side_effect = Exception("API Error")
        
        service = AIService(self.api_key, self.model)
        
        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_file:
            temp_file.write(b"fake audio data")
            audio_path = Path(temp_file.name)
            
        try:
            # Test that exception is propagated
            with self.assertRaises(Exception):
                await service.transcribe_audio(audio_path)
                
        finally:
            audio_path.unlink()
            
    @patch('telegram_ai_bot.utils.ai_service.OpenAI')
    async def test_analysis_error_handling(self, mock_openai_class):
        """Test error handling in analysis"""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        # Mock API error
        mock_client.chat.completions.create.side_effect = Exception("Analysis Error")
        
        service = AIService(self.api_key, self.model)
        
        # Test that exception is propagated
        with self.assertRaises(Exception):
            await service.analyze_text("Test content", "TestUser")

class TestAnthropicService(unittest.IsolatedAsyncioTestCase):
    """Test Anthropic service with mocking"""
    
    def setUp(self):
        """Set up test environment"""
        self.api_key = "test_anthropic_key"
        
    async def test_anthropic_analysis_success(self):
        """Test successful analysis with Anthropic"""
        # Create a mock client directly and patch it into the service
        mock_client = Mock()
        
        # Mock response
        mock_content = Mock()
        mock_content.text = json.dumps({
            "summary": "Claude analysis summary",
            "action_items": [
                {"task": "Claude task", "deadline": "next week", "priority": "medium"}
            ],
            "topics": ["claude", "analysis"]
        })
        mock_response = Mock()
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        
        # Create service and manually set the client
        service = AnthropicService(self.api_key)
        service.client = mock_client  # Override the client
        
        # Test analysis
        result = await service.analyze_text("Test content", "TestUser")
        
        # Verify result
        self.assertIn("summary", result)
        self.assertEqual(result["summary"], "Claude analysis summary")
        
        # Verify API call
        mock_client.messages.create.assert_called_once()
        call_kwargs = mock_client.messages.create.call_args[1]
        self.assertEqual(call_kwargs['model'], 'claude-3-opus-20240229')
        
    def test_anthropic_unavailable(self):
        """Test behavior when Anthropic library is not available"""
        with patch('builtins.__import__', side_effect=ImportError("No module named 'anthropic'")):
            # This should not raise an exception during initialization
            service = AnthropicService(self.api_key)
            self.assertIsNone(service.client)
        
    async def test_anthropic_analysis_without_client(self):
        """Test analysis when client is not available"""
        with patch('builtins.__import__', side_effect=ImportError("No module named 'anthropic'")):
            # Force client to None
            service = AnthropicService(self.api_key)
            
            # Should raise ValueError
            with self.assertRaises(ValueError):
                await service.analyze_text("Test content", "TestUser")

class TestAIServiceIntegration(unittest.TestCase):
    """Test AI service integration scenarios"""
    
    def test_service_initialization(self):
        """Test service initialization with different parameters"""
        # Test with defaults
        service1 = AIService("test_key")
        self.assertEqual(service1.model, "gpt-4")
        
        # Test with custom model
        service2 = AIService("test_key", "gpt-3.5-turbo")
        self.assertEqual(service2.model, "gpt-3.5-turbo")
        
    def test_anthropic_initialization_with_library(self):
        """Test Anthropic service initialization when library is available"""
        with patch('builtins.__import__') as mock_import:
            mock_anthropic = Mock()
            mock_client = Mock()
            mock_anthropic.Anthropic.return_value = mock_client
            
            def side_effect(name, *args):
                if name == 'anthropic':
                    return mock_anthropic
                return __import__(name, *args)
            
            mock_import.side_effect = side_effect
            
            service = AnthropicService("test_key")
            self.assertIsNotNone(service.client)
        
    def test_anthropic_initialization_without_library(self):
        """Test Anthropic service initialization when library is not available"""
        with patch('builtins.__import__', side_effect=ImportError("No module named 'anthropic'")):
            service = AnthropicService("test_key")
            self.assertIsNone(service.client)

if __name__ == '__main__':
    unittest.main()