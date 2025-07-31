"""Completely isolated Whisper transcription to avoid any parameter pollution"""
import subprocess
import json
import tempfile
import os
import sys
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class IsolatedWhisperService:
    """Use subprocess to completely isolate the Whisper API call"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def transcribe(self, audio_file_path: Path, language: Optional[str] = None) -> str:
        """Transcribe using a subprocess to avoid any parameter pollution"""
        logger.info(f"IsolatedWhisperService: Starting transcription of {audio_file_path}")
        
        # Create a Python script that will run in isolation
        script_content = '''
import sys
import openai
from pathlib import Path

api_key = sys.argv[1]
audio_path = sys.argv[2]

# Create a completely fresh client
client = openai.OpenAI(api_key=api_key, timeout=30.0)

# Open and transcribe
with open(audio_path, 'rb') as f:
    response = client.audio.transcriptions.create(
        model="whisper-1",
        file=f,
        response_format="text"
    )

# Print result
print(response)
'''
        
        # Write script to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script_content)
            script_path = f.name
        
        try:
            # Run in subprocess with timeout
            import sys
            result = subprocess.run(
                [sys.executable, script_path, self.api_key, str(audio_file_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"Subprocess error: {result.stderr}")
                raise Exception(f"Transcription failed: {result.stderr}")
            
            transcript = result.stdout.strip()
            logger.info(f"Transcription successful: {transcript[:50]}...")
            return transcript
            
        except subprocess.TimeoutExpired:
            logger.error("Subprocess timed out after 30 seconds")
            raise Exception("Transcription timed out")
        finally:
            # Clean up script
            os.unlink(script_path)

def transcribe_with_curl(api_key: str, audio_file_path: Path) -> str:
    """Alternative: Use curl to make the API call"""
    logger.info("Using curl fallback for transcription")
    
    cmd = [
        'curl',
        '-X', 'POST',
        'https://api.openai.com/v1/audio/transcriptions',
        '-H', f'Authorization: Bearer {api_key}',
        '-F', 'model=whisper-1',
        '-F', f'file=@{audio_file_path}',
        '-F', 'response_format=text',
        '--max-time', '30'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
        if result.returncode != 0:
            raise Exception(f"Curl failed: {result.stderr}")
        return result.stdout.strip()
    except Exception as e:
        logger.error(f"Curl transcription failed: {e}")
        raise