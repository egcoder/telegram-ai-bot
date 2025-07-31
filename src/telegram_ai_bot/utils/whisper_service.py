"""Isolated Whisper transcription service to avoid any parameter pollution"""
import logging
import sys
from pathlib import Path
from typing import Optional
import openai

logger = logging.getLogger(__name__)

class WhisperService:
    """Dedicated service for Whisper transcriptions"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def transcribe(self, audio_file_path: Path, language: Optional[str] = None) -> str:
        """Transcribe audio using Whisper API with clean parameters"""
        logger.info(f"WhisperService.transcribe called with path: {audio_file_path}")
        
        # Create a fresh client for each transcription with timeout
        client = openai.OpenAI(
            api_key=self.api_key,
            timeout=30.0  # 30 second timeout instead of default
        )
        logger.info(f"Created fresh OpenAI client with 30s timeout")
        
        try:
            # Verify file exists and has content
            if not audio_file_path.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
            
            file_size = audio_file_path.stat().st_size
            logger.info(f"Audio file size: {file_size} bytes")
            
            with open(audio_file_path, 'rb') as audio_file:
                # Try the most minimal call first
                logger.info("Attempting minimal Whisper API call...")
                try:
                    response = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                    logger.info(f"Minimal call succeeded: {response}")
                    return response.text if hasattr(response, 'text') else str(response)
                except Exception as minimal_error:
                    logger.error(f"Minimal call failed: {minimal_error}")
                    
                    # Reset file position
                    audio_file.seek(0)
                    
                    # Try with explicit text format
                    logger.info("Attempting with explicit text format...")
                    response = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="text"
                    )
                
                # Handle response
                if isinstance(response, str):
                    return response
                elif hasattr(response, 'text'):
                    return response.text
                else:
                    return str(response)
                    
        except Exception as e:
            logger.error(f"Whisper transcription error: {e}")
            logger.error(f"OpenAI library version: {openai.__version__}")
            logger.error(f"Python version: {sys.version}")
            
            # Log detailed error info
            error_str = str(e)
            if "response_format" in error_str:
                logger.error("ERROR: Invalid response_format parameter detected!")
                logger.error("This suggests the OpenAI client is polluted with chat parameters.")
                logger.error(f"Current OpenAI version: {openai.__version__}")
            raise