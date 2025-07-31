#!/usr/bin/env python3
"""Minimal test to isolate Whisper API issue"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_whisper_directly():
    """Test Whisper API with absolute minimal setup"""
    # Import OpenAI fresh
    import openai
    
    # Get API key from config
    from telegram_ai_bot.core.config import Config
    config = Config()
    
    # Create a completely fresh client
    client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
    
    print(f"OpenAI client created")
    print(f"Client type: {type(client)}")
    print(f"Client attributes: {dir(client)}")
    
    # Check if there's any default configuration
    if hasattr(client, '_client'):
        print(f"Inner client: {client._client}")
        if hasattr(client._client, 'default_headers'):
            print(f"Default headers: {client._client.default_headers}")
    
    # Test with a minimal audio file
    import tempfile
    import struct
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        # Write WAV header
        tmp.write(b'RIFF')
        tmp.write(struct.pack('<I', 36 + 16000))  # File size
        tmp.write(b'WAVE')
        tmp.write(b'fmt ')
        tmp.write(struct.pack('<I', 16))  # Subchunk size
        tmp.write(struct.pack('<H', 1))   # Audio format (PCM)
        tmp.write(struct.pack('<H', 1))   # Channels
        tmp.write(struct.pack('<I', 16000))  # Sample rate
        tmp.write(struct.pack('<I', 32000))  # Byte rate
        tmp.write(struct.pack('<H', 2))   # Block align
        tmp.write(struct.pack('<H', 16))  # Bits per sample
        tmp.write(b'data')
        tmp.write(struct.pack('<I', 16000))  # Data size
        
        # Write 1 second of silence
        for _ in range(8000):
            tmp.write(struct.pack('<h', 0))
        
        audio_file = tmp.name
    
    print(f"\nTesting Whisper API call...")
    
    try:
        with open(audio_file, 'rb') as f:
            # Call with absolutely minimal parameters
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        print(f"SUCCESS: {response}")
    except Exception as e:
        print(f"FAILED: {e}")
        print(f"Error type: {type(e)}")
        if hasattr(e, 'response'):
            print(f"Response status: {e.response.status_code if hasattr(e.response, 'status_code') else 'N/A'}")
            print(f"Response text: {e.response.text if hasattr(e.response, 'text') else 'N/A'}")
    
    # Clean up
    os.unlink(audio_file)

if __name__ == "__main__":
    test_whisper_directly()