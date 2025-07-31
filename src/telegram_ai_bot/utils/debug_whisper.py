"""Debug wrapper for Whisper API calls"""
import logging
import json
from pathlib import Path
from typing import Optional, Any
import openai
import inspect

logger = logging.getLogger(__name__)

class DebugWhisperClient:
    """Wrapper to intercept and log all Whisper API calls"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = None
    
    @property 
    def client(self):
        if not self._client:
            self._client = openai.OpenAI(api_key=self.api_key)
        return self._client
    
    def transcribe(self, audio_file_path: Path) -> str:
        """Transcribe with full debugging"""
        logger.info("="*60)
        logger.info("DEBUG WHISPER TRANSCRIPTION")
        logger.info("="*60)
        
        # Log call stack
        stack = inspect.stack()
        logger.info("Call stack:")
        for i, frame in enumerate(stack[1:6]):  # Skip this frame, show next 5
            logger.info(f"  {i}: {frame.filename}:{frame.lineno} in {frame.function}")
        
        # Create a new client to ensure clean state
        logger.info(f"Creating fresh OpenAI client...")
        fresh_client = openai.OpenAI(api_key=self.api_key)
        
        # Log client state
        logger.info(f"Client type: {type(fresh_client)}")
        if hasattr(fresh_client, '_client'):
            inner = fresh_client._client
            logger.info(f"Inner HTTP client: {type(inner)}")
            if hasattr(inner, '_base_headers'):
                logger.info(f"Base headers: {inner._base_headers}")
        
        # Try transcription
        try:
            with open(audio_file_path, 'rb') as f:
                logger.info(f"File opened: {audio_file_path}")
                logger.info(f"File size: {audio_file_path.stat().st_size} bytes")
                
                # Intercept the actual API call
                import httpx
                original_post = httpx.Client.post if hasattr(httpx.Client, 'post') else None
                
                def debug_post(self, *args, **kwargs):
                    logger.info(f"HTTP POST intercepted!")
                    logger.info(f"URL: {args[0] if args else kwargs.get('url', 'N/A')}")
                    logger.info(f"Headers: {kwargs.get('headers', {})}")
                    if 'data' in kwargs:
                        # Don't log file content, just structure
                        logger.info(f"Data keys: {list(kwargs['data'].keys()) if isinstance(kwargs['data'], dict) else 'Not a dict'}")
                    if 'json' in kwargs:
                        logger.info(f"JSON payload: {json.dumps(kwargs['json'], indent=2)}")
                    if 'files' in kwargs:
                        logger.info(f"Files: {list(kwargs['files'].keys()) if isinstance(kwargs['files'], dict) else 'Present'}")
                    
                    # Call original
                    if original_post:
                        return original_post(self, *args, **kwargs)
                    else:
                        raise Exception("Could not find original post method")
                
                # Temporarily patch
                if original_post:
                    httpx.Client.post = debug_post
                
                try:
                    # Make the call with absolute minimum params
                    logger.info("Making Whisper API call...")
                    response = fresh_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=f
                    )
                    logger.info(f"Success! Response: {response}")
                    return response.text if hasattr(response, 'text') else str(response)
                finally:
                    # Restore original
                    if original_post:
                        httpx.Client.post = original_post
                        
        except Exception as e:
            logger.error(f"Transcription failed!")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error message: {str(e)}")
            if hasattr(e, 'response'):
                logger.error(f"HTTP response status: {getattr(e.response, 'status_code', 'N/A')}")
                logger.error(f"HTTP response text: {getattr(e.response, 'text', 'N/A')}")
            raise