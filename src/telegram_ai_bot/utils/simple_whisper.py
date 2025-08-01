"""Ultra-simple Whisper transcription with no dependencies"""
import logging
import subprocess
import os
from pathlib import Path

logger = logging.getLogger(__name__)

def transcribe_with_curl_only(api_key: str, audio_file_path: Path) -> str:
    """Use only curl, no Python OpenAI library at all"""
    logger.info(f"Using curl-only transcription for {audio_file_path}")
    
    # Ensure file exists
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
    
    cmd = [
        'curl',
        '--request', 'POST',
        '--url', 'https://api.openai.com/v1/audio/transcriptions',
        '--header', f'Authorization: Bearer {api_key}',
        '--header', 'Content-Type: multipart/form-data',
        '--form', 'model=whisper-1',
        '--form', f'file=@{audio_file_path}',
        '--form', 'response_format=text',
        '--max-time', '30',
        '--silent'
    ]
    
    logger.info("Executing curl command...")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=35
        )
        
        if result.returncode != 0:
            logger.error(f"Curl failed with code {result.returncode}")
            logger.error(f"Stderr: {result.stderr}")
            logger.error(f"Stdout: {result.stdout}")
            
            # Try to parse error
            if result.stdout and 'invalid' in result.stdout.lower():
                raise Exception(f"API Error: {result.stdout}")
            else:
                raise Exception(f"Curl failed: {result.stderr or 'Unknown error'}")
        
        transcript = result.stdout.strip()
        logger.info(f"Curl transcription successful: {transcript[:50]}...")
        return transcript
        
    except subprocess.TimeoutExpired:
        logger.error("Curl timeout after 35 seconds")
        raise Exception("Transcription timed out")
    except Exception as e:
        logger.error(f"Curl transcription error: {e}")
        raise