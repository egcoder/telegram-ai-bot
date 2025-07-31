#!/usr/bin/env python3
"""Debug script to test Whisper API parameters"""
import os
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from openai import OpenAI

def test_whisper_with_params():
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Create a minimal WAV file for testing
    import wave
    import struct
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
        # Create a simple WAV file with 1 second of silence
        with wave.open(tmp_file.name, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)   # 16-bit
            wav_file.setframerate(16000)  # 16kHz
            
            # Write 1 second of silence
            for _ in range(16000):
                wav_file.writeframes(struct.pack('<h', 0))
        
        test_file = tmp_file.name
    
    print("Testing Whisper API with different parameters...")
    
    # Test 1: Basic call
    try:
        print("\n1. Basic call with no extra params:")
        with open(test_file, 'rb') as f:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        print(f"   SUCCESS: {response}")
    except Exception as e:
        print(f"   FAILED: {e}")
    
    # Test 2: With valid response_format
    try:
        print("\n2. With valid response_format='text':")
        with open(test_file, 'rb') as f:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="text"
            )
        print(f"   SUCCESS: {response}")
    except Exception as e:
        print(f"   FAILED: {e}")
    
    # Test 3: With invalid response_format (chat completion style)
    try:
        print("\n3. With INVALID response_format={'type': 'json_object'}:")
        with open(test_file, 'rb') as f:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format={"type": "json_object"}
            )
        print(f"   SUCCESS: {response}")
    except Exception as e:
        print(f"   FAILED (expected): {e}")
    
    # Clean up
    os.unlink(test_file)
    
    print("\n4. Testing if client carries configuration:")
    # Create a client and use it for chat, then whisper
    test_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # First make a chat call with response_format
    try:
        chat_response = test_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'test'"}],
            response_format={"type": "json_object"},
            max_tokens=10
        )
        print("   Chat call succeeded")
    except Exception as e:
        print(f"   Chat call failed: {e}")
    
    # Now try whisper with the same client
    try:
        with open(test_file, 'rb') as f:
            response = test_client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        print("   Whisper call after chat: SUCCESS")
    except Exception as e:
        print(f"   Whisper call after chat: FAILED - {e}")

if __name__ == "__main__":
    test_whisper_with_params()