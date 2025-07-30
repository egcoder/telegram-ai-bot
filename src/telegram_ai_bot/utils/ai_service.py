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
        try:
            with open(audio_file_path, 'rb') as audio_file:
                # Run in executor to avoid blocking
                loop = asyncio.get_event_loop()
                transcript = await loop.run_in_executor(
                    None,
                    self._transcribe_sync,
                    audio_file,
                    language
                )
                return transcript
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            raise
            
    def _transcribe_sync(self, audio_file, language: Optional[str]) -> str:
        """Synchronous transcription method"""
        params = {
            "model": "whisper-1",
            "file": audio_file,
            "response_format": "text"
        }
        
        if language:
            params["language"] = language
            
        response = self.client.audio.transcriptions.create(**params)
        return response
        
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