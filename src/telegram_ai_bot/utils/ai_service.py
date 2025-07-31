"""AI service utilities for transcription and analysis"""
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import asyncio

import openai
from openai import OpenAI

logger = logging.getLogger(__name__)

class AIService:
    """Handles AI-related operations (transcription, analysis)"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        
    async def transcribe_audio(self, audio_file_path: Path, language: Optional[str] = None) -> str:
        """Transcribe audio file using OpenAI Whisper"""
        start_time = asyncio.get_event_loop().time()
        logger.info(f"Starting transcription of {audio_file_path}")
        
        try:
            # Try isolated subprocess approach first
            from .isolated_whisper import IsolatedWhisperService, transcribe_with_curl
            isolated = IsolatedWhisperService(self.client.api_key)
            logger.info("Using IsolatedWhisperService to avoid parameter pollution")
            
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            logger.info("Starting isolated transcription...")
            
            try:
                transcript = await loop.run_in_executor(
                    None,
                    isolated.transcribe,
                    audio_file_path,
                    language
                )
            except Exception as e:
                logger.error(f"Subprocess approach failed: {e}, trying curl...")
                transcript = await loop.run_in_executor(
                    None,
                    transcribe_with_curl,
                    self.client.api_key,
                    audio_file_path
                )
            
            elapsed = loop.time() - start_time
            logger.info(f"Transcription completed in {elapsed:.2f} seconds")
            return transcript
        except Exception as e:
            elapsed = asyncio.get_event_loop().time() - start_time
            logger.error(f"All transcription methods failed after {elapsed:.2f} seconds: {e}")
            
            # Last resort: try the original WhisperService
            logger.error("Falling back to WhisperService...")
            from .whisper_service import WhisperService
            whisper = WhisperService(self.client.api_key)
            loop = asyncio.get_event_loop()
            transcript = await loop.run_in_executor(
                None,
                whisper.transcribe,
                audio_file_path,
                language
            )
            return transcript
            
    def _transcribe_sync(self, audio_file, language: Optional[str]) -> str:
        """Synchronous transcription method"""
        try:
            # Create fresh client for transcription to avoid any parameter pollution
            from openai import OpenAI
            transcription_client = OpenAI(api_key=self.client.api_key)
            
            logger.info(f"Starting transcription with file type: {type(audio_file)}")
            
            # Use the most basic parameters possible
            # Explicitly set response_format to avoid any parameter pollution
            response = transcription_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"  # Ensure we use Whisper's format, not chat's
            )
            
            logger.info(f"Whisper response type: {type(response)}")
            logger.info(f"Whisper response: {response}")
            
            # Handle different response types
            if hasattr(response, 'text'):
                logger.info("Using response.text attribute")
                return response.text
            elif isinstance(response, str):
                logger.info("Response is already a string")
                return response
            else:
                # Convert to string as fallback
                logger.info("Converting response to string")
                return str(response)
                
        except Exception as e:
            logger.error(f"Whisper API error: {e}")
            logger.error(f"Error type: {type(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            
            # If it's a parameter error, log the exact issue
            error_str = str(e)
            if "response_format" in error_str and "json_object" in error_str:
                logger.error("CRITICAL: The Whisper API is receiving chat completion parameters!")
                logger.error("This suggests OpenAI client configuration pollution.")
                logger.error("Creating new isolated client...")
                
                # Try one more time with a completely fresh client and explicit params
                try:
                    import openai as fresh_openai
                    fresh_client = fresh_openai.OpenAI(api_key=self.client.api_key)
                    
                    # Reset file position if needed
                    if hasattr(audio_file, 'seek'):
                        audio_file.seek(0)
                    
                    # Use only the exact parameters Whisper accepts
                    # Note: response_format for Whisper should be a string, not an object
                    response = fresh_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="text"  # Valid values: "json", "text", "srt", "verbose_json", "vtt"
                    )
                    
                    logger.info("Successfully transcribed with fresh client")
                    return response if isinstance(response, str) else response.text
                except Exception as retry_error:
                    logger.error(f"Retry also failed: {retry_error}")
                    raise retry_error
            else:
                raise
                
    def _transcribe_sync_with_path(self, audio_file_path: str, language: Optional[str]) -> str:
        """Synchronous transcription method that opens the file"""
        with open(audio_file_path, 'rb') as audio_file:
            return self._transcribe_sync(audio_file, language)
        
    async def get_chat_response(self, message: str, user_name: str) -> str:
        """Get a chat response from the AI"""
        try:
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self._get_chat_response_sync,
                message,
                user_name
            )
            return response
        except Exception as e:
            logger.error(f"Chat response error: {e}")
            raise
    
    def _get_chat_response_sync(self, message: str, user_name: str) -> str:
        """Synchronous chat response method"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": f"You are a helpful AI assistant chatting with {user_name}. Be friendly, concise, and helpful."},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    
    async def analyze_text(self, text: str, user_name: str) -> Dict:
        """Analyze text and extract action items"""
        prompt = f"""Analyze this voice note from {user_name} and extract:
1. A brief summary (2-3 sentences)
2. Action items with deadlines and priorities
3. Key topics discussed

Voice note content: {text}

Format response as JSON with keys: summary, action_items (list with task, deadline, priority), topics"""

        try:
            loop = asyncio.get_event_loop()
            analysis = await loop.run_in_executor(
                None,
                self._analyze_sync,
                prompt
            )
            return analysis
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            raise
            
    def _analyze_sync(self, prompt: str) -> Dict:
        """Synchronous analysis method"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts action items from conversations."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        import json
        return json.loads(response.choices[0].message.content)
        
class AnthropicService:
    """Alternative AI service using Anthropic Claude"""
    
    def __init__(self, api_key: str):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            logger.warning("Anthropic library not installed")
            self.client = None
            
    async def analyze_text(self, text: str, user_name: str) -> Dict:
        """Analyze text using Claude"""
        if not self.client:
            raise ValueError("Anthropic client not available")
            
        prompt = f"""Analyze this voice note from {user_name} and extract:
1. A brief summary (2-3 sentences)
2. Action items with deadlines and priorities
3. Key topics discussed

Voice note content: {text}

Return response as valid JSON with keys: summary, action_items (list with task, deadline, priority), topics"""

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
            )
            
            import json
            return json.loads(response.content[0].text)
        except Exception as e:
            logger.error(f"Claude analysis error: {e}")
            raise